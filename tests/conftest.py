"""
Pytest configuration and fixtures for MwohaOS.
"""
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Enables database access for all pytest fixtures."""
    pass


@pytest.fixture
def test_password():
    return "MwohaOS_Secure_Pass123!"


@pytest.fixture
def test_user(test_password):
    """Creates a standard test user."""
    return User.objects.create_user(
        username="mwoha_test_user",
        email="test@mwohaos.local",
        password=test_password,
    )


@pytest.fixture
def authenticated_client(client, test_user, test_password):
    """Test client logged in as test_user."""
    client.login(username=test_user.username, password=test_password)
    return client


@pytest.fixture(autouse=True)
def celery_eager_mode(settings):
    """Executes Celery tasks synchronously in test runs."""
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True
