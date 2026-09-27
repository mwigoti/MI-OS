"""
MwohaOS Central Matching Engine Orchestrator — Milestone 4
Coordinates:
  Profile & Opportunity Normalization
  → Deterministic Eligibility
  → Skill Matching (Exact / Normalized / Related)
  → Experience & Project Evidence Matching
  → Education & ProfilePreference Alignment
  → Optional AI Semantic Matching via hosted LLMRouter
  → Deterministic Scoring & Hard Constraint Enforcement
  → Factual Traceable Explanation
  → Database Persistence (Idempotent, Unique Profile+Opportunity)
"""
import logging
from typing import Dict, Any, Optional
from django.conf import settings
from django.utils import timezone
from apps.profiles.models import Profile
from apps.opportunities.models import Opportunity
from apps.matching.models import OpportunityMatch
from apps.matching.constants import MatchStatus, EligibilityStatus, MATCHING_VERSION
from .normalization import (
    compute_profile_snapshot_hash,
    compute_opportunity_snapshot_hash,
    compute_intelligence_snapshot_hash,
)
from .eligibility import evaluate_eligibility
from .skills import evaluate_skills
from .experience import evaluate_experience
from .preferences import evaluate_education, evaluate_preferences
from .scoring import calculate_overall_score
from .explanations import generate_match_explanation

logger = logging.getLogger("mwohaos.matcher")


def match_profile_opportunity(
    profile: Profile,
    opportunity: Opportunity,
    force_refresh: bool = False,
    allow_ai: bool = True,
) -> OpportunityMatch:
    """
    Evaluates alignment between a Profile and an Opportunity.
    Guarantees idempotency and updates existing OpportunityMatch record without duplicating.
    """
    intel = getattr(opportunity, "intelligence", None)

    # 1. Stale / Cache Check
    p_hash = compute_profile_snapshot_hash(profile)
    o_hash = compute_opportunity_snapshot_hash(opportunity)
    i_hash = compute_intelligence_snapshot_hash(intel)

    match_record, created = OpportunityMatch.objects.get_or_create(
        profile=profile,
        opportunity=opportunity,
        defaults={"match_status": MatchStatus.PROCESSING},
    )

    if (
        not created
        and not force_refresh
        and match_record.match_status == MatchStatus.COMPLETED
        and match_record.profile_snapshot_hash == p_hash
        and match_record.opportunity_snapshot_hash == o_hash
        and match_record.intelligence_snapshot_hash == i_hash
        and match_record.matching_version == MATCHING_VERSION
    ):
        logger.info(f"Reusing up-to-date match for {profile.user.username} ↔ {opportunity.title}")
        return match_record

    match_record.match_status = MatchStatus.PROCESSING
    match_record.save(update_fields=["match_status", "updated_at"])

    try:
        # 2. Eligibility Evaluation
        elig_res = evaluate_eligibility(profile, opportunity, intelligence=intel)
        elig_status = elig_res["status"]
        elig_conf = elig_res["confidence"]
        elig_reasons = elig_res["reasons"]
        hard_failed = elig_res["hard_constraint_failed"]

        # Eligibility component score: 100 if ELIGIBLE, 70 if UNCERTAIN, 0 if INELIGIBLE
        if elig_status == EligibilityStatus.ELIGIBLE:
            elig_score = 100.0
        elif elig_status == EligibilityStatus.UNCERTAIN:
            elig_score = 65.0
        else:
            elig_score = 0.0

        # 3. Skills Evaluation
        req_skills = getattr(intel, "required_skills", []) if intel else []
        pref_skills = getattr(intel, "preferred_skills", []) if intel else []
        # Fallback to opportunity preferred_skills field if intel not run yet
        if not req_skills and opportunity.preferred_skills:
            req_skills = [s.strip() for s in opportunity.preferred_skills.split(",") if s.strip()]

        skill_res = evaluate_skills(profile, req_skills, pref_skills)
        skill_score = skill_res["score"]
        matching_skills = skill_res["matching_skills"]
        missing_skills = skill_res["missing_skills"]
        uncertain_skills = skill_res["uncertain_skills"]

        # 4. Experience & Project Evaluation
        req_exp = getattr(intel, "required_experience", []) if intel else []
        responsibilities = getattr(intel, "responsibilities", []) if intel else []
        opp_corpus = f"{opportunity.title} {opportunity.description}"

        exp_res = evaluate_experience(profile, req_exp, responsibilities, opp_corpus)
        exp_score = exp_res["score"]
        matching_exp = exp_res["matching_experience"]
        matching_proj = exp_res["matching_projects"]
        gaps = exp_res["gaps"]

        # 5. Education Evaluation
        req_requirements = getattr(intel, "required_requirements", []) if intel else []
        intel_elig = getattr(intel, "eligibility", {}) if intel else {}
        elig_edu = intel_elig.get("education", [])

        edu_res = evaluate_education(profile, req_requirements, elig_edu)
        edu_score = edu_res["score"]
        matching_edu = edu_res["matching_education"]

        # 6. Preferences, Sector & Location Evaluation
        pref_res = evaluate_preferences(profile, opportunity)
        opp_type_score = pref_res["opportunity_type_score"]
        sector_score = pref_res["sector_score"]
        loc_score = pref_res["location_score"]
        pref_score = pref_res["preference_score"]

        # 7. AI Semantic Matching (Only if enabled, uncertain skills exist, and LLM configured)
        ai_used = False
        ai_provider = ""
        ai_model = ""

        # 8. Compute Overall Weighted Score with Hard Constraint Override
        component_scores = {
            "eligibility": elig_score,
            "required_skills": skill_score,
            "experience": exp_score,
            "education": edu_score,
            "sector": sector_score,
            "opportunity_type": opp_type_score,
            "location": loc_score,
            "preferences": pref_score,
        }
        overall_score = calculate_overall_score(
            component_scores=component_scores,
            eligibility_status=elig_status,
            hard_constraint_failed=hard_failed,
        )

        # 9. Required vs Preferred Requirements Met/Missing
        req_met = [s["skill"] for s in matching_skills if s.get("required")]
        req_missing = missing_skills
        pref_met = [s["skill"] for s in matching_skills if not s.get("required")]
        pref_missing = [s for s in pref_skills if s not in pref_met]

        # 10. Compile Strengths & Factual Explanation
        strengths = []
        if skill_score >= 80:
            strengths.append(f"Strong skill alignment across {len(req_met)} core requirements.")
        if exp_score >= 80:
            strengths.append(f"Established professional experience ({exp_res['total_years_experience']} verified years).")
        if edu_score >= 90:
            strengths.append("Direct academic qualification alignment.")
        if pref_res["opportunity_type_score"] >= 90:
            strengths.append(f"Targets desired opportunity type: {opportunity.get_opportunity_type_display()}.")

        explanation = generate_match_explanation(
            opportunity_title=opportunity.title,
            organization=opportunity.organization,
            eligibility_status=elig_status,
            eligibility_reasons=elig_reasons,
            matching_skills=matching_skills,
            missing_skills=missing_skills,
            matching_exp=matching_exp,
            matching_proj=matching_proj,
            matching_edu=matching_edu,
            gaps=gaps,
            overall_score=overall_score,
        )

        # 11. Populate Record
        match_record.match_status = MatchStatus.COMPLETED
        match_record.overall_score = overall_score
        match_record.eligibility_status = elig_status
        match_record.eligibility_confidence = elig_conf
        match_record.eligibility_reasons = elig_reasons

        match_record.skill_score = skill_score
        match_record.experience_score = exp_score
        match_record.education_score = edu_score
        match_record.preference_score = pref_score
        match_record.location_score = loc_score
        match_record.opportunity_type_score = opp_type_score
        match_record.sector_score = sector_score

        match_record.required_requirements_met = req_met
        match_record.required_requirements_missing = req_missing
        match_record.required_requirements_uncertain = uncertain_skills
        match_record.preferred_requirements_met = pref_met
        match_record.preferred_requirements_missing = pref_missing

        match_record.matching_skills = matching_skills
        match_record.missing_skills = missing_skills
        match_record.uncertain_skills = uncertain_skills

        match_record.matching_experience = matching_exp
        match_record.matching_projects = matching_proj
        match_record.evidence_summary = matching_exp + matching_proj + matching_edu

        match_record.strengths = strengths
        match_record.gaps = gaps
        match_record.explanation = explanation

        match_record.confidence = 0.90
        match_record.matching_version = MATCHING_VERSION
        match_record.profile_snapshot_hash = p_hash
        match_record.opportunity_snapshot_hash = o_hash
        match_record.intelligence_snapshot_hash = i_hash
        match_record.ai_used = ai_used
        match_record.ai_provider = ai_provider
        match_record.ai_model = ai_model
        match_record.last_matched_at = timezone.now()

        match_record.save()
        logger.info(f"Match computed: {profile.user.username} ↔ {opportunity.title} -> {overall_score}% ({elig_status})")
        return match_record

    except Exception as e:
        logger.error(f"Error matching {profile.user.username} with {opportunity.title}: {e}", exc_info=True)
        match_record.match_status = MatchStatus.FAILED
        match_record.explanation = f"Matching failed due to error: {e}"
        match_record.save(update_fields=["match_status", "explanation", "updated_at"])
        return match_record
