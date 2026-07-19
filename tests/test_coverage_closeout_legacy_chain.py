"""Branch closeout for frozen, in-memory legacy advisory and mock-chain helpers."""

from __future__ import annotations

import copy
from types import SimpleNamespace

import pytest

from app import hermes_strategy_suggestion_model as strategy
from app import mock_e2e_v0_7 as mock_e2e
from app import mock_hermes_generator as mock_hermes
from app import mock_openclaw_gateway as mock_gateway
from app import security_gates_v0_7 as security
from app import worker_mock_gateway_dry_run as worker_gateway


def _context(**overrides: object) -> dict:
    value = {
        "task_id": "task-advice",
        "source_message_ids": ["message-1"],
        "source_result_ids": ["result-1"],
        "source_decision_ids": ["decision-1"],
        "strategy_summary": "inspect synthetic state",
        "recommended_action": "show preview",
        "risk_assessment": "low",
        "missing_information": [],
        "owner_question": "continue?",
        "suggested_next_step": "owner review",
        "confidence": 0.9,
    }
    value.update(overrides)
    return value


def _command(**overrides: object) -> dict:
    value = {
        "command_id": "command-mock",
        "task_id": "task-advice",
        "tool_target": "synthetic.status",
        "requested_action": "inspect one synthetic value",
        "risk_level": "low",
        "approval_snapshot": {"owner_review_required": True},
        "execution_mode": "mock_only",
        "dry_run": True,
        "mock_only": True,
        "external_touchpoints": [],
        "rollback_plan": "nothing executed",
        "external_side_effects_allowed": False,
    }
    value.update(overrides)
    return value


def _request(**overrides: object) -> dict:
    value = {
        "request_id": "request-e2e",
        "requested_by": "owner",
        "intent": "inspect",
        "goal": "inspect synthetic state",
        "task_type": "query",
        "risk_level": 0,
        "approval_required": False,
        "input_summary": "synthetic input",
        "target_runtime": "mock",
        "target_workspace": "local",
        "metadata": {"mock": True},
    }
    value.update(overrides)
    return value


def test_strategy_builder_validator_and_forced_safety() -> None:
    assert strategy.build_hermes_strategy_suggestion([])["accepted"] is False
    incomplete = _context()
    del incomplete["task_id"]
    assert strategy.build_hermes_strategy_suggestion(incomplete)["rejection_reason"].startswith("missing")

    source = _context(must_not_execute=False)
    snapshot = copy.deepcopy(source)
    suggestion = strategy.build_hermes_strategy_suggestion(source)
    assert suggestion["accepted"] is True
    assert suggestion["must_not_execute"] is True
    assert source == snapshot
    assert strategy.validate_hermes_strategy_suggestion(suggestion)["valid"] is True
    assert strategy.validate_hermes_strategy_suggestion([])["valid"] is False
    del suggestion["owner_question"]
    suggestion["openclaw_call_allowed"] = True
    validation = strategy.validate_hermes_strategy_suggestion(suggestion)
    assert validation["valid"] is False
    assert len(validation["violations"]) == 2


def test_mock_hermes_builder_rejection_passthrough_and_validator(monkeypatch) -> None:
    assert mock_hermes.build_mock_hermes_advice([])["accepted"] is False
    advice = mock_hermes.build_mock_hermes_advice(_context())
    assert advice["accepted"] is True
    assert advice["real_hermes_called"] is False
    assert mock_hermes.validate_mock_hermes_advice(advice)["valid"] is True
    assert mock_hermes.validate_mock_hermes_advice([])["valid"] is False
    del advice["owner_question"]
    advice["queue_write_allowed"] = True
    assert len(mock_hermes.validate_mock_hermes_advice(advice)["violations"]) == 2

    fake = SimpleNamespace(
        build_hermes_strategy_suggestion=lambda _source: {
            "accepted": False,
            "rejection_reason": None,
            "rejection_details": ["synthetic"],
        }
    )
    monkeypatch.setattr(mock_hermes, "_load_suggestion_model_module", lambda: fake)
    rejected = mock_hermes.build_mock_hermes_advice(_context())
    assert rejected["rejection_reason"] == "underlying strategy suggestion rejected"
    assert rejected["task_id"] == "task-advice"


@pytest.mark.parametrize(
    ("changes", "reason"),
    [
        ({"mock_only": False}, "unsafe command envelope flags"),
        ({"dry_run": False}, "unsafe command envelope flags"),
        ({"external_side_effects_allowed": True}, "unsafe command envelope flags"),
        ({"dispatch_allowed": True}, "unsafe command envelope flags"),
    ],
)
def test_mock_gateway_rejects_unsafe_flags(changes, reason) -> None:
    response = mock_gateway.build_mock_openclaw_response(_command(**changes))
    assert response["accepted"] is False
    assert response["rejection_reason"] == reason
    assert response["real_openclaw_called"] is False


def test_mock_gateway_shape_missing_and_success() -> None:
    assert mock_gateway.build_mock_openclaw_response([])["rejection_reason"].startswith("command_envelope")
    incomplete = _command()
    del incomplete["task_id"]
    assert mock_gateway.build_mock_openclaw_response(incomplete)["rejection_reason"].startswith("missing")
    source = _command()
    snapshot = copy.deepcopy(source)
    response = mock_gateway.build_mock_openclaw_response(source)
    assert response["accepted"] is True
    assert response["command_id"] == "command-mock"
    assert source == snapshot


def test_worker_mock_gateway_shape_flags_and_gateway_rejection(monkeypatch) -> None:
    assert worker_gateway.run_worker_to_mock_gateway_dry_run([])["accepted"] is False
    assert worker_gateway.run_worker_to_mock_gateway_dry_run(_command(worker_allowed=True))["accepted"] is False

    accepted = worker_gateway.run_worker_to_mock_gateway_dry_run(_command())
    assert accepted["accepted"] is True
    assert accepted["mock_gateway_called"] is True
    assert accepted["worker_loop_started"] is False

    fake = SimpleNamespace(
        build_mock_openclaw_response=lambda _source: {
            "accepted": False,
            "rejection_reason": "synthetic rejection",
        }
    )
    monkeypatch.setattr(worker_gateway, "_load_mock_gateway_module", lambda: fake)
    rejected = worker_gateway.run_worker_to_mock_gateway_dry_run(_command())
    assert rejected["accepted"] is False
    assert rejected["rejection_details"] == []


def test_in_memory_mock_queue_edges() -> None:
    queue = mock_e2e.InMemoryMockQueue()
    with pytest.raises(mock_e2e.MockE2EError):
        queue.enqueue({})
    assert queue.claim_next() is None
    queue.enqueue({"task_id": "review", "status": "pending_approval"})
    assert queue.claim_next() is None
    queue.enqueue({"task_id": "queued", "status": "queued"})
    claimed = queue.claim_next()
    assert claimed["status"] == "running"
    assert queue.get_task("queued")["status"] == "running"
    assert queue.get_task("missing") is None
    with pytest.raises(mock_e2e.MockE2EError):
        queue.mark_completed("missing", {})
    assert queue.mark_completed("queued", {"event_id": "e-1"})["status"] == "completed"
    assert queue.mark_failed("queued", {"event_id": "e-2"})["status"] == "failed"


def test_mock_worker_callback_paths_and_input_guards() -> None:
    with pytest.raises(mock_e2e.MockE2EError):
        mock_e2e.mock_worker_process_task([])
    completed = mock_e2e.mock_worker_process_task({"task_id": "task-e2e", "task_type": "query"})
    failed = mock_e2e.mock_worker_process_task({"task_id": "task-e2e", "task_type": "mock.fail"})
    assert completed["status"] == "completed"
    assert failed["status"] == "failed" and failed["retryable"] is True
    with pytest.raises(mock_e2e.MockE2EError):
        mock_e2e.apply_callback_to_mock_task([], completed)
    with pytest.raises(mock_e2e.MockE2EError):
        mock_e2e.apply_callback_to_mock_task({}, [])


def test_mock_e2e_frozen_dry_run_paths() -> None:
    stopped = mock_e2e.run_mock_e2e_dry_run(_request(approval_required=True))
    assert stopped["stopped_at"] == "approval_gate"
    assert stopped["callback_event"] is None

    completed = mock_e2e.run_mock_e2e_dry_run(_request())
    assert completed["final_status"] == "completed"
    failed = mock_e2e.run_mock_e2e_dry_run(_request(task_type="mock.fail"))
    assert failed["final_status"] == "failed"


def test_mock_e2e_unexpected_status_and_empty_claim_fail_closed(monkeypatch) -> None:
    monkeypatch.setattr(
        mock_e2e,
        "prepare_queue_candidate_from_mock_request",
        lambda _request: {
            "task_id": "task-bad",
            "status": "draft",
            "approval_required": False,
            "approval_status": "not_required",
        },
    )
    monkeypatch.setattr(mock_e2e, "validate_task_envelope", lambda _candidate: None)
    with pytest.raises(mock_e2e.MockE2EError, match="status"):
        mock_e2e.run_mock_e2e_dry_run({})

    monkeypatch.setattr(
        mock_e2e,
        "prepare_queue_candidate_from_mock_request",
        lambda _request: {
            "task_id": "task-empty",
            "status": "queued",
            "approval_required": False,
            "approval_status": "not_required",
        },
    )
    monkeypatch.setattr(mock_e2e.InMemoryMockQueue, "claim_next", lambda _self: None)
    with pytest.raises(mock_e2e.MockE2EError, match="claim_next"):
        mock_e2e.run_mock_e2e_dry_run({})


@pytest.mark.parametrize(
    ("global_switch", "layer_switch", "reason"),
    [
        (True, False, "global_kill_switch_active"),
        (None, False, "global_kill_switch_unknown"),
        (False, True, "layer_kill_switch_active"),
        (False, None, "layer_kill_switch_unknown"),
        (False, False, "kill_switch_clear"),
    ],
)
def test_security_kill_switch_precedence(global_switch, layer_switch, reason) -> None:
    result = security.evaluate_kill_switch(
        global_kill_switch=global_switch, layer_kill_switch=layer_switch
    )
    assert result["reason"] == reason


@pytest.mark.parametrize(
    ("requested", "allowed", "denied", "reason"),
    [
        (None, ["read"], [], "requested_tools_empty"),
        (["bad tool"], ["bad tool"], [], "invalid_tool_name"),
        (["read"], ["read"], ["read"], "denied_tool_matched"),
        (["read"], [], [], "allowed_tools_empty"),
        (["write"], ["read"], [], "tool_not_in_allowlist"),
        (["read"], ["read"], [], "all_tools_allowed"),
    ],
)
def test_security_tool_gate_matrix(requested, allowed, denied, reason) -> None:
    result = security.evaluate_tool_allowlist(
        requested_tools=requested, allowed_tools=allowed, denied_tools=denied
    )
    assert result["reason"] == reason


def test_security_combined_gate_redaction_and_audit() -> None:
    assert security.evaluate_security_gates(
        requested_tools=["read"], allowed_tools=["read"], denied_tools=[],
        global_kill_switch=True, layer_kill_switch=False,
    )["allowed"] is False
    assert security.evaluate_security_gates(
        requested_tools=["read"], allowed_tools=["read"], denied_tools=[],
        global_kill_switch=False, layer_kill_switch=False,
    )["allowed"] is True

    assert security.redact_audit_metadata(None) == {}
    redacted = security.redact_audit_metadata(
        {
            "access_token": "value",
            "nested": {"password": "value"},
            "items": ["ya29.abcdefghijklmnop", "safe"],
            "private": "-----BEGIN PRIVATE KEY-----",
            "safe": 7,
        }
    )
    assert redacted["access_token"] == security.REDACTED
    assert redacted["nested"]["password"] == security.REDACTED
    assert redacted["items"][0] == security.REDACTED
    assert redacted["safe"] == 7
    assert security._mask_actor_id(None) is None
    event = security.build_audit_event(
        action="synthetic.observe", actor_id="owner", metadata={"secret": "value"}
    )
    assert event["actor_id_masked"].startswith("actor-")
    assert event["metadata_redacted"]["secret"] == security.REDACTED
    assert event["observation_only"] is True
