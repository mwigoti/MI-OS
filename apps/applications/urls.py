"""
MwohaOS Applications URL Configuration — Milestone 5: Application Workspace
"""
from django.urls import path
from . import views

app_name = "applications"

urlpatterns = [
    # Dashboard & Workspace Detail
    path("", views.application_list_view, name="index"),
    path("create/", views.application_create_view, name="create"),
    path("<uuid:pk>/", views.application_detail_view, name="detail"),
    path("<uuid:pk>/update/", views.application_update_view, name="update"),
    path("<uuid:pk>/status/", views.application_status_update_view, name="update_status"),
    path("<uuid:pk>/signoff/", views.application_signoff_view, name="signoff"),
    path("<uuid:pk>/submit/", views.application_submit_view, name="record_submission"),
    path("<uuid:pk>/delete/", views.application_delete_view, name="delete"),

    # Documents Management
    path("<uuid:pk>/documents/add/", views.application_document_add_view, name="document_add"),
    path("<uuid:pk>/documents/<uuid:doc_id>/delete/", views.application_document_delete_view, name="document_delete"),

    # Questions & Answer Drafts Management
    path("<uuid:pk>/questions/add/", views.application_question_add_view, name="question_add"),
    path("<uuid:pk>/questions/<uuid:q_id>/edit/", views.application_question_edit_view, name="question_edit"),
    path("<uuid:pk>/questions/<uuid:q_id>/delete/", views.application_question_delete_view, name="question_delete"),

    # Notes Management
    path("<uuid:pk>/notes/add/", views.application_note_add_view, name="note_add"),
    path("<uuid:pk>/notes/<uuid:note_id>/delete/", views.application_note_delete_view, name="note_delete"),

    # Milestone 6: AI Preparation Studio & Action Endpoints
    path("<uuid:pk>/ai-prep/", views.application_ai_prep_view, name="ai_prep"),
    path("<uuid:pk>/ai-prep/all/", views.application_ai_prep_all_view, name="ai_prep_all"),
    path("<uuid:pk>/ai-prep/cover-letter/", views.application_ai_cover_letter_view, name="ai_cover_letter"),
    path("<uuid:pk>/ai-prep/tailor-cv/", views.application_ai_tailor_cv_view, name="ai_tailor_cv"),
    path("<uuid:pk>/ai-prep/questions/<uuid:q_id>/answer/", views.application_ai_answer_question_view, name="ai_answer_question"),
    path("<uuid:pk>/ai-prep/apply-draft/", views.application_ai_apply_draft_view, name="ai_apply_draft"),
]
