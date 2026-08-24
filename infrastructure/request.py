"""Shared HTTP request helpers for Vocabio."""

from ipaddress import ip_address

from django.conf import settings
from django.http import HttpRequest
from ipware.ip import get_client_ip as resolve_client_ip


def _normalise_ip(value: str | None) -> str | None:
    """Return a canonical IPv4 or IPv6 address, or None if invalid."""
    if value is None:
        return None

    try:
        return str(ip_address(value))
    except ValueError:
        return None


def get_client_ip(request: HttpRequest) -> str | None:
    """Return the client IP according to the Vocabio proxy policy."""
    client_ip, _ = resolve_client_ip(
        request,
        proxy_order=settings.CLIENT_IP_PROXY_ORDER,
        request_header_order=settings.CLIENT_IP_META_PRECEDENCE_ORDER,
    )

    return _normalise_ip(client_ip)
