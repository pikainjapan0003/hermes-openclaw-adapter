#!/usr/bin/env python3
"""v0.5.9 — Backup / Push Plan 文件測試（純文件檢查，不啟動 app、不碰 git remote）。

驗證 docs/BACKUP_PUSH_PLAN.md 存在、README 有入口連結、內容涵蓋必要重點，
且沒有夾帶真實 secret。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "BACKUP_PUSH_PLAN.md"
README = ROOT / "README.md"

FAILURES: list[str] = []


def _check(cond: bool, label: str) -> None:
    if cond:
        print(f"  ok: {label}")
    else:
        print(f"  ❌ FAIL: {label}")
        FAILURES.append(label)


def main_test() -> int:
    print("[1] docs/BACKUP_PUSH_PLAN.md 存在")
    _check(PLAN.is_file(), "BACKUP_PUSH_PLAN.md 存在")
    plan = PLAN.read_text(encoding="utf-8") if PLAN.is_file() else ""

    print("[2] README 有連到 docs/BACKUP_PUSH_PLAN.md")
    readme = README.read_text(encoding="utf-8") if README.is_file() else ""
    _check("docs/BACKUP_PUSH_PLAN.md" in readme, "README 連到 BACKUP_PUSH_PLAN.md")

    print("[3] 包含「本版不 push」或等價文字")
    _check(("不 push" in plan) or ("不要 push" in plan) or ("本版不 push" in plan),
           "含『本版不 push』等價說明")

    print("[4] 包含 dry-run")
    _check("dry-run" in plan.lower(), "含 dry-run")

    print("[5] 包含 secrets scan")
    _check("secrets scan" in plan.lower(), "含 secrets scan")

    print("[6] 包含 .env 不可 commit")
    _check(".env" in plan, "含 .env（不可 commit）")

    print("[7] 包含 data/ 不可 commit")
    _check("data/" in plan, "含 data/（不可 commit）")

    print("[8] 包含 queue.db 不可 commit")
    _check("queue.db" in plan, "含 queue.db（不可 commit）")

    print("[9] 包含 owner 明確批准後才 push")
    _check(("owner" in plan and "批准" in plan), "含『owner 明確批准後才 push』")

    print("[10] 沒有夾帶真實 secret")
    secret_patterns = [
        (r"sk-[A-Za-z0-9]{16,}", "OpenAI 風格金鑰"),
        (r"ghp_[A-Za-z0-9]{20,}", "GitHub token"),
        (r"AIza[A-Za-z0-9_\-]{20,}", "Google API key"),
        (r"xox[baprs]-[A-Za-z0-9-]{10,}", "Slack token"),
        (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "私鑰"),
        # remote URL 不可內嵌憑證（https://user:token@github...）
        (r"https://[^/\s]*:[^/@\s]+@", "URL 內嵌憑證"),
    ]
    leaked = [desc for pat, desc in secret_patterns if re.search(pat, plan)]
    _check(not leaked, f"沒有 secret 樣式（命中：{leaked or '無'}）")

    if FAILURES:
        print(f"\n❌ Backup Push Plan 文件測試失敗 {len(FAILURES)} 項：")
        for f in FAILURES:
            print(f"   - {f}")
        return 1
    print("\n✅ Backup Push Plan 文件測試全數通過。")
    return 0


if __name__ == "__main__":
    sys.exit(main_test())
