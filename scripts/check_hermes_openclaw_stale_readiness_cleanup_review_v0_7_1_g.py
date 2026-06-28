#!/usr/bin/env python3
"""v0.7.1-G — Stale Readiness Cleanup Review 靜態 readiness（純檢查，不連任何系統）。

確認 v0.7.1-G 只做 additive 清理政策：
  - G doc + current-state aggregator + 本 readiness 三檔存在且符合政策。
  - G doc 明寫不改/不刪 stale readiness、A/C/C2/D 為 expected stale、aggregator 為 regression gate。
  - aggregator 含 EXPECTED_STALE_READINESS（含 A/C/C2/D）、檢查 B/C3/D2/E/F/F2、檢查 C3 wiring、
    檢查 approval gate 尚未接入 main/queue_store/worker、檢查 GOOGLE_SHEETS_ENABLED 非 true。
  - 既有 app / readiness / template 檔在本版未被修改（git diff 比對）。
靜態檢查：不連外、不寫 DB、不讀 secrets。敏感檢查一律 regex / 格式比對。
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOC = ROOT / "docs" / "HERMES_OPENCLAW_STALE_READINESS_CLEANUP_REVIEW_V0_7_1_G.md"
AGG = ROOT / "scripts" / "check_hermes_openclaw_v0_7_1_current_state.py"
READINESS = ROOT / "scripts" / "check_hermes_openclaw_stale_readiness_cleanup_review_v0_7_1_g.py"

# 本版唯一允許新增的檔案（git diff 只能出現這 3 個）。
ALLOWED_NEW = {
    "docs/HERMES_OPENCLAW_STALE_READINESS_CLEANUP_REVIEW_V0_7_1_G.md",
    "scripts/check_hermes_openclaw_v0_7_1_current_state.py",
    "scripts/check_hermes_openclaw_stale_readiness_cleanup_review_v0_7_1_g.py",
}

# 絕對不可被修改的既有功能檔（額外明確比對）。
MUST_NOT_MODIFY = (
    "app/main.py",
    "app/queue_store.py",
    "app/worker.py",
    "app/result_sink.py",
    "app/queue_intake_bridge_v0_7.py",
    "app/security_gates_v0_7.py",
    "app/approval_security_gate_v0_7.py",
    "app/dashboard_intake_view_v0_7.py",
    "scripts/check_hermes_openclaw_controlled_queue_intake_plan_v0_7_1_a.py",
    "scripts/check_hermes_openclaw_dashboard_intake_status_view_model_v0_7_1_c_readiness.py",
    "scripts/check_hermes_openclaw_web_dashboard_read_only_status_badges_plan_v0_7_1_c2.py",
    "scripts/check_hermes_openclaw_kill_switch_audit_allowlist_plan_v0_7_1_d.py",
)

REQUIRED_TITLES = (
    "1. Purpose", "2. Current Master State", "3. Why Stale Readiness Exists",
    "4. Readiness Execution Matrix", "5. Green Readiness Checks",
    "6. Expected-Stale Readiness Checks", "7. Why A Is Expected Stale",
    "8. Why C Is Expected Stale", "9. Why C2 Is Expected Stale",
    "10. Why D Is Expected Stale", "11. Historical Snapshot Policy",
    "12. Current-State Aggregator Policy", "13. Expected-Stale Allowlist",
    "14. Current-State Truths", "15. What The Aggregator Checks",
    "16. What The Aggregator Does Not Check", "17. Relationship To v0.7.1-F2",
    "18. Future Maintenance Rules", "19. Safety Boundaries",
    "20. Security / Secrets Rules", "21. Explicit Non-goals", "22. Final Recommendation",
)

REQUIRED_DOC_STATEMENTS = (
    "v0.7.1-G does not modify stale readiness scripts.",
    "v0.7.1-G does not delete historical readiness scripts.",
    "A / C / C2 / D are expected stale because later implementation versions "
    "intentionally superseded their negative assertions.",
    "Current-state aggregator is the regression gate for current master.",
    "Historical readiness scripts are preserved as version-time audit snapshots.",
    "Do not require stale plan-only readiness scripts to be green in current-state "
    "regression.",
    "No app/main.py modification.",
    "No queue_store.py modification.",
    "No worker.py modification.",
    "No result_sink.py modification.",
    "No queue_intake_bridge_v0_7.py modification.",
    "No security_gates_v0_7.py modification.",
    "No approval_security_gate_v0_7.py modification.",
    "No dashboard_intake_view_v0_7.py modification.",
    "No templates modification.",
    "No static modification.",
    "No route wiring.",
    "No new route.",
    "No new POST handler.",
    "No DB schema change.",
    "No Worker start.",
    "No OpenClaw execution.",
    "No Hermes webhook.",
    "No Google Sheets write.",
    "No Queue status mutation.",
)

# aggregator 必須包含的 readiness 檔名（代表它會檢查 B/C3/D2/E/F/F2）。
AGG_GREEN_READINESS_FILES = (
    "check_hermes_openclaw_local_only_queue_intake_bridge_v0_7_1_b_readiness.py",
    "check_hermes_openclaw_web_dashboard_read_only_status_badges_v0_7_1_c3_readiness.py",
    "check_hermes_openclaw_local_only_security_gates_v0_7_1_d2_readiness.py",
    "check_hermes_openclaw_local_only_intake_security_gates_v0_7_1_e_readiness.py",
    "check_hermes_openclaw_approval_to_queued_security_gate_v0_7_1_f_readiness.py",
    "check_hermes_openclaw_approve_route_wiring_plan_v0_7_1_f2.py",
)

RE_SPREADSHEET_URL = re.compile(r"spreadsheets/d/[A-Za-z0-9_-]{20,}")
RE_SPREADSHEET_ASSIGN = re.compile(r"SPREADSHEET_ID\s*[:=]\s*[\"'][A-Za-z0-9_-]{20,}[\"']")
RE_TOKEN_PREFIX = re.compile(r"(ya29\.[A-Za-z0-9_-]{10,}|1//[A-Za-z0-9_-]{10,}|" + "goc" + r"spx-[A-Za-z0-9_-]{10,})")
RE_PRIVATE_KEY = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")
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
    agg = _read(AGG)

    print("[1] G doc / aggregator / G readiness 存在")
    _check(DOC.is_file(), "G doc 存在")
    _check(AGG.is_file(), "current-state aggregator 存在")
    _check(READINESS.is_file(), "G readiness script 自身存在")

    print("[2] G doc 含所有必要章節")
    for title in REQUIRED_TITLES:
        _check(title in doc, f"G doc 含章節「{title}」")

    print("[3] G doc 含政策與邊界聲明")
    for stmt in REQUIRED_DOC_STATEMENTS:
        _check(stmt in doc, f"G doc 含聲明「{stmt[:48]}…」")

    print("[4] aggregator 含 expected-stale allowlist（A/C/C2/D）")
    _check("EXPECTED_STALE_READINESS" in agg, "aggregator 含 EXPECTED_STALE_READINESS")
    for ver in ("v0.7.1-A", "v0.7.1-C", "v0.7.1-C2", "v0.7.1-D"):
        _check(f'"{ver}"' in agg, f"aggregator allowlist 含 {ver}")

    print("[5] aggregator 檢查 green readiness（B/C3/D2/E/F/F2）")
    for fn in AGG_GREEN_READINESS_FILES:
        _check(fn in agg, f"aggregator 引用 {fn}")

    print("[6] aggregator 檢查 current-state truths / boundary")
    _check("dashboard_intake_view_v0_7" in agg, "aggregator 檢查 main.py 含 C3 wiring（dashboard_intake_view_v0_7）")
    _check("derive_intake_status_view" in agg, "aggregator 檢查 main.py 含 C3 wiring（derive_intake_status_view）")
    _check("尚未 import" in agg, "aggregator 檢查 approval gate 尚未 import")
    _check("queue_store.py" in agg, "aggregator 檢查 queue_store.py boundary")
    _check("worker.py" in agg, "aggregator 檢查 worker.py boundary")
    _check("GOOGLE_SHEETS_ENABLED" in agg, "aggregator 檢查 GOOGLE_SHEETS_ENABLED 非 true")

    print("[7] 既有 app / readiness / template 檔未被本版修改（git diff 比對）")
    changed = _git_changed_files()
    extra = sorted(changed - ALLOWED_NEW)
    _check(not extra, f"git diff 只含本版 3 個允許新增檔（多出：{extra}）")
    for rel in MUST_NOT_MODIFY:
        _check(rel not in changed, f"{rel} 未被本版修改")

    print("[8] 無新增 route / webhook / POST handler（doc + aggregator）")
    # 只比對 doc + aggregator；本 G readiness 以字面量持有偵測樣式，故不自我比對。
    for marker in ROUTE_WIRING_MARKERS:
        _check(marker not in doc, f"doc 無 route 接線痕跡「{marker}」")
        _check(marker not in agg, f"aggregator 無 route 接線痕跡「{marker}」")

    print("[9] 敏感檢查（格式比對）：doc / aggregator / G readiness 不含真實 secret")
    for name, text in (("doc", doc), ("aggregator", agg), ("G readiness", _read(READINESS))):
        _check(_no_real_secret(text),
               f"{name} 不含完整 spreadsheet id / url / token / private key（格式比對）")

    if FAILURES:
        print(f"\nXX v0.7.1-G stale readiness cleanup review readiness 失敗 {len(FAILURES)} 項：")
        for f in FAILURES:
            print(f"   - {f}")
        return 1
    print("\nOK v0.7.1-G stale readiness cleanup review readiness 全數通過"
          "（additive；未改/未刪 stale readiness、未動 app、未含 secret）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
