"""
MwohaOS Deterministic Eligibility Matching Service — Milestone 4
Evaluates hard eligibility constraints: nationality, residency, education, location restrictions,
deadlines, and work authorizations.
"""
from typing import Dict, Any, List, Tuple
from django.utils import timezone
from apps.profiles.models import Profile
from apps.opportunities.models import Opportunity
from apps.opportunities.constants import OpportunityStatus
from apps.matching.constants import EligibilityStatus


def evaluate_eligibility(
    profile: Profile,
    opportunity: Opportunity,
    intelligence: Any = None,
) -> Dict[str, Any]:
    """
    Evaluates whether the candidate meets explicit mandatory eligibility criteria.
    Returns:
      {
        "status": EligibilityStatus.ELIGIBLE | INELIGIBLE | UNCERTAIN,
        "confidence": float,
        "reasons": List[str],
        "hard_constraint_failed": bool,
      }
    """
    reasons = []
    hard_failed = False
    is_uncertain = False

    # 1. Deadline Check (Hard constraint)
    now = timezone.now()
    if opportunity.deadline and opportunity.deadline < now:
        hard_failed = True
        reasons.append("Opportunity deadline has already passed.")

    if opportunity.status in [OpportunityStatus.EXPIRED, OpportunityStatus.CLOSED]:
        hard_failed = True
        reasons.append(f"Opportunity status is {opportunity.get_status_display()}.")

    # 2. Extract eligibility parameters from Opportunity and OpportunityIntelligence
    stated_eligibility = opportunity.eligibility_text or ""
    intel_eligibility = getattr(intelligence, "eligibility", {}) if intelligence else {}

    # Check nationality / country restrictions
    eligible_countries = [c.lower() for c in intel_eligibility.get("nationality", [])]
    user_country = (profile.country or "").strip().lower()

    if eligible_countries:
        if not user_country:
            is_uncertain = True
            reasons.append("Opportunity has specific nationality criteria, but profile country is not set.")
        elif any(user_country in c or c in user_country for c in eligible_countries):
            reasons.append(f"Nationality eligibility satisfied: Profile country ({profile.country}) matches allowed countries.")
        elif "africa" in eligible_countries and user_country in ["kenya", "uganda", "tanzania", "rwanda", "ethiopia", "ghana", "nigeria", "south africa"]:
            reasons.append(f"Regional nationality satisfied: {profile.country} is in Africa.")
        else:
            hard_failed = True
            reasons.append(f"Ineligible nationality: Required {eligible_countries}, profile is {profile.country}.")

    # 3. Explicit Ineligible geographic contradiction in description or eligibility text
    corpus = f"{opportunity.title} {opportunity.description} {stated_eligibility}".lower()

    # Case: Explicitly requires Canadian/US/EU citizenship or work authorization
    if "must be based in canada" in corpus or "canadian work authorization" in corpus:
        if user_country != "canada":
            hard_failed = True
            reasons.append("Opportunity explicitly requires candidates to be based in Canada with Canadian work authorization.")

    if "must be based in the us" in corpus or "us work authorization required" in corpus or "us citizens only" in corpus:
        if user_country not in ["united states", "usa", "us"]:
            hard_failed = True
            reasons.append("Opportunity explicitly requires US location / authorization.")

    # 4. Education level check
    req_degrees = [d.lower() for d in intel_eligibility.get("education", [])]
    profile_educations = list(profile.educations.all())

    if req_degrees:
        profile_degree_texts = " ".join([f"{e.degree} {e.field_of_study}".lower() for e in profile_educations])
        if not profile_degree_texts:
            is_uncertain = True
            reasons.append("Education requirements specified, but profile has no education records.")
        else:
            # Check bachelor / master / phd
            for deg in req_degrees:
                if "phd" in deg or "doctorate" in deg:
                    if not any(d in profile_degree_texts for d in ["phd", "doctorate"]):
                        is_uncertain = True
                        reasons.append("PhD/Doctorate degree requested; not conclusively established in profile.")
                elif "master" in deg or "msc" in deg:
                    if not any(d in profile_degree_texts for d in ["master", "msc", "m.sc"]):
                        is_uncertain = True
                        reasons.append("Master's degree requested; profile indicates alternative degree level.")

    # 5. Location / Non-remote check
    if not opportunity.remote:
        opp_loc = (opportunity.location or "").lower()
        opp_country = (opportunity.country or "").lower()
        if opp_country and user_country and opp_country != user_country:
            # Check if user stated flexible / willing to relocate
            prefs = getattr(profile, "preferences", None)
            target_countries = (prefs.target_countries or "").lower() if prefs else ""
            if opp_country not in target_countries:
                reasons.append(f"On-site opportunity located in {opportunity.location or opportunity.country}, differing from candidate country ({profile.country}).")

    # Final status determination
    if hard_failed:
        status = EligibilityStatus.INELIGIBLE
        confidence = 0.95
    elif is_uncertain:
        status = EligibilityStatus.UNCERTAIN
        confidence = 0.70
    else:
        status = EligibilityStatus.ELIGIBLE
        confidence = 0.90
        if not reasons:
            reasons.append("No conflicting eligibility restrictions detected. Candidate meets stated criteria.")

    return {
        "status": status,
        "confidence": confidence,
        "reasons": reasons,
        "hard_constraint_failed": hard_failed,
    }
