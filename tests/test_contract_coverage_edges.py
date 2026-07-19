"""Fail-closed edge coverage for the six pure contract modules."""

from __future__ import annotations

import copy
import json
import unicodedata
from pathlib import Path
from typing import Any, Callable
from unittest.mock import mock_open

import pytest

import app.approval_packet_builder as approval
import app.blackboard_validators as blackboard
import app.evidence_bundle_builder as evidence
import app.hash_chain as hash_chain
import app.remote_readonly_projection as remote
import app.rollback_preview_builder as rollback
from app.worker_mock_gateway_dry_run import run_worker_to_mock_gateway_dry_run


ROOT = Path(__file__).resolve().parent.parent
BLACKBOARD_FIXTURES = ROOT / "fixtures" / "blackboard_contract"
EVIDENCE_FIXTURE = (
    ROOT / "fixtures" / "local_mock_data" / "n1_dry_run_evidence_bundle.json"
)
REMOTE_SCHEMA = ROOT / "docs" / "schemas" / "remote_readonly_projection.schema.json"


def _json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _approval_sources() -> tuple[dict[str, Any], dict[str, Any]]:
    return (
        _json(BLACKBOARD_FIXTURES / "worker_dry_run.valid.json"),
        _json(BLACKBOARD_FIXTURES / "result_message.valid.json"),
    )


def _build_approval(
    worker: Any,
    result: Any,
    **kwargs: Any,
) -> dict[str, Any]:
    return approval.build_approval_packet(worker, result, **kwargs)


@pytest.mark.parametrize(
    "mutation,kwargs,error",
    (
        (lambda w, r: ([], r), {}, "worker_dry_run must be an object"),
        (lambda w, r: (w, []), {}, "result_message must be an object"),
        (lambda w, r: ({**w, "message_type": "bad"}, r), {}, "message_type"),
        (lambda w, r: (w, {**r, "message_type": "bad"}), {}, "message_type"),
        (lambda w, r: (w, r), {"decision": "run"}, "decision"),
        (lambda w, r: (w, r), {"approval_timestamp": ""}, "approval_timestamp"),
        (lambda w, r: (w, r), {"approval_timestamp": 1}, "approval_timestamp"),
        (lambda w, r: (w, r), {"prev_entry_hash": 1}, "prev_entry_hash"),
        (lambda w, r: (w, r), {"prev_entry_hash": "bad"}, "prev_entry_hash"),
        (
            lambda w, r: ({**w, "schema_version": "2.0"}, r),
            {},
            "schema_version",
        ),
        (
            lambda w, r: ({**w, "execution_class": "OWNER_APPROVAL"}, r),
            {},
            "must use AUTO",
        ),
        (lambda w, r: (w, {**r, "task_id": "other"}), {}, "task_id"),
        (
            lambda w, r: (w, {**r, "parent_task_id": "other"}),
            {},
            "parent_task_id",
        ),
        (lambda w, r: ({**w, "preview_only": False}, r), {}, "preview_only"),
        (
            lambda w, r: ({**w, "dry_run_status": "executed"}, r),
            {},
            "must not be executed",
        ),
        (
            lambda w, r: (w, {**r, "result_status": "executed"}),
            {},
            "unexecuted preview",
        ),
        (
            lambda w, r: (w, {**r, "execution_mode": "live"}),
            {},
            "mock_only",
        ),
    ),
)
def test_approval_builder_fail_closed_edges(
    mutation: Callable[[dict[str, Any], dict[str, Any]], tuple[Any, Any]],
    kwargs: dict[str, Any],
    error: str,
) -> None:
    worker, result = _approval_sources()
    worker, result = mutation(worker, result)
    with pytest.raises(approval.ApprovalPacketBuildError, match=error):
        _build_approval(worker, result, **kwargs)


def test_approval_private_guards_reject_bad_nested_values() -> None:
    with pytest.raises(approval.ApprovalPacketBuildError, match="must be an object"):
        approval._mapping({"nested": []}, "nested")
    with pytest.raises(approval.ApprovalPacketBuildError, match="non-empty"):
        approval._text({}, "missing")
    with pytest.raises(approval.ApprovalPacketBuildError, match="values must be false"):
        approval._require_false_flags({"flags": {"flag": True}}, "flags", {"flag"})


def _evidence_sources() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    task = _json(BLACKBOARD_FIXTURES / "task_draft.valid.json")
    command = {
        "command_id": "cmd-evidence-n1-001",
        "task_id": task["task_id"],
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
    return task, command, run_worker_to_mock_gateway_dry_run(command)


def _build_evidence(
    task: Any,
    command: Any,
    mock_result: Any,
    expected: Any = (),
    created_at: Any = "2026-07-19T18:00:00Z",
) -> dict[str, Any]:
    return evidence.build_evidence_bundle(
        task,
        command,
        mock_result,
        expected,
        created_at=created_at,
    )


@pytest.mark.parametrize(
    "target,field,value,error",
    (
        ("task", "task_type", "write", "task_type"),
        ("task", "target_runtime", "live", "target_runtime"),
        ("task", "execution_class", "OWNER_APPROVAL", "execution_class"),
        ("command", "task_id", "other", "task_id must match"),
        ("command", "risk_level", "high", "risk_level"),
        ("command", "execution_mode", "live", "execution_mode"),
        ("command", "dry_run", False, "dry_run"),
        ("command", "mock_only", False, "mock_only"),
        ("command", "external_touchpoints", ["remote"], "external_touchpoints"),
        (
            "command",
            "external_side_effects_allowed",
            True,
            "external_side_effects_allowed",
        ),
        ("mock", "source", "live", "mock_result.source"),
        ("mock", "accepted", False, "mock_result.accepted"),
        ("mock", "worker_dry_run", False, "worker_dry_run"),
        ("mock", "mock_gateway_called", False, "mock_gateway_called"),
        ("gateway", "response_source", "live", "response_source"),
        ("gateway", "accepted", False, "gateway_response.accepted"),
        ("gateway", "mock_gateway", False, "mock_gateway must be true"),
        ("gateway", "task_id", "other", "task_id must match"),
        ("gateway", "command_id", "other", "command_id must match"),
        ("gateway", "tool_target", "other", "tool_target must match"),
        (
            "approval",
            "owner_review_required",
            False,
            "owner_review_required must be true",
        ),
    ),
)
def test_evidence_builder_fail_closed_field_matrix(
    target: str, field: str, value: Any, error: str
) -> None:
    task, command, mock_result = _evidence_sources()
    records = {
        "task": task,
        "command": command,
        "mock": mock_result,
        "gateway": mock_result["gateway_response"],
        "approval": command["approval_snapshot"],
    }
    records[target][field] = value
    with pytest.raises(evidence.EvidenceBundleError, match=error):
        _build_evidence(task, command, mock_result)


@pytest.mark.parametrize(
    "task,command,mock_result,expected,created,error",
    (
        ([], {}, {}, [], "now", "task must be an object"),
        ({}, [], {}, [], "now", "command_envelope must be an object"),
        ({}, {}, [], [], "now", "mock_result must be an object"),
        ({}, {}, {}, [], "now", "gateway_response must be an object"),
    ),
)
def test_evidence_builder_rejects_bad_top_level_shapes(
    task: Any,
    command: Any,
    mock_result: Any,
    expected: Any,
    created: Any,
    error: str,
) -> None:
    with pytest.raises(evidence.EvidenceBundleError, match=error):
        _build_evidence(task, command, mock_result, expected, created)


def test_evidence_builder_rejects_empty_created_at() -> None:
    task, command, mock_result = _evidence_sources()
    with pytest.raises(evidence.EvidenceBundleError, match="created_at"):
        _build_evidence(task, command, mock_result, [], "")


def test_evidence_hash_and_sensitive_value_edges() -> None:
    assert evidence.verify_bundle_hash([]) is False
    assert evidence.verify_bundle_hash({"bundle_hash": "short"}) is False
    with pytest.raises(evidence.EvidenceBundleError, match="bundle must be an object"):
        evidence.compute_bundle_hash([])
    with pytest.raises(evidence.SensitiveEvidenceError):
        evidence._scan_sensitive(["https://example.invalid"], "$")

    task, command, mock_result = _evidence_sources()
    with pytest.raises(evidence.EvidenceBundleError, match="must be an array"):
        _build_evidence(task, command, mock_result, "not-an-array")
    with pytest.raises(evidence.EvidenceBundleError, match="must be empty"):
        _build_evidence(task, command, mock_result, ["write"])


def _remote_source() -> dict[str, Any]:
    flags = {key: False for key in remote.CANONICAL_SAFETY_FLAG_KEYS}
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
        "task_id": "task-n1",
        "parent_task_id": "parent-n1",
        "phase": "approval_ready",
        "status": "ready",
        "execution_class": "OWNER_APPROVAL",
        "safety_flags": flags,
        "approval_readiness": "ready_for_owner",
        "decision": None,
        "decision_timestamp": None,
        "evidence_bundle_hash": "a" * 64,
    }


def _build_remote(source: Any, **kwargs: Any) -> dict[str, Any]:
    defaults = {
        "data_generated_at": "2026-07-19T02:00:00Z",
        "source_commit_sha": "a" * 40,
        "stale_after": "2026-07-19T02:15:00Z",
    }
    defaults.update(kwargs)
    return remote.build_remote_readonly_projection(source, **defaults)


@pytest.mark.parametrize(
    "field,value,error",
    (
        ("phase", "unknown", "phase is outside"),
        ("status", "unknown", "status is outside"),
        ("execution_class", "unknown", "execution_class is invalid"),
        ("approval_readiness", "unknown", "approval_readiness is invalid"),
        ("evidence_bundle_hash", "bad", "evidence_bundle_hash"),
    ),
)
def test_remote_projection_enum_and_hash_guards(
    field: str, value: Any, error: str
) -> None:
    source = _remote_source()
    source[field] = value
    with pytest.raises(remote.RemoteReadonlyProjectionError, match=error):
        _build_remote(source)


def test_remote_projection_shape_timestamp_decision_and_schema_edges() -> None:
    with pytest.raises(remote.RemoteReadonlyProjectionError, match="source must be"):
        _build_remote([])
    with pytest.raises(remote.RemoteReadonlyProjectionError, match="ending in Z"):
        _build_remote(_remote_source(), data_generated_at="2026-07-19")
    with pytest.raises(remote.RemoteReadonlyProjectionError, match="ISO-8601"):
        _build_remote(_remote_source(), data_generated_at="not-a-dateZ")
    with pytest.raises(remote.RemoteReadonlyProjectionError, match="source_commit_sha"):
        _build_remote(_remote_source(), source_commit_sha="bad")

    source = _remote_source()
    source["safety_flags"] = []
    with pytest.raises(remote.RemoteReadonlyProjectionError, match="must be an object"):
        _build_remote(source)
    source = _remote_source()
    source["safety_flags"]["mock_only"] = 1
    with pytest.raises(remote.RemoteReadonlyProjectionError, match="must be booleans"):
        _build_remote(source)

    source = _remote_source()
    source.update({"status": "decided", "phase": "approval_ready"})
    with pytest.raises(remote.RemoteReadonlyProjectionError, match="owner_decided phase"):
        _build_remote(source)
    source.update({"phase": "owner_decided", "decision": "launch"})
    with pytest.raises(remote.RemoteReadonlyProjectionError, match="valid decision"):
        _build_remote(source)

    schema = _json(REMOTE_SCHEMA)
    assert remote.validate_remote_readonly_projection([], schema)["valid"] is False
    assert remote.validate_remote_readonly_projection({}, [])["valid"] is False
    leaked = {"items": ["https://example.invalid"]}
    errors = remote._projection_leaks(leaked)
    assert errors[0]["path"] == "$.items[0]"


def test_hash_chain_remaining_domain_and_sequence_edges(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    hash_chain._validate_value([None, True, 1, "ok"])
    with pytest.raises(hash_chain.HashChainError, match="key is not Unicode NFC"):
        hash_chain._validate_value({unicodedata.normalize("NFD", "café"): 1})
    with pytest.raises(hash_chain.HashChainError, match="root must be an object"):
        hash_chain.canonical_json([])

    def bad_dumps(*args: Any, **kwargs: Any) -> str:
        del args, kwargs
        raise TypeError("synthetic encoding failure")

    monkeypatch.setattr(hash_chain.json, "dumps", bad_dumps)
    with pytest.raises(hash_chain.HashChainError, match="encoding failed"):
        hash_chain.canonical_json({"ok": True})
    monkeypatch.undo()

    assert hash_chain.verify_chain("bad") is False
    assert hash_chain.verify_chain([{}]) is True
    assert hash_chain.verify_chain([{}, []]) is False
    assert hash_chain.verify_chain([{"prev_entry_hash": None, "bad": 1.5}]) is False


def _rollback_sources() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    return (
        _json(BLACKBOARD_FIXTURES / "audit_event.valid.json"),
        _json(EVIDENCE_FIXTURE),
        _json(BLACKBOARD_FIXTURES / "result_message.valid.json"),
    )


@pytest.mark.parametrize(
    "mutation,error",
    (
        (lambda a, b, r: ([], b, r), "audit_event must be an object"),
        (lambda a, b, r: (a, [], r), "evidence_bundle must be an object"),
        (lambda a, b, r: (a, b, []), "result_message must be an object"),
        (lambda a, b, r: ({**a, "message_type": "bad"}, b, r), "message_type"),
        (lambda a, b, r: (a, {**b, "bundle_type": "bad"}, r), "bundle_type"),
        (lambda a, b, r: (a, b, {**r, "message_type": "bad"}), "message_type"),
        (lambda a, b, r: ({**a, "persistence_target": "disk"}, b, r), "persistence_target"),
        (lambda a, b, r: (a, b, {**r, "result_status": "executed"}), "result_status"),
        (lambda a, b, r: (a, b, {**r, "execution_mode": "live"}), "execution_mode"),
        (lambda a, b, r: ({**a, "schema_version": "2.0"}, b, r), "schema_version"),
        (lambda a, b, r: (a, b, {**r, "parent_task_id": "other"}), "parent_task_id"),
    ),
)
def test_rollback_builder_fail_closed_edges(
    mutation: Callable[[dict[str, Any], dict[str, Any], dict[str, Any]], tuple[Any, Any, Any]],
    error: str,
) -> None:
    audit, bundle, result = _rollback_sources()
    audit, bundle, result = mutation(audit, bundle, result)
    with pytest.raises(rollback.RollbackPreviewBuildError, match=error):
        rollback.build_rollback_preview(audit, bundle, result)


def test_rollback_private_nested_guards() -> None:
    with pytest.raises(rollback.RollbackPreviewBuildError, match="must be an object"):
        rollback._mapping({"nested": []}, "nested", "owner")
    with pytest.raises(rollback.RollbackPreviewBuildError, match="non-empty text"):
        rollback._text({}, "missing", "owner")
    with pytest.raises(rollback.RollbackPreviewBuildError, match="parent_task_id"):
        rollback._parent_task_id({"parent_task_id": ""}, "owner")


def test_blackboard_loader_and_path_fail_closed_edges(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert blackboard._json_path(["items", 0, "name"]) == "$.items[0].name"
    with pytest.raises(blackboard.BlackboardSchemaError, match="unknown"):
        blackboard.load_blackboard_schema("not_registered")

    monkeypatch.setitem(blackboard.SCHEMA_FILES, "edge", "edge.schema.json")
    blackboard.load_blackboard_schema.cache_clear()
    blackboard._validator_for.cache_clear()
    monkeypatch.setattr(Path, "open", mock_open(read_data="{"))
    with pytest.raises(blackboard.BlackboardSchemaError, match="failed to load"):
        blackboard.load_blackboard_schema("edge")

    blackboard.load_blackboard_schema.cache_clear()
    monkeypatch.setattr(blackboard.json, "load", lambda handle: [])
    with pytest.raises(blackboard.BlackboardSchemaError, match="root must be"):
        blackboard.load_blackboard_schema("edge")

    blackboard.load_blackboard_schema.cache_clear()
    monkeypatch.setattr(blackboard.json, "load", lambda handle: {"type": "invalid"})
    with pytest.raises(blackboard.BlackboardSchemaError, match="invalid Blackboard"):
        blackboard.load_blackboard_schema("edge")

    result = blackboard.validate_blackboard_message({})
    assert result["errors"][0]["path"] == "$.message_type"
    blackboard.load_blackboard_schema.cache_clear()
    blackboard._validator_for.cache_clear()
