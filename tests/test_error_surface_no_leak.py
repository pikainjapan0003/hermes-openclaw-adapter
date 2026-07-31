"""Contract error messages must not echo synthetic secret or path payloads."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Callable

import pytest

from app.approval_packet_builder import ApprovalPacketBuildError, build_approval_packet
from app.blackboard_validators import validate_blackboard_message
from app.evidence_bundle_builder import SensitiveEvidenceError, build_evidence_bundle
from app.hash_chain import HashChainError, canonical_json
from app.remote_readonly_projection import (
    CANONICAL_SAFETY_FLAG_KEYS,
    RemoteReadonlyProjectionError,
    build_remote_readonly_projection,
)
from app.rollback_preview_builder import RollbackPreviewBuildError, build_rollback_preview
from app.worker_mock_gateway_dry_run import run_worker_to_mock_gateway_dry_run


ROOT = Path(__file__).resolve().parent.parent
SECRET = "FAKE-SECRET-20260723"
ABSOLUTE_PATH = r"C:\Users\Owner\private\payload.txt"


def _load(path: str) -> dict:
    value = json.loads((ROOT / path).read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _assert_redacted(call: Callable[[], object], error_type: type[Exception]) -> None:
    with pytest.raises(error_type) as caught:
        call()
    message = str(caught.value)
    assert SECRET not in message
    assert ABSOLUTE_PATH not in message


def test_approval_builder_error_omits_payload_markers() -> None:
    worker = _load("fixtures/blackboard_contract/worker_dry_run.valid.json")
    result = _load("fixtures/blackboard_contract/result_message.valid.json")
    worker["safety_flags"]["synthetic_local_only"] = SECRET
    worker["private_path"] = ABSOLUTE_PATH
    _assert_redacted(
        lambda: build_approval_packet(worker, result),
        ApprovalPacketBuildError,
    )


def test_evidence_builder_error_omits_payload_markers() -> None:
    task = _load("fixtures/blackboard_contract/task_draft.valid.json")
    command = {
        "command_id": "cmd-error-surface",
        "task_id": task["task_id"],
        "tool_target": "synthetic.adapter.status",
        "requested_action": "read one synthetic adapter status value",
        "risk_level": "low",
        "approval_snapshot": {"owner_review_required": True},
        "execution_mode": "mock_only",
        "dry_run": True,
        "mock_only": True,
        "external_touchpoints": [],
        "rollback_plan": "no rollback required",
        "external_side_effects_allowed": False,
    }
    mock_result = run_worker_to_mock_gateway_dry_run(command)
    mock_result["api_token"] = SECRET
    mock_result["private_path"] = ABSOLUTE_PATH
    _assert_redacted(
        lambda: build_evidence_bundle(
            task, command, mock_result, [], created_at="2026-07-23T00:00:00Z"
        ),
        SensitiveEvidenceError,
    )


def test_rollback_builder_error_omits_payload_markers() -> None:
    audit = _load("fixtures/blackboard_contract/audit_event.valid.json")
    evidence = _load("fixtures/local_mock_data/n1_dry_run_evidence_bundle.json")
    result = _load("fixtures/blackboard_contract/result_message.valid.json")
    audit["message_type"] = SECRET
    audit["private_path"] = ABSOLUTE_PATH
    _assert_redacted(
        lambda: build_rollback_preview(audit, evidence, result),
        RollbackPreviewBuildError,
    )


def test_projection_builder_error_omits_payload_markers() -> None:
    flags = {key: False for key in CANONICAL_SAFETY_FLAG_KEYS}
    source = {
        "task_id": SECRET,
        "parent_task_id": ABSOLUTE_PATH,
        "phase": SECRET,
        "status": "ready",
        "execution_class": "OWNER_APPROVAL",
        "safety_flags": flags,
        "approval_readiness": "ready_for_owner",
        "decision": None,
        "decision_timestamp": None,
        "evidence_bundle_hash": "0" * 64,
    }
    _assert_redacted(
        lambda: build_remote_readonly_projection(
            source,
            data_generated_at="2026-07-23T00:00:00Z",
            source_commit_sha="0" * 40,
            stale_after="2026-07-23T00:15:00Z",
        ),
        RemoteReadonlyProjectionError,
    )


def test_selection_and_canonicalization_errors_omit_unrelated_payload() -> None:
    selection = validate_blackboard_message(
        {"sensitive_note": SECRET, "private_path": ABSOLUTE_PATH}
    )
    serialized = json.dumps(selection, ensure_ascii=False)
    assert selection["valid"] is False
    assert SECRET not in serialized
    assert ABSOLUTE_PATH not in serialized

    hostile = {"safe": copy.deepcopy([SECRET, ABSOLUTE_PATH]), "bad": 1.5}
    _assert_redacted(lambda: canonical_json(hostile), HashChainError)
