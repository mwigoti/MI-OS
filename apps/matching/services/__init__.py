"""
MwohaOS Matching Services Package — Milestone 4
"""
from .matcher import match_profile_opportunity
from .eligibility import evaluate_eligibility
from .skills import evaluate_skills
from .experience import evaluate_experience
from .preferences import evaluate_education, evaluate_preferences
from .scoring import calculate_overall_score
from .explanations import generate_match_explanation
from .normalization import (
    normalize_skill,
    are_skills_related,
    compute_profile_snapshot_hash,
    compute_opportunity_snapshot_hash,
    compute_intelligence_snapshot_hash,
)
from .recommendation import get_relevant_opportunities

__all__ = [
    "match_profile_opportunity",
    "evaluate_eligibility",
    "evaluate_skills",
    "evaluate_experience",
    "evaluate_education",
    "evaluate_preferences",
    "calculate_overall_score",
    "generate_match_explanation",
    "normalize_skill",
    "are_skills_related",
    "compute_profile_snapshot_hash",
    "compute_opportunity_snapshot_hash",
    "compute_intelligence_snapshot_hash",
    "get_relevant_opportunities",
]
