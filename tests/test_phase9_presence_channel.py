"""Concrete, injectable Phase 9 Owner-presence channel tests."""

from __future__ import annotations

import json
import logging
import os
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable

import pytest

from app.phase9_gate import FreshChallenge
from app.phase9_presence import compute_owner_presence
from app.phase9_presence_channel import (
    JsonPresenceChannel,
    PresenceChannelError,
    PresenceEndpoint,
    PresenceRead,
    RegularFilePresenceReader,
)


pytestmark = pytest.mark.contract
NOW = datetime(2026, 8, 7, 8, 0, tzinfo=timezone.utc)
PACKET_HASH = "a" * 64
ACTION_HASH = "b" * 64
CONTRACT_HASH = "c" * 64


def _challenge() -> FreshChallenge:
    return FreshChallenge(
        challenge_id="challenge-final-001",
        rehearsal_id="rehearsal-001",
        approval_packet_hash=PACKET_HASH,
        action_hash=ACTION_HASH,
        issued_at=NOW - timedelta(seconds=1),
        deadline=NOW + timedelta(seconds=30),
    )


def _payload(**changes: object) -> bytes:
    value: dict[str, object] = {
        "action_hash": ACTION_HASH,
        "approval_packet_hash": PACKET_HASH,
        "challenge_id": "challenge-final-001",
        "continuity_id": "continuity-001",
        "owner_confirmed": True,
        "owner_verbatim_authorization_verified": True,
        "rehearsal_id": "rehearsal-001",
    }
    value.update(changes)
    return json.dumps(value, sort_keys=True).encode("utf-8")


class InjectedReader:
    def __init__(
        self,
        *,
        payload: bytes,
        path: Path,
        medium: str,
        principal: str,
        permissions_verified: bool = True,
        observed_at: datetime = NOW,
        failure: Exception | None = None,
    ) -> None:
        self.payload = payload
        self.path = path
        self.medium = medium
        self.principal = principal
        self.permissions_verified = permissions_verified
        self.observed_at = observed_at
        self.failure = failure
        self.calls = 0

    def read(
        self,
        endpoint: PresenceEndpoint,
        *,
        deadline: datetime,
    ) -> PresenceRead:
        del endpoint, deadline
        self.calls += 1
        if self.failure is not None:
            raise self.failure
        return PresenceRead(
            payload=self.payload,
            endpoint_path=self.path,
            medium=self.medium,
            owner_principal=self.principal,
            permissions_verified=self.permissions_verified,
            observed_at=self.observed_at,
        )


def _endpoint(
    path: Path,
    *,
    medium: str = "file",
    gate_principal: str = "uid:1000",
    owner_principal: str = "uid:2000",
) -> PresenceEndpoint:
    return PresenceEndpoint(
        path=path,
        medium=medium,
        gate_principal=gate_principal,
        expected_owner_principal=owner_principal,
        contract_digest=CONTRACT_HASH,
        continuity_id="continuity-001",
    )


def _channel(
    endpoint: PresenceEndpoint,
    reader: InjectedReader | RegularFilePresenceReader,
    *,
    clock: Callable[[], datetime] = lambda: NOW,
) -> JsonPresenceChannel:
    return JsonPresenceChannel(endpoint=endpoint, reader=reader, clock=clock)


@pytest.mark.parametrize(
    ("medium", "path_name", "principal"),
    (
        ("file", "owner-response.json", "uid:2001"),
        ("directory-mailbox", "owner-mailbox", "device:owner-phone"),
    ),
)
def test_two_injected_media_configurations_produce_bound_nonsecret_evidence(
    tmp_path: Path,
    medium: str,
    path_name: str,
    principal: str,
) -> None:
    path = tmp_path / path_name
    endpoint = _endpoint(path, medium=medium, owner_principal=principal)
    reader = InjectedReader(
        payload=_payload(),
        path=path,
        medium=medium,
        principal=principal,
    )

    inputs = _channel(endpoint, reader).collect_after_second_challenge(_challenge())
    result = compute_owner_presence(
        inputs,
        now=NOW,
        final_challenge_issued_at=_challenge().issued_at,
    )

    assert reader.calls == 1
    assert inputs.same_endpoint is False
    assert result.owner_synchronously_present is True
    assert result.owner_response_authenticated is True


def test_same_principal_is_honestly_same_endpoint_and_never_authenticated(
    tmp_path: Path,
) -> None:
    endpoint = _endpoint(
        tmp_path / "separate-looking-path.json",
        gate_principal="uid:1000",
        owner_principal="uid:1000",
    )
    reader = InjectedReader(
        payload=_payload(),
        path=endpoint.path,
        medium=endpoint.medium,
        principal="uid:1000",
    )

    inputs = _channel(endpoint, reader).collect_after_second_challenge(_challenge())
    result = compute_owner_presence(
        inputs,
        now=NOW,
        final_challenge_issued_at=_challenge().issued_at,
    )

    assert inputs.same_endpoint is True
    assert inputs.owner_response_authenticated is not None
    assert inputs.owner_response_authenticated.verified is False
    assert result.owner_response_authenticated is False
    assert result.owner_presence_demonstrated is True
    assert result.owner_synchronously_present is False


@pytest.mark.parametrize(
    "reader",
    (
        InjectedReader(
            payload=_payload(),
            path=Path("/synthetic/missing"),
            medium="file",
            principal="uid:2000",
            failure=FileNotFoundError("SENSITIVE-MISSING-PATH"),
        ),
        InjectedReader(
            payload=_payload(),
            path=Path("/synthetic/permissions"),
            medium="file",
            principal="uid:2000",
            permissions_verified=False,
        ),
        InjectedReader(
            payload=_payload(),
            path=Path("/synthetic/principal"),
            medium="file",
            principal="uid:unexpected",
        ),
        InjectedReader(
            payload=b"{not-json:SENSITIVE-PAYLOAD}",
            path=Path("/synthetic/parse"),
            medium="file",
            principal="uid:2000",
        ),
        InjectedReader(
            payload=_payload(),
            path=Path("/synthetic/expired"),
            medium="file",
            principal="uid:2000",
            observed_at=NOW + timedelta(minutes=11),
        ),
    ),
)
def test_missing_permission_principal_parse_and_timeout_fail_closed_without_leak(
    reader: InjectedReader,
) -> None:
    endpoint = _endpoint(reader.path)

    with pytest.raises(PresenceChannelError) as denial:
        _channel(endpoint, reader).collect_after_second_challenge(_challenge())

    assert str(denial.value) == "owner presence response is unavailable"
    assert "SENSITIVE" not in str(denial.value)


def test_raw_token_shaped_response_is_rejected_without_log_exception_or_file_leak(
    caplog: pytest.LogCaptureFixture,
    tmp_path: Path,
) -> None:
    raw_token = "FAKE-RAW-TOKEN-MUST-NOT-LEAK"
    path = tmp_path / "injected-owner-response"
    value = json.loads(_payload())
    value["raw_token"] = raw_token
    reader = InjectedReader(
        payload=json.dumps(value).encode("utf-8"),
        path=path,
        medium="file",
        principal="uid:2000",
    )

    with caplog.at_level(logging.DEBUG), pytest.raises(PresenceChannelError) as denial:
        _channel(_endpoint(path), reader).collect_after_second_challenge(_challenge())

    assert raw_token not in str(denial.value)
    assert raw_token not in caplog.text
    assert list(tmp_path.iterdir()) == []


def test_regular_file_reader_is_read_only_owner_checked_and_owner_only(
    tmp_path: Path,
) -> None:
    path = tmp_path / "owner-response.json"
    path.write_bytes(_payload())
    path.chmod(0o600)
    endpoint = _endpoint(
        path,
        gate_principal="uid:9999",
        owner_principal=f"uid:{os.getuid()}",
    )
    reader = RegularFilePresenceReader(clock=lambda: NOW)
    before = path.read_bytes()

    inputs = _channel(endpoint, reader).collect_after_second_challenge(_challenge())

    assert inputs.same_endpoint is False
    assert path.read_bytes() == before


def test_validity_configuration_cannot_exceed_ten_minutes(tmp_path: Path) -> None:
    endpoint = _endpoint(tmp_path / "response")

    with pytest.raises(PresenceChannelError):
        replace(endpoint, max_validity_seconds=601)
