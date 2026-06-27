#!/usr/bin/env python3
"""v0.7.1-B — Local-only Queue Intake Bridge 靜態 readiness（純檢查，不連任何系統）。

確認 bridge / doc / test 齊備且未越界：
  - fail-closed（QUEUE_INTAKE_ENABLED 預設 false）、kill switch、allowlist、獨立 intake DB。
  - bridge 不 import app.worker / app.main、不呼叫 run_openclaw_cli / Google client、不寫 queued。
  - 既有 main/worker/queue_store/result_sink 未被接入新流程。
靜態檢查：不 import Google/Hermes/OpenClaw client、不讀 secret、不連線、不寫 DB。
敏感檢查一律使用 regex / 格式比對，不逐字比對完整 spreadsheet id。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

BRIDGE = ROOT / "app" / "queue_intake_bridge_v0_7.py"
DOC = ROOT / "docs" / "HERMES_OPENCLAW_LOCAL_ONLY_QUEUE_INTAKE_BRIDGE_V0_7_1_B.md"
TEST_FILE = ROOT / "scripts" / "test_queue_intake_bridge_v0_7_1_b.py"

APP_MAIN = ROOT / "app" / "main.py"
WORKER = ROOT / "app" / "worker.py"
QUEUE_STORE = ROOT / "app" / "queue_store.py"
RESULT_SINK = ROOT / "app" / "result_sink.py"

REQUIRED_TITLES = (
    "1. Purpose",
    "2. Relationship To v0.7.1-A",
    "3. What v0.7.1-B Allows",
    "4. What v0.7.1-B Does Not Allow",
    "5. Local-only Intake DB Boundary",
    "6. Fail-closed Flag Model",
    "7. Kill Switch Behavior",
    "8. Task Type Allowlist Behavior",
    "9. Waiting Review Status Guarantee",
    "10. Worker Auto-run Prevention",
    "11. Mock / Real Boundary",
    "12. Metadata Marking",
    "13. Result Sink Boundary",
    "14. Google Sheets Boundary",
    "15. Security / Secrets Rules",
    "16. Test Coverage",
    "17. Readiness Checks",
    "18. Explicit Non-goals",
    "19. Final Recommendation",
)

REQUIRED_DECLARATIONS = (
    "No true Hermes webhook.",
    "No true OpenClaw execution.",
    "No true Worker start.",
    "No production Queue DB write.",
    "No automatic Google Sheets write.",
    "No external side effect.",
    "No queued status from intake bridge.",
    "All persisted intake tasks must be waiting_review.",
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
    print("[1] doc / bridge / test 檔存在")
    _check(BRIDGE.is_file(), "app/queue_intake_bridge_v0_7.py 存在")
    _check(DOC.is_file(), "docs/HERMES_OPENCLAW_LOCAL_ONLY_QUEUE_INTAKE_BRIDGE_V0_7_1_B.md 存在")
    _check(TEST_FILE.is_file(), "scripts/test_queue_intake_bridge_v0_7_1_b.py 存在")

    bridge = _read(BRIDGE)
    doc = _read(DOC)

    print("[2] 文件含必要標題與安全聲明")
    for title in REQUIRED_TITLES:
        _check(title in doc, f"文件含章節「{title}」")
    for line in REQUIRED_DECLARATIONS:
        _check(line in doc, f"文件含聲明「{line}」")

    print("[3] bridge 預設 QUEUE_INTAKE_ENABLED=false（fail-closed）")
    _check(bool(re.search(r"_env_bool\(\s*[\"']QUEUE_INTAKE_ENABLED[\"']\s*,\s*False", bridge)),
           "bridge 以預設 False 讀取 QUEUE_INTAKE_ENABLED")

    print("[4] bridge 含 kill switch / allowlist / intake DB 路徑 flag")
    _check("INTAKE_KILL_SWITCH" in bridge, "bridge 含 INTAKE_KILL_SWITCH")
    _check("INTAKE_ALLOWED_TASK_TYPES" in bridge, "bridge 含 INTAKE_ALLOWED_TASK_TYPES")
    _check("INTAKE_QUEUE_DB_PATH" in bridge, "bridge 含 INTAKE_QUEUE_DB_PATH")

    print("[5] bridge 不 import app.worker / app.main（行錨定）")
    worker_import_re = re.compile(r"^\s*(?:import|from)\s+\S*\bapp\.worker\b", re.MULTILINE)
    main_import_re = re.compile(r"^\s*(?:import|from)\s+app\.main\b", re.MULTILINE)
    _check(not worker_import_re.search(bridge), "bridge 未 import app.worker")
    _check(not main_import_re.search(bridge), "bridge 未 import app.main")

    print("[6] bridge 不呼叫 run_openclaw_cli / Google client（行錨定 import + 呼叫痕跡）")
    google_import_re = re.compile(
        r"^\s*(?:import|from)\s+\S*(?:google|googleapiclient|gspread|oauthlib)",
        re.MULTILINE | re.IGNORECASE,
    )
    _check("run_openclaw_cli(" not in bridge, "bridge 未呼叫 run_openclaw_cli()")
    _check(not google_import_re.search(bridge), "bridge 未 import google / oauth client")

    print("[7] bridge 不寫 queued；寫入狀態只能 waiting_review")
    _check("initial_status=WAITING_REVIEW" in bridge, "bridge enqueue 使用 initial_status=WAITING_REVIEW")
    _check("initial_status=QUEUED" not in bridge, "bridge 未使用 initial_status=QUEUED")
    _check(not re.search(r"initial_status\s*=\s*[\"']queued[\"']", bridge),
           "bridge 未以字面 'queued' 作為 initial_status")

    print("[8] bridge 不讀 secret env 名稱")
    for key in ("GOOGLE_OAUTH_REFRESH_TOKEN", "GOOGLE_OAUTH_CLIENT_SECRET", "GOOGLE_SERVICE_ACCOUNT_JSON"):
        _check(key not in bridge, f"bridge 未讀 secret env 名稱 {key}")

    print("[9] 既有 main/worker/queue_store/result_sink 未被接入新流程")
    for path, name in ((APP_MAIN, "app/main.py"), (WORKER, "app/worker.py"),
                       (QUEUE_STORE, "app/queue_store.py"), (RESULT_SINK, "app/result_sink.py")):
        _check("queue_intake_bridge_v0_7" not in _read(path), f"{name} 未 import / 引用 intake bridge")
    rs_low = _read(RESULT_SINK).lower()
    rs_bad = ("import google", "from google", "googleapiclient", "gspread",
              "google.oauth", "google_auth", "google.auth")
    _check(RESULT_SINK.is_file() and not any(b in rs_low for b in rs_bad),
           "result_sink.py 仍 mock-safe（不 import google client）")

    print("[10] bridge 無新增 webhook / route / background worker / scheduler（實作痕跡）")
    # 只看實作痕跡（route decorator / FastAPI / background task），不誤判 docstring 中的「webhook」字樣。
    for bad in ("@app.", "@router.", "FastAPI(", "BackgroundTasks", "add_task", "APIRouter"):
        _check(bad not in bridge, f"bridge 不含實作痕跡「{bad}」")

    print("[11] GOOGLE_SHEETS_ENABLED 無 true")
    _check("GOOGLE_SHEETS_ENABLED=true" not in doc and "GOOGLE_SHEETS_ENABLED=true" not in bridge,
           "doc / bridge 未出現 GOOGLE_SHEETS_ENABLED=true")

    print("[12] 敏感檢查（格式比對）：bridge / doc / test 不含真實 secret")
    for name, text in (("bridge", bridge), ("doc", doc), ("test", _read(TEST_FILE))):
        _check(_no_real_secret(text),
               f"{name} 不含完整 spreadsheet id / url / token / private key（格式比對）")
        for key in SECRET_KEY_NAMES:
            _check(key not in text, f"{name} 不含 secret 變數名 {key}")

    if FAILURES:
        print(f"\nXX v0.7.1-B local-only intake bridge readiness 檢查失敗 {len(FAILURES)} 項：")
        for f in FAILURES:
            print(f"   - {f}")
        return 1
    print("\nOK v0.7.1-B local-only intake bridge readiness 全數通過（純檢查，未連任何系統、未含 secret）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
