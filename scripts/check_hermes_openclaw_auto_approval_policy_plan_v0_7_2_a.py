#!/usr/bin/env python3
"""v0.7.2-A — Auto-Approval Policy / Safe Autopilot Plan 靜態 readiness（純檢查，不連任何系統）。

確認 v0.7.2-A 為 plan-only：
  - plan doc + 本 readiness 存在；doc 含所有必要章節與安全裁定。
  - doc 明寫 plan-only、不實作 auto-approval code、不接 route/intake、不改 QueueStore/Worker、
    禁止 dangerous skip-permissions、AUTO_APPROVAL_MODE 只支援 off|safe、預設全 off。
  - doc 含 Level 0–3、safe allowlists、protected files、forbidden ops、priority order、audit model、
    observation-only 與 queue/execution boundary。
  - 既有 app 功能檔 / templates / static / 既有 readiness 未被修改（git diff 比對）。
  - app/auto_approval_policy_v0_7.py 不存在；無新增 route / webhook / POST handler。
靜態檢查：不連外、不寫 DB、不讀 secrets。敏感檢查一律 regex / 格式比對。
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOC = ROOT / "docs" / "HERMES_OPENCLAW_AUTO_APPROVAL_POLICY_PLAN_V0_7_2_A.md"
READINESS = ROOT / "scripts" / "check_hermes_openclaw_auto_approval_policy_plan_v0_7_2_a.py"
HELPER_MUST_NOT_EXIST = ROOT / "app" / "auto_approval_policy_v0_7.py"

ALLOWED_NEW = {
    "docs/HERMES_OPENCLAW_AUTO_APPROVAL_POLICY_PLAN_V0_7_2_A.md",
    "scripts/check_hermes_openclaw_auto_approval_policy_plan_v0_7_2_a.py",
}

MUST_NOT_MODIFY = (
    "app/main.py",
    "app/queue_store.py",
    "app/worker.py",
    "app/result_sink.py",
    "app/approval_security_gate_v0_7.py",
    "app/security_gates_v0_7.py",
    "app/queue_intake_bridge_v0_7.py",
    "app/dashboard_intake_view_v0_7.py",
)

# 安全掃描範圍（app 功能檔不得 enable Sheets / 不得含真 secret）。
APP_SCAN_FILES = tuple(ROOT / m for m in MUST_NOT_MODIFY)

REQUIRED_TITLES = (
    "1. Purpose", "2. Relationship To v0.7.1-H", "3. Why This Version Is Plan-only",
    "4. Auto-Approval Is Not Skip-Permissions", "5. Design Principles",
    "6. Existing Reusable Gates", "7. Existing Reusable Metadata",
    "8. Existing Reusable Flags", "9. Proposed Env Flags", "10. AUTO_APPROVAL_MODE Behavior",
    "11. SAFE_AUTOPILOT_ENABLED Behavior", "12. LOW_RISK_AUTO_APPROVAL_ENABLED Behavior",
    "13. Level 0 Policy", "14. Level 1 Policy", "15. Level 2 Policy", "16. Level 3 Policy",
    "17. Safe task_type Allowlist", "18. Safe requested_tools Allowlist",
    "19. Protected Files Policy", "20. Forbidden Operations Policy",
    "21. Kill Switch Priority", "22. Denylist / Allowlist Priority", "23. Risk Level Policy",
    "24. requires_confirmation Policy", "25. executable_by_worker / local_only / mock Policy",
    "26. Audit Event Model", "27. Observation-only Boundary", "28. QueueStore Boundary",
    "29. Approval Route Boundary", "30. Worker / OpenClaw Boundary", "31. Hermes Boundary",
    "32. Google Sheets Boundary", "33. Secrets Boundary",
    "34. Future v0.7.2-B Pure Helper Criteria", "35. Future v0.7.2-C Local-only Simulation Criteria",
    "36. Future v0.7.2-D Intake Annotation Criteria", "37. Relationship To Future F2-A",
    "38. Explicit Non-goals", "39. Final Recommendation",
)

REQUIRED_STATEMENTS = (
    # plan-only / boundary
    "v0.7.2-A is plan-only.",
    "v0.7.2-A does not implement auto-approval code.",
    "v0.7.2-A does not add app/auto_approval_policy_v0_7.py.",
    "v0.7.2-A does not modify app/main.py.",
    "v0.7.2-A does not modify queue_store.py.",
    "v0.7.2-A does not modify worker.py.",
    "v0.7.2-A does not wire approve route.",
    "v0.7.2-A does not wire intake bridge.",
    "v0.7.2-A does not modify QueueStore state semantics.",
    "v0.7.2-A does not start Worker.",
    "v0.7.2-A does not call OpenClaw.",
    "v0.7.2-A does not call Hermes.",
    "v0.7.2-A does not write Google Sheets.",
    "v0.7.2-A does not create a v0.7 tag.",
    # dangerous skip-permissions 禁止
    "Auto-approval does not mean auto-execute everything.",
    "No dangerous skip-permissions mode is approved.",
    "No --dangerously-skip-permissions equivalent is approved.",
    "AUTO_APPROVAL_MODE must only support off | safe.",
    "dangerous, unrestricted, skip_permissions, and bypass modes are not allowed.",
    "Safe autopilot must be default-off.",
    "Low-risk tasks may be auto-approved only when all safety gates pass.",
    "High-risk tasks must still require Owner approval.",
    "must never be auto-approved.",
    # env flags
    "AUTO_APPROVAL_MODE=off | safe",
    "SAFE_AUTOPILOT_ENABLED=false",
    "LOW_RISK_AUTO_APPROVAL_ENABLED=false",
    "AUTO_APPROVAL_POLICY=safe",
    "AUTO_APPROVAL_KILL_SWITCH=false",
    "all flags default off",
    "unknown mode must fail closed / fallback to Owner approval",
    # queue / execution boundary
    "auto-approved does not mean queued.",
    "auto-approved does not mean Worker execution.",
    "auto-approved does not bypass approval_security_gate.",
    "auto-approved does not bypass security_gates.",
    "auto-approved does not write QueueStore in v0.7.2-A.",
    # observation-only / audit
    "v0.7.2-A does not persist audit events.",
    'action="auto_approval.policy_decision"',
    "observation_only=true",
    # no v0.7 tag
    "Do not create a v0.7 tag." if False else "does not create a v0.7 tag.",
)

# Level / allowlist / protected / forbidden / priority / roadmap 內容錨點。
REQUIRED_CONTENT = (
    "Level 0:", "Level 1:", "Level 2", "Level 3",
    "docs_only", "plan_only", "pure_helper_local",
    "read_file", "run_tests",
    "scripts/start_worker.sh",
    "set GOOGLE_SHEETS_ENABLED=true",  # forbidden-ops list 內容（負向，刻意列為禁止）
    "1. GLOBAL_KILL_SWITCH", "12. fallback to Owner approval",
    "auto_approved", "needs_owner_approval", "rejected", "prohibited",
    "app/auto_approval_policy_v0_7.py",  # roadmap 提及（B 才實作）
    "evaluate_auto_approval(",
)

RE_SPREADSHEET_URL = re.compile(r"spreadsheets/d/[A-Za-z0-9_-]{20,}")
RE_SPREADSHEET_ASSIGN = re.compile(r"SPREADSHEET_ID\s*[:=]\s*[\"'][A-Za-z0-9_-]{20,}[\"']")
RE_TOKEN_PREFIX = re.compile(r"(ya29\.[A-Za-z0-9_-]{10,}|1//[A-Za-z0-9_-]{10,}|" + "goc" + r"spx-[A-Za-z0-9_-]{10,})")
RE_PRIVATE_KEY = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")
RE_SHEETS_ENABLED_TRUE = re.compile(r"GOOGLE_SHEETS_ENABLED\s*[:=]\s*true", re.IGNORECASE)
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
    changed: set[str] = set()
    for args in (["diff", "--name-only", "HEAD"], ["diff", "--name-only", "--cached"]):
        try:
            out = subprocess.run(["git", *args], cwd=str(ROOT),
                                 capture_output=True, text=True, check=False)
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

    print("[1] plan doc / readiness script 存在")
    _check(DOC.is_file(), "v0.7.2-A plan doc 存在")
    _check(READINESS.is_file(), "readiness script 自身存在")

    print("[2] doc 含所有必要章節")
    for title in REQUIRED_TITLES:
        _check(title in doc, f"doc 含章節「{title}」")

    print("[3] doc 含所有 plan-only / safety 裁定")
    for stmt in REQUIRED_STATEMENTS:
        _check(stmt in doc, f"doc 含聲明「{stmt[:48]}…」")

    print("[4] doc 含 Level / allowlist / protected / forbidden / priority / audit 內容")
    for token in REQUIRED_CONTENT:
        _check(token in doc, f"doc 含內容「{token}」")

    print("[5] 既有 app / readiness 檔未被本版修改（git diff 比對）")
    changed = _git_changed_files()
    extra = sorted(changed - ALLOWED_NEW)
    _check(not extra, f"git diff 只含本版 2 個允許新增檔（多出：{extra}）")
    for rel in MUST_NOT_MODIFY:
        _check(rel not in changed, f"{rel} 未被本版修改")

    print("[6] auto-approval helper 尚未存在（plan-only）")
    _check(not HELPER_MUST_NOT_EXIST.is_file(), "app/auto_approval_policy_v0_7.py 不存在")

    print("[7] 無新增 route / webhook / POST handler（doc）")
    # 只比對 doc：本 readiness 以字面量持有偵測樣式，故不自我比對。
    for marker in ROUTE_WIRING_MARKERS:
        _check(marker not in doc, f"doc 無 route 接線痕跡「{marker}」")

    print("[8] safety：app 功能檔未 enable Sheets、不含真 secret")
    for path in APP_SCAN_FILES:
        rel = path.relative_to(ROOT).as_posix()
        txt = _read(path)
        _check(not RE_SHEETS_ENABLED_TRUE.search(txt), f"{rel} 未把 GOOGLE_SHEETS_ENABLED 設為 true")
        _check(_no_real_secret(txt), f"{rel} 不含完整 spreadsheet id/url/token/private key（格式比對）")

    print("[9] 敏感檢查（格式比對）：doc / readiness 不含真實 secret")
    _check(_no_real_secret(doc), "doc 不含完整 spreadsheet id / url / token / private key（格式比對）")
    _check(_no_real_secret(_read(READINESS)),
           "readiness 不含完整 spreadsheet id / url / token / private key（格式比對）")

    print("[10] 無 v0.7 tag")
    proc = subprocess.run(["git", "tag", "--list", "*0.7*"], cwd=str(ROOT),
                          capture_output=True, text=True, check=False)
    _check(proc.returncode == 0 and proc.stdout.strip() == "", "repo 無 v0.7 tag")

    if FAILURES:
        print(f"\nXX v0.7.2-A auto-approval policy plan readiness 失敗 {len(FAILURES)} 項：")
        for f in FAILURES:
            print(f"   - {f}")
        return 1
    print("\nOK v0.7.2-A auto-approval policy plan readiness 全數通過"
          "（plan-only；未實作 helper、未接線、未動 app、未 tag、未含 secret）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
