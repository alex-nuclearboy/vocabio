"""Security helpers for the accounts application."""

import logging
from typing import Any

from axes.helpers import get_client_username, get_lockout_message
from django.conf import settings
from django.http import HttpRequest, HttpResponse

from infrastructure.audit import format_audit_event
from infrastructure.request import get_client_ip


audit_logger = logging.getLogger("vocabio.audit.accounts")


def login_lockout_response(
    request: HttpRequest,
    _original_response: HttpResponse | None,
    credentials: dict[str, Any] | None,
) -> HttpResponse:
    """Record and return an authentication lockout response."""
    audit_logger.warning(
        format_audit_event(
            "[AUTH|LOCKOUT]",
            {
                "username": get_client_username(request, credentials),
                "client_ip": get_client_ip(request),
                "path": request.path,
            },
        )
    )

    return HttpResponse(
        get_lockout_message(),
        status=settings.AXES_HTTP_RESPONSE_CODE,
    )
