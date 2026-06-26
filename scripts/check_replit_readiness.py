#!/usr/bin/env python3
"""v0.6.5 — Replit readiness 安全檢查（不讀取 / 不輸出任何 secret 真值）。

檢查項目：
1. app.main 可 import。
2. 若 DASHBOARD_AUTH_ENABLED=true，則 DASHBOARD_TOKEN 不可為空（只看「是否有設」，不印值）。
3. .env 不在 git tracked。
4. data/ / queue.db / tasks.jsonl / results.jsonl 不在 git tracked。
5. requirements.txt 存在。
6. templates/login.html 存在。

本腳本只輸出 PASS/FAIL 標籤，絕不輸出 token / secret 真值。
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
    """該 glob/路徑是否被 git 追蹤。"""
    out = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", pattern],
        capture_output=True, text=True,
    ).stdout.strip()
    return bool(out)


def _env_bool(name: str) -> bool:
    raw = os.getenv(name)
    return bool(raw) and raw.strip().lower() in ("1", "true", "yes", "on")


def main() -> int:
    print("[1] app.main 可 import")
    try:
        import app.main as m  # noqa: PLC0415
        _check(hasattr(m, "app"), "import app.main OK")
        app_version = getattr(m, "APP_VERSION", "?")
    except Exception as exc:  # noqa: BLE001
        _check(False, f"import app.main 失敗：{type(exc).__name__}: {exc}")
        app_version = "?"

    print("[2] Dashboard Auth Gate 設定一致性（只看是否有設，不印值）")
    auth_enabled = _env_bool("DASHBOARD_AUTH_ENABLED")
    token_set = bool(os.getenv("DASHBOARD_TOKEN", "").strip())
    if auth_enabled:
        _check(token_set, "DASHBOARD_AUTH_ENABLED=true 時 DASHBOARD_TOKEN 必須有值")
    else:
        print("  -- : DASHBOARD_AUTH_ENABLED 非 true（本機可，Replit 必須設 true）")
    print(f"  info: auth_enabled={auth_enabled}, token_set={token_set} (值未顯示)")

    print("[3] .env 未被 git tracked")
    _check(not _tracked(".env"), ".env 未 tracked")

    print("[4] 執行期資料未被 git tracked")
    for pat in ("data/", "*.db", "queue.db", "tasks.jsonl", "results.jsonl",
                "data/queue.db", "data/tasks.jsonl", "data/results.jsonl"):
        _check(not _tracked(pat), f"{pat} 未 tracked")

    print("[5] requirements.txt 存在")
    _check((ROOT / "requirements.txt").is_file(), "requirements.txt 存在")

    print("[6] templates/login.html 存在（Auth Gate 登入頁）")
    _check((ROOT / "templates" / "login.html").is_file(), "templates/login.html 存在")

    print(f"\nAPP_VERSION={app_version}")
    if FAILURES:
        print(f"\n❌ Replit readiness 檢查失敗 {len(FAILURES)} 項：")
        for f in FAILURES:
            print(f"   - {f}")
        return 1
    print("\n✅ Replit readiness 檢查全數通過（沒有輸出任何 secret 值）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
