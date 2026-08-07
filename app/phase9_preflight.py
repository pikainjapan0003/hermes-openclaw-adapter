"""Concrete fail-closed Phase 9 request verifier and coordination lock.

The verifier freezes only a canonical digest of non-secret request material.
Every verification recomputes that digest from the live ``GateRequest``; no
caller-supplied boolean can make the result green.  The coordination lock is
the process-local half of the burn boundary.  Its mutex is mandatory so all
participating components must deliberately share the same object, while the
burn ledger remains responsible for cross-process exclusion.
"""

from __future__ import annotations

import hashlib
import math
import secrets
from datetime import datetime, timezone
from typing import Protocol

from app.hash_chain import HashChainError, canonical_json
from app.phase9_gate import (
    ActionRequest,
    GateRequest,
    Phase9AuditAuthorizationRecord,
)
from app.phase9_token import IssuedToken, TokenPresentation


DEFAULT_MAXIMUM_LOCK_WAIT_SECONDS = 5.0


class FrozenRequestError(ValueError):
    """Payload-free failure raised while freezing an invalid request."""


class CoordinationLockError(RuntimeError):
    """Payload-free failure raised when the shared mutex cannot be used."""


class Mutex(Protocol):
    """Minimal injected mutex surface; one instance must be shared."""

    def acquire(self, blocking: bool = True, timeout: float = -1) -> bool:
        """Acquire the shared process-local mutex."""

    def release(self) -> None:
        """Release a successfully acquired mutex."""


def _utc_text(value: datetime) -> str:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise FrozenRequestError("frozen request is invalid")
    return value.astimezone(timezone.utc).isoformat()


def _authorization_record(
    record: Phase9AuditAuthorizationRecord | None,
) -> dict[str, object] | None:
    if record is None:
        return None
    if not isinstance(record, Phase9AuditAuthorizationRecord):
        raise FrozenRequestError("frozen request is invalid")
    return {
        "authorized_at": _utc_text(record.authorized_at),
        "owner_instruction_digest": record.owner_instruction_digest,
        "record_id": record.record_id,
        "rehearsal_id": record.rehearsal_id,
        "scope": record.scope,
        "valid_until": _utc_text(record.valid_until),
    }


def _request_record(request: GateRequest) -> dict[str, object]:
    if not isinstance(request, GateRequest):
        raise FrozenRequestError("frozen request is invalid")
    if not isinstance(request.issued_token, IssuedToken):
        raise FrozenRequestError("frozen request is invalid")
    if not isinstance(request.token_presentation, TokenPresentation):
        raise FrozenRequestError("frozen request is invalid")
    if not isinstance(request.action, ActionRequest):
        raise FrozenRequestError("frozen request is invalid")
    if not isinstance(request.initial_challenge_id, str) or not request.initial_challenge_id:
        raise FrozenRequestError("frozen request is invalid")
    if type(request.session_active) is not bool:
        raise FrozenRequestError("frozen request is invalid")
    if not isinstance(request.system_display_strings, tuple) or not all(
        isinstance(item, str) for item in request.system_display_strings
    ):
        raise FrozenRequestError("frozen request is invalid")

    binding = request.issued_token.binding
    presentation = request.token_presentation
    display_digests = [
        hashlib.sha256(item.encode("utf-8")).hexdigest()
        for item in request.system_display_strings
    ]
    return {
        "action": request.action.canonical_record(),
        "audit_authorization": _authorization_record(
            request.phase9_audit_authorization
        ),
        "initial_challenge_id": request.initial_challenge_id,
        "issued_token_binding": binding.canonical_record(),
        "issued_token_binding_digest": binding.digest(),
        "mask_reference": request.issued_token.mask_reference,
        "session_active": request.session_active,
        "system_display_digests": display_digests,
        "token_presentation": {
            "action_hash": presentation.action_hash,
            "approval_packet_hash": presentation.approval_packet_hash,
            "approval_packet_id": presentation.approval_packet_id,
            "attempt_number": presentation.attempt_number,
            "contract_version": presentation.contract_version,
            "evidence_bundle_hash": presentation.evidence_bundle_hash,
            "rehearsal_id": presentation.rehearsal_id,
        },
    }


def _request_digest(request: GateRequest) -> str:
    return hashlib.sha256(canonical_json(_request_record(request))).hexdigest()


class FrozenGateRequestVerifier:
    """Recompute and compare one frozen non-secret GateRequest digest."""

    def __init__(self, *, expected_digest: str) -> None:
        if (
            not isinstance(expected_digest, str)
            or len(expected_digest) != 64
            or any(character not in "0123456789abcdef" for character in expected_digest)
        ):
            raise FrozenRequestError("expected digest is invalid")
        self._expected_digest = expected_digest

    @classmethod
    def freeze(cls, request: GateRequest) -> "FrozenGateRequestVerifier":
        """Freeze a request digest without retaining raw display text or token data."""

        try:
            digest = _request_digest(request)
        except (FrozenRequestError, HashChainError, TypeError, ValueError) as exc:
            raise FrozenRequestError("frozen request is invalid") from exc
        return cls(expected_digest=digest)

    @property
    def expected_digest(self) -> str:
        """Expose only the non-secret canonical digest for evidence records."""

        return self._expected_digest

    def verify(self, request: GateRequest) -> bool:
        """Return false for missing, uncertain, malformed, or changed material."""

        try:
            observed = _request_digest(request)
        except (FrozenRequestError, HashChainError, RuntimeError, TypeError, ValueError):
            return False
        return secrets.compare_digest(observed, self._expected_digest)


class BoundedGateTokenAuditCoordinationLock:
    """Mandatory shared process mutex with finite acquisition waits only."""

    def __init__(
        self,
        *,
        mutex: Mutex,
        maximum_wait_seconds: float = DEFAULT_MAXIMUM_LOCK_WAIT_SECONDS,
    ) -> None:
        if mutex is None or not callable(getattr(mutex, "acquire", None)):
            raise CoordinationLockError("coordination mutex is invalid")
        if not callable(getattr(mutex, "release", None)):
            raise CoordinationLockError("coordination mutex is invalid")
        if (
            isinstance(maximum_wait_seconds, bool)
            or not isinstance(maximum_wait_seconds, (int, float))
            or not math.isfinite(float(maximum_wait_seconds))
            or float(maximum_wait_seconds) <= 0
        ):
            raise CoordinationLockError("coordination wait bound is invalid")
        self._mutex = mutex
        self._maximum_wait_seconds = float(maximum_wait_seconds)

    def acquire(self, blocking: bool = True, timeout: float = -1) -> bool:
        """Acquire within the configured bound or fail without an unbounded wait."""

        if type(blocking) is not bool:
            raise CoordinationLockError("coordination lock request is invalid")
        try:
            if not blocking:
                if timeout != -1:
                    raise CoordinationLockError(
                        "coordination lock request is invalid"
                    )
                return self._mutex.acquire(False)
            if (
                isinstance(timeout, bool)
                or not isinstance(timeout, (int, float))
                or not math.isfinite(float(timeout))
                or not 0 <= float(timeout) <= self._maximum_wait_seconds
            ):
                raise CoordinationLockError("coordination lock request is invalid")
            return self._mutex.acquire(True, float(timeout))
        except CoordinationLockError:
            raise
        except Exception as exc:
            raise CoordinationLockError("coordination lock is unavailable") from exc

    def release(self) -> None:
        """Release explicitly; an underlying failure remains visible to the gate."""

        try:
            self._mutex.release()
        except Exception as exc:
            raise CoordinationLockError("coordination lock release failed") from exc


__all__ = [
    "BoundedGateTokenAuditCoordinationLock",
    "CoordinationLockError",
    "DEFAULT_MAXIMUM_LOCK_WAIT_SECONDS",
    "FrozenGateRequestVerifier",
    "FrozenRequestError",
    "Mutex",
]
