#!/usr/bin/env python3
"""v0.7.1-C — Dashboard Intake Status View Model 靜態 readiness（純檢查，不連任何系統）。

確認 view-model / CLI / doc / test 齊備且未越界：
  - view-model 為純函式：不 import app.main / app.worker、不呼叫 enqueue / claim_next /
    approve / reject / run_openclaw_cli / google client。
  - CLI 只讀（無寫入/狀態轉換呼叫）。
  - 未改 app/main.py / templates/* / static/*、未新增 route / webhook。
靜態檢查：不連外、不寫 DB、不讀 secrets。敏感檢查一律 regex / 格式比對。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

VIEW = ROOT / "app" / "dashboard_intake_view_v0_7.py"
DOC = ROOT / "docs" / "HERMES_OPENCLAW_DASHBOARD_INTAKE_STATUS_VIEW_MODEL_V0_7_1_C.md"
CLI = ROOT / "scripts" / "show_intake_status_v0_7_1_c.py"
TEST_FILE = ROOT / "scripts" / "test_dashboard_intake_view_v0_7_1_c.py"
READINESS = ROOT / "scripts" / "check_hermes_openclaw_dashboard_intake_status_view_model_v0_7_1_c_readiness.py"

APP_MAIN = ROOT / "app" / "main.py"
TEMPLATES_DIR = ROOT / "templates"
STATIC_DIR = ROOT / "static"

REQUIRED_TITLES = (
    "1. Purpose",
    "2. Relationship To v0.7.1-A And v0.7.1-B",
    "3. Why This Version Does Not Modify Web Dashboard",
    "4. What v0.7.1-C Allows",
    "5. What v0.7.1-C Does Not Allow",
    "6. View-model Fields",
    "7. Source Mode Derivation",
    "8. Intake Mode Derivation",
    "9. Executable-by-worker Derivation",
    "10. Approval / Risk Display Derivation",
    "11. Local-only Intake DB Visibility",
    "12. Read-only CLI Report",
    "13. Mock / Real Boundary",
    "14. Result Sink Boundary",
    "15. Google Sheets Boundary",
    "16. Security / Secrets Rules",
    "17. Test Coverage",
    "18. Readiness Checks",
    "19. Explicit Non-goals",
    "20. Final Recommendation",
)

REQUIRED_DECLARATIONS = (
    "No app/main.py modification.",
    "No template modification.",
    "No route addition.",
    "No true Hermes webhook.",
    "No true OpenClaw execution.",
    "No true Worker start.",
    "No Queue status mutation.",
    "No production Queue DB write.",
    "No automatic Google Sheets write.",
    "No external side effect.",
    "Result Sink is observation-only, not Queue source of truth.",
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

# 寫入 / 狀態轉換 / 執行的「呼叫痕跡」（用 '(' 比對，避免 docstring 字樣誤判）。
MUTATING_CALL_PATTERNS = (
    "enqueue(", ".claim_next(", ".approve(", ".reject(",
    ".mark_completed(", ".mark_failed(", ".requeue(", ".cancel", "run_openclaw_cli(",
)

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
    print("[1] doc / view module / CLI / test / readiness 檔存在")
    _check(VIEW.is_file(), "app/dashboard_intake_view_v0_7.py 存在")
    _check(DOC.is_file(), "docs/HERMES_OPENCLAW_DASHBOARD_INTAKE_STATUS_VIEW_MODEL_V0_7_1_C.md 存在")
    _check(CLI.is_file(), "scripts/show_intake_status_v0_7_1_c.py 存在")
    _check(TEST_FILE.is_file(), "scripts/test_dashboard_intake_view_v0_7_1_c.py 存在")
    _check(READINESS.is_file(), "readiness script 自身存在")

    view = _read(VIEW)
    cli = _read(CLI)
    doc = _read(DOC)

    print("[2] doc 含必要標題與安全聲明")
    for title in REQUIRED_TITLES:
        _check(title in doc, f"doc 含章節「{title}」")
    for line in REQUIRED_DECLARATIONS:
        _check(line in doc, f"doc 含聲明「{line}」")

    print("[3] view module 不 import app.main / app.worker（行錨定）")
    main_import_re = re.compile(r"^\s*(?:import|from)\s+app\.main\b", re.MULTILINE)
    worker_import_re = re.compile(r"^\s*(?:import|from)\s+\S*\bapp\.worker\b", re.MULTILINE)
    _check(not main_import_re.search(view), "view module 未 import app.main")
    _check(not worker_import_re.search(view), "view module 未 import app.worker")

    print("[4] view module 不呼叫 enqueue / claim_next / approve / reject / run_openclaw_cli / google")
    for pat in ("enqueue(", ".claim_next(", ".approve(", ".reject(", "run_openclaw_cli("):
        _check(pat not in view, f"view module 無呼叫痕跡「{pat}」")
    google_import_re = re.compile(
        r"^\s*(?:import|from)\s+\S*(?:google|googleapiclient|gspread|oauthlib)",
        re.MULTILINE | re.IGNORECASE,
    )
    _check(not google_import_re.search(view), "view module 未 import google / oauth client")

    print("[5] CLI 只讀（無寫入 / 狀態轉換 / 執行呼叫痕跡）")
    for pat in MUTATING_CALL_PATTERNS:
        _check(pat not in cli, f"CLI 無寫入/轉換呼叫痕跡「{pat}」")
    _check(not main_import_re.search(cli), "CLI 未 import app.main")
    _check(not worker_import_re.search(cli), "CLI 未 import app.worker")

    print("[6] 未改 app/main.py（未接入 view-model）")
    _check("dashboard_intake_view_v0_7" not in _read(APP_MAIN), "app/main.py 未 import dashboard_intake_view_v0_7")

    print("[7] 未改 templates/*（未加入 intake 顯示欄位）")
    tmpl_tokens = ("dashboard_intake_view", "intake_mode", "executable_by_worker", "source_mode")
    if TEMPLATES_DIR.is_dir():
        for tmpl in sorted(TEMPLATES_DIR.glob("*.html")):
            txt = _read(tmpl)
            _check(not any(tok in txt for tok in tmpl_tokens), f"templates/{tmpl.name} 未加入 intake 顯示欄位")
    else:
        _check(True, "templates/ 目錄不存在（無需檢查）")

    print("[8] 未改 static/*（未加入 intake 相關樣式）")
    if STATIC_DIR.is_dir():
        for st in sorted(STATIC_DIR.glob("*")):
            if st.is_file():
                _check("dashboard_intake_view" not in _read(st) and "intake_mode" not in _read(st),
                       f"static/{st.name} 未加入 intake 相關引用")
    else:
        _check(True, "static/ 目錄不存在（無需檢查）")

    print("[9] 無新增 route / webhook / POST handler（view + CLI）")
    for bad in ("@app.", "@router.", "FastAPI(", "APIRouter", "add_api_route"):
        _check(bad not in view and bad not in cli, f"view / CLI 無「{bad}」")

    print("[10] GOOGLE_SHEETS_ENABLED 無 true")
    _check("GOOGLE_SHEETS_ENABLED=true" not in view
           and "GOOGLE_SHEETS_ENABLED=true" not in cli
           and "GOOGLE_SHEETS_ENABLED=true" not in doc,
           "view / CLI / doc 未出現 GOOGLE_SHEETS_ENABLED=true")

    print("[11] 敏感檢查（格式比對）：view / CLI / doc / test 不含真實 secret")
    for name, text in (("view", view), ("CLI", cli), ("doc", doc), ("test", _read(TEST_FILE))):
        _check(_no_real_secret(text),
               f"{name} 不含完整 spreadsheet id / url / token / private key（格式比對）")
        for key in SECRET_KEY_NAMES:
            _check(key not in text, f"{name} 不含 secret 變數名 {key}")

    if FAILURES:
        print(f"\nXX v0.7.1-C dashboard intake view readiness 檢查失敗 {len(FAILURES)} 項：")
        for f in FAILURES:
            print(f"   - {f}")
        return 1
    print("\nOK v0.7.1-C dashboard intake view readiness 全數通過（純檢查，未連任何系統、未含 secret）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
