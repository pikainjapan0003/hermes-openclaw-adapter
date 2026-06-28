#!/usr/bin/env python3
"""v0.7.1-H — Closeout Boundary Review 靜態 readiness（純檢查，不連任何系統）。

確認 v0.7.1-H 為 closeout-only：
  - H closeout doc + 本 readiness 存在；doc 含必要章節與所有 closeout 裁定。
  - doc 凍結 current master hash、A–G complete、aggregator 為 regression gate、
    A/C/C2/D 為 stale snapshot、F2-A/F2-B/v0.7.2 未開始、無 v0.7 tag、不在本版 tag。
  - current-state aggregator 仍存在且可執行 EXIT=0；G readiness 仍存在。
  - app/main.py / queue_store.py / worker.py / result_sink.py 未 import approval gate。
靜態檢查：不連外、不寫 DB、不讀 secrets。敏感檢查一律 regex / 格式比對。
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOC = ROOT / "docs" / "HERMES_OPENCLAW_V0_7_1_CLOSEOUT_BOUNDARY_REVIEW_V0_7_1_H.md"
READINESS = ROOT / "scripts" / "check_hermes_openclaw_v0_7_1_closeout_boundary_review_v0_7_1_h.py"
AGGREGATOR = ROOT / "scripts" / "check_hermes_openclaw_v0_7_1_current_state.py"
G_READINESS = ROOT / "scripts" / "check_hermes_openclaw_stale_readiness_cleanup_review_v0_7_1_g.py"

MAIN = ROOT / "app" / "main.py"
QUEUE_STORE = ROOT / "app" / "queue_store.py"
WORKER = ROOT / "app" / "worker.py"
RESULT_SINK = ROOT / "app" / "result_sink.py"

MASTER_HASH = "0c02c562620b1631cc60f44e8d4e61825bb6a30f"
APPROVAL_MODULE_NAME = "approval_security_gate" + "_v0_7"

REQUIRED_TITLES = (
    "1. Purpose", "2. Current Master State", "3. v0.7.1 Scope Summary",
    "4. v0.7.1-A Status", "5. v0.7.1-B Status", "6. v0.7.1-C Status",
    "7. v0.7.1-C2 Status", "8. v0.7.1-C3 Status", "9. v0.7.1-D Status",
    "10. v0.7.1-D2 Status", "11. v0.7.1-E Status", "12. v0.7.1-F Status",
    "13. v0.7.1-F2 Status", "14. v0.7.1-G Status", "15. Implemented Capabilities",
    "16. Plan-only Items", "17. Explicitly Unwired Items",
    "18. Safety Boundary Confirmation", "19. Current-State Regression Status",
    "20. Stale Readiness Policy", "21. Approval Route Boundary",
    "22. Dashboard Approval Boundary", "23. QueueStore Boundary",
    "24. Worker / OpenClaw Boundary", "25. Hermes Boundary",
    "26. Google Sheets Boundary", "27. Secrets Boundary", "28. F2-A Preconditions",
    "29. v0.7.2 Direction Options", "30. Tag Recommendation",
    "31. Explicit Non-goals", "32. Final Closeout Recommendation",
)

REQUIRED_STATEMENTS = (
    "v0.7.1-H is closeout-only.",
    "v0.7.1-A through G are complete.",
    MASTER_HASH,
    "current-state aggregator is the regression gate.",
    "A/C/C2/D stale readiness scripts are historical snapshots and are not "
    "required to be green.",
    "F2-A has not started.",
    "F2-B has not started.",
    "v0.7.2 has not started.",
    "No v0.7 tag currently exists.",
    "v0.7.1-H does not modify app/main.py.",
    "v0.7.1-H does not modify queue_store.py.",
    "v0.7.1-H does not modify worker.py.",
    "v0.7.1-H does not wire approve routes.",
    "v0.7.1-H does not wire Dashboard approve.",
    "v0.7.1-H does not start Worker.",
    "v0.7.1-H does not call OpenClaw.",
    "v0.7.1-H does not call Hermes.",
    "v0.7.1-H does not write Google Sheets.",
    "Do not tag in v0.7.1-H.",
    "production readiness audit for waiting_review tasks",
)

# v0.7.2-A Safe Autopilot / Auto-Approval policy 必須被 closeout doc 納入（plan-only / safe）。
REQUIRED_AUTOPILOT_STATEMENTS = (
    "v0.7.2-A: Auto-Approval Policy Plan / Safe Autopilot Mode",
    "No --dangerously-skip-permissions equivalent is approved.",
    "AUTO_APPROVAL_MODE=off | safe",
    "SAFE_AUTOPILOT_ENABLED=false by default",
    "LOW_RISK_AUTO_APPROVAL_ENABLED=false by default",
    "AUTO_APPROVAL_POLICY=safe",
    "v0.7.2-A should start as plan-only.",
)

RE_SPREADSHEET_URL = re.compile(r"spreadsheets/d/[A-Za-z0-9_-]{20,}")
RE_SPREADSHEET_ASSIGN = re.compile(r"SPREADSHEET_ID\s*[:=]\s*[\"'][A-Za-z0-9_-]{20,}[\"']")
RE_TOKEN_PREFIX = re.compile(r"(ya29\.[A-Za-z0-9_-]{10,}|1//[A-Za-z0-9_-]{10,}|" + "goc" + r"spx-[A-Za-z0-9_-]{10,})")
RE_PRIVATE_KEY = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")
RE_SHEETS_ENABLED_TRUE = re.compile(r"GOOGLE_SHEETS_ENABLED\s*[:=]\s*true", re.IGNORECASE)

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
    doc = _read(DOC)

    print("[1] H closeout doc / readiness / aggregator / G readiness 存在")
    _check(DOC.is_file(), "H closeout doc 存在")
    _check(READINESS.is_file(), "H readiness script 自身存在")
    _check(AGGREGATOR.is_file(), "current-state aggregator script 存在")
    _check(G_READINESS.is_file(), "G readiness script 存在")

    print("[2] H doc 含所有必要章節")
    for title in REQUIRED_TITLES:
        _check(title in doc, f"H doc 含章節「{title}」")

    print("[3] H doc 含所有 closeout 裁定 / 邊界聲明")
    for stmt in REQUIRED_STATEMENTS:
        _check(stmt in doc, f"H doc 含聲明「{stmt[:48]}…」")

    print("[3b] H doc 含 v0.7.2-A Safe Autopilot / Auto-Approval policy（plan-only / safe）")
    for stmt in REQUIRED_AUTOPILOT_STATEMENTS:
        _check(stmt in doc, f"H doc 含 autopilot 聲明「{stmt[:48]}…」")

    print("[4] current-state aggregator 執行 EXIT=0")
    proc = subprocess.run([sys.executable, str(AGGREGATOR)], cwd=str(ROOT),
                          capture_output=True, text=True, check=False)
    _check(proc.returncode == 0, "current-state aggregator EXIT=0")

    print("[5] approval gate 尚未接入 main/queue_store/worker/result_sink")
    imp_re = re.compile(rf"^\s*(?:import|from)\s+\S*{re.escape(APPROVAL_MODULE_NAME)}\b", re.MULTILINE)
    for path, name in ((MAIN, "main.py"), (QUEUE_STORE, "queue_store.py"),
                       (WORKER, "worker.py"), (RESULT_SINK, "result_sink.py")):
        _check(not imp_re.search(_read(path)), f"{name} 未 import {APPROVAL_MODULE_NAME}")

    print("[6] safety：GOOGLE_SHEETS_ENABLED 非 true（doc）")
    _check(not RE_SHEETS_ENABLED_TRUE.search(doc), "H doc 未把 GOOGLE_SHEETS_ENABLED 設為 true")

    print("[7] 敏感檢查（格式比對）：doc / script 不含真實 secret")
    _check(_no_real_secret(doc), "doc 不含完整 spreadsheet id / url / token / private key（格式比對）")
    _check(_no_real_secret(_read(READINESS)),
           "script 不含完整 spreadsheet id / url / token / private key（格式比對）")

    print("[8] 無 v0.7 tag")
    proc = subprocess.run(["git", "tag", "--list", "*0.7*"], cwd=str(ROOT),
                          capture_output=True, text=True, check=False)
    _check(proc.returncode == 0 and proc.stdout.strip() == "", "repo 無 v0.7 tag")

    if FAILURES:
        print(f"\nXX v0.7.1-H closeout boundary review readiness 失敗 {len(FAILURES)} 項：")
        for f in FAILURES:
            print(f"   - {f}")
        return 1
    print("\nOK v0.7.1-H closeout boundary review readiness 全數通過"
          "（closeout-only；未動 app、未接 route、未 tag、未含 secret）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
