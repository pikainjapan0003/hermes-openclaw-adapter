"""Pure Blackboard contract loading and validation helpers.

This module performs in-memory validation only. It is intentionally not wired
into ``app.main`` or any route, queue, Worker, or runtime path.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError


SCHEMA_FILES: dict[str, str] = {
    "task_draft": "task_draft.schema.json",
    "annotation": "annotation.schema.json",
    "approval_readiness": "approval_readiness.schema.json",
    "owner_decision": "owner_decision.schema.json",
    "worker_dry_run": "worker_dry_run.schema.json",
    "openclaw_command_envelope": "openclaw_command_envelope.schema.json",
    "result_message": "result_message.schema.json",
    "audit_event": "audit_event.schema.json",
    "rollback_event": "rollback_event.schema.json",
    "approval_packet": "approval_packet.schema.json",
}

_SCHEMA_DIR = (
    Path(__file__).resolve().parent.parent / "docs" / "schemas" / "blackboard"
)
_FORMAT_CHECKER = FormatChecker()


class BlackboardSchemaError(ValueError):
    """Raised when a requested Blackboard schema cannot be loaded safely."""


def _json_path(parts: Any) -> str:
    path = "$"
    for part in parts:
        if isinstance(part, int):
            path += f"[{part}]"
        else:
            path += f".{part}"
    return path


def _selection_error(path: str, message: str) -> dict[str, Any]:
    return {
        "path": path,
        "schema_path": "$",
        "validator": "schema_selection",
        "message": message,
    }


@lru_cache(maxsize=len(SCHEMA_FILES))
def load_blackboard_schema(message_type: str) -> dict[str, Any]:
    """Load and meta-validate one allowlisted Blackboard JSON Schema."""

    filename = SCHEMA_FILES.get(message_type)
    if filename is None:
        allowed = ", ".join(sorted(SCHEMA_FILES))
        raise BlackboardSchemaError(
            f"unknown Blackboard message_type {message_type!r}; allowed: {allowed}"
        )

    schema_path = _SCHEMA_DIR / filename
    try:
        with schema_path.open("r", encoding="utf-8") as handle:
            schema = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise BlackboardSchemaError(
            f"failed to load Blackboard schema {filename}: {exc}"
        ) from exc

    if not isinstance(schema, dict):
        raise BlackboardSchemaError(
            f"Blackboard schema {filename} root must be a JSON object"
        )

    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as exc:
        raise BlackboardSchemaError(
            f"invalid Blackboard schema {filename}: {exc}"
        ) from exc
    return schema


@lru_cache(maxsize=len(SCHEMA_FILES))
def _validator_for(message_type: str) -> Draft202012Validator:
    return Draft202012Validator(
        load_blackboard_schema(message_type),
        format_checker=_FORMAT_CHECKER,
    )


def validate_blackboard_message(
    message: Mapping[str, Any],
    message_type: str | None = None,
) -> dict[str, Any]:
    """Validate a Blackboard message and return a structured result.

    ``message_type`` may be supplied explicitly or selected from the message.
    The function does not mutate the input and has no write or runtime effects.
    """

    if not isinstance(message, Mapping):
        return {
            "valid": False,
            "message_type": message_type,
            "schema_file": None,
            "errors": [
                _selection_error("$", "Blackboard message must be a mapping")
            ],
        }

    selected_type = message_type
    if selected_type is None:
        candidate = message.get("message_type")
        if not isinstance(candidate, str) or not candidate:
            return {
                "valid": False,
                "message_type": None,
                "schema_file": None,
                "errors": [
                    _selection_error(
                        "$.message_type",
                        "message_type is required to select a Blackboard schema",
                    )
                ],
            }
        selected_type = candidate

    filename = SCHEMA_FILES.get(selected_type)
    if filename is None:
        allowed = ", ".join(sorted(SCHEMA_FILES))
        return {
            "valid": False,
            "message_type": selected_type,
            "schema_file": None,
            "errors": [
                _selection_error(
                    "$.message_type",
                    f"unknown Blackboard message_type {selected_type!r}; allowed: {allowed}",
                )
            ],
        }

    validator = _validator_for(selected_type)
    validation_errors = sorted(
        validator.iter_errors(dict(message)),
        key=lambda error: (_json_path(error.absolute_path), error.message),
    )
    errors = [
        {
            "path": _json_path(error.absolute_path),
            "schema_path": _json_path(error.absolute_schema_path),
            "validator": error.validator,
            "message": error.message,
        }
        for error in validation_errors
    ]
    return {
        "valid": not errors,
        "message_type": selected_type,
        "schema_file": filename,
        "errors": errors,
    }
