"""
MwohaOS Matching Models — Milestone 4: Opportunity Alignment & Explainability
Represents factual, traceable alignment between a user Profile and an Opportunity.
"""
import uuid
from django.db import models
from django.utils import timezone
from apps.core.models import TimeStampedModel
from apps.profiles.models import Profile
from apps.opportunities.models import Opportunity
from .constants import MatchStatus, EligibilityStatus, MATCHING_VERSION


class OpportunityMatch(TimeStampedModel):
    """
    Evaluates and records the multidimensional alignment between a Profile and an Opportunity.
    Stores separate component scores, evidence claims, requirement statuses, and explanations.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="opportunity_matches",
        db_index=True,
    )
    opportunity = models.ForeignKey(
        Opportunity,
        on_delete=models.CASCADE,
        related_name="profile_matches",
        db_index=True,
    )

    # Lifecycle & Overall Scoring
    match_status = models.CharField(
        max_length=50,
        choices=MatchStatus.choices,
        default=MatchStatus.PENDING,
        db_index=True,
    )
    overall_score = models.FloatField(
        default=0.0,
        db_index=True,
        help_text="Weighted match score (0-100). Never an AI black-box guarantee.",
    )

    # Eligibility Dimension (Hard constraint)
    eligibility_status = models.CharField(
        max_length=50,
        choices=EligibilityStatus.choices,
        default=EligibilityStatus.NOT_ASSESSED,
        db_index=True,
    )
    eligibility_confidence = models.FloatField(
        default=0.0,
        help_text="Confidence of eligibility assessment (0.0 to 1.0).",
    )
    eligibility_reasons = models.JSONField(
        default=list,
        blank=True,
        help_text="Factual reasons explaining eligibility or ineligibility determination.",
    )

    # Component Scores (0 to 100 each)
    skill_score = models.FloatField(default=0.0)
    experience_score = models.FloatField(default=0.0)
    education_score = models.FloatField(default=0.0)
    preference_score = models.FloatField(default=0.0)
    location_score = models.FloatField(default=0.0)
    opportunity_type_score = models.FloatField(default=0.0)
    sector_score = models.FloatField(default=0.0)

    # Requirements Breakdown
    required_requirements_met = models.JSONField(
        default=list,
        blank=True,
        help_text="List of mandatory requirements satisfied by profile evidence.",
    )
    required_requirements_missing = models.JSONField(
        default=list,
        blank=True,
        help_text="List of mandatory requirements with no evidence in profile.",
    )
    required_requirements_uncertain = models.JSONField(
        default=list,
        blank=True,
        help_text="Requirements that cannot be evaluated due to insufficient data.",
    )

    preferred_requirements_met = models.JSONField(
        default=list,
        blank=True,
        help_text="List of bonus/preferred requirements satisfied.",
    )
    preferred_requirements_missing = models.JSONField(
        default=list,
        blank=True,
        help_text="List of preferred requirements not found in profile.",
    )

    # Skills Breakdown
    matching_skills = models.JSONField(
        default=list,
        blank=True,
        help_text="List of skill matches with match_type (EXACT, NORMALIZED, RELATED) and evidence.",
    )
    missing_skills = models.JSONField(
        default=list,
        blank=True,
        help_text="Required skills missing from profile.",
    )
    uncertain_skills = models.JSONField(
        default=list,
        blank=True,
        help_text="Skills that are ambiguous or lack proficiency indicators.",
    )

    # Experience & Project Alignment
    matching_experience = models.JSONField(
        default=list,
        blank=True,
        help_text="Traceable links to Profile Experience records meeting requirements.",
    )
    matching_projects = models.JSONField(
        default=list,
        blank=True,
        help_text="Traceable links to Profile Project/Evidence records demonstrating required skills.",
    )

    # Explainability & Evidence
    evidence_summary = models.JSONField(
        default=list,
        blank=True,
        help_text="Structured claims and foreign references linking requirements to profile facts.",
    )
    strengths = models.JSONField(
        default=list,
        blank=True,
        help_text="Key competitive strengths identified from profile facts.",
    )
    gaps = models.JSONField(
        default=list,
        blank=True,
        help_text="Identified qualification or documentation gaps.",
    )
    explanation = models.TextField(
        blank=True,
        help_text="Comprehensive, factual human-readable explanation of why this matches or gaps exist.",
    )

    # Traceability & Versioning
    confidence = models.FloatField(
        default=0.85,
        help_text="Assessment confidence score (0.0 to 1.0).",
    )
    matching_version = models.CharField(
        max_length=50,
        default=MATCHING_VERSION,
        help_text="Algorithm version used to produce this match.",
    )
    profile_snapshot_hash = models.CharField(
        max_length=64,
        blank=True,
        help_text="SHA-256 hash of profile state at time of matching (stale detection).",
    )
    opportunity_snapshot_hash = models.CharField(
        max_length=64,
        blank=True,
        help_text="SHA-256 hash of opportunity content at time of matching.",
    )
    intelligence_snapshot_hash = models.CharField(
        max_length=64,
        blank=True,
        help_text="SHA-256 hash of opportunity intelligence at time of matching.",
    )

    ai_used = models.BooleanField(default=False)
    ai_provider = models.CharField(max_length=50, blank=True)
    ai_model = models.CharField(max_length=100, blank=True)

    last_matched_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Opportunity Match"
        verbose_name_plural = "Opportunity Matches"
        ordering = ["-overall_score", "-created_at"]
        unique_together = [["profile", "opportunity"]]
        indexes = [
            models.Index(fields=["profile", "match_status"]),
            models.Index(fields=["profile", "eligibility_status"]),
            models.Index(fields=["profile", "overall_score"]),
            models.Index(fields=["last_matched_at"]),
        ]

    def __str__(self) -> str:
        return f"Match: {self.profile.user.username} ↔ {self.opportunity.title} [{self.overall_score:.0f}%]"

    @property
    def score_band_label(self) -> str:
        score = self.overall_score
        if score >= 90:
            return "Very strong alignment"
        elif score >= 80:
            return "Strong alignment"
        elif score >= 70:
            return "Moderate alignment"
        elif score >= 60:
            return "Partial alignment"
        return "Limited alignment"
