#!/usr/bin/env python3
"""OAuth Local Consent Helper（本機 consent helper）。

版本沿革：
- v0.6.8C：本機 consent helper 程式結構。
- v0.6.8F：補上 guarded live scaffolding（`--client-secret-file`、檔案驗證、token non-disclosure）。
- v0.6.8G-B：**unlock guarded local consent** —— 不再以永久 kill-switch 封住 live，
  改由「explicit Owner flags + local-only + file validation + token display acknowledgement」把關。

安全立場（v0.6.8G-B）：
- 預設 dry-run（無參數 / `--dry-run` / `--explain` 皆 exit 0，不連 Google、不讀 .env、不碰 token）。
- 進入真正 consent flow 前，必須同時具備：`--live` + `--i-understand-local-only` + `--client-secret-file`。
- 偵測 Replit / CI / GitHub Actions 一律拒絕（exit 2）。
- client secret 檔必須：在 repo 外、非 service account、檔名非 `my-openclaw*`、為 OAuth Desktop（installed）。
- 預設**不輸出** refresh token；只回報 present: YES/NO + scopes。
- 只有同時加上 `--show-refresh-token-once` + `--i-understand-token-will-be-visible`，
  才會在警告 + countdown 後**顯示一次 refresh token**；**永不**顯示 access token、**永不**寫 token 檔、
  **永不** log token、**不**自動複製 clipboard。
- google library 只在真正取得憑證時延遲 import；dry-run 不 import。
- 取得憑證的步驟集中在 `_obtain_credentials()`，測試以 monkeypatch 注入 fake flow，**永不**連真 Google。

詳見 docs/HERMES_OPENCLAW_OAUTH_V0_6_8G_B_LIVE_CONSENT_UNLOCK.md。
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# 預設 dry-run。
DEFAULT_DRY_RUN = True

# v0.6.8G-B：live 能力已啟用，但「不靠永久 kill-switch」，而是靠下方整套 explicit guard。
# 預設仍不會跑 live（需 --live + 完整風險旗標）。
LIVE_CONSENT_ENABLED = True

# 顯示 refresh token 前的 countdown 秒數（測試可設 0 跳過）。
SHOW_TOKEN_COUNTDOWN_SECONDS = 5

# 真正取得憑證需要的環境變數（只列 key 名，永不放真值、永不印值）。
REQUIRED_LIVE_ENV_KEYS = (
    "GOOGLE_OAUTH_CLIENT_ID",
    "GOOGLE_OAUTH_CLIENT_SECRET",
    "GOOGLE_SHEETS_SPREADSHEET_ID",
)

PREFERRED_SCOPE = "https://www.googleapis.com/auth/spreadsheets"

# 偵測「不應跑 live OAuth」的環境（Replit / 一般 CI / GitHub Actions）。
NON_LOCAL_ENV_VARS = (
    "REPL_ID", "REPL_SLUG", "REPLIT_DB_URL", "REPLIT_DEV_DOMAIN", "REPLIT",
    "CI", "GITHUB_ACTIONS",
)

# 不安全的 client secret 檔名前綴。
UNSAFE_FILENAME_PREFIXES = ("my-openclaw",)

SAFETY_NOTES = (
    "預設 dry-run；無參數即 dry-run。",
    "--live 必須搭配 --i-understand-local-only，否則拒絕（exit 2）。",
    "--live 必須提供 --client-secret-file（缺則拒絕 exit 2）。",
    "live 只能在 Owner 本機跑；偵測到 Replit / CI / GitHub Actions 會拒絕（exit 2）。",
    "client secret 檔不得在 repo 內、不得是 service account、檔名不得是 my-openclaw*、須為 Desktop App。",
    "預設不輸出 refresh token；只回報 present: YES/NO + scopes。",
    "只有 --show-refresh-token-once + --i-understand-token-will-be-visible 才會顯示一次 refresh token。",
    "永不顯示 access token、永不寫 token 檔、永不 log token、不自動複製 clipboard。",
    "google library 只在真正取得憑證時延遲 import；dry-run 不 import。",
    "顯示出的 refresh token 由 Owner 立即手動放進 Replit Secrets（GOOGLE_OAUTH_REFRESH_TOKEN），勿外流。",
)

FUTURE_FLOW_STEPS = (
    "Owner 在 Google Cloud Console 建立 OAuth 2.0 Client ID（Desktop app）。",
    "把 client_secret JSON 放本機 repo 外安全位置（不進 repo、不上傳 Replit / Drive）。",
    "在本機跑：--live --i-understand-local-only --client-secret-file <repo 外路徑>。",
    "Owner 同意最小 scope（優先 spreadsheets）。",
    "預設只看到 present: YES/NO + scopes；不顯示真 token。",
    "需取出 token 時，再加 --show-refresh-token-once --i-understand-token-will-be-visible。",
    "顯示一次後立即手動貼進 Replit Secrets（GOOGLE_OAUTH_REFRESH_TOKEN）。",
    "本機清除任何暫存；client secret 只放 repo 外安全處。",
)


def _detect_non_local_env() -> list[str]:
    """回報哪些「非本機」環境變數被偵測到（不印值，只回報 key 名）。"""
    return [k for k in NON_LOCAL_ENV_VARS if os.environ.get(k)]


def _validate_client_secret_file(path_str: str) -> tuple[bool, str]:
    """驗證 client secret 檔是否可安全用於本機 live consent。

    只檢查「檔案位置 + JSON 結構鍵名」，**永不輸出任何欄位值**。回傳 (ok, reason)。
    """
    if not path_str:
        return False, "缺少 --client-secret-file"
    p = Path(path_str).expanduser()
    if not p.is_file():
        return False, "client secret 檔不存在"
    try:
        rp = p.resolve()
        if rp == ROOT or ROOT in rp.parents:
            return False, "client secret 檔不得位於 repo 目錄內"
    except OSError:
        return False, "無法解析 client secret 檔路徑"
    name_lower = p.name.lower()
    if any(name_lower.startswith(pre) for pre in UNSAFE_FILENAME_PREFIXES):
        return False, "client secret 檔名疑似不安全（my-openclaw*）"
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False, "client secret 檔不是合法 JSON"
    if not isinstance(data, dict):
        return False, "client secret JSON 結構不符（非物件）"
    if data.get("type") == "service_account" or "private_key" in data:
        return False, "偵測到 service account JSON；live OAuth 需 Desktop App client"
    if "installed" in data:
        return True, "OAuth Desktop App client（installed）"
    if "web" in data:
        return False, "偵測到 web client；需 Desktop App（installed）client"
    return False, "格式不像 OAuth Desktop App client secret"


def _obtain_credentials(client_secret_file: str):
    """真正跑 OAuth consent 取得憑證。

    **唯一**會連 Google / 延遲 import google library 的地方；測試以 monkeypatch 取代本函式，
    因此測試永不連真 Google、永不開瀏覽器。
    """
    from google_auth_oauthlib.flow import InstalledAppFlow  # 延遲 import

    flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, scopes=[PREFERRED_SCOPE])
    return flow.run_local_server(port=0)


def _emit_result(creds, show_refresh_token_once: bool) -> int:
    """回報憑證狀態。預設只印 present: YES/NO + scopes；access token 永不顯示。

    僅在 show_refresh_token_once=True 時，於警告 + countdown 後顯示「一次」refresh token。
    """
    has_refresh = bool(getattr(creds, "refresh_token", None))
    has_access = bool(getattr(creds, "token", None))
    scopes = getattr(creds, "scopes", None) or []
    print(f"refresh token present: {'YES' if has_refresh else 'NO'}")
    print(f"access token present: {'YES' if has_access else 'NO'}")
    print("scopes: " + ", ".join(scopes))

    if show_refresh_token_once:
        rt = getattr(creds, "refresh_token", None)
        if not rt:
            print("（無 refresh token 可顯示。）", file=sys.stderr)
            return 0
        print("\n⚠️  即將顯示 refresh token 一次。請注意終端機歷史與螢幕截圖風險。", file=sys.stderr)
        for n in range(SHOW_TOKEN_COUNTDOWN_SECONDS, 0, -1):
            print(f"   顯示倒數 {n} ...", file=sys.stderr)
            time.sleep(1)
        print("=== REFRESH TOKEN (shown once) ===")
        print(rt)
        print("=== END REFRESH TOKEN ===")
        print("\n顯示後請立即：", file=sys.stderr)
        print("  - 不要貼到任何聊天工具（Claude / ChatGPT / Discord / Slack）。", file=sys.stderr)
        print("  - 不要 commit 進 repo。", file=sys.stderr)
        print("  - 立刻放入 Replit Secrets：GOOGLE_OAUTH_REFRESH_TOKEN。", file=sys.stderr)
        print("  - 若外洩立即 revoke / rotate（撤銷授權並重新產生）。", file=sys.stderr)
    return 0


def _print_dry_run(explain: bool) -> int:
    print("=== OAuth Local Consent Helper (v0.6.8G-B) — DRY-RUN ===")
    print("本次為 dry-run：不連 Google、不跑真 OAuth、不碰任何 token。\n")
    print("[安全規則]")
    for note in SAFETY_NOTES:
        print(f"  ok : {note}")
    print("\n[真正取得憑證需要的環境變數 / 參數（key 名，非真值）]")
    for key in REQUIRED_LIVE_ENV_KEYS:
        print(f"  - {key}")
    print("  - --client-secret-file <repo 外的 Desktop App client_secret JSON 路徑>")
    print(f"  - 最小 scope（優先）: {PREFERRED_SCOPE}")
    print("  - 取得後手動放入 Replit Secrets: GOOGLE_OAUTH_REFRESH_TOKEN")
    if explain:
        print("\n[Owner 本機 live consent 流程]")
        for i, step in enumerate(FUTURE_FLOW_STEPS, 1):
            print(f"  {i}. {step}")
        print("\n[為什麼只能本機跑]")
        print("  - Replit / production 不應跑 OAuth consent，也不應保存 client secret / token 檔。")
    print("\n文件：docs/HERMES_OPENCLAW_OAUTH_V0_6_8G_B_LIVE_CONSENT_UNLOCK.md")
    return 0


def _refuse_live_no_flag() -> int:
    print("❌ 拒絕：--live 必須搭配 --i-understand-local-only 才能進入 live 分支。", file=sys.stderr)
    print("   live consent 只能在 Owner 本機進行。", file=sys.stderr)
    return 2


def _run_live_guarded(
    client_secret_file: str | None,
    show_refresh_token_once: bool = False,
    understand_token_visible: bool = False,
) -> int:
    """live 分支：通過整套 guard 後才取得憑證並回報；測試以 monkeypatch 注入 fake flow。"""
    non_local = _detect_non_local_env()
    if non_local:
        print("❌ 拒絕：偵測到非本機環境（Replit / CI / GitHub Actions），不在此處執行 OAuth consent。",
              file=sys.stderr)
        print(f"   偵測到的環境旗標：{', '.join(non_local)}", file=sys.stderr)
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

    if show_refresh_token_once and not understand_token_visible:
        print("❌ 拒絕：--show-refresh-token-once 必須再加 --i-understand-token-will-be-visible。",
              file=sys.stderr)
        return 2

    if not LIVE_CONSENT_ENABLED:
        print("Live OAuth flow is disabled (LIVE_CONSENT_ENABLED is False).", file=sys.stderr)
        return 3

    creds = _obtain_credentials(client_secret_file)
    return _emit_result(creds, show_refresh_token_once=show_refresh_token_once)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="OAuth Local Consent Helper (v0.6.8G-B) — 預設 dry-run；live 需完整風險旗標。",
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
    parser.add_argument("--show-refresh-token-once", action="store_true",
                        help="顯示一次 refresh token（需再加 --i-understand-token-will-be-visible）。")
    parser.add_argument("--i-understand-token-will-be-visible", action="store_true",
                        help="確認知道 refresh token 將在畫面上可見的安全旗標。")
    args = parser.parse_args(argv)

    if args.live:
        if not args.i_understand_local_only:
            return _refuse_live_no_flag()
        return _run_live_guarded(
            args.client_secret_file,
            show_refresh_token_once=args.show_refresh_token_once,
            understand_token_visible=args.i_understand_token_will_be_visible,
        )

    return _print_dry_run(explain=args.explain)


if __name__ == "__main__":
    sys.exit(main())
