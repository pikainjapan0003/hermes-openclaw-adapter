#!/usr/bin/env python3
"""v0.6.8G-A — Token Extraction / Replit Secrets Placement Runbook 靜態檢查。

不連 Google、不讀 .env、不跑 OAuth、不顯示 / 不寫 token。只做文件靜態 gate：
- runbook 文件存在。
- 文件明確說 v0.6.8G-A 不跑 OAuth、不顯示 token、不寫 token file。
- 文件明確說 v0.6.8G-B 才翻 kill-switch、v0.6.8G-C 才 Owner 本機跑 consent。
- 文件明確說 v0.6.9 不得開始。
- 文件不含 Owner 本機真路徑（使用者目錄 / Desktop secrets）。
- 文件不含疑似真 token 前綴。
- helper 仍保留 LIVE_CONSENT_ENABLED = False。

本腳本不輸出任何 secret value，回傳 0/1。
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "HERMES_OPENCLAW_OAUTH_V0_6_8G_A_TOKEN_EXTRACTION_RUNBOOK.md"
HELPER = ROOT / "scripts" / "oauth_local_consent_helper.py"

# 以 chr(92)（反斜線）組裝禁用路徑樣式，避免本腳本原始碼直接出現真路徑字面。
BS = chr(92)
BAD_USER_PATH = "C:" + BS + "Users" + BS + "Lnovo"
BAD_SECRETS_PATH = "Desktop" + BS + "secrets"
# 疑似真 token / secret 前綴（純前綴，非真值）。
SUSPECT_TOKEN_PREFIXES = ("1" + "//", "ya29.", "goc" + "spx-")

FAILURES: list[str] = []


def _check(cond: bool, label: str) -> None:
    print(f"  {'ok ' if cond else '❌ '}: {label}")
    if not cond:
        FAILURES.append(label)


def main() -> int:
    text = DOC.read_text(encoding="utf-8") if DOC.is_file() else ""

    print("[1] runbook 文件存在")
    _check(DOC.is_file(), "docs/HERMES_OPENCLAW_OAUTH_V0_6_8G_A_TOKEN_EXTRACTION_RUNBOOK.md 存在")

    print("[2] 明確說 v0.6.8G-A 不跑 OAuth")
    _check("v0.6.8G-A" in text and ("不執行 OAuth" in text or "不跑真 OAuth" in text),
           "文件明確：v0.6.8G-A 不執行 / 不跑 OAuth")

    print("[3] 明確說不顯示 token / 不寫 token file")
    _check("不顯示 token" in text, "文件明確：不顯示 token")
    _check("不寫 token file" in text, "文件明確：不寫 token file")

    print("[4] 明確說 v0.6.8G-B 才翻 kill-switch")
    _check("v0.6.8G-B" in text and "LIVE_CONSENT_ENABLED" in text,
           "文件明確：v0.6.8G-B 才翻 LIVE_CONSENT_ENABLED kill-switch")

    print("[5] 明確說 v0.6.8G-C 才 Owner 本機跑 consent")
    _check("v0.6.8G-C" in text and "consent" in text,
           "文件明確：v0.6.8G-C 才 Owner 本機跑 consent")

    print("[6] 明確說 v0.6.9 不得開始")
    _check("v0.6.9" in text and "不得開始" in text, "文件明確：v0.6.9 不得開始")

    print("[7] 文件不含 Owner 本機真路徑")
    _check(BAD_USER_PATH not in text, "文件不含使用者目錄真路徑")
    _check(BAD_SECRETS_PATH not in text, "文件不含 Desktop secrets 真路徑")

    print("[8] 文件不含疑似真 token 前綴")
    for pre in SUSPECT_TOKEN_PREFIXES:
        _check(pre not in text, f"文件不含疑似 token 前綴（{pre}）")

    print("[9] helper 仍保留 LIVE_CONSENT_ENABLED = False")
    helper_text = HELPER.read_text(encoding="utf-8") if HELPER.is_file() else ""
    _check("LIVE_CONSENT_ENABLED = False" in helper_text,
           "scripts/oauth_local_consent_helper.py 仍保留 LIVE_CONSENT_ENABLED = False")

    if FAILURES:
        print(f"\n❌ v0.6.8G-A runbook readiness 檢查失敗 {len(FAILURES)} 項：")
        for f in FAILURES:
            print(f"   - {f}")
        return 1
    print("\n✅ v0.6.8G-A runbook readiness 全數通過（沒有跑 OAuth、沒有顯示任何 token）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
