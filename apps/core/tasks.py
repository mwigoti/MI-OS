"""
MwohaOS Core Celery Tasks
Harmless system validation tasks.
"""
import logging
from celery import shared_task

logger = logging.getLogger("mwohaos")


@shared_task(name="core.tasks.health_check_task")
def health_check_task() -> str:
    """
    Validates Celery worker execution and message queue round-trip.
    """
    logger.info("Executing MwohaOS Celery health check task.")
    return "MwohaOS Celery task executed successfully."
