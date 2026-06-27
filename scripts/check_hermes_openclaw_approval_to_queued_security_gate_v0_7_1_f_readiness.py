#!/usr/bin/env python3
"""v0.7.1-F — Approval-to-Queued Security Gate pure helper 靜態 readiness（純檢查，不連任何系統）。

確認 approval gate helper 為純函式、fail-closed，且未接 route / 未改 production 狀態機：
  - helper 不 import main/queue_store/worker/result_sink、不呼叫 approve/reject/enqueue/claim_next/openclaw/google。
  - helper 強制 local_only / mock / executable_by_worker=false reject，使用 evaluate_security_gates。
  - main/queue_store/worker/result_sink/security_gates/queue_intake_bridge 未被改動接入。
靜態檢查：不連外、不寫 DB、不讀 secrets。敏感檢查一律 regex / 格式比對。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MODULE = ROOT / "app" / "approval_security_gate_v0_7.py"
DOC = ROOT / "docs" / "HERMES_OPENCLAW_APPROVAL_TO_QUEUED_SECURITY_GATE_V0_7_1_F.md"
TEST_FILE = ROOT / "scripts" / "test_approval_security_gate_v0_7_1_f.py"
READINESS = ROOT / "scripts" / "check_hermes_openclaw_approval_to_queued_security_gate_v0_7_1_f_readiness.py"

APP_MAIN = ROOT / "app" / "main.py"
QUEUE_STORE = ROOT / "app" / "queue_store.py"
WORKER = ROOT / "app" / "worker.py"
RESULT_SINK = ROOT / "app" / "result_sink.py"
SECURITY_GATES = ROOT / "app" / "security_gates_v0_7.py"
INTAKE_BRIDGE = ROOT / "app" / "queue_intake_bridge_v0_7.py"

REQUIRED_TITLES = (
    "1. Purpose", "2. Relationship To v0.7.1-E", "3. Why This Version Is Pure Helper Only",
    "4. What Was Implemented", "5. What Was Not Implemented",
    "6. APPROVAL_SECURITY_GATES_ENABLED Behavior", "7. Approval-to-Queued Risk",
    "8. Input Task Row Model", "9. Payload / Metadata Extraction", "10. Security Gate Priority",
    "11. Local-only / Mock / Executable Boundary", "12. Tool Allowlist / Denylist Rules",
    "13. Kill Switch Rules", "14. Reject Semantics", "15. Audit Event Boundary",
    "16. Queue Source-of-truth Boundary", "17. Worker / OpenClaw Boundary",
    "18. Google Sheets Boundary", "19. Test Coverage", "20. Readiness Checks",
    "21. Future Route Wiring Criteria", "22. Explicit Non-goals", "23. Final Recommendation",
)
REQUIRED_DECLARATIONS = (
    "No app/main.py modification.", "No queue_store.py modification.",
    "No worker.py modification.", "No result_sink.py modification.",
    "No security_gates_v0_7.py modification.", "No queue_intake_bridge_v0_7.py modification.",
    "No DB write.", "No Queue status mutation.", "No approve route wiring.",
    "No Dashboard approve wiring.", "No new route.", "No new POST handler.",
    "No Worker start.", "No OpenClaw execution.", "No Hermes webhook.", "No Google Sheets write.",
    "Gate rejection does not automatically transition task to rejected.",
    "Gate rejection blocks approve-to-queued and keeps task in current review state.",
    "Audit event is observation-only and not persisted in this version.",
    "Queue SQLite remains the source of truth for task state.",
)

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
    module = _read(MODULE)
    doc = _read(DOC)

    print("[1] doc / module / test / readiness 存在")
    _check(MODULE.is_file(), "app/approval_security_gate_v0_7.py 存在")
    _check(DOC.is_file(), "v0.7.1-F doc 存在")
    _check(TEST_FILE.is_file(), "test 存在")
    _check(READINESS.is_file(), "readiness script 自身存在")

    print("[2] doc 含必要章節與安全聲明")
    for title in REQUIRED_TITLES:
        _check(title in doc, f"doc 含章節「{title}」")
    for line in REQUIRED_DECLARATIONS:
        _check(line in doc, f"doc 含聲明「{line}」")

    print("[3] module 公開 API / 行為")
    _check("def evaluate_approval_to_queued" in module, "module 含 evaluate_approval_to_queued")
    _check("APPROVAL_SECURITY_GATES_ENABLED" in module, "module 含 APPROVAL_SECURITY_GATES_ENABLED")
    _check("approval_security_gates_disabled" in module, "module 有 disabled → allow 行為")
    _check("evaluate_security_gates(" in module, "module 使用 evaluate_security_gates")

    print("[4] module 不 import main / queue_store / worker / result_sink（行錨定）")
    for mod in ("app\\.main", "app\\.queue_store", "app\\.worker", "app\\.result_sink"):
        imp_re = re.compile(rf"^\s*(?:import|from)\s+\S*{mod}\b", re.MULTILINE)
        _check(not imp_re.search(module), f"module 未 import {mod.replace(chr(92), '')}")

    print("[5] module 不呼叫 approve / reject / enqueue / claim_next / openclaw / google、不寫 DB")
    for pat in (".approve(", ".reject(", "enqueue(", ".claim_next(", "run_openclaw_cli("):
        _check(pat not in module, f"module 無呼叫痕跡「{pat}」")
    google_re = re.compile(r"^\s*(?:import|from)\s+\S*(?:google|googleapiclient|gspread|oauthlib)",
                           re.MULTILINE | re.IGNORECASE)
    _check(not google_re.search(module), "module 未 import google / oauth client")
    for pat in ("sqlite3", ".commit(", ".execute("):
        _check(pat not in module, f"module 不含 DB 寫入痕跡「{pat}」")

    print("[6] module 強制 local_only / mock / executable_by_worker reject")
    _check("local_only_not_approvable" in module, "module 強制 local_only reject")
    _check("mock_not_approvable" in module, "module 強制 mock reject")
    _check("executable_by_worker_not_true" in module, "module 強制 executable_by_worker=false/缺失 reject")

    print("[7] 無新增 route / webhook / POST handler（module + doc）")
    for bad in ("@app.", "@router.", "FastAPI(", "APIRouter", "add_api_route"):
        _check(bad not in module and bad not in doc, f"module / doc 無「{bad}」")

    print("[8] main/queue_store/worker/result_sink/security_gates/queue_intake_bridge 未被接入")
    for path, name in ((APP_MAIN, "main.py"), (QUEUE_STORE, "queue_store.py"),
                       (WORKER, "worker.py"), (RESULT_SINK, "result_sink.py"),
                       (SECURITY_GATES, "security_gates_v0_7.py"), (INTAKE_BRIDGE, "queue_intake_bridge_v0_7.py")):
        _check("approval_security_gate_v0_7" not in _read(path),
               f"app/{name} 未 import approval_security_gate_v0_7")
    rs_low = _read(RESULT_SINK).lower()
    rs_bad = ("import google", "from google", "googleapiclient", "gspread",
              "google.oauth", "google_auth", "google.auth")
    _check(RESULT_SINK.is_file() and not any(b in rs_low for b in rs_bad),
           "result_sink.py 仍 mock-safe（不 import google client）")

    print("[9] GOOGLE_SHEETS_ENABLED 無 true")
    _check("GOOGLE_SHEETS_ENABLED=true" not in module and "GOOGLE_SHEETS_ENABLED=true" not in doc,
           "module / doc 未出現 GOOGLE_SHEETS_ENABLED=true")

    print("[10] 敏感檢查（格式比對）：module / doc / test 不含真實 secret")
    for name, text in (("module", module), ("doc", doc), ("test", _read(TEST_FILE))):
        _check(_no_real_secret(text),
               f"{name} 不含完整 spreadsheet id / url / token / private key（格式比對）")
        for key in SECRET_KEY_NAMES:
            _check(key not in text, f"{name} 不含 secret 變數名 {key}")

    if FAILURES:
        print(f"\nXX v0.7.1-F approval security gate readiness 檢查失敗 {len(FAILURES)} 項：")
        for f in FAILURES:
            print(f"   - {f}")
        return 1
    print("\nOK v0.7.1-F approval security gate readiness 全數通過（純檢查，未連任何系統、未含 secret）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
