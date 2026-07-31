"""Known schema-error marker exposure baseline.

These tests deliberately do not change or bless the validator behavior.  An
``xfail`` means the current public result echoes an untrusted instance value
and therefore still needs the Owner-selected redaction design.  Once a schema
stops echoing the marker, its case becomes an ordinary pass.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.blackboard_validators import (
    SCHEMA_FILES,
    validate_blackboard_message,
)


ROOT = Path(__file__).resolve().parent.parent
FIXTURE_DIR = ROOT / "fixtures" / "blackboard_contract"
MARKER = "FAKE-SECRET-NB12"
EXPECTED_REDACTION_XFAIL_SCHEMAS = frozenset(
    {
        "annotation",
        "approval_packet",
        "approval_readiness",
        "audit_event",
        "openclaw_command_envelope",
        "owner_decision",
        "result_message",
        "rollback_event",
        "task_draft",
        "worker_dry_run",
    }
)


def _valid_fixture(message_type: str) -> dict[str, object]:
    path = FIXTURE_DIR / f"{message_type}.valid.json"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize(
    "message_type",
    sorted(EXPECTED_REDACTION_XFAIL_SCHEMAS),
)
def test_schema_error_marker_exposure_baseline(message_type: str) -> None:
    """Record each schema whose raw jsonschema message echoes the marker."""

    message = _valid_fixture(message_type)
    safety_flags = message["safety_flags"]
    assert isinstance(safety_flags, dict)
    safety_flags["synthetic_local_only"] = MARKER

    result = validate_blackboard_message(message)

    assert result["valid"] is False
    assert result["errors"]
    rendered_errors = json.dumps(
        result["errors"],
        ensure_ascii=False,
        sort_keys=True,
    )
    if MARKER in rendered_errors:
        pytest.xfail(
            f"known redaction gap: {message_type} error echoes instance marker"
        )
    assert MARKER not in rendered_errors


def test_redaction_baseline_covers_exact_schema_inventory() -> None:
    fixture_types = {
        path.name.removesuffix(".valid.json")
        for path in FIXTURE_DIR.glob("*.valid.json")
    }
    assert EXPECTED_REDACTION_XFAIL_SCHEMAS == set(SCHEMA_FILES)
    assert EXPECTED_REDACTION_XFAIL_SCHEMAS <= fixture_types
    assert len(EXPECTED_REDACTION_XFAIL_SCHEMAS) == 10


def test_runtime_redaction_gap_inventory_is_exact() -> None:
    """Fail if the ten named xfail cases stop matching actual marker echoes."""

    echoing_schemas: set[str] = set()
    for message_type in sorted(SCHEMA_FILES):
        message = _valid_fixture(message_type)
        safety_flags = message["safety_flags"]
        assert isinstance(safety_flags, dict)
        safety_flags["synthetic_local_only"] = MARKER

        result = validate_blackboard_message(message)
        rendered = json.dumps(result["errors"], ensure_ascii=False, sort_keys=True)
        if MARKER in rendered:
            echoing_schemas.add(message_type)

    assert echoing_schemas == EXPECTED_REDACTION_XFAIL_SCHEMAS


def test_missing_message_type_selection_error_is_payload_free() -> None:
    result = validate_blackboard_message({"untrusted_field": MARKER})

    assert result["valid"] is False
    assert result["schema_file"] is None
    assert result["errors"] == [
        {
            "path": "$.message_type",
            "schema_path": "$",
            "validator": "schema_selection",
            "message": "message_type is required to select a Blackboard schema",
        }
    ]
    assert MARKER not in json.dumps(result, ensure_ascii=False, sort_keys=True)
