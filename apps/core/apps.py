import logging
from django.apps import AppConfig

logger = logging.getLogger("mwohaos")

class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    verbose_name = "Core"

    def ready(self):
        # Section 15: Log application startup
        logger.info("MwohaOS Core initialized successfully.")
