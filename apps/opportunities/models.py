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
