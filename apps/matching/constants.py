"""
MwohaOS Matching Constants & Choices — Milestone 4
"""
from django.db import models


class MatchStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    PROCESSING = "PROCESSING", "Processing"
    COMPLETED = "COMPLETED", "Completed"
    PARTIAL = "PARTIAL", "Partial"
    FAILED = "FAILED", "Failed"
    STALE = "STALE", "Stale"


class EligibilityStatus(models.TextChoices):
    ELIGIBLE = "ELIGIBLE", "Eligible"
    INELIGIBLE = "INELIGIBLE", "Ineligible"
    UNCERTAIN = "UNCERTAIN", "Uncertain"
    NOT_ASSESSED = "NOT_ASSESSED", "Not Assessed"


class SkillMatchType(models.TextChoices):
    EXACT = "EXACT", "Exact Match"
    NORMALIZED = "NORMALIZED", "Normalized Match"
    SEMANTIC = "SEMANTIC", "Semantic Match"
    RELATED = "RELATED", "Related Skill"
    MISSING = "MISSING", "Missing from Profile"
    UNKNOWN = "UNKNOWN", "Unknown"


class LocationMatchType(models.TextChoices):
    MATCH = "MATCH", "Match"
    PARTIAL_MATCH = "PARTIAL_MATCH", "Partial Match"
    MISMATCH = "MISMATCH", "Mismatch"
    UNKNOWN = "UNKNOWN", "Unknown"
    NOT_APPLICABLE = "NOT_APPLICABLE", "Not Applicable (Remote)"


MATCHING_VERSION = "1.0"

# Transparent default weights summing to 100
DEFAULT_SCORING_WEIGHTS = {
    "eligibility": 0.25,
    "required_skills": 0.25,
    "experience": 0.20,
    "education": 0.10,
    "sector": 0.08,
    "opportunity_type": 0.05,
    "location": 0.05,
    "preferences": 0.02,
}
