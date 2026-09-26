"""
MwohaOS Security Baseline Test Suite
Verifies CSRF, protected routes, secure headers, and production standards (Sections 14, 27).
"""
import pytest
from django.conf import settings
from django.urls import reverse


class TestSecurityBaseline:
    def test_csrf_middleware_enabled(self):
        """Ensures CsrfViewMiddleware is active in MIDDLEWARE."""
        assert "django.middleware.csrf.CsrfViewMiddleware" in settings.MIDDLEWARE

    def test_security_middleware_enabled(self):
        """Ensures SecurityMiddleware is active in MIDDLEWARE."""
        assert "django.middleware.security.SecurityMiddleware" in settings.MIDDLEWARE

    def test_clickjacking_middleware_enabled(self):
        """Ensures XFrameOptionsMiddleware is active in MIDDLEWARE."""
        assert "django.middleware.clickjacking.XFrameOptionsMiddleware" in settings.MIDDLEWARE

    @pytest.mark.parametrize("route_name", [
        "core:dashboard",
        "accounts:settings",
        "profiles:index",
        "opportunities:index",
        "applications:index",
    ])
    def test_protected_routes_require_authentication(self, client, route_name):
        """Confirms that sensitive routes redirect unauthenticated users to login."""
        url = reverse(route_name)
        response = client.get(url)
        assert response.status_code == 302
        assert reverse("accounts:login") in response.url

    def test_production_settings_security_configuration(self):
        """Validates that production settings declare mandatory security flags."""
        from config.settings import production as prod_settings

        assert prod_settings.DEBUG is False
        assert prod_settings.SECURE_CONTENT_TYPE_NOSNIFF is True
        assert prod_settings.SESSION_COOKIE_HTTPONLY is True
        assert prod_settings.CSRF_COOKIE_HTTPONLY is True
        assert prod_settings.SECURE_HSTS_SECONDS >= 31536000
        assert prod_settings.SECURE_HSTS_INCLUDE_SUBDOMAINS is True
        assert prod_settings.SECURE_HSTS_PRELOAD is True
