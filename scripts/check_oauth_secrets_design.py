#!/usr/bin/env python3
"""v0.6.8 — OAuth / Secrets design 靜態檢查（不連 Google、不讀 .env、不印任何 secret 值）。

只做靜態檢查，確認「OAuth/Secrets 設計的安全前提」成立：
- 沒有 credential / token / mock-log 檔被 git tracked。
- .env.example 含必要的 OAuth / Sheets placeholder key 名。
- app/result_sink.py 仍未 import google（維持 mock-safe、不連真 Google）。
- v0.6.8 OAuth design 文件存在。
- requirements 目前是否已有 google library（只回報）。

本腳本不讀 .env 真值、不輸出任何 secret value，回傳 0/1。
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FAILURES: list[str] = []


def _check(cond: bool, label: str) -> None:
    print(f"  {'ok ' if cond else '❌ '}: {label}")
    if not cond:
        FAILURES.append(label)


def _tracked(pattern: str) -> bool:
    out = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", pattern],
        capture_output=True, text=True,
    ).stdout.strip()
    return bool(out)


def main() -> int:
    print("[1] credential / token / mock-log 檔案未被 git tracked")
    for pat in (".env", "*credentials*.json", "*service*account*.json",
                "*service_account*.json", "*client_secret*.json", "*token*.json",
                "mock_google_sheets_rows.jsonl", "*mock_google_sheets_rows.jsonl"):
        _check(not _tracked(pat), f"{pat} 未 tracked")

    print("[2] .env.example 含 OAuth / Sheets placeholder key 名")
    envex = ROOT / ".env.example"
    text = envex.read_text(encoding="utf-8") if envex.is_file() else ""
    required_keys = (
        "GOOGLE_AUTH_MODE", "GOOGLE_SHEETS_SPREADSHEET_ID", "GOOGLE_SHEETS_WORKSHEET_NAME",
        "GOOGLE_OAUTH_CLIENT_ID", "GOOGLE_OAUTH_CLIENT_SECRET", "GOOGLE_OAUTH_REFRESH_TOKEN",
        "GOOGLE_DRIVE_FOLDER_ID", "GOOGLE_SERVICE_ACCOUNT_JSON", "GOOGLE_SERVICE_ACCOUNT_FILE",
    )
    for key in required_keys:
        _check(key in text, f".env.example 含 {key}")

    print("[3] 高敏感 key 在 .env.example 為空值（不得有真值）")
    # 對每個高敏感 key，檢查該行是 KEY= 後面為空（容許行尾空白）。
    for key in ("GOOGLE_OAUTH_CLIENT_SECRET", "GOOGLE_OAUTH_REFRESH_TOKEN",
                "GOOGLE_SERVICE_ACCOUNT_JSON", "GOOGLE_OAUTH_CLIENT_ID",
                "GOOGLE_SHEETS_SPREADSHEET_ID", "GOOGLE_DRIVE_FOLDER_ID",
                "GOOGLE_SERVICE_ACCOUNT_FILE"):
        empty = any(
            ln.strip() == f"{key}=" for ln in text.splitlines()
        )
        _check(empty, f"{key} 在 .env.example 為空值（無真值）")

    print("[4] app/result_sink.py 仍未 import google client（mock-safe）")
    rs = (ROOT / "app" / "result_sink.py")
    rs_text = rs.read_text(encoding="utf-8").lower() if rs.is_file() else ""
    _check(rs.is_file(), "app/result_sink.py 存在")
    # 只擋「真的 import google client」，而非字串/識別字裡的 'google'（例如 google_sheets sink type）。
    bad_imports = ("import google", "from google", "googleapiclient", "gspread",
                   "google.oauth", "google_auth", "google.auth", "import oauthlib")
    _check(not any(b in rs_text for b in bad_imports),
           "result_sink.py 不 import 任何 google client library")

    print("[5] v0.6.8 OAuth design 文件存在")
    _check(
        (ROOT / "docs" / "HERMES_OPENCLAW_OAUTH_SECRETS_DESIGN_V0_6_8.md").is_file(),
        "docs/HERMES_OPENCLAW_OAUTH_SECRETS_DESIGN_V0_6_8.md 存在",
    )

    print("[6] requirements google library 現況（只回報，不安裝）")
    req = ROOT / "requirements.txt"
    has_google = False
    if req.is_file():
        rtext = req.read_text(encoding="utf-8").lower()
        has_google = any(k in rtext for k in
                         ("google-api", "google-auth", "gspread", "googleapiclient",
                          "google-cloud", "oauthlib"))
    print(f"  info: requirements 目前{'已' if has_google else '尚未'}含 google library"
          f"（v0.6.8 不安裝、不連 Google）")

    if FAILURES:
        print(f"\n❌ OAuth/Secrets design 檢查失敗 {len(FAILURES)} 項：")
        for f in FAILURES:
            print(f"   - {f}")
        return 1
    print("\n✅ OAuth/Secrets design 檢查全數通過（沒有連 Google、沒有輸出任何 secret）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
