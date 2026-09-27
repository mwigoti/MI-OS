"""
MwohaOS Matching URL Configuration — Milestone 4
"""
from django.urls import path
from . import views

app_name = "matching"

urlpatterns = [
    # Dashboard: /matching/
    path("", views.matching_dashboard_view, name="index"),
    path("matches/", views.matching_dashboard_view, name="matches"),

    # Match Detail: /matching/<uuid>/
    path("<uuid:pk>/", views.match_detail_view, name="detail"),

    # Rematch Trigger: /matching/rematch/<uuid>/
    path("rematch/<uuid:pk>/", views.rematch_opportunity_view, name="rematch"),
]
