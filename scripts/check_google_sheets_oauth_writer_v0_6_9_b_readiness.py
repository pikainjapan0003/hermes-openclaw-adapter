#!/usr/bin/env python3
"""v0.6.9-B — Guarded Google Sheets OAuth writer 靜態 readiness（不連 Google、不印 secret）。

檢查 writer 模組存在且具備所有 guard，且未被接進核心、未在 import 時連 Google。
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOC = ROOT / "docs" / "HERMES_OPENCLAW_GOOGLE_SHEETS_OAUTH_WRITER_V0_6_9_B.md"
WRITER = ROOT / "app" / "google_sheets_oauth_writer.py"
MOCK_TEST = ROOT / "scripts" / "test_google_sheets_oauth_writer_v0_6_9_b.py"
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


def _module_level_google_import(text: str) -> bool:
    for ln in text.splitlines():
        if not ln or ln[0].isspace():
            continue
        s = ln.strip().lower()
        if s.startswith("import google") or s.startswith("from google") \
                or s.startswith("import googleapiclient") or s.startswith("from googleapiclient"):
            return True
    return False


def main() -> int:
    doc = _read(DOC)
    writer = _read(WRITER)
    rs = _read(RESULT_SINK)
    main_txt = _read(APP_MAIN)

    print("[1] 檔案存在")
    _check(DOC.is_file(), "v0.6.9-B 文件存在")
    _check(WRITER.is_file(), "app/google_sheets_oauth_writer.py 存在")
    _check(MOCK_TEST.is_file(), "scripts/test_google_sheets_oauth_writer_v0_6_9_b.py 存在")

    print("[2] 文件明確：本版不真寫、不接 Queue / Worker / result_sink")
    _check("不真寫" in doc, "文件明確：本版不真寫 Google Sheets")
    _check("Queue" in doc and "Worker" in doc and "result_sink" in doc
           and ("不接" in doc or "不接入" in doc or "不接 Queue" in doc),
           "文件明確：本版不接 Queue / Worker / result_sink")

    print("[3] writer guard 字串齊全")
    _check("GOOGLE_SHEETS_ENABLED" in writer, "writer 有 GOOGLE_SHEETS_ENABLED guard")
    _check("GOOGLE_SHEETS_WRITE_MODE" in writer and "pilot" in writer,
           "writer 有 GOOGLE_SHEETS_WRITE_MODE=pilot guard")
    _check("allow_live_write" in writer, "writer 有 allow_live_write guard")
    _check("PILOT_ROW_LEN" in writer or "!= 8" in writer or "len(row)" in writer,
           "writer 有 single-row / 8 欄 guard")
    _check("pilot_result_sink" in writer, "writer 有 worksheet pilot_result_sink guard")
    # APPEND_RANGE 以 f-string 組裝（WORKSHEET_NAME_REQUIRED!A:H），故分別檢查兩段。
    _check("!A:H" in writer and "APPEND_RANGE" in writer,
           "writer append range 為 pilot_result_sink!A:H（f-string 組裝）")

    print("[4] writer import 時不連 / 不 import google service")
    _check(not _module_level_google_import(writer),
           "writer 模組層未 import google（只在 live build 延遲 import）")

    print("[5] writer 未被接進核心")
    mod_name = "google_sheets_oauth_writer"
    _check(mod_name not in rs, "result_sink.py 未 import google sheets writer")
    _check(mod_name not in main_txt, "app/main.py 未 import google sheets writer")

    print("[6] result_sink 仍不 import google client（mock-safe）")
    rs_low = rs.lower()
    rs_bad = ("import google", "from google", "googleapiclient", "gspread",
              "google.oauth", "google_auth", "google.auth", "import oauthlib")
    _check(RESULT_SINK.is_file() and not any(b in rs_low for b in rs_bad),
           "result_sink.py 不 import 任何 google client library")

    print("[7] docs / writer / mock_test 不含真 token / 真路徑 / 真 spreadsheet id 樣式")
    # 只掃 doc / writer / mock_test；不掃本 readiness 自身（它含偵測樣式定義）。
    scan = (("doc", doc), ("writer", writer), ("mock_test", _read(MOCK_TEST)))
    suspect_hit = False
    for name, blob in scan:
        _check(BAD_USER_PATH not in blob, f"{name} 不含使用者目錄真路徑")
        _check(BAD_SECRETS_PATH not in blob, f"{name} 不含 Desktop secrets 真路徑")
        for pre in SUSPECT_TOKEN_PREFIXES:
            if pre in blob:
                suspect_hit = True
    _check(not suspect_hit, "未偵測到疑似真 token 前綴")

    if FAILURES:
        print(f"\n❌ v0.6.9-B writer readiness 檢查失敗 {len(FAILURES)} 項：")
        for f in FAILURES:
            print(f"   - {f}")
        return 1
    print("\n✅ v0.6.9-B writer readiness 全數通過（沒有連 Google、沒有顯示任何 secret）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
