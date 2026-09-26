from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = "core"

urlpatterns = [
    # Root redirects to Dashboard
    path("", RedirectView.as_view(pattern_name="core:dashboard", permanent=False), name="root"),

    # Protected User Dashboard
    path("dashboard/", views.dashboard_view, name="dashboard"),

    # Health Checks (Section 8)
    path("health/", views.health_check, name="health"),
    path("health/database/", views.database_health_check, name="health_database"),
    path("health/redis/", views.redis_health_check, name="health_redis"),
]
