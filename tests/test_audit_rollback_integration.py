"""In-memory rollback preview integration with a real local audit ledger."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest

import app.audit_writer_local as writer
from app.blackboard_validators import validate_blackboard_message
from app.evidence_bundle_builder import build_evidence_bundle
from app.rollback_preview_builder import build_rollback_preview
from app.worker_mock_gateway_dry_run import run_worker_to_mock_gateway_dry_run


pytestmark = pytest.mark.contract

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "fixtures" / "blackboard_contract"


def _fixture(name: str) -> dict[str, Any]:
    value = json.loads((FIXTURES / f"{name}.valid.json").read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _sandbox(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    target = repo / "data" / "audit_dev.jsonl"
    target.parent.mkdir(parents=True)
    monkeypatch.setattr(writer, "REPO_ROOT", repo)
    monkeypatch.setattr(writer, "AUDIT_PATH", target)
    return target


def _evidence_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    task = _fixture("task_draft")
    envelope = _fixture("openclaw_command_envelope")
    command = {
        "command_id": envelope["command_id"],
        "task_id": task["task_id"],
        "tool_target": "synthetic.adapter.status",
        "requested_action": envelope["input_summary"],
        "risk_level": "low",
        "approval_snapshot": {"owner_review_required": True},
        "execution_mode": "mock_only",
        "dry_run": True,
        "mock_only": True,
        "external_touchpoints": [],
        "rollback_plan": "No rollback is required; nothing is executed.",
        "external_side_effects_allowed": False,
    }
    mock_result = run_worker_to_mock_gateway_dry_run(command)
    bundle = build_evidence_bundle(
        task,
        command,
        mock_result,
        [],
        created_at="2026-08-03T00:00:00Z",
    )
    return task, bundle, _fixture("result_message")


def test_real_audit_file_last_event_feeds_preview_only_builder(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    target = _sandbox(monkeypatch, tmp_path)
    task, bundle, result = _evidence_inputs()
    audit = _fixture("audit_event")
    audit["prev_entry_hash"] = None
    audit["task_id"] = task["task_id"]
    audit["related_result_id"] = result["result_id"]
    audit["audit_id"] = "audit-real-file-001"
    audit["event_id"] = "audit-real-file-event-001"

    writer.append_audit_event(audit)
    loaded = writer.read_audit_events()
    assert target.exists()
    assert len(loaded) == 1
    last_event = loaded[-1]
    preview = build_rollback_preview(last_event, bundle, result)

    validation = validate_blackboard_message(preview, "rollback_event")
    assert validation["valid"] is True, validation
    assert preview["preview_only"] is True
    assert preview["rollback_required"] is False
    assert preview["source_audit_id"] == audit["audit_id"]


def test_reader_does_not_mutate_the_audit_event_or_execute_anything(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _sandbox(monkeypatch, tmp_path)
    _, bundle, result = _evidence_inputs()
    audit = _fixture("audit_event")
    audit["prev_entry_hash"] = None
    before = copy.deepcopy(audit)
    writer.append_audit_event(audit)
    loaded = writer.read_audit_events()
    assert loaded[0] == before
    preview = build_rollback_preview(loaded[0], bundle, result)
    assert "command" not in json.dumps(preview).lower()
