"""
MwohaOS Applications Pipeline Service — Milestone 5: Application Workspace
Manages application workspace initialization, document auto-population from intelligence,
stage transitions, and submission recording.
"""
from typing import Optional
from django.utils import timezone
from apps.profiles.models import Profile
from apps.documents.models import Document
from apps.opportunities.models import Opportunity
from apps.matching.models import OpportunityMatch
from apps.applications.models import (
    Application,
    ApplicationDocument,
    ApplicationActivity,
)
from apps.applications.constants import (
    ApplicationStatus,
    ApplicationPriority,
    DocumentRole,
    DocumentAttachmentStatus,
    SubmissionMethod,
    ActivityType,
)
from .readiness import evaluate_application_readiness


def _infer_document_role(doc_name: str) -> str:
    """Helper to map opportunity intelligence document text to a DocumentRole choice."""
    lower = doc_name.lower()
    if "cv" in lower or "curriculum" in lower:
        return DocumentRole.CV
    if "resume" in lower:
        return DocumentRole.RESUME
    if "cover" in lower or "letter of intent" in lower or "motivation" in lower:
        return DocumentRole.COVER_LETTER
    if "transcript" in lower or "academic" in lower:
        return DocumentRole.TRANSCRIPT
    if "portfolio" in lower or "sample" in lower:
        return DocumentRole.PORTFOLIO
    if "certificate" in lower or "degree" in lower or "accreditation" in lower:
        return DocumentRole.CERTIFICATE
    if "proposal" in lower or "concept" in lower:
        return DocumentRole.PROPOSAL
    if "recommendation" in lower or "reference" in lower:
        return DocumentRole.RECOMMENDATION
    if "id" in lower or "passport" in lower or "identification" in lower:
        return DocumentRole.IDENTIFICATION
    return DocumentRole.OTHER


def create_or_get_application(
    profile: Profile,
    opportunity: Opportunity,
    match: Optional[OpportunityMatch] = None,
    priority: str = ApplicationPriority.MEDIUM,
) -> Application:
    """
    Initializes or retrieves an application workspace for a Profile and Opportunity.
    Auto-populates required document slots using OpportunityIntelligence requirements
    and links existing primary documents from the user's Document Vault when available.
    """
    app, created = Application.objects.get_or_create(
        profile=profile,
        opportunity=opportunity,
        defaults={
            "priority": priority,
            "portal_url": opportunity.application_url or "",
            "target_submission_date": opportunity.deadline,
        }
    )

    if match and not app.match:
        app.match = match
        app.save(update_fields=["match"])
    elif not app.match:
        existing_match = OpportunityMatch.objects.filter(profile=profile, opportunity=opportunity).first()
        if existing_match:
            app.match = existing_match
            app.save(update_fields=["match"])

    if created:
        # Record creation activity
        ApplicationActivity.objects.create(
            application=app,
            activity_type=ActivityType.CREATED,
            from_status="",
            to_status=app.status,
            description="Application workspace initialized.",
        )

        # Auto-populate document requirements from intelligence if available
        created_docs = []
        intelligence = getattr(opportunity, "intelligence", None)
        req_docs = []
        if intelligence and isinstance(intelligence.required_documents, list) and intelligence.required_documents:
            req_docs = intelligence.required_documents

        if req_docs:
            for item in req_docs:
                title_str = str(item).strip()
                if not title_str:
                    continue
                role = _infer_document_role(title_str)
                
                # Check if user has an existing matching primary document in vault
                matching_vault_doc = Document.objects.filter(
                    profile=profile,
                    document_type=role,
                    is_primary=True,
                ).first()
                if not matching_vault_doc:
                    # Fallback to any document of that type
                    matching_vault_doc = Document.objects.filter(
                        profile=profile,
                        document_type=role,
                    ).first()

                app_doc = ApplicationDocument.objects.create(
                    application=app,
                    document=matching_vault_doc,
                    document_role=role,
                    title=title_str,
                    is_required=True,
                    status=DocumentAttachmentStatus.ATTACHED if matching_vault_doc else DocumentAttachmentStatus.MISSING,
                )
                created_docs.append(app_doc)
        else:
            # Default required CV/Resume slot
            primary_cv = Document.objects.filter(
                profile=profile,
                document_type__in=[Document.DocumentType.CV, Document.DocumentType.RESUME],
                is_primary=True,
            ).first()
            if not primary_cv:
                primary_cv = Document.objects.filter(
                    profile=profile,
                    document_type__in=[Document.DocumentType.CV, Document.DocumentType.RESUME],
                ).first()

            ApplicationDocument.objects.create(
                application=app,
                document=primary_cv,
                document_role=DocumentRole.CV,
                title="Curriculum Vitae / Resume",
                is_required=True,
                status=DocumentAttachmentStatus.ATTACHED if primary_cv else DocumentAttachmentStatus.MISSING,
            )

        # Calculate initial readiness
        evaluate_application_readiness(app, save=True)

    return app


def transition_application_status(
    application: Application,
    new_status: str,
    notes: str = "",
    user=None,
) -> Application:
    """
    Executes a validated stage movement across the application lifecycle.
    Logs an audit activity trail.
    """
    old_status = application.status
    if old_status == new_status:
        return application

    application.status = new_status
    if new_status == ApplicationStatus.SUBMITTED and not application.submitted_at:
        application.submitted_at = timezone.now()

    application.save(update_fields=["status", "submitted_at", "updated_at"])

    desc = f"Stage changed from '{old_status}' to '{new_status}'."
    if notes:
        desc += f" Note: {notes}"

    ApplicationActivity.objects.create(
        application=application,
        activity_type=ActivityType.STATUS_CHANGE,
        from_status=old_status,
        to_status=new_status,
        description=desc,
    )

    return application


def record_submission(
    application: Application,
    submission_method: str = SubmissionMethod.PORTAL,
    confirmation_code: str = "",
    submission_notes: str = "",
    submitted_at: Optional[timezone.datetime] = None,
) -> Application:
    """
    Records official submission confirmation for the application.
    Marks status as SUBMITTED and updates submission metadata.
    """
    old_status = application.status
    now = submitted_at or timezone.now()

    application.status = ApplicationStatus.SUBMITTED
    application.submitted_at = now
    application.submission_method = submission_method
    application.submission_confirmation_code = confirmation_code
    application.submission_notes = submission_notes
    application.save(
        update_fields=[
            "status",
            "submitted_at",
            "submission_method",
            "submission_confirmation_code",
            "submission_notes",
            "updated_at",
        ]
    )

    desc = f"Application recorded as submitted via {application.get_submission_method_display()}."
    if confirmation_code:
        desc += f" Confirmation code: {confirmation_code}."

    ApplicationActivity.objects.create(
        application=application,
        activity_type=ActivityType.SUBMISSION_RECORDED,
        from_status=old_status,
        to_status=ApplicationStatus.SUBMITTED,
        description=desc,
    )

    return application
