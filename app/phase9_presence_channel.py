"""Fail-closed, injectable Owner-presence channel for Phase 9.

The channel turns one bounded, non-secret JSON response into
``PredicateEvidence`` objects. It never accepts or returns a raw token. The
medium is deliberately injected so the execution-day ceremony can choose a
regular file, FIFO, directory protocol, or off-host adapter without changing
the gate. Only the regular-file reader is supplied here; other media must
implement the same read-only protocol.
"""

from __future__ import annotations

import hashlib
import json
import re
import stat
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable, Protocol

from app.hash_chain import HashChainError, canonical_json
from app.phase9_gate import FreshChallenge
from app.phase9_presence import EvidenceSource, PredicateEvidence, PresenceInputs


MAX_PRESENCE_VALIDITY_SECONDS = 10 * 60
MAX_RESPONSE_BYTES = 64 * 1024
_DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")
_ALLOWED_RESPONSE_KEYS = frozenset(
    {
        "action_hash",
        "approval_packet_hash",
        "challenge_id",
        "continuity_id",
        "owner_confirmed",
        "owner_verbatim_authorization_verified",
        "rehearsal_id",
    }
)
class PresenceChannelError(RuntimeError):
    """Payload-free fail-closed response for an unusable Owner channel."""


@dataclass(frozen=True)
class PresenceEndpoint:
    """Frozen endpoint identity supplied by the execution-day coordinator."""

    path: Path
    medium: str
    gate_principal: str
    expected_owner_principal: str
    contract_digest: str
    continuity_id: str
    max_validity_seconds: int = MAX_PRESENCE_VALIDITY_SECONDS

    def __post_init__(self) -> None:
        if not isinstance(self.path, Path):
            raise PresenceChannelError("presence endpoint configuration is invalid")
        for value in (
            self.medium,
            self.gate_principal,
            self.expected_owner_principal,
            self.continuity_id,
        ):
            if not isinstance(value, str) or not value.strip():
                raise PresenceChannelError("presence endpoint configuration is invalid")
        if _DIGEST_RE.fullmatch(self.contract_digest) is None:
            raise PresenceChannelError("presence endpoint configuration is invalid")
        if (
            type(self.max_validity_seconds) is not int
            or not 1 <= self.max_validity_seconds <= MAX_PRESENCE_VALIDITY_SECONDS
        ):
            raise PresenceChannelError("presence endpoint configuration is invalid")


@dataclass(frozen=True)
class PresenceRead:
    """Read-only endpoint observation; payload is consumed inside the channel."""

    payload: bytes
    endpoint_path: Path
    medium: str
    owner_principal: str
    permissions_verified: bool
    observed_at: datetime


class PresenceReader(Protocol):
    """Injectable read-only boundary for file, FIFO, directory, or remote media."""

    def read(
        self,
        endpoint: PresenceEndpoint,
        *,
        deadline: datetime,
    ) -> PresenceRead:
        """Return one bounded observation or raise without exposing payload data."""


class RegularFilePresenceReader:
    """Read one owner-only regular file without following symlinks or writing."""

    def __init__(self, *, clock: Callable[[], datetime]) -> None:
        self._clock = clock

    def read(
        self,
        endpoint: PresenceEndpoint,
        *,
        deadline: datetime,
    ) -> PresenceRead:
        try:
            before = _as_utc(self._clock())
            if before is None or before >= deadline:
                raise PresenceChannelError("owner presence response is unavailable")
            details = endpoint.path.lstat()
            if not stat.S_ISREG(details.st_mode) or endpoint.path.is_symlink():
                raise PresenceChannelError("owner presence response is unavailable")
            permissions_verified = stat.S_IMODE(details.st_mode) & 0o077 == 0
            with endpoint.path.open("rb") as handle:
                payload = handle.read(MAX_RESPONSE_BYTES + 1)
            observed = _as_utc(self._clock())
            if observed is None or observed >= deadline or len(payload) > MAX_RESPONSE_BYTES:
                raise PresenceChannelError("owner presence response is unavailable")
            return PresenceRead(
                payload=payload,
                endpoint_path=endpoint.path,
                medium="file",
                owner_principal=f"uid:{details.st_uid}",
                permissions_verified=permissions_verified,
                observed_at=observed,
            )
        except PresenceChannelError:
            raise
        except (OSError, ValueError) as exc:
            raise PresenceChannelError(
                "owner presence response is unavailable"
            ) from exc


def _as_utc(value: datetime) -> datetime | None:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        return None
    return value.astimezone(timezone.utc)


def _decode_response(raw: bytes) -> dict[str, object]:
    if not isinstance(raw, bytes) or not raw or len(raw) > MAX_RESPONSE_BYTES:
        raise PresenceChannelError("owner presence response is unavailable")
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PresenceChannelError("owner presence response is unavailable") from exc
    if not isinstance(value, dict) or set(value) != _ALLOWED_RESPONSE_KEYS:
        raise PresenceChannelError("owner presence response is unavailable")
    return value


class JsonPresenceChannel:
    """Convert one injected endpoint response into non-secret presence evidence."""

    def __init__(
        self,
        *,
        endpoint: PresenceEndpoint,
        reader: PresenceReader,
        clock: Callable[[], datetime],
    ) -> None:
        self._endpoint = endpoint
        self._reader = reader
        self._clock = clock

    @staticmethod
    def _evidence(
        *,
        verified: bool,
        observed_at: datetime,
        valid_until: datetime,
        source: EvidenceSource,
        digest: str,
    ) -> PredicateEvidence:
        return PredicateEvidence(
            verified=verified,
            observed_at=observed_at,
            valid_until=valid_until,
            source=source,
            evidence_digest=digest,
        )

    def collect_after_second_challenge(
        self,
        challenge: FreshChallenge,
    ) -> PresenceInputs:
        """Read once, verify bindings, and return evidence without raw secrets."""

        try:
            now = _as_utc(self._clock())
            issued_at = _as_utc(challenge.issued_at)
            challenge_deadline = _as_utc(challenge.deadline)
            if (
                now is None
                or issued_at is None
                or challenge_deadline is None
                or not issued_at <= now < challenge_deadline
            ):
                raise PresenceChannelError("owner presence response is unavailable")
            read = self._reader.read(
                self._endpoint,
                deadline=challenge_deadline,
            )
            observed = _as_utc(read.observed_at)
            if (
                observed is None
                or not issued_at <= observed < challenge_deadline
                or read.endpoint_path != self._endpoint.path
                or read.medium != self._endpoint.medium
                or read.owner_principal != self._endpoint.expected_owner_principal
                or read.permissions_verified is not True
            ):
                raise PresenceChannelError("owner presence response is unavailable")
            response = _decode_response(read.payload)
            expected = {
                "action_hash": challenge.action_hash,
                "approval_packet_hash": challenge.approval_packet_hash,
                "challenge_id": challenge.challenge_id,
                "continuity_id": self._endpoint.continuity_id,
                "rehearsal_id": challenge.rehearsal_id,
            }
            if any(response.get(key) != value for key, value in expected.items()):
                raise PresenceChannelError("owner presence response is unavailable")
            if response.get("owner_confirmed") is not True:
                raise PresenceChannelError("owner presence response is unavailable")
            verbatim = response.get("owner_verbatim_authorization_verified")
            if type(verbatim) is not bool:
                raise PresenceChannelError("owner presence response is unavailable")
            valid_until = min(
                challenge_deadline,
                observed + timedelta(seconds=self._endpoint.max_validity_seconds),
            )
            if valid_until <= observed:
                raise PresenceChannelError("owner presence response is unavailable")
            safe_record = {
                **expected,
                "contract_digest": self._endpoint.contract_digest,
                "medium": self._endpoint.medium,
                "owner_confirmed": True,
                "owner_principal": read.owner_principal,
                "owner_verbatim_authorization_verified": verbatim,
                "observed_at": observed.isoformat(),
            }
            digest = hashlib.sha256(canonical_json(safe_record)).hexdigest()
        except PresenceChannelError:
            raise
        except (HashChainError, OSError, RuntimeError, TypeError, ValueError) as exc:
            raise PresenceChannelError("owner presence response is unavailable") from exc

        same_endpoint = read.owner_principal == self._endpoint.gate_principal
        channel = self._evidence(
            verified=True,
            observed_at=observed,
            valid_until=valid_until,
            source=EvidenceSource.GATE_VERIFICATION,
            digest=digest,
        )
        isolation = self._evidence(
            verified=not same_endpoint,
            observed_at=observed,
            valid_until=valid_until,
            source=EvidenceSource.ISOLATION_PROBE,
            digest=digest,
        )
        bound = self._evidence(
            verified=True,
            observed_at=observed,
            valid_until=valid_until,
            source=EvidenceSource.OOB_CHANNEL,
            digest=digest,
        )
        procedure = self._evidence(
            verified=verbatim,
            observed_at=observed,
            valid_until=valid_until,
            source=EvidenceSource.OWNER_PROCEDURE,
            digest=digest,
        )
        authenticated = self._evidence(
            verified=not same_endpoint,
            observed_at=observed,
            valid_until=valid_until,
            source=EvidenceSource.OWNER_AUTHENTICATOR,
            digest=digest,
        )
        return PresenceInputs(
            same_endpoint=same_endpoint,
            owner_channel_contract_approved=channel,
            best_effort_isolation_attested=isolation,
            fresh_challenge_bound=bound,
            final_presence_reconfirmed=bound,
            channel_continuity_green=bound,
            owner_presence_demonstrated=bound,
            owner_response_authenticated=authenticated,
            owner_verbatim_authorization_verified=procedure,
        )


__all__ = [
    "JsonPresenceChannel",
    "MAX_PRESENCE_VALIDITY_SECONDS",
    "PresenceChannelError",
    "PresenceEndpoint",
    "PresenceRead",
    "PresenceReader",
    "RegularFilePresenceReader",
]
