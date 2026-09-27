"""
MwohaOS Opportunity Intelligence Orchestrator — Milestone 3
Coordinates:
  CONTENT CLEANING → DETERMINISTIC EXTRACTION → AI EXTRACTION (ROUTER) → HYBRID MERGE → STORE
Manages caching, idempotency, and bounded content windows.
"""
import logging
from typing import Dict, Any, Tuple
from django.conf import settings
from django.utils import timezone
from apps.opportunities.models import Opportunity, OpportunityIntelligence
from apps.opportunities.constants import ExtractionStatus, ExtractionMethod, ExtractionProvider
from .deterministic_extraction import extract_deterministic_intelligence
from .llm_router import LLMRouter
from .security import sanitize_html
from .normalization import normalize_whitespace

logger = logging.getLogger("mwohaos.intelligence")

EXTRACTION_VERSION = "v1.0"


def clean_content_for_intelligence(opp: Opportunity) -> str:
    """
    Strips noise, preserves structure (lists, headings, deadlines),
    and limits characters according to AI_MAX_CONTENT_CHARS.
    """
    max_chars = getattr(settings, "AI_MAX_CONTENT_CHARS", 50000)

    parts = [
        f"TITLE: {opp.title}",
        f"ORGANIZATION: {opp.organization}",
        f"OPPORTUNITY TYPE: {opp.get_opportunity_type_display()}",
        f"SECTOR: {opp.get_sector_display()}",
        f"LOCATION: {opp.location or 'Not specified'}",
        f"COUNTRY: {opp.country or 'Not specified'}",
        f"REMOTE STATUS: {'Remote eligible' if opp.remote else 'Onsite / Not specified'}",
    ]
    if opp.deadline:
        parts.append(f"DEADLINE: {opp.deadline.isoformat()} ({opp.deadline_timezone})")
    if opp.compensation:
        parts.append(f"COMPENSATION / FUNDING: {opp.compensation}")
    if opp.eligibility_text:
        parts.append(f"STATED ELIGIBILITY: {opp.eligibility_text}")
    if opp.requirements:
        parts.append(f"STATED REQUIREMENTS: {opp.requirements}")
    if opp.preferred_skills:
        parts.append(f"STATED SKILLS: {opp.preferred_skills}")

    cleaned_desc = sanitize_html(opp.description or "")
    parts.append(f"DESCRIPTION AND DETAILS:\n{cleaned_desc}")

    if opp.raw_content and len(cleaned_desc) < 200:
        parts.append(f"RAW EXTRACT:\n{sanitize_html(opp.raw_content[:5000])}")

    full_text = "\n\n".join(parts)
    return normalize_whitespace(full_text)[:max_chars]


def merge_hybrid_intelligence(
    deterministic: Dict[str, Any],
    ai_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Combines deterministic extractions with AI-assisted enrichment.
    Deterministic facts (URLs, structured deadlines, exact keywords) take precedence.
    AI enriches summaries, nuanced responsibilities, who should apply, and benefits.
    """
    merged = dict(ai_data)

    # 1. Summary: prefer AI summary if rich, else fallback
    merged["summary"] = ai_data.get("summary") or deterministic.get("summary")
    merged["organization_summary"] = ai_data.get("organization_summary") or deterministic.get("organization_summary")
    merged["purpose"] = ai_data.get("purpose") or deterministic.get("purpose")

    # 2. Merge Requirements: combine non-duplicate items
    det_req = deterministic.get("required_requirements", [])
    ai_req = ai_data.get("required_requirements", [])
    merged["required_requirements"] = list(dict.fromkeys(det_req + ai_req))

    det_pref = deterministic.get("preferred_requirements", [])
    ai_pref = ai_data.get("preferred_requirements", [])
    merged["preferred_requirements"] = list(dict.fromkeys(det_pref + ai_pref))

    # 3. Merge Skills: union of deterministic known keywords and AI extracted skills
    det_skills = deterministic.get("required_skills", [])
    ai_skills = ai_data.get("required_skills", [])
    merged["required_skills"] = list(dict.fromkeys(det_skills + ai_skills))

    # 4. Merge Documents: union of checklists
    det_docs = deterministic.get("required_documents", [])
    ai_docs = ai_data.get("required_documents", [])
    doc_map = {d["name"].lower(): d for d in det_docs}
    for doc in ai_docs:
        name_k = doc["name"].lower()
        if name_k not in doc_map:
            doc_map[name_k] = doc
    merged["required_documents"] = list(doc_map.values())

    # 5. Important Dates
    det_dates = deterministic.get("important_dates", [])
    ai_dates = ai_data.get("important_dates", [])
    merged["important_dates"] = det_dates + [d for d in ai_dates if d.get("name") != "Application Deadline"]

    # 6. Eligibility merge
    det_elig = deterministic.get("eligibility", {})
    ai_elig = ai_data.get("eligibility", {})
    merged_elig = {}
    for cat in ["nationality", "residency", "age", "education", "experience", "organization_type", "business_stage", "geography", "sector", "other"]:
        items = det_elig.get(cat, []) + ai_elig.get(cat, [])
        merged_elig[cat] = list(dict.fromkeys(items))
    merged["eligibility"] = merged_elig

    return merged


def process_opportunity_intelligence(
    opportunity: Opportunity,
    force_refresh: bool = False,
) -> OpportunityIntelligence:
    """
    Main extraction service function.
    Executes:
      1. Cache / reuse check (by content hash & extraction version)
      2. Deterministic baseline extraction
      3. AI extraction via LLMRouter (Gemini -> Hugging Face -> None)
      4. Hybrid merging
      5. Atomic database persistence
    """
    # 1. Cache Check
    intel, created = OpportunityIntelligence.objects.get_or_create(opportunity=opportunity)

    if (
        not created
        and not force_refresh
        and intel.extraction_status == ExtractionStatus.COMPLETED
        and intel.confidence >= getattr(settings, "AI_MIN_CONFIDENCE_FOR_REUSE", 0.80)
        and intel.extraction_version == EXTRACTION_VERSION
    ):
        logger.info(f"Reusing existing intelligence for '{opportunity.title}' (cached).")
        return intel

    intel.extraction_status = ExtractionStatus.PROCESSING
    intel.save(update_fields=["extraction_status", "updated_at"])

    try:
        # 2. Content Preparation
        prepared_content = clean_content_for_intelligence(opportunity)

        # 3. Deterministic Extraction
        det_data = extract_deterministic_intelligence(
            title=opportunity.title,
            organization=opportunity.organization,
            description=opportunity.description or "",
            deadline=opportunity.deadline,
            deadline_timezone=opportunity.deadline_timezone,
            raw_content=opportunity.raw_content or "",
        )

        # 4. Hosted AI Extraction via Router
        router = LLMRouter()
        ai_data, provider_used, model_used = router.extract_opportunity(
            prepared_content,
            opportunity=opportunity,
        )

        now = timezone.now()

        if ai_data:
            # Hybrid merge
            final_data = merge_hybrid_intelligence(det_data, ai_data)
            method = ExtractionMethod.HYBRID
            confidence = 0.90
            status = ExtractionStatus.COMPLETED
            err_msg = ""
        else:
            # Deterministic only fallback
            final_data = det_data
            method = ExtractionMethod.DETERMINISTIC
            confidence = det_data.get("confidence", 0.65)
            # If provider is configured but failed, status is PARTIAL, else COMPLETED
            if router.primary_name == "none":
                status = ExtractionStatus.COMPLETED
                err_msg = ""
            else:
                status = ExtractionStatus.PARTIAL
                err_msg = "AI extraction unavailable or failed. Deterministic intelligence preserved."

        # 5. Persist fields
        intel.summary = final_data.get("summary", "")
        intel.organization_summary = final_data.get("organization_summary", "")
        intel.opportunity_purpose = final_data.get("purpose", "")
        intel.who_should_apply = final_data.get("who_should_apply", [])
        intel.responsibilities = final_data.get("responsibilities", [])
        intel.required_requirements = final_data.get("required_requirements", [])
        intel.preferred_requirements = final_data.get("preferred_requirements", [])
        intel.eligibility = final_data.get("eligibility", {})
        intel.required_documents = final_data.get("required_documents", [])
        intel.required_experience = final_data.get("required_experience", [])
        intel.required_skills = final_data.get("required_skills", [])
        intel.preferred_skills = final_data.get("preferred_skills", [])
        intel.benefits = final_data.get("benefits", [])
        intel.compensation_details = final_data.get("compensation_details", "")
        intel.location_details = final_data.get("location_details", "")
        intel.remote_details = final_data.get("remote_details", "")
        intel.application_process = final_data.get("application_process", [])
        intel.important_dates = final_data.get("important_dates", [])
        intel.application_instructions = final_data.get("application_instructions", [])

        intel.confidence = confidence
        intel.extraction_status = status
        intel.extraction_method = method
        intel.extraction_provider = provider_used
        intel.model_name = model_used
        intel.extraction_version = EXTRACTION_VERSION
        intel.raw_extraction = final_data
        intel.extraction_error = err_msg
        intel.last_extracted_at = now
        intel.save()

        return intel

    except Exception as e:
        logger.error(f"Intelligence extraction failed for {opportunity.id}: {e}", exc_info=True)
        intel.extraction_status = ExtractionStatus.FAILED
        intel.extraction_error = str(e)
        intel.save(update_fields=["extraction_status", "extraction_error", "updated_at"])
        return intel
