"""Structured audit-event helpers for Vocabio."""

import json
from collections.abc import Mapping


def _format_value(value: object) -> str:
    """Return a safe single-field representation for an audit event."""
    if value is None:
        return "null"

    if isinstance(value, bool):
        return str(value).lower()

    if isinstance(value, (int, float)):
        return str(value)

    return json.dumps(
        str(value),
        ensure_ascii=False,
    )


def format_audit_event(
    event: str,
    fields: Mapping[str, object] | None = None,
) -> str:
    """Return a structured single-line audit event."""
    parts = [event]

    for key, value in (fields or {}).items():
        parts.append(
            f"{key}={_format_value(value)}"
        )

    return " ".join(parts)
