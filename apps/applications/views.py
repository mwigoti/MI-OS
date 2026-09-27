"""
MwohaOS Applications Views — Milestone 5: Application Workspace
Provides end-to-end management for application workflows, materials tailoring,
question drafting, readiness verification, and submission tracking.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.opportunities.models import Opportunity
from apps.matching.models import OpportunityMatch
from .models import (
    Application,
    ApplicationDocument,
    ApplicationQuestion,
    ApplicationNote,
    ApplicationActivity,
    ApplicationDocumentVersion,
    QuestionDraftVersion,
    CVTailoringResult,
)
from .constants import (
    ApplicationStatus,
    ApplicationPriority,
    SubmissionMethod,
    DocumentRole,
    DocumentAttachmentStatus,
    QuestionStatus,
    ActivityType,
    AITone,
)
from .forms import (
    ApplicationCreateForm,
    ApplicationUpdateForm,
    ApplicationDocumentForm,
    ApplicationQuestionForm,
    ApplicationNoteForm,
    ApplicationSubmissionForm,
)
from .services import (
    evaluate_application_readiness,
    create_or_get_application,
    transition_application_status,
    record_submission,
)
from .services.ai_prep import (
    generate_tailored_cover_letter,
    generate_cv_tailoring,
    draft_question_answer,
    AIPreparationService,
)


@login_required
def application_list_view(request):
    """
    Application Workspace Dashboard:
    Displays status pipeline summaries, filterable application records, and readiness metrics.
    """
    profile = getattr(request.user, "profile", None)
    if not profile:
        messages.warning(request, "Please set up your professional profile first.")
        return redirect("profiles:overview")

    status_filter = request.GET.get("status", "")
    priority_filter = request.GET.get("priority", "")
    search_query = request.GET.get("q", "").strip()
    ordering = request.GET.get("order", "-updated_at")

    qs = Application.objects.filter(profile=profile).select_related("opportunity", "match")

    if status_filter:
        qs = qs.filter(status=status_filter)
    if priority_filter:
        qs = qs.filter(priority=priority_filter)
    if search_query:
        qs = qs.filter(
            Q(custom_title__icontains=search_query)
            | Q(custom_organization__icontains=search_query)
            | Q(opportunity__title__icontains=search_query)
            | Q(opportunity__organization__icontains=search_query)
        )

    # Valid sort fields
    valid_sorts = {
        "-updated_at": "-updated_at",
        "deadline": "target_submission_date",
        "-readiness": "-readiness_score",
        "priority": "priority",
        "status": "status",
    }
    qs = qs.order_by(valid_sorts.get(ordering, "-updated_at"))

    # Pipeline summary metrics
    all_apps = Application.objects.filter(profile=profile)
    stats = {
        "total": all_apps.count(),
        "saved": all_apps.filter(status=ApplicationStatus.SAVED).count(),
        "preparing": all_apps.filter(status=ApplicationStatus.PREPARING).count(),
        "ready": all_apps.filter(status__in=[ApplicationStatus.READY_FOR_REVIEW, ApplicationStatus.READY_TO_SUBMIT]).count(),
        "submitted": all_apps.filter(status=ApplicationStatus.SUBMITTED).count(),
        "review_interview": all_apps.filter(status__in=[ApplicationStatus.UNDER_REVIEW, ApplicationStatus.INTERVIEWING]).count(),
        "offered": all_apps.filter(status=ApplicationStatus.OFFERED).count(),
    }

    paginator = Paginator(qs, 15)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "applications/index.html",
        {
            "applications": page_obj,
            "page_obj": page_obj,
            "stats": stats,
            "status_filter": status_filter,
            "priority_filter": priority_filter,
            "search_query": search_query,
            "ordering": ordering,
            "statuses": ApplicationStatus.choices,
            "priorities": ApplicationPriority.choices,
        },
    )


@login_required
def application_detail_view(request, pk):
    """
    Comprehensive Application Workspace:
    Contains materials checklist, question drafting, readiness audit, notes, and submission actions.
    """
    profile = getattr(request.user, "profile", None)
    if not profile:
        return redirect("profiles:overview")

    application = get_object_or_404(
        Application.objects.select_related("opportunity", "opportunity__intelligence", "match"),
        pk=pk,
        profile=profile,
    )

    # Update readiness calculation
    readiness_report = evaluate_application_readiness(application, save=True)

    documents = application.application_documents.select_related("document").all()
    questions = application.questions.all().order_by("order", "created_at")
    notes = application.notes.all().order_by("-is_pinned", "-created_at")
    activities = application.activities.all().order_by("-created_at")[:20]

    # Quick action forms
    doc_form = ApplicationDocumentForm(profile=profile)
    question_form = ApplicationQuestionForm()
    note_form = ApplicationNoteForm()
    submission_form = ApplicationSubmissionForm(instance=application)
    update_form = ApplicationUpdateForm(instance=application)

    return render(
        request,
        "applications/detail.html",
        {
            "application": application,
            "readiness": readiness_report,
            "documents": documents,
            "questions": questions,
            "notes": notes,
            "activities": activities,
            "doc_form": doc_form,
            "question_form": question_form,
            "note_form": note_form,
            "submission_form": submission_form,
            "update_form": update_form,
            "statuses": ApplicationStatus.choices,
        },
    )


@login_required
def application_create_view(request):
    """
    Creates or initializes an Application Workspace for an Opportunity.
    Accepts GET query param ?opportunity=<uuid> or POST form.
    """
    profile = getattr(request.user, "profile", None)
    if not profile:
        messages.warning(request, "Please set up your profile first.")
        return redirect("profiles:overview")

    opp_id = request.GET.get("opportunity")
    if opp_id:
        opportunity = get_object_or_404(Opportunity, pk=opp_id)
        # Check if already exists
        existing = Application.objects.filter(profile=profile, opportunity=opportunity).first()
        if existing:
            messages.info(request, f"Application workspace for '{opportunity.title}' already exists.")
            return redirect("applications:detail", pk=existing.pk)

        # Look for match
        match = OpportunityMatch.objects.filter(profile=profile, opportunity=opportunity).first()
        app = create_or_get_application(profile=profile, opportunity=opportunity, match=match)
        messages.success(request, f"Application workspace created for '{opportunity.title}'.")
        return redirect("applications:detail", pk=app.pk)

    if request.method == "POST":
        form = ApplicationCreateForm(request.POST, profile=profile)
        if form.is_valid():
            opportunity = form.cleaned_data["opportunity"]
            existing = Application.objects.filter(profile=profile, opportunity=opportunity).first()
            if existing:
                messages.info(request, f"Application workspace for '{opportunity.title}' already exists.")
                return redirect("applications:detail", pk=existing.pk)

            match = OpportunityMatch.objects.filter(profile=profile, opportunity=opportunity).first()
            app = create_or_get_application(
                profile=profile,
                opportunity=opportunity,
                match=match,
                priority=form.cleaned_data.get("priority", ApplicationPriority.MEDIUM),
            )
            # Apply other fields
            if form.cleaned_data.get("target_submission_date"):
                app.target_submission_date = form.cleaned_data["target_submission_date"]
            if form.cleaned_data.get("portal_url"):
                app.portal_url = form.cleaned_data["portal_url"]
            if form.cleaned_data.get("strategy_notes"):
                app.strategy_notes = form.cleaned_data["strategy_notes"]
            app.save()

            messages.success(request, f"Workspace initialized for '{opportunity.title}'.")
            return redirect("applications:detail", pk=app.pk)
    else:
        form = ApplicationCreateForm(profile=profile)

    return render(request, "applications/form.html", {"form": form, "title": "Start New Application Workspace"})


@login_required
@require_POST
def application_update_view(request, pk):
    """Updates application settings and metadata."""
    profile = getattr(request.user, "profile", None)
    application = get_object_or_404(Application, pk=pk, profile=profile)

    form = ApplicationUpdateForm(request.POST, instance=application)
    if form.is_valid():
        old_status = application.status
        app = form.save()
        if old_status != app.status:
            ApplicationActivity.objects.create(
                application=app,
                activity_type=ActivityType.STATUS_CHANGE,
                from_status=old_status,
                to_status=app.status,
                description=f"Status updated via workspace settings to {app.get_status_display()}.",
            )
        evaluate_application_readiness(app, save=True)
        messages.success(request, "Application settings updated.")
    else:
        messages.error(request, "Please check the form for errors.")

    return redirect("applications:detail", pk=pk)


@login_required
@require_POST
def application_status_update_view(request, pk):
    """Quick stage transition action from the workspace header."""
    profile = getattr(request.user, "profile", None)
    application = get_object_or_404(Application, pk=pk, profile=profile)

    new_status = request.POST.get("status")
    notes = request.POST.get("notes", "")

    if new_status in ApplicationStatus.values:
        transition_application_status(application, new_status, notes=notes, user=request.user)
        evaluate_application_readiness(application, save=True)
        messages.success(request, f"Application moved to '{application.get_status_display()}'.")
    else:
        messages.error(request, "Invalid application status specified.")

    return redirect("applications:detail", pk=pk)


@login_required
@require_POST
def application_signoff_view(request, pk):
    """Toggles user review signoff for final application verification."""
    profile = getattr(request.user, "profile", None)
    application = get_object_or_404(Application, pk=pk, profile=profile)

    application.user_review_completed = not application.user_review_completed
    application.user_reviewed_at = timezone.now() if application.user_review_completed else None
    notes = request.POST.get("user_review_notes", "")
    if notes:
        application.user_review_notes = notes
    application.save(update_fields=["user_review_completed", "user_reviewed_at", "user_review_notes", "updated_at"])

    desc = "User completed final review signoff." if application.user_review_completed else "User revoked review signoff."
    ApplicationActivity.objects.create(
        application=application,
        activity_type=ActivityType.REVIEW_SIGNED_OFF,
        description=desc,
    )

    evaluate_application_readiness(application, save=True)
    if application.user_review_completed:
        messages.success(request, "Application materials verified and signed off for submission.")
    else:
        messages.info(request, "Review signoff removed.")

    return redirect("applications:detail", pk=pk)


@login_required
@require_POST
def application_document_add_view(request, pk):
    """Attaches a document to the application workspace."""
    profile = getattr(request.user, "profile", None)
    application = get_object_or_404(Application, pk=pk, profile=profile)

    form = ApplicationDocumentForm(request.POST, request.FILES, profile=profile)
    if form.is_valid():
        doc = form.save(commit=False)
        doc.application = application
        if doc.document and not doc.status:
            doc.status = DocumentAttachmentStatus.ATTACHED
        elif not doc.document and not doc.file:
            doc.status = DocumentAttachmentStatus.MISSING
        doc.save()

        ApplicationActivity.objects.create(
            application=application,
            activity_type=ActivityType.DOCUMENT_ATTACHED,
            description=f"Attached document: '{doc.title}' [{doc.get_document_role_display()}].",
        )
        evaluate_application_readiness(application, save=True)
        messages.success(request, f"Document '{doc.title}' added to workspace.")
    else:
        messages.error(request, "Error adding document. Please verify the fields.")

    return redirect("applications:detail", pk=pk)


@login_required
@require_POST
def application_document_delete_view(request, pk, doc_id):
    """Removes a document slot or attachment from the workspace."""
    profile = getattr(request.user, "profile", None)
    application = get_object_or_404(Application, pk=pk, profile=profile)
    doc = get_object_or_404(ApplicationDocument, pk=doc_id, application=application)

    title = doc.title
    doc.delete()

    ApplicationActivity.objects.create(
        application=application,
        activity_type=ActivityType.DOCUMENT_REMOVED,
        description=f"Removed document: '{title}'.",
    )
    evaluate_application_readiness(application, save=True)
    messages.info(request, f"Document '{title}' removed from workspace.")
    return redirect("applications:detail", pk=pk)


@login_required
@require_POST
def application_question_add_view(request, pk):
    """Adds a new application question prompt and answer draft."""
    profile = getattr(request.user, "profile", None)
    application = get_object_or_404(Application, pk=pk, profile=profile)

    form = ApplicationQuestionForm(request.POST)
    if form.is_valid():
        q = form.save(commit=False)
        q.application = application
        if q.answer_draft and q.answer_draft.strip() and q.status == QuestionStatus.NOT_STARTED:
            q.status = QuestionStatus.IN_PROGRESS
        q.save()

        ApplicationActivity.objects.create(
            application=application,
            activity_type=ActivityType.QUESTION_UPDATED,
            description=f"Added application question: '{q.question_text[:40]}...'",
        )
        evaluate_application_readiness(application, save=True)
        messages.success(request, "Application question added.")
    else:
        messages.error(request, "Failed to add question. Please check input.")

    return redirect("applications:detail", pk=pk)


@login_required
@require_POST
def application_question_edit_view(request, pk, q_id):
    """Updates an application question response draft."""
    profile = getattr(request.user, "profile", None)
    application = get_object_or_404(Application, pk=pk, profile=profile)
    question = get_object_or_404(ApplicationQuestion, pk=q_id, application=application)

    form = ApplicationQuestionForm(request.POST, instance=question)
    if form.is_valid():
        q = form.save()
        ApplicationActivity.objects.create(
            application=application,
            activity_type=ActivityType.QUESTION_UPDATED,
            description=f"Updated answer draft for: '{q.question_text[:40]}...'",
        )
        evaluate_application_readiness(application, save=True)
        messages.success(request, "Question response updated.")
    else:
        messages.error(request, "Error saving response draft.")

    return redirect("applications:detail", pk=pk)


@login_required
@require_POST
def application_question_delete_view(request, pk, q_id):
    """Deletes a question from the workspace."""
    profile = getattr(request.user, "profile", None)
    application = get_object_or_404(Application, pk=pk, profile=profile)
    question = get_object_or_404(ApplicationQuestion, pk=q_id, application=application)

    question.delete()
    evaluate_application_readiness(application, save=True)
    messages.info(request, "Question removed from workspace.")
    return redirect("applications:detail", pk=pk)


@login_required
@require_POST
def application_note_add_view(request, pk):
    """Adds a research, contact, or interview note to the workspace."""
    profile = getattr(request.user, "profile", None)
    application = get_object_or_404(Application, pk=pk, profile=profile)

    form = ApplicationNoteForm(request.POST)
    if form.is_valid():
        note = form.save(commit=False)
        note.application = application
        note.save()

        ApplicationActivity.objects.create(
            application=application,
            activity_type=ActivityType.NOTE_ADDED,
            description=f"Added note: '{note.title or note.get_category_display()}'.",
        )
        messages.success(request, "Note added to workspace.")
    else:
        messages.error(request, "Failed to save note.")

    return redirect("applications:detail", pk=pk)


@login_required
@require_POST
def application_note_delete_view(request, pk, note_id):
    """Deletes a workspace note."""
    profile = getattr(request.user, "profile", None)
    application = get_object_or_404(Application, pk=pk, profile=profile)
    note = get_object_or_404(ApplicationNote, pk=note_id, application=application)
    note.delete()
    messages.info(request, "Note deleted.")
    return redirect("applications:detail", pk=pk)


@login_required
@require_POST
def application_submit_view(request, pk):
    """Records official application submission."""
    profile = getattr(request.user, "profile", None)
    application = get_object_or_404(Application, pk=pk, profile=profile)

    form = ApplicationSubmissionForm(request.POST, instance=application)
    if form.is_valid():
        record_submission(
            application=application,
            submission_method=form.cleaned_data.get("submission_method", SubmissionMethod.PORTAL),
            confirmation_code=form.cleaned_data.get("submission_confirmation_code", ""),
            submission_notes=form.cleaned_data.get("submission_notes", ""),
        )
        messages.success(request, f"Submission recorded successfully for '{application.display_title}'!")
    else:
        messages.error(request, "Invalid submission details.")

    return redirect("applications:detail", pk=pk)


@login_required
@require_POST
def application_delete_view(request, pk):
    """Deletes or archives an application workspace."""
    profile = getattr(request.user, "profile", None)
    application = get_object_or_404(Application, pk=pk, profile=profile)

    title = application.display_title
    application.delete()
    messages.success(request, f"Application workspace for '{title}' has been deleted.")
    return redirect("applications:index")


# =============================================================================
# MILESTONE 6: AI PREPARATION VIEWS
# =============================================================================

@login_required
def application_ai_prep_view(request, pk):
    """
    Dedicated AI Preparation Studio:
    Provides interactive workspace for generating, reviewing, and versioning
    evidence-grounded cover letters, tailored CVs, and application essays.
    """
    profile = getattr(request.user, "profile", None)
    application = get_object_or_404(
        Application.objects.select_related("opportunity", "opportunity__intelligence", "profile"),
        pk=pk,
        profile=profile,
    )

    summary = AIPreparationService.get_prep_summary(application)
    readiness_report = evaluate_application_readiness(application, save=False)

    context = {
        "application": application,
        "summary": summary,
        "readiness_report": readiness_report,
        "tones": AITone.choices,
        "default_tone": AITone.STAR_METHOD,
    }
    return render(request, "applications/ai_prep.html", context)


@login_required
@require_POST
def application_ai_cover_letter_view(request, pk):
    """Generates an evidence-grounded tailored cover letter."""
    profile = getattr(request.user, "profile", None)
    application = get_object_or_404(Application, pk=pk, profile=profile)

    tone = request.POST.get("tone", "PROFESSIONAL")
    guidance = request.POST.get("custom_guidance", "")

    try:
        res = generate_tailored_cover_letter(
            application,
            tone=tone,
            custom_guidance=guidance,
        )
        messages.success(
            request,
            f"Cover Letter v{res['version_number']} generated successfully! Grounded in {res['grounding_count']} verified profile citations.",
        )
    except Exception as e:
        messages.error(request, f"Failed to generate cover letter: {e}")

    return redirect("applications:ai_prep", pk=pk)


@login_required
@require_POST
def application_ai_tailor_cv_view(request, pk):
    """Generates CV tailoring recommendations and ATS keyword coverage."""
    profile = getattr(request.user, "profile", None)
    application = get_object_or_404(Application, pk=pk, profile=profile)

    try:
        res = generate_cv_tailoring(application, update_cv_document=True)
        ats = res.get("ats_keyword_coverage", {})
        score = ats.get("coverage_score", 0)
        messages.success(
            request,
            f"CV Tailoring generated! ATS Keyword Alignment: {score}%. Tailored resume attached to workspace.",
        )
    except Exception as e:
        messages.error(request, f"Failed to tailor CV: {e}")

    return redirect("applications:ai_prep", pk=pk)


@login_required
@require_POST
def application_ai_answer_question_view(request, pk, q_id):
    """Drafts an essay response for an application question."""
    profile = getattr(request.user, "profile", None)
    application = get_object_or_404(Application, pk=pk, profile=profile)
    question = get_object_or_404(ApplicationQuestion, pk=q_id, application=application)

    tone = request.POST.get("tone", AITone.STAR_METHOD)
    guidance = request.POST.get("additional_guidance", "")

    try:
        res = draft_question_answer(
            question=question,
            tone=tone,
            additional_guidance=guidance,
        )
        messages.success(
            request,
            f"Drafted answer for '{question.question_text[:30]}...' ({res['word_count']} words, limit respected).",
        )
    except Exception as e:
        messages.error(request, f"Failed to draft answer: {e}")

    return redirect("applications:ai_prep", pk=pk)


@login_required
@require_POST
def application_ai_prep_all_view(request, pk):
    """Executes a full AI preparation pass (Cover Letter + CV Tailoring + Question Answers)."""
    profile = getattr(request.user, "profile", None)
    application = get_object_or_404(Application, pk=pk, profile=profile)

    tone = request.POST.get("tone", AITone.STAR_METHOD)

    try:
        res = AIPreparationService.prepare_full_application(application, tone=tone)
        messages.success(
            request,
            f"Full AI Preparation pass completed! Readiness score increased to {res['final_readiness_score']}%.",
        )
    except Exception as e:
        messages.error(request, f"Full preparation pass encountered an issue: {e}")

    return redirect("applications:ai_prep", pk=pk)


@login_required
@require_POST
def application_ai_apply_draft_view(request, pk):
    """Restores an earlier version of a document or question draft."""
    profile = getattr(request.user, "profile", None)
    application = get_object_or_404(Application, pk=pk, profile=profile)

    version_type = request.POST.get("version_type")
    version_id = request.POST.get("version_id")

    if version_type == "document":
        version = get_object_or_404(
            ApplicationDocumentVersion,
            pk=version_id,
            application_document__application=application,
        )
        AIPreparationService.apply_document_version(version)
        messages.success(request, f"Restored Draft v{version.version_number} for '{version.application_document.title}'.")
    elif version_type == "question":
        version = get_object_or_404(
            QuestionDraftVersion,
            pk=version_id,
            question__application=application,
        )
        AIPreparationService.apply_question_version(version)
        messages.success(request, f"Restored draft v{version.version_number} for question.")
    else:
        messages.error(request, "Invalid version type.")

    return redirect("applications:ai_prep", pk=pk)

