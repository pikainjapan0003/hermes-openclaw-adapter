"""Round-seven in-memory chain rehearsal with projection conditionals."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from app.remote_readonly_projection import (
    build_remote_readonly_projection,
)
from app.remote_readonly_projection import RemoteReadonlyProjectionError

from tests.test_full_chain_contract_rehearsal import (
    _assert_reference_chain,
    _build_full_chain,
)


pytestmark = pytest.mark.contract

ROOT = Path(__file__).resolve().parents[1]
PROJECTION_SCHEMA = json.loads(
    (
        ROOT
        / "docs"
        / "schemas"
        / "remote_readonly_projection.schema.json"
    ).read_text(encoding="utf-8")
)


def _projection_source(
    messages: dict[str, dict[str, Any]],
    evidence_bundle: dict[str, Any],
    *,
    phase: str = "approval_ready",
    status: str = "ready",
    decision: str | None = None,
    decision_timestamp: str | None = None,
) -> dict[str, Any]:
    task = messages["task_draft"]
    return {
        "task_id": task["task_id"],
        # The display projection contract requires a non-null parent label;
        # this synthetic parent is test data, not a production remapping rule.
        "parent_task_id": f"parent-{task['task_id']}",
        "phase": phase,
        "status": status,
        "execution_class": task["execution_class"],
        "safety_flags": dict(task["safety_flags"]),
        "approval_readiness": "ready_for_owner",
        "decision": decision,
        "decision_timestamp": decision_timestamp,
        "evidence_bundle_hash": evidence_bundle["bundle_hash"],
    }


def _build_projection(source: dict[str, Any]) -> dict[str, Any]:
    return build_remote_readonly_projection(
        source,
        data_generated_at="2026-08-05T00:00:00Z",
        source_commit_sha="c" * 40,
        stale_after="2026-08-05T00:15:00Z",
    )


def test_v7_full_chain_feeds_a_schema_valid_conditional_projection() -> None:
    messages, evidence_bundle = _build_full_chain()
    _assert_reference_chain(messages, evidence_bundle)

    projection = _build_projection(_projection_source(messages, evidence_bundle))
    errors = list(
        Draft202012Validator(
            PROJECTION_SCHEMA, format_checker=FormatChecker()
        ).iter_errors(projection)
    )

    assert errors == []
    assert projection["status"] == "ready"
    assert projection["phase"] == "approval_ready"
    assert projection["decision_summary"] == {
        "decision": None,
        "decision_timestamp": None,
    }

    decided = _build_projection(
        _projection_source(
            messages,
            evidence_bundle,
            phase="owner_decided",
            status="decided",
            decision="approve",
            decision_timestamp="2026-08-05T00:05:00Z",
        )
    )
    assert decided["phase"] == "owner_decided"
    assert decided["decision_summary"]["decision"] == "approve"


@pytest.mark.parametrize(
    ("status", "phase"),
    (("decided", "approval_ready"), ("ready", "owner_decided")),
)
def test_v7_conditional_status_phase_breaks_fail_closed(
    status: str, phase: str
) -> None:
    messages, evidence_bundle = _build_full_chain()
    source = _projection_source(
        messages,
        evidence_bundle,
        status=status,
        phase=phase,
        decision=None,
        decision_timestamp=None,
    )

    with pytest.raises(RemoteReadonlyProjectionError):
        _build_projection(source)
