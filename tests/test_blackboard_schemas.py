from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator

from app.blackboard_validators import (
    SCHEMA_FILES,
    load_blackboard_schema,
    validate_blackboard_message,
)


ROOT = Path(__file__).resolve().parent.parent
FIXTURE_DIR = ROOT / "fixtures" / "blackboard_contract"
SCHEMA_DIR = ROOT / "docs" / "schemas" / "blackboard"
MESSAGE_TYPES = tuple(SCHEMA_FILES)
COMMON_FIELDS = {
    "schema_version",
    "message_type",
    "created_at",
    "safety_flags",
    "prev_entry_hash",
    "execution_class",
    "produced_by",
    "parent_task_id",
    "role",
}
SAFETY_FLAG_KEYS = {
    "synthetic_local_only",
    "mock_only",
    "dry_run",
    "owner_review_required",
    "external_side_effects_allowed",
    "external_side_effects_occurred",
    "blackboard_write_allowed",
    "queue_write_allowed",
    "audit_trail_write_allowed",
    "worker_dispatch_allowed",
    "openclaw_call_allowed",
    "hermes_runtime_allowed",
    "connector_call_allowed",
    "google_sheets_write_allowed",
    "follow_up_allowed",
    "follow_up_requires_owner_confirmation",
}


def load_fixture(message_type: str, case: str) -> dict[str, Any]:
    path = FIXTURE_DIR / f"{message_type}.{case}.json"
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    assert isinstance(data, dict)
    return data


def test_contract_inventory_is_exact() -> None:
    schema_files = sorted(SCHEMA_DIR.glob("*.schema.json"))
    fixture_files = sorted(FIXTURE_DIR.glob("*.json"))

    assert len(SCHEMA_FILES) == 10
    assert len(schema_files) == 10
    assert len(fixture_files) == 30
    assert {path.name for path in schema_files} == set(SCHEMA_FILES.values())

    expected_fixtures = {
        f"{message_type}.{case}.json"
        for message_type in MESSAGE_TYPES
        for case in (
            "valid",
            "invalid_missing_common",
            "invalid_extra_safety_flag",
        )
    }
    assert {path.name for path in fixture_files} == expected_fixtures


@pytest.mark.parametrize("message_type", MESSAGE_TYPES)
def test_schema_is_valid_and_closed(message_type: str) -> None:
    schema = load_blackboard_schema(message_type)
    Draft202012Validator.check_schema(schema)
    assert schema["additionalProperties"] is False
    assert COMMON_FIELDS <= set(schema["required"])
    assert schema["properties"]["message_type"]["const"] == message_type


@pytest.mark.parametrize("message_type", MESSAGE_TYPES)
def test_positive_fixture_is_valid_and_has_canonical_common_fields(
    message_type: str,
) -> None:
    fixture = load_fixture(message_type, "valid")

    assert COMMON_FIELDS <= fixture.keys()
    assert set(fixture["safety_flags"]) == SAFETY_FLAG_KEYS
    assert len(fixture["safety_flags"]) == 16
    assert all(type(value) is bool for value in fixture["safety_flags"].values())

    result = validate_blackboard_message(fixture)
    assert result == {
        "valid": True,
        "message_type": message_type,
        "schema_file": SCHEMA_FILES[message_type],
        "errors": [],
    }


@pytest.mark.parametrize("message_type", MESSAGE_TYPES)
def test_missing_common_field_fixture_is_rejected(message_type: str) -> None:
    fixture = load_fixture(message_type, "invalid_missing_common")
    result = validate_blackboard_message(fixture)

    assert result["valid"] is False
    assert any(
        error["validator"] == "required" and "role" in error["message"]
        for error in result["errors"]
    )


@pytest.mark.parametrize("message_type", MESSAGE_TYPES)
def test_extra_safety_flag_fixture_is_rejected(message_type: str) -> None:
    fixture = load_fixture(message_type, "invalid_extra_safety_flag")
    result = validate_blackboard_message(fixture)

    assert result["valid"] is False
    assert any(
        error["validator"] == "additionalProperties"
        and error["path"] == "$.safety_flags"
        and "read_only" in error["message"]
        for error in result["errors"]
    )


@pytest.mark.parametrize(
    "message_type",
    ("worker_dry_run", "openclaw_command_envelope"),
)
def test_owner_manual_is_structurally_rejected_for_dispatch_path(
    message_type: str,
) -> None:
    fixture = load_fixture(message_type, "valid")
    fixture["execution_class"] = "OWNER_MANUAL"

    result = validate_blackboard_message(fixture)
    assert result["valid"] is False
    assert any(
        error["validator"] == "enum"
        and error["path"] == "$.execution_class"
        for error in result["errors"]
    )


def test_unknown_message_type_returns_structured_selection_error() -> None:
    result = validate_blackboard_message({"message_type": "unknown"})

    assert result["valid"] is False
    assert result["schema_file"] is None
    assert result["errors"][0]["validator"] == "schema_selection"
    assert result["errors"][0]["path"] == "$.message_type"


def test_non_mapping_returns_structured_selection_error() -> None:
    result = validate_blackboard_message([])  # type: ignore[arg-type]

    assert result["valid"] is False
    assert result["schema_file"] is None
    assert result["errors"][0]["validator"] == "schema_selection"
    assert result["errors"][0]["path"] == "$"
