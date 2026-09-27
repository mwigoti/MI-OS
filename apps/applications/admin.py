"""
MwohaOS Applications Admin — Milestone 5: Application Workspace
"""
from django.contrib import admin
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


class ApplicationDocumentInline(admin.TabularInline):
    model = ApplicationDocument
    extra = 1
    fields = ("title", "document_role", "document", "is_required", "is_tailored", "status")


class ApplicationQuestionInline(admin.StackedInline):
    model = ApplicationQuestion
    extra = 0
    fields = ("question_text", "category", "is_required", "max_words", "answer_draft", "status")


class ApplicationNoteInline(admin.TabularInline):
    model = ApplicationNote
    extra = 0
    fields = ("title", "category", "content", "is_pinned")


class ApplicationActivityInline(admin.TabularInline):
    model = ApplicationActivity
    extra = 0
    readonly_fields = ("activity_type", "from_status", "to_status", "description", "created_at")
    can_delete = False


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "display_title",
        "profile",
        "status",
        "priority",
        "readiness_score",
        "is_ready_to_submit",
        "user_review_completed",
        "target_submission_date",
        "submitted_at",
        "created_at",
    )
    list_filter = (
        "status",
        "priority",
        "is_ready_to_submit",
        "user_review_completed",
        "submission_method",
        "created_at",
    )
    search_fields = (
        "custom_title",
        "custom_organization",
        "opportunity__title",
        "opportunity__organization",
        "profile__user__username",
        "submission_confirmation_code",
    )
    readonly_fields = ("readiness_score", "is_ready_to_submit", "created_at", "updated_at")
    inlines = [
        ApplicationDocumentInline,
        ApplicationQuestionInline,
        ApplicationNoteInline,
        ApplicationActivityInline,
    ]


@admin.register(ApplicationDocument)
class ApplicationDocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "application", "document_role", "is_required", "is_tailored", "status", "created_at")
    list_filter = ("document_role", "is_required", "is_tailored", "status")
    search_fields = ("title", "application__custom_title", "application__opportunity__title")


@admin.register(ApplicationQuestion)
class ApplicationQuestionAdmin(admin.ModelAdmin):
    list_display = ("question_text_short", "application", "category", "is_required", "status", "word_count")
    list_filter = ("category", "is_required", "status")
    search_fields = ("question_text", "answer_draft")

    def question_text_short(self, obj):
        return obj.question_text[:50] + "..." if len(obj.question_text) > 50 else obj.question_text


@admin.register(ApplicationNote)
class ApplicationNoteAdmin(admin.ModelAdmin):
    list_display = ("title", "application", "category", "is_pinned", "created_at")
    list_filter = ("category", "is_pinned", "created_at")
    search_fields = ("title", "content")


@admin.register(ApplicationDocumentVersion)
class ApplicationDocumentVersionAdmin(admin.ModelAdmin):
    list_display = ("application_document", "version_number", "provider", "model", "is_active", "created_at")
    list_filter = ("provider", "is_active", "created_at")
    search_fields = ("application_document__title", "content", "tailoring_notes")


@admin.register(QuestionDraftVersion)
class QuestionDraftVersionAdmin(admin.ModelAdmin):
    list_display = ("question", "version_number", "tone", "word_count", "provider", "is_selected", "created_at")
    list_filter = ("tone", "provider", "is_selected", "created_at")
    search_fields = ("question__question_text", "answer_text")


@admin.register(CVTailoringResult)
class CVTailoringResultAdmin(admin.ModelAdmin):
    list_display = ("application", "provider", "model", "created_at")
    search_fields = ("application__custom_title", "targeted_summary")



@admin.register(ApplicationActivity)
class ApplicationActivityAdmin(admin.ModelAdmin):
    list_display = ("application", "activity_type", "from_status", "to_status", "description", "created_at")
    list_filter = ("activity_type", "created_at")
    readonly_fields = ("application", "activity_type", "from_status", "to_status", "description", "created_at")
