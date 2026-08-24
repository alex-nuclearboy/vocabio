"""Tests for the project authentication settings."""

from datetime import timedelta

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


def test_authentication_backends_include_axes_first():
    """Axes checks lockouts before Django authenticates credentials."""
    assert settings.AUTHENTICATION_BACKENDS == [
        "axes.backends.AxesStandaloneBackend",
        "django.contrib.auth.backends.ModelBackend",
    ]


def test_axes_failure_limit_is_three_attempts():
    """Authentication is locked after three failed attempts."""
    assert settings.AXES_FAILURE_LIMIT == 3


def test_axes_cooloff_time_is_fifteen_minutes():
    """Authentication lockouts expire after fifteen minutes."""
    assert settings.AXES_COOLOFF_TIME == timedelta(minutes=15)


def test_axes_resets_failures_after_successful_login():
    """Successful authentication resets accumulated failed attempts."""
    assert settings.AXES_RESET_ON_SUCCESS is True


def test_axes_does_not_extend_cooloff_during_lockout():
    """Failed attempts during lockout do not extend the cool-off period."""
    assert (
        settings.AXES_RESET_COOL_OFF_ON_FAILURE_DURING_LOCKOUT
        is False
    )


def test_axes_lockout_uses_username_and_ip_address():
    """Lockouts are scoped to the username and IP address combination."""
    assert settings.AXES_LOCKOUT_PARAMETERS == [
        ["username", "ip_address"],
    ]


def test_axes_ipware_uses_forwarded_ip_with_remote_fallback():
    """IP resolution prefers forwarded addresses with REMOTE_ADDR fallback."""
    assert settings.AXES_IPWARE_META_PRECEDENCE_ORDER == (
        "HTTP_X_FORWARDED_FOR",
        "REMOTE_ADDR",
    )


def test_axes_ipware_uses_rightmost_proxy_address():
    """Forwarded address resolution uses the rightmost trusted address."""
    assert settings.AXES_IPWARE_PROXY_ORDER == "right-most"
