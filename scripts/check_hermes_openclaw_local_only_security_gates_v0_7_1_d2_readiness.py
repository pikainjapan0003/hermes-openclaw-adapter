#!/usr/bin/env python3
"""v0.7.1-D2 — Local-only Security Gates 靜態 readiness（純檢查，不連任何系統）。

確認 security_gates 模組為純函式 / local-only 且未越界：
  - 不 import app.main / app.worker / app.queue_store / app.result_sink。
  - 不呼叫 enqueue / claim_next / approve / reject / run_openclaw_cli / google client、不寫 DB。
  - 含 evaluate_kill_switch / evaluate_tool_allowlist / redact_audit_metadata / build_audit_event。
  - 既有 main/worker/queue_store/result_sink 未被接入。
靜態檢查：不連外、不寫 DB、不讀 secrets。敏感檢查一律 regex / 格式比對。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MODULE = ROOT / "app" / "security_gates_v0_7.py"
DOC = ROOT / "docs" / "HERMES_OPENCLAW_LOCAL_ONLY_SECURITY_GATES_V0_7_1_D2.md"
TEST_FILE = ROOT / "scripts" / "test_security_gates_v0_7_1_d2.py"
READINESS = ROOT / "scripts" / "check_hermes_openclaw_local_only_security_gates_v0_7_1_d2_readiness.py"

APP_MAIN = ROOT / "app" / "main.py"
WORKER = ROOT / "app" / "worker.py"
QUEUE_STORE = ROOT / "app" / "queue_store.py"
RESULT_SINK = ROOT / "app" / "result_sink.py"

REQUIRED_TITLES = (
    "1. Purpose", "2. Relationship To v0.7.1-D", "3. What Was Implemented",
    "4. What v0.7.1-D2 Does Not Do", "5. Security Gate Priority", "6. Kill Switch Evaluation",
    "7. Per-tool Allowlist Evaluation", "8. Denylist Priority", "9. Audit Event Builder",
    "10. Audit Metadata Redaction", "11. Observation-only Boundary",
    "12. Queue Source-of-truth Boundary", "13. Result Sink Boundary", "14. Google Sheets Boundary",
    "15. Security / Secrets Rules", "16. Test Coverage", "17. Readiness Checks",
    "18. Future Integration Criteria", "19. Explicit Non-goals", "20. Final Recommendation",
)
REQUIRED_DECLARATIONS = (
    "No app/main.py modification.", "No worker.py modification.",
    "No queue_store.py modification.", "No result_sink.py modification.",
    "No DB write.", "No Queue status mutation.", "No new route.", "No new POST handler.",
    "No Worker start.", "No OpenClaw execution.", "No Hermes webhook.",
    "No Google Sheets write.",
    "Audit events are observation-only, not Queue source of truth.",
)
REQUIRED_FUNCS = (
    "def evaluate_kill_switch", "def evaluate_tool_allowlist",
    "def evaluate_security_gates", "def redact_audit_metadata", "def build_audit_event",
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
    _check(MODULE.is_file(), "app/security_gates_v0_7.py 存在")
    _check(DOC.is_file(), "v0.7.1-D2 doc 存在")
    _check(TEST_FILE.is_file(), "test 存在")
    _check(READINESS.is_file(), "readiness script 自身存在")

    print("[2] doc 含必要章節與安全聲明")
    for title in REQUIRED_TITLES:
        _check(title in doc, f"doc 含章節「{title}」")
    for line in REQUIRED_DECLARATIONS:
        _check(line in doc, f"doc 含聲明「{line}」")

    print("[3] module 不 import main / worker / queue_store / result_sink（行錨定）")
    for mod in ("app\\.main", "app\\.worker", "app\\.queue_store", "app\\.result_sink"):
        imp_re = re.compile(rf"^\s*(?:import|from)\s+\S*{mod}\b", re.MULTILINE)
        _check(not imp_re.search(module), f"module 未 import {mod.replace(chr(92), '')}")

    print("[4] module 不呼叫 enqueue / claim_next / approve / reject / run_openclaw_cli / google")
    for pat in ("enqueue(", ".claim_next(", ".approve(", ".reject(", "run_openclaw_cli("):
        _check(pat not in module, f"module 無呼叫痕跡「{pat}」")
    google_re = re.compile(r"^\s*(?:import|from)\s+\S*(?:google|googleapiclient|gspread|oauthlib)",
                           re.MULTILINE | re.IGNORECASE)
    _check(not google_re.search(module), "module 未 import google / oauth client")

    print("[5] module 不寫 DB / sqlite")
    for pat in ("sqlite3", ".execute(", ".commit("):
        _check(pat not in module, f"module 不含 DB 寫入痕跡「{pat}」")
    _check(not re.search(r"open\s*\([^)]*[\"'][wax]", module), "module 不含檔案寫入 open(...'w/a/x')")

    print("[6] module 含必要函式")
    for fn in REQUIRED_FUNCS:
        _check(fn in module, f"module 含 {fn}")

    print("[7] module 實作 denylist priority / allowlist fail-closed")
    _check('"denylist"' in module, "module 標示 denylist priority")
    _check("allowed_tools_empty" in module, "module 有 allowed_tools 空 fail-closed reject")
    _check("requested_tools_empty" in module, "module 有 requested_tools 空 reject")

    print("[8] 既有 main/worker/queue_store/result_sink 未被接入")
    for path, name in ((APP_MAIN, "main.py"), (WORKER, "worker.py"),
                       (QUEUE_STORE, "queue_store.py"), (RESULT_SINK, "result_sink.py")):
        _check("security_gates_v0_7" not in _read(path), f"app/{name} 未 import security_gates_v0_7")
    rs_low = _read(RESULT_SINK).lower()
    rs_bad = ("import google", "from google", "googleapiclient", "gspread",
              "google.oauth", "google_auth", "google.auth")
    _check(RESULT_SINK.is_file() and not any(b in rs_low for b in rs_bad),
           "result_sink.py 仍 mock-safe（不 import google client）")

    print("[9] 無新增 route / webhook / POST handler（module + doc）")
    for bad in ("@app.", "@router.", "FastAPI(", "APIRouter", "add_api_route"):
        _check(bad not in module and bad not in doc, f"module / doc 無「{bad}」")

    print("[10] GOOGLE_SHEETS_ENABLED 無 true")
    _check("GOOGLE_SHEETS_ENABLED=true" not in module and "GOOGLE_SHEETS_ENABLED=true" not in doc,
           "module / doc 未出現 GOOGLE_SHEETS_ENABLED=true")

    print("[11] 敏感檢查（格式比對）：module / doc / test 不含真實 secret")
    for name, text in (("module", module), ("doc", doc), ("test", _read(TEST_FILE))):
        _check(_no_real_secret(text),
               f"{name} 不含完整 spreadsheet id / url / token / private key（格式比對）")
        for key in SECRET_KEY_NAMES:
            _check(key not in text, f"{name} 不含 secret 變數名 {key}")

    if FAILURES:
        print(f"\nXX v0.7.1-D2 local-only security gates readiness 檢查失敗 {len(FAILURES)} 項：")
        for f in FAILURES:
            print(f"   - {f}")
        return 1
    print("\nOK v0.7.1-D2 local-only security gates readiness 全數通過（純檢查，未連任何系統、未含 secret）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
