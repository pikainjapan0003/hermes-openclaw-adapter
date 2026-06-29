"""v0.7.4-F synthetic test: Safe Local Cleanup Tool (dry-run-only).

Pure synthetic tests of the dry-run cleanup helper and CLI. Uses only in-memory
dicts and temp JSON files — no real queue, no POST, no apply, no queue data change.
Verifies the helper classifies candidates only by explicit metadata markers, blocks
production / external-side-effect / active-validation items, pins the fixed safety
values, and does not mutate its input; and that the CLI requires explicit input,
emits a JSON report for a synthetic temp JSON, and rejects apply-like arguments.
"""
import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.demo_task_cleanup_v0_7 import (  # noqa: E402
    derive_demo_task_cleanup_dry_run_report,
)

CLI_PATH = ROOT / "scripts" / "demo_task_cleanup_dry_run_v0_7_4_f.py"

PASS = []
FAIL = []


def check(label, cond):
    (PASS if cond else FAIL).append(label)
    print(f"  {'ok' if cond else 'XX'} : {label}")


def _write_temp_json(obj):
    tmpdir = tempfile.mkdtemp(prefix="v074f_synthetic_")
    path = Path(tmpdir) / "tasks.json"
    path.write_text(json.dumps(obj), encoding="utf-8")
    return str(path)


# ---------------------------------------------------------------------------
# [1] empty task list
# ---------------------------------------------------------------------------
print("[1] empty task list")
r_empty = derive_demo_task_cleanup_dry_run_report([])
check("empty list 回 dict", isinstance(r_empty, dict))
check("empty list candidate_count = 0", r_empty["candidate_count"] == 0)
check("empty list blocked_count = 0", r_empty["blocked_count"] == 0)

# ---------------------------------------------------------------------------
# [2] explicit demo marker candidate
# ---------------------------------------------------------------------------
print("[2] explicit demo marker candidate")
demo_task = {"task_id": "t1", "payload": {"metadata": {"demo_task": True}}}
r_demo = derive_demo_task_cleanup_dry_run_report([demo_task], target_environment="local")
check("explicit demo marker → candidate_count = 1", r_demo["candidate_count"] == 1)
check("explicit demo marker → blocked_count = 0", r_demo["blocked_count"] == 0)

# classification marker variant
class_task = {"task_id": "t2", "metadata": {"cleanup_classification": "sample"}}
r_class = derive_demo_task_cleanup_dry_run_report([class_task])
check("cleanup_classification=sample → candidate", r_class["candidate_count"] == 1)

# ---------------------------------------------------------------------------
# [3] does not classify by name alone
# ---------------------------------------------------------------------------
print("[3] does not classify by name alone")
name_only = {"task_id": "demo-sample-preview-test", "title": "demo sample task", "summary": "test"}
r_name = derive_demo_task_cleanup_dry_run_report([name_only])
check("name-only → not candidate (blocked)", r_name["candidate_count"] == 0 and r_name["blocked_count"] == 1)
check(
    "name-only blocked reason = no explicit marker",
    r_name["blocked_items"][0]["reason"] == "no explicit demo/sample/preview/test marker",
)

# ---------------------------------------------------------------------------
# [4] production marker blocked
# ---------------------------------------------------------------------------
print("[4] production marker blocked")
prod_task = {"task_id": "t3", "payload": {"metadata": {"demo_task": True, "production": True}}}
r_prod = derive_demo_task_cleanup_dry_run_report([prod_task])
check("production marker → blocked", r_prod["candidate_count"] == 0 and r_prod["blocked_count"] == 1)
check("production blocked reason", r_prod["blocked_items"][0]["reason"] == "production marker present")

# ---------------------------------------------------------------------------
# [5] external side effect marker blocked
# ---------------------------------------------------------------------------
print("[5] external side effect marker blocked")
ext_task = {"task_id": "t4", "metadata": {"demo_task": True, "external_side_effect": True}}
r_ext = derive_demo_task_cleanup_dry_run_report([ext_task])
check("external side effect → blocked", r_ext["blocked_count"] == 1 and r_ext["candidate_count"] == 0)
check(
    "external side effect blocked reason",
    r_ext["blocked_items"][0]["reason"] == "external side effect marker present",
)

# secret-like marker blocked (value never echoed)
secret_task = {"task_id": "t5", "metadata": {"demo_task": True, "client_secret": "shhh"}}
r_secret = derive_demo_task_cleanup_dry_run_report([secret_task])
check("secret-like marker → blocked", r_secret["blocked_count"] == 1)
check("secret value not echoed in report", "shhh" not in json.dumps(r_secret))

# ---------------------------------------------------------------------------
# [6] active validation blocked unless replacement approved
# ---------------------------------------------------------------------------
print("[6] active validation gate")
active_task = {"task_id": "t6", "metadata": {"demo_task": True, "active_validation": True}}
r_active = derive_demo_task_cleanup_dry_run_report([active_task])
check("active validation → blocked", r_active["blocked_count"] == 1 and r_active["candidate_count"] == 0)
active_ok = {
    "task_id": "t7",
    "metadata": {"demo_task": True, "active_validation": True, "owner_approved_replacement": True},
}
r_active_ok = derive_demo_task_cleanup_dry_run_report([active_ok])
check("active validation + owner_approved_replacement → candidate", r_active_ok["candidate_count"] == 1)

# target_environment not local/preview blocks every task
r_badenv = derive_demo_task_cleanup_dry_run_report([demo_task], target_environment="production")
check("bad target_environment → all blocked", r_badenv["candidate_count"] == 0 and r_badenv["blocked_count"] == 1)

# ---------------------------------------------------------------------------
# [7] fixed safety values
# ---------------------------------------------------------------------------
print("[7] fixed safety values")
FIXED = {
    "execution_mode": "dry_run_only",
    "dry_run": True,
    "apply_requested": False,
    "apply_allowed": False,
    "would_delete": False,
    "would_archive": False,
    "would_modify": False,
    "external_side_effects": False,
    "owner_approval_required": True,
}
for key, expected in FIXED.items():
    check(f"fixed {key} == {expected!r}", r_demo[key] == expected)

# ---------------------------------------------------------------------------
# [8] input not mutated
# ---------------------------------------------------------------------------
print("[8] input not mutated")
original = [{"task_id": "t8", "payload": {"metadata": {"demo_task": True}}}]
snapshot = copy.deepcopy(original)
_ = derive_demo_task_cleanup_dry_run_report(original)
check("input task list 未被 mutate", original == snapshot)

# ---------------------------------------------------------------------------
# [9] CLI requires explicit input
# ---------------------------------------------------------------------------
print("[9] CLI requires explicit input")
proc_noinput = subprocess.run(
    [sys.executable, str(CLI_PATH)],
    capture_output=True,
    text=True,
)
check("CLI without --input → nonzero exit", proc_noinput.returncode != 0)

# ---------------------------------------------------------------------------
# [10] CLI outputs JSON report for synthetic temp JSON
# ---------------------------------------------------------------------------
print("[10] CLI outputs JSON for synthetic temp JSON")
tmp_json = _write_temp_json([
    {"task_id": "t9", "payload": {"metadata": {"demo_task": True}}},
    {"task_id": "t10", "metadata": {"production": True}},
])
proc_ok = subprocess.run(
    [sys.executable, str(CLI_PATH), "--input", tmp_json, "--source-queue", "synthetic", "--target-environment", "local"],
    capture_output=True,
    text=True,
)
check("CLI with synthetic input → exit 0", proc_ok.returncode == 0)
cli_report = None
try:
    cli_report = json.loads(proc_ok.stdout)
except Exception:  # noqa: BLE001
    cli_report = None
check("CLI stdout is JSON report", isinstance(cli_report, dict))
check("CLI report dry_run = True", bool(cli_report) and cli_report.get("dry_run") is True)
check("CLI report apply_allowed = False", bool(cli_report) and cli_report.get("apply_allowed") is False)
check("CLI report candidate_count = 1", bool(cli_report) and cli_report.get("candidate_count") == 1)

# ---------------------------------------------------------------------------
# [11] CLI rejects apply-like arguments (without applying anything)
# ---------------------------------------------------------------------------
print("[11] CLI rejects apply-like arguments")
for bad_arg in ("--apply", "--confirm-apply", "apply"):
    proc_apply = subprocess.run(
        [sys.executable, str(CLI_PATH), "--input", tmp_json, bad_arg],
        capture_output=True,
        text=True,
    )
    rejected = proc_apply.returncode != 0 and "blocked" in proc_apply.stderr.lower()
    no_report = proc_apply.stdout.strip() == ""
    check(f"CLI rejects «{bad_arg}» (nonzero + blocked, no report)", rejected and no_report)

# ---------------------------------------------------------------------------
# 結果
# ---------------------------------------------------------------------------
total = len(PASS) + len(FAIL)
print(f"\n合計：{len(PASS)}/{total} 通過")
if FAIL:
    print(f"\nXX v0.7.4-F dry-run tool test 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print("\nv0.7.4-F Safe Local Cleanup Tool dry-run test: ALL PASS")
    sys.exit(0)
