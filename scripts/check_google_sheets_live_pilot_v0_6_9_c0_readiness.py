#!/usr/bin/env python3
"""v0.6.9-C0 — Google Sheets live pilot runner + preflight 靜態 readiness（不連 Google、不印 secret）。

確認 C0 runner / 文件具備所有 guard 且未越界。
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "HERMES_OPENCLAW_GOOGLE_SHEETS_LIVE_PILOT_V0_6_9_C0.md"
RUNNER = ROOT / "scripts" / "run_google_sheets_oauth_single_row_pilot_v0_6_9_c.py"
WRITER = ROOT / "app" / "google_sheets_oauth_writer.py"
RESULT_SINK = ROOT / "app" / "result_sink.py"
APP_MAIN = ROOT / "app" / "main.py"

BS = chr(92)
BAD_USER_PATH = "C:" + BS + "Users" + BS + "Lnovo"
BAD_SECRETS_PATH = "Desktop" + BS + "secrets"
SUSPECT_TOKEN_PREFIXES = ("1" + "//", "ya29.", "goc" + "spx-")

FAILURES: list[str] = []


def _check(cond: bool, label: str) -> None:
    print(f"  {'ok ' if cond else '❌ '}: {label}")
    if not cond:
        FAILURES.append(label)


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.is_file() else ""


def main() -> int:
    doc = _read(DOC)
    runner = _read(RUNNER)
    rs = _read(RESULT_SINK)
    main_txt = _read(APP_MAIN)
    runner_low = runner.lower()

    print("[1] 檔案存在")
    _check(DOC.is_file(), "v0.6.9-C0 文件存在")
    _check(RUNNER.is_file(), "scripts/run_google_sheets_oauth_single_row_pilot_v0_6_9_c.py 存在")
    _check(WRITER.is_file(), "app/google_sheets_oauth_writer.py 存在")

    print("[2] 文件明確：C0 不真寫、C1 才第一次真寫")
    _check("不真寫" in doc, "文件明確：C0 不真寫 Google Sheets")
    _check("C1" in doc and ("第一次真寫" in doc or "第一次 真寫" in doc),
           "文件明確：C1 才能第一次真寫")

    print("[3] runner 有雙重 live guard 旗標")
    _check("--i-understand-this-writes-one-row" in runner,
           "runner 有 --i-understand-this-writes-one-row 旗標")

    print("[4] runner masked spreadsheet id、不印 token / client secret / 完整 env")
    _check("_mask" in runner or "masked" in runner_low, "runner 有 masked spreadsheet id")
    # 不得直接整串印出 config.spreadsheet_id（未遮罩）。
    _check("print(config.spreadsheet_id" not in runner_low
           and "config.spreadsheet_id)" not in runner.replace("_mask(config.spreadsheet_id)", ""),
           "runner 不直接印出完整 spreadsheet id")
    for bad in ("refresh_token", "client_secret"):
        # 只允許出現在 import / 註解 / 不印出；確保沒有 print(... refresh_token/client_secret ...)
        _check(f"print({bad}" not in runner_low and f"print(config.{bad}" not in runner_low,
               f"runner 不 print {bad}")
    _check("os.environ)" not in runner and "print(os.environ" not in runner_low,
           "runner 不印出完整 env")

    print("[5] runner 使用 writer guard，且未接 Queue / Worker / result_sink")
    _check("google_sheets_oauth_writer" in runner and "append_single_pilot_row" in runner,
           "runner 使用 app.google_sheets_oauth_writer 的 guard")
    # 只擋「真的 import 核心模組」，不擋散文 / worksheet 名（pilot_result_sink 含 result_sink）。
    for forbidden in ("from app.queue", "import app.queue", "from app.worker",
                      "import app.worker", "app.result_sink", "from app.main", "import app.main"):
        _check(forbidden not in runner, f"runner 未 import {forbidden}")

    print("[6] app/main / result_sink 未 import runner / writer")
    _check("google_sheets_oauth_writer" not in main_txt and "run_google_sheets_oauth_single_row" not in main_txt,
           "app/main.py 未 import runner / writer")
    _check("google_sheets_oauth_writer" not in rs and "run_google_sheets_oauth_single_row" not in rs,
           "result_sink.py 未 import runner / writer")

    print("[7] result_sink 仍不 import google client（mock-safe）")
    rs_low = rs.lower()
    rs_bad = ("import google", "from google", "googleapiclient", "gspread",
              "google.oauth", "google_auth", "google.auth", "import oauthlib")
    _check(RESULT_SINK.is_file() and not any(b in rs_low for b in rs_bad),
           "result_sink.py 不 import 任何 google client library")

    print("[8] 文件預設狀態仍是 GOOGLE_SHEETS_ENABLED=false（true 只在 C1 toggle 說明）")
    _check("GOOGLE_SHEETS_ENABLED=false" in doc, "文件含 GOOGLE_SHEETS_ENABLED=false 預設")

    print("[9] doc / runner 不含真 token / 真路徑 / 疑似 token 前綴")
    for name, blob in (("doc", doc), ("runner", runner)):
        _check(BAD_USER_PATH not in blob, f"{name} 不含使用者目錄真路徑")
        _check(BAD_SECRETS_PATH not in blob, f"{name} 不含 Desktop secrets 真路徑")
    suspect = any(pre in doc or pre in runner for pre in SUSPECT_TOKEN_PREFIXES)
    _check(not suspect, "doc / runner 不含疑似真 token 前綴")

    if FAILURES:
        print(f"\n❌ v0.6.9-C0 live pilot readiness 檢查失敗 {len(FAILURES)} 項：")
        for f in FAILURES:
            print(f"   - {f}")
        return 1
    print("\n✅ v0.6.9-C0 live pilot readiness 全數通過（沒有真寫、沒有連 Google、沒有顯示 secret）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
