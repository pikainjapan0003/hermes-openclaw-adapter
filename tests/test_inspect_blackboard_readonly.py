"""Tests for the stdout-only Blackboard directory inspector."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from scripts import inspect_blackboard_readonly as inspector


ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "fixtures" / "blackboard_contract"


def _fixture(message_type: str) -> dict[str, object]:
    return json.loads(
        (FIXTURES / f"{message_type}.valid.json").read_text(encoding="utf-8")
    )


def _put(board: Path, sequence: int, message_type: str, message: dict[str, object]) -> None:
    (board / f"{sequence:04d}_{message_type}.json").write_text(
        json.dumps(message, ensure_ascii=False), encoding="utf-8"
    )


def test_inspector_counts_types_and_reports_only_identifier_links(tmp_path: Path) -> None:
    _put(tmp_path, 1, "task_draft", _fixture("task_draft"))
    _put(tmp_path, 2, "annotation", _fixture("annotation"))

    summary = inspector.inspect_board(tmp_path)

    assert summary["valid"] is True
    assert summary["message_type_counts"] == {"annotation": 1, "task_draft": 1}
    assert summary["validation"] == {
        "passed": ["0001_task_draft.json", "0002_annotation.json"],
        "failed": [],
        "errors": [],
    }
    task_link, annotation_link = summary["id_chain"]
    assert task_link["identifiers"] == {
        "parent_task_id": None,
        "task_id": "task-phase3-001",
    }
    assert annotation_link["identifiers"]["annotation_id"] == "annotation-phase3-001"
    rendered = json.dumps(summary)
    assert "Prepare a harmless" not in rendered
    assert "safety_flags" not in rendered


def test_inspector_lists_good_and_bad_files_without_echoing_bad_payload(tmp_path: Path) -> None:
    _put(tmp_path, 1, "task_draft", _fixture("task_draft"))
    invalid = deepcopy(_fixture("annotation"))
    invalid.pop("role")
    invalid["private_payload"] = "must-not-be-echoed"
    _put(tmp_path, 2, "annotation", invalid)

    summary = inspector.inspect_board(tmp_path)

    assert summary["valid"] is False
    assert summary["message_type_counts"] == {"annotation": 1, "task_draft": 1}
    assert summary["validation"]["passed"] == ["0001_task_draft.json"]
    assert summary["validation"]["failed"] == ["0002_annotation.json"]
    assert summary["validation"]["errors"] == [
        {"filename": "0002_annotation.json", "code": "schema_rejected"}
    ]
    assert "must-not-be-echoed" not in json.dumps(summary)


def test_inspector_reports_malformed_file_and_main_uses_stdout(
    tmp_path: Path, capsys
) -> None:
    (tmp_path / "0001_task_draft.json").write_text("{truncated", encoding="utf-8")

    assert inspector.main([str(tmp_path)]) == 1
    captured = capsys.readouterr()
    output = json.loads(captured.out)
    assert captured.err == ""
    assert output["validation"]["failed"] == ["0001_task_draft.json"]
    assert output["validation"]["errors"] == [
        {"filename": "0001_task_draft.json", "code": "json_read_failed"}
    ]


def test_inspector_accepts_an_empty_existing_board(tmp_path: Path) -> None:
    summary = inspector.inspect_board(tmp_path)
    assert summary["valid"] is True
    assert summary["entry_count"] == 0
    assert summary["message_type_counts"] == {}
    assert summary["id_chain"] == []
