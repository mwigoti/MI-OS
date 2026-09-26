"""
MwohaOS Documents Models — Milestone 1: Document Management & Security
Secure, isolated file vault for resumes, certifications, transcripts, and professional proof.
"""
import os
import uuid
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from apps.core.models import TimeStampedModel


def document_upload_path(instance, filename: str) -> str:
    """
    Generate an isolated, unguessable, structured storage path for user documents.
    Prevents path traversal, filename collisions, and unauthorized enumeration.
    Format: documents/user_<user_id>/<uuid>_<clean_filename>
    """
    user_id = instance.profile.user_id
    ext = os.path.splitext(filename)[1].lower()
    safe_name = "".join(c for c in os.path.splitext(filename)[0] if c.isalnum() or c in ("-", "_"))[:50]
    unique_name = f"{uuid.uuid4().hex[:12]}_{safe_name}{ext}"
    return f"documents/user_{user_id}/{unique_name}"


def validate_document_file(file):
    """
    Validate uploaded document file size and extension.
    Accepts: PDF, DOCX, TXT, RTF, PNG, JPG, JPEG, WEBP.
    Enforces MAX_UPLOAD_SIZE_MB setting (defaults to 10MB).
    """
    allowed_extensions = {".pdf", ".docx", ".txt", ".rtf", ".png", ".jpg", ".jpeg", ".webp"}
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in allowed_extensions:
        raise ValidationError(
            f"Unsupported file format '{ext}'. Allowed formats: {', '.join(sorted(allowed_extensions))}."
        )

    max_size_bytes = getattr(settings, "MAX_UPLOAD_SIZE_MB", 10) * 1024 * 1024
    if file.size > max_size_bytes:
        raise ValidationError(
            f"File size ({file.size / (1024*1024):.1f}MB) exceeds the maximum allowed limit of {settings.MAX_UPLOAD_SIZE_MB}MB."
        )


class Document(TimeStampedModel):
    """
    Professional documents owned by a Profile.
    Multiple versions and document types (General CV, Geospatial CV, Transcripts, Certifications).
    """

    class DocumentType(models.TextChoices):
        CV = "CV", "Curriculum Vitae (CV)"
        RESUME = "RESUME", "Resume"
        CERTIFICATE = "CERTIFICATE", "Certificate / License"
        TRANSCRIPT = "TRANSCRIPT", "Academic Transcript"
        PORTFOLIO = "PORTFOLIO", "Portfolio / Work Sample"
        REFERENCE = "REFERENCE", "Letter of Recommendation / Reference"
        COVER_LETTER = "COVER_LETTER", "Cover Letter"
        PUBLICATION = "PUBLICATION", "Publication / Paper"
        AWARD = "AWARD", "Award Notice"
        IDENTIFICATION = "IDENTIFICATION", "Identification Document"
        OTHER = "OTHER", "Other Document"

    profile = models.ForeignKey(
        "profiles.Profile",
        on_delete=models.CASCADE,
        related_name="documents",
    )
    title = models.CharField(
        max_length=255,
        help_text="Descriptive title (e.g. 2026 Geospatial CV, AWS Solutions Architect Certificate).",
    )
    document_type = models.CharField(
        max_length=50,
        choices=DocumentType.choices,
        default=DocumentType.CV,
        db_index=True,
    )
    file = models.FileField(
        upload_to=document_upload_path,
        validators=[validate_document_file],
        help_text="Supported: PDF, DOCX, TXT, PNG, JPG (max 10MB).",
    )
    description = models.TextField(
        blank=True,
        help_text="Notes on this document, target audience, or specific revisions.",
    )
    version = models.CharField(
        max_length=50,
        default="1.0",
        help_text="Version identifier (e.g. 1.0, 2026-Q1, Tech-Focused).",
    )
    is_primary = models.BooleanField(
        default=False,
        help_text="Mark as the default / primary document for this category.",
    )

    class Meta:
        verbose_name = "Document"
        verbose_name_plural = "Documents"
        ordering = ["-is_primary", "-created_at"]

    def save(self, *args, **kwargs):
        # If this document is marked as primary, unmark existing primary docs of same type for this profile
        if self.is_primary:
            Document.objects.filter(
                profile=self.profile,
                document_type=self.document_type,
                is_primary=True,
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)

    @property
    def file_extension(self) -> str:
        if self.file:
            return os.path.splitext(self.file.name)[1].lower().replace(".", "").upper()
        return ""

    @property
    def file_size_display(self) -> str:
        try:
            if self.file and self.file.size:
                size = self.file.size
                if size < 1024:
                    return f"{size} B"
                elif size < 1024 * 1024:
                    return f"{size / 1024:.1f} KB"
                else:
                    return f"{size / (1024 * 1024):.1f} MB"
        except Exception:
            pass
        return "Unknown size"

    def __str__(self) -> str:
        return f"{self.title} ({self.get_document_type_display()} v{self.version})"
