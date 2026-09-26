"""
MwohaOS Celery Test Suite
Validates Celery task execution and queue configuration (Section 9).
"""
import pytest
from apps.core.tasks import health_check_task
from config.celery import app as celery_app


class TestCelery:
    def test_health_check_task_executes_directly(self):
        """Validates that the test task executes and returns expected string."""
        result = health_check_task()
        assert result == "MwohaOS Celery task executed successfully."

    def test_health_check_task_executes_via_delay(self):
        """Validates async task execution via Celery delay/apply."""
        async_result = health_check_task.apply()
        assert async_result.successful()
        assert async_result.result == "MwohaOS Celery task executed successfully."

    def test_celery_task_registered(self):
        """Verifies that core.tasks.health_check_task is registered in Celery."""
        assert "core.tasks.health_check_task" in celery_app.tasks
