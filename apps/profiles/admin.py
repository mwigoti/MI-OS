"""
MwohaOS Profiles Admin Registration — Milestone 1
"""
from django.contrib import admin
from .models import (
    Achievement,
    Certification,
    Education,
    Evidence,
    Experience,
    Language,
    Profile,
    ProfilePreference,
    ProfileVersion,
    Project,
    Publication,
    Skill,
)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "headline", "location", "country", "remote_preference", "availability", "created_at"]
    search_fields = ["user__username", "user__email", "headline", "professional_summary", "location"]
    list_filter = ["remote_preference", "availability", "country"]


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ["name", "profile", "category", "proficiency", "years_experience"]
    search_fields = ["name", "profile__user__username"]
    list_filter = ["category", "proficiency"]


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ["position", "organization", "profile", "employment_type", "start_date", "end_date", "is_current"]
    search_fields = ["position", "organization", "profile__user__username"]
    list_filter = ["employment_type", "is_current"]


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ["degree", "field_of_study", "institution", "profile", "start_date", "end_date", "is_current"]
    search_fields = ["degree", "field_of_study", "institution", "profile__user__username"]
    list_filter = ["is_current"]


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "profile", "role", "is_current", "start_date"]
    search_fields = ["name", "technologies", "profile__user__username"]
    list_filter = ["category", "is_current"]


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ["title", "organization", "profile", "date"]
    search_fields = ["title", "organization", "profile__user__username"]


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ["name", "issuer", "profile", "issue_date", "expiry_date"]
    search_fields = ["name", "issuer", "profile__user__username"]


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ["title", "publication_type", "publisher", "profile", "publication_date"]
    search_fields = ["title", "authors", "doi", "profile__user__username"]
    list_filter = ["publication_type"]


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ["language", "proficiency", "profile"]
    search_fields = ["language", "profile__user__username"]
    list_filter = ["proficiency"]


@admin.register(ProfilePreference)
class ProfilePreferenceAdmin(admin.ModelAdmin):
    list_display = ["profile", "target_countries", "target_regions", "min_compensation"]
    search_fields = ["profile__user__username", "target_countries", "target_regions"]


@admin.register(ProfileVersion)
class ProfileVersionAdmin(admin.ModelAdmin):
    list_display = ["profile", "version", "change_summary", "created_at"]
    search_fields = ["profile__user__username", "change_summary"]


@admin.register(Evidence)
class EvidenceAdmin(admin.ModelAdmin):
    list_display = ["title", "evidence_type", "profile", "verified", "source_url", "document", "created_at"]
    search_fields = ["title", "claim_summary", "profile__user__username"]
    list_filter = ["evidence_type", "verified"]
