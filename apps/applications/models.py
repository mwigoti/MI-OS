"""
MwohaOS Applications Models — Milestone 5: Application Workspace
Structured application management, material tailoring, question answering, and review workspace.
"""
import os
import uuid
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from apps.core.models import TimeStampedModel
from apps.profiles.models import Profile
from apps.opportunities.models import Opportunity
from apps.documents.models import Document, validate_document_file
from .constants import (
    ApplicationStatus,
    ApplicationPriority,
    SubmissionMethod,
    DocumentRole,
    DocumentAttachmentStatus,
    QuestionStatus,
    QuestionCategory,
    NoteCategory,
    ActivityType,
    AITone,
    AIPrepStatus,
)


def application_upload_path(instance, filename: str) -> str:
    """
    Generate an isolated, unguessable storage path for application-specific document attachments.
    Format: applications/user_<user_id>/app_<app_id>/<uuid>_<clean_filename>
    """
    user_id = instance.application.profile.user_id
    app_id = instance.application.id
    ext = os.path.splitext(filename)[1].lower()
    safe_name = "".join(c for c in os.path.splitext(filename)[0] if c.isalnum() or c in ("-", "_"))[:50]
    unique_name = f"{uuid.uuid4().hex[:12]}_{safe_name}{ext}"
    return f"applications/user_{user_id}/app_{app_id}/{unique_name}"


class Application(TimeStampedModel):
    """
    Primary workspace entity representing a candidate's structured application for an Opportunity.
    Maintains materials checklist, questions, readiness score, submission records, and audit history.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="applications",
        db_index=True,
    )
    opportunity = models.ForeignKey(
        Opportunity,
        on_delete=models.CASCADE,
        related_name="applications",
        db_index=True,
    )
    match = models.ForeignKey(
        "matching.OpportunityMatch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="applications",
    )

    # Lifecycle & Priority
    status = models.CharField(
        max_length=50,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.SAVED,
        db_index=True,
    )
    priority = models.CharField(
        max_length=50,
        choices=ApplicationPriority.choices,
        default=ApplicationPriority.MEDIUM,
        db_index=True,
    )

    # Strategy & Notes
    custom_title = models.CharField(
        max_length=255,
        blank=True,
        help_text="Custom title override for internal tracking (defaults to opportunity title).",
    )
    custom_organization = models.CharField(
        max_length=255,
        blank=True,
        help_text="Custom organization override.",
    )
    strategy_notes = models.TextField(
        blank=True,
        help_text="Personal positioning strategy, narrative angle, or research findings.",
    )
    portal_url = models.URLField(
        blank=True,
        max_length=1000,
        help_text="Official application submission portal URL.",
    )

    # Dates & Deadlines
    target_submission_date = models.DateField(
        null=True,
        blank=True,
        help_text="Personal target completion date (defaults to opportunity deadline).",
    )

    # Readiness & Checklist Validation
    readiness_score = models.PositiveSmallIntegerField(
        default=0,
        help_text="Deterministic readiness score (0-100) based on materials, questions, and review.",
    )
    is_ready_to_submit = models.BooleanField(
        default=False,
        help_text="True when all mandatory documents and questions are completed.",
    )
    user_review_completed = models.BooleanField(
        default=False,
        help_text="Explicit user signoff before final submission.",
    )
    user_review_notes = models.TextField(
        blank=True,
        help_text="Candidate signoff comments or final review notes.",
    )
    user_reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    # Submission Records
    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    submission_method = models.CharField(
        max_length=50,
        choices=SubmissionMethod.choices,
        default=SubmissionMethod.PORTAL,
        blank=True,
    )
    submission_confirmation_code = models.CharField(
        max_length=255,
        blank=True,
        help_text="Confirmation number, receipt reference, or application ID.",
    )
    submission_notes = models.TextField(
        blank=True,
        help_text="Submission confirmation receipt details, portal message, or verification notes.",
    )

    class Meta:
        verbose_name = "Application"
        verbose_name_plural = "Applications"
        unique_together = ("profile", "opportunity")
        ordering = ["-updated_at"]

    def __str__(self) -> str:
        return f"{self.display_title} ({self.get_status_display()})"

    @property
    def display_title(self) -> str:
        return self.custom_title or (self.opportunity.title if self.opportunity else "Untitled Application")

    @property
    def display_organization(self) -> str:
        return self.custom_organization or (self.opportunity.organization if self.opportunity else "")

    @property
    def active_deadline(self):
        if self.target_submission_date:
            return self.target_submission_date
        if self.opportunity and self.opportunity.deadline:
            return self.opportunity.deadline
        return None

    @property
    def days_remaining(self) -> int | None:
        deadline = self.active_deadline
        if not deadline:
            return None
        today = timezone.localdate()
        return (deadline - today).days

    @property
    def is_overdue(self) -> bool:
        rem = self.days_remaining
        if rem is None:
            return False
        return rem < 0 and self.status not in (
            ApplicationStatus.SUBMITTED,
            ApplicationStatus.UNDER_REVIEW,
            ApplicationStatus.INTERVIEWING,
            ApplicationStatus.OFFERED,
            ApplicationStatus.REJECTED,
            ApplicationStatus.WITHDRAWN,
            ApplicationStatus.ARCHIVED,
        )


class ApplicationDocument(TimeStampedModel):
    """
    Required or supplementary document attached to an application.
    Can reference a verified file from the user's Document Vault or an application-tailored file.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="application_documents",
        db_index=True,
    )
    document = models.ForeignKey(
        Document,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="application_usages",
        help_text="Linked document from the user's Document Vault.",
    )
    document_role = models.CharField(
        max_length=50,
        choices=DocumentRole.choices,
        default=DocumentRole.CV,
        db_index=True,
    )
    title = models.CharField(
        max_length=255,
        help_text="Label for this document (e.g. 'Targeted 2-Page CV', 'Cover Letter Draft').",
    )
    is_required = models.BooleanField(
        default=True,
        help_text="Whether this document is mandatory for application submission.",
    )
    is_tailored = models.BooleanField(
        default=False,
        help_text="Flag indicating this document was specifically customized for this opportunity.",
    )
    tailored_notes = models.TextField(
        blank=True,
        help_text="Summary of customizations made to tailor this document for the role.",
    )
    content = models.TextField(
        blank=True,
        help_text="Tailored document text or markdown (e.g. for generated cover letters or tailored CV text).",
    )
    status = models.CharField(
        max_length=50,
        choices=DocumentAttachmentStatus.choices,
        default=DocumentAttachmentStatus.ATTACHED,
        db_index=True,
    )
    file = models.FileField(
        upload_to=application_upload_path,
        validators=[validate_document_file],
        blank=True,
        null=True,
        help_text="Optional dedicated file uploaded specifically for this application.",
    )

    class Meta:
        verbose_name = "Application Document"
        verbose_name_plural = "Application Documents"
        ordering = ["-is_required", "created_at"]

    def __str__(self) -> str:
        return f"{self.title} [{self.get_document_role_display()}] - {self.get_status_display()}"

    @property
    def has_file(self) -> bool:
        return bool(self.file) or (self.document is not None and bool(self.document.file)) or bool(self.content and self.content.strip())

    @property
    def effective_file_url(self) -> str | None:
        if self.file:
            return self.file.url
        if self.document and self.document.file:
            return self.document.file.url
        return None

    @property
    def effective_filename(self) -> str:
        if self.file:
            return os.path.basename(self.file.name)
        if self.document and self.document.file:
            return os.path.basename(self.document.file.name)
        return ""


class ApplicationQuestion(TimeStampedModel):
    """
    Application question, essay prompt, or motivation statement required by the opportunity.
    Allows drafting, tracking word/character limits, and reviewing responses.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="questions",
        db_index=True,
    )
    question_text = models.TextField(
        help_text="The prompt or question asked in the application.",
    )
    category = models.CharField(
        max_length=50,
        choices=QuestionCategory.choices,
        default=QuestionCategory.MOTIVATION,
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        help_text="Order in the application questionnaire.",
    )
    is_required = models.BooleanField(
        default=True,
        help_text="Whether answering this question is required for submission.",
    )
    max_words = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum allowed words (optional).",
    )
    max_characters = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum allowed characters (optional).",
    )
    answer_draft = models.TextField(
        blank=True,
        help_text="Candidate answer draft.",
    )
    status = models.CharField(
        max_length=50,
        choices=QuestionStatus.choices,
        default=QuestionStatus.NOT_STARTED,
        db_index=True,
    )

    class Meta:
        verbose_name = "Application Question"
        verbose_name_plural = "Application Questions"
        ordering = ["order", "created_at"]

    def __str__(self) -> str:
        return f"Q: {self.question_text[:60]}... ({self.get_status_display()})"

    @property
    def word_count(self) -> int:
        if not self.answer_draft:
            return 0
        return len(self.answer_draft.split())

    @property
    def char_count(self) -> int:
        if not self.answer_draft:
            return 0
        return len(self.answer_draft)

    @property
    def is_within_limits(self) -> bool:
        if self.max_words and self.word_count > self.max_words:
            return False
        if self.max_characters and self.char_count > self.max_characters:
            return False
        return True


class ApplicationNote(TimeStampedModel):
    """
    Workspace notes, contact information, research details, and interview preparation logs.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="notes",
        db_index=True,
    )
    title = models.CharField(
        max_length=200,
        blank=True,
    )
    category = models.CharField(
        max_length=50,
        choices=NoteCategory.choices,
        default=NoteCategory.GENERAL,
    )
    content = models.TextField()
    is_pinned = models.BooleanField(
        default=False,
    )

    class Meta:
        verbose_name = "Application Note"
        verbose_name_plural = "Application Notes"
        ordering = ["-is_pinned", "-created_at"]

    def __str__(self) -> str:
        return f"{self.title or self.get_category_display()} ({self.created_at.strftime('%Y-%m-%d')})"


class ApplicationActivity(TimeStampedModel):
    """
    Audit log of state changes, document attachments, and application actions.
    Provides verifiable traceability across the application lifecycle.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="activities",
        db_index=True,
    )
    activity_type = models.CharField(
        max_length=50,
        choices=ActivityType.choices,
        default=ActivityType.STATUS_CHANGE,
    )
    from_status = models.CharField(
        max_length=50,
        blank=True,
    )
    to_status = models.CharField(
        max_length=50,
        blank=True,
    )
    description = models.TextField()

    class Meta:
        verbose_name = "Application Activity"
        verbose_name_plural = "Application Activities"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.get_activity_type_display()}: {self.description[:50]}"


class ApplicationDocumentVersion(TimeStampedModel):
    """
    Versioned iteration of an application document (Cover Letter, Tailored CV, Proposal).
    Allows reviewing previous drafts, comparing diffs, and rolling back.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application_document = models.ForeignKey(
        ApplicationDocument,
        on_delete=models.CASCADE,
        related_name="versions",
        db_index=True,
    )
    version_number = models.PositiveIntegerField(default=1)
    title = models.CharField(max_length=255, blank=True)
    content = models.TextField(help_text="Tailored document text or markdown.")
    tailoring_notes = models.TextField(blank=True, help_text="Notes on how this draft was tailored.")
    grounding_evidence = models.JSONField(
        default=list,
        blank=True,
        help_text="Traceable citations of profile experiences, skills, and projects used in this version.",
    )
    provider = models.CharField(max_length=50, default="DETERMINISTIC")
    model = models.CharField(max_length=100, blank=True)
    token_metrics = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Application Document Version"
        verbose_name_plural = "Application Document Versions"
        ordering = ["-version_number", "-created_at"]
        unique_together = ("application_document", "version_number")

    def __str__(self) -> str:
        return f"{self.application_document.title} (v{self.version_number})"

    @property
    def word_count(self) -> int:
        return len(self.content.split()) if self.content else 0


class QuestionDraftVersion(TimeStampedModel):
    """
    Versioned answer draft for an ApplicationQuestion with style/tone and evidence grounding.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(
        ApplicationQuestion,
        on_delete=models.CASCADE,
        related_name="draft_versions",
        db_index=True,
    )
    version_number = models.PositiveIntegerField(default=1)
    tone = models.CharField(
        max_length=50,
        choices=AITone.choices,
        default=AITone.STAR_METHOD,
    )
    answer_text = models.TextField()
    word_count = models.PositiveIntegerField(default=0)
    char_count = models.PositiveIntegerField(default=0)
    grounding_evidence = models.JSONField(
        default=list,
        blank=True,
        help_text="Profile evidence citations incorporated into this answer.",
    )
    provider = models.CharField(max_length=50, default="DETERMINISTIC")
    model = models.CharField(max_length=100, blank=True)
    token_metrics = models.JSONField(default=dict, blank=True)
    is_selected = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Question Draft Version"
        verbose_name_plural = "Question Draft Versions"
        ordering = ["-version_number", "-created_at"]
        unique_together = ("question", "version_number")

    def __str__(self) -> str:
        return f"Q:{self.question_id} v{self.version_number} [{self.get_tone_display()}]"

    def save(self, *args, **kwargs):
        if self.answer_text:
            self.word_count = len(self.answer_text.split())
            self.char_count = len(self.answer_text)
        super().save(*args, **kwargs)


class CVTailoringResult(TimeStampedModel):
    """
    Structured CV/Resume tailoring optimization results and recommendations for an Application.
    Maps profile assets to opportunity requirements, providing targeted summary, prioritized skills,
    and tailored bullet points.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.OneToOneField(
        Application,
        on_delete=models.CASCADE,
        related_name="cv_tailoring",
        db_index=True,
    )
    targeted_summary = models.TextField(
        blank=True,
        help_text="Targeted professional summary emphasizing opportunity alignment.",
    )
    prioritized_skills = models.JSONField(
        default=list,
        blank=True,
        help_text="Skills ordered by relevance to requirements with match explanations.",
    )
    tailored_experience_bullets = models.JSONField(
        default=list,
        blank=True,
        help_text="Accomplishment bullet points enhanced with action verbs and metrics.",
    )
    selected_projects = models.JSONField(
        default=list,
        blank=True,
        help_text="Recommended projects highlighting target proficiencies.",
    )
    ats_keyword_coverage = models.JSONField(
        default=dict,
        blank=True,
        help_text="ATS keyword match statistics: coverage percentage, found keywords, missing keywords.",
    )
    provider = models.CharField(max_length=50, default="DETERMINISTIC")
    model = models.CharField(max_length=100, blank=True)
    token_metrics = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "CV Tailoring Result"
        verbose_name_plural = "CV Tailoring Results"

    def __str__(self) -> str:
        return f"CV Tailoring for {self.application.display_title}"

