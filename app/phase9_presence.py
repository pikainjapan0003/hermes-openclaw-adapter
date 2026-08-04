"""Computed six-predicate Owner-presence accounting for Phase 9.

No public API accepts a caller's bare ``owner_synchronously_present`` boolean.
Every predicate is derived from fresh, verifiable evidence and combined with a
single AND.  Same-endpoint returns demonstrate presence only; they never become
Owner authentication evidence.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum


class EvidenceSource(str, Enum):
    """Sources that distinguish verified evidence from caller assertions."""

    GATE_VERIFICATION = "GATE_VERIFICATION"
    ISOLATION_PROBE = "ISOLATION_PROBE"
    OOB_CHANNEL = "OOB_CHANNEL"
    OWNER_PROCEDURE = "OWNER_PROCEDURE"
    OWNER_AUTHENTICATOR = "OWNER_AUTHENTICATOR"
    CALLER_CLAIM = "CALLER_CLAIM"
    UNKNOWN = "UNKNOWN"


_VERIFIABLE_SOURCES = frozenset(
    {
        EvidenceSource.GATE_VERIFICATION,
        EvidenceSource.ISOLATION_PROBE,
        EvidenceSource.OOB_CHANNEL,
        EvidenceSource.OWNER_PROCEDURE,
        EvidenceSource.OWNER_AUTHENTICATOR,
    }
)


@dataclass(frozen=True)
class PredicateEvidence:
    """Time-bounded, non-secret evidence for one gate predicate."""

    verified: bool
    observed_at: datetime
    valid_until: datetime
    source: EvidenceSource
    evidence_digest: str


@dataclass(frozen=True)
class PresenceInputs:
    """Evidence inputs used to recompute the six predicates after challenge 2."""

    same_endpoint: bool
    owner_channel_contract_approved: PredicateEvidence | None
    best_effort_isolation_attested: PredicateEvidence | None
    fresh_challenge_bound: PredicateEvidence | None
    final_presence_reconfirmed: PredicateEvidence | None
    channel_continuity_green: PredicateEvidence | None
    owner_presence_demonstrated: PredicateEvidence | None = None
    owner_response_authenticated: PredicateEvidence | None = None
    owner_verbatim_authorization_verified: PredicateEvidence | None = None


@dataclass(frozen=True)
class PresenceResult:
    """Complete accounting result, including the §6.17 semantic split."""

    owner_channel_contract_approved: bool
    best_effort_isolation_attested: bool
    fresh_challenge_bound: bool
    owner_authorization_evidence_green: bool
    final_presence_reconfirmed: bool
    channel_continuity_green: bool
    owner_presence_demonstrated: bool
    owner_response_authenticated: bool
    owner_verbatim_authorization_verified: bool
    owner_synchronously_present: bool

    def six_predicates(self) -> tuple[bool, bool, bool, bool, bool, bool]:
        return (
            self.owner_channel_contract_approved,
            self.best_effort_isolation_attested,
            self.fresh_challenge_bound,
            self.owner_authorization_evidence_green,
            self.final_presence_reconfirmed,
            self.channel_continuity_green,
        )


def _as_utc(value: datetime) -> datetime | None:
    if value.tzinfo is None or value.utcoffset() is None:
        return None
    return value.astimezone(timezone.utc)


def _evidence_green(
    evidence: PredicateEvidence | None,
    *,
    now: datetime,
    not_before: datetime,
) -> bool:
    if evidence is None or evidence.verified is not True:
        return False
    if evidence.source not in _VERIFIABLE_SOURCES:
        return False
    observed = _as_utc(evidence.observed_at)
    expires = _as_utc(evidence.valid_until)
    if observed is None or expires is None:
        return False
    if not evidence.evidence_digest:
        return False
    return not_before <= observed <= now < expires


def compute_owner_presence(
    inputs: PresenceInputs,
    *,
    now: datetime,
    final_challenge_issued_at: datetime,
) -> PresenceResult:
    """Recompute all six predicates from post-challenge evidence as one AND."""

    observed_now = _as_utc(now)
    challenge_time = _as_utc(final_challenge_issued_at)
    if observed_now is None or challenge_time is None or challenge_time > observed_now:
        false_now = datetime.min.replace(tzinfo=timezone.utc)
        observed_now = false_now
        challenge_time = datetime.max.replace(tzinfo=timezone.utc)

    channel = _evidence_green(
        inputs.owner_channel_contract_approved,
        now=observed_now,
        not_before=challenge_time,
    )
    isolation = _evidence_green(
        inputs.best_effort_isolation_attested,
        now=observed_now,
        not_before=challenge_time,
    )
    challenge = _evidence_green(
        inputs.fresh_challenge_bound,
        now=observed_now,
        not_before=challenge_time,
    )
    final_presence = _evidence_green(
        inputs.final_presence_reconfirmed,
        now=observed_now,
        not_before=challenge_time,
    )
    continuity = _evidence_green(
        inputs.channel_continuity_green,
        now=observed_now,
        not_before=challenge_time,
    )
    presence_demonstrated = _evidence_green(
        inputs.owner_presence_demonstrated,
        now=observed_now,
        not_before=challenge_time,
    )
    authenticated = _evidence_green(
        inputs.owner_response_authenticated,
        now=observed_now,
        not_before=challenge_time,
    )
    verbatim = _evidence_green(
        inputs.owner_verbatim_authorization_verified,
        now=observed_now,
        not_before=challenge_time,
    )

    if inputs.same_endpoint:
        # §6.17: echo demonstrates liveness only.  It cannot authenticate.
        authenticated = False
        authorization = verbatim
    else:
        authorization = authenticated or verbatim

    six = (
        channel,
        isolation,
        challenge,
        authorization,
        final_presence,
        continuity,
    )
    return PresenceResult(
        owner_channel_contract_approved=channel,
        best_effort_isolation_attested=isolation,
        fresh_challenge_bound=challenge,
        owner_authorization_evidence_green=authorization,
        final_presence_reconfirmed=final_presence,
        channel_continuity_green=continuity,
        owner_presence_demonstrated=presence_demonstrated,
        owner_response_authenticated=authenticated,
        owner_verbatim_authorization_verified=verbatim,
        owner_synchronously_present=all(six),
    )
