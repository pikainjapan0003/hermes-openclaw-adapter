"""Close the remaining fail-closed branches in three read-only legacy modules."""

from __future__ import annotations

from pathlib import Path

import pytest

from app import blackboard_board_reader as board_reader
from app import dashboard_intake_view_v0_7 as intake
from app import queue_task_annotation_v0_7 as annotation


pytestmark = pytest.mark.legacy


def test_intake_non_payload_and_absent_risk_remain_unknown() -> None:
    assert intake._as_payload_dict(None) == {}
    assert intake._derive_risk_level({}, {}, {}) is None

    view = intake.derive_intake_status_view(
        {
            "task_id": "task-no-risk",
            "status": "custom",
            "payload": None,
        }
    )
    assert view["risk_level"] is None
    assert all(not badge.startswith("risk:") for badge in view["display_badges"])


def test_board_reader_rejects_symlink_before_reading_target(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    entry = tmp_path / "0001_task_draft.json"
    entry.write_text("must-not-be-read", encoding="utf-8")
    original_is_symlink = Path.is_symlink
    original_read_text = Path.read_text

    def synthetic_is_symlink(path: Path) -> bool:
        if path == entry:
            return True
        return original_is_symlink(path)

    def forbidden_read(path: Path, *args: object, **kwargs: object) -> str:
        if path == entry:
            raise AssertionError("reader followed a rejected synthetic symlink")
        return original_read_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "is_symlink", synthetic_is_symlink)
    monkeypatch.setattr(Path, "read_text", forbidden_read)

    result = board_reader.read_blackboard_board(tmp_path)
    assert result["valid"] is False
    assert result["entry_count"] == 0
    assert result["errors"] == [
        {
            "filename": "0001_task_draft.json",
            "code": "symlink_rejected",
            "message": "symlinks are not read",
        }
    ]


@pytest.mark.parametrize(
    ("metadata", "expected"),
    [
        ({"approval_readiness": "prohibited"}, "prohibited"),
        ({"approval_readiness": "blocked_by_policy"}, "blocked_by_policy"),
    ],
)
def test_annotation_direct_restrictive_readiness_precedes_other_signals(
    metadata: dict[str, object],
    expected: str,
) -> None:
    metadata.update(
        {
            "policy_decision": "ready_for_owner_decision",
            "approval_status": "ready_for_owner_decision",
        }
    )
    view = annotation.derive_queue_task_annotation(
        {
            "status": "queued",
            "payload": {"metadata": metadata},
        }
    )

    assert view["approval_readiness"] == expected
    assert view["approval_blockers"] == [expected]
    assert view["execution_permission"] is False
    assert view["dispatch_allowed"] is False

