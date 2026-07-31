"""Contract error messages must not echo synthetic secret or path payloads."""

from __future__ import annotations

import copy
import ast
import json
import os
from pathlib import Path
import subprocess
import sys
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
TEST_HELPER_REPORT_MARKER = "FAKE-SECRET-NB17-TEST-HELPER"


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


def test_fixture_loader_success_does_not_write_payload_to_captured_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    fixture = tmp_path / "synthetic.json"
    fixture.write_text(
        json.dumps(
            {"marker": TEST_HELPER_REPORT_MARKER, "path": ABSOLUTE_PATH},
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    monkeypatch.setitem(_load.__globals__, "ROOT", tmp_path)

    loaded = _load(fixture.name)

    captured = capsys.readouterr()
    assert loaded["marker"] == TEST_HELPER_REPORT_MARKER
    assert TEST_HELPER_REPORT_MARKER not in captured.out + captured.err
    assert ABSOLUTE_PATH not in captured.out + captured.err


def test_fixture_loader_helpers_have_no_direct_output_calls() -> None:
    """Fixture readers may return data, but must not print or log it themselves."""

    output_calls: list[tuple[str, str, str]] = []
    loader_count = 0
    for source_path in sorted((ROOT / "tests").glob("test_*.py")):
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            calls = [child for child in ast.walk(node) if isinstance(child, ast.Call)]
            call_names = {
                child.func.attr
                if isinstance(child.func, ast.Attribute)
                else child.func.id
                if isinstance(child.func, ast.Name)
                else ""
                for child in calls
            }
            if "read_text" not in call_names or "loads" not in call_names:
                continue
            loader_count += 1
            for child in calls:
                if isinstance(child.func, ast.Name) and child.func.id == "print":
                    output_calls.append((source_path.name, node.name, "print"))
                if (
                    isinstance(child.func, ast.Attribute)
                    and isinstance(child.func.value, ast.Name)
                    and child.func.value.id in {"logging", "logger", "sys"}
                    and child.func.attr
                    in {"debug", "info", "warning", "error", "exception", "stdout", "stderr"}
                ):
                    output_calls.append(
                        (source_path.name, node.name, child.func.attr)
                    )

    assert loader_count >= 20
    assert output_calls == []


@pytest.mark.parametrize("probe_case", ("malformed_payload", "missing_path"))
def test_fixture_loader_pytest_report_leak_baseline_is_explicit(
    tmp_path: Path, probe_case: str
) -> None:
    """Lock the known local-only report leak without adding another xfail."""

    fixture_root = tmp_path / "fixtures"
    fixture_root.mkdir()
    if probe_case == "malformed_payload":
        fixture_name = "hostile.json"
        (fixture_root / fixture_name).write_text(
            json.dumps([TEST_HELPER_REPORT_MARKER, ABSOLUTE_PATH]),
            encoding="utf-8",
        )
    else:
        fixture_name = f"{TEST_HELPER_REPORT_MARKER}.json"

    probe = tmp_path / "test_fixture_loader_report_probe.py"
    probe.write_text(
        "from pathlib import Path\n"
        "import json\n"
        "import os\n"
        "ROOT = Path(os.environ['NB17_FIXTURE_ROOT'])\n\n"
        "def loader(path):\n"
        "    value = json.loads((ROOT / path).read_text(encoding='utf-8'))\n"
        "    assert isinstance(value, dict)\n"
        "    return value\n\n"
        "def test_probe():\n"
        "    loader(os.environ['NB17_FIXTURE_NAME'])\n",
        encoding="utf-8",
    )
    environment = os.environ.copy()
    environment.update(
        {
            "NB17_FIXTURE_ROOT": str(fixture_root),
            "NB17_FIXTURE_NAME": fixture_name,
        }
    )

    completed = subprocess.run(
        [sys.executable, "-m", "pytest", "-p", "no:cacheprovider", "-q", str(probe)],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    report = completed.stdout + completed.stderr

    assert completed.returncode == 1
    assert TEST_HELPER_REPORT_MARKER in report
    if probe_case == "malformed_payload":
        assert ABSOLUTE_PATH.replace("\\", "\\\\") in report
