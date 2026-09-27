"""
MwohaOS Applications Celery Tasks — Milestone 6: AI Preparation
Asynchronous workers for generation of tailored cover letters, CV optimizations,
and application questionnaires.
"""
import logging
from celery import shared_task
from apps.applications.models import Application, ApplicationQuestion
from apps.applications.services.ai_prep import (
    generate_tailored_cover_letter,
    generate_cv_tailoring,
    draft_question_answer,
    AIPreparationService,
)

logger = logging.getLogger("mwohaos.applications.tasks")


@shared_task(name="apps.applications.tasks.generate_tailored_cover_letter_task", bind=True, max_retries=2)
def generate_tailored_cover_letter_task(self, application_id: str, tone: str = "PROFESSIONAL"):
    try:
        app = Application.objects.get(id=application_id)
        result = generate_tailored_cover_letter(app, tone=tone)
        return {
            "application_id": application_id,
            "document_id": result.get("document_id"),
            "version_number": result.get("version_number"),
            "success": True,
        }
    except Exception as e:
        logger.error(f"Task generate_tailored_cover_letter_task failed: {e}", exc_info=True)
        raise self.retry(exc=e, countdown=10)


@shared_task(name="apps.applications.tasks.generate_cv_tailoring_task", bind=True, max_retries=2)
def generate_cv_tailoring_task(self, application_id: str):
    try:
        app = Application.objects.get(id=application_id)
        result = generate_cv_tailoring(app, update_cv_document=True)
        return {
            "application_id": application_id,
            "tailoring_id": result.get("tailoring_id"),
            "success": True,
        }
    except Exception as e:
        logger.error(f"Task generate_cv_tailoring_task failed: {e}", exc_info=True)
        raise self.retry(exc=e, countdown=10)


@shared_task(name="apps.applications.tasks.draft_question_answer_task", bind=True, max_retries=2)
def draft_question_answer_task(self, question_id: str, tone: str = "STAR_METHOD"):
    try:
        q = ApplicationQuestion.objects.get(id=question_id)
        result = draft_question_answer(q, tone=tone)
        return {
            "question_id": question_id,
            "version_number": result.get("version_number"),
            "success": True,
        }
    except Exception as e:
        logger.error(f"Task draft_question_answer_task failed: {e}", exc_info=True)
        raise self.retry(exc=e, countdown=10)


@shared_task(name="apps.applications.tasks.prepare_full_application_task", bind=True, max_retries=1)
def prepare_full_application_task(self, application_id: str, tone: str = "STAR_METHOD"):
    try:
        app = Application.objects.get(id=application_id)
        result = AIPreparationService.prepare_full_application(app, tone=tone)
        return {
            "application_id": application_id,
            "readiness_score": result.get("final_readiness_score"),
            "success": True,
        }
    except Exception as e:
        logger.error(f"Task prepare_full_application_task failed: {e}", exc_info=True)
        raise self.retry(exc=e, countdown=15)
