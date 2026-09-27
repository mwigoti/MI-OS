"""
MwohaOS Opportunities Models — Milestone 2: Opportunity Discovery & Ingestion
Provides UUID-keyed Opportunity, OpportunitySource, and IngestionRun models.
"""
import uuid
from django.db import models
from django.utils import timezone
from apps.core.models import TimeStampedModel
from .constants import OpportunityStatus, OpportunityType, Sector, SourceType, IngestionStatus


class OpportunitySource(TimeStampedModel):
    """
    Catalog of configured public opportunity discovery sources.
    Supports RSS, APIs, and public feeds with run history and observability.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True, help_text="Readable name of the source.")
    slug = models.SlugField(max_length=100, unique=True, help_text="Unique connector identifier.")
    source_type = models.CharField(
        max_length=50,
        choices=SourceType.choices,
        default=SourceType.RSS,
        help_text="Transport mechanism.",
    )
    base_url = models.URLField(max_length=500, help_text="Base feed or API endpoint URL.")
    enabled = models.BooleanField(default=True, db_index=True, help_text="Toggle automated polling.")
    configuration = models.JSONField(
        default=dict,
        blank=True,
        help_text="Connector-specific options (e.g. headers, default sector, opportunity type override).",
    )
    last_run = models.DateTimeField(null=True, blank=True, help_text="Timestamp of most recent run.")
    last_success = models.DateTimeField(null=True, blank=True, help_text="Timestamp of most recent successful run.")
    last_error = models.TextField(blank=True, help_text="Error message from last failure.")

    class Meta:
        verbose_name = "Opportunity Source"
        verbose_name_plural = "Opportunity Sources"
        ordering = ["name"]

    def __str__(self) -> str:
        status_str = "Enabled" if self.enabled else "Disabled"
        return f"{self.name} ({self.get_source_type_display()}) [{status_str}]"


class Opportunity(TimeStampedModel):
    """
    Primary Opportunity entity in MwohaOS.
    Normalized from RSS, APIs, public portals, or manual URLs.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=500, db_index=True, help_text="Opportunity title.")
    organization = models.CharField(max_length=255, db_index=True, help_text="Host company, university, or foundation.")
    description = models.TextField(blank=True, help_text="Sanitized opportunity overview and context.")
    opportunity_type = models.CharField(
        max_length=50,
        choices=OpportunityType.choices,
        default=OpportunityType.JOB,
        db_index=True,
        help_text="Primary category.",
    )
    sector = models.CharField(
        max_length=50,
        choices=Sector.choices,
        default=Sector.GENERAL,
        db_index=True,
        help_text="Domain focus.",
    )
    location = models.CharField(max_length=255, blank=True, help_text="City, region, or general location string.")
    country = models.CharField(max_length=100, blank=True, db_index=True, help_text="Primary country.")
    remote = models.BooleanField(default=False, db_index=True, help_text="Is remote participation/employment allowed?")
    
    posted_date = models.DateTimeField(null=True, blank=True, help_text="Publication date from source.")
    deadline = models.DateTimeField(null=True, blank=True, db_index=True, help_text="Application/submission deadline.")
    deadline_timezone = models.CharField(max_length=50, blank=True, default="Africa/Nairobi", help_text="Timezone specified by source.")

    source = models.ForeignKey(
        OpportunitySource,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="opportunities",
        help_text="Origin source connector if automated.",
    )
    source_url = models.URLField(max_length=1000, db_index=True, help_text="Canonical source webpage or listing URL.")
    application_url = models.URLField(max_length=1000, blank=True, help_text="Direct submission, portal, or registration link.")

    eligibility_text = models.TextField(blank=True, help_text="Eligibility parameters extracted from source.")
    requirements = models.TextField(blank=True, help_text="Mandatory qualifications or requirements.")
    preferred_skills = models.CharField(max_length=500, blank=True, help_text="Key skills mentioned in source.")
    compensation = models.CharField(max_length=255, blank=True, help_text="Salary, grant amount, or prize funding.")

    raw_content = models.TextField(blank=True, help_text="Raw payload or HTML extract preserved for audit & debug.")
    content_hash = models.CharField(max_length=64, db_index=True, help_text="Deterministic SHA-256 hash of core content.")

    status = models.CharField(
        max_length=50,
        choices=OpportunityStatus.choices,
        default=OpportunityStatus.ACTIVE,
        db_index=True,
    )
    first_seen_at = models.DateTimeField(default=timezone.now, help_text="When first detected by MwohaOS.")
    last_seen_at = models.DateTimeField(default=timezone.now, help_text="When most recently re-observed.")

    class Meta:
        verbose_name = "Opportunity"
        verbose_name_plural = "Opportunities"
        ordering = ["-posted_date", "-created_at"]
        indexes = [
            models.Index(fields=["status", "deadline"]),
            models.Index(fields=["organization", "title"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} @ {self.organization} ({self.get_opportunity_type_display()})"

    @property
    def is_expired(self) -> bool:
        if self.deadline and self.deadline < timezone.now():
            return True
        return self.status == OpportunityStatus.EXPIRED


class IngestionRun(TimeStampedModel):
    """
    Audit record for every execution of an opportunity connector.
    Provides observability into items fetched, parsed, created, updated, and failed.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source = models.ForeignKey(
        OpportunitySource,
        on_delete=models.CASCADE,
        related_name="ingestion_runs",
    )
    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=50,
        choices=IngestionStatus.choices,
        default=IngestionStatus.RUNNING,
        db_index=True,
    )
    items_fetched = models.PositiveIntegerField(default=0)
    items_parsed = models.PositiveIntegerField(default=0)
    items_created = models.PositiveIntegerField(default=0)
    items_updated = models.PositiveIntegerField(default=0)
    items_skipped = models.PositiveIntegerField(default=0)
    items_failed = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True)

    class Meta:
        verbose_name = "Ingestion Run"
        verbose_name_plural = "Ingestion Runs"
        ordering = ["-started_at"]

    @property
    def duration_seconds(self) -> float:
        if self.completed_at and self.started_at:
            return round((self.completed_at - self.started_at).total_seconds(), 2)
        return 0.0

    def __str__(self) -> str:
        return f"Run {self.id} for {self.source.name} [{self.status}]"


class OpportunityIntelligence(TimeStampedModel):
    """
    Structured intelligence record derived from deterministic and AI extraction.
    Maintains a 1-to-1 relationship with Opportunity.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    opportunity = models.OneToOneField(
        Opportunity,
        on_delete=models.CASCADE,
        related_name="intelligence",
        help_text="The opportunity analyzed.",
    )
    summary = models.TextField(blank=True, help_text="Executive summary of the opportunity.")
    organization_summary = models.TextField(blank=True, help_text="Background and mission of host entity.")
    opportunity_purpose = models.TextField(blank=True, help_text="Objective, problem addressed, or goal.")
    who_should_apply = models.JSONField(default=list, blank=True, help_text="Target applicant personas / demographics.")
    responsibilities = models.JSONField(default=list, blank=True, help_text="Key duties, tasks, or project milestones.")
    required_requirements = models.JSONField(default=list, blank=True, help_text="Mandatory qualifications / prerequisites.")
    preferred_requirements = models.JSONField(default=list, blank=True, help_text="Bonus / nice-to-have qualifications.")
    eligibility = models.JSONField(default=dict, blank=True, help_text="Structured eligibility parameters (nationality, education, etc.).")
    required_documents = models.JSONField(default=list, blank=True, help_text="Document checklist (CV, Proposal, Letters, etc.).")
    required_experience = models.JSONField(default=list, blank=True, help_text="Years of experience and domain track record.")
    required_skills = models.JSONField(default=list, blank=True, help_text="Mandatory technical, domain, or soft skills.")
    preferred_skills = models.JSONField(default=list, blank=True, help_text="Preferred / secondary skills.")
    benefits = models.JSONField(default=list, blank=True, help_text="Funding, stipends, equity, mentoring, or perks.")
    compensation_details = models.CharField(max_length=500, blank=True, help_text="Detailed compensation or prize structure.")
    location_details = models.CharField(max_length=500, blank=True, help_text="Specific geographic or venue constraints.")
    remote_details = models.CharField(max_length=500, blank=True, help_text="Remote policy (fully remote, timezones, hybrid).")
    application_process = models.JSONField(default=list, blank=True, help_text="Step-by-step application workflow.")
    important_dates = models.JSONField(default=list, blank=True, help_text="Key timeline events (opens, review, start date).")
    application_instructions = models.JSONField(default=list, blank=True, help_text="Submission rules, portal links, or email guidelines.")

    confidence = models.FloatField(default=0.0, help_text="Extraction confidence score (0.0 to 1.0). Never a fit/match score.")

    extraction_status = models.CharField(
        max_length=50,
        choices=[
            ("PENDING", "Pending"),
            ("PROCESSING", "Processing"),
            ("COMPLETED", "Completed"),
            ("PARTIAL", "Partial"),
            ("FAILED", "Failed"),
        ],
        default="PENDING",
        db_index=True,
    )
    extraction_method = models.CharField(
        max_length=50,
        choices=[
            ("DETERMINISTIC", "Deterministic"),
            ("AI", "AI-Assisted"),
            ("HYBRID", "Hybrid"),
            ("MANUAL", "Manual"),
        ],
        default="DETERMINISTIC",
    )
    extraction_provider = models.CharField(
        max_length=50,
        choices=[
            ("NONE", "None (Deterministic Only)"),
            ("GEMINI", "Google Gemini"),
            ("HUGGINGFACE", "Hugging Face Inference"),
        ],
        default="NONE",
    )
    model_name = models.CharField(max_length=100, blank=True, help_text="Exact LLM model name used.")
    extraction_version = models.CharField(max_length=50, default="v1.0", help_text="Schema extraction version for cache invalidation.")

    raw_extraction = models.JSONField(default=dict, blank=True, help_text="Full structured JSON returned by extraction engine.")
    extraction_error = models.TextField(blank=True, help_text="Any error message encountered during analysis.")

    last_extracted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Opportunity Intelligence"
        verbose_name_plural = "Opportunity Intelligence Records"
        ordering = ["-updated_at"]

    def __str__(self) -> str:
        return f"Intelligence: {self.opportunity.title} [{self.extraction_status}]"


class AIUsageLog(TimeStampedModel):
    """
    Audit log tracking AI provider invocations, model latency, token counts, and errors.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.CharField(max_length=50, db_index=True, help_text="Provider used (gemini, huggingface).")
    model = models.CharField(max_length=100, help_text="Model identifier.")
    operation = models.CharField(max_length=100, default="extract_opportunity")
    opportunity = models.ForeignKey(
        Opportunity,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ai_usage_logs",
    )
    requested_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    success = models.BooleanField(default=False)
    input_tokens = models.PositiveIntegerField(null=True, blank=True)
    output_tokens = models.PositiveIntegerField(null=True, blank=True)
    error_type = models.CharField(max_length=100, blank=True)
    error_message = models.TextField(blank=True)

    class Meta:
        verbose_name = "AI Usage Log"
        verbose_name_plural = "AI Usage Logs"
        ordering = ["-requested_at"]

    @property
    def latency_seconds(self) -> float:
        if self.completed_at and self.requested_at:
            return round((self.completed_at - self.requested_at).total_seconds(), 2)
        return 0.0

    def __str__(self) -> str:
        status_str = "Success" if self.success else "Failed"
        return f"{self.provider}:{self.model} - {self.operation} [{status_str}]"

