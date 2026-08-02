"""Unit and refusal tests for the authorized local audit writer."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest

import app.audit_writer_local as writer
from app.hash_chain import entry_hash, verify_chain


pytestmark = pytest.mark.contract


ROOT = Path(__file__).resolve().parent.parent
FIXTURE = ROOT / "fixtures" / "blackboard_contract" / "audit_event.valid.json"


def _event(index: int, previous: str | None = None) -> dict[str, Any]:
    event = json.loads(FIXTURE.read_text(encoding="utf-8"))
    event["prev_entry_hash"] = previous
    event["audit_id"] = f"audit-local-{index}"
    event["event_id"] = f"audit-local-event-{index}"
    event["task_id"] = "task-local-n1"
    event["related_result_id"] = "result-local-n1"
    event["event_notes"] = f"Synthetic local preview event {index}; no execution."
    return event


def _sandbox(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    data = repo / "data"
    data.mkdir(parents=True)
    target = data / "audit_dev.jsonl"
    monkeypatch.setattr(writer, "REPO_ROOT", repo)
    monkeypatch.setattr(writer, "AUDIT_PATH", target)
    return target


def test_empty_file_genesis_then_two_linked_appends_verify(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    target = _sandbox(monkeypatch, tmp_path)

    first_result = writer.append_audit_event(_event(1))
    second_result = writer.append_audit_event(_event(2, first_result["entry_hash"]))
    writer.append_audit_event(_event(3, second_result["entry_hash"]))

    entries = writer.read_audit_events()
    assert len(entries) == 3
    assert entries[0]["prev_entry_hash"] is None
    assert entries[1]["prev_entry_hash"] == entry_hash(entries[0])
    assert entries[2]["prev_entry_hash"] == entry_hash(entries[1])
    assert verify_chain(entries) is True
    raw = target.read_bytes()
    assert raw.endswith(b"\n")
    assert b"\r\n" not in raw
    assert first_result["verified"] is True
    assert second_result["chain_length"] == 2


def test_tampered_middle_event_is_rejected_and_reports_first_break(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    target = _sandbox(monkeypatch, tmp_path)
    first = writer.append_audit_event(_event(1))
    second = writer.append_audit_event(_event(2, first["entry_hash"]))
    writer.append_audit_event(_event(3, second["entry_hash"]))
    original = target.read_bytes()

    rows = [json.loads(line) for line in original.decode("utf-8").splitlines()]
    rows[1]["event_notes"] = "Tampered middle record"
    target.write_bytes(
        b"".join(
            json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
            + b"\n"
            for row in rows
        )
    )
    tampered = target.read_bytes()
    with pytest.raises(writer.AuditWriterError) as error:
        writer.read_audit_events()
    assert error.value.entry_index == 2
    parsed = [json.loads(line) for line in tampered.decode("utf-8").splitlines()]
    assert verify_chain(parsed) is False
    assert target.read_bytes() == tampered
    assert original != tampered


def test_hardlink_target_is_rejected_without_changing_bytes(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    target = _sandbox(monkeypatch, tmp_path)
    first = writer.append_audit_event(_event(1))
    alias = target.with_name("audit-alias.jsonl")
    try:
        alias.hardlink_to(target)
    except (OSError, NotImplementedError) as exc:
        pytest.skip(f"hardlinks unavailable: {exc}")
    before = target.read_bytes()
    with pytest.raises(writer.AuditWriterError, match="shared inode"):
        writer.append_audit_event(_event(2, first["entry_hash"]))
    assert target.read_bytes() == before


def test_wrong_predecessor_is_rejected_before_any_bytes_change(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    target = _sandbox(monkeypatch, tmp_path)
    writer.append_audit_event(_event(1))
    before = target.read_bytes()
    with pytest.raises(writer.AuditWriterError, match="predecessor"):
        writer.append_audit_event(_event(2, "0" * 64))
    assert target.read_bytes() == before


def test_non_schema_event_is_rejected_without_creating_target(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    target = _sandbox(monkeypatch, tmp_path)
    invalid = _event(1)
    del invalid["event_notes"]
    with pytest.raises(writer.AuditWriterError, match="schema"):
        writer.append_audit_event(invalid)
    assert not target.exists()


def test_symlink_target_escape_is_rejected(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    target = _sandbox(monkeypatch, tmp_path)
    outside = tmp_path / "outside.jsonl"
    try:
        target.symlink_to(outside)
    except (OSError, NotImplementedError) as exc:
        pytest.skip(f"symlinks unavailable: {exc}")
    with pytest.raises(writer.AuditWriterError, match="indirect"):
        writer.append_audit_event(_event(1))
    assert not outside.exists()


def test_noncanonical_target_escape_is_rejected(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _sandbox(monkeypatch, tmp_path)
    outside = tmp_path / "outside.jsonl"
    monkeypatch.setattr(writer, "AUDIT_PATH", outside)
    with pytest.raises(writer.AuditWriterError, match="outside"):
        writer.append_audit_event(_event(1))
    assert not outside.exists()


def test_existing_crlf_is_rejected_without_normalization(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    target = _sandbox(monkeypatch, tmp_path)
    target.write_bytes(b'{"not":"an audit event"}\r\n')
    before = target.read_bytes()
    with pytest.raises(writer.AuditWriterError, match="line endings"):
        writer.read_audit_events()
    assert target.read_bytes() == before


def test_input_mapping_is_not_mutated(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _sandbox(monkeypatch, tmp_path)
    event = _event(1)
    before = copy.deepcopy(event)
    writer.append_audit_event(event)
    assert event == before
