"""
MwohaOS Profiles URL Patterns — Milestone 1
"""
from django.urls import path
from . import views

app_name = "profiles"

urlpatterns = [
    # Overview
    path("", views.profile_overview, name="overview"),
    path("index/", views.profile_overview, name="index"),
    path("edit/", views.profile_edit, name="edit"),

    # Skills CRUD
    path("skills/", views.skill_list, name="skill_list"),
    path("skills/add/", views.skill_create, name="skill_create"),
    path("skills/<int:pk>/edit/", views.skill_edit, name="skill_edit"),
    path("skills/<int:pk>/delete/", views.skill_delete, name="skill_delete"),

    # Experience CRUD
    path("experience/", views.experience_list, name="experience_list"),
    path("experience/add/", views.experience_create, name="experience_create"),
    path("experience/<int:pk>/edit/", views.experience_edit, name="experience_edit"),
    path("experience/<int:pk>/delete/", views.experience_delete, name="experience_delete"),

    # Education CRUD
    path("education/", views.education_list, name="education_list"),
    path("education/add/", views.education_create, name="education_create"),
    path("education/<int:pk>/edit/", views.education_edit, name="education_edit"),
    path("education/<int:pk>/delete/", views.education_delete, name="education_delete"),

    # Projects CRUD
    path("projects/", views.project_list, name="project_list"),
    path("projects/add/", views.project_create, name="project_create"),
    path("projects/<int:pk>/edit/", views.project_edit, name="project_edit"),
    path("projects/<int:pk>/delete/", views.project_delete, name="project_delete"),

    # Achievements CRUD
    path("achievements/", views.achievement_list, name="achievement_list"),
    path("achievements/add/", views.achievement_create, name="achievement_create"),
    path("achievements/<int:pk>/edit/", views.achievement_edit, name="achievement_edit"),
    path("achievements/<int:pk>/delete/", views.achievement_delete, name="achievement_delete"),

    # Certifications CRUD
    path("certifications/", views.certification_list, name="certification_list"),
    path("certifications/add/", views.certification_create, name="certification_create"),
    path("certifications/<int:pk>/edit/", views.certification_edit, name="certification_edit"),
    path("certifications/<int:pk>/delete/", views.certification_delete, name="certification_delete"),

    # Publications CRUD
    path("publications/", views.publication_list, name="publication_list"),
    path("publications/add/", views.publication_create, name="publication_create"),
    path("publications/<int:pk>/edit/", views.publication_edit, name="publication_edit"),
    path("publications/<int:pk>/delete/", views.publication_delete, name="publication_delete"),

    # Languages CRUD
    path("languages/", views.language_list, name="language_list"),
    path("languages/add/", views.language_create, name="language_create"),
    path("languages/<int:pk>/edit/", views.language_edit, name="language_edit"),
    path("languages/<int:pk>/delete/", views.language_delete, name="language_delete"),

    # Target Preferences
    path("preferences/", views.preference_view, name="preferences"),

    # Evidence Bank CRUD
    path("evidence/", views.evidence_list, name="evidence_list"),
    path("evidence/add/", views.evidence_create, name="evidence_create"),
    path("evidence/<int:pk>/edit/", views.evidence_edit, name="evidence_edit"),
    path("evidence/<int:pk>/delete/", views.evidence_delete, name="evidence_delete"),
    path("evidence/<int:pk>/toggle-verify/", views.evidence_toggle_verification, name="evidence_toggle_verify"),
]
