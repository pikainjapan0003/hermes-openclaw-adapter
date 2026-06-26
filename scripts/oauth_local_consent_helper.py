#!/usr/bin/env python3
"""v0.6.8C/F — OAuth Local Consent Helper（本機 consent helper；預設 dry-run，本版仍不跑真 OAuth）。

v0.6.8C：把草案升級為「本機 consent helper 程式結構」。
v0.6.8F：補上 guarded live 能力——新增 `--client-secret-file`、client secret 檔案安全驗證、
         Plan A 回報（只說 token 存在與否，不顯示真值）、延遲 import google（只在 live 路徑）。

本版（v0.6.8F）安全立場：
- 預設 dry-run，不連 Google、不讀 .env、不開 browser、不產生 / 不印 / 不寫任何 token。
- `--live` 必須額外搭配 `--i-understand-local-only`，否則拒絕（exit 2）。
- live 分支：偵測 Replit / CI → 拒絕（exit 2）；要求 `--client-secret-file`（缺則 exit 2）；
  驗證 client secret 檔（不在 repo 內、非 service account、檔名非 my-openclaw*、須為 Desktop App）。
- 真正的網路 consent 仍由 `LIVE_CONSENT_ENABLED`（本版 = False）這道最終 kill-switch 封住：
  驗證通過後印「結構就緒但本版停用」並 exit 3。Owner 未來在本機 v0.6.8G 才翻開。
- live 分支**永不**把 refresh / access token 印到 console，**永不**寫 token 檔。
- google library 只在 live 真執行路徑延遲 import；dry-run 完全不 import google。

詳見 docs/HERMES_OPENCLAW_OAUTH_LIVE_HELPER_ENABLEMENT_V0_6_8F.md。
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# 預設 dry-run。
DEFAULT_DRY_RUN = True

# 最終 kill-switch：實際 live consent（連 Google、跑 OAuth、換 token）一律停用。
# v0.6.8F 只備齊結構；真正啟用只能由 Owner 在本機未來版本（v0.6.8G）手動開啟。
LIVE_CONSENT_ENABLED = False

# 未來 live 真執行需要的環境變數（只列 key 名，永不放真值、永不印值）。
REQUIRED_LIVE_ENV_KEYS = (
    "GOOGLE_OAUTH_CLIENT_ID",        # 可公開但建議 Secrets
    "GOOGLE_OAUTH_CLIENT_SECRET",    # 高敏感，僅本機 consent 時用
    "GOOGLE_SHEETS_SPREADSHEET_ID",  # 目標試算表 ID
)

# live 真執行優先的最小 scope（dry-run 只描述、不請求）。
PREFERRED_SCOPE = "https://www.googleapis.com/auth/spreadsheets"

# 偵測「不應跑 live OAuth」的環境（Replit / 一般 CI）。
NON_LOCAL_ENV_VARS = (
    "REPL_ID", "REPL_SLUG", "REPLIT_DB_URL", "REPLIT_DEV_DOMAIN", "REPLIT",
    "CI", "GITHUB_ACTIONS",
)

# 不安全的 client secret 檔名前綴（避免誤用其他用途的金鑰）。
UNSAFE_FILENAME_PREFIXES = ("my-openclaw",)

FUTURE_FLOW_STEPS = (
    "Owner 在 Google Cloud Console 建立 OAuth 2.0 Client ID（Desktop app）。",
    "把 client_secret JSON 放本機 repo 外安全位置（不進 repo、不上傳 Replit / Drive）。",
    "在本機跑 live helper：--live --i-understand-local-only --client-secret-file <repo 外路徑>。",
    "Owner 同意最小 scope（優先 spreadsheets）。",
    "helper 以 Installed App / Loopback 流程換取 refresh token + access token。",
    "helper 只回報 token 是否存在（YES/NO）+ scopes；refresh token 不印 console、不寫檔。",
    "Owner 依 v0.6.8G runbook 安全取得 token 並手動放進 Replit Secrets（GOOGLE_OAUTH_REFRESH_TOKEN）。",
    "本機清除任何暫存；client secret 只放 repo 外安全處。",
)

SAFETY_NOTES = (
    "預設 dry-run；無參數即 dry-run。",
    "--live 必須搭配 --i-understand-local-only，否則拒絕（exit 2）。",
    "live 只能在 Owner 本機跑；偵測到 Replit / CI 會拒絕（exit 2）。",
    "live 必須提供 --client-secret-file（缺則拒絕 exit 2）。",
    "client secret 檔不得在 repo 內、不得是 service account、檔名不得是 my-openclaw*。",
    "本版 LIVE_CONSENT_ENABLED = False：驗證通過仍不連 Google、不跑真 OAuth、不換 token。",
    "refresh / access token 永不印 console、永不寫檔、永不進 repo。",
    "google library 只在 live 真執行路徑延遲 import；dry-run 不 import。",
    "token 只能由 Owner 依 v0.6.8G 手動放進 Replit Secrets（GOOGLE_OAUTH_REFRESH_TOKEN）。",
)


def _detect_non_local_env() -> list[str]:
    """回報哪些「非本機」環境變數被偵測到（不印值，只回報 key 名）。"""
    return [k for k in NON_LOCAL_ENV_VARS if os.environ.get(k)]


def _validate_client_secret_file(path_str: str) -> tuple[bool, str]:
    """驗證 client secret 檔是否可安全用於本機 live consent。

    只檢查「檔案位置 + JSON 結構鍵名」，**永不輸出任何欄位值**（不印 client_id / secret）。
    回傳 (ok, reason)。
    """
    if not path_str:
        return False, "缺少 --client-secret-file"
    p = Path(path_str).expanduser()
    if not p.is_file():
        return False, "client secret 檔不存在"

    # 不得位於 repo 目錄內（避免被 commit）。
    try:
        rp = p.resolve()
        if rp == ROOT or ROOT in rp.parents:
            return False, "client secret 檔不得位於 repo 目錄內"
    except OSError:
        return False, "無法解析 client secret 檔路徑"

    # 檔名不得是 my-openclaw*.json 等不安全名稱。
    name_lower = p.name.lower()
    if any(name_lower.startswith(pre) for pre in UNSAFE_FILENAME_PREFIXES):
        return False, "client secret 檔名疑似不安全（my-openclaw*）"

    # 解析 JSON 結構（只看鍵名，不輸出值）。
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False, "client secret 檔不是合法 JSON"
    if not isinstance(data, dict):
        return False, "client secret JSON 結構不符（非物件）"

    # service account 一律拒絕（live OAuth 需 Desktop App client，不是 SA）。
    if data.get("type") == "service_account" or "private_key" in data:
        return False, "偵測到 service account JSON；live OAuth 需 Desktop App client"

    # 必須是 Installed / Desktop App client（頂層有 "installed"）。
    if "installed" in data:
        return True, "OAuth Desktop App client（installed）"
    if "web" in data:
        return False, "偵測到 web client；需 Desktop App（installed）client"
    return False, "格式不像 OAuth Desktop App client secret"


def _print_dry_run(explain: bool) -> int:
    print("=== OAuth Local Consent Helper (v0.6.8F) — DRY-RUN ===")
    print("本版不連 Google、不跑真 OAuth、不開 browser、不碰任何 token。\n")

    print("[安全規則]")
    for note in SAFETY_NOTES:
        print(f"  ok : {note}")

    print("\n[未來 live 真執行需要的環境變數 / 參數（key 名，非真值）]")
    for key in REQUIRED_LIVE_ENV_KEYS:
        print(f"  - {key}")
    print("  - --client-secret-file <repo 外的 Desktop App client_secret JSON 路徑>")
    print(f"  - 最小 scope（優先）: {PREFERRED_SCOPE}")
    print("  - 取得後手動放入 Replit Secrets: GOOGLE_OAUTH_REFRESH_TOKEN")

    if explain:
        print("\n[未來 live 真執行流程（只能在 Owner 本機）]")
        for i, step in enumerate(FUTURE_FLOW_STEPS, 1):
            print(f"  {i}. {step}")
        print("\n[為什麼只能本機跑]")
        print("  - Replit / production 不應跑 OAuth consent，也不應保存 client secret / token 檔。")
        print("  - consent 會短暫接觸 client secret，且產出長期 refresh token，必須在受控本機完成。")

    print("\n提示：真正 live consent 留待 Owner 本機 v0.6.8G 啟用；本版只備齊 guarded 結構。")
    print("      文件：docs/HERMES_OPENCLAW_OAUTH_LIVE_HELPER_ENABLEMENT_V0_6_8F.md")
    return 0


def _refuse_live_no_flag() -> int:
    print("❌ 拒絕：--live 必須搭配 --i-understand-local-only 才能進入 live 分支。", file=sys.stderr)
    print("   live consent 只能在 Owner 本機進行，且本版不會實際連 Google。", file=sys.stderr)
    return 2


def _run_live_guarded(client_secret_file: str | None) -> int:
    """live 分支：本版備齊 guard + 驗證結構，但因 kill-switch 仍不執行真 OAuth。

    流程：
      1. 偵測 Replit / CI → 拒絕（exit 2）。
      2. 要求 --client-secret-file（缺則 exit 2）。
      3. 驗證 client secret 檔（不在 repo / 非 SA / 檔名安全 / Desktop App）→ 不合則 exit 2。
      4. LIVE_CONSENT_ENABLED 為 False（本版）→ 印「結構就緒但停用」後 exit 3。
      5.（本版不可達）真正 consent 才延遲 import google-auth-oauthlib 並 run_local_server，
         成功後只回報 token 是否存在（YES/NO）+ scopes，**不印真 token、不寫 token 檔**。
    """
    non_local = _detect_non_local_env()
    if non_local:
        print("❌ 拒絕：偵測到非本機環境（Replit / CI），不在此處執行 OAuth consent。", file=sys.stderr)
        print(f"   偵測到的環境旗標：{', '.join(non_local)}", file=sys.stderr)
        print("   OAuth consent 只能在 Owner 本機進行。", file=sys.stderr)
        return 2

    if not client_secret_file:
        print("❌ 拒絕：live 需要 --client-secret-file <repo 外的 Desktop App client_secret JSON>。",
              file=sys.stderr)
        return 2

    ok, reason = _validate_client_secret_file(client_secret_file)
    if not ok:
        print(f"❌ 拒絕：client secret 檔未通過驗證 — {reason}。", file=sys.stderr)
        return 2
    print(f"ℹ️  client secret 檔通過驗證：{reason}（未輸出任何欄位值）。")

    if not LIVE_CONSENT_ENABLED:
        print("Live OAuth flow is still disabled in v0.6.8F.", file=sys.stderr)
        print("This version only validates guarded live prerequisites.", file=sys.stderr)
        print("Proceed to v0.6.8G only with Owner approval.", file=sys.stderr)
        print("（本版不連 Google、不跑真 OAuth、不換 / 不印 / 不寫任何 token；"
              "未取得任何 refresh token。）", file=sys.stderr)
        return 3

    # --- 以下為「未來真執行」程式結構；本版因 LIVE_CONSENT_ENABLED=False 不可達。 ---
    # 延遲 import：只有真執行才需要 google library（dry-run 不 import）。
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        print("❌ live 真執行需要 google-auth-oauthlib（本機自行安裝）。", file=sys.stderr)
        return 4

    flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, scopes=[PREFERRED_SCOPE])
    creds = flow.run_local_server(port=0)
    # Plan A：只回報存在與否與 scopes，**不印任何 token 真值、不寫 token 檔**。
    print("refresh token 是否存在：" + ("YES" if getattr(creds, "refresh_token", None) else "NO"))
    print("access token 是否存在：" + ("YES" if getattr(creds, "token", None) else "NO"))
    print("scopes：" + ", ".join(getattr(creds, "scopes", None) or []))
    print("下一步：請依 v0.6.8G runbook 安全取得 token 並放入 Replit Secrets（本版/本流程不顯示真 token）。")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="OAuth Local Consent Helper (v0.6.8F) — 預設 dry-run，本版不跑真 OAuth。",
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="只印流程，不讀 credentials、不連 Google（預設行為）。")
    parser.add_argument("--explain", action="store_true",
                        help="dry-run，並額外列出 live 流程與安全說明。")
    parser.add_argument("--live", action="store_true",
                        help="進入 live 分支（需 --i-understand-local-only + --client-secret-file）。")
    parser.add_argument("--i-understand-local-only", action="store_true",
                        help="確認只在 Owner 本機執行的安全旗標。")
    parser.add_argument("--client-secret-file", default=None,
                        help="live 用：repo 外的 Desktop App client_secret JSON 路徑。")
    args = parser.parse_args(argv)

    if args.live:
        if not args.i_understand_local_only:
            return _refuse_live_no_flag()
        return _run_live_guarded(args.client_secret_file)

    # 無參數 / --dry-run / --explain 皆為 dry-run。
    return _print_dry_run(explain=args.explain)


if __name__ == "__main__":
    sys.exit(main())
