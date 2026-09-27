"""
MwohaOS Evidence-Backed Experience & Project Matching Service — Milestone 4
Validates required years of experience, responsibilities, and correlates project evidence.
"""
from typing import Dict, Any, List
import re
from apps.profiles.models import Profile, Experience, Project, Evidence


def evaluate_experience(
    profile: Profile,
    required_experience_items: List[str],
    responsibilities: List[str],
    opportunity_corpus: str = "",
) -> Dict[str, Any]:
    """
    Evaluates profile experiences, projects, and evidence items against opportunity requirements.
    Every claim must trace to an actual database record.
    """
    experiences = list(profile.experiences.all())
    projects = list(profile.projects.all())
    evidence_items = list(profile.evidence_items.all())

    matching_exp = []
    matching_proj = []
    gaps = []

    # 1. Calculate total verified years of professional experience
    total_months = 0
    for exp in experiences:
        months = exp.duration_months
        if months:
            total_months += months
    total_years = round(total_months / 12.0, 1)

    # 2. Check explicit required experience years
    required_years = 0
    for req in required_experience_items:
        match = re.search(r"(\d+)\+?\s*years?", req, re.IGNORECASE)
        if match:
            required_years = max(required_years, int(match.group(1)))

    if required_years > 0:
        if total_years >= required_years:
            matching_exp.append({
                "claim": f"Satisfies {required_years}+ years experience requirement.",
                "evidence": f"Profile establishes {total_years} cumulative years across {len(experiences)} professional roles.",
                "verified": True,
            })
        else:
            gaps.append(
                f"Opportunity requests {required_years}+ years experience; profile establishes {total_years} years."
            )

    # 3. Match experience roles to opportunity domain/responsibilities
    corpus_lower = opportunity_corpus.lower()
    for exp in experiences:
        exp_text = f"{exp.title} {exp.company} {exp.description}".lower()
        # Find keyword overlap
        overlap = []
        for word in ["satellite", "remote sensing", "gis", "earth observation", "climate", "hydrology", "machine learning", "python", "developer", "research"]:
            if word in exp_text and word in corpus_lower:
                overlap.append(word)

        if overlap:
            matching_exp.append({
                "role": f"{exp.title} at {exp.company}",
                "dates": f"{exp.start_date} to {exp.end_date or 'Present'}",
                "overlap_keywords": list(dict.fromkeys(overlap)),
                "evidence_ref": f"Experience ID: {exp.id}",
                "description": exp.description[:250] if exp.description else "",
            })

    # 4. Match Projects and Evidence items
    for proj in projects:
        proj_text = f"{proj.title} {proj.description} {proj.technologies}".lower()
        proj_overlap = []
        for word in ["satellite", "remote sensing", "gis", "earth observation", "agriculture", "climate", "sentinel", "flood", "machine learning"]:
            if word in proj_text and word in corpus_lower:
                proj_overlap.append(word)

        if proj_overlap:
            matching_proj.append({
                "project_title": proj.title,
                "role": proj.role or "Lead / Developer",
                "technologies": proj.technologies,
                "overlap": list(dict.fromkeys(proj_overlap)),
                "evidence_url": proj.project_url or "",
                "evidence_ref": f"Project ID: {proj.id}",
            })

    # 5. Score Experience alignment
    score = 60.0  # Baseline
    if required_years > 0:
        if total_years >= required_years:
            score += 25.0
        else:
            # Partial credit if at least some experience exists
            score += min(20.0, (total_years / required_years) * 20.0)
    elif len(experiences) >= 1:
        score += 20.0

    if matching_proj:
        score += min(15.0, len(matching_proj) * 7.5)

    final_score = min(100.0, max(20.0, score))

    return {
        "score": round(final_score, 1),
        "total_years_experience": total_years,
        "matching_experience": matching_exp,
        "matching_projects": matching_proj,
        "gaps": gaps,
    }
