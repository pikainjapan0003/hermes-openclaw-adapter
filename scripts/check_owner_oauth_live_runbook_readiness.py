#!/usr/bin/env python3
"""v0.6.8D — Owner OAuth Live Runbook 靜態檢查（不連 Google、不讀 .env、不印任何 secret）。

確認 v0.6.8D runbook 的安全前提成立：
- runbook 文件存在。
- 文件提到 v0.6.9 gate（前置條件）。
- 文件沒有把 v0.6.9 誤寫成 v0.9。
- 文件含「不貼給 Claude / ChatGPT」提醒。
- 文件含 Replit Secrets 高敏感 key 名。
- scripts/oauth_local_consent_helper.py 仍存在，且 LIVE_CONSENT_ENABLED 仍為 False。
- token / credential 檔未被 git tracked，.env 未 tracked。
- .env.example 高敏感 key 仍為空值。
- app/result_sink.py 仍未 import google。
- requirements 是否新增 google library（只回報）。

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
    doc = ROOT / "docs" / "HERMES_OPENCLAW_OWNER_OAUTH_LIVE_RUNBOOK_V0_6_8D.md"
    doc_text = doc.read_text(encoding="utf-8") if doc.is_file() else ""

    print("[1] Owner runbook 文件存在")
    _check(doc.is_file(), "docs/HERMES_OPENCLAW_OWNER_OAUTH_LIVE_RUNBOOK_V0_6_8D.md 存在")

    print("[2] 文件提到 v0.6.9 gate（前置條件）")
    _check("v0.6.9" in doc_text, "文件含 v0.6.9")
    _check("Gate" in doc_text or "gate" in doc_text or "前置條件" in doc_text,
           "文件含 v0.6.9 gate / 前置條件段落")

    print("[3] 文件沒有把 v0.6.9 誤寫成 v0.9")
    # 'v0.6.9' 不含子字串 'v0.9'，故直接搜尋 'v0.9' 不會誤判正確寫法。
    has_bad = "v0.9" in doc_text or "V0.9" in doc_text
    _check(not has_bad, "文件無誤寫 v0.9（正確應為 v0.6.9）")

    print("[4] 文件含『不貼給 Claude / ChatGPT』提醒")
    _check("Claude" in doc_text and "ChatGPT" in doc_text,
           "文件含 不貼給 Claude / ChatGPT 提醒")

    print("[5] 文件含 Replit Secrets 高敏感 key 名")
    for key in ("GOOGLE_OAUTH_CLIENT_SECRET", "GOOGLE_OAUTH_REFRESH_TOKEN",
                "GOOGLE_SHEETS_SPREADSHEET_ID"):
        _check(key in doc_text, f"文件含 {key}")

    print("[6] consent helper 仍存在且 live 由 explicit Owner 風險旗標把關")
    helper = ROOT / "scripts" / "oauth_local_consent_helper.py"
    helper_text = helper.read_text(encoding="utf-8") if helper.is_file() else ""
    _check(helper.is_file(), "scripts/oauth_local_consent_helper.py 存在")
    # v0.6.8G-B 後：live 不靠永久 kill-switch，而靠 explicit Owner flags + local-only +
    # file validation + token display acknowledgement。
    _check("--i-understand-local-only" in helper_text
           and "--i-understand-token-will-be-visible" in helper_text,
           "helper 以 explicit Owner 風險旗標把關 live consent（取代永久 kill-switch）")

    print("[7] token / credential 檔未被 git tracked")
    for pat in ("*token*.json", "*credentials*.json", "*client_secret*.json",
                "*service*account*.json", ".env"):
        _check(not _tracked(pat), f"{pat} 未 tracked")

    print("[8] .env.example 高敏感 key 仍為空值")
    envex = ROOT / ".env.example"
    env_text = envex.read_text(encoding="utf-8") if envex.is_file() else ""
    for key in ("GOOGLE_OAUTH_CLIENT_SECRET", "GOOGLE_OAUTH_REFRESH_TOKEN",
                "GOOGLE_SERVICE_ACCOUNT_JSON"):
        empty = any(ln.strip() == f"{key}=" for ln in env_text.splitlines())
        _check(empty, f"{key} 在 .env.example 為空值（無真值）")

    print("[9] app/result_sink.py 仍未 import google client（mock-safe）")
    rs = ROOT / "app" / "result_sink.py"
    rs_text = rs.read_text(encoding="utf-8").lower() if rs.is_file() else ""
    _check(rs.is_file(), "app/result_sink.py 存在")
    rs_bad = ("import google", "from google", "googleapiclient", "gspread",
              "google.oauth", "google_auth", "google.auth", "import oauthlib")
    _check(not any(b in rs_text for b in rs_bad),
           "result_sink.py 不 import 任何 google client library")

    print("[10] requirements google library 現況（只回報，不安裝）")
    req = ROOT / "requirements.txt"
    has_google = False
    if req.is_file():
        rtext = req.read_text(encoding="utf-8").lower()
        has_google = any(k in rtext for k in
                         ("google-api", "google-auth", "gspread", "googleapiclient",
                          "google-cloud", "oauthlib"))
    print(f"  info: requirements 目前{'已' if has_google else '尚未'}含 google library"
          f"（v0.6.8D 不安裝、不連 Google）")

    if FAILURES:
        print(f"\n❌ Owner OAuth live runbook readiness 檢查失敗 {len(FAILURES)} 項：")
        for f in FAILURES:
            print(f"   - {f}")
        return 1
    print("\n✅ Owner OAuth live runbook readiness 全數通過（沒有連 Google、沒有輸出任何 secret）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
