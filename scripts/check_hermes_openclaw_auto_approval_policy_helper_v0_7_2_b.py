#!/usr/bin/env python3
"""v0.7.2-B — Auto-Approval Policy pure helper 靜態 readiness（純檢查，不連任何系統）。

確認 helper 為純函式、observation-only、import 邊界正確、固定安全欄位，且未接任何系統：
  - helper 不 import main/queue_store/worker/result_sink/sqlite3/requests/subprocess/google/gspread/oauth。
  - helper 無 DB / route / webhook / approve / reject / claim_next / run_openclaw_cli 痕跡。
  - helper 固定 can_execute=False / queue_transition_allowed=False / observation_only=True。
  - doc 含必要章節與 closeout 邊界；test 覆蓋 Level 0–3 / kill switch / denylist / protected / forbidden 等。
  - 既有 app / templates / static / 既有 readiness 未被修改（git diff 比對）。
靜態檢查：不連外、不寫 DB、不讀 secrets。敏感檢查一律 regex / 格式比對。
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

HELPER = ROOT / "app" / "auto_approval_policy_v0_7.py"
DOC = ROOT / "docs" / "HERMES_OPENCLAW_AUTO_APPROVAL_POLICY_HELPER_V0_7_2_B.md"
TEST = ROOT / "scripts" / "test_auto_approval_policy_v0_7_2_b.py"
READINESS = ROOT / "scripts" / "check_hermes_openclaw_auto_approval_policy_helper_v0_7_2_b.py"

ALLOWED_NEW = {
    "app/auto_approval_policy_v0_7.py",
    "docs/HERMES_OPENCLAW_AUTO_APPROVAL_POLICY_HELPER_V0_7_2_B.md",
    "scripts/test_auto_approval_policy_v0_7_2_b.py",
    "scripts/check_hermes_openclaw_auto_approval_policy_helper_v0_7_2_b.py",
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

REQUIRED_TITLES = (
    "1. Purpose", "2. Relationship To v0.7.2-A", "3. Why Pure Helper First",
    "4. Helper API", "5. Return Schema", "6. Decision Enum",
    "7. can_auto_approve vs can_execute", "8. queue_transition_allowed Boundary",
    "9. observation_only Boundary", "10. Reused Pure Functions", "11. Import Boundary",
    "12. Level 0 Behavior", "13. Level 1 Behavior", "14. Level 2 Behavior",
    "15. Level 3 Behavior", "16. Safe task_type Allowlist", "17. Safe requested_tools Allowlist",
    "18. Protected Files", "19. Forbidden Operations", "20. Priority Order",
    "21. Kill Switch Behavior", "22. Denylist Overrides Allowlist", "23. Risk Level Behavior",
    "24. requires_confirmation Behavior", "25. touched_files / requested_operations Schema",
    "26. Audit Event Model", "27. QueueStore Boundary", "28. Approval Route Boundary",
    "29. Worker / OpenClaw Boundary", "30. Hermes Boundary", "31. Google Sheets Boundary",
    "32. Secrets Boundary", "33. Tests", "34. Readiness", "35. Explicit Non-goals",
    "36. Future v0.7.2-C", "37. Future v0.7.2-D", "38. Relationship To Future F2-A",
    "39. Final Recommendation",
)

REQUIRED_DOC_STATEMENTS = (
    "v0.7.2-B is pure-helper only.",
    "v0.7.2-B is observation-only.",
    "v0.7.2-B does not wire routes.",
    "v0.7.2-B does not write QueueStore.",
    "v0.7.2-B does not start Worker.",
    "v0.7.2-B does not call OpenClaw.",
    "v0.7.2-B does not call Hermes.",
    "v0.7.2-B does not write Google Sheets.",
    "v0.7.2-B does not read or display secrets.",
    "auto_approved does not mean queued.",
    "can_execute is always false.",
    "queue_transition_allowed is always false.",
    "observation_only is always true.",
    "No dangerous skip-permissions mode is approved.",
    "No --dangerously-skip-permissions equivalent is approved.",
)

# helper 必須含的固定安全欄位行為。
HELPER_REQUIRED = (
    "def evaluate_auto_approval",
    '"can_execute": False',
    '"queue_transition_allowed": False',
    '"observation_only": True',
)

# helper 不得出現的 import / 副作用 / dangerous 痕跡。
HELPER_FORBIDDEN_IMPORTS = ("app\\.main", "app\\.queue_store", "app\\.worker", "app\\.result_sink")
HELPER_FORBIDDEN_TOKENS = (
    "sqlite3", "import requests", "import subprocess", "subprocess.",
    ".execute(", ".commit(", "QueueStore", "get_queue", ".approve(", ".reject(",
    "claim_next", "run_openclaw_cli(",
    "@app.", "@router.", "add_api_route", "APIRouter", "FastAPI(",
    "skip_permissions", "dangerously-skip-permissions", "unrestricted", "bypass",
)
HELPER_GOOGLE_RE = re.compile(r"^\s*(?:import|from)\s+\S*(?:google|googleapiclient|gspread|oauthlib|oauth)",
                              re.MULTILINE | re.IGNORECASE)

# test 覆蓋錨點。
TEST_REQUIRED = (
    "Level0", "Level1", "Level2", "Level3",
    "GLOBAL_KILL_SWITCH", "AUTO_APPROVAL_KILL_SWITCH",
    "denied_tools", "protected file", "git_push",
    "requires_confirmation", "safety_level", "empty requested_tools",
    "unknown requested_tool", "未被 mutate", "can_execute", "queue_transition_allowed",
    "observation_only",
)

RE_SPREADSHEET_URL = re.compile(r"spreadsheets/d/[A-Za-z0-9_-]{20,}")
RE_SPREADSHEET_ASSIGN = re.compile(r"SPREADSHEET_ID\s*[:=]\s*[\"'][A-Za-z0-9_-]{20,}[\"']")
RE_TOKEN_PREFIX = re.compile(r"(ya29\.[A-Za-z0-9_-]{10,}|1//[A-Za-z0-9_-]{10,}|" + "goc" + r"spx-[A-Za-z0-9_-]{10,})")
RE_PRIVATE_KEY = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")

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
    helper = _read(HELPER)
    doc = _read(DOC)
    test = _read(TEST)

    print("[1] helper / doc / test / readiness 存在")
    _check(HELPER.is_file(), "app/auto_approval_policy_v0_7.py 存在")
    _check(DOC.is_file(), "B doc 存在")
    _check(TEST.is_file(), "B test 存在")
    _check(READINESS.is_file(), "B readiness 自身存在")

    print("[2] helper 公開 API / 固定安全欄位")
    for tok in HELPER_REQUIRED:
        _check(tok in helper, f"helper 含「{tok}」")

    print("[3] helper import 邊界（不 import main/queue_store/worker/result_sink/google）")
    for mod in HELPER_FORBIDDEN_IMPORTS:
        imp_re = re.compile(rf"^\s*(?:import|from)\s+\S*{mod}\b", re.MULTILINE)
        _check(not imp_re.search(helper), f"helper 未 import {mod.replace(chr(92), '')}")
    _check(not HELPER_GOOGLE_RE.search(helper), "helper 未 import google / oauth client")

    print("[4] helper 無 DB / route / webhook / 狀態轉換 / dangerous 痕跡")
    for tok in HELPER_FORBIDDEN_TOKENS:
        _check(tok not in helper, f"helper 無痕跡「{tok}」")

    print("[5] doc 含所有必要章節")
    for title in REQUIRED_TITLES:
        _check(title in doc, f"doc 含章節「{title}」")

    print("[6] doc 含 pure-helper / observation-only / boundary 聲明")
    for stmt in REQUIRED_DOC_STATEMENTS:
        _check(stmt in doc, f"doc 含聲明「{stmt[:46]}…」")

    print("[7] test 覆蓋 Level 0–3 / kill switch / denylist / protected / forbidden 等")
    for tok in TEST_REQUIRED:
        _check(tok in test, f"test 覆蓋「{tok}」")

    print("[8] 既有 app / readiness 檔未被本版修改（git diff 比對）")
    changed = _git_changed_files()
    extra = sorted(changed - ALLOWED_NEW)
    _check(not extra, f"git diff 只含本版 4 個允許新增檔（多出：{extra}）")
    for rel in MUST_NOT_MODIFY:
        _check(rel not in changed, f"{rel} 未被本版修改")

    print("[9] 敏感檢查（格式比對）：helper / doc / test 不含真實 secret")
    for name, text in (("helper", helper), ("doc", doc), ("test", test)):
        _check(_no_real_secret(text),
               f"{name} 不含完整 spreadsheet id / url / token / private key（格式比對）")

    if FAILURES:
        print(f"\nXX v0.7.2-B auto-approval policy helper readiness 失敗 {len(FAILURES)} 項：")
        for f in FAILURES:
            print(f"   - {f}")
        return 1
    print("\nOK v0.7.2-B auto-approval policy helper readiness 全數通過"
          "（pure / observation-only / 未接線 / 未動 app / 未含 secret）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
