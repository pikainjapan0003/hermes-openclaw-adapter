#!/usr/bin/env python3
"""v0.7.1-D — Kill Switch / Audit Log / Per-tool Allowlist Plan 靜態 readiness（純文件檢查）。

確認 v0.7.1-D 規劃文件涵蓋必要章節、安全聲明與 gate 優先序，且本版 plan-only 未越界：
  - 未改 app/main.py / worker.py / queue_store.py / result_sink.py。
  - 未新增 security gate 實作模組、未新增 route / POST handler。
靜態檢查：不連外、不寫 DB、不讀 secrets。敏感檢查一律 regex / 格式比對。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOC = ROOT / "docs" / "HERMES_OPENCLAW_KILL_SWITCH_AUDIT_ALLOWLIST_PLAN_V0_7_1_D.md"
READINESS = ROOT / "scripts" / "check_hermes_openclaw_kill_switch_audit_allowlist_plan_v0_7_1_d.py"

APP_MAIN = ROOT / "app" / "main.py"
WORKER = ROOT / "app" / "worker.py"
QUEUE_STORE = ROOT / "app" / "queue_store.py"
RESULT_SINK = ROOT / "app" / "result_sink.py"
APP_DIR = ROOT / "app"

REQUIRED_TITLES = (
    "1. Purpose",
    "2. Relationship To v0.7.1-A/B/C/C2/C3",
    "3. Why This Version Is Plan-only",
    "4. Current Safety Flags And Gates",
    "5. Current Dashboard / API Actions",
    "6. Current TaskEnvelope Tool Fields",
    "7. Kill Switch Model",
    "8. Kill Switch Control Points",
    "9. Audit Log Model",
    "10. Audit Events",
    "11. Audit Log Boundary",
    "12. Per-tool Allowlist Model",
    "13. Denylist / Allowlist Priority",
    "14. Adapter / Intake / Approval / Worker Layering",
    "15. Queue Source-of-truth Boundary",
    "16. Result Sink Boundary",
    "17. Google Sheets Boundary",
    "18. Security / Secrets Rules",
    "19. Future v0.7.1-D2 Local-only Implementation Criteria",
    "20. Future Worker / OpenClaw Integration Criteria",
    "21. Explicit Non-goals",
    "22. Final Recommendation",
)

REQUIRED_DECLARATIONS = (
    "v0.7.1-D is plan-only.",
    "No app/main.py modification.",
    "No worker.py modification.",
    "No queue_store.py modification.",
    "No result_sink.py modification.",
    "No DB schema change.",
    "No new route.",
    "No new POST handler.",
    "No Worker start.",
    "No OpenClaw execution.",
    "No Hermes webhook.",
    "No Google Sheets write.",
    "No Result Sink write.",
    "No Queue status mutation.",
    "Audit log is observation-only, not Queue source of truth.",
    "Queue SQLite remains the source of truth for task state.",
)

REQUIRED_SECRET_NOLOG = (
    "Do not log refresh token.",
    "Do not log client secret.",
    "Do not log access token.",
    "Do not log private key.",
    "Do not log full spreadsheet ID.",
    "Do not log full Google Sheets URL.",
    "Do not log raw credentials.",
)

GATE_PRIORITY = (
    "1. Global kill switch",
    "2. Layer-specific kill switch",
    "3. Denylist",
    "4. Allowlist",
    "5. Risk / approval gate",
    "6. Queue status gate",
    "7. Worker execution gate",
)

# 未來實作才會出現的 security gate 痕跡；plan-only 不應出現在既有程式檔。
GATE_IMPL_TOKENS = ("evaluate_tool_allowlist", "kill_switch_active", "audit_record",
                    "GLOBAL_KILL_SWITCH", "security_gates_v0_7")

# --- 敏感格式比對（regex） ---
RE_SPREADSHEET_URL = re.compile(r"spreadsheets/d/[A-Za-z0-9_-]{20,}")
RE_SPREADSHEET_ASSIGN = re.compile(r"SPREADSHEET_ID\s*[:=]\s*[\"'][A-Za-z0-9_-]{20,}[\"']")
RE_TOKEN_PREFIX = re.compile(r"(ya29\.[A-Za-z0-9_-]{10,}|1//[A-Za-z0-9_-]{10,}|" + "goc" + r"spx-[A-Za-z0-9_-]{10,})")
RE_PRIVATE_KEY = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")
SECRET_KEY_NAMES = (
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
    print("[1] v0.7.1-D doc / readiness script 存在")
    _check(DOC.is_file(), "v0.7.1-D doc 存在")
    _check(READINESS.is_file(), "readiness script 自身存在")
    doc = _read(DOC)

    print("[2] doc 含必要標題")
    for title in REQUIRED_TITLES:
        _check(title in doc, f"doc 含章節「{title}」")

    print("[3] doc 含 plan-only 安全聲明")
    for line in REQUIRED_DECLARATIONS:
        _check(line in doc, f"doc 含聲明「{line}」")

    print("[4] doc 含 audit 不記 secret 規則")
    for line in REQUIRED_SECRET_NOLOG:
        _check(line in doc, f"doc 含「{line}」")

    print("[5] doc 含 gate 優先順序（kill switch / denylist > allowlist）")
    for line in GATE_PRIORITY:
        _check(line in doc, f"doc 含 gate 優先序「{line}」")
    _check("denylist 優先於 allowlist" in doc, "doc 明確 denylist 優先於 allowlist")
    _check("kill switch 優先於所有 allowlist" in doc, "doc 明確 kill switch 優先於所有 allowlist")

    print("[6] app/main.py / worker.py / queue_store.py / result_sink.py 未被接入 gate 實作")
    for path, name in ((APP_MAIN, "app/main.py"), (WORKER, "app/worker.py"),
                       (QUEUE_STORE, "app/queue_store.py"), (RESULT_SINK, "app/result_sink.py")):
        txt = _read(path)
        hits = [tok for tok in GATE_IMPL_TOKENS if tok in txt]
        _check(not hits, f"{name} 未含 gate 實作痕跡（找到：{hits or '無'}）")

    print("[7] 無新增 security gate 實作模組")
    impl_modules = sorted(
        p.name for p in APP_DIR.glob("*.py")
        if "security_gate" in p.name or "kill_switch" in p.name or "audit_log" in p.name
    )
    _check(not impl_modules, f"app/ 未新增 security gate 模組（找到：{impl_modules or '無'}）")

    print("[8] doc 無新增 route / webhook / POST handler 實作痕跡")
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
        print(f"\nXX v0.7.1-D kill switch / audit / allowlist plan readiness 檢查失敗 {len(FAILURES)} 項：")
        for f in FAILURES:
            print(f"   - {f}")
        return 1
    print("\nOK v0.7.1-D kill switch / audit / allowlist plan readiness 全數通過（純文件，未連任何系統、未含 secret）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
