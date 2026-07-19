"""Tests for the pure three-input Phase 7 rollback preview builder."""

from __future__ import annotations

import ast
import copy
import json
from pathlib import Path
from typing import Any, Callable

import pytest

import app.rollback_preview_builder as builder_module
from app.blackboard_validators import validate_blackboard_message
from app.evidence_bundle_builder import compute_bundle_hash
from app.rollback_preview_builder import (
    RollbackPreviewBuildError,
    build_rollback_preview,
)


ROOT = Path(__file__).resolve().parent.parent
BLACKBOARD_FIXTURES = ROOT / "fixtures" / "blackboard_contract"
EVIDENCE_FIXTURE = (
    ROOT / "fixtures" / "local_mock_data" / "n1_dry_run_evidence_bundle.json"
)


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _sources() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    return (
        _load(BLACKBOARD_FIXTURES / "audit_event.valid.json"),
        _load(EVIDENCE_FIXTURE),
        _load(BLACKBOARD_FIXTURES / "result_message.valid.json"),
    )


def _rehash(bundle: dict[str, Any]) -> None:
    bundle["bundle_hash"] = compute_bundle_hash(bundle)


def test_valid_sources_build_schema_valid_deterministic_preview_without_mutation() -> None:
    audit, bundle, result = _sources()
    before = copy.deepcopy((audit, bundle, result))

    preview = build_rollback_preview(audit, bundle, result)

    assert (audit, bundle, result) == before
    assert preview["rollback_id"] == (
        "rollback-audit-phase3-001-result-phase3-001"
    )
    assert preview["created_at"] == audit["created_at"]
    assert preview["prev_entry_hash"] is None
    assert preview["rollback_status"] == "NOT_REQUIRED"
    assert preview["rollback_required"] is False
    assert preview["preview_only"] is True
    assert "token" not in preview
    validation = validate_blackboard_message(preview, "rollback_event")
    assert validation["valid"] is True, validation["errors"]


def _bad_bundle_hash(
    audit: dict[str, Any], bundle: dict[str, Any], result: dict[str, Any]
) -> None:
    del audit, result
    bundle["bundle_hash"] = "0" * 64


def _result_side_effect(
    audit: dict[str, Any], bundle: dict[str, Any], result: dict[str, Any]
) -> None:
    del audit, bundle
    result["external_side_effects"] = ["unexpected write"]


def _bundle_expected_side_effect(
    audit: dict[str, Any], bundle: dict[str, Any], result: dict[str, Any]
) -> None:
    del audit, result
    bundle["expected_side_effects"] = ["unexpected write"]
    _rehash(bundle)


def _audit_task_mismatch(
    audit: dict[str, Any], bundle: dict[str, Any], result: dict[str, Any]
) -> None:
    del bundle, result
    audit["task_id"] = "task-unrelated"


def _result_id_mismatch(
    audit: dict[str, Any], bundle: dict[str, Any], result: dict[str, Any]
) -> None:
    del audit, bundle
    result["result_id"] = "result-unrelated"


def _safety_flag_mismatch(
    audit: dict[str, Any], bundle: dict[str, Any], result: dict[str, Any]
) -> None:
    del audit, bundle
    result["safety_flags"]["worker_dispatch_allowed"] = True


def _non_auto(
    audit: dict[str, Any], bundle: dict[str, Any], result: dict[str, Any]
) -> None:
    del bundle, result
    audit["execution_class"] = "OWNER_APPROVAL"


def _not_preview_only(
    audit: dict[str, Any], bundle: dict[str, Any], result: dict[str, Any]
) -> None:
    del bundle, result
    audit["preview_only"] = False


def _persisted_audit(
    audit: dict[str, Any], bundle: dict[str, Any], result: dict[str, Any]
) -> None:
    del bundle, result
    audit["audit_status"] = "persisted"


def _missing_audit_id(
    audit: dict[str, Any], bundle: dict[str, Any], result: dict[str, Any]
) -> None:
    del bundle, result
    del audit["audit_id"]


@pytest.mark.parametrize(
    "mutation,error_match",
    (
        (_bad_bundle_hash, "hash verification"),
        (_result_side_effect, "external_side_effects must be empty"),
        (_bundle_expected_side_effect, "expected_side_effects must be empty"),
        (_audit_task_mismatch, "task_id values must match"),
        (_result_id_mismatch, "result_id values must match"),
        (_safety_flag_mismatch, "canonical 16-key safe profile"),
        (_non_auto, "execution_class values must be AUTO"),
        (_not_preview_only, "must be preview_only"),
        (_persisted_audit, "audit_status must be preview"),
        (_missing_audit_id, "audit_event.audit_id must be non-empty text"),
    ),
    ids=(
        "bad-bundle-hash",
        "result-side-effect",
        "bundle-expected-side-effect",
        "task-chain",
        "result-chain",
        "safety-profile",
        "execution-class",
        "preview-only",
        "audit-status",
        "missing-field",
    ),
)
def test_fail_closed_source_mutations_are_rejected(
    mutation: Callable[
        [dict[str, Any], dict[str, Any], dict[str, Any]], None
    ],
    error_match: str,
) -> None:
    audit, bundle, result = _sources()
    mutation(audit, bundle, result)

    with pytest.raises(RollbackPreviewBuildError, match=error_match):
        build_rollback_preview(audit, bundle, result)


@pytest.mark.parametrize(
    "flag",
    (
        "external_side_effects_performed",
        "worker_dispatched",
        "real_openclaw_called",
        "queue_written",
        "audit_trail_written",
    ),
)
def test_each_mock_execution_flag_fails_closed(flag: str) -> None:
    audit, bundle, result = _sources()
    bundle["mock_result"][flag] = True
    _rehash(bundle)

    with pytest.raises(RollbackPreviewBuildError, match=rf"{flag} must be false"):
        build_rollback_preview(audit, bundle, result)


def test_builder_imports_only_pure_contract_dependencies() -> None:
    source = Path(builder_module.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".", 1)[0])

    assert imported_roots <= {"__future__", "app", "collections", "typing"}
    assert imported_roots.isdisjoint(
        {"httpx", "os", "pathlib", "requests", "socket", "subprocess"}
    )
