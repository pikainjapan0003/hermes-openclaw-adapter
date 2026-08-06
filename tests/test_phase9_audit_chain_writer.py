"""Concrete Phase 9 audit-chain writer tests using an isolated tmp ledger."""

from __future__ import annotations

import ast
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest

from app import audit_writer_local
from app.hash_chain import entry_hash, verify_chain
from app.phase9_audit_chain_writer import (
    LocalAuditChainWriter,
    Phase9AuditChainWriterError,
)
from app.phase9_gate import AuditChainReceipt, BurnRecord


pytestmark = pytest.mark.contract


def _point_writer_at_tmp(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    repository = tmp_path / "repo"
    target = repository / "data" / "audit_dev.jsonl"
    target.parent.mkdir(parents=True)
    monkeypatch.setattr(audit_writer_local, "REPO_ROOT", repository)
    monkeypatch.setattr(audit_writer_local, "AUDIT_PATH", target)
    return target


def _burn_record(index: int = 1) -> BurnRecord:
    digit = str(index % 10)
    return BurnRecord(
        rehearsal_id=f"rehearsal-phase9-{index:03d}",
        approval_packet_hash=digit * 64,
        action_hash=f"{(index + 1) % 10}" * 64,
        token_digest=f"{(index + 2) % 10}" * 64,
        binding_hash=f"{(index + 3) % 10}" * 64,
        burned_at=datetime(2026, 8, 7, 9, index, tzinfo=timezone.utc),
        attempt_number=1,
        owner_presence_demonstrated=True,
        owner_verbatim_authorization_verified=True,
        owner_instruction_digest=f"{(index + 4) % 10}" * 64,
        authorization_record_id=f"owner-audit-auth-{index:03d}",
    )


def test_writer_appends_real_phase7_entries_and_reports_verified_chain(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    target = _point_writer_at_tmp(monkeypatch, tmp_path)
    writer = LocalAuditChainWriter()

    first = writer.append_burn_evidence(_burn_record(1))
    second = writer.append_burn_evidence(_burn_record(2))

    entries = audit_writer_local.read_audit_events()
    assert len(entries) == 2
    assert entries[0]["prev_entry_hash"] is None
    assert entries[1]["prev_entry_hash"] == entry_hash(entries[0])
    assert verify_chain(entries) is True
    assert first == AuditChainReceipt(
        event_id=entries[0]["event_id"],
        entry_hash=entry_hash(entries[0]),
        chain_length=1,
        durable=True,
        verified=True,
    )
    assert second == AuditChainReceipt(
        event_id=entries[1]["event_id"],
        entry_hash=entry_hash(entries[1]),
        chain_length=2,
        durable=True,
        verified=True,
    )
    raw = target.read_text(encoding="utf-8")
    assert _burn_record(1).token_digest not in raw
    assert _burn_record(1).binding_hash not in raw
    assert "\r" not in raw
    assert raw.endswith("\n")


def test_writer_rejects_non_verified_or_inconsistent_append_receipt(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _point_writer_at_tmp(monkeypatch, tmp_path)
    real_append = audit_writer_local.append_audit_event

    def unverified_append(event: dict[str, Any]) -> dict[str, Any]:
        result = real_append(event)
        return {**result, "verified": False}

    monkeypatch.setattr(audit_writer_local, "append_audit_event", unverified_append)

    with pytest.raises(
        Phase9AuditChainWriterError,
        match="append receipt is invalid",
    ):
        LocalAuditChainWriter().append_burn_evidence(_burn_record(1))


def test_writer_rejects_invalid_record_before_append(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    target = _point_writer_at_tmp(monkeypatch, tmp_path)
    invalid = replace(_burn_record(1), token_digest="not-a-digest")

    with pytest.raises(Phase9AuditChainWriterError, match="token_digest"):
        LocalAuditChainWriter().append_burn_evidence(invalid)

    assert not target.exists()


def test_writer_source_has_one_explicit_phase7_persistence_dependency() -> None:
    source_path = (
        Path(__file__).parents[1] / "app" / "phase9_audit_chain_writer.py"
    )
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    names = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }

    string_constants = {
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    }

    assert "app.audit_writer_local" in string_constants
    assert "importlib" in names
    assert not {"subprocess", "socket"} & names


def test_gate_source_checks_audit_hash_type_before_length() -> None:
    source_path = Path(__file__).parents[1] / "app" / "phase9_gate.py"
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    source = source_path.read_text(encoding="utf-8")

    assert isinstance(tree, ast.Module)
    type_check = "isinstance(\n                                        audit_chain_receipt.entry_hash, str"
    assert type_check in source
    assert source.index(type_check) < source.index(
        "len(audit_chain_receipt.entry_hash)"
    )
