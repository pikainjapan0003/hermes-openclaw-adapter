"""Phase 9 N=1 entry-point tests: rehearsal works, real mode never does."""

from __future__ import annotations

import ast
import base64
import io
import json
import os
import subprocess
from contextlib import AbstractContextManager, contextmanager
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterator

import pytest

from scripts.check_phase9_oob_wiring import OobFileObservation, main as wiring_main
from app.phase9_gate import FreshChallenge
from app.phase9_presence import compute_owner_presence
from app.phase9_presence_channel import (
    DedicatedGroupPolicy,
    JsonPresenceChannel,
    PresenceChannelError,
    PresenceEndpoint,
    RegularFilePresenceReader,
)
from scripts.run_phase9_n1 import (
    _MountFilesystem,
    _runtime_gate_principal,
    _validated_oob_directory,
    main,
    run_dry_rehearsal,
)


pytestmark = pytest.mark.contract
REPO_ROOT = Path(__file__).parents[1]
PRESENCE_NOW = datetime(2026, 8, 7, 10, 0, tzinfo=timezone.utc)


class CountingRealExecutorFactory:
    def __init__(self) -> None:
        self.calls = 0

    def __call__(self) -> object:
        self.calls += 1
        raise AssertionError("real executor must remain unreachable")


@contextmanager
def _workspace(path: Path) -> Iterator[str]:
    yield str(path)


def _owner_principal_distinct_from_gate() -> str:
    return f"uid:{os.getuid() + 1}"


def _presence_challenge() -> FreshChallenge:
    return FreshChallenge(
        challenge_id="c2-real-reader-challenge",
        rehearsal_id="phase9-n1-entrypoint-rehearsal",
        approval_packet_hash="a" * 64,
        action_hash="b" * 64,
        issued_at=PRESENCE_NOW - timedelta(seconds=1),
        deadline=PRESENCE_NOW + timedelta(seconds=30),
    )


def _presence_payload(challenge: FreshChallenge) -> bytes:
    return json.dumps(
        {
            "action_hash": challenge.action_hash,
            "approval_packet_hash": challenge.approval_packet_hash,
            "challenge_id": challenge.challenge_id,
            "continuity_id": "rehearsal-continuity",
            "owner_confirmed": True,
            "owner_verbatim_authorization_verified": True,
            "rehearsal_id": challenge.rehearsal_id,
        },
        sort_keys=True,
    ).encode("utf-8")


def _real_presence_channel(
    path: Path,
    *,
    expected_owner_principal: str,
) -> JsonPresenceChannel:
    endpoint = PresenceEndpoint(
        path=path,
        medium="file",
        gate_principal=_runtime_gate_principal(),
        expected_owner_principal=expected_owner_principal,
        contract_digest="c" * 64,
        continuity_id="rehearsal-continuity",
        max_validity_seconds=60,
    )
    return JsonPresenceChannel(
        endpoint=endpoint,
        reader=RegularFilePresenceReader(
            clock=lambda: PRESENCE_NOW,
            group_policy=DedicatedGroupPolicy(
                group_name="test-phase9-oob",
                group_gid=path.lstat().st_gid,
                gate_principal=endpoint.gate_principal,
                expected_owner_principal=endpoint.expected_owner_principal,
            ),
            group_member_resolver=lambda _name, _gid: frozenset(
                {
                    int(endpoint.gate_principal.removeprefix("uid:")),
                    int(endpoint.expected_owner_principal.removeprefix("uid:")),
                }
            ),
        ),
        clock=lambda: PRESENCE_NOW,
    )


def test_explicit_synthetic_rehearsal_runs_all_thirteen_owner_readable_steps(
    tmp_path: Path,
) -> None:
    output = io.StringIO()
    factory = CountingRealExecutorFactory()
    report = run_dry_rehearsal(
        output=output,
        real_executor_factory=factory,
        expected_owner_principal=_owner_principal_distinct_from_gate(),
        synthetic_presence=True,
        workspace_factory=lambda: _workspace(tmp_path),
    )
    text = output.getvalue()

    assert report.fake_executor_calls == 1
    assert report.real_executor_calls == 0
    assert report.burn_records == 1
    assert report.audit_records == 1
    assert factory.calls == 0
    assert len(report.trace) == 16
    assert report.trace[0] == "1:DENY_ALL_TO_CHECKING"
    assert report.trace[-1] == "15:POST_ATTEMPT_EVIDENCE_COMPUTED"
    assert all(f"[{index}/13]" in text for index in range(1, 14))
    assert "不會呼叫真實 OpenClaw" in text
    assert "真實 executor 呼叫：0" in text
    assert "⚠ 本次為合成回應，未經真實 OOB 管道" in text
    assert "Traceback" not in text
    raw_fixed_value = base64.urlsafe_b64encode(b"d" * 32).rstrip(b"=").decode()
    assert raw_fixed_value not in text
    assert raw_fixed_value not in "".join(
        path.read_text(encoding="utf-8")
        for path in tmp_path.rglob("*")
        if path.is_file()
    )


def test_t1_gate_owned_real_file_is_same_endpoint_and_not_authenticated(
    tmp_path: Path,
) -> None:
    """T1 is a real lstat/read of a gate-owned WSL-native temporary file."""

    challenge = _presence_challenge()
    path = tmp_path / "owner-response.json"
    path.write_bytes(_presence_payload(challenge))
    path.chmod(0o640)
    gate_principal = _runtime_gate_principal()

    inputs = _real_presence_channel(
        path,
        expected_owner_principal=gate_principal,
    ).collect_after_second_challenge(challenge)
    result = compute_owner_presence(
        inputs,
        now=PRESENCE_NOW,
        final_challenge_issued_at=challenge.issued_at,
    )

    assert f"uid:{path.lstat().st_uid}" == gate_principal
    assert inputs.same_endpoint is True
    assert inputs.owner_response_authenticated is not None
    assert inputs.owner_response_authenticated.verified is False
    assert result.owner_response_authenticated is False
    assert result.owner_synchronously_present is False


def test_t2_different_owner_principal_can_authenticate_only_under_simulation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """T2 is simulation only; C4 exists, but Owner cross-uid proof is pending."""

    challenge = _presence_challenge()
    path = tmp_path / "owner-response.json"
    path.write_bytes(_presence_payload(challenge))
    path.chmod(0o640)
    simulated_owner = _owner_principal_distinct_from_gate()
    original_read = RegularFilePresenceReader.read

    def simulated_different_owner_read(
        self: RegularFilePresenceReader,
        endpoint: PresenceEndpoint,
        *,
        deadline: datetime,
    ) -> object:
        observation = original_read(self, endpoint, deadline=deadline)
        return replace(observation, owner_principal=simulated_owner)

    monkeypatch.setattr(
        RegularFilePresenceReader,
        "read",
        simulated_different_owner_read,
    )
    inputs = _real_presence_channel(
        path,
        expected_owner_principal=simulated_owner,
    ).collect_after_second_challenge(challenge)
    result = compute_owner_presence(
        inputs,
        now=PRESENCE_NOW,
        final_challenge_issued_at=challenge.issued_at,
    )

    assert inputs.same_endpoint is False
    assert inputs.owner_response_authenticated is not None
    assert inputs.owner_response_authenticated.verified is True
    assert result.owner_response_authenticated is True
    assert result.owner_synchronously_present is True


@pytest.mark.parametrize(
    "failure_kind",
    ("missing", "timeout", "principal", "json"),
)
def test_t3_real_oob_failures_close_without_synthetic_fallback(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    failure_kind: str,
) -> None:
    oob_directory = tmp_path / "oob"
    oob_directory.mkdir()
    response_path = oob_directory / "owner-response.json"
    expected_owner = _runtime_gate_principal()

    if failure_kind == "timeout":
        def timed_out_read(
            _self: RegularFilePresenceReader,
            _endpoint: PresenceEndpoint,
            *,
            deadline: datetime,
        ) -> object:
            del deadline
            raise PresenceChannelError("owner presence response is unavailable")

        monkeypatch.setattr(RegularFilePresenceReader, "read", timed_out_read)
    elif failure_kind == "principal":
        response_path.write_text("{}", encoding="utf-8")
        response_path.chmod(0o640)
        expected_owner = _owner_principal_distinct_from_gate()
    elif failure_kind == "json":
        response_path.write_text("{not-json", encoding="utf-8")
        response_path.chmod(0o640)

    output = io.StringIO()
    factory = CountingRealExecutorFactory()
    status = main(
        (),
        output=output,
        real_executor_factory=factory,
        expected_owner_principal=expected_owner,
        oob_directory=oob_directory,
        oob_group_name="test-phase9-oob",
        oob_group_gid=oob_directory.lstat().st_gid,
        group_member_resolver=lambda _name, _gid: frozenset(
            {os.getuid(), int(expected_owner.removeprefix("uid:"))}
        ),
    )

    text = output.getvalue()
    assert status == 1
    assert factory.calls == 0
    assert "Owner OOB 回應不可用" in text
    assert "未退回合成回應" in text
    assert "合成回應，未經真實 OOB 管道" not in text
    assert "Traceback" not in text


def test_t4_synthetic_presence_requires_explicit_flag(tmp_path: Path) -> None:
    output = io.StringIO()
    owner = _owner_principal_distinct_from_gate()

    denied = main((), output=output, expected_owner_principal=owner)

    assert denied == 2
    assert "未設定真實 OOB 目錄" in output.getvalue()
    output = io.StringIO()
    allowed = main(
        ("--synthetic-presence",),
        output=output,
        expected_owner_principal=owner,
        workspace_factory=lambda: _workspace(tmp_path / "synthetic-workspace"),
    )
    assert allowed == 0
    assert "⚠ 本次為合成回應，未經真實 OOB 管道" in output.getvalue()


def test_t4_synthetic_presence_and_real_oob_directory_are_mutually_exclusive(
    tmp_path: Path,
) -> None:
    output = io.StringIO()

    def forbidden_workspace() -> AbstractContextManager[str]:
        raise AssertionError("mutually exclusive configuration must reject early")

    status = main(
        ("--synthetic-presence",),
        output=output,
        expected_owner_principal=_owner_principal_distinct_from_gate(),
        oob_directory=tmp_path,
        workspace_factory=forbidden_workspace,
    )

    assert status == 2
    assert "不可同時設定" in output.getvalue()
    assert "[1/13]" not in output.getvalue()


def test_non_native_oob_directory_is_rejected_before_rehearsal() -> None:
    output = io.StringIO()

    def forbidden_workspace() -> AbstractContextManager[str]:
        raise AssertionError("/mnt/c OOB configuration must reject early")

    status = main(
        (),
        output=output,
        expected_owner_principal=_owner_principal_distinct_from_gate(),
        oob_directory=Path("/mnt/c/unsafe-phase9-oob"),
        oob_group_name="test-phase9-oob",
        oob_group_gid=os.getgid(),
        group_member_resolver=lambda _name, _gid: frozenset(
            {os.getuid(), os.getuid() + 1}
        ),
        workspace_factory=forbidden_workspace,
    )

    assert status == 2
    assert "不是可驗證的 WSL 原生 ext4 路徑" in output.getvalue()
    assert "/var/hermes-phase9" in output.getvalue()


@pytest.mark.parametrize(
    "directory",
    (
        Path("//mnt/c/phase9-oob"),
        Path("/mnt/C/phase9-oob"),
        Path("/mnt/d/phase9-oob"),
        Path("/mnt/wsl/phase9-oob"),
    ),
)
def test_mount_guard_rejects_wsl_shared_and_drive_namespaces(
    directory: Path,
) -> None:
    with pytest.raises(ValueError, match="WSL native ext4"):
        _validated_oob_directory(directory)


def test_mount_guard_resolves_alias_before_namespace_decision(tmp_path: Path) -> None:
    alias = tmp_path / "windows-drive-alias"
    alias.symlink_to("/mnt/c", target_is_directory=True)

    with pytest.raises(ValueError, match="WSL native ext4"):
        _validated_oob_directory(alias / "phase9-oob")


def test_mount_guard_rejects_unresolvable_symlink_loop(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    first.symlink_to(second)
    second.symlink_to(first)

    with pytest.raises(ValueError, match="cannot verify OOB directory"):
        _validated_oob_directory(first)


def test_mount_guard_accepts_actual_wsl_native_ext4_directory(tmp_path: Path) -> None:
    assert _validated_oob_directory(tmp_path) == tmp_path.resolve()


def test_mount_guard_uses_backing_filesystem_type_not_string_only(
    tmp_path: Path,
) -> None:
    drvfs = _MountFilesystem(
        mount_point=tmp_path,
        filesystem_type="9p",
        mount_source="drvfs",
        super_options=frozenset({"aname=drvfs;path=C:\\"}),
    )

    with pytest.raises(ValueError, match="WSL native ext4"):
        _validated_oob_directory(tmp_path, filesystem_resolver=lambda _path: drvfs)


@pytest.mark.parametrize(
    ("argv", "expected_status"),
    (
        ((), 2),
        (("--dry-run",), 2),
        (("--synthetic-presence",), 0),
        (("--dry-run", "--synthetic-presence"), 0),
        (("--real",), 2),
        (("--unknown",), 2),
        (("--real", "--dry-run"), 2),
        (("n1_harmless_query",), 2),
    ),
)
def test_every_argument_shape_keeps_real_process_and_executor_calls_at_zero(
    argv: tuple[str, ...],
    expected_status: int,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    process_calls = 0

    def forbidden_process(*_args: object, **_kwargs: object) -> object:
        nonlocal process_calls
        process_calls += 1
        raise AssertionError("no process may start")

    monkeypatch.setattr(subprocess, "run", forbidden_process)
    output = io.StringIO()
    factory = CountingRealExecutorFactory()

    status = main(
        argv,
        output=output,
        real_executor_factory=factory,
        expected_owner_principal=_owner_principal_distinct_from_gate(),
    )

    assert status == expected_status
    assert factory.calls == 0
    assert process_calls == 0
    assert "Traceback" not in output.getvalue()


def test_missing_owner_principal_rejects_before_thirteen_steps() -> None:
    output = io.StringIO()
    factory = CountingRealExecutorFactory()

    def forbidden_workspace() -> AbstractContextManager[str]:
        raise AssertionError("thirteen-step rehearsal must not start")

    status = main(
        (),
        output=output,
        real_executor_factory=factory,
        workspace_factory=forbidden_workspace,
    )

    text = output.getvalue()
    assert status == 2
    assert factory.calls == 0
    assert "未設定 Owner principal" in text
    assert "[1/13]" not in text
    assert "Traceback" not in text


def test_gate_principal_uses_runtime_uid_format(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(os, "getuid", lambda: 4242)

    assert _runtime_gate_principal() == "uid:4242"


def test_entrypoint_is_not_wired_to_routes_main_or_worker() -> None:
    forbidden_consumers = (
        REPO_ROOT / "app" / "main.py",
        REPO_ROOT / "app" / "worker.py",
    )
    for path in forbidden_consumers:
        source = path.read_text(encoding="utf-8")
        assert "run_phase9_n1" not in source

    entrypoint = REPO_ROOT / "scripts" / "run_phase9_n1.py"
    tree = ast.parse(entrypoint.read_text(encoding="utf-8"))
    forbidden_calls = {
        "Popen",
        "Thread",
        "os.system",
        "run_forever",
        "start",
    }
    observed = {
        (
            f"{node.func.value.id}.{node.func.attr}"
            if isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            else node.func.attr
            if isinstance(node.func, ast.Attribute)
            else node.func.id
            if isinstance(node.func, ast.Name)
            else ""
        )
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
    }
    assert observed.isdisjoint(forbidden_calls)


def test_t6b_entrypoint_delegates_token_issuance_to_phase9_issuer() -> None:
    entrypoint = REPO_ROOT / "scripts" / "run_phase9_n1.py"
    tree = ast.parse(entrypoint.read_text(encoding="utf-8"))
    imported_from_issuer = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        and node.module == "app.phase9_token_issuer"
        for alias in node.names
    }
    direct_issue_imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        and node.module == "app.phase9_token"
        for alias in node.names
    }
    direct_issue_calls = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }

    assert {
        "OwnerPresenceProof",
        "Phase9TokenIssuer",
        "TokenIssuanceRequest",
    }.issubset(imported_from_issuer)
    assert "issue_token" not in direct_issue_imports
    assert "issue_token" not in direct_issue_calls


def test_t8_owner_preflight_accepts_distinct_expected_writer_under_simulation() -> None:
    """這是 gate 端模擬，非真實跨 uid 驗證。"""

    output = io.StringIO()

    status = wiring_main(
        (),
        output=output,
        current_uid=lambda: 1000,
        owner_uid_lookup=lambda _name: 1001,
        observer=lambda _path: OobFileObservation(
            writer_uid=1001,
            group_gid=77,
            file_mode=0o100640,
        ),
        expected_group_name="test-phase9-oob",
        expected_group_gid=77,
        group_member_resolver=lambda _name, _gid: frozenset({1000, 1001}),
    )

    assert status == 0
    assert "✓ gate 讀到了，而且確認是 hermes-owner 寫的" in output.getvalue()


def test_t8_owner_side_preflight_stops_before_self_observation() -> None:
    """Owner creates the file; the decisive read must happen at the gate."""

    output = io.StringIO()

    def forbidden_observer(_path: Path) -> OobFileObservation:
        raise AssertionError("owner-side self-observation must not run")

    status = wiring_main(
        (),
        output=output,
        current_uid=lambda: 1001,
        owner_uid_lookup=lambda _name: 1001,
        observer=forbidden_observer,
        expected_group_name="test-phase9-oob",
        expected_group_gid=77,
    )

    rendered = output.getvalue()
    assert status == 1
    assert "你正在 hermes-owner 視窗" in rendered
    assert "證明不了 gate 讀不讀得到" in rendered
    assert "✓" not in rendered


def test_t8_owner_preflight_rejects_same_gate_principal_under_simulation() -> None:
    """這是模擬，非真實跨 uid 驗證。"""

    output = io.StringIO()

    status = wiring_main(
        (),
        output=output,
        current_uid=lambda: 1000,
        owner_uid_lookup=lambda _name: 1001,
        observer=lambda _path: OobFileObservation(
            writer_uid=1000,
            group_gid=77,
            file_mode=0o100640,
        ),
        expected_group_name="test-phase9-oob",
        expected_group_gid=77,
        group_member_resolver=lambda _name, _gid: frozenset({1000, 1001}),
    )

    assert status == 1
    assert "寫入者是 lnovo → 同端點" in output.getvalue()


def test_t8_owner_preflight_reports_missing_file_under_simulation() -> None:
    """這是模擬，非真實跨 uid 驗證。"""

    output = io.StringIO()

    def missing(_path: Path) -> OobFileObservation:
        raise FileNotFoundError

    status = wiring_main(
        (),
        output=output,
        current_uid=lambda: 1000,
        owner_uid_lookup=lambda _name: 1001,
        observer=missing,
        expected_group_name="test-phase9-oob",
        expected_group_gid=77,
        group_member_resolver=lambda _name, _gid: frozenset({1000, 1001}),
    )

    assert status == 1
    assert "✗ 找不到" in output.getvalue()
    assert "Traceback" not in output.getvalue()


def test_t8_owner_preflight_reports_unreadable_file_under_simulation() -> None:
    """這是模擬，非真實跨 uid 驗證。"""

    output = io.StringIO()

    def unreadable(_path: Path) -> OobFileObservation:
        raise PermissionError

    status = wiring_main(
        (),
        output=output,
        current_uid=lambda: 1000,
        owner_uid_lookup=lambda _name: 1001,
        observer=unreadable,
        expected_group_name="test-phase9-oob",
        expected_group_gid=77,
        group_member_resolver=lambda _name, _gid: frozenset({1000, 1001}),
    )

    assert status == 1
    assert "✗ 無法安全讀取" in output.getvalue()
    assert "Traceback" not in output.getvalue()


def test_t8_owner_preflight_rejects_windows_mount_before_observation() -> None:
    """這是模擬，非真實跨 uid 驗證。"""

    output = io.StringIO()
    observer_calls = 0

    def forbidden_observer(_path: Path) -> OobFileObservation:
        nonlocal observer_calls
        observer_calls += 1
        raise AssertionError("/mnt/c must reject before observation")

    status = wiring_main(
        ("/mnt/c/phase9/owner-response.json",),
        output=output,
        current_uid=lambda: 1000,
        owner_uid_lookup=lambda _name: 1001,
        observer=forbidden_observer,
        expected_group_name="test-phase9-oob",
        expected_group_gid=77,
        group_member_resolver=lambda _name, _gid: frozenset({1000, 1001}),
    )

    assert status == 1
    assert observer_calls == 0
    assert "不在可驗證的 WSL 原生 ext4 路徑" in output.getvalue()
