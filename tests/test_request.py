"""Tests for shared request infrastructure."""

from unittest.mock import patch

from django.test import RequestFactory

from infrastructure.request import get_client_ip


@patch("infrastructure.request.resolve_client_ip")
def test_client_ip_rejects_invalid_resolved_address(mock_resolve_client_ip):
    """An invalid resolved client address is rejected."""
    mock_resolve_client_ip.return_value = (
        "not-an-ip-address",
        False,
    )
    request = RequestFactory().get("/")

    assert get_client_ip(request) is None


def test_client_ip_uses_remote_address_as_fallback():
    """REMOTE_ADDR is used when no forwarded address is available."""
    request = RequestFactory().get(
        "/",
        REMOTE_ADDR="203.0.113.10",
    )

    assert get_client_ip(request) == "203.0.113.10"


def test_client_ip_prefers_forwarded_address():
    """A forwarded client address takes precedence over REMOTE_ADDR."""
    request = RequestFactory().get(
        "/",
        HTTP_X_FORWARDED_FOR="203.0.113.20",
        REMOTE_ADDR="10.0.0.1",
    )

    assert get_client_ip(request) == "203.0.113.20"


def test_client_ip_uses_rightmost_forwarded_address():
    """Forwarded address resolution uses the rightmost address."""
    request = RequestFactory().get(
        "/",
        HTTP_X_FORWARDED_FOR=(
            "198.51.100.10, 198.51.100.20"
        ),
        REMOTE_ADDR="10.0.0.1",
    )

    assert get_client_ip(request) == "198.51.100.20"


def test_client_ip_normalises_ipv6_address():
    """IPv6 client addresses are returned in canonical form."""
    request = RequestFactory().get(
        "/",
        REMOTE_ADDR="2001:0db8:0000:0000:0000:0000:0000:0001",
    )

    assert get_client_ip(request) == "2001:db8::1"


def test_client_ip_returns_none_for_unusable_address():
    """An unusable client address resolves to None."""
    request = RequestFactory().get(
        "/",
        HTTP_X_FORWARDED_FOR="not-an-ip-address",
        REMOTE_ADDR="also-invalid",
    )

    assert get_client_ip(request) is None
