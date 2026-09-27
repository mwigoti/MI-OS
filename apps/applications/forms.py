"""
MwohaOS Applications Forms — Milestone 5: Application Workspace
Forms for managing application metadata, materials, questionnaire drafts, notes, and submissions.
"""
from django import forms
from apps.opportunities.models import Opportunity
from apps.documents.models import Document
from .models import (
    Application,
    ApplicationDocument,
    ApplicationQuestion,
    ApplicationNote,
)
from .constants import (
    ApplicationStatus,
    ApplicationPriority,
    SubmissionMethod,
    DocumentRole,
    DocumentAttachmentStatus,
    QuestionStatus,
    QuestionCategory,
    NoteCategory,
)


class ApplicationCreateForm(forms.ModelForm):
    """Initiates an application workspace for an opportunity."""
    
    class Meta:
        model = Application
        fields = [
            "opportunity",
            "priority",
            "target_submission_date",
            "portal_url",
            "strategy_notes",
        ]
        widgets = {
            "opportunity": forms.Select(attrs={"class": "w-full rounded-md border-slate-300 shadow-sm text-sm"}),
            "priority": forms.Select(attrs={"class": "w-full rounded-md border-slate-300 shadow-sm text-sm"}),
            "target_submission_date": forms.DateInput(attrs={"type": "date", "class": "w-full rounded-md border-slate-300 shadow-sm text-sm"}),
            "portal_url": forms.URLInput(attrs={"class": "w-full rounded-md border-slate-300 shadow-sm text-sm", "placeholder": "https://..."}),
            "strategy_notes": forms.Textarea(attrs={"rows": 3, "class": "w-full rounded-md border-slate-300 shadow-sm text-sm", "placeholder": "Positioning, unique angle, or strategy notes..."}),
        }

    def __init__(self, *args, profile=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.profile = profile
        if profile:
            # Filter opportunities that the profile hasn't already created an application for
            existing_opp_ids = Application.objects.filter(profile=profile).values_list("opportunity_id", flat=True)
            self.fields["opportunity"].queryset = Opportunity.objects.exclude(id__in=existing_opp_ids).order_by("-created_at")


class ApplicationUpdateForm(forms.ModelForm):
    """Updates application settings, deadlines, and strategy."""

    class Meta:
        model = Application
        fields = [
            "status",
            "priority",
            "custom_title",
            "custom_organization",
            "target_submission_date",
            "portal_url",
            "strategy_notes",
            "user_review_notes",
        ]
        widgets = {
            "status": forms.Select(attrs={"class": "w-full rounded-md border-slate-300 shadow-sm text-sm"}),
            "priority": forms.Select(attrs={"class": "w-full rounded-md border-slate-300 shadow-sm text-sm"}),
            "custom_title": forms.TextInput(attrs={"class": "w-full rounded-md border-slate-300 shadow-sm text-sm"}),
            "custom_organization": forms.TextInput(attrs={"class": "w-full rounded-md border-slate-300 shadow-sm text-sm"}),
            "target_submission_date": forms.DateInput(attrs={"type": "date", "class": "w-full rounded-md border-slate-300 shadow-sm text-sm"}),
            "portal_url": forms.URLInput(attrs={"class": "w-full rounded-md border-slate-300 shadow-sm text-sm"}),
            "strategy_notes": forms.Textarea(attrs={"rows": 4, "class": "w-full rounded-md border-slate-300 shadow-sm text-sm"}),
            "user_review_notes": forms.Textarea(attrs={"rows": 2, "class": "w-full rounded-md border-slate-300 shadow-sm text-sm"}),
        }


class ApplicationDocumentForm(forms.ModelForm):
    """Attaches a document from the vault or uploads an application-tailored file."""

    class Meta:
        model = ApplicationDocument
        fields = [
            "document_role",
            "title",
            "document",
            "file",
            "is_required",
            "is_tailored",
            "tailored_notes",
            "status",
        ]
        widgets = {
            "document_role": forms.Select(attrs={"class": "w-full rounded-md border-slate-300 shadow-sm text-sm"}),
            "title": forms.TextInput(attrs={"class": "w-full rounded-md border-slate-300 shadow-sm text-sm", "placeholder": "e.g. 2-Page Tailored CV"}),
            "document": forms.Select(attrs={"class": "w-full rounded-md border-slate-300 shadow-sm text-sm"}),
            "file": forms.FileInput(attrs={"class": "w-full text-xs text-slate-500"}),
            "is_required": forms.CheckboxInput(attrs={"class": "rounded text-blue-600 focus:ring-blue-500"}),
            "is_tailored": forms.CheckboxInput(attrs={"class": "rounded text-blue-600 focus:ring-blue-500"}),
            "tailored_notes": forms.Textarea(attrs={"rows": 2, "class": "w-full rounded-md border-slate-300 shadow-sm text-sm", "placeholder": "How was this tailored for this role?"}),
            "status": forms.Select(attrs={"class": "w-full rounded-md border-slate-300 shadow-sm text-sm"}),
        }

    def __init__(self, *args, profile=None, **kwargs):
        super().__init__(*args, **kwargs)
        if profile:
            self.fields["document"].queryset = Document.objects.filter(profile=profile)
            self.fields["document"].empty_label = "-- Or select from your Document Vault --"


class ApplicationQuestionForm(forms.ModelForm):
    """Adds or edits an application question prompt and answer draft."""

    class Meta:
        model = ApplicationQuestion
        fields = [
            "question_text",
            "category",
            "is_required",
            "max_words",
            "max_characters",
            "answer_draft",
            "status",
        ]
        widgets = {
            "question_text": forms.Textarea(attrs={"rows": 2, "class": "w-full rounded-md border-slate-300 shadow-sm text-sm", "placeholder": "The question or prompt as written on the application..."}),
            "category": forms.Select(attrs={"class": "w-full rounded-md border-slate-300 shadow-sm text-sm"}),
            "is_required": forms.CheckboxInput(attrs={"class": "rounded text-blue-600 focus:ring-blue-500"}),
            "max_words": forms.NumberInput(attrs={"class": "w-full rounded-md border-slate-300 shadow-sm text-sm", "placeholder": "e.g. 300"}),
            "max_characters": forms.NumberInput(attrs={"class": "w-full rounded-md border-slate-300 shadow-sm text-sm", "placeholder": "e.g. 2000"}),
            "answer_draft": forms.Textarea(attrs={"rows": 6, "class": "w-full rounded-md border-slate-300 shadow-sm text-sm", "placeholder": "Draft your response here..."}),
            "status": forms.Select(attrs={"class": "w-full rounded-md border-slate-300 shadow-sm text-sm"}),
        }


class ApplicationNoteForm(forms.ModelForm):
    """Creates a workspace note, research finding, or contact log."""

    class Meta:
        model = ApplicationNote
        fields = ["title", "category", "content", "is_pinned"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "w-full rounded-md border-slate-300 shadow-sm text-sm", "placeholder": "Note title / subject"}),
            "category": forms.Select(attrs={"class": "w-full rounded-md border-slate-300 shadow-sm text-sm"}),
            "content": forms.Textarea(attrs={"rows": 3, "class": "w-full rounded-md border-slate-300 shadow-sm text-sm", "placeholder": "Write notes, contacts, interview prep details..."}),
            "is_pinned": forms.CheckboxInput(attrs={"class": "rounded text-blue-600 focus:ring-blue-500"}),
        }


class ApplicationSubmissionForm(forms.ModelForm):
    """Records official submission verification for an application."""

    class Meta:
        model = Application
        fields = [
            "submission_method",
            "submission_confirmation_code",
            "submission_notes",
        ]
        widgets = {
            "submission_method": forms.Select(attrs={"class": "w-full rounded-md border-slate-300 shadow-sm text-sm"}),
            "submission_confirmation_code": forms.TextInput(attrs={"class": "w-full rounded-md border-slate-300 shadow-sm text-sm", "placeholder": "e.g. APP-948190 or Confirmation Email ID"}),
            "submission_notes": forms.Textarea(attrs={"rows": 3, "class": "w-full rounded-md border-slate-300 shadow-sm text-sm", "placeholder": "Submission receipt notes, follow-up timeline, or portal message..."}),
        }
