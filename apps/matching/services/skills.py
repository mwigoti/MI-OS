"""
MwohaOS Transparent Skill Matching Service — Milestone 4
Distinguishes between EXACT, NORMALIZED, RELATED, and MISSING skills without overclaiming.
"""
from typing import Dict, Any, List
from apps.profiles.models import Profile, Skill
from apps.matching.constants import SkillMatchType
from .normalization import normalize_skill, are_skills_related


def evaluate_skills(
    profile: Profile,
    required_skills: List[str],
    preferred_skills: List[str],
) -> Dict[str, Any]:
    """
    Evaluates profile skills against opportunity requirements.
    Calculates skill match percentage, matches list with evidence, missing skills, and uncertainty.
    """
    profile_skills = list(profile.skills.all())
    # Map normalized name to profile skill object
    profile_skill_map: Dict[str, Skill] = {}
    for s in profile_skills:
        norm = normalize_skill(s.name)
        profile_skill_map[norm] = s

    matching_skills = []
    missing_skills = []
    uncertain_skills = []

    satisfied_required_count = 0.0

    # 1. Evaluate Required Skills
    for req in required_skills:
        req_clean = req.strip()
        if not req_clean:
            continue
        norm_req = normalize_skill(req_clean)

        # Check Exact Match (raw case-insensitive)
        exact_match = next((s for s in profile_skills if s.name.strip().lower() == req_clean.lower()), None)
        if exact_match:
            matching_skills.append({
                "skill": req_clean,
                "profile_skill": exact_match.name,
                "match_type": SkillMatchType.EXACT,
                "required": True,
                "evidence": f"Profile Skill: {exact_match.name} ({exact_match.get_level_display()})",
            })
            satisfied_required_count += 1.0
            continue

        # Check Normalized Match
        if norm_req in profile_skill_map:
            p_skill = profile_skill_map[norm_req]
            matching_skills.append({
                "skill": req_clean,
                "profile_skill": p_skill.name,
                "match_type": SkillMatchType.NORMALIZED,
                "required": True,
                "evidence": f"Normalized alias match with Profile Skill: {p_skill.name}",
            })
            satisfied_required_count += 1.0
            continue

        # Check Related Match
        related_skill = None
        for p_norm, p_skill in profile_skill_map.items():
            if are_skills_related(norm_req, p_norm):
                related_skill = p_skill
                break

        if related_skill:
            matching_skills.append({
                "skill": req_clean,
                "profile_skill": related_skill.name,
                "match_type": SkillMatchType.RELATED,
                "required": True,
                "evidence": f"Related competency via Profile Skill: {related_skill.name}",
            })
            satisfied_required_count += 0.7  # Partial credit for related skill
            continue

        # Missing
        missing_skills.append(req_clean)

    # 2. Evaluate Preferred Skills
    satisfied_preferred_count = 0.0
    for pref in preferred_skills:
        pref_clean = pref.strip()
        if not pref_clean:
            continue
        norm_pref = normalize_skill(pref_clean)

        if norm_pref in profile_skill_map:
            p_skill = profile_skill_map[norm_pref]
            matching_skills.append({
                "skill": pref_clean,
                "profile_skill": p_skill.name,
                "match_type": SkillMatchType.NORMALIZED,
                "required": False,
                "evidence": f"Profile Preferred Skill: {p_skill.name}",
            })
            satisfied_preferred_count += 1.0
        else:
            # Check related
            rel = next((s for p_n, s in profile_skill_map.items() if are_skills_related(norm_pref, p_n)), None)
            if rel:
                matching_skills.append({
                    "skill": pref_clean,
                    "profile_skill": rel.name,
                    "match_type": SkillMatchType.RELATED,
                    "required": False,
                    "evidence": f"Related preferred competency via {rel.name}",
                })
                satisfied_preferred_count += 0.6

    # Calculate Score
    total_req = len([r for r in required_skills if r.strip()])
    if total_req > 0:
        base_score = (satisfied_required_count / total_req) * 100.0
    else:
        # If no specific required skills listed, score 80 baseline
        base_score = 80.0

    # Add small bonus for preferred skills satisfied (up to +15 pts, max 100)
    total_pref = len([p for p in preferred_skills if p.strip()])
    if total_pref > 0:
        bonus = (satisfied_preferred_count / total_pref) * 15.0
        final_score = min(100.0, base_score + bonus)
    else:
        final_score = min(100.0, base_score)

    return {
        "score": round(final_score, 1),
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "uncertain_skills": uncertain_skills,
        "satisfied_required_count": satisfied_required_count,
        "total_required_count": total_req,
    }
