"""
MwohaOS Authentication Test Suite
Verifies login, logout, protected routes, and session management.
"""
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestAuthentication:
    def test_login_works(self, client, test_user, test_password):
        """Valid credentials log the user in and redirect to dashboard."""
        login_url = reverse("accounts:login")
        response = client.post(login_url, {
            "username": test_user.username,
            "password": test_password,
        })
        assert response.status_code in [302, 200]
        # Redirects to dashboard
        assert response.url == reverse("core:dashboard")

    def test_invalid_login_rejected(self, client, test_user):
        """Invalid credentials keep user on login page with error."""
        login_url = reverse("accounts:login")
        response = client.post(login_url, {
            "username": test_user.username,
            "password": "wrong-password",
        })
        assert response.status_code == 200
        assert "_auth_user_id" not in client.session

    def test_unauthenticated_users_cannot_access_dashboard(self, client):
        """Anonymous access to /dashboard/ redirects to login."""
        dashboard_url = reverse("core:dashboard")
        response = client.get(dashboard_url)
        assert response.status_code == 302
        assert reverse("accounts:login") in response.url

    def test_authenticated_user_can_access_dashboard(self, authenticated_client):
        """Authenticated user successfully accesses dashboard."""
        dashboard_url = reverse("core:dashboard")
        response = authenticated_client.get(dashboard_url)
        assert response.status_code == 200
        assert b"MwohaOS" in response.content
        assert b"System Status" in response.content

    def test_logout_works(self, authenticated_client):
        """Logout clears the authenticated session."""
        logout_url = reverse("accounts:logout")
        response = authenticated_client.get(logout_url)
        assert response.status_code == 302
        assert reverse("accounts:login") in response.url
        assert "_auth_user_id" not in authenticated_client.session

    def test_registration_creates_user_and_logs_in(self, client):
        """Registration view creates new user and redirects to dashboard."""
        register_url = reverse("accounts:register")
        response = client.post(register_url, {
            "username": "new_candidate",
            "email": "candidate@example.org",
            "password1": "SecureCandidate2026!",
            "password2": "SecureCandidate2026!",
        })
        assert response.status_code == 302
        assert response.url == reverse("core:dashboard")
        assert User.objects.filter(username="new_candidate").exists()
