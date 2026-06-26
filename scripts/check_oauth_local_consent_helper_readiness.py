#!/usr/bin/env python3
"""v0.6.8C — OAuth Local Consent Helper 靜態檢查（不連 Google、不讀 .env、不印任何 secret）。

確認 v0.6.8C consent helper 的安全前提成立：
- helper 存在，且預設 dry-run。
- `--live` 無 `--i-understand-local-only` 會拒絕（exit 2）。
- helper 含 Replit / CI 偵測，且本版 LIVE_CONSENT_ENABLED 為 False。
- helper 無硬編 client secret / refresh token。
- helper 不在 dry-run / 模組層 import google（只在 live 真執行路徑延遲 import）。
- helper 不寫 token 檔。
- 無 token / credential 檔被 git tracked。
- .env.example 高敏感 key 仍為空值。
- app/result_sink.py 仍未 import google。
- requirements 是否新增 google library（只回報）。
- v0.6.8C 文件存在。

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
    helper = ROOT / "scripts" / "oauth_local_consent_helper.py"
    text = helper.read_text(encoding="utf-8") if helper.is_file() else ""
    lower = text.lower()

    print("[1] consent helper 存在且預設 dry-run")
    _check(helper.is_file(), "scripts/oauth_local_consent_helper.py 存在")
    _check("default_dry_run = true" in lower, "helper 預設 dry-run（DEFAULT_DRY_RUN = True）")

    print("[2] --live guard：需安全旗標，否則拒絕")
    _check("--i-understand-local-only" in text, "helper 含 --i-understand-local-only 安全旗標")
    _check("_refuse_live_no_flag" in text, "helper 無旗標時拒絕 --live")

    print("[3] live 安全閘：偵測 Replit/CI + explicit Owner 風險旗標把關")
    # v0.6.8G-B 後：不靠永久 kill-switch，而靠 explicit Owner flags 把關。
    _check("--i-understand-token-will-be-visible" in text,
           "helper 以 explicit Owner 風險旗標把關 live（取代永久 kill-switch）")
    _check("REPL_ID" in text and "_detect_non_local_env" in text,
           "helper 含 Replit / CI 偵測並會拒絕")

    print("[4] helper 無硬編 client secret / refresh token 真值")
    bad_literals = ("client_secret=\"", "client_secret='", "refresh_token=\"",
                    "refresh_token='", "1//", "gocspx-")
    _check(not any(b in lower for b in bad_literals),
           "helper 無硬編 client secret / refresh token 真值樣式")

    print("[5] helper 不在模組層 import google（只允許 live 路徑延遲 import）")
    # 只抓「真的 import 語句」：行首無縮排（模組層）且該行以 import/from google 開頭。
    # 避免把 docstring / 註解裡的散文（例如「dry-run 不 import google」）誤判。
    def _is_module_level_google_import(ln: str) -> bool:
        if not ln or ln[0].isspace():  # 有縮排 = 函式內延遲 import，允許
            return False
        s = ln.strip().lower()
        return s.startswith("import google") or s.startswith("from google")
    module_level_google = any(_is_module_level_google_import(ln) for ln in text.splitlines())
    _check(not module_level_google, "helper 模組層未 import google（dry-run 不 import google）")

    print("[6] helper 不寫 token 檔")
    # 不得出現把 token 寫檔的樣式。
    bad_writes = ("token.json", "token.pickle", "credentials.json",
                  "open(\"token", "open('token", ".write_text(")
    _check(not any(b in lower for b in bad_writes), "helper 無寫 token / credential 檔樣式")

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

    print("[10] v0.6.8C 文件存在")
    _check(
        (ROOT / "docs" / "HERMES_OPENCLAW_OAUTH_LOCAL_CONSENT_HELPER_V0_6_8C.md").is_file(),
        "docs/HERMES_OPENCLAW_OAUTH_LOCAL_CONSENT_HELPER_V0_6_8C.md 存在",
    )

    print("[11] requirements google library 現況（只回報，不安裝）")
    req = ROOT / "requirements.txt"
    has_google = False
    if req.is_file():
        rtext = req.read_text(encoding="utf-8").lower()
        has_google = any(k in rtext for k in
                         ("google-api", "google-auth", "gspread", "googleapiclient",
                          "google-cloud", "oauthlib"))
    print(f"  info: requirements 目前{'已' if has_google else '尚未'}含 google library"
          f"（v0.6.8C 不安裝、不連 Google）")

    if FAILURES:
        print(f"\n❌ OAuth local consent helper readiness 檢查失敗 {len(FAILURES)} 項：")
        for f in FAILURES:
            print(f"   - {f}")
        return 1
    print("\n✅ OAuth local consent helper readiness 全數通過（沒有連 Google、沒有輸出任何 secret）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
