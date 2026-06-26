#!/usr/bin/env python3
"""v0.6.9-C1 — Google Sheets live pilot closeout 靜態檢查（不連 Google、不真寫、不印 secret）。

確認 closeout 文件如實收尾，且不含完整 spreadsheet id / token / client secret / Owner 真路徑。
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "HERMES_OPENCLAW_GOOGLE_SHEETS_LIVE_PILOT_V0_6_9_C1_CLOSEOUT.md"
RESULT_SINK = ROOT / "app" / "result_sink.py"
APP_MAIN = ROOT / "app" / "main.py"

BS = chr(92)
BAD_USER_PATH = "C:" + BS + "Users" + BS + "Lnovo"
BAD_SECRETS_PATH = "Desktop" + BS + "secrets"
SUSPECT_TOKEN_PREFIXES = ("1" + "//", "ya29.", "goc" + "spx-")
# spreadsheet id 的 masked 前 6 碼（允許出現；用來偵測是否被未遮罩地接續）。
MASKED_ID_PREFIX = "1vzR1T"

FAILURES: list[str] = []


def _check(cond: bool, label: str) -> None:
    print(f"  {'ok ' if cond else '❌ '}: {label}")
    if not cond:
        FAILURES.append(label)


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.is_file() else ""


def _has_unmasked_id(text: str) -> bool:
    """若 masked 前綴後面不是 '...'（即被未遮罩地接續），視為含完整 id。"""
    idx = 0
    while True:
        i = text.find(MASKED_ID_PREFIX, idx)
        if i == -1:
            return False
        after = text[i + len(MASKED_ID_PREFIX): i + len(MASKED_ID_PREFIX) + 3]
        if after != "...":
            return True
        idx = i + len(MASKED_ID_PREFIX)


def main() -> int:
    doc = _read(DOC)
    rs = _read(RESULT_SINK)
    main_txt = _read(APP_MAIN)

    print("[1] C1 closeout 文件存在")
    _check(DOC.is_file(), "docs/HERMES_OPENCLAW_GOOGLE_SHEETS_LIVE_PILOT_V0_6_9_C1_CLOSEOUT.md 存在")

    print("[2] 文件明確：C1 由 Owner 手動完成")
    _check("Owner" in doc and "手動" in doc, "文件明確：C1 由 Owner 手動完成")

    print("[3] 文件明確：writer result status = appended")
    _check("appended" in doc, "文件含 writer result status = appended")

    print("[4] 文件明確：GOOGLE_SHEETS_ENABLED=false")
    _check("GOOGLE_SHEETS_ENABLED=false" in doc, "文件含 GOOGLE_SHEETS_ENABLED=false")

    print("[5] 文件明確：不再真寫")
    _check("不再真寫" in doc, "文件明確：不再真寫 Google Sheets")

    print("[6] 文件明確：未接 Queue / Worker / result_sink")
    _check("Queue" in doc and "Worker" in doc and "result_sink" in doc and "未接" in doc,
           "文件明確：未接 Queue / Worker / result_sink")

    print("[7] 文件不含完整 spreadsheet id（masked 前綴後必為 ...）")
    _check(not _has_unmasked_id(doc), "文件無未遮罩的完整 spreadsheet id")

    print("[8] 文件不含 refresh token / client secret 真值樣式 / Owner 真路徑")
    for pre in SUSPECT_TOKEN_PREFIXES:
        _check(pre not in doc, f"文件不含疑似 token 前綴（{pre}）")
    _check(BAD_USER_PATH not in doc, "文件不含使用者目錄真路徑")
    _check(BAD_SECRETS_PATH not in doc, "文件不含 Desktop secrets 真路徑")

    print("[9] 文件目前狀態不得是 GOOGLE_SHEETS_ENABLED=true")
    _check("GOOGLE_SHEETS_ENABLED=true" not in doc,
           "文件未把 GOOGLE_SHEETS_ENABLED=true 當作目前狀態")

    print("[10] app/main / result_sink 未 import google writer")
    _check("google_sheets_oauth_writer" not in main_txt, "app/main.py 未 import google writer")
    _check("google_sheets_oauth_writer" not in rs, "result_sink.py 未 import google writer")

    print("[11] result_sink 仍不 import google client（mock-safe）")
    rs_low = rs.lower()
    rs_bad = ("import google", "from google", "googleapiclient", "gspread",
              "google.oauth", "google_auth", "google.auth", "import oauthlib")
    _check(RESULT_SINK.is_file() and not any(b in rs_low for b in rs_bad),
           "result_sink.py 不 import 任何 google client library")

    if FAILURES:
        print(f"\n❌ v0.6.9-C1 closeout 檢查失敗 {len(FAILURES)} 項：")
        for f in FAILURES:
            print(f"   - {f}")
        return 1
    print("\n✅ v0.6.9-C1 closeout 檢查全數通過（沒有再真寫、沒有顯示 / 含任何 secret 或完整 id）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
