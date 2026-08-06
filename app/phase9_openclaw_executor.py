"""Single-attempt foreground subprocess boundary for Phase 9.

Nothing imports or constructs this runner from a route or runtime path.  The
Owner-authorized gate wrappers inject it explicitly.  This module contains the
only Phase 9 production import of ``subprocess``; it never uses a shell, retry,
network, socket, or background process.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import Callable, Protocol, Sequence


@dataclass(frozen=True)
class ProcessOutcome:
    """Bounded-attempt process metadata; byte payloads are hashed by the caller."""

    exit_code: int | None
    timed_out: bool
    stdout: bytes
    stderr: bytes


class ProcessRunner(Protocol):
    def invoke(
        self,
        argv: Sequence[str],
        *,
        timeout_seconds: int,
    ) -> ProcessOutcome:
        """Run one foreground attempt, with no retry."""


_RunCallable = Callable[..., subprocess.CompletedProcess[bytes]]


def _partial_bytes(value: bytes | str | None) -> bytes:
    if value is None:
        return b""
    if isinstance(value, bytes):
        return value
    return value.encode("utf-8", errors="replace")


class ForegroundSubprocessRunner:
    """Run one shell-free foreground process with an explicit timeout."""

    def __init__(self, run_callable: _RunCallable = subprocess.run) -> None:
        self._run_callable = run_callable

    def invoke(
        self,
        argv: Sequence[str],
        *,
        timeout_seconds: int,
    ) -> ProcessOutcome:
        if isinstance(argv, (str, bytes)) or not argv:
            raise ValueError("process argv must be a non-empty sequence")
        if any(not isinstance(value, str) or not value for value in argv):
            raise ValueError("process argv contains an invalid item")
        if type(timeout_seconds) is not int or timeout_seconds < 1:
            raise ValueError("process timeout must be a positive integer")
        try:
            completed = self._run_callable(
                list(argv),
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False,
                check=False,
                timeout=timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:
            return ProcessOutcome(
                exit_code=None,
                timed_out=True,
                stdout=_partial_bytes(exc.stdout),
                stderr=_partial_bytes(exc.stderr),
            )
        return ProcessOutcome(
            exit_code=completed.returncode,
            timed_out=False,
            stdout=_partial_bytes(completed.stdout),
            stderr=_partial_bytes(completed.stderr),
        )


__all__ = ["ForegroundSubprocessRunner", "ProcessOutcome", "ProcessRunner"]
