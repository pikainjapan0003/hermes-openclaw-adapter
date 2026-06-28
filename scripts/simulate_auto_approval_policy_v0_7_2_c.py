#!/usr/bin/env python3
"""v0.7.2-C — Auto-Approval Local-only Simulation（decision preview；observation-only）。

本工具是「假工單模擬器」：只用內建 sample tasks 呼叫純函式
`app.auto_approval_policy_v0_7.evaluate_auto_approval(...)`，把 policy decision
**預覽**印出來。它**不**讀真 Queue、不改 Queue、不寫 DB、不接 route、不啟 Worker、
不呼叫 OpenClaw / Hermes、不寫 Google Sheets、不讀 secrets、不連網、不開子行程。

Simulation 不等於 execution；decision preview 不等於 queued。
helper 永遠回傳 can_execute=False / queue_transition_allowed=False / observation_only=True，
故本模擬器展示的任何「auto_approved」都僅是 policy 層預覽，無任何外部副作用。

CLI：
  python scripts/simulate_auto_approval_policy_v0_7_2_c.py
  python scripts/simulate_auto_approval_policy_v0_7_2_c.py --sample all|level0|level1|level2|level3|edge
  python scripts/simulate_auto_approval_policy_v0_7_2_c.py --json
  python scripts/simulate_auto_approval_policy_v0_7_2_c.py --profile safe|default-off

預設：--sample all、human-readable、safe_autopilot simulation profile。

import 邊界：只 import stdlib（argparse / copy / json / sys / pathlib / typing）與
app.auto_approval_policy_v0_7.evaluate_auto_approval。不 import app.main / queue_store /
worker / result_sink / sqlite3 / requests / 子行程 / google / gspread / oauth。
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.auto_approval_policy_v0_7 import evaluate_auto_approval

VERSION = "v0.7.2-C"

# ---- Safe Autopilot simulation profile ----
# 這只是「模擬展示用」的安全設定檔，不是 dangerous mode：helper 即使在此 profile 下，
# 仍恆回傳 can_execute=False / queue_transition_allowed=False / observation_only=True。
# 需要此 profile 才能展示 Level 0 / Level 1 的 auto_approved；否則（見 default-off）全部
# fallback 成 needs_owner_approval。
SAFE_AUTOPILOT_PROFILE: Dict[str, Any] = {
    "auto_approval_mode": "safe",
    "safe_autopilot_enabled": True,
    "low_risk_auto_approval_enabled": True,
    "auto_approval_policy": "safe",
    "global_kill_switch": False,
    "auto_approval_kill_switch": False,
}

# ---- Default-off profile（對照組）----
# 所有 flags 全 off：任何任務都會 fallback 到 needs_owner_approval（mode off 先短路），
# 用來證明「未開啟 safe autopilot 時，沒有任何任務會被自動通過」。
DEFAULT_OFF_PROFILE: Dict[str, Any] = {
    "auto_approval_mode": "off",
    "safe_autopilot_enabled": False,
    "low_risk_auto_approval_enabled": False,
    "auto_approval_policy": "safe",
    "global_kill_switch": False,
    "auto_approval_kill_switch": False,
}

PROFILE_NAMES = {
    "safe": "safe_autopilot",
    "default-off": "default_off",
}

# 每筆 sample 在 JSON / human 輸出固定呈現的欄位（含三個恆定安全旗標）。
SAMPLE_OUTPUT_FIELDS = (
    "sample_name",
    "policy_decision",
    "matched_level",
    "reason",
    "can_auto_approve",
    "can_execute",
    "queue_transition_allowed",
    "observation_only",
)

SAMPLE_GROUPS = ("level0", "level1", "level2", "level3", "edge")


def _task(
    sample_id: str,
    *,
    task_type: Any = None,
    safety_level: Any = None,
    requested_tools: Any = None,
    requested_operations: Any = None,
    touched_files: Any = None,
    requires_confirmation: Any = None,
    allowed_tools: Any = None,
    denied_tools: Any = None,
) -> Dict[str, Any]:
    """組一個假 task_row（沿用 v0.7.2-B helper 期望的 payload.metadata 結構）。

    None 代表「不放這個 key」，以便精準觸發 missing / fail-closed 分支。
    """
    md: Dict[str, Any] = {}
    if task_type is not None:
        md["task_type"] = task_type
    if safety_level is not None:
        md["safety_level"] = safety_level
    if requested_tools is not None:
        md["requested_tools"] = requested_tools
    if requested_operations is not None:
        md["requested_operations"] = requested_operations
    if touched_files is not None:
        md["touched_files"] = touched_files
    if requires_confirmation is not None:
        md["requires_confirmation"] = requires_confirmation
    payload: Dict[str, Any] = {"metadata": md}
    if allowed_tools is not None:
        payload["allowed_tools"] = allowed_tools
    if denied_tools is not None:
        payload["denied_tools"] = denied_tools
    return {
        "task_id": sample_id,
        "correlation_id": "sim-" + sample_id,
        "status": "waiting_review",
        "payload": payload,
    }


def build_samples() -> List[Dict[str, Any]]:
    """回傳內建假工單目錄（含 group 與 safe-profile 下的 expected 決策）。

    expected 是「safe_autopilot profile」下的預期；default-off 對照另計（全 needs_owner）。
    profile_overrides 只在 safe profile 模擬時套用（展示 kill switch / unsupported mode）。
    """
    samples: List[Dict[str, Any]] = []

    def add(name, group, task_row, expected, *, profile_overrides=None):
        samples.append({
            "sample_name": name,
            "group": group,
            "task_row": task_row,
            "profile_overrides": profile_overrides or {},
            "expected": expected,
        })

    # ---- Level 0：唯讀 / report / test / compile / readiness（safe → auto_approved L0）----
    add("level0_read_only_query", "level0",
        _task("level0_read_only_query", task_type="read_only_query", safety_level=0,
              requested_tools=["search"], allowed_tools=["search"]),
        {"policy_decision": "auto_approved", "matched_level": 0, "reason": "auto_approved_low_risk"})
    add("level0_report", "level0",
        _task("level0_report", task_type="report", safety_level=0,
              requested_tools=["read_file"], allowed_tools=["read_file"]),
        {"policy_decision": "auto_approved", "matched_level": 0, "reason": "auto_approved_low_risk"})
    add("level0_test", "level0",
        _task("level0_test", task_type="test", safety_level=0,
              requested_tools=["run_tests"], allowed_tools=["run_tests"]),
        {"policy_decision": "auto_approved", "matched_level": 0, "reason": "auto_approved_low_risk"})
    add("level0_compile", "level0",
        _task("level0_compile", task_type="compile", safety_level=0,
              requested_tools=["compile"], allowed_tools=["compile"]),
        {"policy_decision": "auto_approved", "matched_level": 0, "reason": "auto_approved_low_risk"})
    add("level0_readiness_check", "level0",
        _task("level0_readiness_check", task_type="readiness_check", safety_level=0,
              requested_tools=["list_files"], allowed_tools=["list_files"]),
        {"policy_decision": "auto_approved", "matched_level": 0, "reason": "auto_approved_low_risk"})

    # ---- Level 1：local-only docs / plan / pure helper（safe → auto_approved L1）----
    for tt in ("docs_only", "plan_only", "pure_helper_local"):
        add(f"level1_{tt}", "level1",
            _task(f"level1_{tt}", task_type=tt, safety_level=1,
                  requested_tools=["read_file"], allowed_tools=["read_file"]),
            {"policy_decision": "auto_approved", "matched_level": 1, "reason": "auto_approved_low_risk"})

    # ---- Level 2：protected file / 非 safe task_type → needs_owner_approval ----
    add("level2_protected_main", "level2",
        _task("level2_protected_main", task_type="test", safety_level=0,
              requested_tools=["run_tests"], allowed_tools=["run_tests"],
              touched_files=["app/main.py"]),
        {"policy_decision": "needs_owner_approval", "matched_level": 2, "reason": "protected_file_touched"})
    add("level2_queue_store", "level2",
        _task("level2_queue_store", task_type="test", safety_level=0,
              requested_tools=["run_tests"], allowed_tools=["run_tests"],
              touched_files=["app/queue_store.py"]),
        {"policy_decision": "needs_owner_approval", "matched_level": 2, "reason": "protected_file_touched"})
    add("level2_commit_operation", "level2",
        _task("level2_commit_operation", task_type="commit", safety_level=0,
              requested_tools=["read_file"], allowed_tools=["read_file"]),
        {"policy_decision": "needs_owner_approval", "matched_level": 2,
         "reason": "task_type_not_in_safe_allowlist"})
    add("level2_state_machine_change", "level2",
        _task("level2_state_machine_change", task_type="state_machine_change", safety_level=0,
              requested_tools=["read_file"], allowed_tools=["read_file"]),
        {"policy_decision": "needs_owner_approval", "matched_level": 2,
         "reason": "task_type_not_in_safe_allowlist"})
    add("level2_approve_route", "level2",
        _task("level2_approve_route", task_type="approve_route", safety_level=0,
              requested_tools=["read_file"], allowed_tools=["read_file"]),
        {"policy_decision": "needs_owner_approval", "matched_level": 2,
         "reason": "task_type_not_in_safe_allowlist"})

    # ---- Level 3：forbidden operations → prohibited ----
    level3_ops = (
        ("level3_git_push", "git_push"),
        ("level3_git_tag", "git_tag"),
        ("level3_read_secrets", "read_secrets"),
        ("level3_display_secrets", "display_secrets"),
        ("level3_production_db", "write_production_db"),
        ("level3_worker_start", "start_worker"),
        ("level3_openclaw_call", "call_openclaw"),
        ("level3_hermes_call", "call_hermes"),
        ("level3_google_sheets_live_write", "google_sheets_live_write"),
        ("level3_webhook", "create_webhook"),
    )
    for name, op in level3_ops:
        add(name, "level3",
            _task(name, task_type="test", safety_level=0,
                  requested_tools=["run_tests"], allowed_tools=["run_tests"],
                  requested_operations=[op]),
            {"policy_decision": "prohibited", "matched_level": 3, "reason": "forbidden_operation"})

    # ---- Edge cases ----
    add("unknown_task_type", "edge",
        _task("unknown_task_type", task_type="frobnicate", safety_level=0,
              requested_tools=["read_file"], allowed_tools=["read_file"]),
        {"policy_decision": "needs_owner_approval", "matched_level": 2,
         "reason": "task_type_not_in_safe_allowlist"})
    add("missing_safety_level", "edge",
        _task("missing_safety_level", task_type="test",
              requested_tools=["run_tests"], allowed_tools=["run_tests"]),
        {"policy_decision": "needs_owner_approval", "matched_level": None,
         "reason": "missing_or_invalid_safety_level"})
    add("invalid_safety_level", "edge",
        _task("invalid_safety_level", task_type="test", safety_level="abc",
              requested_tools=["run_tests"], allowed_tools=["run_tests"]),
        {"policy_decision": "needs_owner_approval", "matched_level": None,
         "reason": "missing_or_invalid_safety_level"})
    add("requires_confirmation_true", "edge",
        _task("requires_confirmation_true", task_type="test", safety_level=0,
              requested_tools=["run_tests"], allowed_tools=["run_tests"],
              requires_confirmation=True),
        {"policy_decision": "needs_owner_approval", "matched_level": None,
         "reason": "requires_confirmation"})
    add("empty_requested_tools", "edge",
        _task("empty_requested_tools", task_type="test", safety_level=0,
              requested_tools=[], allowed_tools=["run_tests"]),
        {"policy_decision": "needs_owner_approval", "matched_level": None,
         "reason": "requested_tools_empty"})
    add("empty_allowed_tools", "edge",
        _task("empty_allowed_tools", task_type="test", safety_level=0,
              requested_tools=["run_tests"], allowed_tools=[]),
        {"policy_decision": "needs_owner_approval", "matched_level": None,
         "reason": "tool_gate_allowed_tools_empty"})
    add("unknown_requested_tool", "edge",
        _task("unknown_requested_tool", task_type="test", safety_level=0,
              requested_tools=["delete_everything"], allowed_tools=["delete_everything"]),
        {"policy_decision": "needs_owner_approval", "matched_level": None,
         "reason": "requested_tool_not_in_safe_allowlist"})
    add("denied_tool_hit", "edge",
        _task("denied_tool_hit", task_type="test", safety_level=0,
              requested_tools=["read_file"], allowed_tools=["read_file"],
              denied_tools=["read_file"]),
        {"policy_decision": "prohibited", "matched_level": 3, "reason": "denied_tool_matched"})
    add("kill_switch_global", "edge",
        _task("kill_switch_global", task_type="test", safety_level=0,
              requested_tools=["run_tests"], allowed_tools=["run_tests"]),
        {"policy_decision": "rejected", "matched_level": None, "reason": "global_kill_switch_active"},
        profile_overrides={"global_kill_switch": True})
    add("kill_switch_auto_approval", "edge",
        _task("kill_switch_auto_approval", task_type="test", safety_level=0,
              requested_tools=["run_tests"], allowed_tools=["run_tests"]),
        {"policy_decision": "rejected", "matched_level": None,
         "reason": "auto_approval_kill_switch_active"},
        profile_overrides={"auto_approval_kill_switch": True})
    add("task_row_not_dict", "edge",
        "this-sample-task-row-is-not-a-dict",
        {"policy_decision": "needs_owner_approval", "matched_level": None, "reason": "task_row_not_dict"})
    add("payload_missing_or_invalid", "edge",
        {"task_id": "payload_missing_or_invalid", "correlation_id": "sim-payload",
         "status": "waiting_review", "payload": "not-a-valid-json-payload"},
        {"policy_decision": "needs_owner_approval", "matched_level": None,
         "reason": "payload_missing_or_invalid"})
    add("invalid_requested_operations", "edge",
        _task("invalid_requested_operations", task_type="test", safety_level=0,
              requested_tools=["run_tests"], allowed_tools=["run_tests"],
              requested_operations="git_push"),
        {"policy_decision": "needs_owner_approval", "matched_level": None,
         "reason": "invalid_requested_operations"})
    add("invalid_touched_files", "edge",
        _task("invalid_touched_files", task_type="test", safety_level=0,
              requested_tools=["run_tests"], allowed_tools=["run_tests"],
              touched_files="app/main.py"),
        {"policy_decision": "needs_owner_approval", "matched_level": None,
         "reason": "invalid_touched_files"})
    add("unsupported_auto_approval_mode", "edge",
        _task("unsupported_auto_approval_mode", task_type="test", safety_level=0,
              requested_tools=["run_tests"], allowed_tools=["run_tests"]),
        {"policy_decision": "needs_owner_approval", "matched_level": None,
         "reason": "unsupported_auto_approval_mode"},
        profile_overrides={"auto_approval_mode": "unsupported_demo_mode"})
    add("safety_level_too_high", "edge",
        _task("safety_level_too_high", task_type="test", safety_level=2,
              requested_tools=["run_tests"], allowed_tools=["run_tests"]),
        {"policy_decision": "needs_owner_approval", "matched_level": None,
         "reason": "safety_level_too_high"})
    add("client_protected_file", "edge",
        _task("client_protected_file", task_type="test", safety_level=0,
              requested_tools=["run_tests"], allowed_tools=["run_tests"],
              touched_files=["app/some_openclaw_client.py"]),
        {"policy_decision": "needs_owner_approval", "matched_level": 2, "reason": "protected_file_touched"})

    return samples


def _select(samples: List[Dict[str, Any]], sample_filter: str) -> List[Dict[str, Any]]:
    if sample_filter == "all":
        return list(samples)
    return [s for s in samples if s["group"] == sample_filter]


def simulate_one(sample: Dict[str, Any], profile: Dict[str, Any], *,
                 apply_overrides: bool = True) -> Dict[str, Any]:
    """對單一 sample 做 decision preview。回傳含固定安全旗標 + 是否 mutate 的 dict。"""
    overrides = sample.get("profile_overrides", {}) if apply_overrides else {}
    kwargs = {**profile, **overrides}
    task_row = sample["task_row"]
    is_container = isinstance(task_row, (dict, list))
    snapshot = copy.deepcopy(task_row) if is_container else task_row
    result = evaluate_auto_approval(task_row, **kwargs)
    mutated = is_container and task_row != snapshot
    return {
        "sample_name": sample["sample_name"],
        "policy_decision": result["policy_decision"],
        "matched_level": result["matched_level"],
        "reason": result["reason"],
        "can_auto_approve": result["can_auto_approve"],
        "can_execute": result["can_execute"],
        "queue_transition_allowed": result["queue_transition_allowed"],
        "observation_only": result["observation_only"],
        "input_unchanged": not mutated,
    }


def simulate_samples(samples: List[Dict[str, Any]], *, profile: Dict[str, Any],
                     apply_overrides: bool = True) -> List[Dict[str, Any]]:
    return [simulate_one(s, profile, apply_overrides=apply_overrides) for s in samples]


def summarize(rows: List[Dict[str, Any]]) -> Dict[str, int]:
    summary = {"auto_approved": 0, "needs_owner_approval": 0, "rejected": 0, "prohibited": 0}
    for r in rows:
        d = r["policy_decision"]
        if d in summary:
            summary[d] += 1
    summary["total"] = len(rows)
    return summary


def build_report(sample_filter: str = "all", *, profile_key: str = "safe") -> Dict[str, Any]:
    profile = SAFE_AUTOPILOT_PROFILE if profile_key == "safe" else DEFAULT_OFF_PROFILE
    apply_overrides = profile_key == "safe"
    selected = _select(build_samples(), sample_filter)
    rows = simulate_samples(selected, profile=profile, apply_overrides=apply_overrides)
    sample_rows = [{k: r[k] for k in SAMPLE_OUTPUT_FIELDS} for r in rows]
    return {
        "version": VERSION,
        "mode": "simulation",
        "profile": PROFILE_NAMES[profile_key],
        "observation_only": True,
        "samples": sample_rows,
        "summary": summarize(rows),
    }


def _format_human(report: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append(f"{report['version']} Auto-Approval Local-only Simulation"
                 f" — decision preview (mode={report['mode']}, profile={report['profile']})")
    lines.append("NOTE: simulation only. Decision preview does not mean queued and does not mean"
                 " execution.")
    lines.append("      can_execute / queue_transition_allowed are always false;"
                 " observation_only is always true.")
    lines.append("")
    for s in report["samples"]:
        lvl = "--" if s["matched_level"] is None else f"L{s['matched_level']}"
        lines.append(
            f"  [{s['policy_decision']:<20}] {s['sample_name']:<32} {lvl:<3}"
            f" reason={s['reason']:<34}"
            f" exec={s['can_execute']} queue={s['queue_transition_allowed']}"
            f" obs={s['observation_only']}"
        )
    su = report["summary"]
    lines.append("")
    lines.append(
        f"Summary: auto_approved={su['auto_approved']}"
        f" needs_owner_approval={su['needs_owner_approval']}"
        f" rejected={su['rejected']} prohibited={su['prohibited']} total={su['total']}"
    )
    if report["profile"] == "safe_autopilot":
        lines.append("Default-off note: with all flags off (--profile default-off), every sample"
                     " falls back to needs_owner_approval (no auto-approval, no execution).")
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="v0.7.2-C Auto-Approval Local-only Simulation (decision preview; "
                    "observation-only; no Queue, no Worker, no network).")
    parser.add_argument("--sample", choices=("all", *SAMPLE_GROUPS), default="all",
                        help="which sample group to preview (default: all)")
    parser.add_argument("--json", action="store_true",
                        help="emit valid JSON instead of human-readable text")
    parser.add_argument("--profile", choices=("safe", "default-off"), default="safe",
                        help="simulation profile (default: safe = safe_autopilot)")
    args = parser.parse_args(argv)

    report = build_report(args.sample, profile_key=args.profile)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(_format_human(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
