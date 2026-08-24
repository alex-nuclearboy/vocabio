"""Tests for authentication audit events."""

from unittest.mock import patch

import pytest
from django.conf import settings
from django.urls import reverse


pytestmark = pytest.mark.django_db


def _create_audit_user(django_user_model):
    """Create a user for authentication audit tests."""
    return django_user_model.objects.create_user(
        username="editor",
        password="test-password",
    )


@patch("accounts.views.audit_logger.info")
def test_successful_login_emits_audit_event(
    mock_audit_info,
    client,
    django_user_model,
):
    """Successful authentication emits a structured audit event."""
    user = _create_audit_user(django_user_model)

    response = client.post(
        reverse("accounts:login"),
        {
            "username": user.username,
            "password": "test-password",
        },
        REMOTE_ADDR="203.0.113.10",
        secure=True,
    )

    assert response.status_code == 302
    mock_audit_info.assert_called_once_with(
        (
            f'[AUTH|LOGIN] user_id={user.pk} '
            'client_ip="203.0.113.10"'
        )
    )


@patch("accounts.views.audit_logger.info")
def test_logout_emits_audit_event(
    mock_audit_info,
    client,
    django_user_model,
):
    """Logout emits a structured audit event."""
    user = _create_audit_user(django_user_model)
    client.force_login(user)

    response = client.post(
        reverse("accounts:logout"),
        REMOTE_ADDR="203.0.113.10",
        secure=True,
    )

    assert response.status_code == 302
    mock_audit_info.assert_called_once_with(
        (
            f'[AUTH|LOGOUT] user_id={user.pk} '
            'client_ip="203.0.113.10"'
        )
    )


@patch("accounts.views.audit_logger.info")
def test_anonymous_logout_does_not_emit_audit_event(
    mock_audit_info,
    client,
):
    """Anonymous logout attempts do not emit logout audit events."""
    response = client.post(
        reverse("accounts:logout"),
        secure=True,
    )

    assert response.status_code == 302
    mock_audit_info.assert_not_called()


@patch("accounts.security.audit_logger.warning")
def test_lockout_emits_audit_event(
    mock_audit_warning,
    client,
    django_user_model,
):
    """Authentication lockout emits a structured audit event."""
    user = django_user_model.objects.create_user(
        username="editor",
        password="correct-password",
    )

    credentials = {
        "username": user.username,
        "password": "wrong-password",
    }

    for _ in range(settings.AXES_FAILURE_LIMIT - 1):
        response = client.post(
            reverse("accounts:login"),
            credentials,
            REMOTE_ADDR="203.0.113.10",
            secure=True,
        )

        assert response.status_code == 200

    response = client.post(
        reverse("accounts:login"),
        credentials,
        REMOTE_ADDR="203.0.113.10",
        secure=True,
    )

    assert response.status_code == 429
    mock_audit_warning.assert_called_once_with(
        (
            '[AUTH|LOCKOUT] username="editor" '
            'client_ip="203.0.113.10" '
            'path="/login/"'
        )
    )
