"""Real-filesystem and decision-parity tests for the read-only OOB checker."""

from __future__ import annotations

import io
import os
import pwd
import stat
from pathlib import Path

import pytest

from app.phase9_presence_channel import (
    DedicatedGroupPolicy,
    dedicated_group_access_verified,
)
from scripts.check_phase9_oob_wiring import (
    OobFileObservation,
    _observe_regular_file,
    _principal_name,
    check_oob_wiring,
    main,
)


pytestmark = pytest.mark.contract
GATE_UID = 1000
OWNER_UID = 1001
GROUP_GID = 77
GROUP_NAME = "test-phase9-oob"
GROUP_MEMBERS = frozenset({GATE_UID, OWNER_UID})


def test_p6_observe_regular_file_reports_real_metadata_without_mutation(
    tmp_path: Path,
) -> None:
    endpoint = tmp_path / "owner-response.json"
    endpoint.write_bytes(b"owner-response")
    endpoint.chmod(0o640)
    before = endpoint.read_bytes()

    observation = _observe_regular_file(endpoint)

    assert observation.writer_uid == os.getuid()
    assert observation.group_gid == endpoint.lstat().st_gid
    assert stat.S_IMODE(observation.file_mode) == 0o640
    assert endpoint.read_bytes() == before


@pytest.mark.parametrize("kind", ["directory", "symlink", "fifo"])
def test_p6_observe_regular_file_rejects_nonregular_entries(
    tmp_path: Path,
    kind: str,
) -> None:
    endpoint = tmp_path / "owner-response.json"
    if kind == "directory":
        endpoint.mkdir()
    elif kind == "symlink":
        target = tmp_path / "target.json"
        target.write_text("{}", encoding="utf-8")
        endpoint.symlink_to(target)
    else:
        os.mkfifo(endpoint)

    with pytest.raises(OSError, match="not a regular file"):
        _observe_regular_file(endpoint)


def test_p6_principal_name_uses_real_system_lookup_and_payload_free_fallback() -> None:
    current_uid = os.getuid()

    assert _principal_name(current_uid) == pwd.getpwuid(current_uid).pw_name
    assert _principal_name(2**31 - 1) == f"uid {2**31 - 1}"


@pytest.mark.parametrize(
    ("file_mode", "file_gid", "member_uids"),
    [
        (0o100640, GROUP_GID, GROUP_MEMBERS),
        (0o100600, GROUP_GID, GROUP_MEMBERS),
        (0o100644, GROUP_GID, GROUP_MEMBERS),
        (0o100604, GROUP_GID, GROUP_MEMBERS),
        (0o100640, GROUP_GID + 1, GROUP_MEMBERS),
        (0o100640, GROUP_GID, frozenset({GATE_UID, OWNER_UID, 1002})),
    ],
)
def test_p8_checker_and_gate_shared_helper_make_the_same_decision(
    tmp_path: Path,
    file_mode: int,
    file_gid: int,
    member_uids: frozenset[int],
) -> None:
    policy = DedicatedGroupPolicy(
        group_name=GROUP_NAME,
        group_gid=GROUP_GID,
        gate_principal=f"uid:{GATE_UID}",
        expected_owner_principal=f"uid:{OWNER_UID}",
    )
    gate_decision = dedicated_group_access_verified(
        file_mode=file_mode,
        file_gid=file_gid,
        policy=policy,
        actual_member_uids=member_uids,
    )
    tool_decision = check_oob_wiring(
        tmp_path / "owner-response.json",
        observer=lambda _path: OobFileObservation(
            writer_uid=OWNER_UID,
            group_gid=file_gid,
            file_mode=file_mode,
        ),
        expected_owner_uid=OWNER_UID,
        gate_uid=GATE_UID,
        expected_group_name=GROUP_NAME,
        expected_group_gid=GROUP_GID,
        group_member_resolver=lambda _name, _gid: member_uids,
        principal_name=lambda uid: f"uid {uid}",
    ).ok

    assert tool_decision is gate_decision


def test_p7_owner_side_is_nonzero_without_green_result_or_observation() -> None:
    output = io.StringIO()

    def forbidden_observer(_path: Path) -> OobFileObservation:
        raise AssertionError("owner-side self-check must stop before reading")

    status = main(
        (),
        output=output,
        current_uid=lambda: OWNER_UID,
        owner_uid_lookup=lambda _name: OWNER_UID,
        observer=forbidden_observer,
        expected_group_name=GROUP_NAME,
        expected_group_gid=GROUP_GID,
    )

    rendered = output.getvalue()
    assert status != 0
    assert "你正在 hermes-owner 視窗" in rendered
    assert "證明不了 gate 讀不讀得到" in rendered
    assert "✓" not in rendered


def test_gate_side_prints_pasteable_owner_command_and_checks_read_only() -> None:
    output = io.StringIO()
    calls = 0

    def observer(_path: Path) -> OobFileObservation:
        nonlocal calls
        calls += 1
        return OobFileObservation(
            writer_uid=OWNER_UID,
            group_gid=GROUP_GID,
            file_mode=0o100640,
        )

    status = main(
        (),
        output=output,
        current_uid=lambda: GATE_UID,
        owner_uid_lookup=lambda _name: OWNER_UID,
        observer=observer,
        expected_group_name=GROUP_NAME,
        expected_group_gid=GROUP_GID,
        group_member_resolver=lambda _name, _gid: GROUP_MEMBERS,
    )

    rendered = output.getvalue()
    assert status == 0
    assert calls == 1
    assert "touch -- /var/hermes-phase9/owner-response.json" in rendered
    assert "chgrp -- test-phase9-oob" in rendered
    assert "chmod 0640 -- /var/hermes-phase9/owner-response.json" in rendered
    assert "步驟 2（gate）" in rendered
    assert "Traceback" not in rendered
