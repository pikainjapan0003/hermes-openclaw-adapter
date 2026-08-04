"""Single-session Phase 9 token primitives with no runtime or persistence IO.

The selected T-B design generates a high-entropy value for an Owner-present
ceremony.  Generation is not authorization.  The raw value is deliberately
excluded from representations, errors, bindings, and evidence records.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import re
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Callable

from app.hash_chain import canonical_json


MAX_VALIDITY_SECONDS = 10 * 60
ATTEMPT_NUMBER = 1
TOKEN_CONTRACT_VERSION = "phase9-token-binding-v1"
_DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")
_KEY_ID_RE = re.compile(r"^[A-Za-z0-9._-]{1,32}$")


class Phase9TokenError(ValueError):
    """Payload-free failure raised by token construction or presentation."""


class TokenVerificationCode(str, Enum):
    """Non-secret token verification outcomes."""

    VALID = "VALID"
    DENIED = "DENIED"


@dataclass(frozen=True)
class TokenVerification:
    """A deliberately low-detail fail-closed verification result."""

    valid: bool
    code: TokenVerificationCode


def _utc(value: datetime, field: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise Phase9TokenError(f"{field} must be timezone-aware")
    return value.astimezone(timezone.utc)


def _text(value: str, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise Phase9TokenError(f"{field} must be non-empty")
    return value


def _digest(value: str, field: str) -> str:
    if not isinstance(value, str) or _DIGEST_RE.fullmatch(value) is None:
        raise Phase9TokenError(f"{field} must be a lowercase sha256 digest")
    return value


@dataclass(frozen=True)
class TokenBinding:
    """Canonical non-secret binding for exactly one N=1 presentation."""

    approval_packet_id: str
    approval_packet_hash: str
    evidence_bundle_hash: str
    action_hash: str
    rehearsal_id: str
    issued_at: datetime
    expires_at: datetime
    attempt_number: int
    nonce_digest: str
    contract_version: str

    def __post_init__(self) -> None:
        _text(self.approval_packet_id, "approval_packet_id")
        _digest(self.approval_packet_hash, "approval_packet_hash")
        _digest(self.evidence_bundle_hash, "evidence_bundle_hash")
        _digest(self.action_hash, "action_hash")
        _text(self.rehearsal_id, "rehearsal_id")
        issued = _utc(self.issued_at, "issued_at")
        expires = _utc(self.expires_at, "expires_at")
        if expires <= issued:
            raise Phase9TokenError("expires_at must be after issued_at")
        if expires - issued > timedelta(seconds=MAX_VALIDITY_SECONDS):
            raise Phase9TokenError("token validity exceeds ten minutes")
        if self.attempt_number != ATTEMPT_NUMBER:
            raise Phase9TokenError("attempt_number must be one")
        _digest(self.nonce_digest, "nonce_digest")
        if self.contract_version != TOKEN_CONTRACT_VERSION:
            raise Phase9TokenError("token contract version is not accepted")

    def canonical_record(self) -> dict[str, object]:
        """Return the complete non-secret record used for binding hashes."""

        return {
            "action_hash": self.action_hash,
            "approval_packet_hash": self.approval_packet_hash,
            "approval_packet_id": self.approval_packet_id,
            "attempt_number": self.attempt_number,
            "contract_version": self.contract_version,
            "evidence_bundle_hash": self.evidence_bundle_hash,
            "expires_at": self.expires_at.astimezone(timezone.utc).isoformat(),
            "issued_at": self.issued_at.astimezone(timezone.utc).isoformat(),
            "nonce_digest": self.nonce_digest,
            "rehearsal_id": self.rehearsal_id,
        }

    def digest(self) -> str:
        """Return the canonical binding digest without exposing the token."""

        return hashlib.sha256(canonical_json(self.canonical_record())).hexdigest()


@dataclass(frozen=True)
class TokenPresentation:
    """Caller-observed non-secret values that must match the frozen binding."""

    approval_packet_id: str
    approval_packet_hash: str
    evidence_bundle_hash: str
    action_hash: str
    rehearsal_id: str
    attempt_number: int = ATTEMPT_NUMBER
    contract_version: str = TOKEN_CONTRACT_VERSION

    @classmethod
    def from_binding(cls, binding: TokenBinding) -> "TokenPresentation":
        return cls(
            approval_packet_id=binding.approval_packet_id,
            approval_packet_hash=binding.approval_packet_hash,
            evidence_bundle_hash=binding.evidence_bundle_hash,
            action_hash=binding.action_hash,
            rehearsal_id=binding.rehearsal_id,
            attempt_number=binding.attempt_number,
            contract_version=binding.contract_version,
        )


class IssuedToken:
    """In-memory T-B result whose raw value can be displayed only once."""

    __slots__ = ("binding", "mask_reference", "_raw_value", "_revealed")

    def __init__(
        self,
        *,
        binding: TokenBinding,
        raw_value: str,
        mask_reference: str,
    ) -> None:
        self.binding = binding
        self.mask_reference = mask_reference
        self._raw_value = raw_value
        self._revealed = False

    def __repr__(self) -> str:
        return (
            "IssuedToken(binding_digest="
            f"{self.binding.digest()!r}, mask_reference={self.mask_reference!r}, "
            "raw_value='<REDACTED>')"
        )

    def reveal_for_oob_once(self) -> str:
        """Return the value once for the separately isolated Owner display."""

        if self._revealed:
            raise Phase9TokenError("token display is already consumed")
        self._revealed = True
        return self._raw_value

    def matches(self, candidate: str) -> bool:
        """Compare a presented value without exposing comparison detail."""

        if not isinstance(candidate, str):
            return False
        return hmac.compare_digest(self._raw_value, candidate)


def issue_token(
    *,
    approval_packet_id: str,
    approval_packet_hash: str,
    evidence_bundle_hash: str,
    action_hash: str,
    rehearsal_id: str,
    session_ends_at: datetime,
    session_hmac_key: bytes,
    key_id: str,
    now: datetime,
    validity_seconds: int = MAX_VALIDITY_SECONDS,
    random_bytes: Callable[[int], bytes] = secrets.token_bytes,
) -> IssuedToken:
    """Generate one high-entropy T-B token bound to frozen session inputs."""

    issued_at = _utc(now, "now")
    session_end = _utc(session_ends_at, "session_ends_at")
    if type(validity_seconds) is not int or not 1 <= validity_seconds <= MAX_VALIDITY_SECONDS:
        raise Phase9TokenError("validity_seconds must be between one and 600")
    if session_end <= issued_at:
        raise Phase9TokenError("Owner-present session has already ended")
    if not isinstance(session_hmac_key, bytes) or len(session_hmac_key) < 32:
        raise Phase9TokenError("session HMAC key must contain at least 32 bytes")
    if not isinstance(key_id, str) or _KEY_ID_RE.fullmatch(key_id) is None:
        raise Phase9TokenError("key_id has an invalid format")

    secret_bytes = random_bytes(32)
    if not isinstance(secret_bytes, bytes) or len(secret_bytes) != 32:
        raise Phase9TokenError("token generator did not return 32 bytes")
    raw_value = base64.urlsafe_b64encode(secret_bytes).rstrip(b"=").decode("ascii")
    nonce_digest = hmac.new(
        session_hmac_key,
        raw_value.encode("ascii"),
        hashlib.sha256,
    ).hexdigest()
    expires_at = min(
        issued_at + timedelta(seconds=validity_seconds),
        session_end,
    )
    binding = TokenBinding(
        approval_packet_id=approval_packet_id,
        approval_packet_hash=approval_packet_hash,
        evidence_bundle_hash=evidence_bundle_hash,
        action_hash=action_hash,
        rehearsal_id=rehearsal_id,
        issued_at=issued_at,
        expires_at=expires_at,
        attempt_number=ATTEMPT_NUMBER,
        nonce_digest=nonce_digest,
        contract_version=TOKEN_CONTRACT_VERSION,
    )
    mask_reference = f"token=<REDACTED:hmac-sha256/{key_id}[{nonce_digest[:8]}]>"
    return IssuedToken(
        binding=binding,
        raw_value=raw_value,
        mask_reference=mask_reference,
    )


def verify_token_presentation(
    *,
    issued_token: IssuedToken,
    presented_raw_value: str,
    presentation: TokenPresentation,
    now: datetime,
    session_active: bool,
) -> TokenVerification:
    """Verify freshness, one-session binding, and raw value fail-closed."""

    try:
        observed_at = _utc(now, "now")
    except Phase9TokenError:
        return TokenVerification(False, TokenVerificationCode.DENIED)
    binding = issued_token.binding
    expected = TokenPresentation.from_binding(binding)
    valid = (
        session_active is True
        and observed_at < binding.expires_at.astimezone(timezone.utc)
        and presentation == expected
        and issued_token.matches(presented_raw_value)
    )
    return TokenVerification(
        valid=valid,
        code=TokenVerificationCode.VALID if valid else TokenVerificationCode.DENIED,
    )
