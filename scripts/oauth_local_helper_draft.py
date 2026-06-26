#!/usr/bin/env python3
"""v0.6.8B — OAuth Local Helper *草案*（預設 dry-run，不連 Google、不開 browser、不碰 token）。

這支腳本是「未來在 Owner 本機取得 refresh token」的**草案 / 占位**，本身**不做任何真事**：
- 不 import 任何 google library。
- 不讀 .env、不讀 / 不印任何 client secret / token。
- 不開 browser、不連網路、不啟動 redirect server。
- 不產生 / 不輸出 / 不寫入任何 refresh token 或 access token 檔。

行為：
- 無參數 / `--explain`：dry-run，印出未來 OAuth 流程、需要的參數 key 名、安全自檢，exit 0。
- `--live`：**明確拒絕**（v0.6.8B 不在 repo 內跑真 OAuth），exit 2。

真實作（live 模式）留待 v0.6.9，且只在 Owner 本機進行。
詳見 docs/HERMES_OPENCLAW_OAUTH_LOCAL_HELPER_DRAFT_V0_6_8B.md。
"""

from __future__ import annotations

import argparse
import sys

# 預設 dry-run。本草案不提供真實的 OAuth 執行路徑。
DEFAULT_DRY_RUN = True

# 未來真實作需要的參數（只列 key 名，永不放真值）。
REQUIRED_PARAM_KEYS = (
    "GOOGLE_OAUTH_CLIENT_ID",      # 可公開但建議 Secrets
    "GOOGLE_OAUTH_CLIENT_SECRET",  # 高敏感，僅本機 consent 時用
    "GOOGLE_OAUTH_REFRESH_TOKEN",  # 最高敏感，consent 產出後貼 Replit Secrets
)

# 未來真實作優先的最小 scope（草案不請求任何 scope，僅描述）。
PREFERRED_SCOPE = "https://www.googleapis.com/auth/spreadsheets"

FUTURE_FLOW_STEPS = (
    "Owner 在 Google Cloud Console 建立 OAuth 2.0 Client ID（Desktop app）。",
    "把 client_id / client_secret 放本機環境變數或本機檔案（不進 repo）。",
    "在本機跑 live helper：以 Installed App / Loopback 流程開啟 consent 頁。",
    "Owner 同意最小 scope（優先 spreadsheets）。",
    "helper 收到 authorization code，換取 refresh token + access token。",
    "refresh token 只顯示給 Owner，絕不寫進 repo。",
    "Owner 手動把 refresh token 貼進 Replit Secrets（GOOGLE_OAUTH_REFRESH_TOKEN）。",
    "本機刪除暫存 token；client secret 只放 Replit Secrets / 本機安全處。",
)

SAFETY_SELF_CHECKS = (
    "預設 dry-run（DEFAULT_DRY_RUN = True）",
    "不 import 任何 google library",
    "不讀 .env、不讀 / 不印 client secret / token",
    "不開 browser、不連網路",
    "不產生 / 不輸出 / 不寫入任何 token",
    "--live 會被明確拒絕（草案不在 repo 內跑真 OAuth）",
)


def _print_dry_run(explain: bool) -> int:
    print("=== OAuth Local Helper Draft (v0.6.8B) — DRY-RUN ===")
    print("本草案不連 Google、不開 browser、不碰任何 token。\n")

    print("[安全自檢]")
    for item in SAFETY_SELF_CHECKS:
        print(f"  ok : {item}")

    print("\n[未來真實作需要的參數（key 名，非真值）]")
    for key in REQUIRED_PARAM_KEYS:
        print(f"  - {key}")
    print(f"  - 最小 scope（優先）: {PREFERRED_SCOPE}")

    if explain:
        print("\n[未來真實作流程（v0.6.9，於 Owner 本機）]")
        for i, step in enumerate(FUTURE_FLOW_STEPS, 1):
            print(f"  {i}. {step}")

    print("\n提示：真實取得 refresh token 的 live 流程留待 v0.6.9，且只在 Owner 本機進行。")
    print("      文件：docs/HERMES_OPENCLAW_OAUTH_LOCAL_HELPER_DRAFT_V0_6_8B.md")
    return 0


def _refuse_live() -> int:
    print("❌ 拒絕：v0.6.8B 的 OAuth Local Helper 僅為草案，不在 repo 內執行真 OAuth。", file=sys.stderr)
    print("   真實 consent（取得 refresh token）留待 v0.6.9，且只在 Owner 本機進行。", file=sys.stderr)
    print("   本草案不連 Google、不開 browser、不產生任何 token。", file=sys.stderr)
    return 2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="OAuth Local Helper draft (v0.6.8B) — 預設 dry-run，不連 Google。",
    )
    parser.add_argument(
        "--explain", action="store_true",
        help="dry-run，並額外列出未來真實作流程步驟。",
    )
    parser.add_argument(
        "--live", action="store_true",
        help="（草案占位）會被明確拒絕；v0.6.8B 不跑真 OAuth。",
    )
    args = parser.parse_args(argv)

    if args.live:
        return _refuse_live()
    return _print_dry_run(explain=args.explain)


if __name__ == "__main__":
    sys.exit(main())
