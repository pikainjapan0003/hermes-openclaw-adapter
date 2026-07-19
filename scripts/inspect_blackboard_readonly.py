#!/usr/bin/env python3
"""Print a payload-free summary of an existing local Blackboard directory.

The tool delegates all reads and validation to ``blackboard_board_reader``.  It
prints JSON to stdout and has no network, repair, mutation, or execution path.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from app.blackboard_board_reader import read_blackboard_board


def _identifier_overview(message: Mapping[str, Any]) -> dict[str, str | None]:
    identifiers: dict[str, str | None] = {}

    def visit(value: object, prefix: str = "") -> None:
        if not isinstance(value, Mapping):
            return
        for key, child in value.items():
            if not isinstance(key, str):
                continue
            path = f"{prefix}.{key}" if prefix else key
            if key == "id" or key.endswith("_id"):
                if child is None or isinstance(child, str):
                    identifiers[path] = child
            elif isinstance(child, Mapping):
                visit(child, path)

    visit(message)
    return dict(sorted(identifiers.items()))


def summarize_board_result(result: Mapping[str, Any]) -> dict[str, Any]:
    """Create a non-payload summary from ``read_blackboard_board`` output."""

    entries = result.get("entries", [])
    safe_entries = entries if isinstance(entries, list) else []
    counts: Counter[str] = Counter()
    passed: list[str] = []
    failed: set[str] = set()
    id_chain: list[dict[str, Any]] = []

    for entry in safe_entries:
        if not isinstance(entry, Mapping):
            continue
        filename = entry.get("filename")
        message_type = entry.get("message_type")
        if isinstance(message_type, str):
            counts[message_type] += 1
        if entry.get("valid") is True and isinstance(filename, str):
            passed.append(filename)
            message = entry.get("message")
            if isinstance(message, Mapping):
                id_chain.append(
                    {
                        "filename": filename,
                        "message_type": message_type,
                        "identifiers": _identifier_overview(message),
                    }
                )
        elif isinstance(filename, str):
            failed.add(filename)

    errors = result.get("errors", [])
    safe_errors = errors if isinstance(errors, list) else []
    error_list: list[dict[str, str | None]] = []
    for error in safe_errors:
        if not isinstance(error, Mapping):
            continue
        filename = error.get("filename")
        code = error.get("code")
        if isinstance(filename, str):
            failed.add(filename)
        error_list.append(
            {
                "filename": filename if isinstance(filename, str) else None,
                "code": code if isinstance(code, str) else "unknown_error",
            }
        )

    return {
        "board_name": result.get("board_name"),
        "valid": result.get("valid") is True,
        "entry_count": result.get("entry_count", 0),
        "message_type_counts": dict(sorted(counts.items())),
        "validation": {
            "passed": sorted(passed),
            "failed": sorted(failed),
            "errors": error_list,
        },
        "id_chain": id_chain,
    }


def inspect_board(directory: str | Path) -> dict[str, Any]:
    return summarize_board_result(read_blackboard_board(directory))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    summary = inspect_board(args.directory)
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if summary["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
