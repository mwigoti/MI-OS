"""
MwohaOS AI Preparation Service Orchestrator — Milestone 6: AI Preparation
Coordinates full application preparation passes, version rollbacks, and status reporting.
"""
import logging
from typing import Dict, Any, List
from django.utils import timezone

from apps.applications.models import (
    Application,
    ApplicationDocument,
    ApplicationDocumentVersion,
    ApplicationQuestion,
    QuestionDraftVersion,
    CVTailoringResult,
    ApplicationActivity,
)
from apps.applications.constants import (
    DocumentRole,
    QuestionStatus,
    ActivityType,
    AITone,
)
from apps.applications.services.readiness import evaluate_application_readiness
from .cover_letter import generate_tailored_cover_letter
from .cv_tailor import generate_cv_tailoring
from .question_answering import draft_question_answer

logger = logging.getLogger("mwohaos.ai_prep.service")


class AIPreparationService:
    """
    Unified coordinator for Milestone 6 AI preparation actions.
    """

    @staticmethod
    def prepare_full_application(
        application: Application,
        tone: str = AITone.STAR_METHOD,
        force_deterministic: bool = False,
    ) -> Dict[str, Any]:
        """
        Runs complete AI preparation pass for an application:
        1. Generates tailored cover letter
        2. Performs CV tailoring and ATS alignment analysis
        3. Drafts answers for all unanswered mandatory application questions
        """
        results: Dict[str, Any] = {
            "cover_letter": None,
            "cv_tailoring": None,
            "questions_drafted": [],
        }

        # 1. Cover Letter
        try:
            cl_res = generate_tailored_cover_letter(
                application,
                tone="PROFESSIONAL",
                force_deterministic=force_deterministic,
            )
            results["cover_letter"] = cl_res
        except Exception as e:
            logger.error(f"Failed to generate cover letter for {application.id}: {e}", exc_info=True)
            results["cover_letter"] = {"success": False, "error": str(e)}

        # 2. CV Tailoring
        try:
            cv_res = generate_cv_tailoring(
                application,
                update_cv_document=True,
                force_deterministic=force_deterministic,
            )
            results["cv_tailoring"] = cv_res
        except Exception as e:
            logger.error(f"Failed to generate CV tailoring for {application.id}: {e}", exc_info=True)
            results["cv_tailoring"] = {"success": False, "error": str(e)}

        # 3. Draft Questions
        for q in application.questions.filter(is_required=True):
            try:
                q_res = draft_question_answer(
                    q,
                    tone=tone,
                    force_deterministic=force_deterministic,
                )
                results["questions_drafted"].append(q_res)
            except Exception as e:
                logger.error(f"Failed to draft question {q.id}: {e}", exc_info=True)
                results["questions_drafted"].append({"question_id": str(q.id), "success": False, "error": str(e)})

        # Recalculate readiness
        readiness_report = evaluate_application_readiness(application, save=True)
        results["final_readiness_score"] = readiness_report["readiness_score"]
        results["is_ready_to_submit"] = readiness_report["is_ready_to_submit"]

        return results

    @staticmethod
    def apply_document_version(version: ApplicationDocumentVersion) -> ApplicationDocument:
        """
        Reverts or activates a specific document version.
        """
        doc = version.application_document
        doc.versions.filter(is_active=True).update(is_active=False)
        version.is_active = True
        version.save(update_fields=["is_active"])

        doc.content = version.content
        doc.tailored_notes = f"Reverted to Draft v{version.version_number}."
        doc.save()

        # Audit
        ApplicationActivity.objects.create(
            application=doc.application,
            activity_type=ActivityType.AI_APPLIED,
            from_status=doc.application.status,
            to_status=doc.application.status,
            description=f"Applied version v{version.version_number} for '{doc.title}'.",
        )

        evaluate_application_readiness(doc.application, save=True)
        return doc

    @staticmethod
    def apply_question_version(version: QuestionDraftVersion) -> ApplicationQuestion:
        """
        Reverts or activates a specific question draft version.
        """
        question = version.question
        question.draft_versions.filter(is_selected=True).update(is_selected=False)
        version.is_selected = True
        version.save(update_fields=["is_selected"])

        question.answer_draft = version.answer_text
        question.status = QuestionStatus.READY_FOR_REVIEW
        question.save()

        # Audit
        ApplicationActivity.objects.create(
            application=question.application,
            activity_type=ActivityType.AI_APPLIED,
            from_status=question.application.status,
            to_status=question.application.status,
            description=f"Applied draft v{version.version_number} ({version.get_tone_display()}) for question '{question.question_text[:35]}...'.",
        )

        evaluate_application_readiness(question.application, save=True)
        return question

    @staticmethod
    def get_prep_summary(application: Application) -> Dict[str, Any]:
        """
        Gathers comprehensive AI preparation state for workspace display.
        """
        # Cover Letter
        cl_doc = application.application_documents.filter(document_role=DocumentRole.COVER_LETTER).first()
        cl_versions = list(cl_doc.versions.all()) if cl_doc else []
        active_cl_version = next((v for v in cl_versions if v.is_active), None)

        # Tailored CV
        cv_doc = application.application_documents.filter(document_role__in=[DocumentRole.CV, DocumentRole.RESUME]).first()
        cv_versions = list(cv_doc.versions.all()) if cv_doc else []
        active_cv_version = next((v for v in cv_versions if v.is_active), None)

        cv_tailoring = getattr(application, "cv_tailoring", None)

        # Questions
        questions = []
        for q in application.questions.all():
            q_versions = list(q.draft_versions.all())
            selected_v = next((v for v in q_versions if v.is_selected), None)
            questions.append({
                "question": q,
                "versions": q_versions,
                "selected_version": selected_v,
            })

        return {
            "cover_letter_doc": cl_doc,
            "cover_letter_versions": cl_versions,
            "active_cl_version": active_cl_version,
            "cv_doc": cv_doc,
            "cv_versions": cv_versions,
            "active_cv_version": active_cv_version,
            "cv_tailoring": cv_tailoring,
            "questions": questions,
        }
