"""
MwohaOS Context Processors
Provides global template context variables.
"""
from django.conf import settings
from django.utils import timezone


def mwohaos_context(request):
    """
    Injects platform metadata, timezone, and environment status into all templates.
    """
    return {
        "APP_NAME": getattr(settings, "APP_NAME", "MwohaOS"),
        "APP_VERSION": getattr(settings, "APP_VERSION", "0.1.0"),
        "APP_DESCRIPTION": getattr(settings, "APP_DESCRIPTION", "Personal Opportunity Operating System"),
        "CURRENT_TIMEZONE": getattr(settings, "TIME_ZONE", "Africa/Nairobi"),
        "IS_DEBUG": settings.DEBUG,
        "CURRENT_TIME": timezone.now(),
    }
