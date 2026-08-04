"""Truth-table and §6.17 tests for computed Phase 9 Owner presence."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from app.phase9_presence import (
    EvidenceSource,
    PredicateEvidence,
    PresenceInputs,
    compute_owner_presence,
)


pytestmark = pytest.mark.contract

CHALLENGE_AT = datetime(2026, 8, 4, 9, 0, tzinfo=timezone.utc)
NOW = CHALLENGE_AT + timedelta(seconds=2)


def _evidence(
    *,
    green: bool = True,
    source: EvidenceSource = EvidenceSource.GATE_VERIFICATION,
    observed_at: datetime = CHALLENGE_AT + timedelta(seconds=1),
    valid_until: datetime = CHALLENGE_AT + timedelta(minutes=1),
) -> PredicateEvidence:
    return PredicateEvidence(
        verified=green,
        observed_at=observed_at,
        valid_until=valid_until,
        source=source,
        evidence_digest="e" * 64,
    )


def _inputs(mask: int, *, same_endpoint: bool = True) -> PresenceInputs:
    values = [bool(mask & (1 << index)) for index in range(6)]
    return PresenceInputs(
        same_endpoint=same_endpoint,
        owner_channel_contract_approved=_evidence(green=values[0]),
        best_effort_isolation_attested=_evidence(
            green=values[1], source=EvidenceSource.ISOLATION_PROBE
        ),
        fresh_challenge_bound=_evidence(
            green=values[2], source=EvidenceSource.OOB_CHANNEL
        ),
        owner_verbatim_authorization_verified=_evidence(
            green=values[3], source=EvidenceSource.OWNER_PROCEDURE
        ),
        final_presence_reconfirmed=_evidence(
            green=values[4], source=EvidenceSource.OOB_CHANNEL
        ),
        channel_continuity_green=_evidence(
            green=values[5], source=EvidenceSource.ISOLATION_PROBE
        ),
        owner_presence_demonstrated=_evidence(source=EvidenceSource.OOB_CHANNEL),
        owner_response_authenticated=_evidence(
            source=EvidenceSource.OWNER_AUTHENTICATOR
        ),
    )


@pytest.mark.parametrize("mask", range(64))
def test_all_64_six_predicate_truth_table_rows_use_one_and(mask: int) -> None:
    result = compute_owner_presence(
        _inputs(mask),
        now=NOW,
        final_challenge_issued_at=CHALLENGE_AT,
    )

    expected = tuple(bool(mask & (1 << index)) for index in range(6))
    assert result.six_predicates() == expected
    assert result.owner_synchronously_present is (mask == 63)


def test_same_endpoint_echo_cannot_light_criterion_four() -> None:
    inputs = _inputs(63)
    inputs = PresenceInputs(
        **{
            **inputs.__dict__,
            "owner_verbatim_authorization_verified": None,
        }
    )

    result = compute_owner_presence(
        inputs,
        now=NOW,
        final_challenge_issued_at=CHALLENGE_AT,
    )

    assert result.owner_presence_demonstrated is True
    assert result.owner_response_authenticated is False
    assert result.owner_authorization_evidence_green is False
    assert result.owner_synchronously_present is False


def test_different_endpoint_owner_authenticator_can_light_criterion_four() -> None:
    inputs = _inputs(63, same_endpoint=False)
    inputs = PresenceInputs(
        **{
            **inputs.__dict__,
            "owner_verbatim_authorization_verified": None,
        }
    )

    result = compute_owner_presence(
        inputs,
        now=NOW,
        final_challenge_issued_at=CHALLENGE_AT,
    )

    assert result.owner_response_authenticated is True
    assert result.owner_authorization_evidence_green is True
    assert result.owner_synchronously_present is True


@pytest.mark.parametrize(
    "bad_evidence",
    [
        None,
        _evidence(green=False),
        _evidence(source=EvidenceSource.CALLER_CLAIM),
        _evidence(source=EvidenceSource.UNKNOWN),
        _evidence(observed_at=CHALLENGE_AT - timedelta(seconds=1)),
        _evidence(valid_until=NOW),
    ],
)
def test_missing_false_caller_claim_stale_or_expired_evidence_is_false(
    bad_evidence: PredicateEvidence | None,
) -> None:
    inputs = _inputs(63)
    inputs = PresenceInputs(
        **{
            **inputs.__dict__,
            "owner_channel_contract_approved": bad_evidence,
        }
    )

    result = compute_owner_presence(
        inputs,
        now=NOW,
        final_challenge_issued_at=CHALLENGE_AT,
    )

    assert result.owner_channel_contract_approved is False
    assert result.owner_synchronously_present is False


def test_naive_or_future_clock_evidence_fails_closed() -> None:
    inputs = _inputs(63)

    naive = compute_owner_presence(
        inputs,
        now=NOW.replace(tzinfo=None),
        final_challenge_issued_at=CHALLENGE_AT,
    )
    future = compute_owner_presence(
        inputs,
        now=CHALLENGE_AT - timedelta(seconds=1),
        final_challenge_issued_at=CHALLENGE_AT,
    )

    assert naive.owner_synchronously_present is False
    assert future.owner_synchronously_present is False
