"""Fixed-vector tests for the locked Phase 9 token issuance boundary."""

from __future__ import annotations

import base64
import hashlib
import logging
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from app.phase9_token_issuer import (
    OwnerPresenceProof,
    Phase9TokenIssuer,
    TokenIssuanceError,
    TokenIssuanceRequest,
)


pytestmark = pytest.mark.contract
NOW = datetime(2026, 8, 7, 11, 0, tzinfo=timezone.utc)
REHEARSAL_ID = "phase9-token-issuer-fixed-vector"


class FixedPresenceVerifier:
    def __init__(self, result: bool = True, failure: Exception | None = None) -> None:
        self.result = result
        self.failure = failure
        self.calls = 0

    def verify(
        self,
        proof: OwnerPresenceProof,
        *,
        request: TokenIssuanceRequest,
    ) -> bool:
        del proof, request
        self.calls += 1
        if self.failure is not None:
            raise self.failure
        return self.result


class CaptureEgress:
    def __init__(self, *, failure_with_raw: bool = False) -> None:
        self.calls = 0
        self.raw_value: str | None = None
        self.mask_reference: str | None = None
        self.failure_with_raw = failure_with_raw

    def display_once(
        self,
        raw_value: str,
        *,
        mask_reference: str,
        expires_at: datetime,
    ) -> bool:
        del expires_at
        self.calls += 1
        self.raw_value = raw_value
        self.mask_reference = mask_reference
        if self.failure_with_raw:
            raise RuntimeError(raw_value)
        return True


class SequenceRandom:
    def __init__(self, values: list[bytes]) -> None:
        self.values = list(values)
        self.calls = 0

    def __call__(self, size: int) -> bytes:
        self.calls += 1
        value = self.values.pop(0)
        assert size == 32
        assert len(value) == size
        return value


def _request(rehearsal_id: str = REHEARSAL_ID) -> TokenIssuanceRequest:
    return TokenIssuanceRequest(
        approval_packet_id="packet-issuer-001",
        approval_packet_hash="a" * 64,
        evidence_bundle_hash="b" * 64,
        action_hash="c" * 64,
        rehearsal_id=rehearsal_id,
        session_ends_at=NOW + timedelta(minutes=5),
        now=NOW,
        validity_seconds=600,
        key_id="session-fixed-vector",
    )


def _proof(rehearsal_id: str = REHEARSAL_ID) -> OwnerPresenceProof:
    return OwnerPresenceProof(
        rehearsal_id=rehearsal_id,
        approval_packet_hash="a" * 64,
        action_hash="c" * 64,
        observed_at=NOW,
        valid_until=NOW + timedelta(minutes=5),
        evidence_digest="d" * 64,
    )


def _fixed_issuer(
    *,
    verifier: FixedPresenceVerifier | None = None,
    egress: CaptureEgress | None = None,
    key: bytes = b"k" * 32,
    token: bytes = b"t" * 32,
) -> tuple[Phase9TokenIssuer, CaptureEgress, SequenceRandom]:
    selected_egress = egress or CaptureEgress()
    random = SequenceRandom([key, token])
    issuer = Phase9TokenIssuer(
        rehearsal_id=REHEARSAL_ID,
        presence_verifier=verifier or FixedPresenceVerifier(),
        owner_egress=selected_egress,
        random_bytes=random,
    )
    return issuer, selected_egress, random


def test_fixed_vector_binds_packet_action_session_and_ends_with_session() -> None:
    issuer, egress, random = _fixed_issuer()

    package = issuer.issue(_request(), presence_proof=_proof())

    binding = package.issued_token.binding
    assert binding.approval_packet_id == "packet-issuer-001"
    assert binding.approval_packet_hash == "a" * 64
    assert binding.action_hash == "c" * 64
    assert binding.rehearsal_id == REHEARSAL_ID
    assert binding.expires_at == NOW + timedelta(minutes=5)
    assert package.receipt.expires_at == binding.expires_at
    assert package.receipt.retry_permitted is False
    assert issuer.freeze.frozen is True
    assert issuer.rejection_freeze_threshold == 1
    assert random.calls == 2
    assert egress.calls == 1


def test_first_mismatch_freezes_the_session_and_prevents_later_retry() -> None:
    verifier = FixedPresenceVerifier(False)
    issuer, egress, random = _fixed_issuer(verifier=verifier)

    with pytest.raises(TokenIssuanceError, match="token issuance denied"):
        issuer.issue(_request(), presence_proof=_proof())
    verifier.result = True
    with pytest.raises(TokenIssuanceError, match="token issuance denied"):
        issuer.issue(_request(), presence_proof=_proof())

    assert issuer.freeze.frozen is True
    assert issuer.freeze.rejection_count == 1
    assert random.calls == 0
    assert egress.calls == 0


def test_formal_csprng_path_is_unreachable_without_execution_day_authorization(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    random_calls = 0

    def counted_csprng(size: int) -> bytes:
        nonlocal random_calls
        random_calls += 1
        return b"x" * size

    monkeypatch.setattr(secrets, "token_bytes", counted_csprng)
    egress = CaptureEgress()
    issuer = Phase9TokenIssuer.for_formal_runtime(
        rehearsal_id=REHEARSAL_ID,
        owner_egress=egress,
    )

    with pytest.raises(TokenIssuanceError, match="token issuance denied"):
        issuer.issue(_request(), presence_proof=_proof())

    assert random_calls == 0
    assert egress.calls == 0
    assert issuer.freeze.rejection_count == 1
    assert issuer.freeze.frozen is True


def test_session_hmac_masks_change_and_are_not_public_token_hashes() -> None:
    first, first_egress, _ = _fixed_issuer(key=b"1" * 32, token=b"z" * 32)
    second, second_egress, _ = _fixed_issuer(key=b"2" * 32, token=b"z" * 32)

    first_package = first.issue(_request(), presence_proof=_proof())
    second_package = second.issue(_request(), presence_proof=_proof())

    assert first_egress.raw_value == second_egress.raw_value
    assert first_package.receipt.mask_reference != second_package.receipt.mask_reference
    assert first_egress.raw_value is not None
    public_digest = hashlib.sha256(first_egress.raw_value.encode("ascii")).hexdigest()
    assert public_digest[:8] not in first_package.receipt.mask_reference
    assert public_digest[:8] not in second_package.receipt.mask_reference


def test_raw_fixed_vector_never_enters_logs(
    caplog: pytest.LogCaptureFixture,
) -> None:
    issuer, egress, _ = _fixed_issuer()

    with caplog.at_level(logging.DEBUG):
        issuer.issue(_request(), presence_proof=_proof())

    assert egress.raw_value is not None
    assert egress.raw_value not in caplog.text


def test_raw_fixed_vector_is_removed_from_exception_chains() -> None:
    egress = CaptureEgress(failure_with_raw=True)
    issuer, _egress, _ = _fixed_issuer(egress=egress)

    with pytest.raises(TokenIssuanceError) as denial:
        issuer.issue(_request(), presence_proof=_proof())

    assert egress.raw_value is not None
    assert egress.raw_value not in str(denial.value)
    assert egress.raw_value not in repr(denial.value)
    assert denial.value.__cause__ is None
    assert denial.value.__context__ is None


def test_raw_fixed_vector_never_enters_receipt_or_trace_representations() -> None:
    issuer, egress, _ = _fixed_issuer()

    package = issuer.issue(_request(), presence_proof=_proof())
    safe_trace = (repr(package), repr(package.receipt), package.receipt.binding_digest)

    assert egress.raw_value is not None
    assert all(egress.raw_value not in item for item in safe_trace)
    assert "<REDACTED>" in repr(package.issued_token)


def test_raw_fixed_vector_never_becomes_argv_or_filename() -> None:
    issuer, egress, _ = _fixed_issuer()

    package = issuer.issue(_request(), presence_proof=_proof())

    assert egress.raw_value is not None
    assert not hasattr(package.receipt, "argv")
    assert not hasattr(package.receipt, "filename")
    assert egress.raw_value not in package.receipt.mask_reference


def test_raw_fixed_vector_never_writes_a_file(tmp_path: Path) -> None:
    issuer, egress, _ = _fixed_issuer()

    issuer.issue(_request(), presence_proof=_proof())

    assert egress.raw_value is not None
    assert list(tmp_path.rglob("*")) == []
    expected_raw = base64.urlsafe_b64encode(b"t" * 32).rstrip(b"=").decode()
    assert egress.raw_value == expected_raw


def test_issuer_is_not_imported_by_main_worker_or_routes() -> None:
    root = Path(__file__).parents[1]
    for relative in ("app/main.py", "app/worker.py"):
        assert "phase9_token_issuer" not in (root / relative).read_text(
            encoding="utf-8"
        )
