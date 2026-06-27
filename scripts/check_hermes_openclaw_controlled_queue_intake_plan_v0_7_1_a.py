#!/usr/bin/env python3
"""v0.7.1-A — Controlled Queue Intake Plan 靜態 readiness（純文件檢查，不連任何系統）。

確認 v0.7.1-A 規劃文件涵蓋必要章節與 plan-only 安全聲明，且本版未越界：
  - plan-only：無真 Hermes / OpenClaw / Queue DB / Worker / Google Sheets。
  - Result Sink observation-only 邊界明確。
  - 未把 intake 接進 app/main / queue_store / worker / result_sink。
靜態檢查：不 import Google / Hermes / OpenClaw client，不讀 secret，不連線，不寫 DB。
敏感檢查一律使用 regex / 格式比對，不逐字比對完整 spreadsheet id。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOC = ROOT / "docs" / "HERMES_OPENCLAW_CONTROLLED_QUEUE_INTAKE_PLAN_V0_7_1_A.md"
APP_MAIN = ROOT / "app" / "main.py"
QUEUE_STORE = ROOT / "app" / "queue_store.py"
WORKER = ROOT / "app" / "worker.py"
RESULT_SINK = ROOT / "app" / "result_sink.py"
APP_DIR = ROOT / "app"

REQUIRED_TITLES = (
    "1. Purpose",
    "2. Current State From v0.7.0-E",
    "3. What v0.7.1-A Allows",
    "4. What v0.7.1-A Does Not Allow",
    "5. Controlled Queue Intake Model",
    "6. Mock / Real Boundary",
    "7. Task Type Intake Policy",
    "8. Risk Level Policy",
    "9. Approval Gate Requirements",
    "10. Worker Auto-run Prevention",
    "11. Kill Switch Plan",
    "12. Audit Log Plan",
    "13. Per-tool Allowlist Plan",
    "14. Result Sink Boundary",
    "15. Google Sheets Boundary",
    "16. Security / Secrets Rules",
    "17. Readiness Criteria For v0.7.1-B",
    "18. Explicit Non-goals",
    "19. Final Recommendation",
)

PLAN_ONLY_DECLARATIONS = (
    "v0.7.1-A is plan-only.",
    "No true Hermes webhook.",
    "No true OpenClaw execution.",
    "No true Queue DB write.",
    "No true Worker start.",
    "No automatic Google Sheets write.",
    "No external side effect.",
    "No automatic approval for high-risk tasks.",
    "Result Sink is observation-only, not Queue source of truth.",
)

# --- 敏感格式比對（regex），不放任何真實 secret / 完整 spreadsheet id ---
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
# 視為「intake 實作」的痕跡（plan-only 不應出現在受保護來源檔）。
RE_INTAKE_IMPL = re.compile(r"controlled_queue_intake|QUEUE_INTAKE_ENABLED|WORKER_AUTORUN_ENABLED|INTAKE_KILL_SWITCH")

FAILURES: list[str] = []


def _check(cond: bool, label: str) -> None:
    print(f"  {'ok ' if cond else 'XX '}: {label}")
    if not cond:
        FAILURES.append(label)


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.is_file() else ""


def _no_real_secret(text: str) -> bool:
    if RE_SPREADSHEET_URL.search(text):
        return False
    if RE_SPREADSHEET_ASSIGN.search(text):
        return False
    if RE_TOKEN_PREFIX.search(text):
        return False
    if RE_PRIVATE_KEY.search(text):
        return False
    return True


def main() -> int:
    print("[1] v0.7.1-A 文件存在")
    _check(DOC.is_file(), "docs/HERMES_OPENCLAW_CONTROLLED_QUEUE_INTAKE_PLAN_V0_7_1_A.md 存在")
    doc = _read(DOC)

    print("[2] 文件包含必要標題")
    for title in REQUIRED_TITLES:
        _check(title in doc, f"文件含章節「{title}」")

    print("[3] 文件包含 plan-only 安全聲明")
    for line in PLAN_ONLY_DECLARATIONS:
        _check(line in doc, f"文件含聲明「{line}」")

    print("[4] 文件包含 no true Hermes / OpenClaw / Queue DB / Worker / Google Sheets")
    _check("No true Hermes" in doc, "文件含 No true Hermes")
    _check("No true OpenClaw" in doc, "文件含 No true OpenClaw")
    _check("No true Queue DB" in doc, "文件含 No true Queue DB")
    _check("No true Worker" in doc, "文件含 No true Worker")
    _check("No automatic Google Sheets" in doc, "文件含 No automatic Google Sheets")

    print("[5] 文件包含 Result Sink observation-only 邊界")
    _check("observation-only" in doc and "not Queue source of truth" in doc,
           "文件含 Result Sink observation-only, not Queue source of truth")

    print("[6] 本次未修改 app/main.py（未接入 intake 實作）")
    main_txt = _read(APP_MAIN)
    _check(not RE_INTAKE_IMPL.search(main_txt), "app/main.py 未接入 intake 實作痕跡")
    _check("CONTROLLED_QUEUE_INTAKE_PLAN" not in main_txt, "app/main.py 未 import / 引用本規劃")

    print("[7] 本次未修改 queue_store / worker / result_sink（未接入 intake 實作）")
    _check(not RE_INTAKE_IMPL.search(_read(QUEUE_STORE)), "queue_store.py 未接入 intake 實作痕跡")
    _check(not RE_INTAKE_IMPL.search(_read(WORKER)), "worker.py 未接入 intake 實作痕跡")
    rs_low = _read(RESULT_SINK).lower()
    rs_bad = ("import google", "from google", "googleapiclient", "gspread",
              "google.oauth", "google_auth", "google.auth")
    _check(RESULT_SINK.is_file() and not any(b in rs_low for b in rs_bad),
           "result_sink.py 仍 mock-safe（未被改成真 Google Sheets 自動寫入）")
    _check(not RE_INTAKE_IMPL.search(_read(RESULT_SINK)), "result_sink.py 未接入 intake 實作痕跡")

    print("[8] 沒有新增 intake 實作模組（plan-only：只新增 docs + readiness）")
    impl_modules = sorted(
        p.name for p in APP_DIR.glob("*.py")
        if "controlled_queue_intake" in p.name or "queue_intake" in p.name
    )
    _check(not impl_modules, f"app/ 未新增 intake 實作模組（找到：{impl_modules or '無'}）")
    # 文件為純規劃：不應包含 web route / 實作 webhook 痕跡。
    _check("@app." not in doc and "@router." not in doc and "FastAPI(" not in doc,
           "文件未包含 web route / webhook 實作痕跡（@app. / @router. / FastAPI(）")

    print("[9] GOOGLE_SHEETS_ENABLED 維持 false（文件未出現 =true）")
    _check("GOOGLE_SHEETS_ENABLED=false" in doc, "文件含 GOOGLE_SHEETS_ENABLED=false")
    _check("GOOGLE_SHEETS_ENABLED=true" not in doc, "文件未出現 GOOGLE_SHEETS_ENABLED=true")

    print("[10] 敏感檢查（格式比對）：文件不含完整 spreadsheet id / url / token / secret / private key")
    _check(_no_real_secret(doc),
           "文件不含完整 spreadsheet id / Google Sheets URL / token / private key（格式比對）")
    for key in SECRET_KEY_NAMES:
        _check(key not in doc, f"文件不含 secret 變數名 {key}")

    if FAILURES:
        print(f"\nXX v0.7.1-A controlled queue intake plan readiness 檢查失敗 {len(FAILURES)} 項：")
        for f in FAILURES:
            print(f"   - {f}")
        return 1
    print("\nOK v0.7.1-A controlled queue intake plan readiness 全數通過（純文件，未連任何系統、未含 secret）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
