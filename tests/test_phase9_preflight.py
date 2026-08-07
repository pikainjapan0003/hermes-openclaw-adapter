"""Concrete Phase 9 frozen-request verifier and bounded-lock tests."""

from __future__ import annotations

import threading
import time
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest

from app.phase9_gate import (
    ActionRequest,
    GateRequest,
    PHASE9_AUDIT_AUTHORIZATION_GRANT_SHA256,
    PHASE9_AUDIT_SCOPE,
    Phase9AuditAuthorizationRecord,
)
from app.phase9_preflight import (
    BoundedGateTokenAuditCoordinationLock,
    CoordinationLockError,
    FrozenGateRequestVerifier,
    FrozenRequestError,
)
from app.phase9_token import TokenPresentation, issue_token


pytestmark = pytest.mark.contract
NOW = datetime(2026, 8, 7, 9, 0, tzinfo=timezone.utc)


def _request() -> GateRequest:
    action = ActionRequest(
        action_name="n1_harmless_query",
        target="target-local-demo",
        message="Return one harmless local status summary.",
        requested_cli_timeout_seconds=30,
        gate_timeout_seconds=12,
        agent_id="main",
        model_id="safe-model",
    )
    issued = issue_token(
        approval_packet_id="packet-001",
        approval_packet_hash="a" * 64,
        evidence_bundle_hash="b" * 64,
        action_hash=action.digest(),
        rehearsal_id="rehearsal-001",
        session_ends_at=NOW + timedelta(minutes=5),
        session_hmac_key=b"h" * 32,
        key_id="session-001",
        now=NOW,
        random_bytes=lambda size: b"t" * size,
    )
    return GateRequest(
        issued_token=issued,
        token_presentation=TokenPresentation.from_binding(issued.binding),
        action=action,
        system_display_strings=("safe digest view",),
        initial_challenge_id="initial-challenge",
        session_active=True,
        phase9_audit_authorization=Phase9AuditAuthorizationRecord(
            record_id="owner-audit-auth-001",
            rehearsal_id="rehearsal-001",
            scope=PHASE9_AUDIT_SCOPE,
            owner_instruction_digest=PHASE9_AUDIT_AUTHORIZATION_GRANT_SHA256,
            authorized_at=NOW - timedelta(seconds=1),
            valid_until=NOW + timedelta(minutes=3),
        ),
    )


def test_frozen_verifier_recomputes_the_live_request() -> None:
    request = _request()
    verifier = FrozenGateRequestVerifier.freeze(request)

    assert verifier.verify(request) is True
    assert len(verifier.expected_digest) == 64


@pytest.mark.parametrize(
    "mutation",
    (
        lambda request: replace(
            request,
            action=replace(request.action, target="changed-target"),
        ),
        lambda request: replace(
            request,
            token_presentation=replace(
                request.token_presentation,
                approval_packet_id="changed-packet",
            ),
        ),
        lambda request: replace(request, session_active=False),
        lambda request: replace(request, phase9_audit_authorization=None),
        lambda request: replace(
            request,
            system_display_strings=("changed display",),
        ),
    ),
)
def test_frozen_verifier_fails_closed_for_changed_material(
    mutation: Any,
) -> None:
    request = _request()
    verifier = FrozenGateRequestVerifier.freeze(request)

    assert verifier.verify(mutation(request)) is False


def test_frozen_verifier_fails_closed_for_missing_or_uncertain_material(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    request = _request()
    verifier = FrozenGateRequestVerifier.freeze(request)

    assert verifier.verify(None) is False  # type: ignore[arg-type]
    monkeypatch.setattr(
        "app.phase9_preflight._request_digest",
        lambda _request: (_ for _ in ()).throw(RuntimeError("uncertain")),
    )
    assert verifier.verify(request) is False


def test_invalid_expected_digest_cannot_create_a_green_verifier() -> None:
    with pytest.raises(FrozenRequestError, match="expected digest is invalid"):
        FrozenGateRequestVerifier(expected_digest="caller-says-green")


def test_shared_coordination_lock_is_mutually_exclusive_and_bounded() -> None:
    shared_mutex = threading.Lock()
    first = BoundedGateTokenAuditCoordinationLock(
        mutex=shared_mutex,
        maximum_wait_seconds=0.2,
    )
    second = BoundedGateTokenAuditCoordinationLock(
        mutex=shared_mutex,
        maximum_wait_seconds=0.2,
    )
    observations: list[tuple[bool, float]] = []
    assert first.acquire(timeout=0.1) is True

    def contend() -> None:
        started = time.monotonic()
        acquired = second.acquire(timeout=0.05)
        observations.append((acquired, time.monotonic() - started))

    contender = threading.Thread(target=contend)
    contender.start()
    contender.join(timeout=0.5)
    first.release()

    assert contender.is_alive() is False
    assert observations and observations[0][0] is False
    assert 0.02 <= observations[0][1] < 0.5
    assert second.acquire(timeout=0.1) is True
    second.release()


class FailingMutex:
    def acquire(self, blocking: bool = True, timeout: float = -1) -> bool:
        del blocking, timeout
        raise OSError("sensitive mutex detail")

    def release(self) -> None:
        raise OSError("sensitive mutex detail")


def test_coordination_lock_errors_are_payload_free_and_fail_closed() -> None:
    lock = BoundedGateTokenAuditCoordinationLock(mutex=FailingMutex())

    with pytest.raises(CoordinationLockError) as acquire_denial:
        lock.acquire(timeout=0.01)
    with pytest.raises(CoordinationLockError) as release_denial:
        lock.release()

    assert str(acquire_denial.value) == "coordination lock is unavailable"
    assert str(release_denial.value) == "coordination lock release failed"
    assert "sensitive" not in str(acquire_denial.value)
    assert "sensitive" not in str(release_denial.value)


@pytest.mark.parametrize("timeout", (-1, float("nan"), float("inf"), 5.1))
def test_coordination_lock_rejects_unbounded_or_overlong_waits(timeout: float) -> None:
    lock = BoundedGateTokenAuditCoordinationLock(
        mutex=threading.Lock(),
        maximum_wait_seconds=5.0,
    )

    started = time.monotonic()
    with pytest.raises(CoordinationLockError):
        lock.acquire(timeout=timeout)

    assert time.monotonic() - started < 0.5
