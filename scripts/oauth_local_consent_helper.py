#!/usr/bin/env python3
"""v0.6.8C — OAuth Local Consent Helper（本機 consent helper；預設 dry-run，本版不跑真 OAuth）。

把 v0.6.8B 的草案升級為「本機可用的 consent helper 程式結構」，但本版**仍不執行真 OAuth**：
- 預設 dry-run，不連 Google、不讀 .env、不開 browser、不產生 / 不印 / 不寫任何 token。
- `--live` 必須額外搭配 `--i-understand-local-only` 才能進入 live 分支，否則拒絕（exit 2）。
- live 分支會：偵測 Replit / CI → 拒絕（exit 2）；真正 consent 由 `LIVE_CONSENT_ENABLED`
  旗標封住（本版 = False），印出「結構就緒但本版停用」後 exit 3。
- live 分支**永不**把 refresh token 印到 console，**永不**寫 token 檔。
- google library 只在 live 真執行路徑用延遲 import；dry-run 完全不 import google。

未來真正取得 refresh token（live 真執行）只能由 Owner 在**自己本機**進行，並手動把
token 放進 Replit Secrets（GOOGLE_OAUTH_REFRESH_TOKEN）。本檔不替 Owner 做這件事。

詳見 docs/HERMES_OPENCLAW_OAUTH_LOCAL_CONSENT_HELPER_V0_6_8C.md。
"""

from __future__ import annotations

import argparse
import os
import sys

# 預設 dry-run。
DEFAULT_DRY_RUN = True

# v0.6.8C 安全閘：實際 live consent（連 Google、跑 OAuth、換 token）一律停用。
# 本版只提供程式結構；真正啟用只能由 Owner 在本機未來版本手動開啟。
LIVE_CONSENT_ENABLED = False

# 未來 live 真執行需要的環境變數（只列 key 名，永不放真值、永不印值）。
REQUIRED_LIVE_ENV_KEYS = (
    "GOOGLE_OAUTH_CLIENT_ID",       # 可公開但建議 Secrets
    "GOOGLE_OAUTH_CLIENT_SECRET",   # 高敏感，僅本機 consent 時用
    "GOOGLE_SHEETS_SPREADSHEET_ID",  # 目標試算表 ID
)

# live 真執行優先的最小 scope（dry-run 只描述、不請求）。
PREFERRED_SCOPE = "https://www.googleapis.com/auth/spreadsheets"

# 偵測「不應跑 live OAuth」的環境（Replit / 一般 CI）。
NON_LOCAL_ENV_VARS = (
    "REPL_ID", "REPL_SLUG", "REPLIT_DB_URL", "REPLIT_DEV_DOMAIN", "REPLIT",
    "CI", "GITHUB_ACTIONS",
)

FUTURE_FLOW_STEPS = (
    "Owner 在 Google Cloud Console 建立 OAuth 2.0 Client ID（Desktop app）。",
    "把 client_id / client_secret 放本機環境變數（不進 repo、不寫 .env 進 git）。",
    "在本機跑 live helper：以 Installed App / Loopback 流程開啟 consent 頁。",
    "Owner 同意最小 scope（優先 spreadsheets）。",
    "helper 收到 authorization code，換取 refresh token + access token。",
    "refresh token 不印 console、不寫 repo；Owner 以安全方式取得後手動處理。",
    "Owner 手動把 refresh token 貼進 Replit Secrets（GOOGLE_OAUTH_REFRESH_TOKEN）。",
    "本機清除任何暫存；client secret 只放 Replit Secrets / 本機安全處。",
)

SAFETY_NOTES = (
    "預設 dry-run；無參數即 dry-run。",
    "--live 必須搭配 --i-understand-local-only，否則拒絕（exit 2）。",
    "live 只能在 Owner 本機跑；偵測到 Replit / CI 會拒絕（exit 2）。",
    "本版 LIVE_CONSENT_ENABLED = False：不連 Google、不跑真 OAuth、不換 token。",
    "refresh token 永不印 console、永不寫檔、永不進 repo。",
    "google library 只在 live 真執行路徑延遲 import；dry-run 不 import。",
    "token 只能由 Owner 手動放進 Replit Secrets（GOOGLE_OAUTH_REFRESH_TOKEN）。",
)


def _detect_non_local_env() -> list[str]:
    """回報哪些「非本機」環境變數被偵測到（不印值，只回報 key 名）。"""
    return [k for k in NON_LOCAL_ENV_VARS if os.environ.get(k)]


def _print_dry_run(explain: bool) -> int:
    print("=== OAuth Local Consent Helper (v0.6.8C) — DRY-RUN ===")
    print("本版不連 Google、不跑真 OAuth、不開 browser、不碰任何 token。\n")

    print("[安全規則]")
    for note in SAFETY_NOTES:
        print(f"  ok : {note}")

    print("\n[未來 live 真執行需要的環境變數（key 名，非真值）]")
    for key in REQUIRED_LIVE_ENV_KEYS:
        print(f"  - {key}")
    print(f"  - 最小 scope（優先）: {PREFERRED_SCOPE}")
    print("  - 取得後手動放入 Replit Secrets: GOOGLE_OAUTH_REFRESH_TOKEN")

    if explain:
        print("\n[未來 live 真執行流程（只能在 Owner 本機）]")
        for i, step in enumerate(FUTURE_FLOW_STEPS, 1):
            print(f"  {i}. {step}")
        print("\n[為什麼只能本機跑]")
        print("  - Replit / production 不應跑 OAuth consent，也不應保存 client secret / token 檔。")
        print("  - consent 會短暫接觸 client secret，且產出長期 refresh token，必須在受控本機完成。")

    print("\n提示：真正 live consent 留待 Owner 本機未來啟用；本版只提供結構。")
    print("      文件：docs/HERMES_OPENCLAW_OAUTH_LOCAL_CONSENT_HELPER_V0_6_8C.md")
    return 0


def _refuse_live_no_flag() -> int:
    print("❌ 拒絕：--live 必須搭配 --i-understand-local-only 才能進入 live 分支。", file=sys.stderr)
    print("   live consent 只能在 Owner 本機進行，且本版不會實際連 Google。", file=sys.stderr)
    return 2


def _run_live_guarded() -> int:
    """live 分支：本版只有安全結構，不執行真 OAuth。

    流程：
      1. 偵測 Replit / CI → 拒絕（exit 2）。
      2. LIVE_CONSENT_ENABLED 為 False（本版）→ 印「結構就緒但停用」後 exit 3。
      3. （本版不可達）真正 consent 才會延遲 import google-auth-oauthlib 並 run_local_server。
    """
    non_local = _detect_non_local_env()
    if non_local:
        print("❌ 拒絕：偵測到非本機環境（Replit / CI），不在此處執行 OAuth consent。", file=sys.stderr)
        print(f"   偵測到的環境旗標：{', '.join(non_local)}", file=sys.stderr)
        print("   OAuth consent 只能在 Owner 本機進行。", file=sys.stderr)
        return 2

    if not LIVE_CONSENT_ENABLED:
        print("ℹ️  live consent 程式結構已就緒，但本版（v0.6.8C）刻意停用。", file=sys.stderr)
        print("   本版不連 Google、不跑真 OAuth、不換 / 不印 / 不寫任何 token。", file=sys.stderr)
        print("   真正啟用只能由 Owner 在本機未來步驟手動開啟，並自行安裝 google-auth-oauthlib。", file=sys.stderr)
        print("   取得 refresh token 後，Owner 手動放進 Replit Secrets：GOOGLE_OAUTH_REFRESH_TOKEN。", file=sys.stderr)
        return 3

    # --- 以下為「未來真執行」的程式結構；本版因 LIVE_CONSENT_ENABLED=False 不可達。 ---
    # 延遲 import：只有真執行才需要 google library（本版 requirements 未新增）。
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow  # noqa: F401
    except ImportError:
        print("❌ live 真執行需要 google-auth-oauthlib（本機自行安裝；本版不加入 requirements）。",
              file=sys.stderr)
        return 4

    # 真執行時：用 os.environ 的 client_id / client_secret 建 InstalledAppFlow，
    # 以 run_local_server(port=0) 取得 credentials，refresh token **不印、不寫檔**，
    # 僅引導 Owner 以安全方式放入 Replit Secrets。此區塊本版不會執行。
    print("（未來真執行區塊；本版不可達）", file=sys.stderr)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="OAuth Local Consent Helper (v0.6.8C) — 預設 dry-run，本版不跑真 OAuth。",
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="只印流程，不讀 credentials、不連 Google（預設行為）。")
    parser.add_argument("--explain", action="store_true",
                        help="dry-run，並額外列出 live 流程與安全說明。")
    parser.add_argument("--live", action="store_true",
                        help="進入 live 分支（需 --i-understand-local-only；本版仍不連 Google）。")
    parser.add_argument("--i-understand-local-only", action="store_true",
                        help="確認只在 Owner 本機執行的安全旗標。")
    args = parser.parse_args(argv)

    if args.live:
        if not args.i_understand_local_only:
            return _refuse_live_no_flag()
        return _run_live_guarded()

    # 無參數 / --dry-run / --explain 皆為 dry-run。
    return _print_dry_run(explain=args.explain)


if __name__ == "__main__":
    sys.exit(main())
