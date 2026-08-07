"""Owner-present, one-shot Phase 9 token issuance boundary.

The formal constructor is deliberately locked for this implementation batch:
it references the production CSPRNG but cannot reach it until a separately
authorized execution-day presence verifier replaces the locked verifier.  The
issuer returns only an ``IssuedToken`` whose one display has already been
consumed plus non-secret receipt data; the raw value is sent once to the
injected Owner egress and is never logged, persisted, named, or returned.
"""

from __future__ import annotations

import secrets
import threading
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, NoReturn, Protocol

from app.phase9_abort import REJECTION_FREEZE_THRESHOLD, RehearsalFreeze
from app.phase9_token import IssuedToken, issue_token


ISSUANCE_LOCK_TIMEOUT_SECONDS = 5.0


class TokenIssuanceError(RuntimeError):
    """Payload-free terminal denial; the session cannot retry."""


@dataclass(frozen=True)
class TokenIssuanceRequest:
    """Frozen N=1 binding and validity inputs; it contains no raw token."""

    approval_packet_id: str
    approval_packet_hash: str
    evidence_bundle_hash: str
    action_hash: str
    rehearsal_id: str
    session_ends_at: datetime
    now: datetime
    validity_seconds: int
    key_id: str


@dataclass(frozen=True)
class OwnerPresenceProof:
    """Non-secret evidence handle evaluated by an injected verifier."""

    rehearsal_id: str
    approval_packet_hash: str
    action_hash: str
    observed_at: datetime
    valid_until: datetime
    evidence_digest: str


class OwnerPresenceVerifier(Protocol):
    def verify(
        self,
        proof: OwnerPresenceProof,
        *,
        request: TokenIssuanceRequest,
    ) -> bool:
        """Recompute execution-day Owner presence; caller claims are insufficient."""


class OwnerTokenEgress(Protocol):
    def display_once(
        self,
        raw_value: str,
        *,
        mask_reference: str,
        expires_at: datetime,
    ) -> bool:
        """Display once on the separately authorized Owner endpoint."""


class ExecutionDayAuthorizationRequiredVerifier:
    """Current formal-path lock: implementation authorization is not execution."""

    def verify(
        self,
        proof: OwnerPresenceProof,
        *,
        request: TokenIssuanceRequest,
    ) -> bool:
        del proof, request
        return False


@dataclass(frozen=True)
class TokenIssuanceReceipt:
    """Non-secret issuance evidence safe for logs and audit records."""

    rehearsal_id: str
    approval_packet_hash: str
    action_hash: str
    binding_digest: str
    mask_reference: str
    expires_at: datetime
    egress_confirmed: bool
    retry_permitted: bool = False


@dataclass(frozen=True)
class IssuedTokenPackage:
    """Consumed-display token object plus a non-secret receipt."""

    issued_token: IssuedToken
    receipt: TokenIssuanceReceipt


class Phase9TokenIssuer:
    """Issue and display at most one token, freezing on the first rejection."""

    def __init__(
        self,
        *,
        rehearsal_id: str,
        presence_verifier: OwnerPresenceVerifier,
        owner_egress: OwnerTokenEgress,
        random_bytes: Callable[[int], bytes],
    ) -> None:
        if not isinstance(rehearsal_id, str) or not rehearsal_id.strip():
            raise TokenIssuanceError("token issuance configuration is invalid")
        if not callable(getattr(presence_verifier, "verify", None)):
            raise TokenIssuanceError("token issuance configuration is invalid")
        if not callable(getattr(owner_egress, "display_once", None)):
            raise TokenIssuanceError("token issuance configuration is invalid")
        if not callable(random_bytes):
            raise TokenIssuanceError("token issuance configuration is invalid")
        self.rehearsal_id = rehearsal_id
        self.presence_verifier = presence_verifier
        self.owner_egress = owner_egress
        self._random_bytes = random_bytes
        self.freeze = RehearsalFreeze(rehearsal_id)
        self._issuance_lock = threading.Lock()

    @classmethod
    def for_formal_runtime(
        cls,
        *,
        rehearsal_id: str,
        owner_egress: OwnerTokenEgress,
    ) -> "Phase9TokenIssuer":
        """Build the CSPRNG path while keeping execution-day issuance locked."""

        return cls(
            rehearsal_id=rehearsal_id,
            presence_verifier=ExecutionDayAuthorizationRequiredVerifier(),
            owner_egress=owner_egress,
            random_bytes=secrets.token_bytes,
        )

    @property
    def rejection_freeze_threshold(self) -> int:
        return REJECTION_FREEZE_THRESHOLD

    def _deny(self) -> NoReturn:
        if not self.freeze.frozen:
            self.freeze.reject()
        raise TokenIssuanceError("token issuance denied")

    def _presence_green(
        self,
        proof: OwnerPresenceProof,
        request: TokenIssuanceRequest,
    ) -> bool:
        try:
            result = self.presence_verifier.verify(proof, request=request)
        except Exception:
            result = False
        return result is True

    def issue(
        self,
        request: TokenIssuanceRequest,
        *,
        presence_proof: OwnerPresenceProof,
    ) -> IssuedTokenPackage:
        """Verify presence, generate, display once, and irreversibly close."""

        acquired = self._issuance_lock.acquire(
            timeout=ISSUANCE_LOCK_TIMEOUT_SECONDS
        )
        if not acquired:
            self._deny()
        try:
            if self.freeze.frozen:
                self._deny()
            if (
                not isinstance(request, TokenIssuanceRequest)
                or not isinstance(presence_proof, OwnerPresenceProof)
                or request.rehearsal_id != self.rehearsal_id
                or presence_proof.rehearsal_id != self.rehearsal_id
                or presence_proof.approval_packet_hash
                != request.approval_packet_hash
                or presence_proof.action_hash != request.action_hash
                or not self._presence_green(presence_proof, request)
            ):
                self._deny()

            generated: IssuedToken | None = None
            try:
                session_hmac_key = self._random_bytes(32)
                generated = issue_token(
                    approval_packet_id=request.approval_packet_id,
                    approval_packet_hash=request.approval_packet_hash,
                    evidence_bundle_hash=request.evidence_bundle_hash,
                    action_hash=request.action_hash,
                    rehearsal_id=request.rehearsal_id,
                    session_ends_at=request.session_ends_at,
                    session_hmac_key=session_hmac_key,
                    key_id=request.key_id,
                    now=request.now,
                    validity_seconds=request.validity_seconds,
                    random_bytes=self._random_bytes,
                )
            except Exception:
                generated = None
            if generated is None:
                self._deny()

            raw_value = generated.reveal_for_oob_once()
            delivered = False
            try:
                delivered = self.owner_egress.display_once(
                    raw_value,
                    mask_reference=generated.mask_reference,
                    expires_at=generated.binding.expires_at,
                )
            except Exception:
                delivered = False
            if delivered is not True:
                self._deny()

            receipt = TokenIssuanceReceipt(
                rehearsal_id=request.rehearsal_id,
                approval_packet_hash=request.approval_packet_hash,
                action_hash=request.action_hash,
                binding_digest=generated.binding.digest(),
                mask_reference=generated.mask_reference,
                expires_at=generated.binding.expires_at,
                egress_confirmed=True,
            )
            self.freeze.freeze()
            return IssuedTokenPackage(generated, receipt)
        finally:
            self._issuance_lock.release()


__all__ = [
    "ExecutionDayAuthorizationRequiredVerifier",
    "ISSUANCE_LOCK_TIMEOUT_SECONDS",
    "IssuedTokenPackage",
    "OwnerPresenceProof",
    "OwnerPresenceVerifier",
    "OwnerTokenEgress",
    "Phase9TokenIssuer",
    "TokenIssuanceError",
    "TokenIssuanceReceipt",
    "TokenIssuanceRequest",
]
