"""Integration tests for database connectivity."""

import pytest
from django.db import connection


@pytest.mark.django_db
def test_postgresql_connection():
    """Verify that Django can connect to PostgreSQL."""
    connection.ensure_connection()

    assert connection.vendor == "postgresql"
    assert connection.is_usable()
