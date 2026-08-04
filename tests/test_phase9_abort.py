"""Tests for all seventeen inert Phase 9 abort decisions."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

import pytest

from app.phase9_abort import (
    REJECTION_FREEZE_THRESHOLD,
    AbortScenario,
    RehearsalFreeze,
    TokenDisposition,
    decide_abort,
)


pytestmark = pytest.mark.contract


def test_abort_catalog_has_exactly_the_seventeen_frozen_scenarios() -> None:
    assert len(AbortScenario) == 17
    assert {scenario.value for scenario in AbortScenario} == {
        "EXECUTABLE_MISSING",
        "CLI_INTERFACE_UNVERIFIED",
        "TIMEOUT",
        "NONZERO_EXIT_OR_SIGNAL",
        "OUTPUT_INVALID",
        "PRECALL_AUDIT_FAILURE",
        "TOKEN_INVALID_OR_REPLAYED",
        "PREFLIGHT_DRIFT",
        "OWNER_STOP_OR_DISCONNECT",
        "FROZEN_INPUT_MISMATCH",
        "UNEXPECTED_SIDE_EFFECT",
        "POSTCALL_AUDIT_FAILURE",
        "CRASH_AFTER_BURN",
        "SECOND_START_OR_RETRY",
        "RAW_TOKEN_EXPOSURE",
        "OOB_ISOLATION_DRIFT",
        "DELIBERATE_BYPASS_SUSPECTED",
    }


@pytest.mark.parametrize("scenario", list(AbortScenario))
def test_every_abort_is_terminal_nonretrying_and_has_no_fallback(
    scenario: AbortScenario,
) -> None:
    decision = decide_abort(scenario, known_fresh_token=True)

    assert decision.terminal_state == "CLOSED_DENY"
    assert decision.executor_allowed is False
    assert decision.retry_permitted is False
    assert decision.freeze_rehearsal is True
    assert decision.owner_notification_required is True
    assert decision.fallback_persistence_allowed is False


@pytest.mark.parametrize(
    "scenario",
    [
        AbortScenario.TIMEOUT,
        AbortScenario.NONZERO_EXIT_OR_SIGNAL,
        AbortScenario.OUTPUT_INVALID,
        AbortScenario.POSTCALL_AUDIT_FAILURE,
        AbortScenario.CRASH_AFTER_BURN,
        AbortScenario.SECOND_START_OR_RETRY,
    ],
)
def test_attempt_or_ambiguous_start_is_permanently_spent(
    scenario: AbortScenario,
) -> None:
    assert decide_abort(scenario).token_disposition is TokenDisposition.BURN_ATTEMPT
    assert (
        decide_abort(AbortScenario.UNEXPECTED_SIDE_EFFECT, process_started=True)
        .token_disposition
        is TokenDisposition.BURN_ATTEMPT
    )


def test_raw_exposure_and_oob_drift_revoke_without_retry() -> None:
    assert (
        decide_abort(AbortScenario.RAW_TOKEN_EXPOSURE).token_disposition
        is TokenDisposition.REVOKE_OR_EXPIRE
    )
    assert (
        decide_abort(AbortScenario.OOB_ISOLATION_DRIFT).token_disposition
        is TokenDisposition.REVOKE_OR_EXPIRE
    )


def test_suspected_deliberate_bypass_is_spent_or_unsafe_not_solved() -> None:
    decision = decide_abort(AbortScenario.DELIBERATE_BYPASS_SUSPECTED)

    assert decision.token_disposition is TokenDisposition.SPENT_OR_UNSAFE
    assert decision.retry_permitted is False


def test_first_rejection_freezes_rehearsal_irreversibly() -> None:
    freeze = RehearsalFreeze("rehearsal-001")

    assert REJECTION_FREEZE_THRESHOLD == 1
    assert freeze.frozen is False
    assert freeze.reject() == 1
    assert freeze.frozen is True
    assert freeze.reject() == 2
    assert freeze.frozen is True


def test_concurrent_rejections_cannot_unfreeze_or_lose_count() -> None:
    freeze = RehearsalFreeze("rehearsal-concurrent")

    with ThreadPoolExecutor(max_workers=8) as pool:
        counts = list(pool.map(lambda _item: freeze.reject(), range(32)))

    assert sorted(counts) == list(range(1, 33))
    assert freeze.rejection_count == 32
    assert freeze.frozen is True
