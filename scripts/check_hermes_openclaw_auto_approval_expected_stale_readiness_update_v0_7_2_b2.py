#!/usr/bin/env python3
"""v0.7.2-B2 — Auto-Approval Expected-Stale Readiness Update 靜態 readiness（純檢查，不連任何系統）。

確認 B2 只做回歸/政策更新：
  - current-state aggregator 已把 v0.7.2-A 列入 EXPECTED_STALE_READINESS，並加入 v0.7.2-B green gates
    與 auto-approval helper 的正向/邊界斷言。
  - B2 doc 含必要章節與裁定；v0.7.2-A / B helper / B readiness / B test / app 功能檔 / templates / static
    未被本版修改（git diff 比對）。
靜態檢查：不連外、不寫 DB、不讀 secrets。敏感檢查一律 regex / 格式比對。
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOC = ROOT / "docs" / "HERMES_OPENCLAW_AUTO_APPROVAL_EXPECTED_STALE_READINESS_UPDATE_V0_7_2_B2.md"
READINESS = ROOT / "scripts" / "check_hermes_openclaw_auto_approval_expected_stale_readiness_update_v0_7_2_b2.py"
AGG = ROOT / "scripts" / "check_hermes_openclaw_v0_7_1_current_state.py"

# 本版唯一允許「修改」的既有檔。
ALLOWED_MODIFY = {"scripts/check_hermes_openclaw_v0_7_1_current_state.py"}
# 本版允許「新增」的檔。
ALLOWED_NEW = {
    "docs/HERMES_OPENCLAW_AUTO_APPROVAL_EXPECTED_STALE_READINESS_UPDATE_V0_7_2_B2.md",
    "scripts/check_hermes_openclaw_auto_approval_expected_stale_readiness_update_v0_7_2_b2.py",
}

# 絕對不可被本版修改的既有檔。
MUST_NOT_MODIFY = (
    "scripts/check_hermes_openclaw_auto_approval_policy_plan_v0_7_2_a.py",
    "scripts/check_hermes_openclaw_auto_approval_policy_helper_v0_7_2_b.py",
    "scripts/test_auto_approval_policy_v0_7_2_b.py",
    "app/auto_approval_policy_v0_7.py",
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
    "1. Purpose", "2. Context", "3. Why v0.7.2-A Readiness Became Stale",
    "4. Expected-Stale Classification", "5. Relationship To v0.7.2-A",
    "6. Relationship To v0.7.2-B", "7. Current-State Aggregator Update",
    "8. New Green Gates", "9. Positive Current-State Assertions",
    "10. Historical Snapshot Policy", "11. Why Not Modify v0.7.2-A Readiness",
    "12. Why Not Modify v0.7.2-B Readiness", "13. Safety Boundary", "14. No Route Wiring",
    "15. No QueueStore Mutation", "16. No Worker Execution", "17. No OpenClaw / Hermes Calls",
    "18. No Google Sheets Live Write", "19. No Secrets Access", "20. No v0.7 Tag",
    "21. Future Maintenance Rule", "22. Final Recommendation",
)

REQUIRED_DOC_STATEMENTS = (
    "v0.7.2-A readiness is expected-stale after v0.7.2-B.",
    "The only stale reason is app/auto_approval_policy_v0_7.py now exists.",
    "v0.7.2-A readiness remains a historical snapshot and must not be rewritten.",
    "v0.7.2-B helper readiness and test are now current green gates.",
    "current-state aggregator is the source of truth for current health.",
    "B2 does not add features.",
    "B2 does not modify auto_approval_policy_v0_7.py.",
    "B2 does not modify A readiness.",
    "B2 does not modify B readiness.",
    "B2 does not wire routes.",
    "B2 does not wire QueueStore.",
    "B2 does not start Worker.",
    "B2 does not call OpenClaw.",
    "B2 does not call Hermes.",
    "B2 does not write Google Sheets.",
    "B2 does not read secrets.",
    "B2 does not create tag.",
)

# aggregator 必須包含的更新內容。
AGG_REQUIRED = (
    '"v0.7.2-A"',
    "superseded by v0.7.2-B auto_approval_policy_v0_7.py pure helper",
    "check_hermes_openclaw_auto_approval_policy_helper_v0_7_2_b.py",
    "test_auto_approval_policy_v0_7_2_b.py",
    "app/auto_approval_policy_v0_7.py",
    "evaluate_auto_approval",
    '"can_execute": False',
    '"queue_transition_allowed": False',
    '"observation_only": True',
    "aa_imp",  # auto-approval helper 未被接入的 boundary 檢查
    "auto-approval helper 尚未被 main/queue_store/worker/result_sink 接入",
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
    doc = _read(DOC)
    agg = _read(AGG)

    print("[1] B2 doc / B2 readiness / aggregator 存在")
    _check(DOC.is_file(), "B2 doc 存在")
    _check(READINESS.is_file(), "B2 readiness 自身存在")
    _check(AGG.is_file(), "current-state aggregator 存在")

    print("[2] aggregator 已更新（expected-stale + green gates + 正向/邊界斷言）")
    for tok in AGG_REQUIRED:
        _check(tok in agg, f"aggregator 含「{tok}」")

    print("[3] B2 doc 含所有必要章節")
    for title in REQUIRED_TITLES:
        _check(title in doc, f"B2 doc 含章節「{title}」")

    print("[4] B2 doc 含所有裁定 / 邊界聲明")
    for stmt in REQUIRED_DOC_STATEMENTS:
        _check(stmt in doc, f"B2 doc 含聲明「{stmt[:46]}…」")

    print("[5] 本版只改允許檔（git diff 比對；A readiness / B helper / B readiness / B test / app 不變）")
    changed = _git_changed_files()
    extra = sorted(changed - ALLOWED_MODIFY - ALLOWED_NEW)
    _check(not extra, f"git diff 只含本版允許檔（多出：{extra}）")
    for rel in MUST_NOT_MODIFY:
        _check(rel not in changed, f"{rel} 未被本版修改")

    print("[6] 敏感檢查（格式比對）：doc / readiness / aggregator 不含真實 secret")
    for name, text in (("doc", doc), ("readiness", _read(READINESS)), ("aggregator", agg)):
        _check(_no_real_secret(text),
               f"{name} 不含完整 spreadsheet id / url / token / private key（格式比對）")

    if FAILURES:
        print(f"\nXX v0.7.2-B2 expected-stale readiness update 失敗 {len(FAILURES)} 項：")
        for f in FAILURES:
            print(f"   - {f}")
        return 1
    print("\nOK v0.7.2-B2 expected-stale readiness update 全數通過"
          "（只更新 aggregator + 新增 doc/readiness；未改 A/B readiness、未動 app、未含 secret）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
