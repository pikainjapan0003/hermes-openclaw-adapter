"""Round-four deterministic mutations for identity, hash, and version boundaries."""

from __future__ import annotations

import copy
import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator

from app.approval_packet_builder import ApprovalPacketBuildError, build_approval_packet
from app.blackboard_validators import validate_blackboard_message
from app.evidence_bundle_builder import (
    EvidenceBundleError,
    build_evidence_bundle,
    verify_bundle_hash,
)
from app.worker_mock_gateway_dry_run import run_worker_to_mock_gateway_dry_run


pytestmark = pytest.mark.fuzz

ROOT = Path(__file__).resolve().parents[1]
BLACKBOARD = ROOT / "fixtures" / "blackboard_contract"
EVIDENCE_SCHEMA = ROOT / "docs" / "schemas" / "evidence_bundle.json"
SEED = 20260801
CASES_PER_MODULE = 30


@dataclass(frozen=True)
class Mutation:
    kind: str
    index: int


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _fixture(message_type: str) -> dict[str, Any]:
    return _load(BLACKBOARD / f"{message_type}.valid.json")


def _cases() -> tuple[Mutation, ...]:
    cases = [
        Mutation(kind, index)
        for kind in ("id", "hash", "version")
        for index in range(1, CASES_PER_MODULE + 1)
    ]
    random.Random(SEED).shuffle(cases)
    return tuple(cases)


CASES = _cases()


def _evidence_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    task = _fixture("task_draft")
    command = {
        "command_id": "cmd-round4-001",
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


def _validate_evidence(bundle: dict[str, Any]) -> bool:
    schema = _load(EVIDENCE_SCHEMA)
    return not list(Draft202012Validator(schema).iter_errors(bundle))


def test_round4_inventory_is_seeded_and_balanced() -> None:
    assert len(CASES) == 90
    assert {kind: sum(case.kind == kind for case in CASES) for kind in ("id", "hash", "version")} == {
        "id": 30,
        "hash": 30,
        "version": 30,
    }
    assert SEED == 20260801


@pytest.mark.parametrize("mutation", CASES, ids=lambda case: f"{case.kind}-{case.index:02d}")
def test_blackboard_identity_hash_version_mutations_fail_closed(mutation: Mutation) -> None:
    packet = _fixture("approval_packet")
    if mutation.kind == "id":
        packet["task_id"] = None
    elif mutation.kind == "hash":
        packet["prev_entry_hash"] = "not-a-sha256"
    else:
        # The current contract permits forward-compatible version strings;
        # use a wrong type so this mutation is unambiguously invalid.
        packet["schema_version"] = None

    result = validate_blackboard_message(packet, "approval_packet")
    assert result["valid"] is False
    assert result["errors"]


@pytest.mark.parametrize("mutation", CASES, ids=lambda case: f"{case.kind}-{case.index:02d}")
def test_approval_builder_identity_hash_version_mutations_fail_closed(
    mutation: Mutation,
) -> None:
    worker = _fixture("worker_dry_run")
    result = _fixture("result_message")
    if mutation.kind == "id":
        worker["task_id"] = None
    elif mutation.kind == "hash":
        with pytest.raises(ApprovalPacketBuildError):
            build_approval_packet(worker, result, prev_entry_hash="not-a-sha256")
        return
    else:
        result["schema_version"] = "9.9"

    with pytest.raises(ApprovalPacketBuildError):
        build_approval_packet(worker, result)


@pytest.mark.parametrize("mutation", CASES, ids=lambda case: f"{case.kind}-{case.index:02d}")
def test_evidence_bundle_identity_hash_version_mutations_fail_closed(
    mutation: Mutation,
) -> None:
    task, command, mock_result = _evidence_inputs()
    if mutation.kind == "id":
        command["task_id"] = None
        with pytest.raises(EvidenceBundleError):
            build_evidence_bundle(task, command, mock_result, [], created_at="2026-08-01T00:00:00Z")
        return

    bundle = build_evidence_bundle(
        task,
        command,
        mock_result,
        [],
        created_at="2026-08-01T00:00:00Z",
    )
    if mutation.kind == "hash":
        bundle["mock_result"]["accepted"] = False
    else:
        bundle["schema_version"] = "9.9"

    assert verify_bundle_hash(bundle) is False
    assert _validate_evidence(bundle) is False


def test_round4_does_not_mutate_source_fixture_inputs() -> None:
    task, command, mock_result = _evidence_inputs()
    before = copy.deepcopy((task, command, mock_result))
    build_evidence_bundle(task, command, mock_result, [], created_at="2026-08-01T00:00:00Z")
    assert (task, command, mock_result) == before
