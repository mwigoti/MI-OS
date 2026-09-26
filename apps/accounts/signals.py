"""
Accounts signals for automated preference creation.
"""
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserPreference


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_preference(sender, instance, created, **kwargs):
    if created:
        UserPreference.objects.create(
            user=instance,
            timezone=getattr(settings, "TIME_ZONE", "Africa/Nairobi"),
        )
