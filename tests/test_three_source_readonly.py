"""Tests for the Phase 0 local/GitHub/Replit read-only status reporter."""

from __future__ import annotations

import subprocess
from pathlib import Path
from urllib.error import URLError

from scripts import check_three_source_readonly as checker


LOCAL_HASH = "1" * 40
REMOTE_HASH = "2" * 40


class _Response:
    def __init__(self, status: int) -> None:
        self.status = status

    def __enter__(self) -> _Response:
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def getcode(self) -> int:
        return self.status


def _git_runner(local_hash: str, remote_hash: str):
    def run(command: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        if command[1:] == ["rev-parse", "HEAD"]:
            return subprocess.CompletedProcess(command, 0, local_hash + "\n", "")
        if command[1:] == ["ls-remote", "origin", "refs/heads/master"]:
            output = f"{remote_hash}\trefs/heads/master\n"
            return subprocess.CompletedProcess(command, 0, output, "")
        raise AssertionError(f"unexpected git command: {command}")

    return run


def test_three_sources_report_aligned_when_hashes_match_and_replit_is_reachable(
    monkeypatch,
) -> None:
    monkeypatch.setattr(checker.subprocess, "run", _git_runner(LOCAL_HASH, LOCAL_HASH))
    monkeypatch.setattr(checker, "urlopen", lambda *_args, **_kwargs: _Response(200))

    report = checker.check_three_sources(Path("repo"))

    assert report.verdict == "ALIGNED"
    assert report.local.value == LOCAL_HASH
    assert report.github.value == LOCAL_HASH
    assert report.replit.value == "REACHABLE"
    rendered = checker.render_report(report)
    assert "VERDICT: ALIGNED" in rendered
    assert "reachability only" in rendered


def test_three_sources_report_drift_without_attempting_repair(monkeypatch) -> None:
    calls: list[list[str]] = []
    runner = _git_runner(LOCAL_HASH, REMOTE_HASH)

    def recording_runner(command: list[str], **kwargs: object):
        calls.append(command)
        return runner(command, **kwargs)

    monkeypatch.setattr(checker.subprocess, "run", recording_runner)
    monkeypatch.setattr(checker, "urlopen", lambda *_args, **_kwargs: _Response(200))

    report = checker.check_three_sources(Path("repo"))

    assert report.verdict == "DRIFT"
    assert [command[1] for command in calls] == ["rev-parse", "ls-remote"]
    forbidden = {"pull", "push", "reset", "checkout", "switch"}
    assert all(not forbidden.intersection(command) for command in calls)


def test_origin_and_replit_failures_are_unreachable_not_exceptions(monkeypatch) -> None:
    def failing_remote(command: list[str], **_kwargs: object):
        if command[1:] == ["rev-parse", "HEAD"]:
            return subprocess.CompletedProcess(command, 0, LOCAL_HASH + "\n", "")
        return subprocess.CompletedProcess(command, 128, "", "network unavailable")

    def failing_replit(*_args: object, **_kwargs: object):
        raise URLError("offline")

    monkeypatch.setattr(checker.subprocess, "run", failing_remote)
    monkeypatch.setattr(checker, "urlopen", failing_replit)

    report = checker.check_three_sources(Path("repo"))

    assert report.verdict == "INCOMPLETE"
    assert report.github.value == "UNREACHABLE"
    assert report.github.detail == "network unavailable"
    assert report.replit.value == "UNREACHABLE"
    assert "offline" in report.replit.detail


def test_main_exit_codes_are_status_only(monkeypatch, capsys) -> None:
    report = checker.ThreeSourceReport(
        checker.SourceState("local", LOCAL_HASH, "local"),
        checker.SourceState("github", REMOTE_HASH, "remote"),
        checker.SourceState("replit", "REACHABLE", "HTTP 200"),
        "DRIFT",
    )
    monkeypatch.setattr(checker, "check_three_sources", lambda *_args, **_kwargs: report)

    assert checker.main(["--repo", "."]) == 1
    assert "VERDICT: DRIFT" in capsys.readouterr().out
