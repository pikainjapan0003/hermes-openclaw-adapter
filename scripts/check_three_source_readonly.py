#!/usr/bin/env python3
"""Report local/GitHub/Replit state without changing any source.

This Phase 0 helper only reads local Git state, runs ``git ls-remote``, and checks
the configured Replit HTTP endpoint.  It never attempts pull, push, reset,
checkout, deploy, or drift repair.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_REPLIT_URL = (
    "https://hermes-openclaw-adapter.replit.app/dashboard/system"
)
HASH_PATTERN = re.compile(r"^[0-9a-f]{40}$")


@dataclass(frozen=True)
class SourceState:
    source: str
    value: str
    detail: str


@dataclass(frozen=True)
class ThreeSourceReport:
    local: SourceState
    github: SourceState
    replit: SourceState
    verdict: str


def _git_output(repo: Path, arguments: list[str], timeout: float) -> tuple[str, str]:
    try:
        completed = subprocess.run(
            ["git", *arguments],
            cwd=repo,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return "", f"{type(exc).__name__}: {exc}"

    if completed.returncode != 0:
        detail = completed.stderr.strip() or f"git exited {completed.returncode}"
        return "", detail
    return completed.stdout.strip(), ""


def read_local_head(repo: Path, timeout: float = 10.0) -> SourceState:
    output, error = _git_output(repo, ["rev-parse", "HEAD"], timeout)
    if error or not HASH_PATTERN.fullmatch(output):
        return SourceState("local", "UNREACHABLE", error or "invalid HEAD hash")
    return SourceState("local", output, "git rev-parse HEAD")


def read_origin_head(
    repo: Path,
    remote: str = "origin",
    branch: str = "master",
    timeout: float = 15.0,
) -> SourceState:
    output, error = _git_output(
        repo, ["ls-remote", remote, f"refs/heads/{branch}"], timeout
    )
    if error:
        return SourceState("github", "UNREACHABLE", error)

    expected_ref = f"refs/heads/{branch}"
    for line in output.splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[1] == expected_ref:
            if HASH_PATTERN.fullmatch(parts[0]):
                return SourceState(
                    "github", parts[0], f"git ls-remote {remote} {branch}"
                )
            break
    return SourceState("github", "UNREACHABLE", "branch hash not returned")


def read_replit_status(url: str, timeout: float = 10.0) -> SourceState:
    request = Request(url, headers={"User-Agent": "hoa-phase0-readonly-check/1"})
    try:
        with urlopen(request, timeout=timeout) as response:
            status = response.getcode()
    except HTTPError as exc:
        return SourceState("replit", "UNREACHABLE", f"HTTP {exc.code}: {url}")
    except (URLError, OSError, TimeoutError) as exc:
        return SourceState("replit", "UNREACHABLE", f"{type(exc).__name__}: {exc}")

    if 200 <= status < 400:
        return SourceState("replit", "REACHABLE", f"HTTP {status}: {url}")
    return SourceState("replit", "UNREACHABLE", f"HTTP {status}: {url}")


def check_three_sources(
    repo: Path,
    remote: str = "origin",
    branch: str = "master",
    replit_url: str = DEFAULT_REPLIT_URL,
) -> ThreeSourceReport:
    local = read_local_head(repo)
    github = read_origin_head(repo, remote=remote, branch=branch)
    replit = read_replit_status(replit_url)

    if "UNREACHABLE" in {local.value, github.value, replit.value}:
        verdict = "INCOMPLETE"
    elif local.value != github.value:
        verdict = "DRIFT"
    else:
        verdict = "ALIGNED"

    return ThreeSourceReport(local, github, replit, verdict)


def render_report(report: ThreeSourceReport) -> str:
    rows = [report.local, report.github, report.replit]
    widths = {
        "source": max(len("SOURCE"), *(len(row.source) for row in rows)),
        "value": max(len("HASH / STATUS"), *(len(row.value) for row in rows)),
    }
    header = (
        f"{'SOURCE':<{widths['source']}} | "
        f"{'HASH / STATUS':<{widths['value']}} | DETAIL"
    )
    separator = f"{'-' * widths['source']}-+-{'-' * widths['value']}-+-------"
    body = [
        f"{row.source:<{widths['source']}} | "
        f"{row.value:<{widths['value']}} | {row.detail}"
        for row in rows
    ]
    note = (
        "Replit reports HTTP reachability only; it does not prove the deployed "
        "commit hash."
    )
    return "\n".join([header, separator, *body, f"VERDICT: {report.verdict}", note])


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--branch", default="master")
    parser.add_argument("--replit-url", default=DEFAULT_REPLIT_URL)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    report = check_three_sources(
        args.repo.resolve(),
        remote=args.remote,
        branch=args.branch,
        replit_url=args.replit_url,
    )
    print(render_report(report))
    return {"ALIGNED": 0, "DRIFT": 1, "INCOMPLETE": 2}[report.verdict]


if __name__ == "__main__":
    sys.exit(main())
