#!/usr/bin/env python3
"""Compare authoritative repo docs with a read-only documentation mirror.

The command only reads files and prints a table.  It never synchronizes, repairs,
creates, deletes, or otherwise changes either directory.
"""

from __future__ import annotations

import argparse
import hashlib
from dataclasses import dataclass
from pathlib import Path


SAME = "SAME"
BEHIND = "BEHIND"
AHEAD = "AHEAD"
DIFFERS = "DIFFERS"


@dataclass(frozen=True)
class DriftEntry:
    path: str
    status: str
    detail: str


def _files(root: Path) -> dict[str, Path]:
    if not root.is_dir():
        raise ValueError(f"not a directory: {root}")
    return {
        path.relative_to(root).as_posix(): path
        for path in root.rglob("*")
        if path.is_file()
    }


def _digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(64 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def compare_mirror(repo_docs: Path, mirror_docs: Path) -> tuple[DriftEntry, ...]:
    """Return deterministic per-file states without changing either tree.

    A repo-only path means the downstream mirror is behind the authoritative repo.
    A mirror-only path is an unambiguous ahead/incident case.  When both paths exist
    but their hashes differ, ancestry cannot be inferred from two snapshots, so the
    entry is classified as DIFFERS and requires human review.
    """

    repo_files = _files(repo_docs)
    mirror_files = _files(mirror_docs)
    entries: list[DriftEntry] = []

    for relative_path in sorted(repo_files.keys() | mirror_files.keys()):
        repo_file = repo_files.get(relative_path)
        mirror_file = mirror_files.get(relative_path)
        if repo_file is None:
            entries.append(
                DriftEntry(relative_path, AHEAD, "mirror-only path; incident review")
            )
        elif mirror_file is None:
            entries.append(
                DriftEntry(relative_path, BEHIND, "missing from downstream mirror")
            )
        elif _digest(repo_file) == _digest(mirror_file):
            entries.append(DriftEntry(relative_path, SAME, "sha256 equal"))
        else:
            entries.append(
                DriftEntry(
                    relative_path,
                    DIFFERS,
                    "content differs; ancestry unknown, human review required",
                )
            )

    return tuple(entries)


def render_report(entries: tuple[DriftEntry, ...]) -> str:
    rows = ["STATUS | PATH | DETAIL"]
    rows.extend(f"{entry.status} | {entry.path} | {entry.detail}" for entry in entries)
    if any(entry.status == AHEAD for entry in entries):
        rows.append(
            "INCIDENT: mirror is ahead of repo; stop and report under "
            "40_MAINTENANCE_PROTOCOL.md F6."
        )
    if any(entry.status == DIFFERS for entry in entries):
        rows.append(
            "DIFFERS: human decision required; do not overwrite either copy "
            "(L-007 scenario)."
        )
    counts = {
        state: sum(entry.status == state for entry in entries)
        for state in (SAME, BEHIND, AHEAD, DIFFERS)
    }
    rows.append(
        f"SUMMARY: SAME={counts[SAME]} BEHIND={counts[BEHIND]} "
        f"AHEAD={counts[AHEAD]} DIFFERS={counts[DIFFERS]}"
    )
    return "\n".join(rows)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo_docs", type=Path)
    parser.add_argument("mirror_docs", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    entries = compare_mirror(args.repo_docs.resolve(), args.mirror_docs.resolve())
    print(render_report(entries))
    if any(entry.status == DIFFERS for entry in entries):
        return 3
    if any(entry.status == AHEAD for entry in entries):
        return 2
    if any(entry.status == BEHIND for entry in entries):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
