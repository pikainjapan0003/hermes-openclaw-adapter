#!/usr/bin/env python3
"""v0.7.2-C — Auto-Approval Local-only Simulation 測試（純函式 / 不連任何系統）。

直接 import simulation 模組（不開子行程），驗證：
  - 所有 sample 都能跑、輸出含每個 sample name；
  - safe profile 下每筆 decision / matched_level / reason 與 expected 相符；
  - summary counts 與逐筆統計一致；
  - --json 為 valid JSON 且每筆含固定欄位；
  - 每筆 can_execute / queue_transition_allowed / observation_only 恆為 false/false/true；
  - level0/level1 → auto_approved；level2 → needs_owner；level3 → prohibited；
    kill switch → rejected；unknown/missing/invalid → fail-closed needs_owner；
  - default-off profile 下所有 sample → needs_owner_approval；
  - simulation 不 mutate sample task_row；
  - simulation 只 import evaluate_auto_approval，不 import main/queue_store/worker/result_sink/
    sqlite3/requests/subprocess/google/gspread/oauth，且無 QueueStore/approve/reject/claim_next/
    run_openclaw_cli/route/webhook 痕跡。
"""

from __future__ import annotations

import copy
import importlib.util
import io
import json
import re
import sys
from contextlib import redirect_stdout
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
SIM_PATH = SCRIPTS / "simulate_auto_approval_policy_v0_7_2_c.py"

_spec = importlib.util.spec_from_file_location("sim_c_mod", SIM_PATH)
sim = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sim)

FAILURES: list[str] = []

SAFE_FIELDS = ("can_execute", "queue_transition_allowed", "observation_only")


def _assert(cond: bool, label: str) -> None:
    print(f"  {'ok ' if cond else 'XX '}: {label}")
    if not cond:
        FAILURES.append(label)


def _capture(argv: list[str]) -> tuple[int, str]:
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = sim.main(argv)
    return rc, buf.getvalue()


def _fixed_safe_fields(r: dict) -> bool:
    return (r["can_execute"] is False
            and r["queue_transition_allowed"] is False
            and r["observation_only"] is True)


def main() -> int:
    samples = sim.build_samples()

    # --- sample catalog 覆蓋 Level 0–3 + edge ---
    groups = {s["group"] for s in samples}
    for g in ("level0", "level1", "level2", "level3", "edge"):
        _assert(g in groups, f"sample catalog 含 group {g}")
    _assert(len(samples) >= 38, f"sample 數量足夠（實際 {len(samples)}）")
    names = [s["sample_name"] for s in samples]
    _assert(len(names) == len(set(names)), "sample name 不重複")

    # --- safe profile：逐筆 decision / matched_level / reason 與 expected 相符 ---
    rows = sim.simulate_samples(samples, profile=sim.SAFE_AUTOPILOT_PROFILE, apply_overrides=True)
    by_name = {r["sample_name"]: r for r in rows}
    for s in samples:
        nm = s["sample_name"]
        r = by_name[nm]
        exp = s["expected"]
        _assert(r["policy_decision"] == exp["policy_decision"],
                f"{nm} → policy_decision={exp['policy_decision']}")
        _assert(r["matched_level"] == exp["matched_level"],
                f"{nm} → matched_level={exp['matched_level']}")
        _assert(r["reason"] == exp["reason"], f"{nm} → reason={exp['reason']}")

    # --- 每筆固定安全旗標 + 不被 mutate ---
    for r in rows:
        _assert(_fixed_safe_fields(r), f"{r['sample_name']} 安全欄位固定（exec/queue/obs）")
        _assert(r["input_unchanged"] is True, f"{r['sample_name']} 未 mutate task_row")
    # auto_approved 仍 can_execute=false / queue_transition_allowed=false
    for r in rows:
        if r["policy_decision"] == "auto_approved":
            _assert(r["can_auto_approve"] is True and r["can_execute"] is False
                    and r["queue_transition_allowed"] is False,
                    f"{r['sample_name']} auto_approved 不代表 queued / 不代表執行")

    # --- 分群行為（safe profile）---
    for s in samples:
        nm, grp = s["sample_name"], s["group"]
        d = by_name[nm]["policy_decision"]
        if grp == "level0":
            _assert(d == "auto_approved" and by_name[nm]["matched_level"] == 0,
                    f"{nm} (level0) → auto_approved L0")
        elif grp == "level1":
            _assert(d == "auto_approved" and by_name[nm]["matched_level"] == 1,
                    f"{nm} (level1) → auto_approved L1")
        elif grp == "level2":
            _assert(d == "needs_owner_approval", f"{nm} (level2) → needs_owner_approval")
        elif grp == "level3":
            _assert(d == "prohibited", f"{nm} (level3) → prohibited")

    # --- kill switch → rejected ---
    _assert(by_name["kill_switch_global"]["policy_decision"] == "rejected",
            "kill_switch_global → rejected")
    _assert(by_name["kill_switch_auto_approval"]["policy_decision"] == "rejected",
            "kill_switch_auto_approval → rejected")

    # --- unknown / missing / invalid → fail-closed needs_owner ---
    for nm in ("unknown_task_type", "missing_safety_level", "invalid_safety_level",
               "task_row_not_dict", "payload_missing_or_invalid", "invalid_requested_operations",
               "invalid_touched_files", "unsupported_auto_approval_mode"):
        _assert(by_name[nm]["policy_decision"] == "needs_owner_approval",
                f"{nm} → fail-closed needs_owner_approval")

    # --- summary counts 與逐筆一致 ---
    su = sim.summarize(rows)
    recomputed = {"auto_approved": 0, "needs_owner_approval": 0, "rejected": 0, "prohibited": 0}
    for r in rows:
        recomputed[r["policy_decision"]] += 1
    for k, v in recomputed.items():
        _assert(su[k] == v, f"summary[{k}]={v} 與逐筆一致")
    _assert(su["total"] == len(rows), "summary total 與 sample 數一致")

    # --- default-off profile：全部 → needs_owner_approval；安全旗標仍固定 ---
    off_rows = sim.simulate_samples(samples, profile=sim.DEFAULT_OFF_PROFILE, apply_overrides=False)
    for r in off_rows:
        _assert(r["policy_decision"] == "needs_owner_approval",
                f"{r['sample_name']} default-off → needs_owner_approval")
        _assert(_fixed_safe_fields(r), f"{r['sample_name']} default-off 安全欄位仍固定")

    # --- CLI：--sample all 輸出含每個 sample name ---
    rc, out = _capture(["--sample", "all"])
    _assert(rc == 0, "main --sample all 回傳 0")
    for nm in names:
        _assert(nm in out, f"human 輸出含 sample name {nm}")

    # --- CLI：--json 為 valid JSON 且 schema 正確 ---
    rc, js = _capture(["--json"])
    _assert(rc == 0, "main --json 回傳 0")
    data = json.loads(js)  # 若非 valid JSON 會丟例外（測試失敗）
    _assert(data["version"] == "v0.7.2-C", "json version=v0.7.2-C")
    _assert(data["mode"] == "simulation", "json mode=simulation")
    _assert(data["profile"] == "safe_autopilot", "json profile=safe_autopilot")
    _assert(data["observation_only"] is True, "json observation_only=true")
    _assert(len(data["samples"]) == len(samples), "json samples 數與 catalog 一致")
    required_keys = ("sample_name", "policy_decision", "matched_level", "reason",
                     "can_auto_approve", "can_execute", "queue_transition_allowed",
                     "observation_only")
    for entry in data["samples"]:
        for k in required_keys:
            _assert(k in entry, f"json sample {entry.get('sample_name')} 含欄位 {k}")
        _assert(entry["can_execute"] is False, f"json {entry['sample_name']} can_execute=false")
        _assert(entry["queue_transition_allowed"] is False,
                f"json {entry['sample_name']} queue_transition_allowed=false")
        _assert(entry["observation_only"] is True,
                f"json {entry['sample_name']} observation_only=true")
    for k in ("auto_approved", "needs_owner_approval", "rejected", "prohibited", "total"):
        _assert(k in data["summary"], f"json summary 含 {k}")

    # --- default-off CLI 也是 valid JSON 且全 needs_owner ---
    rc, js2 = _capture(["--profile", "default-off", "--json"])
    data2 = json.loads(js2)
    _assert(data2["profile"] == "default_off", "json default-off profile=default_off")
    _assert(all(e["policy_decision"] == "needs_owner_approval" for e in data2["samples"]),
            "default-off json 全部 needs_owner_approval")

    # --- 靜態：simulation import 邊界 / 無接線痕跡 ---
    src = SIM_PATH.read_text(encoding="utf-8")
    _assert("evaluate_auto_approval" in src, "simulation 含 evaluate_auto_approval")
    _assert(re.search(r"^\s*from\s+app\.auto_approval_policy_v0_7\s+import\s+.*evaluate_auto_approval",
                      src, re.MULTILINE) is not None,
            "simulation import evaluate_auto_approval")
    forbidden_imports = (r"app\.main", r"app\.queue_store", r"app\.worker", r"app\.result_sink",
                         r"sqlite3", r"requests", r"subprocess",
                         r"google", r"googleapiclient", r"gspread", r"oauth")
    for mod in forbidden_imports:
        imp = re.compile(rf"^\s*(?:import|from)\s+\S*{mod}\b", re.MULTILINE | re.IGNORECASE)
        _assert(imp.search(src) is None, f"simulation 未 import {mod}")
    forbidden_tokens = ("QueueStore", "claim_next", "run_openclaw_cli", ".approve(", ".reject(",
                        "add_api_route", "APIRouter", "FastAPI(", "@app.", "@router.",
                        "subprocess.", "skip_permissions", "dangerously-skip-permissions",
                        "unrestricted", "bypass")
    for tok in forbidden_tokens:
        _assert(tok not in src, f"simulation 無接線/危險痕跡「{tok}」")

    if FAILURES:
        print(f"\nXX v0.7.2-C simulation 測試失敗 {len(FAILURES)} 項：")
        for f in FAILURES:
            print(f"   - {f}")
        return 1
    print("\nOK v0.7.2-C auto-approval local-only simulation 測試全數通過"
          "（decision preview / observation-only / 未接線 / 未 mutate）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
