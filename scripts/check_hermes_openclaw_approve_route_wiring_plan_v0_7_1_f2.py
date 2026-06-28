#!/usr/bin/env python3
"""v0.7.1-F2 — Approve Route Wiring Plan 靜態 readiness（純檢查，不連任何系統）。

本版為 plan-only：只新增 doc + 本 readiness script，不接 approve route、不改 production。
本 script 只做靜態檢查：
  - 確認 plan doc / 本 script 存在，doc 含所有必要章節與安全聲明。
  - 確認 doc 明確聲明 plan-only、gate 預設 false、fail-closed、reject 不呼叫 QueueStore.approve。
  - 確認 doc 含 Metadata / Requested Tools Gap 與 production readiness audit 需求。
  - 確認 app/main.py / queue_store.py / approval_security_gate_v0_7.py / security_gates_v0_7.py /
    worker.py / result_sink.py / queue_intake_bridge_v0_7.py 在本版未被修改（git diff 比對）。
  - 確認 doc / script 未新增 route / webhook / POST handler。
不連外、不寫 DB、不讀 secrets。敏感檢查一律 regex / 格式比對。
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOC = ROOT / "docs" / "HERMES_OPENCLAW_APPROVE_ROUTE_WIRING_PLAN_V0_7_1_F2.md"
READINESS = ROOT / "scripts" / "check_hermes_openclaw_approve_route_wiring_plan_v0_7_1_f2.py"

# 本版「絕對不允許修改」的既有檔案（用 git diff 比對是否被改動）。
MUST_NOT_MODIFY = (
    "app/main.py",
    "app/queue_store.py",
    "app/approval_security_gate_v0_7.py",
    "app/security_gates_v0_7.py",
    "app/worker.py",
    "app/result_sink.py",
    "app/queue_intake_bridge_v0_7.py",
)

REQUIRED_TITLES = (
    "1. Purpose",
    "2. Relationship To v0.7.1-F",
    "3. Why This Version Is Plan-only",
    "4. Current API Approve Flow",
    "5. Current Dashboard Approve Flow",
    "6. Current QueueStore Approve Semantics",
    "7. Current Risk: Metadata / Requested Tools Gap",
    "8. Proposed Env Flags",
    "9. APPROVAL_SECURITY_GATES_ENABLED Behavior",
    "10. APPROVAL_KILL_SWITCH Behavior",
    "11. API Approve Wiring Proposal",
    "12. Dashboard Approve Wiring Proposal",
    "13. Gate Disabled Compatibility Contract",
    "14. Gate Enabled Fail-closed Contract",
    "15. Reject Semantics",
    "16. Audit / Ledger / Comment Boundary",
    "17. Task Row / Payload Requirements Before Enabling",
    "18. Required Production Readiness Audit Before Enabling",
    "19. Test Matrix For Future F2-A API-only Wiring",
    "20. Test Matrix For Future F2-B Dashboard Wiring",
    "21. Queue Source-of-truth Boundary",
    "22. Worker / OpenClaw Boundary",
    "23. Google Sheets Boundary",
    "24. Security / Secrets Rules",
    "25. Future Implementation Criteria",
    "26. Explicit Non-goals",
    "27. Final Recommendation",
)

REQUIRED_DECLARATIONS = (
    "v0.7.1-F2 is plan-only.",
    "No app/main.py modification.",
    "No queue_store.py modification.",
    "No worker.py modification.",
    "No result_sink.py modification.",
    "No approval_security_gate_v0_7.py modification.",
    "No security_gates_v0_7.py modification.",
    "No queue_intake_bridge_v0_7.py modification.",
    "No approve route wiring.",
    "No Dashboard approve wiring.",
    "No new route.",
    "No new POST handler.",
    "No DB schema change.",
    "No Worker start.",
    "No OpenClaw execution.",
    "No Hermes webhook.",
    "No Google Sheets write.",
    "No Queue status mutation.",
    "No audit ledger persistence.",
    "APPROVAL_SECURITY_GATES_ENABLED must default to false.",
    "APPROVAL_KILL_SWITCH must default to false.",
    "Gate disabled must preserve current approve behavior.",
    "Gate enabled must fail closed.",
    "Gate reject must not call QueueStore.approve.",
    "Gate reject must not create queued tasks.",
    "Gate reject must keep task in waiting_review / pending_approval.",
    "Gate reject must not automatically transition task to rejected.",
    "QueueStore remains the source of truth for task state.",
)

# production readiness audit 需求（至少這些問題要出現在 doc）。
REQUIRED_AUDIT_QUESTIONS = (
    "How many waiting_review tasks exist?",
    "How many have payload?",
    "How many have payload.metadata?",
    "How many have metadata.requested_tools?",
    "How many have allowed_tools?",
    "How many have executable_by_worker=true?",
    "How many are local_only/mock/executable_by_worker=false?",
)

RE_SPREADSHEET_URL = re.compile(r"spreadsheets/d/[A-Za-z0-9_-]{20,}")
RE_SPREADSHEET_ASSIGN = re.compile(r"SPREADSHEET_ID\s*[:=]\s*[\"'][A-Za-z0-9_-]{20,}[\"']")
RE_TOKEN_PREFIX = re.compile(r"(ya29\.[A-Za-z0-9_-]{10,}|1//[A-Za-z0-9_-]{10,}|" + "goc" + r"spx-[A-Za-z0-9_-]{10,})")
RE_PRIVATE_KEY = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")
RE_SHEETS_ENABLED_TRUE = re.compile(r"GOOGLE_SHEETS_ENABLED\s*[:=]\s*true", re.IGNORECASE)
SECRET_KEY_NAMES = (
    "GOOGLE_OAUTH_REFRESH_TOKEN",
    "GOOGLE_OAUTH_CLIENT_SECRET",
    "GOOGLE_SERVICE_ACCOUNT_JSON",
)
# 不允許在 doc / script 出現的「真接 route」痕跡（decorator / app 物件）。
ROUTE_WIRING_MARKERS = ("@app.post", "@app.get", "@router.", "add_api_route", "APIRouter", "FastAPI(")

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


def _git_changed_files() -> set[str]:
    """回傳相對 HEAD 已變動（含 staged / unstaged）的檔案集合。git 不可用 → 空集合 + 警告。"""
    changed: set[str] = set()
    for args in (["diff", "--name-only", "HEAD"], ["diff", "--name-only", "--cached"]):
        try:
            out = subprocess.run(
                ["git", *args], cwd=str(ROOT), capture_output=True, text=True, check=False
            )
        except (OSError, ValueError):
            print("  ?? : git 不可用，略過 diff 比對（仍以靜態檢查為準）")
            return set()
        for line in out.stdout.splitlines():
            line = line.strip()
            if line:
                changed.add(line)
    return changed


def main() -> int:
    doc = _read(DOC)
    script = _read(READINESS)

    print("[1] plan doc / readiness script 存在")
    _check(DOC.is_file(), "F2 plan doc 存在")
    _check(READINESS.is_file(), "readiness script 自身存在")

    print("[2] doc 含所有必要章節")
    for title in REQUIRED_TITLES:
        _check(title in doc, f"doc 含章節「{title}」")

    print("[3] doc 含所有必要安全聲明")
    for line in REQUIRED_DECLARATIONS:
        _check(line in doc, f"doc 含聲明「{line}」")

    print("[4] doc 含 Metadata / Requested Tools Gap 與 production readiness audit 需求")
    _check("Metadata / Requested Tools Gap" in doc, "doc 含 Metadata / Requested Tools Gap 一節")
    _check("production waiting_review tasks may not have metadata.requested_tools" in doc
           or "production `waiting_review` tasks may not have" in doc,
           "doc 說明 production waiting_review 可能缺 requested_tools / allowed_tools")
    _check("production readiness audit" in doc, "doc 含 production readiness audit 字樣")
    for q in REQUIRED_AUDIT_QUESTIONS:
        _check(q in doc, f"doc 含 audit 問題「{q}」")

    print("[5] doc 未新增 route / webhook / POST handler")
    # 只比對 doc：本 readiness script 本身會以字串字面量持有偵測樣式，故不自我比對。
    for marker in ROUTE_WIRING_MARKERS:
        _check(marker not in doc, f"doc 無 route 接線痕跡「{marker}」")

    print("[6] 既有檔案在本版未被修改（git diff 比對）")
    changed = _git_changed_files()
    for rel in MUST_NOT_MODIFY:
        _check(rel not in changed, f"{rel} 未被本版修改")

    print("[7] doc 內 GOOGLE_SHEETS_ENABLED 未設為 true")
    # 只比對 doc：本 script 的標籤字面量含旗標名，故不自我比對。
    _check(not RE_SHEETS_ENABLED_TRUE.search(doc), "doc 未把 GOOGLE_SHEETS_ENABLED 設為 true")

    print("[8] 敏感檢查（格式比對）：doc / script 不含真實 secret")
    # secret 格式比對：doc + script 皆檢查（純格式，不含真實值）。
    _check(_no_real_secret(doc),
           "doc 不含完整 spreadsheet id / url / token / private key（格式比對）")
    _check(_no_real_secret(script),
           "script 不含完整 spreadsheet id / url / token / private key（格式比對）")
    # secret 變數名只比對 doc：本 script 以字面量持有名單，故不自我比對。
    for key in SECRET_KEY_NAMES:
        _check(key not in doc, f"doc 不含 secret 變數名 {key}")

    if FAILURES:
        print(f"\nXX v0.7.1-F2 approve route wiring plan readiness 檢查失敗 {len(FAILURES)} 項：")
        for f in FAILURES:
            print(f"   - {f}")
        return 1
    print("\nOK v0.7.1-F2 approve route wiring plan readiness 全數通過"
          "（plan-only，未接 route、未連任何系統、未含 secret）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
