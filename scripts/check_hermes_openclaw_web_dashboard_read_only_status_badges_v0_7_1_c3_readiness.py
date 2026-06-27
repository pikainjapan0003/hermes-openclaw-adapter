#!/usr/bin/env python3
"""v0.7.1-C3 — Web Dashboard read-only status badges 靜態 readiness（純檢查，不連任何系統）。

確認唯讀 badge 顯示的接入是安全的：
  - app/main.py 只 import 並在 dashboard 觀測 helper 使用 derive_intake_status_view（唯讀）。
  - 未為此功能新增 route / webhook / POST handler / 新表單。
  - templates 只新增唯讀 badge；static 只新增 badge 樣式（無 JS / 無 CDN）。
  - app/worker.py / queue_store.py / result_sink.py 未被接入新顯示流程。
靜態檢查：不連外、不寫 DB、不讀 secrets。敏感檢查一律 regex / 格式比對。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOC = ROOT / "docs" / "HERMES_OPENCLAW_WEB_DASHBOARD_READ_ONLY_STATUS_BADGES_V0_7_1_C3.md"
TEST_FILE = ROOT / "scripts" / "test_web_dashboard_status_badges_v0_7_1_c3.py"
READINESS = ROOT / "scripts" / "check_hermes_openclaw_web_dashboard_read_only_status_badges_v0_7_1_c3_readiness.py"

APP_MAIN = ROOT / "app" / "main.py"
VIEW = ROOT / "app" / "dashboard_intake_view_v0_7.py"
WORKER = ROOT / "app" / "worker.py"
QUEUE_STORE = ROOT / "app" / "queue_store.py"
RESULT_SINK = ROOT / "app" / "result_sink.py"
TASKS_TMPL = ROOT / "templates" / "tasks.html"
DETAIL_TMPL = ROOT / "templates" / "task_detail.html"
CSS = ROOT / "static" / "dashboard.css"

REQUIRED_TITLES = (
    "1. Purpose", "2. Relationship To v0.7.1-C And v0.7.1-C2", "3. What Was Implemented",
    "4. Files Changed", "5. Read-only Badge Fields", "6. View-model Reuse",
    "7. No Queue Status Mutation Guarantee", "8. No Worker Trigger Guarantee",
    "9. No Result Sink Write Guarantee", "10. No Google Sheets Write Guarantee",
    "11. Mock / Local-only / Real Boundary", "12. Local-only Safety Behavior",
    "13. Test Coverage", "14. Readiness Checks", "15. Explicit Non-goals",
    "16. Final Recommendation",
)
REQUIRED_DECLARATIONS = (
    "No new route.", "No new POST handler.", "No Queue status mutation.",
    "No Worker start.", "No OpenClaw execution.", "No Hermes webhook.",
    "No Google Sheets write.", "No Result Sink write.", "No production Queue DB write.",
    "Badges are read-only display only.",
)

RE_SPREADSHEET_URL = re.compile(r"spreadsheets/d/[A-Za-z0-9_-]{20,}")
RE_SPREADSHEET_ASSIGN = re.compile(r"SPREADSHEET_ID\s*[:=]\s*[\"'][A-Za-z0-9_-]{20,}[\"']")
RE_TOKEN_PREFIX = re.compile(r"(ya29\.[A-Za-z0-9_-]{10,}|1//[A-Za-z0-9_-]{10,}|" + "goc" + r"spx-[A-Za-z0-9_-]{10,})")
RE_PRIVATE_KEY = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")
SECRET_KEY_NAMES = (
    "client_secret", "refresh_token", "access_token",
    "GOOGLE_OAUTH_REFRESH_TOKEN", "GOOGLE_OAUTH_CLIENT_SECRET", "GOOGLE_SERVICE_ACCOUNT_JSON",
)

FAILURES: list[str] = []


def _check(cond: bool, label: str) -> None:
    print(f"  {'ok ' if cond else 'XX '}: {label}")
    if not cond:
        FAILURES.append(label)


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.is_file() else ""


def _no_real_secret(text: str) -> bool:
    return not (RE_SPREADSHEET_URL.search(text) or RE_SPREADSHEET_ASSIGN.search(text)
                or RE_TOKEN_PREFIX.search(text) or RE_PRIVATE_KEY.search(text))


def main() -> int:
    main_txt = _read(APP_MAIN)
    tasks_txt = _read(TASKS_TMPL)
    detail_txt = _read(DETAIL_TMPL)
    css_txt = _read(CSS)
    doc = _read(DOC)

    print("[1] doc / test / readiness 存在")
    _check(DOC.is_file(), "v0.7.1-C3 doc 存在")
    _check(TEST_FILE.is_file(), "test 存在")
    _check(READINESS.is_file(), "readiness script 自身存在")

    print("[2] doc 含必要標題與安全聲明")
    for title in REQUIRED_TITLES:
        _check(title in doc, f"doc 含章節「{title}」")
    for line in REQUIRED_DECLARATIONS:
        _check(line in doc, f"doc 含聲明「{line}」")

    print("[3] app/main.py import 並使用 derive_intake_status_view（唯讀）")
    _check(bool(re.search(r"^\s*from app\.dashboard_intake_view_v0_7 import derive_intake_status_view",
                          main_txt, re.MULTILINE)),
           "app/main.py import derive_intake_status_view")
    usages = main_txt.count("derive_intake_status_view(")
    _check(usages == 2, f"derive_intake_status_view 僅在 2 個 helper 使用（實際 {usages}）")

    print("[4] 未為此功能新增 route / webhook / POST handler")
    # 不應出現「intake / badge」相關的新路由。
    route_re = re.compile(r"@app\.(?:get|post|put|delete|patch)\([^)]*(?:intake|badge)", re.IGNORECASE)
    _check(not route_re.search(main_txt), "app/main.py 未新增 intake/badge 相關 route")
    # 不為此功能新增 webhook route（既有 Hermes callback 註解 / 設定不算；只擋新的 webhook 路由）。
    webhook_route_re = re.compile(r"@app\.(?:get|post)\([^)]*webhook", re.IGNORECASE)
    _check(not webhook_route_re.search(main_txt), "app/main.py 未新增 webhook route")
    # view-model 不應被放進任何 POST handler（粗略：import 行附近與 helper 才用）。
    _check("derive_intake_status_view" not in detail_txt and "derive_intake_status_view" not in tasks_txt,
           "templates 未直接呼叫 view-model 函式（只用 context 變數）")

    print("[5] templates 只新增唯讀 badge（未新增 intake 相關表單 / POST）")
    _check("intake_status" in tasks_txt, "tasks.html 顯示 intake_status badges")
    _check("intake_status" in detail_txt, "task_detail.html 顯示 intake_status")
    form_intake_re = re.compile(r"<form[^>]*action=\"[^\"]*intake", re.IGNORECASE)
    _check(not form_intake_re.search(tasks_txt) and not form_intake_re.search(detail_txt),
           "templates 未新增 action 指向 intake 的表單")
    # tasks.html 為列表頁，不應有任何 POST 表單。
    _check("method=\"post\"" not in tasks_txt.lower().replace(" ", ""),
           "tasks.html 未引入 POST 表單")

    print("[6] static 只新增 badge 樣式（無 JS / 無外部 CDN）")
    _check("badge-local-only" in css_txt and "badge-executable-false" in css_txt
           and "badge-unknown" in css_txt, "dashboard.css 含 badge 樣式")
    _check("<script" not in css_txt and "function(" not in css_txt, "dashboard.css 未引入 JS")
    _check("http://" not in css_txt and "https://" not in css_txt, "dashboard.css 未外連 CDN")

    print("[7] app/worker.py / queue_store.py / result_sink.py 未被接入新顯示流程")
    for path, name in ((WORKER, "worker.py"), (QUEUE_STORE, "queue_store.py"), (RESULT_SINK, "result_sink.py")):
        txt = _read(path)
        _check("dashboard_intake_view_v0_7" not in txt and "derive_intake_status_view" not in txt,
               f"app/{name} 未 import / 引用 view-model")
    rs_low = _read(RESULT_SINK).lower()
    rs_bad = ("import google", "from google", "googleapiclient", "gspread",
              "google.oauth", "google_auth", "google.auth")
    _check(RESULT_SINK.is_file() and not any(b in rs_low for b in rs_bad),
           "result_sink.py 仍 mock-safe（不 import google client）")

    print("[8] view-model 仍為純函式（不 import worker / google）")
    view = _read(VIEW)
    view_bad = re.compile(r"^\s*(?:import|from)\s+\S*(?:app\.worker|app\.main|google|googleapiclient|gspread)",
                          re.MULTILINE | re.IGNORECASE)
    _check(not view_bad.search(view), "dashboard_intake_view_v0_7.py 未 import worker / main / google")

    print("[9] GOOGLE_SHEETS_ENABLED 無 true（changed files）")
    for name, txt in (("main.py", main_txt), ("doc", doc), ("css", css_txt),
                      ("tasks.html", tasks_txt), ("task_detail.html", detail_txt)):
        _check("GOOGLE_SHEETS_ENABLED=true" not in txt, f"{name} 未出現 GOOGLE_SHEETS_ENABLED=true")

    print("[10] 敏感檢查（格式比對）：doc / test / 變更檔不含真實 secret")
    for name, txt in (("doc", doc), ("test", _read(TEST_FILE)), ("tasks.html", tasks_txt),
                      ("task_detail.html", detail_txt), ("css", css_txt)):
        _check(_no_real_secret(txt), f"{name} 不含完整 spreadsheet id / url / token / private key（格式比對）")
        for key in SECRET_KEY_NAMES:
            _check(key not in txt, f"{name} 不含 secret 變數名 {key}")

    if FAILURES:
        print(f"\nXX v0.7.1-C3 web dashboard badges readiness 檢查失敗 {len(FAILURES)} 項：")
        for f in FAILURES:
            print(f"   - {f}")
        return 1
    print("\nOK v0.7.1-C3 web dashboard badges readiness 全數通過（純檢查，未連任何系統、未含 secret）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
