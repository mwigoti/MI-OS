"""
MwohaOS Opportunities Admin Registration — Milestone 2
Provides searching, filtering, and readonly audit fields for Opportunity,
OpportunitySource, and IngestionRun.
"""
from django.contrib import admin
from .models import Opportunity, OpportunitySource, IngestionRun, OpportunityIntelligence, AIUsageLog


@admin.register(OpportunityIntelligence)
class OpportunityIntelligenceAdmin(admin.ModelAdmin):
    list_display = [
        "opportunity",
        "extraction_status",
        "extraction_method",
        "extraction_provider",
        "model_name",
        "confidence",
        "updated_at",
    ]
    list_filter = [
        "extraction_status",
        "extraction_method",
        "extraction_provider",
    ]
    search_fields = ["opportunity__title", "opportunity__organization", "summary", "opportunity_purpose"]
    readonly_fields = [
        "id",
        "confidence",
        "raw_extraction",
        "created_at",
        "updated_at",
        "last_extracted_at",
    ]


@admin.register(AIUsageLog)
class AIUsageLogAdmin(admin.ModelAdmin):
    list_display = [
        "provider",
        "model",
        "operation",
        "success",
        "input_tokens",
        "output_tokens",
        "latency_seconds",
        "requested_at",
    ]
    list_filter = ["provider", "success", "operation"]
    search_fields = ["provider", "model", "error_type", "error_message"]
    readonly_fields = [
        "id",
        "provider",
        "model",
        "operation",
        "opportunity",
        "requested_at",
        "completed_at",
        "success",
        "input_tokens",
        "output_tokens",
        "error_type",
        "error_message",
        "latency_seconds",
        "created_at",
        "updated_at",
    ]


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "organization",
        "opportunity_type",
        "sector",
        "country",
        "remote",
        "deadline",
        "status",
        "source",
        "created_at",
    ]
    list_filter = [
        "opportunity_type",
        "sector",
        "status",
        "remote",
        "source",
    ]
    search_fields = ["title", "organization", "description", "preferred_skills"]
    readonly_fields = ["id", "content_hash", "first_seen_at", "last_seen_at", "created_at", "updated_at"]
    ordering = ["-posted_date", "-created_at"]


@admin.register(OpportunitySource)
class OpportunitySourceAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "source_type", "enabled", "last_run", "last_success"]
    list_filter = ["source_type", "enabled"]
    search_fields = ["name", "slug", "base_url"]
    readonly_fields = ["id", "last_run", "last_success", "last_error", "created_at", "updated_at"]


@admin.register(IngestionRun)
class IngestionRunAdmin(admin.ModelAdmin):
    list_display = [
        "source",
        "status",
        "items_fetched",
        "items_parsed",
        "items_created",
        "items_updated",
        "items_failed",
        "started_at",
        "duration_seconds",
    ]
    list_filter = ["status", "source"]
    readonly_fields = [
        "id",
        "source",
        "status",
        "started_at",
        "completed_at",
        "items_fetched",
        "items_parsed",
        "items_created",
        "items_updated",
        "items_skipped",
        "items_failed",
        "error_message",
        "created_at",
        "updated_at",
    ]
    ordering = ["-started_at"]
