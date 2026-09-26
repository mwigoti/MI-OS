"""
MwohaOS Documents Admin Registration — Milestone 1
"""
from django.contrib import admin
from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ["title", "document_type", "profile", "version", "is_primary", "created_at"]
    search_fields = ["title", "description", "profile__user__username"]
    list_filter = ["document_type", "is_primary"]
