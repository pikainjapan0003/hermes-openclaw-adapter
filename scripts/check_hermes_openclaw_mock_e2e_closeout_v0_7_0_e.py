#!/usr/bin/env python3
"""v0.7.0-E — Hermes ↔ OpenClaw mock E2E closeout + boundary review 靜態 readiness（純檢查，不連任何系統）。

確認 v0.7.0 A–E 交付齊備、closeout 文件涵蓋邊界聲明，且整體未越界：
  - mock_e2e / mock_adapter 不接真 Google / Hermes / OpenClaw、不讀 secret、
    不 import queue_store / sqlite3 / worker。
  - app/main 未接入 mock 流程；result_sink 仍 mock-safe。
敏感檢查一律使用「格式（regex）比對」，不使用任何真實 secret 或完整 spreadsheet id 逐字比對。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CLOSEOUT_DOC = ROOT / "docs" / "HERMES_OPENCLAW_MOCK_E2E_CLOSEOUT_BOUNDARY_REVIEW_V0_7_0_E.md"

# v0.7.0 A–E 應齊備的檔案。
REQUIRED_FILES = (
    "docs/HERMES_OPENCLAW_INTEGRATION_PLAN_V0_7_0_A.md",
    "docs/schemas/task_envelope_v0_7.schema.json",
    "docs/schemas/callback_event_v0_7.schema.json",
    "app/contracts_v0_7.py",
    "scripts/test_contracts_v0_7_b.py",
    "scripts/check_hermes_openclaw_contracts_v0_7_b_readiness.py",
    "app/mock_adapter_v0_7.py",
    "docs/HERMES_OPENCLAW_MOCK_ADAPTER_V0_7_0_C.md",
    "scripts/test_mock_adapter_v0_7_c.py",
    "scripts/check_hermes_openclaw_mock_adapter_v0_7_c_readiness.py",
    "app/mock_e2e_v0_7.py",
    "docs/HERMES_OPENCLAW_MOCK_E2E_DRY_RUN_V0_7_0_D.md",
    "scripts/test_mock_e2e_v0_7_d.py",
    "scripts/check_hermes_openclaw_mock_e2e_v0_7_d_readiness.py",
    "docs/HERMES_OPENCLAW_MOCK_E2E_CLOSEOUT_BOUNDARY_REVIEW_V0_7_0_E.md",
)

# closeout 文件必含關鍵字。
REQUIRED_KEYWORDS = (
    "v0.7.0-A",
    "v0.7.0-B",
    "v0.7.0-C",
    "v0.7.0-D",
    "Mock E2E",
    "Boundary Review",
    "No true Hermes",
    "No true OpenClaw",
    "No true Queue DB",
    "No true Worker",
    "No automatic Google Sheets",
    "GOOGLE_SHEETS_ENABLED=false",
)

APP_MAIN = ROOT / "app" / "main.py"
RESULT_SINK = ROOT / "app" / "result_sink.py"
MOCK_E2E = ROOT / "app" / "mock_e2e_v0_7.py"
MOCK_ADAPTER = ROOT / "app" / "mock_adapter_v0_7.py"

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
    print("[1] v0.7.0 A–E 必要檔案齊備")
    for rel in REQUIRED_FILES:
        _check((ROOT / rel).is_file(), f"{rel} 存在")

    print("[2] closeout 文件含關鍵字 / 邊界聲明")
    closeout = _read(CLOSEOUT_DOC)
    for kw in REQUIRED_KEYWORDS:
        _check(kw in closeout, f"closeout 文件含關鍵字「{kw}」")

    print("[3] app/main 未接入 mock 流程；result_sink 仍 mock-safe")
    main_txt = _read(APP_MAIN)
    _check("mock_e2e_v0_7" not in main_txt, "app/main.py 未 import mock_e2e_v0_7")
    _check("mock_adapter_v0_7" not in main_txt, "app/main.py 未 import mock_adapter_v0_7")
    rs_low = _read(RESULT_SINK).lower()
    rs_bad = ("import google", "from google", "googleapiclient", "gspread",
              "google.oauth", "google_auth", "google.auth")
    _check(RESULT_SINK.is_file() and not any(b in rs_low for b in rs_bad),
           "result_sink.py 未被改成真 Google Sheets 自動寫入（不 import google client）")

    print("[4] mock_e2e / mock_adapter 未接真系統（行錨定 import 偵測）")
    e2e_txt = _read(MOCK_E2E)
    adapter_txt = _read(MOCK_ADAPTER)
    # 行錨定：只看實際 import 行，不因 docstring 提到 sqlite3 等字而誤判。
    e2e_bad_import_re = re.compile(
        r"^\s*(?:import|from)\s+\S*"
        r"(?:google|googleapiclient|gspread|oauthlib|openclaw|hermes|sqlite3|queue_store|worker)",
        re.MULTILINE | re.IGNORECASE,
    )
    adapter_bad_import_re = re.compile(
        r"^\s*(?:import|from)\s+\S*"
        r"(?:google|googleapiclient|gspread|oauthlib|openclaw|hermes|sqlite3|queue_store|worker)",
        re.MULTILINE | re.IGNORECASE,
    )
    secret_re = re.compile(r"\bos\.(?:environ|getenv)\b|\bgetenv\s*\(|\bload_dotenv\b")
    _check(not e2e_bad_import_re.search(e2e_txt),
           "mock_e2e_v0_7.py 未 import google / queue_store / sqlite3 / worker / openclaw / hermes")
    _check(not secret_re.search(e2e_txt), "mock_e2e_v0_7.py 未讀 os.environ / getenv / load_dotenv")
    _check(not adapter_bad_import_re.search(adapter_txt),
           "mock_adapter_v0_7.py 未 import google / queue_store / sqlite3 / worker / openclaw / hermes")
    _check(not secret_re.search(adapter_txt),
           "mock_adapter_v0_7.py 未讀 os.environ / getenv / load_dotenv")

    print("[5] closeout 文件不含真實 secret（格式比對）")
    _check(_no_real_secret(closeout),
           "closeout 文件不含完整 spreadsheet id / url / token / private key（格式比對）")
    for key in SECRET_KEY_NAMES:
        _check(key not in closeout, f"closeout 文件不含 secret 變數名 {key}")

    if FAILURES:
        print(f"\nXX v0.7.0-E closeout readiness 檢查失敗 {len(FAILURES)} 項：")
        for f in FAILURES:
            print(f"   - {f}")
        return 1
    print("\nOK v0.7.0-E closeout readiness 全數通過（純檢查，未連任何系統、未含 secret）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
