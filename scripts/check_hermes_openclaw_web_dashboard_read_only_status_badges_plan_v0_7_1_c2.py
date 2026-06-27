#!/usr/bin/env python3
"""v0.7.1-C2 — Web Dashboard Read-only Status Badges Plan 靜態 readiness（純文件檢查，不連任何系統）。

確認 v0.7.1-C2 規劃文件涵蓋必要章節與 plan-only 安全聲明，且本版未越界：
  - plan-only：未改 app/main.py / templates/* / static/*、未新增 route / webhook。
  - 明確聲明 no Queue status mutation / no Worker / no OpenClaw / no Google Sheets / no Result Sink。
靜態檢查：不連外、不寫 DB、不讀 secrets。敏感檢查一律 regex / 格式比對。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOC = ROOT / "docs" / "HERMES_OPENCLAW_WEB_DASHBOARD_READ_ONLY_STATUS_BADGES_PLAN_V0_7_1_C2.md"
READINESS = ROOT / "scripts" / "check_hermes_openclaw_web_dashboard_read_only_status_badges_plan_v0_7_1_c2.py"

APP_MAIN = ROOT / "app" / "main.py"
TEMPLATES_DIR = ROOT / "templates"
STATIC_DIR = ROOT / "static"

REQUIRED_TITLES = (
    "1. Purpose",
    "2. Relationship To v0.7.1-C",
    "3. Why This Version Is Plan-only",
    "4. Existing Dashboard Routes",
    "5. Existing Templates",
    "6. Proposed Read-only Badges",
    "7. Proposed View-model Reuse",
    "8. Production Queue Visibility",
    "9. Local-only Intake DB Visibility",
    "10. No Queue Status Mutation Guarantee",
    "11. No Worker Trigger Guarantee",
    "12. No Result Sink Write Guarantee",
    "13. No Google Sheets Write Guarantee",
    "14. Proposed Minimal Future Implementation",
    "15. Files That May Be Modified In Future Implementation",
    "16. Files That Must Not Be Modified",
    "17. Readiness Criteria For Future Web Dashboard Integration",
    "18. Explicit Non-goals",
    "19. Final Recommendation",
)

REQUIRED_DECLARATIONS = (
    "v0.7.1-C2 is plan-only.",
    "No app/main.py modification.",
    "No template modification.",
    "No static modification.",
    "No route addition.",
    "No Queue status mutation.",
    "No Worker start.",
    "No OpenClaw execution.",
    "No Hermes webhook.",
    "No Google Sheets write.",
    "No Result Sink write.",
    "No production Queue DB write.",
)

# --- 敏感格式比對（regex） ---
RE_SPREADSHEET_URL = re.compile(r"spreadsheets/d/[A-Za-z0-9_-]{20,}")
RE_SPREADSHEET_ASSIGN = re.compile(r"SPREADSHEET_ID\s*[:=]\s*[\"'][A-Za-z0-9_-]{20,}[\"']")
RE_TOKEN_PREFIX = re.compile(r"(ya29\.[A-Za-z0-9_-]{10,}|1//[A-Za-z0-9_-]{10,}|" + "goc" + r"spx-[A-Za-z0-9_-]{10,})")
RE_PRIVATE_KEY = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")
SECRET_KEY_NAMES = (
    "client_secret",
    "refresh_token",
    "access_token",
    "GOOGLE_OAUTH_REFRESH_TOKEN",
    "GOOGLE_OAUTH_CLIENT_SECRET",
    "GOOGLE_SERVICE_ACCOUNT_JSON",
)

# 未來實作才會出現的 badge / view-model 接線痕跡；plan-only 不應出現在既有顯示檔。
DASHBOARD_WIRING_TOKENS = ("dashboard_intake_view_v0_7", "derive_intake_status_view")

FAILURES: list[str] = []


def _check(cond: bool, label: str) -> None:
    print(f"  {'ok ' if cond else 'XX '}: {label}")
    if not cond:
        FAILURES.append(label)


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.is_file() else ""


def _no_real_secret(text: str) -> bool:
    return not (
        RE_SPREADSHEET_URL.search(text)
        or RE_SPREADSHEET_ASSIGN.search(text)
        or RE_TOKEN_PREFIX.search(text)
        or RE_PRIVATE_KEY.search(text)
    )


def main() -> int:
    print("[1] v0.7.1-C2 doc / readiness script 存在")
    _check(DOC.is_file(), "v0.7.1-C2 doc 存在")
    _check(READINESS.is_file(), "readiness script 自身存在")
    doc = _read(DOC)

    print("[2] doc 含必要標題")
    for title in REQUIRED_TITLES:
        _check(title in doc, f"doc 含章節「{title}」")

    print("[3] doc 含 plan-only 安全聲明")
    for line in REQUIRED_DECLARATIONS:
        _check(line in doc, f"doc 含聲明「{line}」")

    print("[4] doc 明確涵蓋關鍵邊界字句")
    _check("No app/main.py modification." in doc, "doc 含 no app/main.py modification")
    _check("No template modification." in doc, "doc 含 no template modification")
    _check("No route addition." in doc, "doc 含 no route addition")
    _check("No Queue status mutation." in doc, "doc 含 no Queue status mutation")
    _check("No Worker start." in doc and "No OpenClaw execution." in doc,
           "doc 含 no Worker start / no OpenClaw execution")
    _check("No Google Sheets write." in doc, "doc 含 no Google Sheets write")

    print("[5] app/main.py 未修改（未接入 badge / view-model 接線）")
    main_txt = _read(APP_MAIN)
    for tok in DASHBOARD_WIRING_TOKENS:
        _check(tok not in main_txt, f"app/main.py 未含接線痕跡「{tok}」")

    print("[6] templates/* 未修改（未加入 intake badge 顯示）")
    tmpl_tokens = ("dashboard_intake_view", "derive_intake_status_view",
                   "intake_mode", "executable_by_worker", "source_mode")
    if TEMPLATES_DIR.is_dir():
        for tmpl in sorted(TEMPLATES_DIR.glob("*.html")):
            txt = _read(tmpl)
            _check(not any(t in txt for t in tmpl_tokens), f"templates/{tmpl.name} 未加入 intake badge")
    else:
        _check(True, "templates/ 目錄不存在（無需檢查）")

    print("[7] static/* 未修改（未加入 intake 相關引用）")
    if STATIC_DIR.is_dir():
        for st in sorted(STATIC_DIR.glob("*")):
            if st.is_file():
                txt = _read(st)
                _check("dashboard_intake_view" not in txt and "intake_mode" not in txt,
                       f"static/{st.name} 未加入 intake 相關引用")
    else:
        _check(True, "static/ 目錄不存在（無需檢查）")

    print("[8] 無新增 route / webhook / POST handler（doc 不含實作痕跡）")
    for bad in ("@app.", "@router.", "FastAPI(", "APIRouter", "add_api_route"):
        _check(bad not in doc, f"doc 不含實作痕跡「{bad}」")

    print("[9] GOOGLE_SHEETS_ENABLED 無 true")
    _check("GOOGLE_SHEETS_ENABLED=true" not in doc, "doc 未出現 GOOGLE_SHEETS_ENABLED=true")

    print("[10] 敏感檢查（格式比對）：doc 不含真實 secret")
    _check(_no_real_secret(doc),
           "doc 不含完整 spreadsheet id / Google Sheets URL / token / private key（格式比對）")
    for key in SECRET_KEY_NAMES:
        _check(key not in doc, f"doc 不含 secret 變數名 {key}")

    if FAILURES:
        print(f"\nXX v0.7.1-C2 web dashboard badges plan readiness 檢查失敗 {len(FAILURES)} 項：")
        for f in FAILURES:
            print(f"   - {f}")
        return 1
    print("\nOK v0.7.1-C2 web dashboard badges plan readiness 全數通過（純文件，未連任何系統、未含 secret）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
