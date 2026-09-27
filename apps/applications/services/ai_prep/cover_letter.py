"""
MwohaOS AI Cover Letter Generator — Milestone 6: AI Preparation
Synthesizes bespoke, evidence-grounded cover letters tailored to target opportunities,
with full version control, grounding verification, and readiness recalculation.
"""
import logging
from typing import Dict, Any, Optional
from django.conf import settings
from django.utils import timezone

from apps.applications.models import (
    Application,
    ApplicationDocument,
    ApplicationDocumentVersion,
    ApplicationActivity,
)
from apps.applications.constants import (
    DocumentRole,
    DocumentAttachmentStatus,
    ActivityType,
)
from apps.applications.services.readiness import evaluate_application_readiness
from apps.opportunities.services.llm_router import LLMRouter
from .prompts import format_cover_letter_prompt
from .evidence_grounding import gather_candidate_evidence, audit_grounding_evidence
from .deterministic_ai_prep import synthesize_deterministic_cover_letter

logger = logging.getLogger("mwohaos.ai_prep.cover_letter")


def generate_tailored_cover_letter(
    application: Application,
    tone: str = "PROFESSIONAL",
    custom_guidance: str = "",
    force_deterministic: bool = False,
) -> Dict[str, Any]:
    """
    Generates an evidence-grounded, tailored Cover Letter for an Application.
    Creates or updates the ApplicationDocument and archives previous iterations as versions.
    """
    profile = application.profile
    opportunity = application.opportunity

    # 1. Gather candidate profile facts & opportunity intelligence
    candidate_evidence = gather_candidate_evidence(profile)

    opp_data: Dict[str, Any] = {
        "title": application.display_title,
        "organization": application.display_organization,
        "purpose": "",
        "summary": opportunity.description or "",
        "required_requirements": [],
        "required_skills": [],
        "preferred_skills": [],
        "responsibilities": [],
    }

    if hasattr(opportunity, "intelligence") and opportunity.intelligence:
        intel = opportunity.intelligence
        opp_data["purpose"] = intel.purpose or ""
        opp_data["summary"] = intel.summary or opportunity.description or ""
        opp_data["required_requirements"] = intel.required_requirements or []
        opp_data["required_skills"] = intel.required_skills or []
        opp_data["preferred_skills"] = intel.preferred_skills or []
        opp_data["responsibilities"] = intel.responsibilities or []

    # 2. Call LLM or deterministic engine
    generated_text = ""
    tailoring_notes = ""
    provider_name = "DETERMINISTIC"
    model_name = "rule-based-v1"
    token_metrics: Dict[str, Any] = {}

    llm_provider_setting = getattr(settings, "LLM_PROVIDER", "gemini").lower()

    if not force_deterministic and llm_provider_setting != "none":
        try:
            router = LLMRouter()
            prompt = format_cover_letter_prompt(candidate_evidence, opp_data, tone=tone, custom_guidance=custom_guidance)
            primary = router.get_provider_instance(router.primary_name)
            
            if primary and getattr(primary, "api_key", None):
                logger.info(f"Generating cover letter using primary provider: {primary.get_provider_name()}")
                # Use summarize / text generation or custom call
                if hasattr(primary, "_call_gemini_api"):
                    resp = primary._call_gemini_api(prompt, enforce_json=False)
                    candidates = resp.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        generated_text = "".join(p.get("text", "") for p in parts).strip()
                    provider_name = primary.get_provider_name()
                    model_name = primary.get_model_name()
                    token_metrics = resp.get("usageMetadata", {})
        except Exception as e:
            logger.warning(f"Hosted LLM failed for cover letter ({e}), falling back to deterministic generation.")

    if not generated_text:
        det_result = synthesize_deterministic_cover_letter(candidate_evidence, opp_data, tone=tone, custom_guidance=custom_guidance)
        generated_text = det_result["content"]
        tailoring_notes = det_result["tailoring_notes"]
        provider_name = det_result["provider"]
        model_name = det_result["model"]
        token_metrics = det_result["token_metrics"]
    else:
        tailoring_notes = f"Generated with {provider_name} ({model_name}) with {tone} tone targeting {opp_data['title']} at {opp_data['organization']}."

    # 3. Grounding Verification Audit
    citations = audit_grounding_evidence(generated_text, candidate_evidence)

    # 4. Attach to ApplicationDocument
    app_doc = ApplicationDocument.objects.filter(
        application=application,
        document_role=DocumentRole.COVER_LETTER,
    ).first()

    if not app_doc:
        app_doc = ApplicationDocument.objects.create(
            application=application,
            document_role=DocumentRole.COVER_LETTER,
            title=f"Cover Letter - {application.display_title[:40]}",
            is_required=True,
            is_tailored=True,
            tailored_notes=tailoring_notes,
            content=generated_text,
            status=DocumentAttachmentStatus.ATTACHED,
        )
    else:
        app_doc.is_tailored = True
        app_doc.tailored_notes = tailoring_notes
        app_doc.content = generated_text
        app_doc.status = DocumentAttachmentStatus.ATTACHED
        app_doc.save()

    # 5. Versioning
    # Deactivate older active versions
    app_doc.versions.filter(is_active=True).update(is_active=False)
    next_version = (app_doc.versions.count() or 0) + 1

    version_record = ApplicationDocumentVersion.objects.create(
        application_document=app_doc,
        version_number=next_version,
        title=f"Draft v{next_version} ({tone})",
        content=generated_text,
        tailoring_notes=tailoring_notes,
        grounding_evidence=citations,
        provider=provider_name,
        model=model_name,
        token_metrics=token_metrics,
        is_active=True,
    )

    # 6. Recalculate Readiness
    readiness_report = evaluate_application_readiness(application, save=True)

    # 7. Audit Activity Log
    ApplicationActivity.objects.create(
        application=application,
        activity_type=ActivityType.AI_GENERATION,
        from_status=application.status,
        to_status=application.status,
        description=f"Generated tailored Cover Letter (v{next_version}) via {provider_name} with {len(citations)} verified citations. Readiness score updated to {readiness_report['readiness_score']}%.",
    )

    return {
        "success": True,
        "document_id": str(app_doc.id),
        "version_id": str(version_record.id),
        "version_number": next_version,
        "content": generated_text,
        "tailoring_notes": tailoring_notes,
        "grounding_citations": citations,
        "grounding_count": len(citations),
        "readiness_score": readiness_report["readiness_score"],
        "provider": provider_name,
        "model": model_name,
    }
