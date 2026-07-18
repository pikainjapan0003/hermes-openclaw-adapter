from __future__ import annotations

import ast
import copy
import json
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator, FormatChecker

import app.evidence_bundle_builder as builder_module
from app.evidence_bundle_builder import (
    EvidenceBundleError,
    SensitiveEvidenceError,
    build_evidence_bundle,
    compute_bundle_hash,
    verify_bundle_hash,
)
from app.worker_mock_gateway_dry_run import run_worker_to_mock_gateway_dry_run


ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "docs" / "schemas" / "evidence_bundle.json"
BUNDLE_FIXTURE_PATH = (
    ROOT / "fixtures" / "local_mock_data" / "n1_dry_run_evidence_bundle.json"
)
TASK_FIXTURE_PATH = (
    ROOT / "fixtures" / "blackboard_contract" / "task_draft.valid.json"
)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    assert isinstance(value, dict)
    return value


def n1_command(task_id: str) -> dict[str, Any]:
    return {
        "command_id": "cmd-evidence-n1-001",
        "task_id": task_id,
        "tool_target": "synthetic.adapter.status",
        "requested_action": "read one synthetic adapter status value",
        "risk_level": "low",
        "approval_snapshot": {"owner_review_required": True},
        "execution_mode": "mock_only",
        "dry_run": True,
        "mock_only": True,
        "external_touchpoints": [],
        "rollback_plan": "no rollback required; nothing is executed",
        "external_side_effects_allowed": False,
    }


def validate_bundle(bundle: dict[str, Any]) -> list[Any]:
    schema = load_json(SCHEMA_PATH)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return sorted(validator.iter_errors(bundle), key=lambda error: list(error.path))


def build_from_rehearsal() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    task = load_json(TASK_FIXTURE_PATH)
    command = n1_command(task["task_id"])
    mock_result = run_worker_to_mock_gateway_dry_run(command)
    bundle = build_evidence_bundle(
        task,
        command,
        mock_result,
        [],
        created_at="2026-07-19T18:00:00Z",
    )
    return bundle, command, mock_result


def test_evidence_bundle_schema_is_closed_and_valid() -> None:
    schema = load_json(SCHEMA_PATH)

    Draft202012Validator.check_schema(schema)
    assert schema["additionalProperties"] is False
    assert schema["properties"]["bundle_type"]["const"] == "n1_dry_run_evidence"
    assert schema["properties"]["hash_algorithm"]["const"] == "sha256"


def test_complete_rehearsal_flow_builds_schema_valid_fixture() -> None:
    bundle, command, mock_result = build_from_rehearsal()

    assert mock_result["accepted"] is True
    assert mock_result["worker_dispatched"] is False
    assert mock_result["real_openclaw_called"] is False
    assert mock_result["external_side_effects_performed"] is False
    assert bundle == load_json(BUNDLE_FIXTURE_PATH)
    assert validate_bundle(bundle) == []
    assert bundle["command_envelope"]["command_id"] == command["command_id"]


def test_fixture_hash_recomputes_consistently() -> None:
    bundle = load_json(BUNDLE_FIXTURE_PATH)

    assert compute_bundle_hash(bundle) == bundle["bundle_hash"]
    assert verify_bundle_hash(bundle) is True


def test_tampered_bundle_fails_hash_verification() -> None:
    bundle = load_json(BUNDLE_FIXTURE_PATH)
    bundle["mock_result"]["gateway_response"]["mock_response_summary"] = (
        "tampered result"
    )

    assert verify_bundle_hash(bundle) is False


def test_builder_does_not_mutate_rehearsal_inputs() -> None:
    task = load_json(TASK_FIXTURE_PATH)
    command = n1_command(task["task_id"])
    mock_result = run_worker_to_mock_gateway_dry_run(command)
    before = copy.deepcopy((task, command, mock_result))

    build_evidence_bundle(
        task,
        command,
        mock_result,
        [],
        created_at="2026-07-19T18:00:00Z",
    )

    assert (task, command, mock_result) == before


@pytest.mark.parametrize(
    "field,value",
    (
        ("api_token", "sk-proj-1234567890abcdefghijklmnop"),
        ("workspace_path", "C:\\Users\\Owner\\private"),
        ("environment", {"MODE": "production"}),
    ),
)
def test_builder_rejects_secret_path_and_environment_fields(
    field: str, value: Any
) -> None:
    task = load_json(TASK_FIXTURE_PATH)
    command = n1_command(task["task_id"])
    mock_result = run_worker_to_mock_gateway_dry_run(command)
    mock_result[field] = value

    with pytest.raises(SensitiveEvidenceError, match="forbidden sensitive"):
        build_evidence_bundle(
            task,
            command,
            mock_result,
            [],
            created_at="2026-07-19T18:00:00Z",
        )


def test_builder_projects_only_allowlisted_fields() -> None:
    task = load_json(TASK_FIXTURE_PATH)
    task["display_only_note"] = "benign source-only note"
    command = n1_command(task["task_id"])
    mock_result = run_worker_to_mock_gateway_dry_run(command)

    bundle = build_evidence_bundle(
        task,
        command,
        mock_result,
        [],
        created_at="2026-07-19T18:00:00Z",
    )

    assert "display_only_note" not in bundle["task"]
    assert validate_bundle(bundle) == []


def test_builder_rejects_side_effect_or_dispatch_evidence() -> None:
    task = load_json(TASK_FIXTURE_PATH)
    command = n1_command(task["task_id"])
    mock_result = run_worker_to_mock_gateway_dry_run(command)
    mock_result["worker_dispatched"] = True

    with pytest.raises(EvidenceBundleError, match="worker_dispatched must be false"):
        build_evidence_bundle(
            task,
            command,
            mock_result,
            [],
            created_at="2026-07-19T18:00:00Z",
        )


def test_builder_has_no_io_runtime_or_dispatch_imports() -> None:
    source = Path(builder_module.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".", 1)[0])

    assert imported_roots <= {
        "__future__",
        "hashlib",
        "hmac",
        "json",
        "re",
        "typing",
    }
    assert imported_roots.isdisjoint(
        {"app", "os", "pathlib", "subprocess", "requests", "httpx", "socket"}
    )
