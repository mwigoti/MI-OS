"""
MwohaOS Accounts Models
User account preferences and configuration settings.
"""
from django.conf import settings
from django.db import models
from apps.core.models import TimeStampedModel


class UserPreference(TimeStampedModel):
    """
    Stores user preferences including UI timezone and notification preferences.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="preferences",
    )
    timezone = models.CharField(
        max_length=64,
        default="Africa/Nairobi",
        help_text="User display timezone for dates and deadline tracking.",
    )
    email_notifications = models.BooleanField(
        default=True,
        help_text="Whether to receive system notifications via email.",
    )

    def __str__(self) -> str:
        return f"Preferences for {self.user.username}"
