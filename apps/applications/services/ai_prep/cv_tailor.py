"""
MwohaOS CV Tailoring & ATS Alignment Engine — Milestone 6: AI Preparation
Optimizes resume bullets, prioritizes skills, provides ATS keyword match coverage,
and generates structured CV tailoring artifacts for applications.
"""
import json
import logging
from typing import Dict, Any, Optional
from django.conf import settings

from apps.applications.models import (
    Application,
    ApplicationDocument,
    ApplicationDocumentVersion,
    CVTailoringResult,
    ApplicationActivity,
)
from apps.applications.constants import (
    DocumentRole,
    DocumentAttachmentStatus,
    ActivityType,
)
from apps.applications.services.readiness import evaluate_application_readiness
from apps.opportunities.services.llm_router import LLMRouter
from .prompts import format_cv_tailor_prompt
from .evidence_grounding import gather_candidate_evidence, audit_grounding_evidence
from .deterministic_ai_prep import synthesize_deterministic_cv_tailoring

logger = logging.getLogger("mwohaos.ai_prep.cv_tailor")


def generate_cv_tailoring(
    application: Application,
    update_cv_document: bool = True,
    force_deterministic: bool = False,
) -> Dict[str, Any]:
    """
    Produces structured CV tailoring recommendations and updates CVTailoringResult.
    Optionally updates or creates the tailored CV ApplicationDocument.
    """
    profile = application.profile
    opportunity = application.opportunity

    candidate_evidence = gather_candidate_evidence(profile)

    opp_data: Dict[str, Any] = {
        "title": application.display_title,
        "organization": application.display_organization,
        "summary": opportunity.description or "",
        "required_requirements": [],
        "required_skills": [],
        "preferred_skills": [],
        "responsibilities": [],
    }

    if hasattr(opportunity, "intelligence") and opportunity.intelligence:
        intel = opportunity.intelligence
        opp_data["summary"] = intel.summary or opportunity.description or ""
        opp_data["required_requirements"] = intel.required_requirements or []
        opp_data["required_skills"] = intel.required_skills or []
        opp_data["preferred_skills"] = intel.preferred_skills or []
        opp_data["responsibilities"] = intel.responsibilities or []

    # 1. Generate via LLM or deterministic fallback
    tailoring_data: Dict[str, Any] = {}
    provider_name = "DETERMINISTIC"
    model_name = "rule-based-v1"
    token_metrics: Dict[str, Any] = {}

    llm_provider_setting = getattr(settings, "LLM_PROVIDER", "gemini").lower()

    if not force_deterministic and llm_provider_setting != "none":
        try:
            router = LLMRouter()
            prompt = format_cv_tailor_prompt(candidate_evidence, opp_data)
            primary = router.get_provider_instance(router.primary_name)
            
            if primary and getattr(primary, "api_key", None):
                logger.info(f"Generating CV tailoring using primary provider: {primary.get_provider_name()}")
                if hasattr(primary, "_call_gemini_api"):
                    resp = primary._call_gemini_api(prompt, enforce_json=True)
                    candidates = resp.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        raw_json = "".join(p.get("text", "") for p in parts).strip()
                        tailoring_data = json.loads(raw_json)
                    provider_name = primary.get_provider_name()
                    model_name = primary.get_model_name()
                    token_metrics = resp.get("usageMetadata", {})
        except Exception as e:
            logger.warning(f"Hosted LLM failed for CV tailoring ({e}), falling back to deterministic generation.")

    if not tailoring_data or not isinstance(tailoring_data, dict) or "targeted_summary" not in tailoring_data:
        det_result = synthesize_deterministic_cv_tailoring(candidate_evidence, opp_data)
        tailoring_data = det_result
        provider_name = det_result["provider"]
        model_name = det_result["model"]
        token_metrics = det_result["token_metrics"]

    targeted_summary = tailoring_data.get("targeted_summary", "")
    prioritized_skills = tailoring_data.get("prioritized_skills", [])
    tailored_bullets = tailoring_data.get("tailored_experience_bullets", [])
    selected_projects = tailoring_data.get("selected_projects", [])
    ats_coverage = tailoring_data.get("ats_keyword_coverage", {})

    # 2. Persist CVTailoringResult
    cv_result, _ = CVTailoringResult.objects.update_or_create(
        application=application,
        defaults={
            "targeted_summary": targeted_summary,
            "prioritized_skills": prioritized_skills,
            "tailored_experience_bullets": tailored_bullets,
            "selected_projects": selected_projects,
            "ats_keyword_coverage": ats_coverage,
            "provider": provider_name,
            "model": model_name,
            "token_metrics": token_metrics,
        },
    )

    # 3. Format complete markdown CV document artifact
    cv_markdown = format_tailored_cv_markdown(
        candidate_evidence,
        targeted_summary,
        prioritized_skills,
        tailored_bullets,
        selected_projects,
        opp_data,
    )

    citations = audit_grounding_evidence(cv_markdown, candidate_evidence)

    # 4. Update / create ApplicationDocument if requested
    version_number = 1
    if update_cv_document:
        app_doc = ApplicationDocument.objects.filter(
            application=application,
            document_role__in=[DocumentRole.CV, DocumentRole.RESUME],
        ).first()

        tailoring_notes = (
            f"Tailored for {opp_data['title']} at {opp_data['organization']}. "
            f"ATS Keyword Alignment: {ats_coverage.get('coverage_score', 80)}%."
        )

        if not app_doc:
            app_doc = ApplicationDocument.objects.create(
                application=application,
                document_role=DocumentRole.CV,
                title=f"Tailored CV - {application.display_title[:40]}",
                is_required=True,
                is_tailored=True,
                tailored_notes=tailoring_notes,
                content=cv_markdown,
                status=DocumentAttachmentStatus.ATTACHED,
            )
        else:
            app_doc.is_tailored = True
            app_doc.tailored_notes = tailoring_notes
            app_doc.content = cv_markdown
            app_doc.status = DocumentAttachmentStatus.ATTACHED
            app_doc.save()

        app_doc.versions.filter(is_active=True).update(is_active=False)
        version_number = (app_doc.versions.count() or 0) + 1

        ApplicationDocumentVersion.objects.create(
            application_document=app_doc,
            version_number=version_number,
            title=f"Tailored CV Draft v{version_number}",
            content=cv_markdown,
            tailoring_notes=tailoring_notes,
            grounding_evidence=citations,
            provider=provider_name,
            model=model_name,
            token_metrics=token_metrics,
            is_active=True,
        )

    # 5. Recalculate Readiness
    readiness_report = evaluate_application_readiness(application, save=True)

    # 6. Audit Activity Log
    ApplicationActivity.objects.create(
        application=application,
        activity_type=ActivityType.AI_GENERATION,
        from_status=application.status,
        to_status=application.status,
        description=f"Generated tailored CV and ATS optimization ({ats_coverage.get('coverage_score', 80)}% keyword match) via {provider_name}.",
    )

    return {
        "success": True,
        "tailoring_id": str(cv_result.id),
        "targeted_summary": targeted_summary,
        "prioritized_skills": prioritized_skills,
        "tailored_bullets": tailored_bullets,
        "selected_projects": selected_projects,
        "ats_keyword_coverage": ats_coverage,
        "cv_markdown": cv_markdown,
        "grounding_count": len(citations),
        "readiness_score": readiness_report["readiness_score"],
        "provider": provider_name,
        "model": model_name,
    }


def format_tailored_cv_markdown(
    candidate_evidence: Dict[str, Any],
    targeted_summary: str,
    prioritized_skills: list,
    tailored_bullets: list,
    selected_projects: list,
    opp_data: Dict[str, Any],
) -> str:
    """
    Renders structured resume data into clean, exportable Markdown.
    """
    name = candidate_evidence.get("full_name") or "Applicant"
    email = candidate_evidence.get("email") or ""
    location = candidate_evidence.get("location") or ""
    headline = candidate_evidence.get("headline") or ""

    md_lines = [
        f"# {name}",
        f"**{headline}** | {location} | {email}",
        "",
        "## Professional Summary",
        targeted_summary,
        "",
        "## Core Competencies & Technical Skills",
    ]

    # Skills line
    matched = [s["name"] for s in prioritized_skills if s.get("is_matched_requirement")]
    other = [s["name"] for s in prioritized_skills if not s.get("is_matched_requirement")]
    
    if matched:
        md_lines.append(f"- **Target Proficiencies**: {', '.join(matched)}")
    if other:
        md_lines.append(f"- **Additional Competencies**: {', '.join(other[:8])}")
    md_lines.append("")

    # Experience section
    md_lines.append("## Professional Experience")
    bullet_map = {b.get("experience_id"): b.get("tailored_bullets", []) for b in tailored_bullets if isinstance(b, dict)}

    for exp in candidate_evidence.get("experiences", []):
        exp_id = exp.get("id")
        title = exp.get("title")
        org = exp.get("organization")
        dates = f"{exp.get('start_date', '')} – {exp.get('end_date', 'Present')}"
        md_lines.append(f"### {title} | {org} ({dates})")
        
        custom_bullets = bullet_map.get(exp_id)
        if custom_bullets:
            for b in custom_bullets:
                md_lines.append(f"- {b}")
        else:
            achieve = exp.get("achievements") or exp.get("description") or ""
            md_lines.append(f"- {achieve}")
        md_lines.append("")

    # Projects section
    if selected_projects:
        md_lines.append("## Key Projects & Impact")
        for p in selected_projects:
            title = p.get("title")
            highlight = p.get("alignment_highlight")
            md_lines.append(f"- **{title}**: {highlight}")
        md_lines.append("")

    # Education section
    education = candidate_evidence.get("education", [])
    if education:
        md_lines.append("## Education")
        for edu in education:
            deg = edu.get("degree")
            field = edu.get("field_of_study")
            inst = edu.get("institution")
            yr = edu.get("graduation_year")
            md_lines.append(f"- **{deg} in {field}**, {inst} ({yr})")

    return "\n".join(md_lines)
