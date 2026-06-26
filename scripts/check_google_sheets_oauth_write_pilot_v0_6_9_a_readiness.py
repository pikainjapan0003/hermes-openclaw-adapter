#!/usr/bin/env python3
"""v0.6.9-A — Google Sheets OAuth Write Pilot Plan 靜態 + env gate 檢查。

只做文件靜態檢查與環境變數 gate，**不連 Google、不真寫 Sheets、不讀/不印任何 secret 值**：
- v0.6.9-A 文件存在，且明確聲明：不真寫、ENABLED=false、WRITE_MODE=pilot、
  single spreadsheet/worksheet/row、v0.6.9-B 才實作 writer、v0.6.9-C 才第一次真寫。
- 文件不含真 refresh token、不含 Owner 真路徑（使用者目錄 / Desktop secrets）。
- env gate：GOOGLE_OAUTH_REFRESH_TOKEN 只印 SET / MISSING（不印值）；
  GOOGLE_SHEETS_ENABLED 必須為 false（本版不允許真寫）；GOOGLE_SHEETS_WRITE_MODE 必須為 pilot。

回傳 0/1，永不輸出任何 secret value。
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "HERMES_OPENCLAW_GOOGLE_SHEETS_OAUTH_WRITE_PILOT_V0_6_9_A.md"

# 以 chr(92)（反斜線）組裝禁用路徑樣式，避免本腳本原始碼出現真路徑字面。
BS = chr(92)
BAD_USER_PATH = "C:" + BS + "Users" + BS + "Lnovo"
BAD_SECRETS_PATH = "Desktop" + BS + "secrets"
# 疑似真 token 前綴（純前綴，非真值）。
SUSPECT_TOKEN_PREFIXES = ("1" + "//", "ya29.", "goc" + "spx-")

FAILURES: list[str] = []


def _check(cond: bool, label: str) -> None:
    print(f"  {'ok ' if cond else '❌ '}: {label}")
    if not cond:
        FAILURES.append(label)


def main() -> int:
    text = DOC.read_text(encoding="utf-8") if DOC.is_file() else ""

    print("[1] v0.6.9-A 文件存在")
    _check(DOC.is_file(), "docs/HERMES_OPENCLAW_GOOGLE_SHEETS_OAUTH_WRITE_PILOT_V0_6_9_A.md 存在")

    print("[2] 文件明確：本版不真寫 Google Sheets")
    _check("不真寫" in text or "不是真寫" in text, "文件明確：本版不真寫 Google Sheets")

    print("[3] 文件明確：GOOGLE_SHEETS_ENABLED=false / WRITE_MODE=pilot")
    _check("GOOGLE_SHEETS_ENABLED=false" in text, "文件含 GOOGLE_SHEETS_ENABLED=false")
    _check("GOOGLE_SHEETS_WRITE_MODE=pilot" in text, "文件含 GOOGLE_SHEETS_WRITE_MODE=pilot")

    print("[4] 文件明確：single spreadsheet / worksheet / row")
    _check("single" in text.lower() and ("single row" in text.lower() or "單列" in text),
           "文件明確：single spreadsheet / worksheet / single row")

    print("[5] 文件明確：v0.6.9-B 才實作 writer、v0.6.9-C 才第一次真寫")
    _check("v0.6.9-B" in text, "文件含 v0.6.9-B writer 條件")
    _check("v0.6.9-C" in text, "文件含 v0.6.9-C 第一次真寫條件")

    print("[6] 文件不含真 refresh token / Owner 真路徑")
    _check(BAD_USER_PATH not in text, "文件不含使用者目錄真路徑")
    _check(BAD_SECRETS_PATH not in text, "文件不含 Desktop secrets 真路徑")
    for pre in SUSPECT_TOKEN_PREFIXES:
        _check(pre not in text, f"文件不含疑似 token 前綴（{pre}）")

    print("[7] env gate：GOOGLE_OAUTH_REFRESH_TOKEN 只印 SET / MISSING（不印值）")
    rt = os.environ.get("GOOGLE_OAUTH_REFRESH_TOKEN", "")
    rt_set = bool(rt.strip())
    print(f"  GOOGLE_OAUTH_REFRESH_TOKEN: {'SET' if rt_set else 'MISSING'}")
    # 本版不強制 token 必須 SET（plan 階段），只確保印出時不洩值。

    print("[8] env gate：本版必須 GOOGLE_SHEETS_ENABLED=false（不允許真寫）")
    enabled_norm = os.environ.get("GOOGLE_SHEETS_ENABLED", "").strip().lower()
    print(f"  GOOGLE_SHEETS_ENABLED: {enabled_norm or '(unset)'}")
    # unset 視為尚未開啟（safe）；只在被設成 true 時 fail。
    _check(enabled_norm != "true", "GOOGLE_SHEETS_ENABLED 不得為 true（v0.6.9-A 不允許真寫）")

    print("[9] env gate：GOOGLE_SHEETS_WRITE_MODE 必須為 pilot（若有設）")
    mode_norm = os.environ.get("GOOGLE_SHEETS_WRITE_MODE", "").strip().lower()
    print(f"  GOOGLE_SHEETS_WRITE_MODE: {mode_norm or '(unset)'}")
    _check(mode_norm in ("", "pilot"), "GOOGLE_SHEETS_WRITE_MODE 為 pilot 或未設（不得為其他值）")

    print("[10] result_sink 仍不 import google client（mock-safe，本版未實作真 writer）")
    rs = ROOT / "app" / "result_sink.py"
    rs_text = rs.read_text(encoding="utf-8").lower() if rs.is_file() else ""
    rs_bad = ("import google", "from google", "googleapiclient", "gspread",
              "google.oauth", "google_auth", "google.auth", "import oauthlib")
    _check(rs.is_file() and not any(b in rs_text for b in rs_bad),
           "app/result_sink.py 仍不 import 任何 google client library")

    if FAILURES:
        print(f"\n❌ v0.6.9-A pilot plan readiness 檢查失敗 {len(FAILURES)} 項：")
        for f in FAILURES:
            print(f"   - {f}")
        return 1
    print("\n✅ v0.6.9-A pilot plan readiness 全數通過（沒有真寫 Sheets、沒有顯示任何 secret）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
