"""Fail-closed Phase 9 abort classifications and rejection freeze state.

The module implements the seventeen reviewed abort classes as inert decisions.
It performs no runtime stop, audit write, retry, dispatch, or persistence work.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass
from enum import Enum


REJECTION_FREEZE_THRESHOLD = 1


class AbortScenario(str, Enum):
    """The seventeen frozen scenarios from PHASE9_ABORT_PLAYBOOK.md."""

    EXECUTABLE_MISSING = "EXECUTABLE_MISSING"
    CLI_INTERFACE_UNVERIFIED = "CLI_INTERFACE_UNVERIFIED"
    TIMEOUT = "TIMEOUT"
    NONZERO_EXIT_OR_SIGNAL = "NONZERO_EXIT_OR_SIGNAL"
    OUTPUT_INVALID = "OUTPUT_INVALID"
    PRECALL_AUDIT_FAILURE = "PRECALL_AUDIT_FAILURE"
    TOKEN_INVALID_OR_REPLAYED = "TOKEN_INVALID_OR_REPLAYED"
    PREFLIGHT_DRIFT = "PREFLIGHT_DRIFT"
    OWNER_STOP_OR_DISCONNECT = "OWNER_STOP_OR_DISCONNECT"
    FROZEN_INPUT_MISMATCH = "FROZEN_INPUT_MISMATCH"
    UNEXPECTED_SIDE_EFFECT = "UNEXPECTED_SIDE_EFFECT"
    POSTCALL_AUDIT_FAILURE = "POSTCALL_AUDIT_FAILURE"
    CRASH_AFTER_BURN = "CRASH_AFTER_BURN"
    SECOND_START_OR_RETRY = "SECOND_START_OR_RETRY"
    RAW_TOKEN_EXPOSURE = "RAW_TOKEN_EXPOSURE"
    OOB_ISOLATION_DRIFT = "OOB_ISOLATION_DRIFT"
    DELIBERATE_BYPASS_SUSPECTED = "DELIBERATE_BYPASS_SUSPECTED"


class TokenDisposition(str, Enum):
    """Non-secret terminal token accounting."""

    NONE = "NONE"
    BURN_DENY = "BURN_DENY"
    BURN_ATTEMPT = "BURN_ATTEMPT"
    REVOKE_OR_EXPIRE = "REVOKE_OR_EXPIRE"
    SPENT_OR_UNSAFE = "SPENT_OR_UNSAFE"


@dataclass(frozen=True)
class AbortDecision:
    """Inert evidence describing the mandatory response to one failure."""

    scenario: AbortScenario
    terminal_state: str
    token_disposition: TokenDisposition
    executor_allowed: bool
    retry_permitted: bool
    freeze_rehearsal: bool
    owner_notification_required: bool
    fallback_persistence_allowed: bool


def decide_abort(
    scenario: AbortScenario,
    *,
    process_started: bool = False,
    known_fresh_token: bool = False,
) -> AbortDecision:
    """Return the fixed fail-closed disposition without taking side effects."""

    if not isinstance(scenario, AbortScenario):
        raise ValueError("unknown Phase 9 abort scenario")

    if scenario is AbortScenario.DELIBERATE_BYPASS_SUSPECTED:
        disposition = TokenDisposition.SPENT_OR_UNSAFE
    elif scenario in {
        AbortScenario.TIMEOUT,
        AbortScenario.NONZERO_EXIT_OR_SIGNAL,
        AbortScenario.OUTPUT_INVALID,
        AbortScenario.POSTCALL_AUDIT_FAILURE,
        AbortScenario.CRASH_AFTER_BURN,
        AbortScenario.SECOND_START_OR_RETRY,
    } or process_started:
        disposition = TokenDisposition.BURN_ATTEMPT
    elif scenario in {
        AbortScenario.RAW_TOKEN_EXPOSURE,
        AbortScenario.OOB_ISOLATION_DRIFT,
    }:
        disposition = TokenDisposition.REVOKE_OR_EXPIRE
    elif known_fresh_token:
        disposition = TokenDisposition.BURN_DENY
    else:
        disposition = TokenDisposition.NONE

    return AbortDecision(
        scenario=scenario,
        terminal_state="CLOSED_DENY",
        token_disposition=disposition,
        executor_allowed=False,
        retry_permitted=False,
        freeze_rehearsal=True,
        owner_notification_required=True,
        fallback_persistence_allowed=False,
    )


class RehearsalFreeze:
    """Thread-safe threshold-one freeze with no reset or retry transition."""

    def __init__(self, rehearsal_id: str) -> None:
        if not isinstance(rehearsal_id, str) or not rehearsal_id.strip():
            raise ValueError("rehearsal_id must be non-empty")
        self.rehearsal_id = rehearsal_id
        self._rejections = 0
        self._frozen = False
        self._lock = threading.Lock()

    @property
    def rejection_count(self) -> int:
        with self._lock:
            return self._rejections

    @property
    def frozen(self) -> bool:
        with self._lock:
            return self._frozen

    def reject(self) -> int:
        """Record one denial and irreversibly freeze at the selected threshold."""

        with self._lock:
            self._rejections += 1
            if self._rejections >= REJECTION_FREEZE_THRESHOLD:
                self._frozen = True
            return self._rejections

    def freeze(self) -> None:
        """Irreversibly close the rehearsal after any terminal event."""

        with self._lock:
            self._frozen = True
