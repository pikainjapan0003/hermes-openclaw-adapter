"""Contract tests for the in-memory Phase 9 T-B token primitives."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest

from app.phase9_token import (
    MAX_VALIDITY_SECONDS,
    Phase9TokenError,
    TokenPresentation,
    TokenVerificationCode,
    issue_token,
    verify_token_presentation,
)


pytestmark = pytest.mark.contract


NOW = datetime(2026, 8, 4, 8, 0, tzinfo=timezone.utc)
DIGEST_A = "a" * 64
DIGEST_B = "b" * 64
DIGEST_C = "c" * 64


def _issue(*, key: bytes = b"k" * 32, session_seconds: int = 900):
    return issue_token(
        approval_packet_id="approval-packet-001",
        approval_packet_hash=DIGEST_A,
        evidence_bundle_hash=DIGEST_B,
        action_hash=DIGEST_C,
        rehearsal_id="rehearsal-20260804-001",
        session_ends_at=NOW + timedelta(seconds=session_seconds),
        session_hmac_key=key,
        key_id="session-key-1",
        now=NOW,
        random_bytes=lambda size: b"r" * size,
    )


def test_t_b_token_is_high_entropy_bound_and_redacted() -> None:
    issued = _issue()
    raw = issued.reveal_for_oob_once()

    assert len(raw) == 43
    assert issued.binding.approval_packet_hash == DIGEST_A
    assert issued.binding.evidence_bundle_hash == DIGEST_B
    assert issued.binding.action_hash == DIGEST_C
    assert issued.binding.rehearsal_id == "rehearsal-20260804-001"
    assert issued.binding.expires_at == NOW + timedelta(seconds=MAX_VALIDITY_SECONDS)
    assert issued.mask_reference.startswith(
        "token=<REDACTED:hmac-sha256/session-key-1["
    )
    assert raw not in repr(issued)
    assert raw not in issued.mask_reference
    assert len(issued.binding.digest()) == 64


def test_raw_token_can_be_displayed_only_once() -> None:
    issued = _issue()
    issued.reveal_for_oob_once()

    with pytest.raises(Phase9TokenError, match="display is already consumed"):
        issued.reveal_for_oob_once()


def test_expiry_is_earlier_session_end_when_owner_leaves_first() -> None:
    issued = _issue(session_seconds=75)

    assert issued.binding.expires_at == NOW + timedelta(seconds=75)


def test_each_session_hmac_key_changes_mask_and_nonce_digest() -> None:
    first = _issue(key=b"a" * 32)
    second = _issue(key=b"b" * 32)

    assert first.binding.nonce_digest != second.binding.nonce_digest
    assert first.mask_reference != second.mask_reference


def test_exact_presentation_verifies_without_leaking_detail() -> None:
    issued = _issue()
    raw = issued.reveal_for_oob_once()
    result = verify_token_presentation(
        issued_token=issued,
        presented_raw_value=raw,
        presentation=TokenPresentation.from_binding(issued.binding),
        now=NOW + timedelta(seconds=1),
        session_active=True,
    )

    assert result.valid is True
    assert result.code is TokenVerificationCode.VALID


@pytest.mark.parametrize(
    "mutation",
    [
        "wrong-secret",
        "wrong-packet",
        "wrong-action",
        "wrong-rehearsal",
        "expired",
        "session-ended",
    ],
)
def test_any_presentation_mismatch_fails_closed(mutation: str) -> None:
    issued = _issue()
    raw = issued.reveal_for_oob_once()
    presentation = TokenPresentation.from_binding(issued.binding)
    now = NOW + timedelta(seconds=1)
    active = True
    if mutation == "wrong-secret":
        raw = "not-the-token"
    elif mutation == "wrong-packet":
        presentation = replace(presentation, approval_packet_hash="d" * 64)
    elif mutation == "wrong-action":
        presentation = replace(presentation, action_hash="d" * 64)
    elif mutation == "wrong-rehearsal":
        presentation = replace(presentation, rehearsal_id="different")
    elif mutation == "expired":
        now = NOW + timedelta(seconds=MAX_VALIDITY_SECONDS)
    else:
        active = False

    result = verify_token_presentation(
        issued_token=issued,
        presented_raw_value=raw,
        presentation=presentation,
        now=now,
        session_active=active,
    )

    assert result.valid is False
    assert result.code is TokenVerificationCode.DENIED


@pytest.mark.parametrize(
    ("seconds", "message"),
    [(0, "between one and 600"), (601, "between one and 600")],
)
def test_validity_window_cannot_exceed_frozen_bounds(
    seconds: int,
    message: str,
) -> None:
    with pytest.raises(Phase9TokenError, match=message):
        issue_token(
            approval_packet_id="packet",
            approval_packet_hash=DIGEST_A,
            evidence_bundle_hash=DIGEST_B,
            action_hash=DIGEST_C,
            rehearsal_id="rehearsal",
            session_ends_at=NOW + timedelta(minutes=20),
            session_hmac_key=b"k" * 32,
            key_id="key",
            now=NOW,
            validity_seconds=seconds,
        )


def test_generator_shape_is_fail_closed() -> None:
    with pytest.raises(Phase9TokenError, match="did not return 32 bytes"):
        issue_token(
            approval_packet_id="packet",
            approval_packet_hash=DIGEST_A,
            evidence_bundle_hash=DIGEST_B,
            action_hash=DIGEST_C,
            rehearsal_id="rehearsal",
            session_ends_at=NOW + timedelta(minutes=1),
            session_hmac_key=b"k" * 32,
            key_id="key",
            now=NOW,
            random_bytes=lambda _size: b"short",
        )
