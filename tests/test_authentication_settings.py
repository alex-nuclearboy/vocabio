"""Tests for the project authentication settings."""

from django.conf import settings


def test_login_url_uses_accounts_login_route():
    """The project uses the Vocabio login route for authentication."""
    assert settings.LOGIN_URL == "accounts:login"


def test_login_redirect_url_points_to_public_root():
    """Successful login redirects to the public application root by default."""
    assert settings.LOGIN_REDIRECT_URL == "/"


def test_logout_redirect_url_points_to_public_root():
    """Logout redirects to the public application root."""
    assert settings.LOGOUT_REDIRECT_URL == "/"
