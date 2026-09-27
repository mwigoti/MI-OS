"""
MwohaOS Evidence-Grounded Explanation Generator — Milestone 4
Produces clear, human-readable explanations based exclusively on verified profile and opportunity facts.
"""
from typing import Dict, Any, List


def generate_match_explanation(
    opportunity_title: str,
    organization: str,
    eligibility_status: str,
    eligibility_reasons: List[str],
    matching_skills: List[Dict[str, Any]],
    missing_skills: List[str],
    matching_exp: List[Dict[str, Any]],
    matching_proj: List[Dict[str, Any]],
    matching_edu: List[Dict[str, Any]],
    gaps: List[str],
    overall_score: float,
) -> str:
    """
    Constructs a factual, transparent explanation answering:
    'How well does this opportunity align with my professional profile, and why?'
    """
    paragraphs = []

    # 1. Summary statement
    if eligibility_status == "INELIGIBLE":
        paragraphs.append(
            f"This opportunity with {organization} is marked INELIGIBLE based on explicit constraints. "
            f"Reasons: {' '.join(eligibility_reasons)}"
        )
    elif overall_score >= 80.0:
        paragraphs.append(
            f"This opportunity strongly aligns with your verified profile credentials, "
            f"demonstrating direct overlap with your core technical competencies and background."
        )
    elif overall_score >= 65.0:
        paragraphs.append(
            f"This opportunity shows moderate to good alignment with your professional profile, "
            f"satisfying primary requirements with a few potential experience or tooling gaps to consider."
        )
    else:
        paragraphs.append(
            f"This opportunity has limited alignment with your current profile evidence. "
            f"Several mandatory requirements or domain competencies are not yet established."
        )

    # 2. Key matching strengths
    strong_points = []
    # Collect exact and normalized skills
    top_skills = [s["skill"] for s in matching_skills if s.get("required")]
    if top_skills:
        strong_points.append(f"Satisfied required skills: {', '.join(top_skills[:6])}.")

    if matching_edu:
        edu_summary = ", ".join([f"{e['degree']} ({e['field_of_study']})" for e in matching_edu[:2]])
        strong_points.append(f"Relevant academic credentials: {edu_summary}.")

    if matching_proj:
        proj_titles = ", ".join([p["project_title"] for p in matching_proj[:3]])
        strong_points.append(f"Demonstrated project track record in: {proj_titles}.")

    if strong_points:
        paragraphs.append("Key Alignment Evidence:\n• " + "\n• ".join(strong_points))

    # 3. Gaps & Missing Requirements
    gap_points = []
    if missing_skills:
        gap_points.append(f"Required skills missing from profile: {', '.join(missing_skills[:5])}.")

    for g in gaps:
        gap_points.append(g)

    if gap_points:
        paragraphs.append("Potential Gaps & Considerations:\n• " + "\n• ".join(gap_points))
    elif eligibility_status != "INELIGIBLE":
        paragraphs.append("No critical qualification or document gaps identified.")

    return "\n\n".join(paragraphs)
