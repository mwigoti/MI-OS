"""
MwohaOS Application Readiness Service — Milestone 5: Application Workspace
Evaluates deterministic submission readiness, validates mandatory materials, questions, and signoff.
"""
from typing import Dict, Any, List
from django.utils import timezone
from apps.applications.models import Application, ApplicationDocument, ApplicationQuestion
from apps.applications.constants import (
    DocumentAttachmentStatus,
    QuestionStatus,
)


def evaluate_application_readiness(application: Application, save: bool = True) -> Dict[str, Any]:
    """
    Evaluates the readiness of an Application for submission.
    Scoring breakdown (100 total):
      - 40 pts: Required Document completeness (all required docs attached or verified)
      - 30 pts: Application Questionnaire completeness (all required questions answered & within limits)
      - 20 pts: User Review & Signoff (user explicitly verified application package)
      - 10 pts: Submission Channel & Planning (portal URL or valid deadline set)
    """
    blockers: List[str] = []
    warnings: List[str] = []

    # 1. Evaluate Documents (40 points)
    docs = list(application.application_documents.all())
    required_docs = [d for d in docs if d.is_required]
    
    doc_points = 0.0
    missing_docs: List[str] = []
    attached_docs: List[str] = []

    if required_docs:
        valid_attached = 0
        for doc in required_docs:
            if doc.status in (DocumentAttachmentStatus.ATTACHED, DocumentAttachmentStatus.VERIFIED) and doc.has_file:
                valid_attached += 1
                attached_docs.append(doc.title)
            else:
                missing_docs.append(doc.title)
                blockers.append(f"Required document '{doc.title}' is missing or unattached.")
        
        doc_ratio = valid_attached / len(required_docs)
        doc_points = doc_ratio * 40.0
    else:
        # If no specific required docs configured, give base points but warn
        doc_points = 30.0
        warnings.append("No required documents configured for this opportunity.")

    # 2. Evaluate Questions (30 points)
    questions = list(application.questions.all())
    required_questions = [q for q in questions if q.is_required]

    question_points = 0.0
    unanswered_questions: List[str] = []
    over_limit_questions: List[str] = []

    if required_questions:
        answered_count = 0
        for q in required_questions:
            if q.answer_draft and q.answer_draft.strip():
                if not q.is_within_limits:
                    over_limit_questions.append(q.question_text[:50])
                    blockers.append(f"Answer for '{q.question_text[:40]}...' exceeds word/character limits.")
                else:
                    if q.status in (QuestionStatus.READY_FOR_REVIEW, QuestionStatus.FINAL):
                        answered_count += 1
                    else:
                        answered_count += 0.7  # In progress
            else:
                unanswered_questions.append(q.question_text[:50])
                blockers.append(f"Mandatory question '{q.question_text[:40]}...' is unanswered.")

        q_ratio = min(1.0, answered_count / len(required_questions))
        question_points = q_ratio * 30.0
    else:
        # If no questions required, full points
        question_points = 30.0

    # 3. Evaluate User Review & Signoff (20 points)
    review_points = 0.0
    if application.user_review_completed:
        review_points = 20.0
    else:
        warnings.append("Application materials have not received final user review signoff.")

    # 4. Submission Planning & Details (10 points)
    planning_points = 0.0
    has_portal = bool(application.portal_url or (application.opportunity and application.opportunity.application_url))
    if has_portal:
        planning_points += 5.0
    else:
        warnings.append("No submission portal URL configured.")

    deadline = application.active_deadline
    if deadline:
        days = application.days_remaining
        if days is not None:
            if days < 0:
                blockers.append("The target deadline for this opportunity has already passed.")
            elif days <= 3:
                warnings.append(f"Deadline is imminent ({days} days remaining).")
                planning_points += 5.0
            else:
                planning_points += 5.0
    else:
        warnings.append("No target or official deadline set.")
        planning_points += 2.0

    total_score = int(round(doc_points + question_points + review_points + planning_points))
    total_score = max(0, min(100, total_score))

    # Determine Ready to Submit:
    # Requires zero critical blockers AND all required documents attached AND mandatory questions done
    is_ready = (
        len(missing_docs) == 0
        and len(unanswered_questions) == 0
        and len(over_limit_questions) == 0
        and not (application.is_overdue)
    )

    result = {
        "readiness_score": total_score,
        "is_ready_to_submit": is_ready,
        "blockers": blockers,
        "warnings": warnings,
        "document_score": int(round(doc_points)),
        "question_score": int(round(question_points)),
        "review_score": int(round(review_points)),
        "planning_score": int(round(planning_points)),
        "required_documents_total": len(required_docs),
        "required_documents_attached": len(attached_docs),
        "missing_documents": missing_docs,
        "required_questions_total": len(required_questions),
        "unanswered_questions": unanswered_questions,
        "user_review_completed": application.user_review_completed,
    }

    if save:
        application.readiness_score = total_score
        application.is_ready_to_submit = is_ready
        application.save(update_fields=["readiness_score", "is_ready_to_submit", "updated_at"])

    return result
