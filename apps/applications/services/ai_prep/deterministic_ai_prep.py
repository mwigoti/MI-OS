"""
MwohaOS Deterministic AI Preparation Engine — Milestone 6: AI Preparation
Provides reliable, grounded, rule-based preparation of cover letters, CV tailoring,
and application essay answers when hosted LLM providers are unavailable or disabled.
"""
from typing import Dict, Any, List
import re


def synthesize_deterministic_cover_letter(
    candidate_evidence: Dict[str, Any],
    opportunity_data: Dict[str, Any],
    tone: str = "PROFESSIONAL",
    custom_guidance: str = "",
) -> Dict[str, Any]:
    """
    Synthesizes a bespoke Cover Letter using verified profile evidence and opportunity data.
    """
    candidate_name = candidate_evidence.get("full_name") or "Applicant"
    role_title = opportunity_data.get("title", "this position")
    org_name = opportunity_data.get("organization", "your organization")
    purpose = opportunity_data.get("purpose") or "advancing high-impact initiatives"

    # Match candidate skills with opportunity required skills
    opp_skills = set(s.lower() for s in opportunity_data.get("required_skills", []))
    matched_skills = [
        s["name"] for s in candidate_evidence.get("skills", [])
        if s["name"].lower() in opp_skills or not opp_skills
    ][:5]
    if not matched_skills:
        matched_skills = [s["name"] for s in candidate_evidence.get("skills", [])][:4]

    # Select primary experience
    experiences = candidate_evidence.get("experiences", [])
    primary_exp = experiences[0] if experiences else None

    # Select primary project
    projects = candidate_evidence.get("projects", [])
    primary_project = projects[0] if projects else None

    # Opening paragraph
    opening = (
        f"Dear Hiring Committee at {org_name},\n\n"
        f"I am writing to express my strong enthusiasm for the {role_title} role at {org_name}. "
        f"With a dedicated track record in {', '.join(matched_skills[:2]) if matched_skills else 'my field'}, "
        f"I am deeply inspired by {org_name}'s mission focused on {purpose.lower().rstrip('.')}."
    )

    # Core Experience paragraph
    if primary_exp:
        exp_title = primary_exp.get("title")
        exp_org = primary_exp.get("organization")
        exp_desc = primary_exp.get("description") or "leading key technical initiatives"
        exp_achieve = primary_exp.get("achievements") or "delivering scalable solutions and cross-functional leadership"
        body_1 = (
            f"In my role as {exp_title} at {exp_org}, I focused on {exp_desc.rstrip('.')}. "
            f"Specifically, I spearheaded {exp_achieve.rstrip('.')}. "
            f"This direct experience aligns seamlessly with your requirement for demonstrated proficiency in "
            f"{', '.join(matched_skills[:3]) if matched_skills else 'technical execution'}."
        )
    else:
        body_1 = (
            f"Throughout my career, I have cultivated hands-on expertise in {', '.join(matched_skills)}, "
            f"consistently translating complex challenges into robust, measurable solutions."
        )

    # Core Project / Impact paragraph
    if primary_project:
        proj_title = primary_project.get("title")
        proj_desc = primary_project.get("description") or "developing domain-specific workflows"
        proj_impact = primary_project.get("impact") or "delivering actionable insights"
        body_2 = (
            f"Furthermore, through my work on '{proj_title}', I was responsible for {proj_desc.rstrip('.')}, "
            f"which resulted in {proj_impact.rstrip('.')}. "
            f"This demonstrates my capacity to take full ownership of mission-critical objectives and deliver tangible value."
        )
    else:
        body_2 = (
            f"My technical background and rigorous analytical approach ensure that I can hit the ground running, "
            f"collaborating effectively across technical and strategic stakeholders."
        )

    # Closing paragraph
    closing = (
        f"I welcome the opportunity to discuss how my verified background and commitment can contribute "
        f"to {org_name}'s ongoing initiatives. Thank you for your time and consideration.\n\n"
        f"Sincerely,\n{candidate_name}"
    )

    full_text = f"{opening}\n\n{body_1}\n\n{body_2}\n\n{closing}"

    return {
        "content": full_text,
        "tailoring_notes": f"Tailored for {role_title} at {org_name} highlighting skills: {', '.join(matched_skills)}.",
        "provider": "DETERMINISTIC",
        "model": "rule-based-v1",
        "token_metrics": {"prompt_tokens": 0, "completion_tokens": len(full_text.split()), "total_tokens": len(full_text.split())},
    }


def synthesize_deterministic_cv_tailoring(
    candidate_evidence: Dict[str, Any],
    opportunity_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Synthesizes tailored CV optimizations: targeted summary, prioritized skills,
    tailored bullets, and ATS keyword coverage.
    """
    candidate_name = candidate_evidence.get("full_name") or "Professional"
    role_title = opportunity_data.get("title", "Role")
    org_name = opportunity_data.get("organization", "Target Organization")

    req_skills = [s.strip().lower() for s in opportunity_data.get("required_skills", []) if s.strip()]
    pref_skills = [s.strip().lower() for s in opportunity_data.get("preferred_skills", []) if s.strip()]
    all_opp_skills = set(req_skills + pref_skills)

    candidate_skills = candidate_evidence.get("skills", [])
    candidate_skill_names = [s["name"] for s in candidate_skills]
    candidate_skill_set = set(s.lower() for s in candidate_skill_names)

    # Match skills
    matched_skills = []
    missing_skills = []

    for opp_s in req_skills:
        if opp_s in candidate_skill_set:
            matched_skills.append(opp_s)
        else:
            missing_skills.append(opp_s)

    # Prioritize skills
    prioritized_skills = []
    for s in candidate_skills:
        s_name = s["name"]
        is_match = s_name.lower() in all_opp_skills
        prioritized_skills.append({
            "name": s_name,
            "match_type": "EXACT" if is_match else "COMPETENCY",
            "relevance_explanation": f"Matches required qualification for {role_title}" if is_match else "Supporting core capability",
            "is_matched_requirement": is_match,
        })
    # Sort so matched skills are first
    prioritized_skills.sort(key=lambda x: not x["is_matched_requirement"])

    # Targeted Summary
    top_matches = [s["name"] for s in prioritized_skills if s["is_matched_requirement"]][:3]
    top_skills_str = ", ".join(top_matches) if top_matches else "analytical and technical execution"
    targeted_summary = (
        f"Results-driven specialist with proven expertise in {top_skills_str}, offering proven experience "
        f"in high-impact research, systems architecture, and data-driven analysis. Targeted specifically for the "
        f"{role_title} at {org_name} to drive verifiable outcomes and mission-critical objectives."
    )

    # Tailored Experience Bullets
    tailored_experience_bullets = []
    for exp in candidate_evidence.get("experiences", []):
        exp_id = exp.get("id")
        title = exp.get("title")
        org = exp.get("organization")
        achieve = exp.get("achievements") or exp.get("description") or "Executed operational initiatives"

        tailored_bullets = [
            f"Spearheaded {achieve.rstrip('.')}, directly applying {top_skills_str} to optimize performance and delivery.",
            f"Collaborated cross-functionally at {org} to architect reliable solutions, adhering to industry best practices.",
        ]
        tailored_experience_bullets.append({
            "experience_id": exp_id,
            "role": title,
            "organization": org,
            "tailored_bullets": tailored_bullets,
        })

    # Selected Projects
    selected_projects = []
    for p in candidate_evidence.get("projects", [])[:3]:
        selected_projects.append({
            "project_id": p.get("id"),
            "title": p.get("title"),
            "alignment_highlight": f"Demonstrates practical application of {p.get('technologies') or 'methodologies'} in solving domain-specific challenges.",
        })

    # ATS Keyword Coverage
    total_req = max(1, len(req_skills))
    coverage_score = round((len(matched_skills) / total_req) * 100) if req_skills else 80

    ats_keyword_coverage = {
        "coverage_score": coverage_score,
        "matched_keywords": matched_skills,
        "missing_keywords": missing_skills,
        "total_keywords_analyzed": len(req_skills),
    }

    return {
        "targeted_summary": targeted_summary,
        "prioritized_skills": prioritized_skills,
        "tailored_experience_bullets": tailored_experience_bullets,
        "selected_projects": selected_projects,
        "ats_keyword_coverage": ats_keyword_coverage,
        "provider": "DETERMINISTIC",
        "model": "rule-based-v1",
        "token_metrics": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    }


def synthesize_deterministic_question_answer(
    question_text: str,
    max_words: int | None,
    max_characters: int | None,
    tone: str,
    candidate_evidence: Dict[str, Any],
    opportunity_data: Dict[str, Any],
    additional_guidance: str = "",
) -> Dict[str, Any]:
    """
    Synthesizes a structured answer adhering to STAR framework and strict word/char limits.
    """
    experiences = candidate_evidence.get("experiences", [])
    primary_exp = experiences[0] if experiences else None
    projects = candidate_evidence.get("projects", [])
    primary_proj = projects[0] if projects else None

    exp_title = primary_exp.get("title") if primary_exp else "Lead Researcher"
    exp_org = primary_exp.get("organization") if primary_exp else "my previous organization"
    proj_title = primary_proj.get("title") if primary_proj else "strategic project"

    # STAR Synthesis
    situation = f"In my role as {exp_title} at {exp_org}, our team encountered a critical requirement to deliver reliable results under demanding constraints."
    task = f"My specific responsibility was to design and implement an end-to-end strategy, leveraging verified methodologies and hands-on execution."
    action = f"I deployed targeted solutions through '{proj_title}', coordinating closely with stakeholders, validating data pipelines, and mitigating key operational bottlenecks."
    result = f"As a result, we successfully achieved mission-critical milestones ahead of schedule, establishing a repeatable benchmark for future initiatives."

    answer = f"{situation} {task} {action} {result}"

    # Enforce strict length limits
    if max_words and len(answer.split()) > max_words:
        words = answer.split()[:max_words]
        answer = " ".join(words)
        # Ensure it ends with punctuation
        if not answer.endswith((".", "!", "?")):
            answer = re.sub(r'[,;:]$', '', answer) + "."

    if max_characters and len(answer) > max_characters:
        answer = answer[:max_characters].rstrip()
        # Ensure clean word boundary
        last_space = answer.rfind(" ")
        if last_space > 0:
            answer = answer[:last_space]
        if not answer.endswith((".", "!", "?")):
            answer += "."

    return {
        "answer_text": answer,
        "word_count": len(answer.split()),
        "char_count": len(answer),
        "provider": "DETERMINISTIC",
        "model": "rule-based-star-v1",
        "token_metrics": {"prompt_tokens": 0, "completion_tokens": len(answer.split()), "total_tokens": len(answer.split())},
    }
