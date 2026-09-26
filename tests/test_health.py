"""
MwohaOS Health Checks Test Suite
Verifies application, database, and Redis health check probes (Section 8).
"""
import pytest
from unittest.mock import patch, MagicMock
from django.urls import reverse


@pytest.mark.django_db
class TestHealthChecks:
    def test_application_health_check(self, client):
        """GET /health/ returns status: ok."""
        url = reverse("core:health")
        response = client.get(url)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["app"] == "MwohaOS"
        assert "version" in data
        assert "timestamp" in data

    def test_database_health_check_success(self, client):
        """GET /health/database/ executes query and returns 200."""
        url = reverse("core:health_database")
        response = client.get(url)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "database"
        assert data["connected"] is True

    def test_database_health_check_failure(self, client):
        """GET /health/database/ returns 503 when connection fails."""
        with patch("django.db.connection.cursor", side_effect=Exception("DB connection refused")):
            url = reverse("core:health_database")
            response = client.get(url)
            assert response.status_code == 503
            data = response.json()
            assert data["status"] == "error"
            assert data["service"] == "database"

    def test_redis_health_check_success(self, client):
        """GET /health/redis/ returns 200 when redis ping succeeds."""
        mock_redis = MagicMock()
        mock_redis.ping.return_value = True

        with patch("redis.from_url", return_value=mock_redis):
            url = reverse("core:health_redis")
            response = client.get(url)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ok"
            assert data["service"] == "redis"
            assert data["connected"] is True

    def test_redis_health_check_failure(self, client):
        """GET /health/redis/ returns 503 when redis connection fails."""
        mock_redis = MagicMock()
        mock_redis.ping.side_effect = Exception("Connection refused")

        with patch("redis.from_url", return_value=mock_redis):
            url = reverse("core:health_redis")
            response = client.get(url)
            assert response.status_code == 503
            data = response.json()
            assert data["status"] == "error"
            assert data["service"] == "redis"
