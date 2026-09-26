"""
MwohaOS Core Models
Shared abstract foundation models.
"""
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-updating
    ``created_at`` and ``updated_at`` fields using timezone-aware datetimes.
    """
    created_at = models.DateTimeField(
        default=timezone.now,
        editable=False,
        help_text="Timestamp when this record was created (timezone-aware).",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when this record was last modified (timezone-aware).",
    )

    class Meta:
        abstract = True
        ordering = ["-created_at"]
