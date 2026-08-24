"""Public home view for Vocabio."""

from django.http import HttpRequest, HttpResponse
from django.views.decorators.http import require_GET


@require_GET
def home(_request: HttpRequest) -> HttpResponse:
    """Return the public Vocabio home page."""
    return HttpResponse("Vocabio")
