#!/usr/bin/env python3
"""v0.6.9-B — Guarded Google Sheets OAuth writer mock 測試（fake transport，永不連 Google）。

只用 fake env / fake transport / fake token，驗證 writer 的 guard 行為。
**不**真寫 Google Sheets、**不**跑 OAuth、**不**使用真 Replit Secrets。
"""

from __future__ import annotations

import contextlib
import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.google_sheets_oauth_writer import (  # noqa: E402
    APPEND_RANGE,
    GoogleSheetsWriterConfig,
    GoogleSheetsWriterConfigError,
    GoogleSheetsWriterGuardError,
    append_single_pilot_row,
    build_pilot_row,
    load_google_sheets_writer_config,
)

# 純 fake 值（非真 secret）。
FAKE_REFRESH = "fake-refresh-token-for-test"
FAKE_CLIENT_ID = "fake-client-id"
FAKE_CLIENT_SECRET = "fake-client-secret"
FAKE_SPREADSHEET = "fake-spreadsheet-id"

FAILURES: list[str] = []


def _check(cond: bool, label: str) -> None:
    print(f"  {'ok ' if cond else '❌ '}: {label}")
    if not cond:
        FAILURES.append(label)


class _FakeTransport:
    def __init__(self) -> None:
        self.calls: list[tuple] = []

    def append(self, spreadsheet_id, range_a1, values) -> dict:
        self.calls.append((spreadsheet_id, range_a1, values))
        return {"updates": {"updatedRows": 1}}


def _cfg(enabled, write_mode="pilot", spreadsheet=FAKE_SPREADSHEET,
         worksheet="pilot_result_sink") -> GoogleSheetsWriterConfig:
    return GoogleSheetsWriterConfig(
        enabled=enabled, write_mode=write_mode,
        spreadsheet_id=spreadsheet, worksheet_name=worksheet,
    )


def _row():
    return build_pilot_row(timestamp="2026-06-26T00:00:00Z")


def main() -> int:
    # 1. disabled → skipped；fake transport 不被呼叫。
    print("[1/2/3] disabled → skipped，transport 不呼叫，不需 token")
    t = _FakeTransport()
    # disabled config 由 fake env 載入（刻意不給 refresh token）。
    cfg_disabled = load_google_sheets_writer_config(env={
        "GOOGLE_SHEETS_ENABLED": "false",
        "GOOGLE_SHEETS_WRITE_MODE": "pilot",
        "GOOGLE_SHEETS_SPREADSHEET_ID": FAKE_SPREADSHEET,
        "GOOGLE_SHEETS_WORKSHEET_NAME": "pilot_result_sink",
    })
    res = append_single_pilot_row(_row(), cfg_disabled, transport=t, allow_live_write=True)
    _check(res.get("status") == "skipped", "disabled → status skipped")
    _check(len(t.calls) == 0, "disabled → fake transport 未被呼叫")

    # 4. enabled 但 write_mode 不是 pilot → fail。
    print("[4] enabled + write_mode!=pilot → GuardError")
    t = _FakeTransport()
    try:
        append_single_pilot_row(_row(), _cfg(True, write_mode="live"),
                                transport=t, allow_live_write=True)
        _check(False, "應丟出 GuardError")
    except GoogleSheetsWriterGuardError:
        _check(len(t.calls) == 0, "write_mode!=pilot → GuardError 且未 append")

    # 5. enabled 但缺 spreadsheet id → fail。
    print("[5] enabled + 缺 spreadsheet_id → ConfigError")
    try:
        append_single_pilot_row(_row(), _cfg(True, spreadsheet=""),
                                transport=_FakeTransport(), allow_live_write=True)
        _check(False, "應丟出 ConfigError")
    except GoogleSheetsWriterConfigError:
        _check(True, "缺 spreadsheet_id → ConfigError")

    # 6. worksheet 不是 pilot_result_sink → fail。
    print("[6] worksheet!=pilot_result_sink → GuardError")
    try:
        append_single_pilot_row(_row(), _cfg(True, worksheet="Sheet1"),
                                transport=_FakeTransport(), allow_live_write=True)
        _check(False, "應丟出 GuardError")
    except GoogleSheetsWriterGuardError:
        _check(True, "worksheet!=pilot_result_sink → GuardError")

    # 7. row 不是 8 欄 → fail。
    print("[7] row 非 8 欄 → GuardError")
    try:
        append_single_pilot_row(["only", "three", "cols"], _cfg(True),
                                transport=_FakeTransport(), allow_live_write=True)
        _check(False, "應丟出 GuardError")
    except GoogleSheetsWriterGuardError:
        _check(True, "row 非 8 欄 → GuardError")

    # 8. 多列 append 不允許（巢狀 → 視為多列）。
    print("[8] 多列 / 巢狀 → GuardError")
    try:
        append_single_pilot_row([_row(), _row()], _cfg(True),
                                transport=_FakeTransport(), allow_live_write=True)
        _check(False, "應丟出 GuardError")
    except GoogleSheetsWriterGuardError:
        _check(True, "多列 → GuardError")

    # 9. allow_live_write=False 即使 enabled=true 也 fail-safe。
    print("[9] allow_live_write=False → fail-safe GuardError")
    t = _FakeTransport()
    try:
        append_single_pilot_row(_row(), _cfg(True), transport=t, allow_live_write=False)
        _check(False, "應丟出 GuardError")
    except GoogleSheetsWriterGuardError:
        _check(len(t.calls) == 0, "allow_live_write=False → 未 append（fail-safe）")

    # 10 & 11. allow_live_write=True + fake transport → 只 append 一列，range 正確。
    print("[10/11] allow_live_write=True + fake transport → append 一列，range=pilot_result_sink!A:H")
    t = _FakeTransport()
    res = append_single_pilot_row(_row(), _cfg(True), transport=t, allow_live_write=True)
    _check(res.get("status") == "appended" and res.get("appended_rows") == 1,
           "回報 appended 一列")
    _check(len(t.calls) == 1, "fake transport 只被呼叫一次")
    if t.calls:
        sid, rng, values = t.calls[0]
        _check(sid == FAKE_SPREADSHEET, "spreadsheet_id 正確")
        _check(rng == APPEND_RANGE == "pilot_result_sink!A:H", "append range = pilot_result_sink!A:H")
        _check(len(values) == 1 and len(values[0]) == 8, "values 為單列 8 欄")

    # 12. 不印出 token 值。
    print("[12] 不印出 token 值")
    t = _FakeTransport()
    env = {
        "GOOGLE_OAUTH_REFRESH_TOKEN": FAKE_REFRESH,
        "GOOGLE_OAUTH_CLIENT_ID": FAKE_CLIENT_ID,
        "GOOGLE_OAUTH_CLIENT_SECRET": FAKE_CLIENT_SECRET,
    }
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        append_single_pilot_row(_row(), _cfg(True), transport=t, allow_live_write=True, env=env)
    out = buf.getvalue()
    _check(FAKE_REFRESH not in out and FAKE_CLIENT_SECRET not in out,
           "writer 不印出 refresh token / client secret 值")

    if FAILURES:
        print(f"\n❌ v0.6.9-B writer 測試失敗 {len(FAILURES)} 項：")
        for f in FAILURES:
            print(f"   - {f}")
        return 1
    print("\n✅ v0.6.9-B writer 測試全數通過（fake transport only，沒有連 Google、沒有顯示 token）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
