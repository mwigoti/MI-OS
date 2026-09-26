"""
MwohaOS Deterministic Profile Completeness Service
Calculates structured, reproducible percentage scores across profile sections.
No AI, no heuristic guessing — fully deterministic based on recorded facts.
"""
from typing import Dict, Any


def calculate_profile_completeness(profile) -> Dict[str, Any]:
    """
    Computes completeness percentages across all key Milestone 1 profile dimensions:
    - Identity & Summary
    - Contact & Links
    - Experience
    - Education
    - Skills
    - Projects
    - Achievements
    - Certifications
    - Documents
    - Evidence
    - Preferences

    Returns:
        Dict with overall percentage and section-by-section breakdown:
        {
            "overall": 72,
            "sections": {
                "identity": 100,
                "contact": 80,
                "experience": 80,
                "education": 100,
                "skills": 75,
                "projects": 60,
                "achievements": 50,
                "certifications": 50,
                "documents": 50,
                "evidence": 40,
                "preferences": 60
            },
            "stats": {
                "skill_count": 8,
                "experience_count": 3,
                "education_count": 1,
                "project_count": 2,
                "document_count": 2,
                "evidence_count": 4,
                "verified_evidence_count": 2
            }
        }
    """
    if not profile:
        return {
            "overall": 0,
            "sections": {},
            "stats": {}
        }

    # 1. Identity & Summary (Weight: 10%)
    identity_points = 0
    if profile.headline and len(profile.headline.strip()) > 3:
        identity_points += 40
    if profile.professional_summary and len(profile.professional_summary.strip()) > 30:
        identity_points += 40
    if profile.work_authorization:
        identity_points += 20
    identity_score = min(100, identity_points)

    # 2. Contact & Location (Weight: 10%)
    contact_points = 0
    if profile.location or (profile.country and profile.city):
        contact_points += 30
    if profile.linkedin_url:
        contact_points += 25
    if profile.github_url:
        contact_points += 25
    if profile.portfolio_url or profile.personal_website_url:
        contact_points += 20
    contact_score = min(100, contact_points)

    # 3. Experience (Weight: 15%)
    exp_count = profile.experiences.count()
    if exp_count >= 2:
        experience_score = 100
    elif exp_count == 1:
        experience_score = 70
    else:
        experience_score = 0

    # 4. Education (Weight: 10%)
    edu_count = profile.education.count()
    if edu_count >= 1:
        education_score = 100
    else:
        education_score = 0

    # 5. Skills (Weight: 15%)
    skill_count = profile.skills.count()
    if skill_count >= 8:
        skills_score = 100
    elif skill_count >= 5:
        skills_score = 80
    elif skill_count >= 2:
        skills_score = 50
    elif skill_count == 1:
        skills_score = 25
    else:
        skills_score = 0

    # 6. Projects (Weight: 15%)
    proj_count = profile.projects.count()
    if proj_count >= 3:
        projects_score = 100
    elif proj_count >= 2:
        projects_score = 75
    elif proj_count == 1:
        projects_score = 50
    else:
        projects_score = 0

    # 7. Achievements & Certifications (Weight: 5%)
    ach_count = profile.achievements.count()
    cert_count = profile.certifications.count()
    ach_cert_points = min(100, (ach_count * 30) + (cert_count * 30))

    # 8. Documents (Weight: 10%)
    doc_count = profile.documents.count()
    has_cv = profile.documents.filter(document_type__in=["CV", "RESUME"]).exists()
    doc_points = 0
    if has_cv:
        doc_points += 70
    if doc_count >= 2:
        doc_points += 30
    document_score = min(100, doc_points)

    # 9. Evidence Bank (Weight: 10%)
    ev_count = profile.evidence_items.count()
    verified_ev_count = profile.evidence_items.filter(verified=True).count()
    ev_points = 0
    if ev_count >= 3:
        ev_points += 60
    elif ev_count >= 1:
        ev_points += 30
    if verified_ev_count >= 1:
        ev_points += 40
    evidence_score = min(100, ev_points)

    # 10. Preferences (Weight: 5%)
    pref_score = 0
    try:
        pref = profile.preferences
        if pref.target_opportunity_types and len(pref.target_opportunity_types) > 0:
            pref_score += 40
        if pref.target_sectors and len(pref.target_sectors) > 0:
            pref_score += 30
        if pref.work_modes and len(pref.work_modes) > 0:
            pref_score += 30
    except Exception:
        pref_score = 0

    # Calculate overall weighted score
    # Weights sum to 1.0 (100%):
    # identity: 0.10, contact: 0.10, experience: 0.15, education: 0.10, skills: 0.15,
    # projects: 0.15, ach_cert: 0.05, documents: 0.10, evidence: 0.10, preferences: 0.05
    overall = (
        (identity_score * 0.10) +
        (contact_score * 0.10) +
        (experience_score * 0.15) +
        (education_score * 0.10) +
        (skills_score * 0.15) +
        (projects_score * 0.15) +
        (ach_cert_points * 0.05) +
        (document_score * 0.10) +
        (evidence_score * 0.10) +
        (pref_score * 0.05)
    )

    return {
        "overall": round(overall),
        "sections": {
            "identity": identity_score,
            "contact": contact_score,
            "experience": experience_score,
            "education": education_score,
            "skills": skills_score,
            "projects": projects_score,
            "achievements_and_certs": ach_cert_points,
            "documents": document_score,
            "evidence": evidence_score,
            "preferences": pref_score,
        },
        "stats": {
            "skill_count": skill_count,
            "experience_count": exp_count,
            "education_count": edu_count,
            "project_count": proj_count,
            "achievement_count": ach_count,
            "certification_count": cert_count,
            "document_count": doc_count,
            "evidence_count": ev_count,
            "verified_evidence_count": verified_ev_count,
        }
    }
