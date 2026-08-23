"""Tests for the accounts URL configuration."""

from django.urls import resolve, reverse


def test_login_url():
    """The login route uses the public /login/ path."""
    url = reverse("accounts:login")

    assert url == "/login/"
    assert resolve(url).view_name == "accounts:login"


def test_logout_url():
    """The logout route uses the public /logout/ path."""
    url = reverse("accounts:logout")

    assert url == "/logout/"
    assert resolve(url).view_name == "accounts:logout"
