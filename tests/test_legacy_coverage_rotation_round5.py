"""Branch rotation for the two lowest managed modules after NIGHT-BATCH-19.

The `audit_flags != result_flags` guard in rollback_preview_builder remains
intentionally unreachable after both values independently equal the exact safe
profile. It is retained as defense in depth and is not weakened for coverage.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest

import app.full_loop_preview_adapter as full_loop
from app.evidence_bundle_builder import compute_bundle_hash
from app.rollback_preview_builder import (
    RollbackPreviewBuildError,
    build_rollback_preview,
)


pytestmark = pytest.mark.legacy
ROOT = Path(__file__).resolve().parent.parent
BLACKBOARD = ROOT / "fixtures" / "blackboard_contract"
EVIDENCE = ROOT / "fixtures" / "local_mock_data" / "n1_dry_run_evidence_bundle.json"


def _json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _rollback_sources() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    return (
        _json(BLACKBOARD / "audit_event.valid.json"),
        _json(EVIDENCE),
        _json(BLACKBOARD / "result_message.valid.json"),
    )


def _rehash(bundle: dict[str, Any]) -> None:
    bundle["bundle_hash"] = compute_bundle_hash(bundle)


class _SchemaInvalidBoolLike:
    """Equal to its bool value, but never to a peer instance.

    Valid JSON/schema input cannot have this behavior.  It lets the test reach
    the retained defense-in-depth comparison without weakening or deleting it.
    """

    def __init__(self, value: bool) -> None:
        self.value = value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, bool):
            return self.value is other
        return self is other


@pytest.mark.parametrize(
    ("target", "field", "value", "error"),
    (
        ("bundle", "task", [], "evidence_bundle.task must be an object"),
        ("bundle", "mock_result", [], "evidence_bundle.mock_result must be an object"),
        ("audit", "safety_flags", [], "audit_event.safety_flags must be an object"),
        ("result", "safety_flags", [], "result_message.safety_flags must be an object"),
        ("result", "execution_class", "OWNER_APPROVAL", "execution_class values"),
    ),
)
def test_rollback_remaining_shape_and_execution_guards(
    target: str, field: str, value: object, error: str
) -> None:
    audit, bundle, result = _rollback_sources()
    records = {"audit": audit, "bundle": bundle, "result": result}
    records[target][field] = value
    if target == "bundle":
        _rehash(bundle)

    with pytest.raises(RollbackPreviewBuildError, match=error):
        build_rollback_preview(audit, bundle, result)


def test_rollback_rejects_bundle_only_task_and_execution_drift() -> None:
    audit, bundle, result = _rollback_sources()
    bundle["task"]["task_id"] = "task-bundle-drift"
    _rehash(bundle)
    with pytest.raises(RollbackPreviewBuildError, match="task_id values must match"):
        build_rollback_preview(audit, bundle, result)

    audit, bundle, result = _rollback_sources()
    bundle["task"]["execution_class"] = "OWNER_APPROVAL"
    _rehash(bundle)
    with pytest.raises(RollbackPreviewBuildError, match="execution_class values"):
        build_rollback_preview(audit, bundle, result)


def test_rollback_retains_cross_source_flag_defense_for_nonschema_objects() -> None:
    audit, bundle, result = _rollback_sources()
    audit["safety_flags"] = {
        key: _SchemaInvalidBoolLike(value)
        for key, value in audit["safety_flags"].items()
    }
    result["safety_flags"] = {
        key: _SchemaInvalidBoolLike(value)
        for key, value in result["safety_flags"].items()
    }

    with pytest.raises(RollbackPreviewBuildError, match="source safety_flags must match$"):
        build_rollback_preview(audit, bundle, result)


def test_full_loop_prefix_timeline_reports_missing_steps_without_order_claim() -> None:
    record = json.loads(full_loop.FIXTURE_PATH.read_text(encoding="utf-8"))
    timeline = copy.deepcopy(record["timeline"][:1])

    violations = full_loop._validate_timeline(timeline)

    assert any(item.startswith("missing required timeline steps:") for item in violations)
    assert "timeline steps are out of the required deterministic order" not in violations


def test_full_loop_recursive_helpers_cover_non_mapping_leaf_edges() -> None:
    assert full_loop._contains_unsafe_text(7) is False
    assert full_loop._contains_forbidden_field_names([7, "safe"]) == []
    summary = full_loop._summarize_step({"safety_flags": []})
    assert summary["safety_flags_summary"] == ""
