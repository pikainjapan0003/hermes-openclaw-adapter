#!/usr/bin/env python3
"""v0.7.2-C2 — Auto-Approval Local-only Simulation Current-State Update 靜態 readiness。

確認 v0.7.2-C2 只把 v0.7.2-C simulation 收編進 current-state aggregator：
  - aggregator 已把 C readiness + C test 列為 green gate、加入 C artifacts、加入 simulation 正向斷言
    與「未被 main/queue_store/worker/result_sink 接入」邊界。
  - C2 doc 含必要章節與裁定。
  - 本版只修改 aggregator、只新增 C2 doc + C2 readiness；C simulation/readiness/test、app 功能檔、
    templates/static 皆未改（git diff --name-only HEAD 比對）。
  - 不改 EXPECTED_STALE_READINESS（C 不進 expected-stale）。
靜態檢查：不連外、不寫 DB、不讀 secrets。敏感檢查一律 regex / 格式比對。
（註：本 readiness 自身僅用 subprocess 跑 git diff 做靜態驗證；對 simulation 的 subprocess 禁令
  僅針對 simulation/產品層，不針對 verification tooling，沿用 v0.7.2-C readiness 慣例。）
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOC = ROOT / "docs" / "HERMES_OPENCLAW_AUTO_APPROVAL_LOCAL_ONLY_SIMULATION_CURRENT_STATE_UPDATE_V0_7_2_C2.md"
READINESS = ROOT / "scripts" / "check_hermes_openclaw_auto_approval_local_only_simulation_current_state_update_v0_7_2_c2.py"
AGG = ROOT / "scripts" / "check_hermes_openclaw_v0_7_1_current_state.py"

# 本版唯一允許「修改」的既有檔。
ALLOWED_MODIFY = {"scripts/check_hermes_openclaw_v0_7_1_current_state.py"}
# 本版允許「新增」的檔。
ALLOWED_NEW = {
    "docs/HERMES_OPENCLAW_AUTO_APPROVAL_LOCAL_ONLY_SIMULATION_CURRENT_STATE_UPDATE_V0_7_2_C2.md",
    "scripts/check_hermes_openclaw_auto_approval_local_only_simulation_current_state_update_v0_7_2_c2.py",
}
# 絕對不可被本版修改的既有檔。
MUST_STAY_UNCHANGED = (
    "scripts/simulate_auto_approval_policy_v0_7_2_c.py",
    "scripts/check_hermes_openclaw_auto_approval_local_only_simulation_v0_7_2_c.py",
    "scripts/test_auto_approval_local_only_simulation_v0_7_2_c.py",
    "app/auto_approval_policy_v0_7.py",
    "app/main.py",
    "app/queue_store.py",
    "app/worker.py",
    "app/result_sink.py",
    "app/approval_security_gate_v0_7.py",
    "app/security_gates_v0_7.py",
    "scripts/check_hermes_openclaw_auto_approval_policy_helper_v0_7_2_b.py",
    "scripts/test_auto_approval_policy_v0_7_2_b.py",
    "scripts/check_hermes_openclaw_auto_approval_expected_stale_readiness_update_v0_7_2_b2.py",
    "scripts/check_hermes_openclaw_auto_approval_policy_plan_v0_7_2_a.py",
)

# aggregator 必須包含的更新內容（green gate=C test / artifacts / 正向斷言 / 邊界）。
# 註：C readiness 是 required artifact，但**不**是 subprocess green gate（見 [2c] 反向檢查）。
AGG_REQUIRED = (
    # green gate：只有 C test（C readiness 不在此重跑，避免循環）
    "C-sim-test",
    "test_auto_approval_local_only_simulation_v0_7_2_c.py",
    # C artifacts（含 C readiness 為 required artifact）
    "REQUIRED_C_SIM_ARTIFACTS",
    "check_hermes_openclaw_auto_approval_local_only_simulation_v0_7_2_c.py",
    "HERMES_OPENCLAW_AUTO_APPROVAL_LOCAL_ONLY_SIMULATION_V0_7_2_C.md",
    "simulate_auto_approval_policy_v0_7_2_c.py",
    # positive assertions
    "simulation imports evaluate_auto_approval",
    "simulation supports --sample",
    "simulation supports --json",
    "simulation has safe profile",
    "simulation has default-off profile",
    "level0_", "level1_", "level2_", "level3_",
    "simulation includes edge samples",
    "simulation returns can_execute false",
    "simulation returns queue_transition_allowed false",
    "simulation returns observation_only true",
    # boundary：simulation 未被接入 main/queue_store/worker/result_sink
    "SIMULATE_C_MODULE_NAME",
    "尚未被 main/queue_store/worker/result_sink 接入",
)

REQUIRED_TITLES = (
    "1. Purpose", "2. Context", "3. Relationship To v0.7.2-C",
    "4. Why Current-State Aggregator Needs C", "5. C Is Additive",
    "6. C Does Not Supersede B", "7. C Does Not Supersede B2", "8. New Green Gates",
    "9. Required C Artifacts", "10. Positive Current-State Assertions",
    "11. Simulation Boundary", "12. QueueStore Boundary", "13. Route Boundary",
    "14. Worker / OpenClaw Boundary", "15. Hermes Boundary", "16. Google Sheets Boundary",
    "17. Secrets Boundary", "18. Network / Subprocess Boundary", "19. No Expected-Stale Change",
    "20. No v0.7 Tag", "21. Future v0.7.2-D", "22. Final Recommendation",
)

REQUIRED_STATEMENTS = (
    "v0.7.2-C2 updates current-state only.",
    "v0.7.2-C2 does not add features.",
    "v0.7.2-C2 does not modify the simulation script.",
    "v0.7.2-C2 does not modify the C readiness script.",
    "v0.7.2-C2 does not modify the C test.",
    "v0.7.2-C is additive and does not supersede v0.7.2-B.",
    "v0.7.2-C is additive and does not supersede v0.7.2-B2.",
    "v0.7.2-C test is a current-state green gate.",
    "v0.7.2-C readiness remains a standalone readiness check and required artifact.",
    "current-state aggregator does not subprocess-call C readiness, to avoid circular dependency.",
    "current-state aggregator validates C simulation through C test plus inline positive assertions.",
    "current-state aggregator is the source of truth for current health.",
    "v0.7.2-C2 does not wire routes.",
    "v0.7.2-C2 does not wire QueueStore.",
    "v0.7.2-C2 does not start Worker.",
    "v0.7.2-C2 does not call OpenClaw.",
    "v0.7.2-C2 does not call Hermes.",
    "v0.7.2-C2 does not write Google Sheets.",
    "v0.7.2-C2 does not read secrets.",
    "v0.7.2-C2 does not use network.",
    "v0.7.2-C2 does not use subprocess.",
    "v0.7.2-C2 does not create tag.",
)

RE_SPREADSHEET_URL = re.compile(r"spreadsheets/d/[A-Za-z0-9_-]{20,}")
RE_SPREADSHEET_ASSIGN = re.compile(r"SPREADSHEET_ID\s*[:=]\s*[\"'][A-Za-z0-9_-]{20,}[\"']")
RE_TOKEN_PREFIX = re.compile(r"(ya29\.[A-Za-z0-9_-]{10,}|1//[A-Za-z0-9_-]{10,}|" + "goc" + r"spx-[A-Za-z0-9_-]{10,})")
RE_PRIVATE_KEY = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")
RE_SECRET_ASSIGN = re.compile(r"(refresh_token|client_secret|private_key)\s*[:=]\s*[\"'][^\"']{8,}[\"']",
                              re.IGNORECASE)

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


def _git_changed_tracked() -> set[str]:
    """working tree 相對 HEAD 的 tracked 修改（不含 untracked 新檔）。"""
    try:
        out = subprocess.run(["git", "diff", "--name-only", "HEAD"], cwd=str(ROOT),
                             capture_output=True, text=True, check=False)
    except (OSError, ValueError):
        print("  ?? : git 不可用，略過 diff 比對（仍以靜態檢查為準）")
        return set()
    return {line.strip() for line in out.stdout.splitlines() if line.strip()}


def _git_untracked() -> set[str]:
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
    doc = _read(DOC)
    agg = _read(AGG)

    print("[1] C2 doc / C2 readiness / aggregator 存在")
    _check(DOC.is_file(), "C2 doc 存在")
    _check(READINESS.is_file(), "C2 readiness 自身存在")
    _check(AGG.is_file(), "current-state aggregator 存在")

    print("[2] aggregator 已收編 C（green gate=C test + artifacts + 正向斷言 + 邊界）")
    for tok in AGG_REQUIRED:
        _check(tok in agg, f"aggregator 含「{tok}」")

    print("[2c] 無循環依賴：aggregator 不把 C readiness 當 subprocess green gate、且無 re-entrancy guard")
    m_green = re.search(r"GREEN_READINESS\s*=\s*\((.*?)\n\)", agg, re.DOTALL)
    green_block = m_green.group(1) if m_green else ""
    _check(bool(green_block), "找到 GREEN_READINESS 區塊")
    _check("check_hermes_openclaw_auto_approval_local_only_simulation_v0_7_2_c.py" not in green_block,
           "GREEN_READINESS 不含 C readiness（避免 current-state ⇄ C readiness 循環）")
    _check("test_auto_approval_local_only_simulation_v0_7_2_c.py" in green_block,
           "GREEN_READINESS 含 C test（C test 仍為 green gate）")
    _check("C-sim-readiness" not in agg, "aggregator 無 C-sim-readiness gate tag（C readiness 非 gate）")
    _check("HERMES_CURRENT_STATE_NESTED" not in agg, "aggregator 無 re-entrancy guard（已隨循環移除）")
    m_art = re.search(r"REQUIRED_C_SIM_ARTIFACTS\s*=\s*\((.*?)\n\)", agg, re.DOTALL)
    art_block = m_art.group(1) if m_art else ""
    _check("check_hermes_openclaw_auto_approval_local_only_simulation_v0_7_2_c.py" in art_block,
           "C readiness 仍列為 required artifact（REQUIRED_C_SIM_ARTIFACTS）")
    # [4c] inline 正向斷言區塊存在（simulation 健康改由此驗證）。
    _check("[4c]" in agg, "aggregator 保留 [4c] inline positive assertions 區塊")

    print("[3] C2 doc 含所有必要章節")
    for title in REQUIRED_TITLES:
        _check(title in doc, f"C2 doc 含章節「{title}」")

    print("[4] C2 doc 含所有裁定 / 邊界聲明")
    for stmt in REQUIRED_STATEMENTS:
        _check(stmt in doc, f"C2 doc 含聲明「{stmt[:46]}…」")

    print("[5] 本版只改 aggregator、只新增 C2 doc + C2 readiness（git diff --name-only HEAD 比對）")
    changed = _git_changed_tracked()
    extra = sorted(changed - ALLOWED_MODIFY)
    _check(not extra, f"tracked 修改只含 aggregator（多出：{extra}）")
    for rel in MUST_STAY_UNCHANGED:
        _check(rel not in changed, f"{rel} 未被本版修改")
    for rel in changed:
        _check(not (rel.startswith("templates/") or rel.startswith("static/")),
               f"templates/static 未被本版修改（{rel}）")
    untracked = _git_untracked()
    extra_untracked = sorted(untracked - ALLOWED_NEW)
    _check(not extra_untracked, f"未追蹤新檔僅本版 C2 doc + C2 readiness（多出：{extra_untracked}）")

    print("[6] expected-stale policy 未被破壞（C 不進 expected-stale）")
    _check("EXPECTED_STALE_READINESS" in agg, "aggregator 仍有 EXPECTED_STALE_READINESS")
    # 抽出 EXPECTED_STALE_READINESS 區塊，確認未把 v0.7.2-C 列入。
    m = re.search(r"EXPECTED_STALE_READINESS\s*=\s*\{(.*?)\}", agg, re.DOTALL)
    stale_block = m.group(1) if m else ""
    _check('"v0.7.2-C"' not in stale_block, "v0.7.2-C 未被列入 expected-stale")

    print("[7] 敏感檢查（格式比對）：doc / readiness / aggregator 不含真實 secret")
    for name, text in (("doc", doc), ("readiness", _read(READINESS)), ("aggregator", agg)):
        _check(_no_real_secret(text),
               f"{name} 不含完整 spreadsheet id / url / token / private key（格式比對）")

    if FAILURES:
        print(f"\nXX v0.7.2-C2 current-state update readiness 失敗 {len(FAILURES)} 項：")
        for f in FAILURES:
            print(f"   - {f}")
        return 1
    print("\nOK v0.7.2-C2 current-state update readiness 全數通過"
          "（aggregator 已收編 C green gates/artifacts/斷言；只改 aggregator + 新增 C2 doc/readiness；"
          "未動 simulation/C readiness/C test/app；未含 secret）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
