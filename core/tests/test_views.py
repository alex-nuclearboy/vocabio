"""Tests for project-level Vocabio views."""

from unittest.mock import patch

import pytest
from django.db import OperationalError
from django.urls import reverse

from tests.assertions import assert_response_is_not_cached


def test_home_page_is_available(client):
    """The public home page responds successfully."""
    response = client.get(
        reverse("core:home"),
        secure=True,
    )

    assert response.status_code == 200
    assert response.content == b"Vocabio"


def test_home_page_rejects_post(client):
    """The public home page accepts GET requests only."""
    response = client.post(
        reverse("core:home"),
        secure=True,
    )

    assert response.status_code == 405


def test_liveness_reports_healthy_process(client):
    """The liveness endpoint reports a responding application."""
    response = client.get(
        reverse("core:health-live"),
        secure=True,
    )

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_liveness_accepts_forwarded_https(client, settings):
    """The liveness endpoint accepts trusted forwarded HTTPS requests."""
    settings.SECURE_SSL_REDIRECT = True
    settings.SECURE_PROXY_SSL_HEADER = (
        "HTTP_X_FORWARDED_PROTO",
        "https",
    )

    response = client.get(
        reverse("core:health-live"),
        HTTP_X_FORWARDED_PROTO="https",
    )

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_liveness_is_not_cached(client):
    """The liveness response prevents intermediary caching."""
    response = client.get(
        reverse("core:health-live"),
        secure=True,
    )

    assert_response_is_not_cached(response)


def test_liveness_rejects_post(client):
    """The liveness endpoint accepts GET requests only."""
    response = client.post(
        reverse("core:health-live"),
        secure=True,
    )

    assert response.status_code == 405


@pytest.mark.django_db
def test_readiness_reports_available_database(client):
    """The readiness endpoint reports an available database."""
    response = client.get(
        reverse("core:health-ready"),
        secure=True,
    )

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@patch("core.views.health.connection.cursor")
def test_readiness_reports_unavailable_database(
    mock_cursor,
    client,
):
    """The readiness endpoint returns 503 when the database is unavailable."""
    mock_cursor.side_effect = OperationalError(
        "database unavailable"
    )

    response = client.get(
        reverse("core:health-ready"),
        secure=True,
    )

    assert response.status_code == 503
    assert response.json() == {
        "status": "unavailable",
    }


@patch("core.views.health.connection.cursor")
def test_readiness_rejects_unexpected_database_result(
    mock_cursor,
    client,
):
    """The readiness endpoint returns 503 for an unexpected database result."""
    cursor = mock_cursor.return_value.__enter__.return_value
    cursor.fetchone.return_value = None

    response = client.get(
        reverse("core:health-ready"),
        secure=True,
    )

    assert response.status_code == 503
    assert response.json() == {
        "status": "unavailable",
    }
    cursor.execute.assert_called_once_with("SELECT 1")
    cursor.fetchone.assert_called_once_with()


@patch("core.views.health.connection.cursor")
def test_readiness_accepts_expected_database_result(
    mock_cursor,
    client,
):
    """The readiness endpoint accepts the expected database probe result."""
    cursor = mock_cursor.return_value.__enter__.return_value
    cursor.fetchone.return_value = (1,)

    response = client.get(
        reverse("core:health-ready"),
        secure=True,
    )

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    cursor.execute.assert_called_once_with("SELECT 1")
    cursor.fetchone.assert_called_once_with()


@pytest.mark.django_db
def test_readiness_is_not_cached(client):
    """The readiness response prevents intermediary caching."""
    response = client.get(
        reverse("core:health-ready"),
        secure=True,
    )

    assert_response_is_not_cached(response)


def test_readiness_rejects_post(client):
    """The readiness endpoint accepts GET requests only."""
    response = client.post(
        reverse("core:health-ready"),
        secure=True,
    )

    assert response.status_code == 405
