"""Malicious-path boundaries for the read-only Blackboard board reader."""

from __future__ import annotations

import json
import os
import socket
import stat
from pathlib import Path

import pytest

from app.blackboard_board_reader import read_blackboard_board


pytestmark = pytest.mark.fuzz

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures" / "blackboard_contract"


def _fixture(message_type: str) -> dict[str, object]:
    value = json.loads(
        (FIXTURES / f"{message_type}.valid.json").read_text(encoding="utf-8")
    )
    assert isinstance(value, dict)
    return value


def test_reader_rejects_symlink_without_reading_outside_board(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    outside_marker = "OUTSIDE-BOARD-SECRET-MUST-NOT-BE-READ"
    outside = tmp_path.parent / f"{tmp_path.name}-outside.json"
    outside.write_text(outside_marker, encoding="utf-8")
    link = tmp_path / "0001_task_draft.json"
    try:
        link.symlink_to(outside)
    except OSError as exc:
        pytest.skip(f"platform cannot create test symlink: {type(exc).__name__}")

    original_read_text = Path.read_text
    read_paths: list[Path] = []

    def recording_read_text(path: Path, *args: object, **kwargs: object) -> str:
        read_paths.append(path.resolve())
        return original_read_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", recording_read_text)
    result = read_blackboard_board(tmp_path)

    assert result["valid"] is False
    assert result["entries"] == []
    assert result["errors"] == [
        {
            "filename": link.name,
            "code": "symlink_rejected",
            "message": "symlinks are not read",
        }
    ]
    assert read_paths == []
    assert outside.read_text(encoding="utf-8") == outside_marker
    assert outside_marker not in json.dumps(result, ensure_ascii=False)


def test_reader_accepts_a_caller_selected_root_symlink(tmp_path: Path) -> None:
    real_root = tmp_path / "real-board"
    real_root.mkdir()
    (real_root / "0001_task_draft.json").write_text(
        json.dumps(_fixture("task_draft"), ensure_ascii=False, sort_keys=True),
        encoding="utf-8",
    )
    selected_root = tmp_path / "selected-board"
    try:
        selected_root.symlink_to(real_root, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"platform cannot create root symlink: {type(exc).__name__}")

    result = read_blackboard_board(selected_root)

    assert selected_root.resolve() == real_root.resolve()
    assert result["valid"] is True
    assert result["board_name"] == selected_root.name
    assert result["entry_count"] == 1
    assert result["errors"] == []


def test_reader_rejects_relative_parent_escape_symlink(tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    marker = "RELATIVE-PARENT-ESCAPE-MUST-NOT-BE-READ"
    (outside / "payload.json").write_text(marker, encoding="utf-8")
    board = tmp_path / "board"
    board.mkdir()
    link = board / "0001_task_draft.json"
    try:
        link.symlink_to(Path("..") / "outside" / "payload.json")
    except OSError as exc:
        pytest.skip(f"platform cannot create relative symlink: {type(exc).__name__}")

    result = read_blackboard_board(board)

    assert link.resolve() == (outside / "payload.json").resolve()
    assert result["valid"] is False
    assert result["entries"] == []
    assert result["errors"][0]["code"] == "symlink_rejected"
    assert marker not in json.dumps(result, ensure_ascii=False)


def test_reader_structurally_rejects_hostile_entry_shapes(tmp_path: Path) -> None:
    # Long enough to stress the contract filename matcher while remaining
    # creatable under Windows' legacy aggregate path limit.
    long_name = ("x" * 96) + ".json"
    (tmp_path / long_name).write_text("long filename payload", encoding="utf-8")
    (tmp_path / "0001-task_draft.json").write_text(
        "illegal contract filename payload", encoding="utf-8"
    )
    (tmp_path / ".hidden.json").write_text("hidden payload", encoding="utf-8")
    (tmp_path / "nested").mkdir()
    (tmp_path / "nested" / "0001_task_draft.json").write_text(
        "nested payload must not be read", encoding="utf-8"
    )
    (tmp_path / "0002_task_draft.json").write_bytes(b"")
    bom_payload = json.dumps(
        _fixture("annotation"), ensure_ascii=False, sort_keys=True
    ).encode("utf-8-sig")
    (tmp_path / "0003_annotation.json").write_bytes(bom_payload)

    result = read_blackboard_board(tmp_path)

    assert result["valid"] is False
    assert result["entries"] == []
    codes = [error["code"] for error in result["errors"]]
    assert codes.count("invalid_filename") == 3
    assert codes.count("unexpected_entry") == 1
    assert codes.count("json_read_failed") == 2
    assert {error["filename"] for error in result["errors"]} == {
        long_name,
        "0001-task_draft.json",
        ".hidden.json",
        "nested",
        "0002_task_draft.json",
        "0003_annotation.json",
    }
    serialized = json.dumps(result, ensure_ascii=False)
    assert "nested payload must not be read" not in serialized
    assert "illegal contract filename payload" not in serialized


def test_reader_accepts_hardlink_and_marks_shared_inode(tmp_path: Path) -> None:
    source = tmp_path.parent / f"{tmp_path.name}-hardlink-source.json"
    source.write_text(
        json.dumps(_fixture("task_draft"), ensure_ascii=False, sort_keys=True),
        encoding="utf-8",
    )
    target = tmp_path / "0001_task_draft.json"
    try:
        target.hardlink_to(source)
    except OSError as exc:
        pytest.skip(f"platform cannot create test hardlink: {type(exc).__name__}")

    result = read_blackboard_board(tmp_path)

    assert result["valid"] is True
    assert result["entry_count"] == 1
    assert result["errors"] == []
    entry = result["entries"][0]
    assert entry["shared_inode"] is True
    assert entry["message"]["message_type"] == "task_draft"


def test_reader_rejects_fifo_as_nonregular_entry(tmp_path: Path) -> None:
    fifo = tmp_path / "0001_task_draft.json"
    try:
        os.mkfifo(fifo)
    except (AttributeError, NotImplementedError, OSError) as exc:
        pytest.skip(f"platform cannot create test fifo: {type(exc).__name__}")

    result = read_blackboard_board(tmp_path)

    assert result["valid"] is False
    assert result["entries"] == []
    assert result["errors"] == [
        {
            "filename": fifo.name,
            "code": "unexpected_entry",
            "message": "nested or non-file entry is not allowed",
        }
    ]


def test_reader_rejects_unix_socket_as_nonregular_entry(tmp_path: Path) -> None:
    if not hasattr(socket, "AF_UNIX"):
        pytest.skip("platform has no AF_UNIX filesystem socket support")
    socket_path = tmp_path / "0001_task_draft.json"
    listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        listener.bind(str(socket_path))
        result = read_blackboard_board(tmp_path)
    except OSError as exc:
        pytest.skip(f"platform cannot create filesystem socket: {type(exc).__name__}")
    finally:
        listener.close()

    assert result["valid"] is False
    assert result["entries"] == []
    assert result["errors"][0]["code"] == "unexpected_entry"


def test_reader_rejects_device_as_nonregular_entry(tmp_path: Path) -> None:
    if os.name == "nt" or not hasattr(os, "mknod") or not hasattr(os, "makedev"):
        pytest.skip("device-node creation is unavailable on this platform")
    device_path = tmp_path / "0001_task_draft.json"
    try:
        os.mknod(device_path, stat.S_IFCHR | 0o600, os.makedev(1, 3))
    except (OSError, PermissionError) as exc:
        pytest.skip(f"platform cannot create device node: {type(exc).__name__}")

    result = read_blackboard_board(tmp_path)

    assert result["valid"] is False
    assert result["entries"] == []
    assert result["errors"][0]["code"] == "unexpected_entry"


def test_reader_does_not_recurse_through_recursive_symlink(
    tmp_path: Path,
) -> None:
    outside = tmp_path.parent / f"{tmp_path.name}-recursive-outside"
    outside.mkdir()
    marker = "RECURSIVE-SYMLINK-PAYLOAD-MUST-NOT-BE-READ"
    (outside / "payload.txt").write_text(marker, encoding="utf-8")
    link = tmp_path / "nested-link"
    try:
        link.symlink_to(tmp_path, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"platform cannot create directory symlink: {type(exc).__name__}")

    result = read_blackboard_board(tmp_path)

    assert result["valid"] is False
    assert result["entries"] == []
    assert result["errors"] == [
        {
            "filename": link.name,
            "code": "symlink_rejected",
            "message": "symlinks are not read",
        }
    ]
    assert marker not in json.dumps(result, ensure_ascii=False)


def test_reader_does_not_descend_into_one_hundred_nested_directories(
    tmp_path: Path,
) -> None:
    deep = tmp_path
    try:
        for index in range(100):
            deep = deep / f"d{index:03d}"
            deep.mkdir()
        marker = "DEEP-DIRECTORY-PAYLOAD-MUST-NOT-BE-READ"
        (deep / "payload.txt").write_text(marker, encoding="utf-8")
    except OSError as exc:
        pytest.skip(f"platform cannot create 100 nested directories: {type(exc).__name__}")

    result = read_blackboard_board(tmp_path)

    assert result["valid"] is False
    assert result["entries"] == []
    assert result["errors"] == [
        {
            "filename": "d000",
            "code": "unexpected_entry",
            "message": "nested or non-file entry is not allowed",
        }
    ]
    assert marker not in json.dumps(result, ensure_ascii=False)


def test_reader_handles_case_conflicting_entry_names_without_payload_leak(
    tmp_path: Path,
) -> None:
    canonical = tmp_path / "0001_task_draft.json"
    conflict = tmp_path / "0001_TASK_DRAFT.json"
    canonical.write_text(
        json.dumps(_fixture("task_draft"), ensure_ascii=False, sort_keys=True),
        encoding="utf-8",
    )
    marker = "CASE-CONFLICT-PAYLOAD-MUST-NOT-BE-READ"
    try:
        conflict.write_text(marker, encoding="utf-8")
    except OSError as exc:
        pytest.skip(f"platform cannot create case-conflict fixture: {type(exc).__name__}")
    if len(list(tmp_path.iterdir())) < 2:
        pytest.skip("filesystem is case-insensitive; case-conflict names alias")

    result = read_blackboard_board(tmp_path)

    assert result["valid"] is False
    assert result["entry_count"] == 1
    assert any(error["code"] == "invalid_filename" for error in result["errors"])
    assert marker not in json.dumps(result, ensure_ascii=False)


def test_reader_rejects_unreadable_entry_without_echoing_payload(
    tmp_path: Path,
) -> None:
    if os.name == "nt":
        pytest.skip("chmod 000 boundary is POSIX-only")
    entry = tmp_path / "0001_task_draft.json"
    marker = "CHMOD-000-PAYLOAD-MUST-NOT-BE-READ"
    entry.write_text(marker, encoding="utf-8")
    entry.chmod(0)
    try:
        result = read_blackboard_board(tmp_path)
    finally:
        entry.chmod(0o600)

    assert result["valid"] is False
    assert result["entries"] == []
    assert result["errors"][0]["code"] == "json_read_failed"
    assert marker not in json.dumps(result, ensure_ascii=False)
