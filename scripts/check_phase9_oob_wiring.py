"""從 gate 端唯讀檢查 Phase 9 Owner OOB 檔案的身分與權限。

這是兩步驟工具：Owner 先在 ``hermes-owner`` 終端建立檔案，之後 gate
principal 再執行本工具。Owner 在自己的終端讀取自己建立的檔案，不能證明
gate 是否讀得到，因此該用法會明確失敗。測試替身也不等於真實跨 uid 驗證。
"""

from __future__ import annotations

import importlib
import os
import pwd
import shlex
import stat
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Protocol, Sequence, TextIO, cast

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.phase9_presence_channel import (  # noqa: E402
    DedicatedGroupPolicy,
    GroupMemberResolver,
    dedicated_group_access_verified,
    resolve_system_group_member_uids,
)


DEFAULT_OOB_DIRECTORY = Path("/var/hermes-phase9")
OOB_RESPONSE_FILENAME = "owner-response.json"
EXPECTED_OWNER_NAME = "hermes-owner"


@dataclass(frozen=True)
class OobFileObservation:
    """Non-payload file identity returned by the injected read boundary."""

    writer_uid: int
    group_gid: int
    file_mode: int


@dataclass(frozen=True)
class OobWiringResult:
    """Chinese, payload-free result safe to show directly to the Owner."""

    ok: bool
    message: str


class OobFileObserver(Protocol):
    def __call__(self, path: Path) -> OobFileObservation:
        """Read enough to prove accessibility without returning file content."""


class _EntrypointModule(Protocol):
    def _validated_oob_directory(self, value: Path) -> Path: ...


def _entrypoint() -> _EntrypointModule:
    return cast(
        _EntrypointModule,
        importlib.import_module("scripts.run_phase9_n1"),
    )


def _observe_regular_file(path: Path) -> OobFileObservation:
    details = path.lstat()
    if not stat.S_ISREG(details.st_mode) or path.is_symlink():
        raise OSError("not a regular file")
    with path.open("rb") as handle:
        handle.read(1)
    return OobFileObservation(
        writer_uid=details.st_uid,
        group_gid=details.st_gid,
        file_mode=details.st_mode,
    )


def _principal_name(uid: int) -> str:
    try:
        return pwd.getpwuid(uid).pw_name
    except KeyError:
        return f"uid {uid}"


def check_oob_wiring(
    path: Path,
    *,
    observer: OobFileObserver = _observe_regular_file,
    expected_owner_uid: int,
    gate_uid: int,
    expected_group_name: str,
    expected_group_gid: int,
    group_member_resolver: GroupMemberResolver = resolve_system_group_member_uids,
    principal_name: Callable[[int], str] = _principal_name,
) -> OobWiringResult:
    """Apply the same fail-closed owner/group/mode policy as the real gate."""

    try:
        _entrypoint()._validated_oob_directory(path.parent)
    except ValueError:
        return OobWiringResult(
            False,
            "✗ OOB 檔案不在可驗證的 WSL 原生 ext4 路徑；請使用 /var/hermes-phase9。",
        )
    try:
        observation = observer(path)
    except FileNotFoundError:
        return OobWiringResult(False, f"✗ 找不到 {path}，請先由 Owner 建立回應檔。")
    except (OSError, ValueError):
        return OobWiringResult(False, f"✗ 無法安全讀取 {path}，請檢查檔案與權限。")

    writer_name = principal_name(observation.writer_uid)
    if observation.writer_uid == gate_uid:
        return OobWiringResult(
            False,
            f"✗ 讀到了，但寫入者是 {writer_name} → 同端點，不能當成 Owner 驗證。",
        )
    if observation.writer_uid != expected_owner_uid:
        return OobWiringResult(
            False,
            f"✗ 讀到了，但寫入者是 {writer_name}，不是 {EXPECTED_OWNER_NAME}。",
        )
    try:
        policy = DedicatedGroupPolicy(
            group_name=expected_group_name,
            group_gid=expected_group_gid,
            gate_principal=f"uid:{gate_uid}",
            expected_owner_principal=f"uid:{expected_owner_uid}",
        )
        actual_member_uids = group_member_resolver(
            expected_group_name,
            expected_group_gid,
        )
        access_verified = dedicated_group_access_verified(
            file_mode=observation.file_mode,
            file_gid=observation.group_gid,
            policy=policy,
            actual_member_uids=actual_member_uids,
        )
    except (KeyError, OSError, RuntimeError, ValueError):
        access_verified = False
    if not access_verified:
        return OobWiringResult(
            False,
            "✗ Owner 檔案的專用群組或 0640 權限不符合 gate 規約。",
        )
    return OobWiringResult(
        True,
        f"✓ gate 讀到了，而且確認是 {EXPECTED_OWNER_NAME} 寫的；專用群組與 0640 權限皆正確",
    )


def _owner_creation_command(path: Path, group_name: str) -> str:
    """Return a pasteable command; this read-only tool never executes it."""

    quoted_path = shlex.quote(str(path))
    quoted_group = shlex.quote(group_name)
    return (
        f"umask 0027 && touch -- {quoted_path} && "
        f"chgrp -- {quoted_group} {quoted_path} && chmod 0640 -- {quoted_path}"
    )


def main(
    argv: Sequence[str] | None = None,
    *,
    output: TextIO = sys.stdout,
    current_uid: Callable[[], int] = os.getuid,
    owner_uid_lookup: Callable[[str], int] = lambda name: pwd.getpwnam(name).pw_uid,
    observer: OobFileObserver = _observe_regular_file,
    expected_group_name: str | None = None,
    expected_group_gid: int | None = None,
    group_member_resolver: GroupMemberResolver = resolve_system_group_member_uids,
) -> int:
    """Print the two-step ceremony and run the decisive check only at the gate."""

    arguments = tuple(argv or ())
    if len(arguments) > 1:
        output.write("✗ 參數過多；只可提供一個 WSL 原生 OOB 檔案路徑。\n")
        return 2
    path = (
        Path(arguments[0])
        if arguments
        else DEFAULT_OOB_DIRECTORY / OOB_RESPONSE_FILENAME
    )
    try:
        expected_owner_uid = owner_uid_lookup(EXPECTED_OWNER_NAME)
    except (KeyError, OSError, ValueError):
        output.write("✗ 找不到 hermes-owner 帳號，請先確認 Owner 視窗設定。\n")
        return 1
    group_name = expected_group_name or os.environ.get("PHASE9_OOB_GROUP_NAME")
    group_gid_text = os.environ.get("PHASE9_OOB_GROUP_GID")
    if expected_group_gid is None and group_gid_text is not None:
        try:
            expected_group_gid = int(group_gid_text)
        except ValueError:
            expected_group_gid = None
    output.write("步驟 1（Owner）：在 hermes-owner 終端建立 OOB 檔案；本工具只列命令、不會執行。\n")
    if group_name:
        output.write(_owner_creation_command(path, group_name) + "\n")
    else:
        output.write("請先設定 PHASE9_OOB_GROUP_NAME 與 PHASE9_OOB_GROUP_GID。\n")
    output.write("步驟 2（gate）：切回 gate/lnovo 終端執行本工具，才是決定性檢查。\n")
    gate_uid = current_uid()
    if gate_uid == expected_owner_uid:
        output.write(
            "✗ 你正在 hermes-owner 視窗；這裡讀到的是自己寫的檔，證明不了 gate 讀不讀得到。請改在 gate 側執行。\n"
        )
        return 1
    if not group_name or type(expected_group_gid) is not int or expected_group_gid < 0:
        output.write("✗ 專用 OOB 群組設定缺失或無效；gate 檢查已停止。\n")
        return 1
    result = check_oob_wiring(
        path,
        observer=observer,
        expected_owner_uid=expected_owner_uid,
        gate_uid=gate_uid,
        expected_group_name=group_name,
        expected_group_gid=expected_group_gid,
        group_member_resolver=group_member_resolver,
    )
    output.write(result.message + "\n")
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
