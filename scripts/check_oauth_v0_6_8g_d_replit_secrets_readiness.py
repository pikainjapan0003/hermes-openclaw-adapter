#!/usr/bin/env python3
"""v0.6.8G-D — Replit Secrets Placement Confirmation（只確認 env key 狀態，永不顯示 token 值）。

只做環境變數確認，**不連 Google、不跑 OAuth、不讀 Owner OAuth JSON、不真寫 Sheets**：
- GOOGLE_OAUTH_REFRESH_TOKEN：存在且非空 → 印 `SET`；否則印 `MISSING`（並判為失敗）。
  **永不**印出 token 值、**永不** log token。
- GOOGLE_SHEETS_ENABLED：必須為 `false`（Sheets 真寫入仍關閉）。
- GOOGLE_SHEETS_WRITE_MODE：必須為 `pilot`。

本機若無 Replit Secrets，可用測試 env 模擬（見 docs）；本腳本不含任何真 token。回傳 0/1。
"""

from __future__ import annotations

import os
import sys

FAILURES: list[str] = []


def _check(cond: bool, label: str) -> None:
    print(f"  {'ok ' if cond else '❌ '}: {label}")
    if not cond:
        FAILURES.append(label)


def main() -> int:
    print("[1] GOOGLE_OAUTH_REFRESH_TOKEN 狀態（只印 SET / MISSING，不印值）")
    rt = os.environ.get("GOOGLE_OAUTH_REFRESH_TOKEN", "")
    rt_set = bool(rt.strip())
    print(f"  GOOGLE_OAUTH_REFRESH_TOKEN: {'SET' if rt_set else 'MISSING'}")
    _check(rt_set, "GOOGLE_OAUTH_REFRESH_TOKEN 存在且非空")

    print("[2] GOOGLE_SHEETS_ENABLED 必須為 false（Sheets 真寫入仍關閉）")
    enabled = os.environ.get("GOOGLE_SHEETS_ENABLED", "")
    enabled_norm = enabled.strip().lower()
    print(f"  GOOGLE_SHEETS_ENABLED: {enabled_norm or '(unset)'}")
    _check(enabled_norm == "false", "GOOGLE_SHEETS_ENABLED == false")

    print("[3] GOOGLE_SHEETS_WRITE_MODE 必須為 pilot")
    mode = os.environ.get("GOOGLE_SHEETS_WRITE_MODE", "")
    mode_norm = mode.strip().lower()
    print(f"  GOOGLE_SHEETS_WRITE_MODE: {mode_norm or '(unset)'}")
    _check(mode_norm == "pilot", "GOOGLE_SHEETS_WRITE_MODE == pilot")

    if FAILURES:
        print(f"\n❌ v0.6.8G-D Replit secrets 確認失敗 {len(FAILURES)} 項：")
        for f in FAILURES:
            print(f"   - {f}")
        print("（提示：本機若無 Replit Secrets，可用測試 env 模擬；不要貼真 token 進指令歷史。）")
        return 1
    print("\n✅ v0.6.8G-D Replit secrets 確認通過（未顯示任何 token 值，Sheets 寫入仍關閉）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
