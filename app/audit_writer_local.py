"""Fail-closed append-only writer for the authorized local audit ledger.

The module has one persistence boundary: ``data/audit_dev.jsonl`` under the
repository containing this file.  Importing it, validating an event, and
diagnosing an existing ledger never writes bytes.  The public append function
accepts an in-memory mapping only; it does not accept a path or a serialized
line.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, Mapping

from app.blackboard_validators import validate_blackboard_message
from app.hash_chain import HashChainError, canonical_json, entry_hash, verify_chain


REPO_ROOT = Path(__file__).resolve().parent.parent
AUDIT_PATH = REPO_ROOT / "data" / "audit_dev.jsonl"


class AuditWriterError(ValueError):
    """Payload-free, structured failure raised by the local writer."""

    def __init__(self, message: str, *, entry_index: int | None = None) -> None:
        super().__init__(message)
        self.entry_index = entry_index


class _DuplicateObjectKeyError(ValueError):
    pass


def _reject_duplicate_object_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateObjectKeyError("duplicate JSON object key")
        result[key] = value
    return result


def _reject_json_constant(value: str) -> None:
    raise ValueError(value)


def _fixed_target() -> Path:
    """Resolve and validate the one permitted target without creating it."""

    try:
        root = Path(REPO_ROOT).resolve(strict=True)
        if not root.is_dir():
            raise AuditWriterError("repository root is not a directory")
        expected = root / "data" / "audit_dev.jsonl"
        data_dir = expected.parent
        if not data_dir.exists() or not data_dir.is_dir():
            raise AuditWriterError("authorized data directory is unavailable")
        if data_dir.is_symlink():
            raise AuditWriterError("authorized data path is indirect")

        target = Path(AUDIT_PATH)
        resolved_target = target.resolve(strict=False)
        resolved_expected = expected.resolve(strict=False)
        if resolved_target != resolved_expected:
            raise AuditWriterError("audit target is outside the repository")
        if target.is_symlink() or expected.is_symlink():
            raise AuditWriterError("audit target is indirect")
        if target.name != "audit_dev.jsonl" or target.parent.resolve() != data_dir.resolve():
            raise AuditWriterError("audit target is not the fixed ledger")
        if target.exists() and not target.is_file():
            raise AuditWriterError("audit target is not a regular file")
        if target.exists() and target.stat().st_nlink > 1:
            raise AuditWriterError("audit target has shared inode")
        return target
    except AuditWriterError:
        raise
    except (OSError, RuntimeError, ValueError) as exc:
        raise AuditWriterError("audit target resolution failed") from exc


def _decode_bytes(raw: bytes) -> list[dict[str, Any]]:
    if not raw:
        return []
    if raw.startswith(b"\xef\xbb\xbf"):
        raise AuditWriterError("audit file has an encoding marker")
    if b"\r" in raw:
        raise AuditWriterError("audit file has non-LF line endings")
    if not raw.endswith(b"\n"):
        raise AuditWriterError("audit file has no final LF")

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise AuditWriterError("audit file is not UTF-8") from exc

    entries: list[dict[str, Any]] = []
    for index, line in enumerate(text.split("\n")[:-1]):
        if not line.strip():
            raise AuditWriterError("audit file contains a blank line", entry_index=index)
        try:
            value = json.loads(
                line,
                object_pairs_hook=_reject_duplicate_object_keys,
                parse_constant=_reject_json_constant,
            )
        except (_DuplicateObjectKeyError, json.JSONDecodeError, ValueError) as exc:
            raise AuditWriterError("audit file contains invalid JSON", entry_index=index) from exc
        if not isinstance(value, dict):
            raise AuditWriterError("audit file entry is not an object", entry_index=index)
        entries.append(value)
    return entries


def _read_bytes(target: Path) -> bytes:
    try:
        with target.open("rb") as handle:
            return handle.read()
    except FileNotFoundError:
        return b""
    except OSError as exc:
        raise AuditWriterError("audit file could not be read") from exc


def _validate_event(event: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(event, Mapping):
        raise AuditWriterError("audit event must be an object")
    try:
        candidate = dict(event)
    except (TypeError, ValueError) as exc:
        raise AuditWriterError("audit event must be an object") from exc
    result = validate_blackboard_message(candidate, "audit_event")
    if not result.get("valid"):
        raise AuditWriterError("audit event schema rejected")
    try:
        canonical_json(candidate)
    except HashChainError as exc:
        raise AuditWriterError("audit event has unsupported canonical values") from exc
    return candidate


def _validate_entries(entries: list[dict[str, Any]]) -> str | None:
    seen_audit_ids: set[str] = set()
    seen_event_ids: set[str] = set()
    previous_hash: str | None = None
    for index, entry in enumerate(entries):
        if not validate_blackboard_message(entry, "audit_event").get("valid"):
            raise AuditWriterError("audit file contains a schema-invalid event", entry_index=index)
        audit_id = entry.get("audit_id")
        event_id = entry.get("event_id")
        if audit_id in seen_audit_ids or event_id in seen_event_ids:
            raise AuditWriterError("audit file contains a duplicate identifier", entry_index=index)
        seen_audit_ids.add(str(audit_id))
        seen_event_ids.add(str(event_id))
        expected_previous = None if index == 0 else previous_hash
        if entry.get("prev_entry_hash") != expected_previous:
            raise AuditWriterError("audit chain is broken", entry_index=index)
        try:
            previous_hash = entry_hash(entry)
        except HashChainError as exc:
            raise AuditWriterError("audit event hash could not be computed", entry_index=index) from exc
    return previous_hash


def _read_and_validate(target: Path) -> tuple[list[dict[str, Any]], str | None]:
    entries = _decode_bytes(_read_bytes(target))
    tail = _validate_entries(entries)
    if entries and not verify_chain(entries):
        # Keep a stable payload-free error even if a future verifier changes.
        raise AuditWriterError("audit chain verification failed")
    return entries, tail


@contextmanager
def _exclusive_append(handle: Any) -> Iterator[None]:
    """Hold an exclusive lock on the authorized ledger for one append."""

    try:
        if os.name == "nt":
            import msvcrt

            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        yield
    except (OSError, ImportError) as exc:
        raise AuditWriterError("audit append lock unavailable") from exc
    finally:
        try:
            if os.name == "nt":
                import msvcrt

                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        except (OSError, ImportError):
            # The append result is already ambiguous if unlock itself fails.
            pass


def read_audit_events() -> list[dict[str, Any]]:
    """Read and verify the complete authorized ledger without writing."""

    target = _fixed_target()
    entries, _ = _read_and_validate(target)
    return entries


def append_audit_event(event: Mapping[str, Any]) -> dict[str, Any]:
    """Append exactly one schema-valid audit event and return chain evidence."""

    candidate = _validate_event(event)
    target = _fixed_target()
    # Validate before opening in append mode, so invalid input never creates a file.
    existing, tail = _read_and_validate(target)
    expected_previous = tail if existing else None
    if candidate.get("prev_entry_hash") != expected_previous:
        raise AuditWriterError("audit event predecessor does not match ledger")
    if candidate["audit_id"] in {entry["audit_id"] for entry in existing}:
        raise AuditWriterError("audit event identifier already exists")
    if candidate["event_id"] in {entry["event_id"] for entry in existing}:
        raise AuditWriterError("audit event identifier already exists")
    try:
        candidate_bytes = canonical_json(candidate) + b"\n"
    except HashChainError as exc:
        raise AuditWriterError("audit event cannot be serialized") from exc

    try:
        with target.open("a+b") as handle:
            with _exclusive_append(handle):
                # Re-resolve and re-check after lock acquisition, then re-read the tail.
                locked_target = _fixed_target()
                if locked_target != target:
                    raise AuditWriterError("audit target changed during append")
                if os.fstat(handle.fileno()).st_nlink > 1:
                    raise AuditWriterError("audit target has shared inode")
                handle.seek(0)
                locked_raw = handle.read()
                locked_entries = _decode_bytes(locked_raw)
                locked_tail = _validate_entries(locked_entries)
                locked_expected = locked_tail if locked_entries else None
                if candidate.get("prev_entry_hash") != locked_expected:
                    raise AuditWriterError("audit event predecessor changed during append")
                if candidate["audit_id"] in {entry["audit_id"] for entry in locked_entries}:
                    raise AuditWriterError("audit event identifier already exists")
                if candidate["event_id"] in {entry["event_id"] for entry in locked_entries}:
                    raise AuditWriterError("audit event identifier already exists")
                handle.seek(0, 2)
                written = handle.write(candidate_bytes)
                if written != len(candidate_bytes):
                    raise AuditWriterError("audit append was incomplete")
                handle.flush()
                os.fsync(handle.fileno())
    except AuditWriterError:
        raise
    except (OSError, ValueError) as exc:
        raise AuditWriterError("audit append failed") from exc

    try:
        final_entries, final_tail = _read_and_validate(target)
    except AuditWriterError as exc:
        raise AuditWriterError("audit append verification failed", entry_index=exc.entry_index) from exc
    if len(final_entries) != len(existing) + 1 or final_tail != entry_hash(candidate):
        raise AuditWriterError("audit append verification failed")
    return {
        "entry_hash": final_tail,
        "chain_length": len(final_entries),
        "verified": True,
        "path": str(target),
    }


__all__ = [
    "AUDIT_PATH",
    "AuditWriterError",
    "REPO_ROOT",
    "append_audit_event",
    "read_audit_events",
]
