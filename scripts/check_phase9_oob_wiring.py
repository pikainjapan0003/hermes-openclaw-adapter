"""唯讀檢查 Phase 9 Owner OOB 檔案的實際寫入者與可讀性。

測試無法建立由其他 uid 擁有的檔案（需要特權），
所以真正的端對端驗證只有 Owner 本人做得到。
不得以測試替身假裝已完成此驗證。
"""

from __future__ import annotations

import importlib
import os
import pwd
import stat
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Protocol, Sequence, TextIO, cast


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


DEFAULT_OOB_DIRECTORY = Path("/var/hermes-phase9")
OOB_RESPONSE_FILENAME = "owner-response.json"
EXPECTED_OWNER_NAME = "hermes-owner"
GATE_UID = 1000


@dataclass(frozen=True)
class OobFileObservation:
    """Non-payload file identity returned by the injected read boundary."""

    writer_uid: int


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
    return OobFileObservation(writer_uid=details.st_uid)


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
    gate_uid: int = GATE_UID,
    principal_name: Callable[[int], str] = _principal_name,
) -> OobWiringResult:
    """Apply the fail-closed identity decision to one read-only observation."""

    try:
        _entrypoint()._validated_oob_directory(path.parent)
    except ValueError:
        return OobWiringResult(
            False,
            "✗ OOB 檔案不可放在 /mnt/c；請使用 /var/hermes-phase9。",
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
    return OobWiringResult(True, f"✓ 讀到了，而且確認是 {EXPECTED_OWNER_NAME} 寫的")


def main(
    argv: Sequence[str] | None = None,
    *,
    output: TextIO = sys.stdout,
    current_uid: Callable[[], int] = os.getuid,
    owner_uid_lookup: Callable[[str], int] = lambda name: pwd.getpwnam(name).pw_uid,
    observer: OobFileObserver = _observe_regular_file,
) -> int:
    """Run one read-only check and present only a Chinese, payload-free result."""

    arguments = tuple(argv or ())
    output.write("請在 hermes-owner 視窗執行此檢查。\n")
    if current_uid() == GATE_UID:
        output.write("⚠ 目前是 lnovo（uid 1000）；這只是樣張，不能代替 Owner 驗證。\n")
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
    result = check_oob_wiring(
        path,
        observer=observer,
        expected_owner_uid=expected_owner_uid,
    )
    output.write(result.message + "\n")
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
