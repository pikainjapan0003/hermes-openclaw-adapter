"""Phase 9 N=1 entry-point tests: rehearsal works, real mode never does."""

from __future__ import annotations

import ast
import base64
import io
import os
import subprocess
from contextlib import AbstractContextManager, contextmanager
from pathlib import Path
from typing import Iterator

import pytest

from scripts.run_phase9_n1 import _runtime_gate_principal, main, run_dry_rehearsal


pytestmark = pytest.mark.contract
REPO_ROOT = Path(__file__).parents[1]


class CountingRealExecutorFactory:
    def __init__(self) -> None:
        self.calls = 0

    def __call__(self) -> object:
        self.calls += 1
        raise AssertionError("real executor must remain unreachable")


@contextmanager
def _workspace(path: Path) -> Iterator[str]:
    yield str(path)


def _owner_principal_distinct_from_gate() -> str:
    return f"uid:{os.getuid() + 1}"


def test_default_rehearsal_runs_all_thirteen_owner_readable_steps(
    tmp_path: Path,
) -> None:
    output = io.StringIO()
    factory = CountingRealExecutorFactory()
    report = run_dry_rehearsal(
        output=output,
        real_executor_factory=factory,
        expected_owner_principal=_owner_principal_distinct_from_gate(),
        workspace_factory=lambda: _workspace(tmp_path),
    )
    text = output.getvalue()

    assert report.fake_executor_calls == 1
    assert report.real_executor_calls == 0
    assert report.burn_records == 1
    assert report.audit_records == 1
    assert factory.calls == 0
    assert len(report.trace) == 16
    assert report.trace[0] == "1:DENY_ALL_TO_CHECKING"
    assert report.trace[-1] == "15:POST_ATTEMPT_EVIDENCE_COMPUTED"
    assert all(f"[{index}/13]" in text for index in range(1, 14))
    assert "不會呼叫真實 OpenClaw" in text
    assert "真實 executor 呼叫：0" in text
    assert "Traceback" not in text
    raw_fixed_value = base64.urlsafe_b64encode(b"d" * 32).rstrip(b"=").decode()
    assert raw_fixed_value not in text
    assert raw_fixed_value not in "".join(
        path.read_text(encoding="utf-8")
        for path in tmp_path.rglob("*")
        if path.is_file()
    )


@pytest.mark.parametrize(
    ("argv", "expected_status"),
    (
        ((), 0),
        (("--dry-run",), 0),
        (("--real",), 2),
        (("--unknown",), 2),
        (("--real", "--dry-run"), 2),
        (("n1_harmless_query",), 2),
    ),
)
def test_every_argument_shape_keeps_real_process_and_executor_calls_at_zero(
    argv: tuple[str, ...],
    expected_status: int,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    process_calls = 0

    def forbidden_process(*_args: object, **_kwargs: object) -> object:
        nonlocal process_calls
        process_calls += 1
        raise AssertionError("no process may start")

    monkeypatch.setattr(subprocess, "run", forbidden_process)
    output = io.StringIO()
    factory = CountingRealExecutorFactory()

    status = main(
        argv,
        output=output,
        real_executor_factory=factory,
        expected_owner_principal=_owner_principal_distinct_from_gate(),
    )

    assert status == expected_status
    assert factory.calls == 0
    assert process_calls == 0
    assert "Traceback" not in output.getvalue()


def test_missing_owner_principal_rejects_before_thirteen_steps() -> None:
    output = io.StringIO()
    factory = CountingRealExecutorFactory()

    def forbidden_workspace() -> AbstractContextManager[str]:
        raise AssertionError("thirteen-step rehearsal must not start")

    status = main(
        (),
        output=output,
        real_executor_factory=factory,
        workspace_factory=forbidden_workspace,
    )

    text = output.getvalue()
    assert status == 2
    assert factory.calls == 0
    assert "未設定 Owner principal" in text
    assert "[1/13]" not in text
    assert "Traceback" not in text


def test_gate_principal_uses_runtime_uid_format(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(os, "getuid", lambda: 4242)

    assert _runtime_gate_principal() == "uid:4242"


def test_entrypoint_is_not_wired_to_routes_main_or_worker() -> None:
    forbidden_consumers = (
        REPO_ROOT / "app" / "main.py",
        REPO_ROOT / "app" / "worker.py",
    )
    for path in forbidden_consumers:
        source = path.read_text(encoding="utf-8")
        assert "run_phase9_n1" not in source

    entrypoint = REPO_ROOT / "scripts" / "run_phase9_n1.py"
    tree = ast.parse(entrypoint.read_text(encoding="utf-8"))
    forbidden_calls = {
        "Popen",
        "Thread",
        "os.system",
        "run_forever",
        "start",
    }
    observed = {
        (
            f"{node.func.value.id}.{node.func.attr}"
            if isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            else node.func.attr
            if isinstance(node.func, ast.Attribute)
            else node.func.id
            if isinstance(node.func, ast.Name)
            else ""
        )
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
    }
    assert observed.isdisjoint(forbidden_calls)
