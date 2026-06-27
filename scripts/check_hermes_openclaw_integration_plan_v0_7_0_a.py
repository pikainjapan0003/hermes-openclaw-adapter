#!/usr/bin/env python3
"""v0.7.0-A — Hermes ↔ OpenClaw Integration Plan 靜態 readiness（純文件檢查，不連任何系統）。

確認整合計畫文件涵蓋必要契約，且方向校正回主線、未越界（不呼叫真系統、不自動寫 Sheets）。
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "HERMES_OPENCLAW_INTEGRATION_PLAN_V0_7_0_A.md"
RESULT_SINK = ROOT / "app" / "result_sink.py"
APP_MAIN = ROOT / "app" / "main.py"

BS = chr(92)
BAD_USER_PATH = "C:" + BS + "Users" + BS + "Lnovo"
BAD_SECRETS_PATH = "Desktop" + BS + "secrets"
SUSPECT_TOKEN_PREFIXES = ("1" + "//", "ya29.", "goc" + "spx-")
MASKED_ID_PREFIX = "1vzR1T"

FAILURES: list[str] = []


def _check(cond: bool, label: str) -> None:
    print(f"  {'ok ' if cond else '❌ '}: {label}")
    if not cond:
        FAILURES.append(label)


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.is_file() else ""


def _has_unmasked_id(text: str) -> bool:
    idx = 0
    while True:
        i = text.find(MASKED_ID_PREFIX, idx)
        if i == -1:
            return False
        if text[i + len(MASKED_ID_PREFIX): i + len(MASKED_ID_PREFIX) + 3] != "...":
            return True
        idx = i + len(MASKED_ID_PREFIX)


def main() -> int:
    doc = _read(DOC)
    rs = _read(RESULT_SINK)
    main_txt = _read(APP_MAIN)

    print("[1] v0.7.0-A 文件存在")
    _check(DOC.is_file(), "docs/HERMES_OPENCLAW_INTEGRATION_PLAN_V0_7_0_A.md 存在")

    print("[2] 文件涵蓋主線角色")
    for role in ("Hermes", "Adapter", "Queue", "OpenClaw Worker", "Callback",
                 "Result Sink", "Dashboard"):
        _check(role in doc, f"文件含角色 {role}")

    print("[3] 文件明確核心原則")
    _check("Hermes 是主腦" in doc, "文件明確：Hermes 是主腦")
    _check("OpenClaw 是執行網關" in doc, "文件明確：OpenClaw 是執行網關")
    _check("Queue 是任務唯一事實來源" in doc, "文件明確：Queue 是任務唯一事實來源")
    _check("Result Sink 不可破壞 Queue 狀態" in doc or "Result Sink 不是 Queue 狀態來源" in doc,
           "文件明確：Result Sink 不可破壞 Queue 狀態")

    print("[4] 文件含 schema / 契約草案")
    _check("TaskEnvelope" in doc, "文件含 TaskEnvelope schema 草案")
    _check("CallbackEvent" in doc, "文件含 CallbackEvent schema 草案")
    _check("Approval" in doc and "Level 3" in doc, "文件含 Approval model")
    _check("idempotency" in doc and "DLQ" in doc and "Retry" in doc,
           "文件含 Retry / DLQ / idempotency")

    print("[5] 文件明確本版邊界")
    _check("不呼叫真 OpenClaw" in doc, "文件明確：本版不呼叫真 OpenClaw")
    _check("不呼叫真 Hermes" in doc, "文件明確：本版不呼叫真 Hermes")
    _check("不自動寫 Google Sheets" in doc, "文件明確：本版不自動寫 Google Sheets")
    _check("GOOGLE_SHEETS_ENABLED=false" in doc, "文件明確：GOOGLE_SHEETS_ENABLED=false")
    _check("GOOGLE_SHEETS_ENABLED=true" not in doc,
           "文件未把 GOOGLE_SHEETS_ENABLED=true 當作目前狀態")

    print("[6] app/main 未 import 新整合流程；result_sink 未變真寫")
    _check("integration_plan" not in main_txt and "google_sheets_oauth_writer" not in main_txt,
           "app/main.py 未 import 新整合流程 / google writer")
    _check("google_sheets_oauth_writer" not in rs, "result_sink.py 未 import google writer")

    print("[7] result_sink 仍不 import google client（mock-safe）")
    rs_low = rs.lower()
    rs_bad = ("import google", "from google", "googleapiclient", "gspread",
              "google.oauth", "google_auth", "google.auth", "import oauthlib")
    _check(RESULT_SINK.is_file() and not any(b in rs_low for b in rs_bad),
           "result_sink.py 不 import 任何 google client library")

    print("[8] 文件不含真 token / client secret / 完整 spreadsheet id / Owner 真路徑")
    for pre in SUSPECT_TOKEN_PREFIXES:
        _check(pre not in doc, f"文件不含疑似 token 前綴（{pre}）")
    _check(not _has_unmasked_id(doc), "文件不含未遮罩的完整 spreadsheet id")
    _check(BAD_USER_PATH not in doc, "文件不含使用者目錄真路徑")
    _check(BAD_SECRETS_PATH not in doc, "文件不含 Desktop secrets 真路徑")

    if FAILURES:
        print(f"\n❌ v0.7.0-A integration plan readiness 檢查失敗 {len(FAILURES)} 項：")
        for f in FAILURES:
            print(f"   - {f}")
        return 1
    print("\n✅ v0.7.0-A integration plan readiness 全數通過（純文件，沒有連任何系統、沒有 secret）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
