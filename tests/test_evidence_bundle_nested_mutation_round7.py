"""Round-seven mutations for evidence-bundle nested identity consistency."""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

from app.evidence_bundle_builder import EvidenceBundleError, build_evidence_bundle
from app.worker_mock_gateway_dry_run import run_worker_to_mock_gateway_dry_run


pytestmark = pytest.mark.fuzz

ROOT = Path(__file__).resolve().parents[1]
TASK_FIXTURE = ROOT / "fixtures" / "blackboard_contract" / "task_draft.valid.json"
SEED = 20260804
CASES_PER_CLASS = 30


@dataclass(frozen=True)
class Mutation:
    owner: str
    index: int


def _cases() -> tuple[Mutation, ...]:
    values = [
        Mutation(owner, index)
        for owner in ("task", "command_envelope", "mock_result")
        for index in range(1, CASES_PER_CLASS + 1)
    ]
    random.Random(SEED).shuffle(values)
    return tuple(values)


CASES = _cases()


def _load_task() -> dict[str, Any]:
    value = json.loads(TASK_FIXTURE.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    task = _load_task()
    command = {
        "command_id": "cmd-round7-001",
        "task_id": task["task_id"],
        "tool_target": "synthetic.adapter.status",
        "requested_action": "read one synthetic adapter status value",
        "risk_level": "low",
        "approval_snapshot": {"owner_review_required": True},
        "execution_mode": "mock_only",
        "dry_run": True,
        "mock_only": True,
        "external_touchpoints": [],
        "rollback_plan": "nothing executed",
        "external_side_effects_allowed": False,
    }
    return task, command, run_worker_to_mock_gateway_dry_run(command)


def test_round7_inventory_is_seeded_balanced_and_targets_real_fields() -> None:
    assert SEED == 20260804
    assert len(CASES) == 90
    assert {
        owner: sum(case.owner == owner for case in CASES)
        for owner in ("task", "command_envelope", "mock_result")
    } == {"task": 30, "command_envelope": 30, "mock_result": 30}

    task, command, mock_result = _inputs()
    assert "task_id" in task
    assert "task_id" in command
    assert "gateway_response" in mock_result
    assert "task_id" in mock_result["gateway_response"]


@pytest.mark.parametrize(
    "mutation",
    CASES,
    ids=lambda case: f"{case.owner}-{case.index:02d}",
)
def test_nested_identity_combinations_fail_closed(mutation: Mutation) -> None:
    task, command, mock_result = _inputs()
    bad_task_id = f"task-round7-mismatch-{mutation.index:02d}"

    if mutation.owner == "task":
        task["task_id"] = bad_task_id
    elif mutation.owner == "command_envelope":
        command["task_id"] = bad_task_id
    else:
        mock_result["gateway_response"]["task_id"] = bad_task_id

    output = None
    with pytest.raises(EvidenceBundleError, match="task_id.*match"):
        output = build_evidence_bundle(
            task,
            command,
            mock_result,
            [],
            created_at="2026-08-04T00:00:00Z",
        )
    assert output is None
