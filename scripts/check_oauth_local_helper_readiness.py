#!/usr/bin/env python3
"""v0.6.8B — OAuth Local Helper draft 靜態檢查（不連 Google、不讀 .env、不印任何 secret）。

確認 v0.6.8B 草案的安全前提成立：
- helper 草案存在，且預設 dry-run、`--live` 會拒絕。
- helper 不 import google client、不呼叫 webbrowser.open（不開瀏覽器）。
- helper 原始碼無硬編 client secret / refresh token。
- 無 token 檔被 git tracked。
- .env.example 高敏感 key 仍為空值。
- app/result_sink.py 仍未 import google（mock-safe）。
- requirements 是否新增 google library（只回報）。
- v0.6.8B 文件存在。

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
    helper = ROOT / "scripts" / "oauth_local_helper_draft.py"
    helper_text = helper.read_text(encoding="utf-8") if helper.is_file() else ""
    helper_lower = helper_text.lower()

    print("[1] OAuth local helper 草案存在且預設 dry-run")
    _check(helper.is_file(), "scripts/oauth_local_helper_draft.py 存在")
    _check("default_dry_run = true" in helper_lower, "helper 預設 dry-run（DEFAULT_DRY_RUN = True）")
    _check("_refuse_live" in helper_text and "--live" in helper_text,
           "helper 提供 --live 但會明確拒絕")

    print("[2] helper 不 import google client、不開 browser、不連網路")
    bad_imports = ("import google", "from google", "googleapiclient", "gspread",
                   "google.oauth", "google_auth", "google.auth", "import oauthlib",
                   "import requests", "import httpx", "urllib.request")
    _check(not any(b in helper_lower for b in bad_imports),
           "helper 不 import google / network client library")
    _check("webbrowser" not in helper_lower, "helper 不使用 webbrowser（不開瀏覽器）")

    print("[3] helper 原始碼無硬編 client secret / refresh token 真值")
    # 只允許出現 key 名（占位）；不允許出現賦值真值樣式。
    bad_literals = ("client_secret=\"", "client_secret='", "refresh_token=\"",
                    "refresh_token='", "1//", "gocspx-")
    _check(not any(b in helper_lower for b in bad_literals),
           "helper 無硬編 client secret / refresh token 真值樣式")

    print("[4] token / credential 檔未被 git tracked")
    for pat in ("*token*.json", "*credentials*.json", "*client_secret*.json",
                "*service*account*.json", ".env"):
        _check(not _tracked(pat), f"{pat} 未 tracked")

    print("[5] .env.example 高敏感 key 仍為空值")
    envex = ROOT / ".env.example"
    env_text = envex.read_text(encoding="utf-8") if envex.is_file() else ""
    for key in ("GOOGLE_OAUTH_CLIENT_SECRET", "GOOGLE_OAUTH_REFRESH_TOKEN",
                "GOOGLE_SERVICE_ACCOUNT_JSON"):
        empty = any(ln.strip() == f"{key}=" for ln in env_text.splitlines())
        _check(empty, f"{key} 在 .env.example 為空值（無真值）")

    print("[6] app/result_sink.py 仍未 import google client（mock-safe）")
    rs = ROOT / "app" / "result_sink.py"
    rs_text = rs.read_text(encoding="utf-8").lower() if rs.is_file() else ""
    _check(rs.is_file(), "app/result_sink.py 存在")
    rs_bad = ("import google", "from google", "googleapiclient", "gspread",
              "google.oauth", "google_auth", "google.auth", "import oauthlib")
    _check(not any(b in rs_text for b in rs_bad),
           "result_sink.py 不 import 任何 google client library")

    print("[7] v0.6.8B 文件存在")
    _check(
        (ROOT / "docs" / "HERMES_OPENCLAW_OAUTH_LOCAL_HELPER_DRAFT_V0_6_8B.md").is_file(),
        "docs/HERMES_OPENCLAW_OAUTH_LOCAL_HELPER_DRAFT_V0_6_8B.md 存在",
    )

    print("[8] requirements google library 現況（只回報，不安裝）")
    req = ROOT / "requirements.txt"
    has_google = False
    if req.is_file():
        rtext = req.read_text(encoding="utf-8").lower()
        has_google = any(k in rtext for k in
                         ("google-api", "google-auth", "gspread", "googleapiclient",
                          "google-cloud", "oauthlib"))
    print(f"  info: requirements 目前{'已' if has_google else '尚未'}含 google library"
          f"（v0.6.8B 不安裝、不連 Google）")

    if FAILURES:
        print(f"\n❌ OAuth local helper readiness 檢查失敗 {len(FAILURES)} 項：")
        for f in FAILURES:
            print(f"   - {f}")
        return 1
    print("\n✅ OAuth local helper readiness 全數通過（沒有連 Google、沒有輸出任何 secret）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
