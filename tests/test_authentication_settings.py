"""Tests for the project authentication settings."""

from django.conf import settings


def test_login_url_uses_accounts_login_route():
    """The project uses the Vocabio login route for authentication."""
    assert settings.LOGIN_URL == "accounts:login"


def test_login_redirect_url_points_to_application_root():
    """Successful login uses the application root as the temporary default."""
    assert settings.LOGIN_REDIRECT_URL == "/"


def test_logout_redirect_url_points_to_application_root():
    """Logout uses the application root as the temporary default."""
    assert settings.LOGOUT_REDIRECT_URL == "/"
