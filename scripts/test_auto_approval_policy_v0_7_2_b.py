#!/usr/bin/env python3
"""v0.7.2-B — Auto-Approval Policy helper 純函式測試（不連任何系統）。

覆蓋 Level 0–3、kill switch、mode/flags、denylist 覆蓋 allowlist、protected files、
forbidden operations、risk level、requires_confirmation、空/未知 requested_tools、
input 不被 mutate，以及固定安全欄位（can_execute / queue_transition_allowed / observation_only）。
"""

from __future__ import annotations

import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.auto_approval_policy_v0_7 import evaluate_auto_approval

FAILURES: list[str] = []


def _assert(cond: bool, label: str) -> None:
    print(f"  {'ok ' if cond else 'XX '}: {label}")
    if not cond:
        FAILURES.append(label)


SAFE = dict(
    auto_approval_mode="safe",
    safe_autopilot_enabled=True,
    low_risk_auto_approval_enabled=True,
    auto_approval_policy="safe",
)


def make(**md_and_payload):
    md = {}
    for k in ("task_type", "safety_level", "requested_tools", "requested_operations",
              "touched_files", "requires_confirmation"):
        if k in md_and_payload:
            md[k] = md_and_payload[k]
    payload = {"metadata": md}
    if "allowed_tools" in md_and_payload:
        payload["allowed_tools"] = md_and_payload["allowed_tools"]
    if "denied_tools" in md_and_payload:
        payload["denied_tools"] = md_and_payload["denied_tools"]
    return {"task_id": "t-1", "correlation_id": "c-1", "status": "waiting_review", "payload": payload}


def _safe_fields(r: dict) -> bool:
    return (r["can_execute"] is False
            and r["queue_transition_allowed"] is False
            and r["observation_only"] is True
            and "audit_event" in r and isinstance(r["audit_event"], dict)
            and r["audit_event"].get("observation_only") is True)


def main() -> int:
    # --- Level 0：read-only / report / test / compile → auto_approved ---
    for tt, tool in (("test", "run_tests"), ("compile", "compile"),
                     ("report", "read_file"), ("read_only_query", "search"),
                     ("readiness_check", "list_files")):
        r = evaluate_auto_approval(
            make(task_type=tt, safety_level=0, requested_tools=[tool], allowed_tools=[tool]), **SAFE)
        _assert(r["policy_decision"] == "auto_approved" and r["matched_level"] == 0,
                f"Level0 {tt} → auto_approved (level0)")
        _assert(_safe_fields(r) and r["can_auto_approve"] is True, f"Level0 {tt} 安全欄位固定")

    # --- Level 1：docs_only / plan_only / pure_helper_local → auto_approved (level1), can_execute false ---
    for tt in ("docs_only", "plan_only", "pure_helper_local"):
        r = evaluate_auto_approval(
            make(task_type=tt, safety_level=1, requested_tools=["read_file"], allowed_tools=["read_file"]),
            **SAFE)
        _assert(r["policy_decision"] == "auto_approved" and r["matched_level"] == 1,
                f"Level1 {tt} → auto_approved (level1)")
        _assert(r["can_execute"] is False, f"Level1 {tt} → can_execute False")

    # --- Level 2：protected file → needs_owner（覆蓋 safe task_type）---
    r = evaluate_auto_approval(
        make(task_type="test", safety_level=0, requested_tools=["run_tests"], allowed_tools=["run_tests"],
             touched_files=["app/main.py"]), **SAFE)
    _assert(r["policy_decision"] == "needs_owner_approval" and r["reason"] == "protected_file_touched"
            and r["matched_level"] == 2, "Level2 protected file → needs_owner（override safe task_type）")

    # --- Level 2：commit（非 safe task_type）/ state machine change → needs_owner ---
    r = evaluate_auto_approval(
        make(task_type="commit", safety_level=0, requested_tools=["read_file"], allowed_tools=["read_file"]),
        **SAFE)
    _assert(r["policy_decision"] == "needs_owner_approval", "Level2 commit task_type → needs_owner")

    # --- Level 3：forbidden operations → prohibited ---
    for op in ("git_push", "git_tag", "read_secrets", "write_production_db", "start_worker",
               "call_openclaw", "call_hermes", "google_sheets_live_write"):
        r = evaluate_auto_approval(
            make(task_type="test", safety_level=0, requested_tools=["run_tests"], allowed_tools=["run_tests"],
                 requested_operations=[op]), **SAFE)
        _assert(r["policy_decision"] == "prohibited" and r["prohibited"] is True and r["matched_level"] == 3,
                f"Level3 {op} → prohibited")
        _assert(_safe_fields(r) and r["can_auto_approve"] is False, f"Level3 {op} 安全欄位固定")

    # --- mode / flags ---
    base = make(task_type="test", safety_level=0, requested_tools=["run_tests"], allowed_tools=["run_tests"])
    _assert(evaluate_auto_approval(base, **{**SAFE, "auto_approval_mode": "off"})["policy_decision"]
            == "needs_owner_approval", "mode=off → needs_owner")
    r = evaluate_auto_approval(base, **{**SAFE, "auto_approval_mode": "dangerous_unknown"})
    _assert(r["policy_decision"] == "needs_owner_approval" and r["reason"] == "unsupported_auto_approval_mode",
            "unknown mode → needs_owner (fail closed)")
    _assert(evaluate_auto_approval(base, **{**SAFE, "safe_autopilot_enabled": False})["policy_decision"]
            == "needs_owner_approval", "safe_autopilot_enabled=False → needs_owner")
    _assert(evaluate_auto_approval(base, **{**SAFE, "low_risk_auto_approval_enabled": False})["policy_decision"]
            == "needs_owner_approval", "low_risk_auto_approval_enabled=False → needs_owner")
    _assert(evaluate_auto_approval(base, **{**SAFE, "auto_approval_policy": "loose"})["policy_decision"]
            == "needs_owner_approval", "auto_approval_policy!=safe → needs_owner")

    # --- kill switch ---
    _assert(evaluate_auto_approval(base, **{**SAFE, "global_kill_switch": True})["policy_decision"]
            == "rejected", "GLOBAL_KILL_SWITCH=true → rejected")
    _assert(evaluate_auto_approval(base, **{**SAFE, "auto_approval_kill_switch": True})["policy_decision"]
            == "rejected", "AUTO_APPROVAL_KILL_SWITCH=true → rejected")
    # kill switch 覆蓋一切（即使有 forbidden op）。
    r = evaluate_auto_approval(
        make(task_type="test", safety_level=0, requested_tools=["run_tests"], allowed_tools=["run_tests"],
             requested_operations=["git_push"]), **{**SAFE, "global_kill_switch": True})
    _assert(r["policy_decision"] == "rejected", "kill switch 覆蓋 forbidden op")

    # --- task_type / safety_level / requires_confirmation ---
    _assert(evaluate_auto_approval(
        make(task_type="frobnicate", safety_level=0, requested_tools=["read_file"], allowed_tools=["read_file"]),
        **SAFE)["policy_decision"] == "needs_owner_approval", "unknown task_type → needs_owner")
    _assert(evaluate_auto_approval(
        make(task_type="test", requested_tools=["run_tests"], allowed_tools=["run_tests"]), **SAFE)["reason"]
        == "missing_or_invalid_safety_level", "missing safety_level → needs_owner")
    _assert(evaluate_auto_approval(
        make(task_type="test", safety_level="abc", requested_tools=["run_tests"], allowed_tools=["run_tests"]),
        **SAFE)["reason"] == "missing_or_invalid_safety_level", "invalid safety_level → needs_owner")
    _assert(evaluate_auto_approval(
        make(task_type="test", safety_level=3, requested_tools=["run_tests"], allowed_tools=["run_tests"]),
        **SAFE)["reason"] == "safety_level_too_high", "safety_level > 1 → needs_owner")
    _assert(evaluate_auto_approval(
        make(task_type="test", safety_level=0, requested_tools=["run_tests"], allowed_tools=["run_tests"],
             requires_confirmation=True), **SAFE)["reason"] == "requires_confirmation",
        "requires_confirmation=true → needs_owner")

    # --- requested_tools / allowed_tools / denylist ---
    _assert(evaluate_auto_approval(
        make(task_type="test", safety_level=0, requested_tools=[], allowed_tools=["run_tests"]), **SAFE)[
        "policy_decision"] == "needs_owner_approval", "empty requested_tools → needs_owner")
    _assert(evaluate_auto_approval(
        make(task_type="test", safety_level=0, requested_tools=["run_tests"], allowed_tools=[]), **SAFE)[
        "policy_decision"] == "needs_owner_approval", "empty allowed_tools → needs_owner")
    _assert(evaluate_auto_approval(
        make(task_type="test", safety_level=0, requested_tools=["delete_everything"], allowed_tools=["delete_everything"]),
        **SAFE)["reason"] == "requested_tool_not_in_safe_allowlist", "unknown requested_tool → needs_owner")
    r = evaluate_auto_approval(
        make(task_type="test", safety_level=0, requested_tools=["read_file"], allowed_tools=["read_file"],
             denied_tools=["read_file"]), **SAFE)
    _assert(r["policy_decision"] == "prohibited" and r["reason"] == "denied_tool_matched",
            "denied_tools hit → prohibited（覆蓋 allowlist）")

    # --- input 不被 mutate ---
    original = make(task_type="test", safety_level=0, requested_tools=["run_tests"], allowed_tools=["run_tests"])
    snapshot = copy.deepcopy(original)
    evaluate_auto_approval(original, **SAFE)
    _assert(original == snapshot, "input task_row 未被 mutate")

    # --- 固定安全欄位：所有 decision 都帶 audit_event 且 observation_only/can_execute/queue_transition_allowed ---
    for r in (
        evaluate_auto_approval(base, **SAFE),
        evaluate_auto_approval(base, **{**SAFE, "auto_approval_mode": "off"}),
        evaluate_auto_approval(base, **{**SAFE, "global_kill_switch": True}),
        evaluate_auto_approval(
            make(task_type="test", safety_level=0, requested_tools=["run_tests"], allowed_tools=["run_tests"],
                 requested_operations=["git_push"]), **SAFE),
    ):
        _assert(_safe_fields(r), f"安全欄位固定（decision={r['policy_decision']}）")
        _assert(r["can_execute"] is False, f"can_execute False（{r['policy_decision']}）")
        _assert(r["queue_transition_allowed"] is False, f"queue_transition_allowed False（{r['policy_decision']}）")

    # auto_approved ≠ queued / ≠ execute
    r = evaluate_auto_approval(base, **SAFE)
    _assert(r["policy_decision"] == "auto_approved" and r["queue_transition_allowed"] is False
            and r["can_execute"] is False, "auto_approved 不代表 queued / 不代表執行")

    # task_row 非 dict → needs_owner（不崩潰）
    _assert(evaluate_auto_approval("not-a-dict", **SAFE)["policy_decision"] == "needs_owner_approval",
            "task_row 非 dict → needs_owner（fail-closed）")

    if FAILURES:
        print(f"\nXX v0.7.2-B auto-approval policy 測試失敗 {len(FAILURES)} 項：")
        for f in FAILURES:
            print(f"   - {f}")
        return 1
    print("\nOK v0.7.2-B auto-approval policy 測試全數通過（pure / observation-only）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
