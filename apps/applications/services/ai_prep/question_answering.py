"""
MwohaOS Question Answering Engine — Milestone 6: AI Preparation
Drafts structured, evidence-grounded application essay answers using the STAR method
or chosen tone, strictly enforcing word and character limit constraints.
"""
import logging
import re
from typing import Dict, Any, Optional
from django.conf import settings

from apps.applications.models import (
    ApplicationQuestion,
    QuestionDraftVersion,
    ApplicationActivity,
)
from apps.applications.constants import (
    QuestionStatus,
    AITone,
    ActivityType,
)
from apps.applications.services.readiness import evaluate_application_readiness
from apps.opportunities.services.llm_router import LLMRouter
from .prompts import format_question_prompt
from .evidence_grounding import gather_candidate_evidence, audit_grounding_evidence
from .deterministic_ai_prep import synthesize_deterministic_question_answer

logger = logging.getLogger("mwohaos.ai_prep.question_answering")


def draft_question_answer(
    question: ApplicationQuestion,
    tone: str = AITone.STAR_METHOD,
    additional_guidance: str = "",
    force_deterministic: bool = False,
) -> Dict[str, Any]:
    """
    Drafts a grounded answer for an ApplicationQuestion and records it as a QuestionDraftVersion.
    Strictly enforces max_words and max_characters limits.
    """
    application = question.application
    profile = application.profile
    opportunity = application.opportunity

    candidate_evidence = gather_candidate_evidence(profile)

    opp_data: Dict[str, Any] = {
        "title": application.display_title,
        "organization": application.display_organization,
        "summary": opportunity.description or "",
        "required_requirements": [],
    }
    if hasattr(opportunity, "intelligence") and opportunity.intelligence:
        intel = opportunity.intelligence
        opp_data["summary"] = intel.summary or opportunity.description or ""
        opp_data["required_requirements"] = intel.required_requirements or []

    # 1. Generate text via LLM or deterministic fallback
    generated_answer = ""
    provider_name = "DETERMINISTIC"
    model_name = "rule-based-star-v1"
    token_metrics: Dict[str, Any] = {}

    llm_provider_setting = getattr(settings, "LLM_PROVIDER", "gemini").lower()

    if not force_deterministic and llm_provider_setting != "none":
        try:
            router = LLMRouter()
            prompt = format_question_prompt(
                question_text=question.question_text,
                max_words=question.max_words,
                max_characters=question.max_characters,
                tone=tone,
                candidate_evidence=candidate_evidence,
                opportunity_data=opp_data,
                additional_guidance=additional_guidance,
            )
            primary = router.get_provider_instance(router.primary_name)
            
            if primary and getattr(primary, "api_key", None):
                logger.info(f"Drafting question answer using primary provider: {primary.get_provider_name()}")
                if hasattr(primary, "_call_gemini_api"):
                    resp = primary._call_gemini_api(prompt, enforce_json=False)
                    candidates = resp.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        generated_answer = "".join(p.get("text", "") for p in parts).strip()
                    provider_name = primary.get_provider_name()
                    model_name = primary.get_model_name()
                    token_metrics = resp.get("usageMetadata", {})
        except Exception as e:
            logger.warning(f"Hosted LLM failed for question answering ({e}), falling back to deterministic.")

    if not generated_answer:
        det_result = synthesize_deterministic_question_answer(
            question_text=question.question_text,
            max_words=question.max_words,
            max_characters=question.max_characters,
            tone=tone,
            candidate_evidence=candidate_evidence,
            opportunity_data=opp_data,
            additional_guidance=additional_guidance,
        )
        generated_answer = det_result["answer_text"]
        provider_name = det_result["provider"]
        model_name = det_result["model"]
        token_metrics = det_result["token_metrics"]

    # 2. Strict Length Enforcement (Sanity check & re-clipping)
    final_answer = enforce_strict_limits(generated_answer, question.max_words, question.max_characters)

    # 3. Grounding Verification
    citations = audit_grounding_evidence(final_answer, candidate_evidence)

    # 4. Versioning
    # Deselect older selected versions
    question.draft_versions.filter(is_selected=True).update(is_selected=False)
    next_version = (question.draft_versions.count() or 0) + 1

    version_record = QuestionDraftVersion.objects.create(
        question=question,
        version_number=next_version,
        tone=tone,
        answer_text=final_answer,
        word_count=len(final_answer.split()),
        char_count=len(final_answer),
        grounding_evidence=citations,
        provider=provider_name,
        model=model_name,
        token_metrics=token_metrics,
        is_selected=True,
    )

    # 5. Update Question
    question.answer_draft = final_answer
    question.status = QuestionStatus.READY_FOR_REVIEW
    question.save()

    # 6. Recalculate Readiness
    readiness_report = evaluate_application_readiness(application, save=True)

    # 7. Audit Activity Log
    ApplicationActivity.objects.create(
        application=application,
        activity_type=ActivityType.AI_GENERATION,
        from_status=application.status,
        to_status=application.status,
        description=f"Drafted answer for question '{question.question_text[:35]}...' (v{next_version}, {tone}) via {provider_name}. Readiness updated to {readiness_report['readiness_score']}%.",
    )

    return {
        "success": True,
        "question_id": str(question.id),
        "version_id": str(version_record.id),
        "version_number": next_version,
        "answer_text": final_answer,
        "word_count": len(final_answer.split()),
        "char_count": len(final_answer),
        "grounding_count": len(citations),
        "grounding_citations": citations,
        "readiness_score": readiness_report["readiness_score"],
        "provider": provider_name,
        "model": model_name,
    }


def enforce_strict_limits(text: str, max_words: int | None, max_characters: int | None) -> str:
    """
    Guarantees output never exceeds limits, trimming cleanly at sentence or word boundaries.
    """
    result = text.strip()

    if max_words and len(result.split()) > max_words:
        words = result.split()[:max_words]
        result = " ".join(words)
        if not result.endswith((".", "!", "?")):
            result = re.sub(r'[,;:]$', '', result) + "."

    if max_characters and len(result) > max_characters:
        result = result[:max_characters].rstrip()
        last_space = result.rfind(" ")
        if last_space > 0:
            result = result[:last_space]
        if not result.endswith((".", "!", "?")):
            result = re.sub(r'[,;:]$', '', result) + "."

    return result
