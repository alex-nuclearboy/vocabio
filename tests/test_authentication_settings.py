"""Tests for the project authentication settings."""

from datetime import timedelta

from django.conf import settings


def test_login_url_uses_accounts_login_route():
    """The project uses the Vocabio login route for authentication."""
    assert settings.LOGIN_URL == "accounts:login"


def test_login_redirect_url_uses_core_home_route():
    """Successful login redirects to the public Vocabio home route."""
    assert settings.LOGIN_REDIRECT_URL == "core:home"


def test_logout_redirect_url_uses_core_home_route():
    """Logout redirects to the public Vocabio home route."""
    assert settings.LOGOUT_REDIRECT_URL == "core:home"


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


def test_client_ip_policy_prefers_forwarded_address():
    """Client IP resolution prefers forwarded addresses."""
    assert settings.CLIENT_IP_META_PRECEDENCE_ORDER == (
        "HTTP_X_FORWARDED_FOR",
        "REMOTE_ADDR",
    )


def test_client_ip_policy_uses_rightmost_forwarded_address():
    """Client IP resolution uses the rightmost forwarded address."""
    assert settings.CLIENT_IP_PROXY_ORDER == "right-most"


def test_axes_uses_shared_client_ip_policy():
    """Axes uses the project-wide client IP resolution policy."""
    assert (
        settings.AXES_IPWARE_META_PRECEDENCE_ORDER
        == settings.CLIENT_IP_META_PRECEDENCE_ORDER
    )
    assert (
        settings.AXES_IPWARE_PROXY_ORDER
        == settings.CLIENT_IP_PROXY_ORDER
    )
