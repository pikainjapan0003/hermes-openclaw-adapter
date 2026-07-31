"""Determinism at large, deep, Unicode, and maximum timestamp boundaries."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from app.approval_packet_builder import build_approval_packet
from app.blackboard_validators import validate_blackboard_message
from app.evidence_bundle_builder import build_evidence_bundle, verify_bundle_hash
from app.worker_mock_gateway_dry_run import run_worker_to_mock_gateway_dry_run


pytestmark = pytest.mark.contract

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures" / "blackboard_contract"
BOUNDARY_TEXT_LENGTH = 65_536
BOUNDARY_DEPTH = 100
MAX_TIMESTAMP = "9999-12-31T23:59:59.999999Z"
UNICODE_FRAGMENT = "界🚀e\u0301\u200d"


def _fixture(message_type: str) -> dict[str, Any]:
    value = json.loads(
        (FIXTURES / f"{message_type}.valid.json").read_text(encoding="utf-8")
    )
    assert isinstance(value, dict)
    return value


def _long_text() -> str:
    repeats = (BOUNDARY_TEXT_LENGTH // len(UNICODE_FRAGMENT)) + 1
    value = (UNICODE_FRAGMENT * repeats)[:BOUNDARY_TEXT_LENGTH]
    assert len(value) == BOUNDARY_TEXT_LENGTH
    return value


def _deep_benign_value() -> dict[str, Any]:
    root: dict[str, Any] = {}
    cursor = root
    for depth in range(BOUNDARY_DEPTH):
        child: dict[str, Any] = {"depth": depth}
        cursor["layer"] = child
        cursor = child
    cursor["value"] = "synthetic-local-boundary"
    return root


def _independent_hash(value: dict[str, Any], *, omit: str | None = None) -> str:
    payload = {key: item for key, item in value.items() if key != omit}
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _command(task_id: str, boundary_text: str) -> dict[str, Any]:
    return {
        "command_id": "cmd-extreme-n1-001",
        "task_id": task_id,
        "tool_target": "synthetic.adapter.status",
        "requested_action": boundary_text,
        "risk_level": "low",
        "approval_snapshot": {
            "owner_review_required": True,
            "benign_depth_probe": _deep_benign_value(),
        },
        "execution_mode": "mock_only",
        "dry_run": True,
        "mock_only": True,
        "external_touchpoints": [],
        "rollback_plan": boundary_text,
        "external_side_effects_allowed": False,
    }


def test_approval_packet_is_deterministic_at_extreme_accepted_boundaries() -> None:
    boundary_text = _long_text()
    worker = _fixture("worker_dry_run")
    result = _fixture("result_message")
    worker["proposed_worker_action"] = boundary_text
    worker["benign_depth_probe"] = _deep_benign_value()
    result["rollback_note"] = boundary_text
    result["audit_note"] = boundary_text
    result["created_at"] = MAX_TIMESTAMP
    before = copy.deepcopy((worker, result))

    first = build_approval_packet(
        worker,
        result,
        decision="respond",
        approval_timestamp=MAX_TIMESTAMP,
        prev_entry_hash="f" * 64,
    )
    second = build_approval_packet(
        worker,
        result,
        decision="respond",
        approval_timestamp=MAX_TIMESTAMP,
        prev_entry_hash="f" * 64,
    )

    assert first == second
    assert (worker, result) == before
    assert len(first["action_summary"]) == BOUNDARY_TEXT_LENGTH
    assert first["created_at"] == first["approval_timestamp"] == MAX_TIMESTAMP
    assert first["single_use_execution_token"] is None
    assert validate_blackboard_message(first, "approval_packet")["valid"] is True
    assert _independent_hash(first) == _independent_hash(second)


def test_evidence_bundle_hash_is_independently_recomputable_at_extremes() -> None:
    boundary_text = _long_text()
    task = _fixture("task_draft")
    task["title"] = boundary_text
    task["summary"] = boundary_text
    task["benign_depth_probe"] = _deep_benign_value()
    command = _command(task["task_id"], boundary_text)
    mock_result = run_worker_to_mock_gateway_dry_run(command)
    mock_result["benign_depth_probe"] = _deep_benign_value()
    mock_result["gateway_response"]["mock_response_summary"] = boundary_text
    before = copy.deepcopy((task, command, mock_result))

    first = build_evidence_bundle(
        task, command, mock_result, [], created_at=MAX_TIMESTAMP
    )
    second = build_evidence_bundle(
        task, command, mock_result, [], created_at=MAX_TIMESTAMP
    )

    assert first == second
    assert (task, command, mock_result) == before
    assert first["created_at"] == MAX_TIMESTAMP
    assert len(first["task"]["title"]) == BOUNDARY_TEXT_LENGTH
    assert verify_bundle_hash(first) is True
    assert first["bundle_hash"] == _independent_hash(first, omit="bundle_hash")
