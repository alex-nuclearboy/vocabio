"""Shared assertions for the Vocabio test suite."""

from django.http import HttpResponse


def assert_response_is_not_cached(response: HttpResponse) -> None:
    """Assert that a response prevents intermediary caching."""
    cache_control = response.headers["Cache-Control"]

    assert "no-cache" in cache_control
    assert "no-store" in cache_control
    assert "must-revalidate" in cache_control
