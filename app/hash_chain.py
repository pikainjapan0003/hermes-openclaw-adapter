"""Pure in-memory canonical JSON and audit hash-chain calculations.

Inputs are expected to have already passed the audit-event schema.  This
module performs no file, queue, network, runtime, or persistence operation.
"""

from __future__ import annotations

import hashlib
import json
import unicodedata
from collections.abc import Mapping, Sequence
from typing import Any


class HashChainError(ValueError):
    """Raised when a value is outside the Phase 7 canonical JSON domain."""


def _validate_value(value: Any, location: str = "$") -> None:
    if value is None or type(value) in {bool, int}:
        return
    if type(value) is float:
        raise HashChainError(f"floating-point value is forbidden at {location}")
    if type(value) is str:
        if unicodedata.normalize("NFC", value) != value:
            raise HashChainError(f"string is not Unicode NFC at {location}")
        return
    if type(value) is list:
        for index, item in enumerate(value):
            _validate_value(item, f"{location}[{index}]")
        return
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str:
                raise HashChainError(f"object key is not a string at {location}")
            if unicodedata.normalize("NFC", key) != key:
                raise HashChainError(f"object key is not Unicode NFC at {location}")
            _validate_value(item, f"{location}.{key}")
        return
    raise HashChainError(
        f"non-JSON value of type {type(value).__name__} at {location}"
    )


def canonical_json(value: Mapping[str, Any]) -> bytes:
    """Return Phase 7 canonical UTF-8 JSON bytes with no trailing newline.

    Duplicate object keys must be rejected by the caller's JSON decoder,
    because a Python mapping cannot retain duplicate-key information.
    """

    if type(value) is not dict:
        raise HashChainError("canonical JSON root must be an object")
    _validate_value(value)
    try:
        canonical_text = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        return canonical_text.encode("utf-8")
    except (TypeError, ValueError, UnicodeEncodeError) as exc:
        raise HashChainError(f"canonical JSON encoding failed: {exc}") from exc


def entry_hash(event: Mapping[str, Any]) -> str:
    """Hash the complete canonical event, including ``prev_entry_hash``."""

    return hashlib.sha256(canonical_json(event)).hexdigest()


def verify_chain(entries: Sequence[Mapping[str, Any]]) -> bool:
    """Verify genesis and every subsequent in-memory ``prev_entry_hash`` link."""

    if isinstance(entries, (str, bytes, bytearray)) or not isinstance(
        entries, Sequence
    ):
        return False
    previous_hash: str | None = None
    try:
        for index, entry in enumerate(entries):
            if not isinstance(entry, Mapping):
                return False
            expected_previous = None if index == 0 else previous_hash
            if entry.get("prev_entry_hash") != expected_previous:
                return False
            previous_hash = entry_hash(entry)
    except HashChainError:
        return False
    return True
