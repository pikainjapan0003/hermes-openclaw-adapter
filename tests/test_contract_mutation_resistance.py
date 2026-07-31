"""Deterministic cross-field mutation resistance for the six contract modules."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest

from app.approval_packet_builder import ApprovalPacketBuildError, build_approval_packet
from app.blackboard_validators import validate_blackboard_message
from app.evidence_bundle_builder import EvidenceBundleError, build_evidence_bundle
from app.hash_chain import entry_hash, verify_chain
from app.remote_readonly_projection import (
    CANONICAL_SAFETY_FLAG_KEYS,
    RemoteReadonlyProjectionError,
    build_remote_readonly_projection,
)
from app.rollback_preview_builder import (
    RollbackPreviewBuildError,
    build_rollback_preview,
)
from app.worker_mock_gateway_dry_run import run_worker_to_mock_gateway_dry_run


pytestmark = pytest.mark.fuzz

ROOT = Path(__file__).resolve().parent.parent
BLACKBOARD = ROOT / "fixtures" / "blackboard_contract"
LOCAL_MOCK = ROOT / "fixtures" / "local_mock_data"
SEED = 20260727
CASES_PER_MODULE = 40


def _json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _fixture(message_type: str) -> dict[str, Any]:
    return _json(BLACKBOARD / f"{message_type}.valid.json")


def _safe_projection_source() -> dict[str, Any]:
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
    return {
        "task_id": "task-mutation",
        "parent_task_id": "parent-mutation",
        "phase": "approval_ready",
        "status": "ready",
        "execution_class": "OWNER_APPROVAL",
        "safety_flags": flags,
        "approval_readiness": "ready_for_owner",
        "decision": None,
        "decision_timestamp": None,
        "evidence_bundle_hash": "9" * 64,
    }


def _evidence_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    task = _fixture("task_draft")
    command = {
        "command_id": "cmd-mutation",
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


@pytest.mark.parametrize("case", range(CASES_PER_MODULE))
def test_blackboard_validator_rejects_cross_contract_mutations(case: int) -> None:
    packet = _fixture("approval_packet")
    kind = case % 5
    if kind == 0:
        packet["single_use_execution_token"] = f"mutated-{SEED}-{case}"
    elif kind == 1:
        packet["message_type"] = "result_message"
    elif kind == 2:
        packet["safety_flags"].pop("mock_only")
    elif kind == 3:
        packet["safety_flags"][f"extra_{case}"] = False
    else:
        packet.pop("parent_task_id")

    result = validate_blackboard_message(packet, "approval_packet")
    assert result["valid"] is False
    assert result["errors"]
    assert all({"path", "validator", "message"} <= set(error) for error in result["errors"])


@pytest.mark.parametrize("case", range(CASES_PER_MODULE))
def test_approval_builder_rejects_cross_source_mutations(case: int) -> None:
    worker = _fixture("worker_dry_run")
    result = _fixture("result_message")
    kind = case % 5
    if kind == 0:
        result["schema_version"] = f"mutated-{case}"
    elif kind == 1:
        result["parent_task_id"] = f"parent-mutated-{case}"
    elif kind == 2:
        result["task_id"] = f"task-mutated-{case}"
    elif kind == 3:
        result["related_dry_run_id"] = f"dry-mutated-{case}"
    else:
        result["safety_flags"].pop("mock_only")

    with pytest.raises(ApprovalPacketBuildError) as captured:
        build_approval_packet(worker, result)
    assert str(captured.value)


@pytest.mark.parametrize("case", range(CASES_PER_MODULE))
def test_evidence_builder_rejects_cross_source_mutations(case: int) -> None:
    task, command, mock_result = _evidence_inputs()
    kind = case % 5
    if kind == 0:
        command["task_id"] = f"task-mutated-{case}"
    elif kind == 1:
        task["execution_class"] = "OWNER_APPROVAL"
    elif kind == 2:
        command["external_touchpoints"] = [f"touchpoint-{case}"]
    elif kind == 3:
        mock_result["gateway_response"]["command_id"] = f"cmd-mutated-{case}"
    else:
        task["target_runtime"] = "real-runtime"

    with pytest.raises(EvidenceBundleError) as captured:
        build_evidence_bundle(
            task,
            command,
            mock_result,
            [],
            created_at="2026-07-27T00:00:00Z",
        )
    assert str(captured.value)


@pytest.mark.parametrize("case", range(CASES_PER_MODULE))
def test_projection_builder_rejects_cross_field_mutations(case: int) -> None:
    source = _safe_projection_source()
    kind = case % 5
    if kind == 0:
        source["status"] = "decided"
    elif kind == 1:
        source["decision_timestamp"] = "2026-07-27T00:00:00Z"
    elif kind == 2:
        source["safety_flags"].pop("mock_only")
    elif kind == 3:
        source["evidence_bundle_hash"] = f"bad-{case}"
    else:
        source[f"extra_{case}"] = "forbidden"

    with pytest.raises(RemoteReadonlyProjectionError) as captured:
        build_remote_readonly_projection(
            source,
            data_generated_at="2026-07-27T00:00:00Z",
            source_commit_sha="a" * 40,
            stale_after="2026-07-27T00:15:00Z",
        )
    assert str(captured.value)


@pytest.mark.parametrize("case", range(CASES_PER_MODULE))
def test_hash_chain_rejects_cross_entry_mutations(case: int) -> None:
    genesis = _fixture("audit_event")
    genesis["prev_entry_hash"] = None
    second = copy.deepcopy(genesis)
    second["audit_id"] = f"audit-second-{case}"
    second["event_id"] = f"event-second-{case}"
    second["prev_entry_hash"] = entry_hash(genesis)
    third = copy.deepcopy(second)
    third["audit_id"] = f"audit-third-{case}"
    third["event_id"] = f"event-third-{case}"
    third["prev_entry_hash"] = entry_hash(second)
    chain = [genesis, second, third]

    kind = case % 5
    if kind == 0:
        chain[0]["prev_entry_hash"] = "0" * 64
    elif kind == 1:
        chain[1]["prev_entry_hash"] = None
    elif kind == 2:
        chain[1]["event_notes"] = f"tampered-{case}"
    elif kind == 3:
        chain[2]["prev_entry_hash"] = "f" * 64
    else:
        chain[1]["non_json"] = 1.5
    assert verify_chain(chain) is False


@pytest.mark.parametrize("case", range(CASES_PER_MODULE))
def test_rollback_builder_rejects_cross_source_mutations(case: int) -> None:
    audit = _fixture("audit_event")
    bundle = _json(LOCAL_MOCK / "n1_dry_run_evidence_bundle.json")
    result = _fixture("result_message")
    kind = case % 5
    if kind == 0:
        result["schema_version"] = f"mutated-{case}"
    elif kind == 1:
        result["parent_task_id"] = f"parent-mutated-{case}"
    elif kind == 2:
        result["task_id"] = f"task-mutated-{case}"
    elif kind == 3:
        result["result_id"] = f"result-mutated-{case}"
    else:
        result["safety_flags"].pop("mock_only")

    with pytest.raises(RollbackPreviewBuildError) as captured:
        build_rollback_preview(audit, bundle, result)
    assert str(captured.value)
