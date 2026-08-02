"""Static and runtime proof that the Phase 7 writer has one write target."""

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path
from typing import Any, Callable

import pytest

import app.audit_writer_local as writer


pytestmark = pytest.mark.contract

ROOT = Path(__file__).resolve().parent.parent
WRITER_SOURCE = ROOT / "app" / "audit_writer_local.py"


def _event(index: int, previous: str | None = None) -> dict[str, Any]:
    value = json.loads(
        (ROOT / "fixtures" / "blackboard_contract" / "audit_event.valid.json").read_text(
            encoding="utf-8"
        )
    )
    value["prev_entry_hash"] = previous
    value["audit_id"] = f"scope-audit-{index}"
    value["event_id"] = f"scope-event-{index}"
    value["event_notes"] = "Synthetic scope proof; no execution."
    return value


def _sandbox(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    target = repo / "data" / "audit_dev.jsonl"
    target.parent.mkdir(parents=True)
    monkeypatch.setattr(writer, "REPO_ROOT", repo)
    monkeypatch.setattr(writer, "AUDIT_PATH", target)
    return target


def test_writer_ast_has_only_authorized_append_boundary() -> None:
    tree = ast.parse(WRITER_SOURCE.read_text(encoding="utf-8"))
    write_calls: list[ast.Call] = []
    forbidden_calls: list[ast.Call] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Attribute) and node.func.attr in {
            "mkdir",
            "unlink",
            "rename",
            "replace",
        }:
            forbidden_calls.append(node)
        if isinstance(node.func, ast.Attribute) and node.func.attr == "open":
            mode = ""
            if len(node.args) >= 1 and isinstance(node.args[0], ast.Constant):
                mode = str(node.args[0].value)
            mode += " ".join(
                str(keyword.value.value)
                for keyword in node.keywords
                if keyword.arg == "mode"
                and isinstance(keyword.value, ast.Constant)
            )
            if any(flag in mode for flag in ("w", "a", "x", "+")):
                write_calls.append(node)

    assert not forbidden_calls
    assert len(write_calls) == 1
    assert isinstance(write_calls[0].args[0], ast.Constant)
    assert write_calls[0].args[0].value == "a+b"
    literals = {
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    }
    assert "data" in literals
    assert "audit_dev.jsonl" in literals


def test_runtime_write_paths_are_exactly_the_tmp_authorized_target(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    target = _sandbox(monkeypatch, tmp_path)
    writes: list[Path] = []
    original_path_open: Callable[..., Any] = Path.open

    def recording_path_open(self: Path, *args: Any, **kwargs: Any) -> Any:
        mode = kwargs.get("mode", args[0] if args else "r")
        if any(flag in str(mode) for flag in ("w", "a", "x", "+")):
            writes.append(self.resolve(strict=False))
        return original_path_open(self, *args, **kwargs)

    monkeypatch.setattr(Path, "open", recording_path_open)
    first = writer.append_audit_event(_event(1))
    writer.append_audit_event(_event(2, str(first["entry_hash"])))
    assert writes == [target.resolve(strict=False), target.resolve(strict=False)]
    assert set(writes) == {target.resolve(strict=False)}


def test_repo_status_has_no_new_path_other_than_authorized_audit_file(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    before = _status_paths()
    _sandbox(monkeypatch, tmp_path)
    writer.append_audit_event(_event(1))
    after = _status_paths()
    allowed = {"data/audit_dev.jsonl"}
    assert after - before <= allowed
    assert all(path == "data/audit_dev.jsonl" or not path.startswith("data/") for path in after)


def _status_paths() -> set[str]:
    result = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    paths: set[str] = set()
    for line in result.stdout.splitlines():
        if not line:
            continue
        path = line[3:]
        if " -> " in path:
            path = path.rsplit(" -> ", 1)[1]
        paths.add(path.replace("\\", "/"))
    return paths
