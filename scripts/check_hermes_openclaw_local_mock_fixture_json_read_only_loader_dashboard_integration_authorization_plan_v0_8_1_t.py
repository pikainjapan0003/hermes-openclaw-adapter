"""v0.8.1-T readiness check: Local Mock Fixture Read-only Loader Dashboard Integration Authorization Plan
(Dashboard integration authorization plan-only).

Pure local filesystem validation. This script reads only the v0.8.1-T authorization plan doc and
confirms the tracked state of the L/M/N/O/P/Q/R/S artifacts. It uses `git` read-only (ls-files / diff /
status) to confirm tracked status and that no extra repo files exist; it never modifies the git index.

It does NOT import Dashboard, app runtime, QueueStore, or any Worker/OpenClaw/Hermes/Google Sheets
integration; it reads no real queue DB, sends no POST, makes no network call, reads no secrets,
writes no repo file, modifies no loader, and modifies no Dashboard.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

T_DOC_PATH = REPO_ROOT / "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_DASHBOARD_INTEGRATION_AUTHORIZATION_PLAN_V0_8_1_T.md"
T_SCRIPT_PATH = REPO_ROOT / "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_dashboard_integration_authorization_plan_v0_8_1_t.py"

FIXTURE_PATH = REPO_ROOT / "fixtures/local_mock_data/hermes_openclaw_local_mock_messages_v0_8_1.json"
P_LOADER_PATH = REPO_ROOT / "scripts/load_local_mock_fixture_preview_v0_8_1.py"

M_DOC_PATH = REPO_ROOT / "docs/HERMES_OPENCLAW_LOCAL_MOCK_DATA_FIXTURE_JSON_ARTIFACT_VALIDATION_V0_8_1_M.md"
M_SCRIPT_PATH = REPO_ROOT / "scripts/check_hermes_openclaw_local_mock_data_fixture_json_artifact_validation_v0_8_1_m.py"

N_DOC_PATH = REPO_ROOT / "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_PLAN_V0_8_1_N.md"
N_SCRIPT_PATH = REPO_ROOT / "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_plan_v0_8_1_n.py"

O_DOC_PATH = REPO_ROOT / "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_IMPLEMENTATION_AUTHORIZATION_PLAN_V0_8_1_O.md"
O_SCRIPT_PATH = REPO_ROOT / "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_implementation_authorization_plan_v0_8_1_o.py"

Q_DOC_PATH = REPO_ROOT / "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_VALIDATION_PLAN_V0_8_1_Q.md"
Q_SCRIPT_PATH = REPO_ROOT / "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_validation_plan_v0_8_1_q.py"

R_SCRIPT_PATH = REPO_ROOT / "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_runtime_check_v0_8_1_r.py"

S_DOC_PATH = REPO_ROOT / "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_DASHBOARD_INTEGRATION_BOUNDARY_PLAN_V0_8_1_S.md"
S_SCRIPT_PATH = REPO_ROOT / "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_dashboard_integration_boundary_plan_v0_8_1_s.py"

EXPECTED_HEAD = "3bc3eeea9e9502e860e1148010e61a7b14de65fd"

REQUIRED_DOC_PHRASES = [
    "v0.8.1-T",
    "Dashboard Integration Authorization Plan",
    "Dashboard integration authorization plan-only",
    "HEAD = origin/master = 3bc3eeea9e9502e860e1148010e61a7b14de65fd",
    "v0.8.1-T does not modify Dashboard.",
    "v0.8.1-T does not modify loader.",
    "v0.8.1-T does not create a Dashboard route.",
    "v0.8.1-T does not create a Dashboard endpoint.",
    "v0.8.1-T does not create a Dashboard template.",
    "v0.8.1-T does not create a Dashboard static asset.",
    "v0.8.1-T does not read real queue DB.",
    "v0.8.1-T does not send POST.",
    "v0.8.1-T does not make network calls.",
    "v0.8.1-T does not start Worker.",
    "v0.8.1-T does not call OpenClaw.",
    "v0.8.1-T does not activate Hermes.",
    "v0.8.1-T does not read Google Sheets.",
    "v0.8.1-T does not write Google Sheets.",
    "v0.8.1-T does not read secrets.",
    "Future Dashboard integration authorization conditions, plan-only:",
    "Exact future implementation authorization phrase:",
    "批准實作 v0.8.1 local mock fixture read-only loader Dashboard preview integration",
    "Non-authorizing phrases:",
    "Forbidden future implementation actions unless separately approved by Owner:",
    "Required future validation before any implementation:",
    "Rollback boundary:",
    "Validation method, plan-only:",
    "Known pre-commit coupling:",
    "v0.8.1-T acceptance criteria:",
    "v0.8.1-U must not start unless separately approved by Owner using the exact future implementation authorization phrase.",
]

DASHBOARD_PROTECTED_PREFIXES = [
    "app/",
    "templates/",
    "static/",
]

PASS: list[str] = []
FAIL: list[str] = []


def ok(label: str) -> None:
    PASS.append(label)
    print(f"  ok : {label}")


def xx(label: str) -> None:
    FAIL.append(label)
    print(f"  XX : {label}")


def git_tracked(rel: str) -> bool:
    out = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "ls-files", "--", rel],
        capture_output=True,
        text=True,
    )
    return out.returncode == 0 and out.stdout.strip() != ""


# ---------------------------------------------------------------------------
# [A/B] T authorization plan doc + readiness script exist
# ---------------------------------------------------------------------------
print("[A] T authorization plan doc exists")
ok("A. T authorization plan doc exists") if T_DOC_PATH.exists() else xx("A. T authorization plan doc exists")
if not T_DOC_PATH.exists():
    print("\nXX T authorization plan doc 不存在，無法繼續")
    sys.exit(1)

print("[B] T readiness script path is correct")
ok("B. T readiness script exists at expected path") if T_SCRIPT_PATH.exists() else xx(
    "B. T readiness script exists at expected path"
)

doc = T_DOC_PATH.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# [C-J] L/M/N/O/P/Q/R/S artifacts exist and are tracked
# ---------------------------------------------------------------------------
print("[C] L fixture JSON exists and is tracked")
ok("C. L fixture JSON exists") if FIXTURE_PATH.exists() else xx("C. L fixture JSON exists")
ok("C. L fixture JSON is tracked") if git_tracked(
    "fixtures/local_mock_data/hermes_openclaw_local_mock_messages_v0_8_1.json"
) else xx("C. L fixture JSON is tracked")

print("[D] M validation doc/script exist and are tracked")
ok("D. M validation doc exists") if M_DOC_PATH.exists() else xx("D. M validation doc exists")
ok("D. M validation doc is tracked") if git_tracked(
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_DATA_FIXTURE_JSON_ARTIFACT_VALIDATION_V0_8_1_M.md"
) else xx("D. M validation doc is tracked")
ok("D. M validation script exists") if M_SCRIPT_PATH.exists() else xx("D. M validation script exists")
ok("D. M validation script is tracked") if git_tracked(
    "scripts/check_hermes_openclaw_local_mock_data_fixture_json_artifact_validation_v0_8_1_m.py"
) else xx("D. M validation script is tracked")

print("[E] N plan doc/script exist and are tracked")
ok("E. N plan doc exists") if N_DOC_PATH.exists() else xx("E. N plan doc exists")
ok("E. N plan doc is tracked") if git_tracked(
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_PLAN_V0_8_1_N.md"
) else xx("E. N plan doc is tracked")
ok("E. N readiness script exists") if N_SCRIPT_PATH.exists() else xx("E. N readiness script exists")
ok("E. N readiness script is tracked") if git_tracked(
    "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_plan_v0_8_1_n.py"
) else xx("E. N readiness script is tracked")

print("[F] O authorization doc/script exist and are tracked")
ok("F. O authorization doc exists") if O_DOC_PATH.exists() else xx("F. O authorization doc exists")
ok("F. O authorization doc is tracked") if git_tracked(
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_IMPLEMENTATION_AUTHORIZATION_PLAN_V0_8_1_O.md"
) else xx("F. O authorization doc is tracked")
ok("F. O readiness script exists") if O_SCRIPT_PATH.exists() else xx("F. O readiness script exists")
ok("F. O readiness script is tracked") if git_tracked(
    "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_implementation_authorization_plan_v0_8_1_o.py"
) else xx("F. O readiness script is tracked")

print("[G] P loader exists and is tracked")
ok("G. P loader exists") if P_LOADER_PATH.exists() else xx("G. P loader exists")
ok("G. P loader is tracked") if git_tracked(
    "scripts/load_local_mock_fixture_preview_v0_8_1.py"
) else xx("G. P loader is tracked")

print("[H] Q validation doc/script exist and are tracked")
ok("H. Q validation doc exists") if Q_DOC_PATH.exists() else xx("H. Q validation doc exists")
ok("H. Q validation doc is tracked") if git_tracked(
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_VALIDATION_PLAN_V0_8_1_Q.md"
) else xx("H. Q validation doc is tracked")
ok("H. Q readiness script exists") if Q_SCRIPT_PATH.exists() else xx("H. Q readiness script exists")
ok("H. Q readiness script is tracked") if git_tracked(
    "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_validation_plan_v0_8_1_q.py"
) else xx("H. Q readiness script is tracked")

print("[I] R runtime check script exists and is tracked")
ok("I. R runtime check script exists") if R_SCRIPT_PATH.exists() else xx("I. R runtime check script exists")
ok("I. R runtime check script is tracked") if git_tracked(
    "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_runtime_check_v0_8_1_r.py"
) else xx("I. R runtime check script is tracked")

print("[J] S boundary doc/script exist and are tracked")
ok("J. S boundary doc exists") if S_DOC_PATH.exists() else xx("J. S boundary doc exists")
ok("J. S boundary doc is tracked") if git_tracked(
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_DASHBOARD_INTEGRATION_BOUNDARY_PLAN_V0_8_1_S.md"
) else xx("J. S boundary doc is tracked")
ok("J. S readiness script exists") if S_SCRIPT_PATH.exists() else xx("J. S readiness script exists")
ok("J. S readiness script is tracked") if git_tracked(
    "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_dashboard_integration_boundary_plan_v0_8_1_s.py"
) else xx("J. S readiness script is tracked")

# ---------------------------------------------------------------------------
# [K] current master SHA present in T doc
# ---------------------------------------------------------------------------
print("[K] T doc contains current master SHA")
ok(f"K. T doc contains current master SHA {EXPECTED_HEAD}") if EXPECTED_HEAD in doc else xx(
    f"K. T doc contains current master SHA {EXPECTED_HEAD}"
)

# ---------------------------------------------------------------------------
# [L-AD] required doc phrases (positioning, prohibitions, authorization
#        conditions, exact phrase, non-authorizing phrases, forbidden
#        actions, required validation, rollback boundary, validation
#        method, pre-commit coupling, acceptance criteria, next step)
# ---------------------------------------------------------------------------
print("[L-AD] required doc phrases")
for phrase in REQUIRED_DOC_PHRASES:
    ok(f"doc contains「{phrase}」") if phrase in doc else xx(f"doc contains「{phrase}」")

# ---------------------------------------------------------------------------
# [AE] no tracked working-tree modifications
# ---------------------------------------------------------------------------
print("[AE] no tracked working-tree modifications")
diff_out = subprocess.run(
    ["git", "-C", str(REPO_ROOT), "diff", "--name-only"],
    capture_output=True,
    text=True,
)
tracked_changes = [l for l in diff_out.stdout.splitlines() if l.strip()]
ok("AE. no tracked working-tree modifications") if not tracked_changes else xx(
    f"AE. no tracked working-tree modifications（found {tracked_changes}）"
)

# ---------------------------------------------------------------------------
# [AF] no Dashboard/app/templates/static files changed (staged or unstaged)
# ---------------------------------------------------------------------------
print("[AF] no Dashboard/app/templates/static files changed")
status_out = subprocess.run(
    ["git", "-C", str(REPO_ROOT), "status", "--porcelain"],
    capture_output=True,
    text=True,
)
changed_paths = []
for line in status_out.stdout.splitlines():
    if not line.strip():
        continue
    # porcelain format: XY <path>  (path starts at column 3)
    path = line[3:].strip()
    changed_paths.append(path)
dashboard_changes = [
    p for p in changed_paths if any(p.startswith(pref) for pref in DASHBOARD_PROTECTED_PREFIXES)
]
ok("AF. no Dashboard/app/templates/static files changed") if not dashboard_changes else xx(
    f"AF. no Dashboard/app/templates/static files changed（found {dashboard_changes}）"
)

# ---------------------------------------------------------------------------
# [AG] no extra untracked files beyond allowed T files and existing patches/
# ---------------------------------------------------------------------------
print("[AG] no extra untracked files beyond allowed T files and patches/")
others_out = subprocess.run(
    ["git", "-C", str(REPO_ROOT), "ls-files", "--others", "--exclude-standard"],
    capture_output=True,
    text=True,
)
ALLOWED_UNTRACKED = {
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_DASHBOARD_INTEGRATION_AUTHORIZATION_PLAN_V0_8_1_T.md",
    "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_dashboard_integration_authorization_plan_v0_8_1_t.py",
}
untracked = [l for l in others_out.stdout.splitlines() if l.strip()]
unexpected = [
    u for u in untracked if u not in ALLOWED_UNTRACKED and not u.startswith("patches/")
]
ok("AG. no unexpected untracked files") if not unexpected else xx(
    f"AG. no unexpected untracked files（found {unexpected}）"
)

# ---------------------------------------------------------------------------
# 結果
# ---------------------------------------------------------------------------
total = len(PASS) + len(FAIL)
print(f"\n合計：{len(PASS)}/{total} 通過")
if FAIL:
    print(f"\nXX v0.8.1-T readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print("PASS: v0.8.1-T local mock fixture read-only loader dashboard integration authorization plan")
    sys.exit(0)
