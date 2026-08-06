"""All-fake Phase 9 six-step rehearsal with tmp-path evidence persistence."""

from __future__ import annotations

import hashlib
import json
import threading
from datetime import timedelta
from pathlib import Path
from typing import Any

import pytest

from app import audit_writer_local
from app.blackboard_validators import validate_blackboard_message
from app.evidence_bundle_builder import verify_bundle_hash
from app.hash_chain import canonical_json, verify_chain
from app.phase9_audit_chain_writer import LocalAuditChainWriter
from app.phase9_burn_ledger import FileBurnLedger
from app.phase9_gate import (
    PHASE9_AUDIT_AUTHORIZATION_GRANT_SHA256,
    PHASE9_AUDIT_SCOPE,
    ActionRequest,
    GateDenied,
    GateRequest,
    GateState,
    Phase9AuditAuthorizationRecord,
    Phase9Gate,
)
from app.phase9_token import TokenPresentation, issue_token

from tests.test_full_chain_contract_rehearsal import _build_full_chain
from tests.test_phase9_gate import (
    NOW,
    Clock,
    CountingExecutor,
    DirectorySnapshotter,
    SameEndpointPresence,
    StaticAuditVerifier,
    StaticVerifier,
    StaticVersionProbe,
)


pytestmark = pytest.mark.contract

def _persist_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _gate(
    *,
    request: GateRequest,
    ledger: FileBurnLedger,
    audit_chain_writer: LocalAuditChainWriter,
    executor: CountingExecutor,
    state_root: Path,
) -> Phase9Gate:
    return Phase9Gate(
        rehearsal_id=request.issued_token.binding.rehearsal_id,
        contract_verifier=StaticVerifier(),
        preflight_verifier=StaticVerifier(),
        audit_authorization_verifier=StaticAuditVerifier(),
        burn_ledger=ledger,
        audit_chain_writer=audit_chain_writer,
        version_probe=StaticVersionProbe(),
        snapshotter=DirectorySnapshotter(state_root),
        presence_channel=SameEndpointPresence(),
        executor=executor,
        clock=Clock(),
        gate_token_audit_coordination_lock=threading.Lock(),
        challenge_bytes=lambda size: b"r" * size,
    )


def test_all_fake_six_step_rehearsal_persists_evidence_and_rejects_replay(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    rehearsal_root = tmp_path / "phase9-rehearsal"
    evidence_root = rehearsal_root / "evidence"
    audit_root = rehearsal_root / "repo"
    audit_target = audit_root / "data" / "audit_dev.jsonl"
    state_root = rehearsal_root / "openclaw-state"
    evidence_root.mkdir(parents=True)
    audit_target.parent.mkdir(parents=True)
    state_root.mkdir()
    (state_root / "config.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(audit_writer_local, "REPO_ROOT", audit_root)
    monkeypatch.setattr(audit_writer_local, "AUDIT_PATH", audit_target)

    messages, evidence_bundle = _build_full_chain()
    approval_packet = messages["approval_packet"]
    assert verify_bundle_hash(evidence_bundle) is True
    assert validate_blackboard_message(approval_packet, "approval_packet")["valid"]
    assert approval_packet["single_use_execution_token"] is None
    _persist_json(evidence_root / "01_evidence_bundle.json", evidence_bundle)
    _persist_json(evidence_root / "02_approval_packet.json", approval_packet)

    action = ActionRequest(
        action_name=approval_packet["exact_target"]["action_type"],
        target=approval_packet["exact_target"]["task_id"],
        message=approval_packet["exact_target"]["query_action"],
        requested_cli_timeout_seconds=approval_packet["timeout"],
        gate_timeout_seconds=12,
        agent_id="main",
        model_id="safe-model",
    )
    packet_hash = hashlib.sha256(canonical_json(approval_packet)).hexdigest()
    issued = issue_token(
        approval_packet_id=approval_packet["approval_packet_id"],
        approval_packet_hash=packet_hash,
        evidence_bundle_hash=evidence_bundle["bundle_hash"],
        action_hash=action.digest(),
        rehearsal_id="phase9-n1-all-fake-20260807",
        session_ends_at=NOW + timedelta(minutes=5),
        session_hmac_key=b"k" * 32,
        key_id="rehearsal-key",
        now=NOW,
        random_bytes=lambda size: b"z" * size,
    )
    raw_token = issued.reveal_for_oob_once()
    request = GateRequest(
        issued_token=issued,
        token_presentation=TokenPresentation.from_binding(issued.binding),
        action=action,
        system_display_strings=("System displays packet and action digests only.",),
        initial_challenge_id="phase9-initial-challenge",
        session_active=True,
        phase9_audit_authorization=Phase9AuditAuthorizationRecord(
            record_id="phase9-audit-owner-grant-rehearsal",
            rehearsal_id="phase9-n1-all-fake-20260807",
            scope=PHASE9_AUDIT_SCOPE,
            owner_instruction_digest=PHASE9_AUDIT_AUTHORIZATION_GRANT_SHA256,
            authorized_at=NOW - timedelta(seconds=1),
            valid_until=NOW + timedelta(minutes=3),
        ),
    )
    ledger = FileBurnLedger(rehearsal_root / "phase9_burn.jsonl")
    audit_chain_writer = LocalAuditChainWriter()
    fake_executor = CountingExecutor()
    gate = _gate(
        request=request,
        ledger=ledger,
        audit_chain_writer=audit_chain_writer,
        executor=fake_executor,
        state_root=state_root,
    )
    owner_text = (
        f"I authorize {action.action_name} for {action.target} in this rehearsal."
    )

    result = gate.run(
        request,
        presented_raw_token=raw_token,
        owner_authorization_text=owner_text,
    )
    execution_evidence = {
        "state": result.state.value,
        "completion_class": result.completion_class,
        "argv": list(result.argv),
        "exit_code": result.execution_result.exit_code,
        "timed_out": result.execution_result.timed_out,
        "stdout_digest": result.execution_result.stdout_digest,
        "stderr_digest": result.execution_result.stderr_digest,
        "controlled_fake_executor_calls": fake_executor.calls,
        "real_openclaw_call_count": 0,
    }
    _persist_json(evidence_root / "03_one_shot_execution.json", execution_evidence)

    audit_entries = audit_writer_local.read_audit_events()
    audit_evidence = {
        "receipt": {
            "event_id": result.audit_chain_receipt.event_id,
            "entry_hash": result.audit_chain_receipt.entry_hash,
            "chain_length": result.audit_chain_receipt.chain_length,
            "durable": result.audit_chain_receipt.durable,
            "verified": result.audit_chain_receipt.verified,
        },
        "entries": audit_entries,
    }
    _persist_json(evidence_root / "04_audit_chain.json", audit_evidence)

    post_verification = {
        "burn_present": ledger.contains(issued.binding.nonce_digest),
        "audit_chain_valid": verify_chain(audit_entries),
        "filesystem_before_digest": result.filesystem_before_digest,
        "filesystem_after_digest": result.filesystem_after_digest,
        "filesystem_changes": list(result.filesystem_changes),
        "retry_permitted": result.retry_permitted,
        "gate_closed": result.state is GateState.CLOSED_DENY,
    }
    _persist_json(evidence_root / "05_post_verification.json", post_verification)

    rollback = messages["rollback_preview"]
    assert validate_blackboard_message(rollback, "rollback_event")["valid"] is True
    assert rollback["rollback_required"] is False
    _persist_json(evidence_root / "06_rollback_preview.json", rollback)

    replay_gate = _gate(
        request=request,
        ledger=ledger,
        audit_chain_writer=audit_chain_writer,
        executor=fake_executor,
        state_root=state_root,
    )
    with pytest.raises(GateDenied, match="TOKEN_ALREADY_BURNED") as replay:
        replay_gate.run(
            request,
            presented_raw_token=raw_token,
            owner_authorization_text=owner_text,
        )

    assert replay.value.code == "TOKEN_ALREADY_BURNED"
    assert replay_gate.state is GateState.CLOSED_DENY
    assert fake_executor.test_double is True
    assert fake_executor.calls == 1
    assert execution_evidence["real_openclaw_call_count"] == 0
    assert len(audit_entries) == 1
    assert post_verification == {
        "burn_present": True,
        "audit_chain_valid": True,
        "filesystem_before_digest": result.filesystem_before_digest,
        "filesystem_after_digest": result.filesystem_after_digest,
        "filesystem_changes": [],
        "retry_permitted": False,
        "gate_closed": True,
    }
    persisted = sorted(path.name for path in evidence_root.glob("*.json"))
    assert persisted == [
        "01_evidence_bundle.json",
        "02_approval_packet.json",
        "03_one_shot_execution.json",
        "04_audit_chain.json",
        "05_post_verification.json",
        "06_rollback_preview.json",
    ]
    all_evidence = "".join(
        path.read_text(encoding="utf-8") for path in evidence_root.glob("*.json")
    )
    assert raw_token not in all_evidence
    assert audit_writer_local.AUDIT_PATH == audit_target
    assert audit_target.is_relative_to(tmp_path)
