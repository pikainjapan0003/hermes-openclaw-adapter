#!/usr/bin/env python3
"""v0.7.2-C — Auto-Approval Local-only Simulation 靜態 readiness（純檢查，不連任何系統）。

確認 v0.7.2-C 只新增「local-only 模擬器」且零副作用：
  - 4 個 C 檔存在；simulation 只 import evaluate_auto_approval，未 import
    main/queue_store/worker/result_sink/sqlite3/requests/subprocess/google/gspread/oauth；
    無 QueueStore/approve/reject/claim_next/run_openclaw_cli/route/webhook/DB-write/network 痕跡；
    無 dangerous skip-permissions 模式。
  - simulation sample tasks 覆蓋 Level 0–3 + edge；test 覆蓋 samples / --json / 固定安全旗標 /
    default-off / no-mutation；doc 含必要章節與 boundary 聲明。
  - B readiness / B2 readiness / current-state 仍 green（subprocess EXIT=0）。
  - git-diff allowlist：本版只允許新增這 4 個 C 檔，未修改任何既有檔。
  - 無真 secret、無 Sheets live enable。
靜態檢查：不連外、不寫 DB、不讀 secrets。敏感檢查一律 regex / 格式比對。
（註：本 readiness 自身使用 subprocess 重跑 green gate；對 simulation 的 subprocess 禁令僅針對
  simulation script，不針對 readiness。）
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOC = ROOT / "docs" / "HERMES_OPENCLAW_AUTO_APPROVAL_LOCAL_ONLY_SIMULATION_V0_7_2_C.md"
SIM = ROOT / "scripts" / "simulate_auto_approval_policy_v0_7_2_c.py"
TEST = ROOT / "scripts" / "test_auto_approval_local_only_simulation_v0_7_2_c.py"
READINESS = ROOT / "scripts" / "check_hermes_openclaw_auto_approval_local_only_simulation_v0_7_2_c.py"

# 本版只允許「新增」這 4 個檔（不允許修改任何既有檔）。
ALLOWED_NEW = {
    "docs/HERMES_OPENCLAW_AUTO_APPROVAL_LOCAL_ONLY_SIMULATION_V0_7_2_C.md",
    "scripts/simulate_auto_approval_policy_v0_7_2_c.py",
    "scripts/test_auto_approval_local_only_simulation_v0_7_2_c.py",
    "scripts/check_hermes_openclaw_auto_approval_local_only_simulation_v0_7_2_c.py",
}

MUST_NOT_MODIFY = (
    "app/auto_approval_policy_v0_7.py",
    "app/main.py",
    "app/queue_store.py",
    "app/worker.py",
    "app/result_sink.py",
    "app/approval_security_gate_v0_7.py",
    "app/security_gates_v0_7.py",
    "app/queue_intake_bridge_v0_7.py",
    "app/dashboard_intake_view_v0_7.py",
    "scripts/check_hermes_openclaw_v0_7_1_current_state.py",
    "scripts/check_hermes_openclaw_auto_approval_policy_helper_v0_7_2_b.py",
    "scripts/test_auto_approval_policy_v0_7_2_b.py",
    "scripts/check_hermes_openclaw_auto_approval_expected_stale_readiness_update_v0_7_2_b2.py",
    "scripts/check_hermes_openclaw_auto_approval_policy_plan_v0_7_2_a.py",
)

# 必須仍 green 的 gate（subprocess returncode==0；returncode 可靠，不受 shell $? 影響）。
GREEN_GATES = (
    ("B readiness", "scripts/check_hermes_openclaw_auto_approval_policy_helper_v0_7_2_b.py"),
    ("B2 readiness", "scripts/check_hermes_openclaw_auto_approval_expected_stale_readiness_update_v0_7_2_b2.py"),
    ("current-state", "scripts/check_hermes_openclaw_v0_7_1_current_state.py"),
)

REQUIRED_TITLES = (
    "1. Purpose", "2. Relationship To v0.7.2-B", "3. Relationship To v0.7.2-B2",
    "4. Why Local-only Simulation", "5. Simulation Is Not Execution", "6. CLI Interface",
    "7. Safe Autopilot Simulation Profile", "8. Default-off Profile Behavior",
    "9. Sample Task Catalog", "10. Level 0 Samples", "11. Level 1 Samples",
    "12. Level 2 Samples", "13. Level 3 Samples", "14. Edge Case Samples",
    "15. JSON Output Schema", "16. Summary Counts", "17. can_execute Boundary",
    "18. queue_transition_allowed Boundary", "19. observation_only Boundary",
    "20. QueueStore Boundary", "21. Route Boundary", "22. Worker / OpenClaw Boundary",
    "23. Hermes Boundary", "24. Google Sheets Boundary", "25. Secrets Boundary",
    "26. No Network / No Subprocess Boundary", "27. Tests", "28. Readiness",
    "29. Current-State Aggregator Future Update", "30. Future v0.7.2-D",
    "31. Explicit Non-goals", "32. Final Recommendation",
)

REQUIRED_STATEMENTS = (
    "v0.7.2-C is local-only simulation.",
    "v0.7.2-C does not read real Queue DB.",
    "v0.7.2-C does not read production task data.",
    "v0.7.2-C does not write QueueStore.",
    "v0.7.2-C does not modify Queue status.",
    "v0.7.2-C does not wire routes.",
    "v0.7.2-C does not wire intake bridge.",
    "v0.7.2-C does not wire approve route.",
    "v0.7.2-C does not start Worker.",
    "v0.7.2-C does not call OpenClaw.",
    "v0.7.2-C does not call Hermes.",
    "v0.7.2-C does not write Google Sheets.",
    "v0.7.2-C does not read or display secrets.",
    "v0.7.2-C does not use network.",
    "v0.7.2-C does not use subprocess.",
    "Simulation does not mean execution.",
    "Decision preview does not mean queued.",
    "can_execute is always false.",
    "queue_transition_allowed is always false.",
    "observation_only is always true.",
)

# simulation script 必含（公開 API / profile / sample 覆蓋 / 固定欄位）。
SIM_REQUIRED = (
    "evaluate_auto_approval", "SAFE_AUTOPILOT_PROFILE", "DEFAULT_OFF_PROFILE",
    "build_samples", "summarize",
    '"can_execute"', '"queue_transition_allowed"', '"observation_only"',
    "level0_", "level1_", "level2_", "level3_",
    "kill_switch_global", "kill_switch_auto_approval", "task_row_not_dict",
    "unknown_task_type",
)

# simulation 不得 import 的模組（import-line regex；避免誤判 docstring 散文）。
SIM_FORBIDDEN_IMPORTS = (
    r"app\.main", r"app\.queue_store", r"app\.worker", r"app\.result_sink",
    r"sqlite3", r"requests", r"subprocess", r"socket", r"urllib", r"httpx", r"http\.client",
    r"google", r"googleapiclient", r"gspread", r"oauth",
)

# simulation 不得出現的接線 / DB-write / dangerous 痕跡（純子字串）。
SIM_FORBIDDEN_TOKENS = (
    "QueueStore", "get_queue", ".approve(", ".reject(", "claim_next", "run_openclaw_cli(",
    "@app.", "@router.", "add_api_route", "APIRouter", "FastAPI(",
    "subprocess.", ".execute(", ".commit(", "INSERT INTO", "DELETE FROM",
    "skip_permissions", "dangerously-skip-permissions", "unrestricted", "bypass",
)

# test 覆蓋錨點。
TEST_REQUIRED = (
    "build_samples", "--json", "can_execute", "queue_transition_allowed", "observation_only",
    "default-off", "safe", "input_unchanged", "evaluate_auto_approval",
    "rejected", "prohibited", "needs_owner_approval", "auto_approved",
)

RE_SPREADSHEET_URL = re.compile(r"spreadsheets/d/[A-Za-z0-9_-]{20,}")
RE_SPREADSHEET_ASSIGN = re.compile(r"SPREADSHEET_ID\s*[:=]\s*[\"'][A-Za-z0-9_-]{20,}[\"']")
RE_TOKEN_PREFIX = re.compile(r"(ya29\.[A-Za-z0-9_-]{10,}|1//[A-Za-z0-9_-]{10,}|" + "goc" + r"spx-[A-Za-z0-9_-]{10,})")
RE_PRIVATE_KEY = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")
RE_SHEETS_ENABLED_TRUE = re.compile(r"GOOGLE_SHEETS_ENABLED\s*[:=]\s*true", re.IGNORECASE)
# 真實 secret 變數賦值（排除 redaction key 清單 / forbidden-list 純字串）。
RE_SECRET_ASSIGN = re.compile(r"(refresh_token|client_secret|private_key)\s*[:=]\s*[\"'][^\"']{8,}[\"']",
                              re.IGNORECASE)
ROUTE_MARKERS = ("@app.post", "@app.get", "@app.put", "@router.", "add_api_route", "APIRouter", "FastAPI(")

FAILURES: list[str] = []


def _check(cond: bool, label: str) -> None:
    print(f"  {'ok ' if cond else 'XX '}: {label}")
    if not cond:
        FAILURES.append(label)


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.is_file() else ""


def _no_real_secret(text: str) -> bool:
    return not (RE_SPREADSHEET_URL.search(text) or RE_SPREADSHEET_ASSIGN.search(text)
                or RE_TOKEN_PREFIX.search(text) or RE_PRIVATE_KEY.search(text)
                or RE_SECRET_ASSIGN.search(text))


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


def _git_untracked_files() -> set[str]:
    try:
        out = subprocess.run(["git", "status", "--porcelain"], cwd=str(ROOT),
                             capture_output=True, text=True, check=False)
    except (OSError, ValueError):
        return set()
    untracked: set[str] = set()
    for line in out.stdout.splitlines():
        if line.startswith("?? "):
            path = line[3:].strip()
            if "__pycache__" in path or path.endswith(".pyc"):
                continue
            untracked.add(path)
    return untracked


def main() -> int:
    sim = _read(SIM)
    test = _read(TEST)
    doc = _read(DOC)

    print("[1] 4 個 C 檔存在")
    _check(DOC.is_file(), "C doc 存在")
    _check(SIM.is_file(), "simulation script 存在")
    _check(TEST.is_file(), "C test 存在")
    _check(READINESS.is_file(), "C readiness 自身存在")

    print("[2] simulation 公開 API / profile / sample 覆蓋 / 固定欄位")
    for tok in SIM_REQUIRED:
        _check(tok in sim, f"simulation 含「{tok}」")

    print("[3] simulation import 邊界（只 import evaluate_auto_approval）")
    _check(re.search(r"^\s*from\s+app\.auto_approval_policy_v0_7\s+import\s+.*evaluate_auto_approval",
                     sim, re.MULTILINE) is not None, "simulation import evaluate_auto_approval")
    for mod in SIM_FORBIDDEN_IMPORTS:
        imp = re.compile(rf"^\s*(?:import|from)\s+\S*{mod}\b", re.MULTILINE | re.IGNORECASE)
        _check(imp.search(sim) is None, f"simulation 未 import {mod}")

    print("[4] simulation 無接線 / DB-write / network / dangerous 痕跡")
    for tok in SIM_FORBIDDEN_TOKENS:
        _check(tok not in sim, f"simulation 無痕跡「{tok}」")
    sim_google = re.compile(r"^\s*(?:import|from)\s+\S*(?:google|gspread|oauthlib|oauth)",
                            re.MULTILINE | re.IGNORECASE)
    _check(sim_google.search(sim) is None, "simulation 未 import google / gspread / oauth client")
    for marker in ROUTE_MARKERS:
        _check(marker not in sim, f"simulation 無 route/webhook 痕跡「{marker}」")
    _check(not RE_SHEETS_ENABLED_TRUE.search(sim), "simulation 未把 GOOGLE_SHEETS_ENABLED 設為 true")

    print("[5] test 覆蓋錨點")
    for tok in TEST_REQUIRED:
        _check(tok in test, f"test 覆蓋「{tok}」")

    print("[6] doc 含所有必要章節")
    for title in REQUIRED_TITLES:
        _check(title in doc, f"doc 含章節「{title}」")

    print("[7] doc 含所有 boundary 聲明")
    for stmt in REQUIRED_STATEMENTS:
        _check(stmt in doc, f"doc 含聲明「{stmt[:46]}…」")

    print("[8] B / B2 / current-state 仍 green（subprocess EXIT=0）")
    for tag, rel in GREEN_GATES:
        path = ROOT / rel
        if not path.is_file():
            _check(False, f"{tag} 檔存在（{rel}）")
            continue
        proc = subprocess.run([sys.executable, str(path)], cwd=str(ROOT),
                              capture_output=True, text=True, check=False)
        _check(proc.returncode == 0, f"{tag} EXIT=0（{rel}）")

    print("[9] git-diff allowlist：本版只新增 4 個 C 檔，未改既有檔")
    changed = _git_changed_files()
    extra = sorted(changed - ALLOWED_NEW)
    _check(not extra, f"git diff 未含非本版修改（多出：{extra}）")
    for rel in MUST_NOT_MODIFY:
        _check(rel not in changed, f"{rel} 未被本版修改")
    untracked = _git_untracked_files()
    extra_untracked = sorted(untracked - ALLOWED_NEW)
    _check(not extra_untracked, f"未追蹤新檔僅本版 4 檔（多出：{extra_untracked}）")

    print("[10] 敏感檢查（格式比對）：sim / test / doc / readiness 不含真 secret")
    for name, text in (("sim", sim), ("test", test), ("doc", doc), ("readiness", _read(READINESS))):
        _check(_no_real_secret(text),
               f"{name} 不含完整 spreadsheet id / url / token / private key（格式比對）")

    if FAILURES:
        print(f"\nXX v0.7.2-C local-only simulation readiness 失敗 {len(FAILURES)} 項：")
        for f in FAILURES:
            print(f"   - {f}")
        return 1
    print("\nOK v0.7.2-C auto-approval local-only simulation readiness 全數通過"
          "（只新增 4 檔 / 零副作用 / 未接線 / B·B2·current-state 仍 green / 未含 secret）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
