"""Tests for authentication lockout behaviour."""

import pytest
from django.test import Client
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_login_is_locked_after_failure_limit(django_user_model):
    """Repeated failed logins lock the username and IP combination."""
    django_user_model.objects.create_user(
        username="editor",
        password="correct-password",
    )

    client = Client()
    login_url = reverse("accounts:login")

    for _ in range(2):
        response = client.post(
            login_url,
            {
                "username": "editor",
                "password": "wrong-password",
            },
            secure=True,
            REMOTE_ADDR="192.0.2.10",
        )

        assert response.status_code == 200

    response = client.post(
        login_url,
        {
            "username": "editor",
            "password": "wrong-password",
        },
        secure=True,
        REMOTE_ADDR="192.0.2.10",
    )

    assert response.status_code == 429
    assert "_auth_user_id" not in client.session


def test_successful_login_resets_failed_attempts(django_user_model):
    """Successful authentication resets previous failed login attempts."""
    django_user_model.objects.create_user(
        username="editor",
        password="correct-password",
    )

    login_url = reverse("accounts:login")
    ip_address = "192.0.2.20"

    client = Client()

    for _ in range(2):
        response = client.post(
            login_url,
            {
                "username": "editor",
                "password": "wrong-password",
            },
            secure=True,
            REMOTE_ADDR=ip_address,
        )

        assert response.status_code == 200

    response = client.post(
        login_url,
        {
            "username": "editor",
            "password": "correct-password",
        },
        secure=True,
        REMOTE_ADDR=ip_address,
    )

    assert response.status_code == 302

    new_client = Client()

    for _ in range(2):
        response = new_client.post(
            login_url,
            {
                "username": "editor",
                "password": "wrong-password",
            },
            secure=True,
            REMOTE_ADDR=ip_address,
        )

        assert response.status_code == 200

    response = new_client.post(
        login_url,
        {
            "username": "editor",
            "password": "wrong-password",
        },
        secure=True,
        REMOTE_ADDR=ip_address,
    )

    assert response.status_code == 429


def test_lockout_is_isolated_by_ip_address(django_user_model):
    """A lockout for one IP address does not block another IP."""
    django_user_model.objects.create_user(
        username="editor",
        password="correct-password",
    )

    login_url = reverse("accounts:login")

    blocked_client = Client()

    for attempt in range(3):
        response = blocked_client.post(
            login_url,
            {
                "username": "editor",
                "password": "wrong-password",
            },
            secure=True,
            REMOTE_ADDR="192.0.2.30",
        )

        expected_status = 429 if attempt == 2 else 200
        assert response.status_code == expected_status

    other_client = Client()

    response = other_client.post(
        login_url,
        {
            "username": "editor",
            "password": "wrong-password",
        },
        secure=True,
        REMOTE_ADDR="192.0.2.31",
    )

    assert response.status_code == 200


def test_lockout_uses_rightmost_forwarded_ip(django_user_model):
    """Lockout uses the rightmost IP from X-Forwarded-For."""
    django_user_model.objects.create_user(
        username="editor",
        password="correct-password",
    )

    login_url = reverse("accounts:login")
    first_forwarded_for = "198.51.100.10, 203.0.113.40"

    first_client = Client()

    for attempt in range(3):
        response = first_client.post(
            login_url,
            {
                "username": "editor",
                "password": "wrong-password",
            },
            secure=True,
            HTTP_X_FORWARDED_FOR=first_forwarded_for,
            REMOTE_ADDR="127.0.0.1",
        )

        expected_status = 429 if attempt == 2 else 200
        assert response.status_code == expected_status

    second_client = Client()

    response = second_client.post(
        login_url,
        {
            "username": "editor",
            "password": "wrong-password",
        },
        secure=True,
        HTTP_X_FORWARDED_FOR="198.51.100.10, 203.0.113.41",
        REMOTE_ADDR="127.0.0.1",
    )

    assert response.status_code == 200


def test_lockout_is_isolated_by_username(django_user_model):
    """A lockout for one username does not block another username."""
    django_user_model.objects.create_user(
        username="editor",
        password="correct-password",
    )
    other_user = django_user_model.objects.create_user(
        username="viewer",
        password="other-password",
    )

    login_url = reverse("accounts:login")
    ip_address = "192.0.2.40"

    blocked_client = Client()

    for attempt in range(3):
        response = blocked_client.post(
            login_url,
            {
                "username": "editor",
                "password": "wrong-password",
            },
            secure=True,
            REMOTE_ADDR=ip_address,
        )

        expected_status = 429 if attempt == 2 else 200
        assert response.status_code == expected_status

    other_client = Client()

    response = other_client.post(
        login_url,
        {
            "username": "viewer",
            "password": "other-password",
        },
        secure=True,
        REMOTE_ADDR=ip_address,
    )

    assert response.status_code == 302
    assert other_client.session["_auth_user_id"] == str(other_user.pk)


def test_admin_login_is_protected_by_lockout(django_user_model):
    """Django Admin login is protected by the same lockout policy."""
    django_user_model.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="correct-password",
    )

    client = Client()
    login_url = reverse("admin:login")
    ip_address = "192.0.2.60"

    for attempt in range(3):
        response = client.post(
            login_url,
            {
                "username": "admin",
                "password": "wrong-password",
            },
            secure=True,
            REMOTE_ADDR=ip_address,
        )

        expected_status = 429 if attempt == 2 else 200
        assert response.status_code == expected_status

    response = client.post(
        login_url,
        {
            "username": "admin",
            "password": "correct-password",
        },
        secure=True,
        REMOTE_ADDR=ip_address,
    )

    assert response.status_code == 429
    assert "_auth_user_id" not in client.session
