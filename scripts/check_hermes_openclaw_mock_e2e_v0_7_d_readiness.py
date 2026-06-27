#!/usr/bin/env python3
"""v0.7.0-D — Hermes ↔ OpenClaw mock E2E dry-run 靜態 readiness（純檢查，不連任何系統）。

確認 mock E2E 模組 / docs / tests 齊備且未越界：
  - mock_e2e 不接真 Google / Hermes / OpenClaw、不讀 secret、不寫 Queue DB、不 import queue_store /
    sqlite3 / worker、不啟動 Worker、不做 network call。
  - app/main、result_sink、Google writer/runner、Queue/Worker 執行邏輯未被改動接入新流程。
敏感檢查一律使用「格式（regex）比對」，不使用任何真實 secret 或完整 spreadsheet id 逐字比對。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

E2E = ROOT / "app" / "mock_e2e_v0_7.py"
DOC = ROOT / "docs" / "HERMES_OPENCLAW_MOCK_E2E_DRY_RUN_V0_7_0_D.md"
TEST_FILE = ROOT / "scripts" / "test_mock_e2e_v0_7_d.py"
ADAPTER = ROOT / "app" / "mock_adapter_v0_7.py"
VALIDATOR = ROOT / "app" / "contracts_v0_7.py"
TASK_SCHEMA = ROOT / "docs" / "schemas" / "task_envelope_v0_7.schema.json"
CALLBACK_SCHEMA = ROOT / "docs" / "schemas" / "callback_event_v0_7.schema.json"

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
    print("[1] 必要檔案存在")
    _check(E2E.is_file(), "app/mock_e2e_v0_7.py 存在")
    _check(DOC.is_file(), "docs/HERMES_OPENCLAW_MOCK_E2E_DRY_RUN_V0_7_0_D.md 存在")
    _check(TEST_FILE.is_file(), "scripts/test_mock_e2e_v0_7_d.py 存在")
    _check(ADAPTER.is_file(), "app/mock_adapter_v0_7.py 存在")
    _check(VALIDATOR.is_file(), "app/contracts_v0_7.py 存在")
    _check(TASK_SCHEMA.is_file(), "docs/schemas/task_envelope_v0_7.schema.json 存在")
    _check(CALLBACK_SCHEMA.is_file(), "docs/schemas/callback_event_v0_7.schema.json 存在")

    e2e_txt = _read(E2E)

    print("[2] mock E2E 公開 API")
    _check("class MockE2EError" in e2e_txt, "暴露 MockE2EError")
    _check("class InMemoryMockQueue" in e2e_txt, "暴露 InMemoryMockQueue")
    _check("def mock_worker_process_task" in e2e_txt, "暴露 mock_worker_process_task")
    _check("def apply_callback_to_mock_task" in e2e_txt, "暴露 apply_callback_to_mock_task")
    _check("def run_mock_e2e_dry_run" in e2e_txt, "暴露 run_mock_e2e_dry_run")
    _check("validate_callback_event" in e2e_txt, "使用 validate_callback_event")
    _check("validate_task_envelope" in e2e_txt, "使用 validate_task_envelope")

    print("[3] mock_e2e 不接 Google / Hermes / OpenClaw、不讀 secret、不寫 Queue DB / worker / network")
    # 行錨定 import 偵測：避免誤判 docstring 中的說明性文字。
    bad_import_re = re.compile(
        r"^\s*(?:import|from)\s+\S*"
        r"(?:google|googleapiclient|gspread|oauthlib|openclaw|hermes|sqlite3|queue_store|worker)",
        re.MULTILINE | re.IGNORECASE,
    )
    secret_re = re.compile(r"\bos\.(?:environ|getenv)\b|\bgetenv\s*\(|\bload_dotenv\b")
    net_re = re.compile(r"\bhttpx\b|\brequests\.(?:get|post)\b|\burllib\.request\b|\bsubprocess\b")
    # DB/檔案「寫入操作」偵測（sqlite3 / queue_store import 由上面 bad_import_re 行錨定處理，
    # 此處只看實際寫入操作，避免誤判 docstring 中提到 sqlite3 等說明文字）。
    db_re = re.compile(r"\bsqlite3\.connect\b|\bQueueStore\s*\(|\.commit\s*\(|\.execute\s*\(|open\s*\([^)]*[\"']w")
    _check(not bad_import_re.search(e2e_txt),
           "未 import google / oauth / openclaw / hermes / sqlite3 / queue_store / worker")
    _check(not secret_re.search(e2e_txt), "未讀環境 secret（os.environ / getenv / load_dotenv）")
    _check(not net_re.search(e2e_txt), "未發出網路呼叫 / 起子程序")
    _check(not db_re.search(e2e_txt),
           "未寫 Queue DB / 檔案（無 sqlite3 / QueueStore / commit / execute / 寫檔）")

    print("[4] app/main 未接入新整合流程")
    _check("mock_e2e_v0_7" not in _read(APP_MAIN), "app/main.py 未 import mock_e2e_v0_7")

    print("[5] result_sink 仍 mock-safe（未被改成真寫 / 未 import google client / 未接 mock e2e）")
    rs_low = _read(RESULT_SINK).lower()
    rs_bad = ("import google", "from google", "googleapiclient", "gspread",
              "google.oauth", "google_auth", "google.auth")
    _check(RESULT_SINK.is_file() and not any(b in rs_low for b in rs_bad),
           "result_sink.py 不 import 任何 google client library")
    _check("mock_e2e_v0_7" not in rs_low, "result_sink.py 未 import mock_e2e_v0_7")

    print("[6] Google writer / Worker / Queue 未接入新 mock e2e 流程")
    _check("mock_e2e_v0_7" not in _read(GOOGLE_WRITER),
           "google_sheets_oauth_writer.py 未 import mock_e2e_v0_7")
    _check("mock_e2e_v0_7" not in _read(WORKER), "worker.py 未 import mock_e2e_v0_7")
    _check("mock_e2e_v0_7" not in _read(QUEUE_STORE), "queue_store.py 未 import mock_e2e_v0_7")

    print("[7] e2e / doc / test 不含真實 secret（格式比對）")
    for name, text in (
        ("mock e2e", e2e_txt),
        ("doc", _read(DOC)),
        ("test", _read(TEST_FILE)),
    ):
        _check(_no_real_secret(text),
               f"{name} 不含完整 spreadsheet id / url / token / private key（格式比對）")
        for key in SECRET_KEY_NAMES:
            _check(key not in text, f"{name} 不含 secret 變數名 {key}")

    if FAILURES:
        print(f"\nXX v0.7.0-D mock E2E readiness 檢查失敗 {len(FAILURES)} 項：")
        for f in FAILURES:
            print(f"   - {f}")
        return 1
    print("\nOK v0.7.0-D mock E2E readiness 全數通過（純檢查，未連任何系統、未含 secret）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
