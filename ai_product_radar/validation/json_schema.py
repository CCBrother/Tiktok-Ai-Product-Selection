from __future__ import annotations

from typing import Any

from jsonschema import Draft202012Validator


PRODUCT_EVENT_SCHEMA = {
    "type": "object",
    "required": ["event_id", "event_type", "source", "collected_at", "url", "payload"],
    "properties": {
        "event_id": {"type": "string"},
        "event_type": {"type": "string"},
        "source": {"type": "string"},
        "collected_at": {"type": "string"},
        "url": {"type": "string"},
        "payload": {"type": "object"},
        "meta": {"type": "object"},
    },
}


def validate_json_schema(payload: dict[str, Any], schema: dict[str, Any] = PRODUCT_EVENT_SCHEMA) -> None:
    Draft202012Validator(schema).validate(payload)
