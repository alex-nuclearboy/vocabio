"""Tests for structured audit-event helpers."""

from infrastructure.audit import format_audit_event


def test_audit_event_formats_integer_fields():
    """Integer audit fields are rendered without quoting."""
    event = format_audit_event(
        "[AUTH|LOGIN]",
        {
            "user_id": 4,
        },
    )

    assert event == "[AUTH|LOGIN] user_id=4"


def test_audit_event_formats_none_as_null():
    """Missing audit values use an explicit null representation."""
    event = format_audit_event(
        "[AUTH|LOGIN]",
        {
            "client_ip": None,
        },
    )

    assert event == "[AUTH|LOGIN] client_ip=null"


def test_audit_event_formats_boolean_fields():
    """Boolean audit fields use lowercase values."""
    event = format_audit_event(
        "[ACCESS|DENIED]",
        {
            "authenticated": True,
        },
    )

    assert event == "[ACCESS|DENIED] authenticated=true"


def test_audit_event_quotes_string_fields():
    """String audit fields are safely quoted."""
    event = format_audit_event(
        "[AUTH|LOCKOUT]",
        {
            "username": "john smith",
        },
    )

    assert event == '[AUTH|LOCKOUT] username="john smith"'


def test_audit_event_escapes_newlines():
    """String audit fields cannot inject additional log lines."""
    event = format_audit_event(
        "[AUTH|LOCKOUT]",
        {
            "username": "john\nsmith",
        },
    )

    assert event == '[AUTH|LOCKOUT] username="john\\nsmith"'


def test_audit_event_supports_no_fields():
    """Audit events can be formatted without additional fields."""
    event = format_audit_event("[SYSTEM|START]")

    assert event == "[SYSTEM|START]"
