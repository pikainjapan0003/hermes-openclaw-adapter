#!/usr/bin/env python3
"""v0.5.8 — Documentation / Operator Guide 測試（純文件檢查，不啟動 app）。

驗證 docs/OPERATOR_GUIDE.md 存在、README 有入口連結、內容涵蓋主要章節，
且沒有夾帶真實 .env secret。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "docs" / "OPERATOR_GUIDE.md"
README = ROOT / "README.md"

FAILURES: list[str] = []


def _check(cond: bool, label: str) -> None:
    if cond:
        print(f"  ok: {label}")
    else:
        print(f"  ❌ FAIL: {label}")
        FAILURES.append(label)


def main_test() -> int:
    print("[1] docs/OPERATOR_GUIDE.md 存在")
    _check(GUIDE.is_file(), "OPERATOR_GUIDE.md 存在")
    guide = GUIDE.read_text(encoding="utf-8") if GUIDE.is_file() else ""

    print("[2] README 有連到 docs/OPERATOR_GUIDE.md")
    readme = README.read_text(encoding="utf-8") if README.is_file() else ""
    _check("docs/OPERATOR_GUIDE.md" in readme, "README 連到 OPERATOR_GUIDE.md")

    print("[3-9] OPERATOR_GUIDE 內容涵蓋主要章節")
    required = {
        "[3] Dashboard": "Dashboard",
        "[4] Worker": "Worker",
        "[5] Approval Flow": "Approval Flow",
        "[6] Limited Control Actions": "Limited Control Actions",
        "[7] Blackboard": "Blackboard",
        "[8] System Health": "System Health",
        "[9] 安全原則": "安全原則",
    }
    for label, needle in required.items():
        _check(needle in guide, f"{label} 含 '{needle}'")

    print("[10] OPERATOR_GUIDE 沒有夾帶真實 .env secret")
    # 不可出現常見的金鑰/憑證樣式，或「環境變數=真實值」。
    secret_patterns = [
        (r"sk-[A-Za-z0-9]{16,}", "OpenAI 風格金鑰"),
        (r"ghp_[A-Za-z0-9]{20,}", "GitHub token"),
        (r"AIza[A-Za-z0-9_\-]{20,}", "Google API key"),
        (r"xox[baprs]-[A-Za-z0-9-]{10,}", "Slack token"),
        (r"(HERMES_ADAPTER_TOKEN|HERMES_CALLBACK_SECRET)\s*=\s*\S+", "敏感環境變數帶值"),
        (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "私鑰"),
    ]
    leaked = []
    for pat, desc in secret_patterns:
        if re.search(pat, guide):
            leaked.append(desc)
    _check(not leaked, f"沒有 secret 樣式（命中：{leaked or '無'}）")
    # 提到 .env 是可以的（教學用），但只能是檔名/設定提醒，不是貼出值。
    _check(".env" in guide, "（教學）有提到 .env 檔名但不含其值")

    if FAILURES:
        print(f"\n❌ Operator Guide 文件測試失敗 {len(FAILURES)} 項：")
        for f in FAILURES:
            print(f"   - {f}")
        return 1
    print("\n✅ Operator Guide 文件測試全數通過。")
    return 0


if __name__ == "__main__":
    sys.exit(main_test())
