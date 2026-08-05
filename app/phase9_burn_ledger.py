"""Cross-process, append-only burn ledger for the disconnected Phase 9 gate.

The caller must inject an explicit path.  This module never selects ``data/``,
creates directories, or connects the gate to a runtime.  Its operating-system
lock is the cross-process half of the two-layer coordination contract.
"""

from __future__ import annotations

import hashlib
import importlib
import json
import os
import threading
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, BinaryIO, Callable, Iterator, Protocol, cast

from app.hash_chain import HashChainError, canonical_json
from app.phase9_gate import BurnReceipt, BurnRecord


_LOCK_POLL_SECONDS = 0.01


class _WindowsFileLockApi(Protocol):
    LK_NBLCK: int
    LK_UNLCK: int

    def locking(self, descriptor: int, mode: int, byte_count: int) -> None: ...


class _PosixFileLockApi(Protocol):
    LOCK_EX: int
    LOCK_NB: int
    LOCK_UN: int

    def flock(self, descriptor: int, operation: int) -> None: ...


def _windows_file_lock_api() -> _WindowsFileLockApi:
    return cast(_WindowsFileLockApi, importlib.import_module("msvcrt"))


def _posix_file_lock_api() -> _PosixFileLockApi:
    return cast(_PosixFileLockApi, importlib.import_module("fcntl"))


class BurnLedgerError(RuntimeError):
    """Payload-free failure at the Phase 9 burn-ledger boundary."""


class FileBurnLedger:
    """JSONL burn ledger with an OS-level, cross-process exclusive lock.

    The two ``threading.Lock`` instances below only serialize callers and
    protect handle state inside this Python object.  They do not provide
    cross-process exclusion; that guarantee comes only from the OS file lock.
    """

    def __init__(
        self,
        target: Path,
        *,
        fsync_fn: Callable[[int], None] = os.fsync,
        monotonic_fn: Callable[[], float] = time.monotonic,
        sleep_fn: Callable[[float], None] = time.sleep,
    ) -> None:
        self._target = Path(target)
        self._fsync = fsync_fn
        self._monotonic = monotonic_fn
        self._sleep = sleep_fn
        self._instance_call_lock = threading.Lock()
        self._active_handle_lock = threading.Lock()
        self._active_handle: BinaryIO | None = None
        self._active_owner_thread_id: int | None = None

    @property
    def target(self) -> Path:
        return self._target

    def _try_lock_once(self, handle: BinaryIO) -> None:
        """Try the host OS lock once without blocking.

        Unlike ``audit_writer_local`` (which uses blocking ``LOCK_EX`` /
        ``LK_LOCK``), this ledger deliberately polls the non-blocking forms so
        it can honor the bounded ``timeout_seconds`` contract.
        """

        if os.name == "nt":
            msvcrt = _windows_file_lock_api()

            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            fcntl = _posix_file_lock_api()

            fcntl.flock(
                handle.fileno(),
                fcntl.LOCK_EX | fcntl.LOCK_NB,
            )

    def _acquire_os_lock(self, handle: BinaryIO, timeout_seconds: float) -> None:
        if not isinstance(timeout_seconds, (int, float)) or timeout_seconds <= 0:
            raise BurnLedgerError("burn ledger lock timeout is invalid")
        deadline = self._monotonic() + float(timeout_seconds)
        while True:
            try:
                self._try_lock_once(handle)
                return
            except (OSError, ImportError) as exc:
                if self._monotonic() >= deadline:
                    raise BurnLedgerError("burn ledger lock unavailable") from exc
                self._sleep(
                    min(_LOCK_POLL_SECONDS, max(0.0, deadline - self._monotonic()))
                )

    @staticmethod
    def _release_os_lock(handle: BinaryIO) -> None:
        try:
            if os.name == "nt":
                msvcrt = _windows_file_lock_api()

                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl = _posix_file_lock_api()

                fcntl.flock(
                    handle.fileno(),
                    fcntl.LOCK_UN,
                )
        except (OSError, ImportError) as exc:
            raise BurnLedgerError("burn ledger unlock failed") from exc

    @contextmanager
    def exclusive_lock(self, *, timeout_seconds: float) -> Iterator[None]:
        """Hold both lock layers for one bounded replay-check/burn cycle.

        The instance lock is process-local object-state protection only.  It
        deliberately shares one timeout budget with the OS-level file lock;
        it is not a substitute for cross-process exclusion.
        """

        if not isinstance(timeout_seconds, (int, float)) or timeout_seconds <= 0:
            raise BurnLedgerError("burn ledger lock timeout is invalid")
        deadline = self._monotonic() + float(timeout_seconds)
        remaining = max(0.0, deadline - self._monotonic())
        if not self._instance_call_lock.acquire(timeout=remaining):
            raise BurnLedgerError("burn ledger lock unavailable")
        instance_acquired = True
        handle: BinaryIO | None = None
        acquired = False
        try:
            try:
                handle = self._target.open("a+b")
            except (OSError, ValueError) as exc:
                raise BurnLedgerError("burn ledger could not be opened") from exc
            remaining = deadline - self._monotonic()
            if remaining <= 0:
                raise BurnLedgerError("burn ledger lock unavailable")
            self._acquire_os_lock(handle, remaining)
            acquired = True
            with self._active_handle_lock:
                self._active_handle = handle
                self._active_owner_thread_id = threading.get_ident()
            yield
        finally:
            try:
                with self._active_handle_lock:
                    self._active_handle = None
                    self._active_owner_thread_id = None
                try:
                    if acquired and handle is not None:
                        self._release_os_lock(handle)
                finally:
                    if handle is not None:
                        handle.close()
            finally:
                if instance_acquired:
                    self._instance_call_lock.release()

    def _active_handle_for_caller(self) -> BinaryIO | None:
        """Return the active handle only to its owning thread."""

        with self._active_handle_lock:
            if self._active_owner_thread_id != threading.get_ident():
                return None
            return self._active_handle

    @staticmethod
    def _decode_records(raw: bytes) -> list[dict[str, Any]]:
        if not raw:
            return []
        records: list[dict[str, Any]] = []
        try:
            text = raw.decode("utf-8")
            for line in text.splitlines():
                if not line:
                    raise BurnLedgerError("burn ledger contains an empty record")
                value = json.loads(line)
                if not isinstance(value, dict):
                    raise BurnLedgerError("burn ledger record is not an object")
                token_digest = value.get("token_digest")
                if not isinstance(token_digest, str) or len(token_digest) != 64:
                    raise BurnLedgerError("burn ledger record digest is invalid")
                records.append(value)
        except BurnLedgerError:
            raise
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise BurnLedgerError("burn ledger cannot be decoded") from exc
        return records

    def _read_physical_records(self) -> list[dict[str, Any]]:
        handle = self._active_handle_for_caller()
        if handle is not None:
            try:
                handle.flush()
                handle.seek(0)
                return self._decode_records(handle.read())
            except BurnLedgerError:
                raise
            except (OSError, ValueError) as exc:
                raise BurnLedgerError("burn ledger could not be read") from exc
        try:
            with self._target.open("rb") as reader:
                return self._decode_records(reader.read())
        except FileNotFoundError:
            return []
        except BurnLedgerError:
            raise
        except (OSError, ValueError) as exc:
            raise BurnLedgerError("burn ledger could not be read") from exc

    def contains(self, token_digest: str) -> bool:
        """Re-read the physical ledger; no in-memory replay cache is trusted."""

        if not isinstance(token_digest, str) or len(token_digest) != 64:
            raise BurnLedgerError("token digest is invalid")
        return any(
            record.get("token_digest") == token_digest
            for record in self._read_physical_records()
        )

    def commit(self, record: BurnRecord) -> BurnReceipt:
        """Append, fsync, and read back one redacted burn record."""

        handle = self._active_handle_for_caller()
        if handle is None:
            raise BurnLedgerError("burn commit requires the exclusive ledger lock")
        payload = record.safe_record()
        try:
            encoded = canonical_json(payload)
        except HashChainError as exc:
            raise BurnLedgerError("burn record cannot be serialized") from exc
        record_digest = hashlib.sha256(encoded).hexdigest()
        handle.seek(0, 2)
        try:
            written = handle.write(encoded + b"\n")
            if written != len(encoded) + 1:
                raise BurnLedgerError("burn append was incomplete")
            handle.flush()
        except BurnLedgerError:
            raise
        except (OSError, ValueError) as exc:
            raise BurnLedgerError("burn append failed") from exc
        try:
            self._fsync(handle.fileno())
        except OSError:
            return BurnReceipt(
                record.token_digest,
                record_digest,
                durable=False,
                verified=False,
            )
        records = self._read_physical_records()
        verified = bool(records) and records[-1] == payload
        return BurnReceipt(
            record.token_digest,
            record_digest,
            durable=True,
            verified=verified,
        )


__all__ = ["BurnLedgerError", "FileBurnLedger"]
