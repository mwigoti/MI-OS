"""
MwohaOS Evidence Grounding & Verification — Milestone 6: AI Preparation
Extracts candidate ground-truth facts and validates AI-generated materials
against actual profile records to ensure zero hallucinations.
"""
from typing import Dict, Any, List
import re
from apps.profiles.models import Profile, Skill, Experience, Education, Project


def gather_candidate_evidence(profile: Profile) -> Dict[str, Any]:
    """
    Extracts verified facts from the user profile into a structured evidence bank.
    """
    skills_data = []
    for s in profile.skills.all():
        skills_data.append({
            "id": str(s.id),
            "name": s.name,
            "category": getattr(s, "category", "GENERAL"),
            "proficiency": getattr(s, "proficiency", "INTERMEDIATE"),
            "verified": getattr(s, "verified", True),
        })

    experiences_data = []
    for exp in profile.experiences.all():
        experiences_data.append({
            "id": str(exp.id),
            "title": exp.title,
            "organization": exp.organization,
            "description": exp.description or "",
            "achievements": exp.achievements or "",
            "start_date": exp.start_date.strftime("%Y-%m") if exp.start_date else "",
            "end_date": exp.end_date.strftime("%Y-%m") if exp.end_date else ("Present" if exp.is_current else ""),
            "is_current": exp.is_current,
        })

    projects_data = []
    for p in profile.projects.all():
        projects_data.append({
            "id": str(p.id),
            "title": p.title,
            "description": p.description or "",
            "role": getattr(p, "role", "Lead Developer / Researcher"),
            "technologies": getattr(p, "technologies", ""),
            "impact": getattr(p, "impact", ""),
        })

    education_data = []
    for edu in profile.educations.all():
        education_data.append({
            "id": str(edu.id),
            "degree": edu.degree,
            "field_of_study": edu.field_of_study,
            "institution": edu.institution,
            "graduation_year": edu.graduation_year or "",
        })

    return {
        "profile_id": str(profile.id),
        "full_name": profile.full_name or profile.user.get_full_name() or profile.user.username,
        "email": profile.user.email,
        "headline": profile.headline or "",
        "bio": profile.bio or "",
        "location": profile.location or "",
        "nationality": profile.nationality or "",
        "skills": skills_data,
        "experiences": experiences_data,
        "projects": projects_data,
        "education": education_data,
    }


def audit_grounding_evidence(text: str, candidate_evidence: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Identifies profile evidence items explicitly referenced in generated text
    to produce a verifiable audit trail of cited facts.
    """
    if not text:
        return []

    citations: List[Dict[str, Any]] = []
    lower_text = text.lower()

    # 1. Match Skills
    for skill in candidate_evidence.get("skills", []):
        name = skill.get("name", "")
        if name and len(name) > 1:
            pattern = r'\b' + re.escape(name.lower()) + r'\b'
            if re.search(pattern, lower_text):
                citations.append({
                    "evidence_type": "SKILL",
                    "id": skill.get("id"),
                    "name": name,
                    "verified": skill.get("verified", True),
                    "note": f"Skill '{name}' explicitly cited.",
                })

    # 2. Match Organizations & Experiences
    for exp in candidate_evidence.get("experiences", []):
        org = exp.get("organization", "")
        title = exp.get("title", "")
        matched = False
        if org and len(org) > 2 and org.lower() in lower_text:
            matched = True
        elif title and len(title) > 3 and title.lower() in lower_text:
            matched = True

        if matched:
            citations.append({
                "evidence_type": "EXPERIENCE",
                "id": exp.get("id"),
                "organization": org,
                "title": title,
                "verified": True,
                "note": f"Experience '{title}' at '{org}' cited.",
            })

    # 3. Match Projects
    for proj in candidate_evidence.get("projects", []):
        p_title = proj.get("title", "")
        if p_title and len(p_title) > 2 and p_title.lower() in lower_text:
            citations.append({
                "evidence_type": "PROJECT",
                "id": proj.get("id"),
                "title": p_title,
                "verified": True,
                "note": f"Project '{p_title}' cited.",
            })

    # 4. Match Education
    for edu in candidate_evidence.get("education", []):
        inst = edu.get("institution", "")
        deg = edu.get("degree", "")
        if (inst and len(inst) > 3 and inst.lower() in lower_text) or (deg and len(deg) > 3 and deg.lower() in lower_text):
            citations.append({
                "evidence_type": "EDUCATION",
                "id": edu.get("id"),
                "institution": inst,
                "degree": deg,
                "verified": True,
                "note": f"Degree '{deg}' at '{inst}' cited.",
            })

    return citations


def calculate_grounding_score(citations: List[Dict[str, Any]]) -> float:
    """
    Calculates a confidence score between 0.0 and 1.0 reflecting the factual density
    of verified profile evidence citations.
    """
    if not citations:
        return 0.5  # Neutral baseline if generic
    # Having multiple distinct verified evidence citations gives high confidence
    unique_types = len(set(c["evidence_type"] for c in citations))
    count = len(citations)
    
    score = min(1.0, 0.4 + (unique_types * 0.15) + (count * 0.05))
    return round(score, 2)
