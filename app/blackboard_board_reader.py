"""Pure read-only loader for one synthetic N=1 Blackboard board directory.

The caller supplies an existing directory.  This module never creates a directory,
writes a file, mutates Blackboard state, or connects to a route, queue, Worker, or
runtime.  Invalid records are reported structurally without echoing their payload.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any, cast

from app.blackboard_validators import (
    BlackboardSchemaError,
    SCHEMA_FILES,
    validate_blackboard_message,
)


_MESSAGE_TYPE_PATTERN = "|".join(re.escape(name) for name in SCHEMA_FILES)
_ENTRY_FILENAME = re.compile(
    rf"^(?P<sequence>[0-9]{{4}})_(?P<message_type>{_MESSAGE_TYPE_PATTERN})\.json$"
)


def _error(
    code: str,
    message: str,
    filename: str | None = None,
) -> dict[str, Any]:
    return {"filename": filename, "code": code, "message": message}


def read_blackboard_board(directory: str | Path) -> dict[str, Any]:
    """Read and validate immediate JSON entries from an existing board directory.

    Empty directories are valid.  Files must use ``NNNN_message_type.json`` names,
    sequence numbers and message types must be unique, and every record is validated
    against the message type selected by its filename.  Symlinks, nested directories,
    unexpected files, malformed JSON, and schema failures are rejected fail-closed.
    """

    board_path = Path(directory)
    board_name = board_path.name
    entries: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []

    if not board_path.exists():
        errors.append(_error("directory_missing", "board directory does not exist"))
        return {
            "valid": False,
            "board_name": board_name,
            "entry_count": 0,
            "entries": entries,
            "errors": errors,
        }
    if not board_path.is_dir():
        errors.append(_error("not_a_directory", "board path is not a directory"))
        return {
            "valid": False,
            "board_name": board_name,
            "entry_count": 0,
            "entries": entries,
            "errors": errors,
        }

    try:
        children = sorted(board_path.iterdir(), key=lambda path: path.name)
    except OSError as exc:
        errors.append(
            _error(
                "directory_read_failed",
                f"board directory could not be enumerated: {type(exc).__name__}",
            )
        )
        return {
            "valid": False,
            "board_name": board_name,
            "entry_count": 0,
            "entries": entries,
            "errors": errors,
        }

    seen_sequences: set[int] = set()
    seen_types: set[str] = set()
    for child in children:
        filename = child.name
        if child.is_symlink():
            errors.append(_error("symlink_rejected", "symlinks are not read", filename))
            continue
        if not child.is_file():
            errors.append(
                _error("unexpected_entry", "nested or non-file entry is not allowed", filename)
            )
            continue

        match = _ENTRY_FILENAME.fullmatch(filename)
        if match is None:
            errors.append(
                _error(
                    "invalid_filename",
                    "entry filename must be NNNN_message_type.json",
                    filename,
                )
            )
            continue

        sequence = int(match.group("sequence"))
        message_type = match.group("message_type")
        if sequence in seen_sequences:
            errors.append(
                _error("duplicate_sequence", "entry sequence must be unique", filename)
            )
            continue
        if message_type in seen_types:
            errors.append(
                _error(
                    "duplicate_message_type",
                    "N=1 board allows at most one entry per message type",
                    filename,
                )
            )
            continue
        seen_sequences.add(sequence)
        seen_types.add(message_type)

        try:
            decoded = json.loads(child.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            errors.append(
                _error(
                    "json_read_failed",
                    f"entry could not be decoded: {type(exc).__name__}",
                    filename,
                )
            )
            continue

        try:
            validation = validate_blackboard_message(
                cast(Mapping[str, Any], decoded), message_type
            )
        except BlackboardSchemaError as exc:
            errors.append(
                _error(
                    "schema_unavailable",
                    f"schema validation could not start: {type(exc).__name__}",
                    filename,
                )
            )
            continue

        entry: dict[str, Any] = {
            "filename": filename,
            "sequence": sequence,
            "message_type": message_type,
            "valid": validation["valid"],
            "errors": validation["errors"],
        }
        if validation["valid"]:
            entry["message"] = dict(cast(Mapping[str, Any], decoded))
        else:
            errors.append(
                _error(
                    "schema_rejected",
                    "entry failed its Blackboard schema",
                    filename,
                )
            )
        entries.append(entry)

    entries.sort(key=lambda entry: entry["sequence"])
    return {
        "valid": not errors,
        "board_name": board_name,
        "entry_count": len(entries),
        "entries": entries,
        "errors": errors,
    }
