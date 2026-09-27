"""
MwohaOS Education & Preference Matching Services — Milestone 4
Evaluates degrees, academic fields, opportunity type preferences, sector alignment, and work modes.
"""
from typing import Dict, Any, List
from apps.profiles.models import Profile, Education, ProfilePreference
from apps.opportunities.models import Opportunity
from apps.matching.constants import LocationMatchType


def evaluate_education(
    profile: Profile,
    required_requirements: List[str],
    eligibility_education: List[str],
) -> Dict[str, Any]:
    """
    Evaluates profile education against degree requirements (Bachelor, Master, PhD, fields).
    """
    educations = list(profile.educations.all())
    if not educations:
        # Distinguish between missing data vs unqualified
        return {
            "score": 50.0,
            "status": "UNCERTAIN",
            "matching_education": [],
            "reason": "Profile has no education records. Adding education credentials may improve accuracy.",
        }

    # Combine requirement strings
    req_corpus = " ".join(required_requirements + eligibility_education).lower()

    requires_phd = "phd" in req_corpus or "doctorate" in req_corpus
    requires_masters = "master" in req_corpus or "msc" in req_corpus or "m.sc" in req_corpus
    requires_bachelor = "bachelor" in req_corpus or "bsc" in req_corpus or "b.sc" in req_corpus or "undergraduate" in req_corpus or "degree" in req_corpus

    matching_edu = []
    satisfied = False

    for edu in educations:
        deg = edu.degree.lower()
        field = edu.field_of_study.lower()
        full_edu = f"{deg} {field}"

        has_bachelor = any(b in deg for b in ["bachelor", "bsc", "b.sc", "beng", "b.eng"])
        has_masters = any(m in deg for m in ["master", "msc", "m.sc", "meng", "m.eng"])
        has_phd = any(p in deg for p in ["phd", "doctorate", "dphil"])

        # Check degree level match
        level_match = False
        if requires_phd and has_phd:
            level_match = True
        elif requires_masters and (has_masters or has_phd):
            level_match = True
        elif requires_bachelor and (has_bachelor or has_masters or has_phd):
            level_match = True
        elif not requires_phd and not requires_masters and not requires_bachelor:
            # Opportunity did not strictly mandate degree
            level_match = True

        # Check domain relevance (e.g. Geospatial, Computer Science, Engineering)
        field_match = any(
            f in req_corpus or f in "geospatial engineering science technology computer remote sensing earth observation"
            for f in field.split()
        )

        if level_match or field_match:
            matching_edu.append({
                "institution": edu.institution,
                "degree": edu.degree,
                "field_of_study": edu.field_of_study,
                "dates": f"{edu.start_date or ''} - {edu.end_date or 'Present'}",
                "level_satisfied": level_match,
                "field_relevant": field_match,
            })
            if level_match:
                satisfied = True

    if satisfied:
        score = 100.0
        status = "SATISFIED"
        reason = "Education degree and field requirements satisfied by profile credentials."
    elif requires_phd or requires_masters or requires_bachelor:
        score = 40.0
        status = "PARTIAL_OR_UNMET"
        reason = "Specific degree level requested; profile contains alternative academic background."
    else:
        score = 85.0
        status = "SATISFIED"
        reason = "No rigid degree restriction specified; profile education is aligned."

    return {
        "score": score,
        "status": status,
        "matching_education": matching_edu,
        "reason": reason,
    }


def evaluate_preferences(
    profile: Profile,
    opportunity: Opportunity,
) -> Dict[str, Any]:
    """
    Evaluates user ProfilePreferences against the Opportunity:
    - Opportunity Type match (e.g. Job vs Fellowship vs Grant)
    - Sector alignment
    - Work Mode / Remote match
    - Country / Regional match
    """
    prefs: ProfilePreference = getattr(profile, "preferences", None)
    if not prefs:
        return {
            "opportunity_type_score": 80.0,
            "sector_score": 80.0,
            "location_score": 80.0,
            "preference_score": 80.0,
            "location_match_type": LocationMatchType.UNKNOWN,
            "alignment_notes": ["No explicit profile preferences set; default neutral baseline applied."],
        }

    alignment_notes = []

    # 1. Opportunity Type
    target_types = [t.upper() for t in (prefs.target_opportunity_types or [])]
    opp_type = opportunity.opportunity_type.upper()
    opp_type_score = 50.0

    if not target_types or opp_type in target_types:
        opp_type_score = 100.0
        alignment_notes.append(f"Opportunity type '{opportunity.get_opportunity_type_display()}' aligns with user targets.")
    elif any(t in opp_type or opp_type in t for t in target_types):
        opp_type_score = 80.0
    else:
        opp_type_score = 40.0

    # 2. Sector Alignment
    target_sectors = [s.upper() for s in (prefs.target_sectors or [])]
    opp_sector = opportunity.sector.upper()
    sector_score = 50.0

    if not target_sectors or opp_sector in target_sectors:
        sector_score = 100.0
        alignment_notes.append(f"Sector '{opportunity.get_sector_display()}' directly matches preferred industry sectors.")
    elif opp_sector in ["GEOSPATIAL", "REMOTE_SENSING", "EARTH_OBSERVATION", "SPACE", "CLIMATE", "AGRICULTURE"]:
        # Strong thematic cluster
        if any(s in ["GEOSPATIAL", "REMOTE_SENSING", "EARTH_OBSERVATION", "CLIMATE", "AGRICULTURE"] for s in target_sectors):
            sector_score = 90.0
            alignment_notes.append(f"Strong domain synergy between {opportunity.get_sector_display()} and target sector interests.")
    else:
        sector_score = 50.0

    # 3. Location & Remote
    work_modes = [w.upper() for w in (prefs.work_modes or [])]
    loc_score = 70.0
    loc_match_type = LocationMatchType.MATCH

    if opportunity.remote:
        loc_score = 100.0
        loc_match_type = LocationMatchType.NOT_APPLICABLE
        alignment_notes.append("Opportunity is remote-eligible.")
    else:
        user_country = (profile.country or "").lower()
        opp_country = (opportunity.country or "").lower()
        target_countries = (prefs.target_countries or "").lower()

        if opp_country and user_country and opp_country == user_country:
            loc_score = 100.0
            loc_match_type = LocationMatchType.MATCH
            alignment_notes.append(f"Onsite location in {profile.country} matches candidate country.")
        elif opp_country and target_countries and opp_country in target_countries:
            loc_score = 90.0
            loc_match_type = LocationMatchType.MATCH
            alignment_notes.append(f"Location in {opportunity.country} matches target country preferences.")
        elif "REMOTE_ONLY" in work_modes:
            loc_score = 30.0
            loc_match_type = LocationMatchType.MISMATCH
            alignment_notes.append("Candidate prefers remote-only, but opportunity is onsite.")
        else:
            loc_score = 50.0
            loc_match_type = LocationMatchType.PARTIAL_MATCH

    # Combined preference score
    preference_score = (opp_type_score * 0.4) + (sector_score * 0.4) + (loc_score * 0.2)

    return {
        "opportunity_type_score": round(opp_type_score, 1),
        "sector_score": round(sector_score, 1),
        "location_score": round(loc_score, 1),
        "preference_score": round(preference_score, 1),
        "location_match_type": loc_match_type,
        "alignment_notes": alignment_notes,
    }
