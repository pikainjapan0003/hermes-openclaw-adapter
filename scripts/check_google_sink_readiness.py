#!/usr/bin/env python3
"""v0.6.6 — Google result-sink readiness 安全檢查（純本機、不連 Google、不讀 secret 真值）。

只檢查「repo 是否具備未來安全接 Google sink 的基礎」，不做任何 Google API call、
不讀取 / 不輸出任何 credential 真值。

檢查項目：
1. app.main 可 import。
2. 敏感 / 執行期 / credential 檔案未被 git tracked
   (.env, data/, queue.db, *.jsonl, *credentials*.json, *service*account*.json,
    *client_secret*.json, *token*.json)。
3. v0.6.5B Replit manual smoke report 文件存在（前置版本可追溯）。
4. requirements.txt 存在；回報目前是否已有 google 相關套件（只回報，不安裝）。

本腳本只輸出 PASS/FAIL 與 key 名，**絕不輸出任何 secret value**。
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

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
    print("[1] app.main 可 import")
    try:
        import app.main as m  # noqa: PLC0415
        _check(hasattr(m, "app"), "import app.main OK")
    except Exception as exc:  # noqa: BLE001
        _check(False, f"import app.main 失敗：{type(exc).__name__}: {exc}")

    print("[2] 敏感 / 執行期 / credential / mock-log 檔案未被 git tracked")
    patterns = [
        ".env", "data/", "*.db", "queue.db", "tasks.jsonl", "results.jsonl",
        "*credentials*.json", "*service*account*.json", "*service_account*.json",
        "*client_secret*.json", "*token*.json",
        "mock_google_sheets_rows.jsonl", "*mock_google_sheets_rows.jsonl",
    ]
    for pat in patterns:
        _check(not _tracked(pat), f"{pat} 未 tracked")

    print("[2b] v0.6.7 Result Sink 基礎件")
    _check((ROOT / "app" / "result_sink.py").is_file(), "app/result_sink.py 存在")
    envex = ROOT / ".env.example"
    envex_text = envex.read_text(encoding="utf-8") if envex.is_file() else ""
    for key in ("RESULT_SINK_ENABLED", "RESULT_SINK_TYPE", "RESULT_SINK_MODE",
                "MOCK_GOOGLE_SHEETS_ROWS_PATH"):
        _check(key in envex_text, f".env.example 含 {key}（placeholder）")
    _check("RESULT_SINK_ENABLED=false" in envex_text, ".env.example 預設 RESULT_SINK_ENABLED=false")

    print("[3] 前置版本可追溯：v0.6.5B Replit manual smoke report 存在")
    _check(
        (ROOT / "docs" / "HERMES_OPENCLAW_REPLIT_MANUAL_SMOKE_TEST_V0_6_5B.md").is_file(),
        "v0.6.5B smoke report 文件存在",
    )

    print("[4] requirements.txt 存在；google 套件現況（只回報，不安裝）")
    req = ROOT / "requirements.txt"
    _check(req.is_file(), "requirements.txt 存在")
    has_google = False
    if req.is_file():
        text = req.read_text(encoding="utf-8").lower()
        has_google = any(k in text for k in
                         ("google-api", "google-auth", "gspread", "googleapiclient",
                          "google-cloud", "oauthlib"))
    print(f"  info: requirements 目前{'已' if has_google else '尚未'}含 google 相關套件"
          f"（v0.6.6 不安裝、不啟用）")

    # 註：是否有 credential 真值的把關，靠 [2] 確認「credential 檔案未被 tracked」即可。
    # 這裡刻意不做 repo-wide 關鍵字 grep —— 本專案的 secret-scanner 測試腳本
    # (test_backup_push_plan.py / test_docs_operator_guide.py) 本身就含 private_key /
    # client_secret 等「樣式字串」，會造成誤判。credential 真值不會出現在 tracked 檔。

    if FAILURES:
        print(f"\n❌ Google sink readiness 檢查失敗 {len(FAILURES)} 項：")
        for f in FAILURES:
            print(f"   - {f}")
        return 1
    print("\n✅ Google sink readiness 檢查全數通過（沒有連 Google、沒有輸出任何 secret）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
