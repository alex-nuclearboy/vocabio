"""Tests for the core application URL configuration."""

from django.urls import resolve, reverse


def test_home_url():
    """The home route uses the public application root."""
    url = reverse("core:home")

    assert url == "/"
    assert resolve(url).view_name == "core:home"


def test_liveness_url():
    """The liveness route uses the expected public path."""
    url = reverse("core:health-live")

    assert url == "/health/live/"
    assert resolve(url).view_name == "core:health-live"


def test_readiness_url():
    """The readiness route uses the expected public path."""
    url = reverse("core:health-ready")

    assert url == "/health/ready/"
    assert resolve(url).view_name == "core:health-ready"
