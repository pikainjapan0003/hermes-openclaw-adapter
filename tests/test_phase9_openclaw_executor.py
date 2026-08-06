"""Offline tests for the Phase 9 real-executor subprocess boundary."""

from __future__ import annotations

import ast
import hashlib
import subprocess
from pathlib import Path
from typing import Sequence

import pytest

from app.phase9_gate import (
    EXPECTED_OPENCLAW_VERSION,
    OwnerAuthorizedOpenClawExecutor,
    OwnerAuthorizedOpenClawVersionProbe,
)
from app.phase9_openclaw_executor import (
    ForegroundSubprocessRunner,
    ProcessOutcome,
)


pytestmark = pytest.mark.contract

SAFE_ARGV = (
    "openclaw",
    "agent",
    "--local",
    "--message",
    "Return one harmless local status summary.",
    "--json",
    "--timeout",
    "12",
)


class FakeProcessRunner:
    def __init__(self, outcome: ProcessOutcome) -> None:
        self.outcome = outcome
        self.calls: list[tuple[tuple[str, ...], int]] = []

    def invoke(
        self,
        argv: Sequence[str],
        *,
        timeout_seconds: int,
    ) -> ProcessOutcome:
        self.calls.append((tuple(argv), timeout_seconds))
        return self.outcome


def test_real_type_executor_issues_one_fake_attempt_and_returns_only_digests() -> None:
    stdout = b'{"status":"ok","secret":"FAKE-NOT-PERSISTED"}'
    stderr = b"synthetic diagnostic"
    runner = FakeProcessRunner(ProcessOutcome(0, False, stdout, stderr))
    executor = OwnerAuthorizedOpenClawExecutor(runner)

    result = executor.execute(SAFE_ARGV, timeout_seconds=12)

    assert executor.test_double is False
    assert runner.calls == [(SAFE_ARGV, 12)]
    assert result.exit_code == 0
    assert result.timed_out is False
    assert result.stdout_digest == hashlib.sha256(stdout).hexdigest()
    assert result.stderr_digest == hashlib.sha256(stderr).hexdigest()
    assert "FAKE-NOT-PERSISTED" not in repr(result)


def test_real_type_executor_records_a_fake_timeout_without_retry() -> None:
    runner = FakeProcessRunner(ProcessOutcome(None, True, b"partial", b"timeout"))
    executor = OwnerAuthorizedOpenClawExecutor(runner)

    result = executor.execute(SAFE_ARGV, timeout_seconds=7)

    assert runner.calls == [(SAFE_ARGV, 7)]
    assert result.exit_code is None
    assert result.timed_out is True


def test_version_probe_uses_exact_bounded_fake_argv() -> None:
    runner = FakeProcessRunner(
        ProcessOutcome(0, False, f"{EXPECTED_OPENCLAW_VERSION}\n".encode(), b"")
    )

    observed = OwnerAuthorizedOpenClawVersionProbe(runner).probe_version()

    assert observed == EXPECTED_OPENCLAW_VERSION
    assert runner.calls == [(('openclaw', '--version'), 5)]


@pytest.mark.parametrize(
    "outcome",
    (
        ProcessOutcome(1, False, b"future", b"failure"),
        ProcessOutcome(None, True, b"partial", b"timeout"),
        ProcessOutcome(0, False, b"\xff", b""),
    ),
)
def test_version_probe_fails_closed_for_unusable_fake_results(
    outcome: ProcessOutcome,
) -> None:
    runner = FakeProcessRunner(outcome)

    assert OwnerAuthorizedOpenClawVersionProbe(runner).probe_version() == ""
    assert len(runner.calls) == 1


def test_foreground_runner_passes_shell_free_bounded_options_to_fake_subprocess() -> None:
    calls: list[tuple[list[str], dict[str, object]]] = []

    def fake_run(
        argv: list[str],
        **kwargs: object,
    ) -> subprocess.CompletedProcess[bytes]:
        calls.append((argv, kwargs))
        return subprocess.CompletedProcess(argv, 0, b"out", b"err")

    result = ForegroundSubprocessRunner(fake_run).invoke(
        ("synthetic-binary", "--synthetic-flag"),
        timeout_seconds=3,
    )

    assert result == ProcessOutcome(0, False, b"out", b"err")
    assert len(calls) == 1
    argv, kwargs = calls[0]
    assert argv == ["synthetic-binary", "--synthetic-flag"]
    assert kwargs["shell"] is False
    assert kwargs["check"] is False
    assert kwargs["timeout"] == 3
    assert kwargs["stdin"] == subprocess.DEVNULL
    assert kwargs["stdout"] == subprocess.PIPE
    assert kwargs["stderr"] == subprocess.PIPE


def test_foreground_runner_converts_fake_timeout_partial_output() -> None:
    def fake_timeout(
        argv: list[str],
        **kwargs: object,
    ) -> subprocess.CompletedProcess[bytes]:
        del argv, kwargs
        raise subprocess.TimeoutExpired(
            cmd="synthetic-binary",
            timeout=2,
            output=b"partial-out",
            stderr=b"partial-err",
        )

    result = ForegroundSubprocessRunner(fake_timeout).invoke(
        ("synthetic-binary",),
        timeout_seconds=2,
    )

    assert result == ProcessOutcome(None, True, b"partial-out", b"partial-err")


def test_executor_module_is_the_only_phase9_subprocess_boundary() -> None:
    root = Path(__file__).parents[1]
    executor_path = root / "app" / "phase9_openclaw_executor.py"
    gate_path = root / "app" / "phase9_gate.py"
    executor_tree = ast.parse(executor_path.read_text(encoding="utf-8"))
    gate_tree = ast.parse(gate_path.read_text(encoding="utf-8"))

    def imports(tree: ast.AST) -> set[str]:
        return {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
            for alias in node.names
        }

    assert "subprocess" in imports(executor_tree)
    assert "subprocess" not in imports(gate_tree)
    assert "socket" not in imports(executor_tree)
    source = executor_path.read_text(encoding="utf-8")
    assert "os.system" not in source
    assert "shell=False" in source


def test_first_real_probe_and_call_remain_execution_day_only() -> None:
    """This package constructs no default runner and invokes no real binary."""

    runner = FakeProcessRunner(ProcessOutcome(0, False, b"synthetic", b""))
    OwnerAuthorizedOpenClawExecutor(runner)
    OwnerAuthorizedOpenClawVersionProbe(runner)

    assert runner.calls == []
