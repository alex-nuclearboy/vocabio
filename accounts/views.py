"""Authentication views for the accounts application."""

import logging

from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_http_methods, require_POST

from accounts.forms import LoginForm
from infrastructure.audit import format_audit_event
from infrastructure.request import get_client_ip


audit_logger = logging.getLogger("vocabio.audit.accounts")


def _get_safe_next_url(request: HttpRequest) -> str:
    """Return a safe local redirect target supplied with the request."""
    next_url = request.POST.get("next") or request.GET.get("next", "")

    if next_url and url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url

    return ""


@sensitive_post_parameters("password")
@csrf_protect
@never_cache
@require_http_methods(["GET", "POST"])
def login_view(request: HttpRequest) -> HttpResponse:
    """Authenticate a user and redirect to the requested local page."""
    if request.user.is_authenticated:
        return redirect(settings.LOGIN_REDIRECT_URL)

    next_url = _get_safe_next_url(request)

    form = LoginForm(
        request=request,
        data=request.POST if request.method == "POST" else None,
    )

    if request.method == "POST" and form.is_valid():
        user = form.get_user()

        login(request, user)

        audit_logger.info(
            format_audit_event(
                "[AUTH|LOGIN]",
                {
                    "user_id": user.pk,
                    "client_ip": get_client_ip(request),
                },
            )
        )

        return redirect(next_url or settings.LOGIN_REDIRECT_URL)

    return render(
        request,
        "accounts/login.html",
        {
            "form": form,
            "next": next_url,
        },
    )


@csrf_protect
@never_cache
@require_POST
@login_required(redirect_field_name=None)
def logout_view(request: HttpRequest) -> HttpResponse:
    """Log out the current user and redirect to the configured destination."""
    user_id = request.user.pk
    client_ip = get_client_ip(request)

    logout(request)

    audit_logger.info(
        format_audit_event(
            "[AUTH|LOGOUT]",
            {
                "user_id": user_id,
                "client_ip": client_ip,
            },
        )
    )

    return redirect(settings.LOGOUT_REDIRECT_URL)
