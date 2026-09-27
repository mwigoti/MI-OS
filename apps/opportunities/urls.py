"""
MwohaOS Opportunities URL Configuration — Milestone 2
"""
from django.urls import path
from . import views

app_name = "opportunities"

urlpatterns = [
    # Opportunity Inbox (List, Filters, Search)
    path("", views.opportunity_inbox_view, name="index"),
    path("inbox/", views.opportunity_inbox_view, name="inbox"),

    # Manual URL Ingestion
    path("add/", views.opportunity_manual_add_view, name="add"),

    # Opportunity Detail & Analysis
    path("<uuid:pk>/", views.opportunity_detail_view, name="detail"),
    path("<uuid:pk>/analyze/", views.opportunity_analyze_view, name="analyze"),

    # Source Management
    path("sources/", views.sources_dashboard_view, name="sources"),
    path("sources/<uuid:pk>/toggle/", views.source_toggle_view, name="source_toggle"),
    path("sources/<uuid:pk>/run/", views.source_trigger_view, name="source_run"),
]
