#!/usr/bin/env python3
"""v0.7.1-E — Local-only Intake Security Gates wiring 靜態 readiness（純檢查，不連任何系統）。

確認 tool-level security gate 已安全接進 local-only intake bridge：
  - bridge import evaluate_security_gates、含 INTAKE_SECURITY_GATES_ENABLED、requested_tools 來源。
  - reject 不寫 DB；成功仍 waiting_review、executable_by_worker=false。
  - bridge 不接 main/worker、不呼叫 OpenClaw/google、不新增 route。
  - main/worker/queue_store/result_sink/security_gates 未被改動接入。
靜態檢查：不連外、不寫 DB、不讀 secrets。敏感檢查一律 regex / 格式比對。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

BRIDGE = ROOT / "app" / "queue_intake_bridge_v0_7.py"
DOC = ROOT / "docs" / "HERMES_OPENCLAW_LOCAL_ONLY_INTAKE_SECURITY_GATES_V0_7_1_E.md"
TEST_FILE = ROOT / "scripts" / "test_intake_security_gates_v0_7_1_e.py"
READINESS = ROOT / "scripts" / "check_hermes_openclaw_local_only_intake_security_gates_v0_7_1_e_readiness.py"

APP_MAIN = ROOT / "app" / "main.py"
WORKER = ROOT / "app" / "worker.py"
QUEUE_STORE = ROOT / "app" / "queue_store.py"
RESULT_SINK = ROOT / "app" / "result_sink.py"
SECURITY_GATES = ROOT / "app" / "security_gates_v0_7.py"

REQUIRED_TITLES = (
    "1. Purpose", "2. Relationship To v0.7.1-B / D / D2", "3. What Was Implemented",
    "4. What Was Not Implemented", "5. Requested Tools Source",
    "6. Missing Requested Tools Behavior", "7. INTAKE_SECURITY_GATES_ENABLED Behavior",
    "8. GLOBAL_KILL_SWITCH Behavior", "9. Security Gate Priority", "10. Local-only Intake Flow",
    "11. Reject Semantics", "12. Audit Event Boundary", "13. Queue Source-of-truth Boundary",
    "14. Worker / OpenClaw Boundary", "15. Google Sheets Boundary", "16. Security / Secrets Rules",
    "17. Test Coverage", "18. Readiness Checks", "19. Future Integration Criteria",
    "20. Explicit Non-goals", "21. Final Recommendation",
)
REQUIRED_DECLARATIONS = (
    "No app/main.py modification.", "No worker.py modification.",
    "No queue_store.py modification.", "No result_sink.py modification.",
    "No security_gates_v0_7.py modification.", "No DB schema change.",
    "No new route.", "No new POST handler.", "No Worker start.", "No OpenClaw execution.",
    "No Hermes webhook.", "No Google Sheets write.", "Rejects do not write Queue DB.",
    "Successful writes remain waiting_review.", "Tasks must not become queued.",
    "executable_by_worker remains false.",
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
    bridge = _read(BRIDGE)
    doc = _read(DOC)

    print("[1] doc / test / readiness 存在")
    _check(BRIDGE.is_file(), "app/queue_intake_bridge_v0_7.py 存在")
    _check(DOC.is_file(), "v0.7.1-E doc 存在")
    _check(TEST_FILE.is_file(), "test 存在")
    _check(READINESS.is_file(), "readiness script 自身存在")

    print("[2] doc 含必要章節與安全聲明")
    for title in REQUIRED_TITLES:
        _check(title in doc, f"doc 含章節「{title}」")
    for line in REQUIRED_DECLARATIONS:
        _check(line in doc, f"doc 含聲明「{line}」")

    print("[3] bridge 已接入 security gate")
    _check(bool(re.search(r"^\s*from app\.security_gates_v0_7 import .*evaluate_security_gates",
                          bridge, re.MULTILINE)), "bridge import evaluate_security_gates")
    _check("evaluate_security_gates(" in bridge, "bridge 呼叫 evaluate_security_gates()")
    _check("INTAKE_SECURITY_GATES_ENABLED" in bridge, "bridge 含 INTAKE_SECURITY_GATES_ENABLED")
    _check("GLOBAL_KILL_SWITCH" in bridge, "bridge 含 GLOBAL_KILL_SWITCH")
    _check('"requested_tools"' in bridge or "requested_tools" in bridge,
           "bridge 使用 metadata.requested_tools 來源")
    _check('metadata.get("requested_tools")' in bridge, "bridge 從 metadata.requested_tools 取值")

    print("[4] reject 不寫 DB；成功仍 waiting_review / executable_by_worker=false")
    _check("security_gate_rejected" in bridge, "bridge 有 security_gate_rejected reject path")
    _check("initial_status=WAITING_REVIEW" in bridge, "bridge 成功 path initial_status=WAITING_REVIEW")
    _check('"executable_by_worker": False' in bridge, "bridge 回傳 executable_by_worker=False")
    _check("initial_status=QUEUED" not in bridge, "bridge 未使用 initial_status=QUEUED")
    _check(not re.search(r"initial_status\s*=\s*[\"']queued[\"']", bridge),
           "bridge 未以字面 'queued' 作為 initial_status")

    print("[5] bridge 不接 main / worker / result_sink、不呼叫 OpenClaw / google、不新增 route")
    main_re = re.compile(r"^\s*(?:import|from)\s+app\.main\b", re.MULTILINE)
    worker_re = re.compile(r"^\s*(?:import|from)\s+\S*\bapp\.worker\b", re.MULTILINE)
    sink_re = re.compile(r"^\s*(?:import|from)\s+\S*\bapp\.result_sink\b", re.MULTILINE)
    google_re = re.compile(r"^\s*(?:import|from)\s+\S*(?:google|googleapiclient|gspread|oauthlib)",
                           re.MULTILINE | re.IGNORECASE)
    _check(not main_re.search(bridge), "bridge 未 import app.main")
    _check(not worker_re.search(bridge), "bridge 未 import app.worker")
    _check(not sink_re.search(bridge), "bridge 未 import app.result_sink")
    _check("run_openclaw_cli(" not in bridge, "bridge 未呼叫 run_openclaw_cli()")
    _check(not google_re.search(bridge), "bridge 未 import google / oauth client")
    for bad in ("@app.", "@router.", "FastAPI(", "APIRouter", "add_api_route"):
        _check(bad not in bridge, f"bridge 無 route/POST 痕跡「{bad}」")

    print("[6] main/worker/queue_store/result_sink/security_gates 未被接入新 wiring")
    for path, name in ((APP_MAIN, "main.py"), (WORKER, "worker.py"),
                       (QUEUE_STORE, "queue_store.py"), (RESULT_SINK, "result_sink.py")):
        txt = _read(path)
        _check("security_gates_v0_7" not in txt and "queue_intake_bridge_v0_7" not in txt,
               f"app/{name} 未 import security_gates / intake bridge")
    # security_gates 維持下層純函式：不得反向 import intake bridge。
    _check("queue_intake_bridge_v0_7" not in _read(SECURITY_GATES),
           "security_gates_v0_7.py 未反向 import intake bridge（維持純函式下層）")
    rs_low = _read(RESULT_SINK).lower()
    rs_bad = ("import google", "from google", "googleapiclient", "gspread",
              "google.oauth", "google_auth", "google.auth")
    _check(RESULT_SINK.is_file() and not any(b in rs_low for b in rs_bad),
           "result_sink.py 仍 mock-safe（不 import google client）")

    print("[7] GOOGLE_SHEETS_ENABLED 無 true")
    _check("GOOGLE_SHEETS_ENABLED=true" not in bridge and "GOOGLE_SHEETS_ENABLED=true" not in doc,
           "bridge / doc 未出現 GOOGLE_SHEETS_ENABLED=true")

    print("[8] 敏感檢查（格式比對）：bridge / doc / test 不含真實 secret")
    for name, text in (("bridge", bridge), ("doc", doc), ("test", _read(TEST_FILE))):
        _check(_no_real_secret(text),
               f"{name} 不含完整 spreadsheet id / url / token / private key（格式比對）")
        for key in SECRET_KEY_NAMES:
            _check(key not in text, f"{name} 不含 secret 變數名 {key}")

    if FAILURES:
        print(f"\nXX v0.7.1-E intake security gates wiring readiness 檢查失敗 {len(FAILURES)} 項：")
        for f in FAILURES:
            print(f"   - {f}")
        return 1
    print("\nOK v0.7.1-E intake security gates wiring readiness 全數通過（純檢查，未連任何系統、未含 secret）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
