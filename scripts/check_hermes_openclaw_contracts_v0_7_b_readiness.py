#!/usr/bin/env python3
"""v0.7.0-B — Hermes ↔ OpenClaw 契約 schema + validator 靜態 readiness（純檢查，不連任何系統）。

確認 schema / validator / tests 齊備且未越界：
  - 不接真 OpenClaw / Hermes / Google；validator 不讀 secret、不 import 外部 client。
  - app/main、result_sink、Google writer/runner、Queue/Worker 執行邏輯未被改動接入新流程。
敏感檢查一律使用「格式（regex）比對」，不使用任何真實 secret 或完整 spreadsheet id 逐字比對。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SCHEMA_DIR = ROOT / "docs" / "schemas"
TASK_SCHEMA = SCHEMA_DIR / "task_envelope_v0_7.schema.json"
CALLBACK_SCHEMA = SCHEMA_DIR / "callback_event_v0_7.schema.json"
VALIDATOR = ROOT / "app" / "contracts_v0_7.py"
TEST_FILE = ROOT / "scripts" / "test_contracts_v0_7_b.py"
PLAN_DOC = ROOT / "docs" / "HERMES_OPENCLAW_INTEGRATION_PLAN_V0_7_0_A.md"

APP_MAIN = ROOT / "app" / "main.py"
RESULT_SINK = ROOT / "app" / "result_sink.py"
GOOGLE_WRITER = ROOT / "app" / "google_sheets_oauth_writer.py"
WORKER = ROOT / "app" / "worker.py"
QUEUE_STORE = ROOT / "app" / "queue_store.py"

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

TASK_REQUIRED = (
    "task_id", "created_at", "created_by", "source", "requested_by", "risk_level",
    "approval_required", "approval_status", "intent", "goal", "task_type", "priority",
    "input_summary", "target_runtime", "target_workspace", "idempotency_key",
    "max_retries", "retry_count", "status", "result_policy", "callback_policy", "metadata",
)
CALLBACK_REQUIRED = (
    "event_id", "task_id", "source", "created_at", "event_type", "status",
    "summary", "retryable", "metadata",
)

FAILURES: list[str] = []


def _check(cond: bool, label: str) -> None:
    print(f"  {'ok ' if cond else 'XX '}: {label}")
    if not cond:
        FAILURES.append(label)


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.is_file() else ""


def _no_real_secret(text: str) -> bool:
    """格式比對：text 不含真實 spreadsheet id / url / token / private key。"""
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
    print("[1] schema / validator / test / plan 檔案存在")
    _check(TASK_SCHEMA.is_file(), "docs/schemas/task_envelope_v0_7.schema.json 存在")
    _check(CALLBACK_SCHEMA.is_file(), "docs/schemas/callback_event_v0_7.schema.json 存在")
    _check(VALIDATOR.is_file(), "app/contracts_v0_7.py 存在")
    _check(TEST_FILE.is_file(), "scripts/test_contracts_v0_7_b.py 存在")
    _check(PLAN_DOC.is_file(), "docs/HERMES_OPENCLAW_INTEGRATION_PLAN_V0_7_0_A.md 存在")

    task_txt = _read(TASK_SCHEMA)
    cb_txt = _read(CALLBACK_SCHEMA)
    val_txt = _read(VALIDATOR)

    print("[2] TaskEnvelope schema 含必要欄位")
    for field in TASK_REQUIRED:
        _check(f'"{field}"' in task_txt, f"TaskEnvelope schema 含欄位 {field}")

    print("[3] CallbackEvent schema 含必要欄位")
    for field in CALLBACK_REQUIRED:
        _check(f'"{field}"' in cb_txt, f"CallbackEvent schema 含欄位 {field}")

    print("[4] validator 公開 API")
    _check("def validate_task_envelope" in val_txt, "validator 暴露 validate_task_envelope")
    _check("def validate_callback_event" in val_txt, "validator 暴露 validate_callback_event")
    _check("class ContractValidationError" in val_txt, "validator 暴露 ContractValidationError")

    print("[5] validator 不讀 secret、不呼叫 Google / Hermes / OpenClaw")
    # 行錨定 import 偵測：避免誤判 docstring 中說明性文字（如「不 import Google API」）。
    import_re = re.compile(
        r"^\s*(?:import|from)\s+\S*(?:google|googleapiclient|gspread|oauthlib|openclaw|hermes)",
        re.MULTILINE | re.IGNORECASE,
    )
    secret_re = re.compile(r"\bos\.(?:environ|getenv)\b|\bgetenv\s*\(|\bload_dotenv\b")
    net_re = re.compile(r"\bhttpx\b|\brequests\.(?:get|post)\b|\burllib\.request\b|\bsubprocess\b")
    _check(not import_re.search(val_txt), "validator 未 import google / oauth / openclaw / hermes client")
    _check(not secret_re.search(val_txt), "validator 未讀環境 secret（os.environ / getenv / load_dotenv）")
    _check(not net_re.search(val_txt), "validator 未發出網路呼叫 / 起子程序")

    print("[6] app/main 未接入新整合流程")
    main_txt = _read(APP_MAIN)
    _check("contracts_v0_7" not in main_txt, "app/main.py 未 import contracts_v0_7")

    print("[7] result_sink 仍 mock-safe（未被改成真寫 / 未 import google client）")
    rs_low = _read(RESULT_SINK).lower()
    rs_bad = ("import google", "from google", "googleapiclient", "gspread",
              "google.oauth", "google_auth", "google.auth")
    _check(RESULT_SINK.is_file() and not any(b in rs_low for b in rs_bad),
           "result_sink.py 不 import 任何 google client library")
    _check("contracts_v0_7" not in rs_low, "result_sink.py 未 import contracts_v0_7")

    print("[8] Google writer / Worker / Queue 未接入新契約流程")
    _check("contracts_v0_7" not in _read(GOOGLE_WRITER), "google_sheets_oauth_writer.py 未 import contracts_v0_7")
    _check("contracts_v0_7" not in _read(WORKER), "worker.py 未 import contracts_v0_7")
    _check("contracts_v0_7" not in _read(QUEUE_STORE), "queue_store.py 未 import contracts_v0_7")

    print("[9] schema / validator / test 不含真實 secret（格式比對）")
    for name, text in (
        ("task schema", task_txt),
        ("callback schema", cb_txt),
        ("validator", val_txt),
        ("test", _read(TEST_FILE)),
    ):
        _check(_no_real_secret(text), f"{name} 不含完整 spreadsheet id / url / token / private key（格式比對）")
        for key in SECRET_KEY_NAMES:
            _check(key not in text, f"{name} 不含 secret 變數名 {key}")

    if FAILURES:
        print(f"\nXX v0.7.0-B contracts readiness 檢查失敗 {len(FAILURES)} 項：")
        for f in FAILURES:
            print(f"   - {f}")
        return 1
    print("\nOK v0.7.0-B contracts readiness 全數通過（純檢查，未連任何系統、未含 secret）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
