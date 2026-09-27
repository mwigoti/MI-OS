"""
MwohaOS Root URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.accounts.views import settings_view

urlpatterns = [
    # Admin Interface
    path("admin/", admin.site.urls),

    # Core & Health Checks
    path("", include("apps.core.urls", namespace="core")),

    # Settings Page (Section 19: /settings/)
    path("settings/", settings_view, name="settings"),

    # Accounts & Authentication
    path("accounts/", include("apps.accounts.urls", namespace="accounts")),

    # Profiles (Milestone 1 — Professional Profile & Evidence)
    path("profile/", include("apps.profiles.urls", namespace="profiles")),

    # Documents (Milestone 1 — Document Vault & Management)
    path("documents/", include("apps.documents.urls", namespace="documents")),

    # Opportunities (Milestone 2 & Milestone 3)
    path("opportunities/", include("apps.opportunities.urls", namespace="opportunities")),

    # Matching & Recommendations (Milestone 4)
    path("matching/", include("apps.matching.urls", namespace="matching")),

    # Applications (Foundation for Milestone 5)
    path("applications/", include("apps.applications.urls", namespace="applications")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom Error Handlers (Section 16)
handler400 = "apps.core.views.bad_request"
handler403 = "apps.core.views.permission_denied"
handler404 = "apps.core.views.page_not_found"
handler500 = "apps.core.views.server_error"
