#!/usr/bin/env python3
"""v0.7.1 current-state regression aggregator — 當前 master 的回歸真相檢查（不連任何系統）。

本 script 是 v0.7.1-F2 之後 master 的「current-state regression gate」：
  - 用正向斷言檢查「目前 master 應該長什麼樣」（artifacts / 接線 / 邊界 / 安全）。
  - 以 subprocess 重跑目前 green 的 readiness（B/C3/D2/E/F/F2）並要求 EXIT=0。
  - **不**把 stale plan-only readiness（A/C/C2/D）當 hard gate；只列印 expected-stale allowlist。
靜態檢查：不連外、不寫 DB、不改狀態、不讀 secrets。敏感檢查一律 regex / 格式比對。
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# ---- expected-stale allowlist：這些早期 plan-only readiness 在 current master 為「預期紅」----
# 不執行、也不要求它們 green；保留為版本時刻 audit snapshot。
EXPECTED_STALE_READINESS = {
    "v0.7.1-A": "superseded by v0.7.1-B queue_intake_bridge_v0_7.py",
    "v0.7.1-C": "superseded by v0.7.1-C3 dashboard wiring",
    "v0.7.1-C2": "superseded by v0.7.1-C3 dashboard badge wiring",
    "v0.7.1-D": "superseded by v0.7.1-D2 and v0.7.1-F security gate modules",
}

# ---- 目前應 green 的 readiness（hard gate，subprocess EXIT=0）----
GREEN_READINESS = (
    ("B", "scripts/check_hermes_openclaw_local_only_queue_intake_bridge_v0_7_1_b_readiness.py"),
    ("C3", "scripts/check_hermes_openclaw_web_dashboard_read_only_status_badges_v0_7_1_c3_readiness.py"),
    ("D2", "scripts/check_hermes_openclaw_local_only_security_gates_v0_7_1_d2_readiness.py"),
    ("E", "scripts/check_hermes_openclaw_local_only_intake_security_gates_v0_7_1_e_readiness.py"),
    ("F", "scripts/check_hermes_openclaw_approval_to_queued_security_gate_v0_7_1_f_readiness.py"),
    ("F2", "scripts/check_hermes_openclaw_approve_route_wiring_plan_v0_7_1_f2.py"),
)

# ---- artifacts：docs + 已落地模組 ----
REQUIRED_DOCS = (
    "docs/HERMES_OPENCLAW_CONTROLLED_QUEUE_INTAKE_PLAN_V0_7_1_A.md",
    "docs/HERMES_OPENCLAW_LOCAL_ONLY_QUEUE_INTAKE_BRIDGE_V0_7_1_B.md",
    "docs/HERMES_OPENCLAW_DASHBOARD_INTAKE_STATUS_VIEW_MODEL_V0_7_1_C.md",
    "docs/HERMES_OPENCLAW_WEB_DASHBOARD_READ_ONLY_STATUS_BADGES_PLAN_V0_7_1_C2.md",
    "docs/HERMES_OPENCLAW_WEB_DASHBOARD_READ_ONLY_STATUS_BADGES_V0_7_1_C3.md",
    "docs/HERMES_OPENCLAW_KILL_SWITCH_AUDIT_ALLOWLIST_PLAN_V0_7_1_D.md",
    "docs/HERMES_OPENCLAW_LOCAL_ONLY_SECURITY_GATES_V0_7_1_D2.md",
    "docs/HERMES_OPENCLAW_LOCAL_ONLY_INTAKE_SECURITY_GATES_V0_7_1_E.md",
    "docs/HERMES_OPENCLAW_APPROVAL_TO_QUEUED_SECURITY_GATE_V0_7_1_F.md",
    "docs/HERMES_OPENCLAW_APPROVE_ROUTE_WIRING_PLAN_V0_7_1_F2.md",
)
REQUIRED_MODULES = (
    "app/queue_intake_bridge_v0_7.py",
    "app/dashboard_intake_view_v0_7.py",
    "app/security_gates_v0_7.py",
    "app/approval_security_gate_v0_7.py",
)

MAIN = ROOT / "app" / "main.py"
TASK_DETAIL = ROOT / "templates" / "task_detail.html"
INTAKE_BRIDGE = ROOT / "app" / "queue_intake_bridge_v0_7.py"
SECURITY_GATES = ROOT / "app" / "security_gates_v0_7.py"
APPROVAL_GATE = ROOT / "app" / "approval_security_gate_v0_7.py"
QUEUE_STORE = ROOT / "app" / "queue_store.py"
WORKER = ROOT / "app" / "worker.py"
RESULT_SINK = ROOT / "app" / "result_sink.py"

# 名稱以字串組裝，避免本檔字面量被其他掃描器誤判為真接線。
APPROVAL_MODULE_NAME = "approval_security_gate" + "_v0_7"
APPROVAL_FUNC_NAME = "evaluate_approval" + "_to_queued"

RE_SPREADSHEET_URL = re.compile(r"spreadsheets/d/[A-Za-z0-9_-]{20,}")
RE_SPREADSHEET_ASSIGN = re.compile(r"SPREADSHEET_ID\s*[:=]\s*[\"'][A-Za-z0-9_-]{20,}[\"']")
RE_TOKEN_PREFIX = re.compile(r"(ya29\.[A-Za-z0-9_-]{10,}|1//[A-Za-z0-9_-]{10,}|" + "goc" + r"spx-[A-Za-z0-9_-]{10,})")
RE_PRIVATE_KEY = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")
RE_SHEETS_ENABLED_TRUE = re.compile(r"GOOGLE_SHEETS_ENABLED\s*[:=]\s*true", re.IGNORECASE)

# 安全掃描範圍：current-state 相關的 app 功能檔。
SAFETY_SCAN_FILES = (
    MAIN, INTAKE_BRIDGE, SECURITY_GATES, APPROVAL_GATE,
    QUEUE_STORE, WORKER, RESULT_SINK,
    ROOT / "app" / "dashboard_intake_view_v0_7.py",
)

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
    print("[0] expected-stale allowlist（資訊，不當 hard gate）")
    for ver, why in EXPECTED_STALE_READINESS.items():
        print(f"  -- {ver}: {why}")

    print("[1] artifacts 存在（docs + 已落地模組）")
    for rel in REQUIRED_DOCS + REQUIRED_MODULES:
        _check((ROOT / rel).is_file(), f"{rel} 存在")

    print("[2] green readiness（B/C3/D2/E/F/F2）subprocess EXIT=0")
    for tag, rel in GREEN_READINESS:
        path = ROOT / rel
        if not path.is_file():
            _check(False, f"{tag} readiness 檔存在（{rel}）")
            continue
        proc = subprocess.run([sys.executable, str(path)], cwd=str(ROOT),
                              capture_output=True, text=True, check=False)
        _check(proc.returncode == 0, f"{tag} readiness EXIT=0（{rel}）")

    print("[3] current implementation truths")
    main_txt = _read(MAIN)
    _check("dashboard_intake_view_v0_7" in main_txt, "main.py 含 C3 wiring：dashboard_intake_view_v0_7")
    _check("derive_intake_status_view" in main_txt, "main.py 含 C3 wiring：derive_intake_status_view")
    td = _read(TASK_DETAIL)
    _check("intake_status" in td or "Intake Status" in td, "task_detail.html 含 intake/status badge 顯示痕跡")
    _check("badge" in td, "task_detail.html 含 badge 樣式痕跡")

    bridge = _read(INTAKE_BRIDGE)
    for tok in ("INTAKE_SECURITY_GATES_ENABLED", "evaluate_security_gates", "requested_tools", "GLOBAL_KILL_SWITCH"):
        _check(tok in bridge, f"queue_intake_bridge_v0_7.py 含 E wiring：{tok}")

    sg = _read(SECURITY_GATES)
    for tok in ("evaluate_security_gates", "evaluate_tool_allowlist", "build_audit_event", "redact_audit_metadata"):
        _check(tok in sg, f"security_gates_v0_7.py 含：{tok}")

    ag = _read(APPROVAL_GATE)
    for tok in (APPROVAL_FUNC_NAME, "approval_security_gates_enabled", "executable_by_worker", "requested_tools"):
        _check(tok in ag, f"approval_security_gate_v0_7.py 含：{tok}")

    print("[4] boundary：approval gate 尚未接入 main/queue_store/worker/result_sink")
    imp_re = re.compile(rf"^\s*(?:import|from)\s+\S*{re.escape(APPROVAL_MODULE_NAME)}\b", re.MULTILINE)
    for path, name in ((MAIN, "main.py"), (QUEUE_STORE, "queue_store.py"),
                       (WORKER, "worker.py"), (RESULT_SINK, "result_sink.py")):
        txt = _read(path)
        _check(not imp_re.search(txt), f"{name} 尚未 import {APPROVAL_MODULE_NAME}")
        _check(APPROVAL_FUNC_NAME + "(" not in txt, f"{name} 尚未呼叫 {APPROVAL_FUNC_NAME}")
    # F2-A / F2-B route wiring 痕跡：approve route 不得呼叫 approval gate（以上 import/call 已涵蓋）。
    _check(APPROVAL_MODULE_NAME not in main_txt, "main.py 無 F2-A/F2-B approve route wiring 痕跡")

    print("[5] safety：無 Sheets live / 無真 secret / 無新 run_openclaw_cli 呼叫")
    for path in SAFETY_SCAN_FILES:
        txt = _read(path)
        rel = path.relative_to(ROOT).as_posix()
        _check(not RE_SHEETS_ENABLED_TRUE.search(txt), f"{rel} 未把 GOOGLE_SHEETS_ENABLED 設為 true")
        _check(_no_real_secret(txt), f"{rel} 不含完整 spreadsheet id/url/token/private key（格式比對）")
    # run_openclaw_cli 不應出現在 intake / gate 路徑（main.py 既有 background dispatch 定義/呼叫不在此清單）。
    for path, name in ((INTAKE_BRIDGE, "queue_intake_bridge_v0_7.py"),
                       (APPROVAL_GATE, "approval_security_gate_v0_7.py"),
                       (SECURITY_GATES, "security_gates_v0_7.py")):
        _check("run_openclaw_cli(" not in _read(path), f"{name} 無 run_openclaw_cli 呼叫點")

    print("[6] 無 v0.7 tag")
    proc = subprocess.run(["git", "tag", "--list", "*0.7*"], cwd=str(ROOT),
                          capture_output=True, text=True, check=False)
    _check(proc.returncode == 0 and proc.stdout.strip() == "", "repo 無 v0.7 tag")

    if FAILURES:
        print(f"\nXX v0.7.1 current-state regression 失敗 {len(FAILURES)} 項：")
        for f in FAILURES:
            print(f"   - {f}")
        return 1
    print("\nOK v0.7.1 current-state regression 全數通過"
          "（current master = v0.7.1-F2 boundary；stale A/C/C2/D 為 expected，未當 hard gate）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
