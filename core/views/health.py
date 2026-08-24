"""Health-check views for the Vocabio application."""

from django.db import DatabaseError, connection
from django.http import HttpRequest, JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET


@never_cache
@require_GET
def liveness(_request: HttpRequest) -> JsonResponse:
    """Report whether the application process is running."""
    return JsonResponse({"status": "ok"})


@never_cache
@require_GET
def readiness(_request: HttpRequest) -> JsonResponse:
    """Report whether the application can access its database."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
    except DatabaseError:
        return JsonResponse(
            {"status": "unavailable"},
            status=503,
        )

    if result != (1,):
        return JsonResponse(
            {"status": "unavailable"},
            status=503,
        )

    return JsonResponse({"status": "ok"})
