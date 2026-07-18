from __future__ import annotations

import ast
import copy
import json
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator

import app.remote_readonly_projection as projection_module
from app.remote_readonly_projection import (
    CANONICAL_SAFETY_FLAG_KEYS,
    RemoteReadonlyProjectionError,
    build_remote_readonly_projection,
    validate_remote_readonly_projection,
)


ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "docs" / "schemas" / "remote_readonly_projection.schema.json"
FIXTURE_DIR = ROOT / "fixtures" / "local_mock_data"
FIXTURE_PREFIX = "remote_readonly_projection."


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    assert isinstance(value, dict)
    return value


def _schema() -> dict[str, Any]:
    return _load_json(SCHEMA_PATH)


def _fixture(case: str) -> dict[str, Any]:
    return _load_json(FIXTURE_DIR / f"{FIXTURE_PREFIX}{case}.json")


def _canonical_safety_flags() -> dict[str, bool]:
    flags = {key: False for key in CANONICAL_SAFETY_FLAG_KEYS}
    flags.update(
        {
            "synthetic_local_only": True,
            "mock_only": True,
            "dry_run": True,
            "owner_review_required": True,
            "follow_up_requires_owner_confirmation": True,
        }
    )
    return flags


def _source() -> dict[str, Any]:
    return {
        "task_id": "task-phase8a-synthetic-0001",
        "parent_task_id": "parent-phase8a-synthetic-0001",
        "phase": "approval_ready",
        "status": "ready",
        "execution_class": "OWNER_APPROVAL",
        "safety_flags": _canonical_safety_flags(),
        "approval_readiness": "ready_for_owner",
        "decision": None,
        "decision_timestamp": None,
        "evidence_bundle_hash": (
            "9ba98d9bcdd8c659b927e7bdd1b10edbdc94f0f15112ddb19e5270c6e802d7aa"
        ),
    }


def _build(source: dict[str, Any] | None = None) -> dict[str, Any]:
    return build_remote_readonly_projection(
        source or _source(),
        data_generated_at="2026-07-19T02:00:00Z",
        source_commit_sha="0123456789abcdef0123456789abcdef01234567",
        stale_after="2026-07-19T02:15:00Z",
    )


def test_projection_schema_is_valid_closed_and_offline_only() -> None:
    schema = _schema()
    Draft202012Validator.check_schema(schema)

    assert schema["additionalProperties"] is False
    assert set(schema["required"]) == set(schema["properties"])
    assert schema["properties"]["pulled_at"] == {
        "description": (
            "Locked to null in offline Phase 8-A. A later remote phase requires separate "
            "authorization and schema revision."
        ),
        "type": "null",
        "const": None,
    }


def test_projection_fixture_inventory_is_exact() -> None:
    names = sorted(path.name for path in FIXTURE_DIR.glob(f"{FIXTURE_PREFIX}*.json"))
    assert names == [
        "remote_readonly_projection.invalid_extra_payload.json",
        "remote_readonly_projection.invalid_pulled_at.json",
        "remote_readonly_projection.invalid_secret_value.json",
        "remote_readonly_projection.valid.json",
    ]


def test_valid_fixture_passes_schema_and_leak_guard() -> None:
    result = validate_remote_readonly_projection(_fixture("valid"), _schema())

    assert result == {
        "valid": True,
        "schema": "remote_readonly_projection",
        "errors": [],
    }


@pytest.mark.parametrize(
    "case,validator",
    (
        ("invalid_extra_payload", "additionalProperties"),
        ("invalid_secret_value", "projectionLeak"),
        ("invalid_pulled_at", "const"),
    ),
)
def test_invalid_fixtures_fail_closed(case: str, validator: str) -> None:
    result = validate_remote_readonly_projection(_fixture(case), _schema())

    assert result["valid"] is False
    assert any(error["validator"] == validator for error in result["errors"])


def test_builder_reproduces_fixture_without_mutating_source() -> None:
    source = _source()
    before = copy.deepcopy(source)

    projection = _build(source)

    assert projection == _fixture("valid")
    assert source == before
    assert source["task_id"] not in json.dumps(projection)
    assert source["parent_task_id"] not in json.dumps(projection)
    assert projection["pulled_at"] is None


@pytest.mark.parametrize(
    "field,value",
    (
        ("raw_payload", {"prompt": "do something"}),
        ("workspace_path", "C:\\Users\\Owner\\private"),
        ("api_token", "sk-proj-abcdefghijklmnop"),
        ("environment", {"MODE": "live"}),
        ("command", "run external tool"),
    ),
)
def test_builder_rejects_any_non_allowlisted_source_field(field: str, value: Any) -> None:
    source = _source()
    source[field] = value

    with pytest.raises(RemoteReadonlyProjectionError, match="source fields must be exact"):
        _build(source)


def test_builder_requires_exact_canonical_safety_flags() -> None:
    missing = _source()
    missing["safety_flags"].pop("follow_up_allowed")
    with pytest.raises(RemoteReadonlyProjectionError, match="safety_flags fields must be exact"):
        _build(missing)

    extra = _source()
    extra["safety_flags"]["legacy_flag"] = False
    with pytest.raises(RemoteReadonlyProjectionError, match="safety_flags fields must be exact"):
        _build(extra)


@pytest.mark.parametrize(
    "flag",
    (
        "external_side_effects_allowed",
        "external_side_effects_occurred",
        "worker_dispatch_allowed",
        "openclaw_call_allowed",
        "hermes_runtime_allowed",
        "connector_call_allowed",
    ),
)
def test_builder_rejects_unsafe_projection_posture(flag: str) -> None:
    source = _source()
    source["safety_flags"][flag] = True

    with pytest.raises(RemoteReadonlyProjectionError, match=rf"safety_flags\.{flag} must be False"):
        _build(source)


def test_decided_projection_is_display_data_only() -> None:
    source = _source()
    source.update(
        {
            "phase": "owner_decided",
            "status": "decided",
            "decision": "approve",
            "decision_timestamp": "2026-07-19T02:05:00Z",
        }
    )

    projection = _build(source)

    assert validate_remote_readonly_projection(projection, _schema())["valid"] is True
    assert projection["decision_summary"] == {
        "decision": "approve",
        "decision_timestamp": "2026-07-19T02:05:00Z",
    }
    assert projection["safety_summary"]["worker_dispatch_allowed"] is False
    assert projection["pulled_at"] is None


def test_timestamp_and_decision_inconsistencies_fail_closed() -> None:
    with pytest.raises(RemoteReadonlyProjectionError, match="stale_after must be later"):
        build_remote_readonly_projection(
            _source(),
            data_generated_at="2026-07-19T02:00:00Z",
            source_commit_sha="0123456789abcdef0123456789abcdef01234567",
            stale_after="2026-07-19T01:59:00Z",
        )

    source = _source()
    source["decision"] = "approve"
    with pytest.raises(RemoteReadonlyProjectionError, match="non-decided projection"):
        _build(source)


def test_projection_module_has_no_io_network_runtime_or_dispatch_imports() -> None:
    source = Path(projection_module.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".", 1)[0])

    assert imported_roots <= {
        "__future__",
        "datetime",
        "hashlib",
        "jsonschema",
        "re",
        "typing",
    }
    forbidden_calls = {
        "open",
        "read",
        "read_bytes",
        "read_text",
        "write",
        "write_bytes",
        "write_text",
        "request",
        "post",
        "put",
        "delete",
        "dispatch",
        "execute",
        "enqueue",
        "send",
        "connect",
        "webhook",
        "callback",
        "runtime",
    }
    calls: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name):
            calls.append(node.func.id.lower())
        elif isinstance(node.func, ast.Attribute):
            calls.append(node.func.attr.lower())
    assert not (set(calls) & forbidden_calls)
