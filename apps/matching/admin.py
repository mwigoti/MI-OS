"""
MwohaOS Matching Admin Registration — Milestone 4
"""
from django.contrib import admin
from .models import OpportunityMatch


@admin.register(OpportunityMatch)
class OpportunityMatchAdmin(admin.ModelAdmin):
    list_display = [
        "opportunity",
        "profile",
        "overall_score",
        "eligibility_status",
        "match_status",
        "skill_score",
        "experience_score",
        "matching_version",
        "last_matched_at",
    ]
    list_filter = [
        "eligibility_status",
        "match_status",
        "matching_version",
        "ai_used",
    ]
    search_fields = [
        "opportunity__title",
        "opportunity__organization",
        "profile__user__username",
        "profile__user__email",
        "explanation",
    ]
    readonly_fields = [
        "id",
        "profile_snapshot_hash",
        "opportunity_snapshot_hash",
        "intelligence_snapshot_hash",
        "created_at",
        "updated_at",
        "last_matched_at",
    ]
    ordering = ["-overall_score", "-last_matched_at"]
