"""
MwohaOS Deterministic Scoring Engine — Milestone 4
Computes transparent weighted alignment scores and enforces hard constraints.
"""
from typing import Dict, Any
from apps.matching.constants import DEFAULT_SCORING_WEIGHTS, EligibilityStatus


def calculate_overall_score(
    component_scores: Dict[str, float],
    eligibility_status: str,
    hard_constraint_failed: bool = False,
    weights: Dict[str, float] = None,
) -> float:
    """
    Calculates weighted overall score (0 to 100).
    Enforces hard constraints:
      - If hard constraint failed or INELIGIBLE, overall score is capped at max 35.0,
        guaranteeing it cannot be recommended as a positive match.
    """
    w = weights or DEFAULT_SCORING_WEIGHTS

    score = (
        component_scores.get("eligibility", 0.0) * w["eligibility"]
        + component_scores.get("required_skills", 0.0) * w["required_skills"]
        + component_scores.get("experience", 0.0) * w["experience"]
        + component_scores.get("education", 0.0) * w["education"]
        + component_scores.get("sector", 0.0) * w["sector"]
        + component_scores.get("opportunity_type", 0.0) * w["opportunity_type"]
        + component_scores.get("location", 0.0) * w["location"]
        + component_scores.get("preferences", 0.0) * w["preferences"]
    )

    score = round(max(0.0, min(100.0, score)), 1)

    # Hard Constraint Enforcement
    if hard_constraint_failed or eligibility_status == EligibilityStatus.INELIGIBLE:
        # Cap score to reflect ineligibility regardless of skill alignment
        score = min(score, 35.0)

    return score
