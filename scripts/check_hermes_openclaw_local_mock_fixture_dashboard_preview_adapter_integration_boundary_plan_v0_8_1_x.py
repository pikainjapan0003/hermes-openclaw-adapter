"""v0.8.1-X readiness check: Local Mock Fixture Dashboard Preview Adapter Integration Boundary Plan
(boundary plan-only).

Pure local filesystem + git metadata validation. This script reads only the v0.8.1-X boundary plan
doc and confirms the tracked state of the L/M/N/O/P/Q/R/S/T/U/V/W artifacts. It uses `git` read-only
(ls-files / diff / status / merge-base) to confirm tracked status, ancestry, and that no extra repo
files exist; it never modifies the git index.

It does NOT import Dashboard, app runtime, QueueStore, the v0.8.1-V adapter, the v0.8.1-P loader, or
any Worker/OpenClaw/Hermes/Google Sheets integration; it reads no real queue DB, sends no POST, makes
no network call, reads no secrets, writes no repo file, modifies no adapter, modifies no loader, and
modifies no Dashboard. It does not read the fixture JSON directly.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

X_DOC_PATH = REPO_ROOT / "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_DASHBOARD_PREVIEW_ADAPTER_INTEGRATION_BOUNDARY_PLAN_V0_8_1_X.md"
X_SCRIPT_PATH = REPO_ROOT / "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_integration_boundary_plan_v0_8_1_x.py"

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

T_DOC_PATH = REPO_ROOT / "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_DASHBOARD_INTEGRATION_AUTHORIZATION_PLAN_V0_8_1_T.md"
T_SCRIPT_PATH = REPO_ROOT / "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_dashboard_integration_authorization_plan_v0_8_1_t.py"

U_DOC_PATH = REPO_ROOT / "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_DASHBOARD_PREVIEW_INTEGRATION_IMPLEMENTATION_PLAN_V0_8_1_U.md"
U_SCRIPT_PATH = REPO_ROOT / "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_dashboard_preview_integration_implementation_plan_v0_8_1_u.py"

V_ADAPTER_PATH = REPO_ROOT / "scripts/local_mock_fixture_dashboard_preview_adapter_v0_8_1.py"
V_READINESS_PATH = REPO_ROOT / "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_v0_8_1_v.py"

W_SCRIPT_PATH = REPO_ROOT / "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_runtime_check_v0_8_1_w.py"

EXPECTED_BASE_HEAD = "3b1b1bcaa248b5f2706d75a84ccaa366198cf91f"

REQUIRED_DOC_PHRASES = [
    "v0.8.1-X is a boundary plan only.",
    "v0.8.1-X does not implement Dashboard integration.",
    "v0.8.1-X does not modify Dashboard.",
    "v0.8.1-X does not modify adapter.",
    "v0.8.1-X does not modify loader.",
    "v0.8.1-X only defines the future safe boundary for Dashboard to consume the v0.8.1-V read-only preview adapter.",
    f"Base HEAD / origin/master:\n{EXPECTED_BASE_HEAD}",
    "Future Dashboard integration must consume only:",
    "build_dashboard_preview_model()",
    "build_dashboard_preview_rows()",
    "Dashboard must not call:\nload_local_mock_fixture_preview()",
    "validate_local_mock_fixture_preview_object()",
    "Do not read fixture JSON directly from Dashboard.",
    "Do not read real queue DB.",
    "Do not call QueueStore.",
    "Do not POST.",
    "Do not make network calls.",
    "Do not start Worker.",
    "Do not call OpenClaw.",
    "Do not activate Hermes.",
    "Do not read Google Sheets.",
    "Do not write Google Sheets.",
    "Do not read secrets.",
    "Do not create .env.",
    "Do not create webhook.",
    "Do not create connector.",
    "Do not create production DB.",
    "Do not create shared DB.",
    "Do not create Remote Blackboard API runtime.",
    "Do not expose execution controls.",
    "Do not expose dispatch controls.",
    "Do not expose external actions.",
    "Dashboard display must be read-only.",
    "Dashboard display must show disabled runtime badges.",
    "Dashboard display must show or preserve local_only = True.",
    "Dashboard display must show or preserve read_only = True.",
    "Dashboard display must show or preserve is_mock = True.",
    "Dashboard display must show or preserve execution_permission = False.",
    "Dashboard display must show or preserve dispatch_permission = False.",
    "Dashboard display must show or preserve external_side_effects_permission = False.",
    "Dashboard display must not expose execution controls.",
    "Dashboard display must not expose dispatch controls.",
    "Dashboard display must not expose external action controls.",
    "Dashboard display must not expose action_url, post_url, webhook_url, endpoint_url, execute_url, dispatch_url.",
    "Future separately approved integration may modify only explicitly approved Dashboard preview files.",
    "v0.8.1-X itself creates none of these files.",
    "v0.8.1-X itself modifies none of these files.",
    "Future validation requirements, plan-only:",
    "Rollback boundary, plan-only:",
    "Recommended next step:\nv0.8.1-Y — Dashboard Preview Adapter Integration Authorization Plan",
    "v0.8.1-Y is not started by v0.8.1-X.",
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
# [A/B] X boundary plan doc + readiness script exist
# ---------------------------------------------------------------------------
print("[A] X doc exists")
ok("A. X doc exists") if X_DOC_PATH.exists() else xx("A. X doc exists")
if not X_DOC_PATH.exists():
    print("\nXX X boundary plan doc 不存在，無法繼續")
    sys.exit(1)

print("[B] X readiness script path is correct")
ok("B. X readiness script exists at expected path") if X_SCRIPT_PATH.exists() else xx(
    "B. X readiness script exists at expected path"
)

doc = X_DOC_PATH.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# [C-N] L/M/N/O/P/Q/R/S/T/U/V/W artifacts exist and are tracked
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

print("[K] T authorization doc/script exist and are tracked")
ok("K. T authorization doc exists") if T_DOC_PATH.exists() else xx("K. T authorization doc exists")
ok("K. T authorization doc is tracked") if git_tracked(
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_DASHBOARD_INTEGRATION_AUTHORIZATION_PLAN_V0_8_1_T.md"
) else xx("K. T authorization doc is tracked")
ok("K. T readiness script exists") if T_SCRIPT_PATH.exists() else xx("K. T readiness script exists")
ok("K. T readiness script is tracked") if git_tracked(
    "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_dashboard_integration_authorization_plan_v0_8_1_t.py"
) else xx("K. T readiness script is tracked")

print("[L] U implementation plan doc/script exist and are tracked")
ok("L. U implementation plan doc exists") if U_DOC_PATH.exists() else xx("L. U implementation plan doc exists")
ok("L. U implementation plan doc is tracked") if git_tracked(
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_DASHBOARD_PREVIEW_INTEGRATION_IMPLEMENTATION_PLAN_V0_8_1_U.md"
) else xx("L. U implementation plan doc is tracked")
ok("L. U readiness script exists") if U_SCRIPT_PATH.exists() else xx("L. U readiness script exists")
ok("L. U readiness script is tracked") if git_tracked(
    "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_dashboard_preview_integration_implementation_plan_v0_8_1_u.py"
) else xx("L. U readiness script is tracked")

print("[M] V adapter/readiness script exist and are tracked")
ok("M. V adapter exists") if V_ADAPTER_PATH.exists() else xx("M. V adapter exists")
ok("M. V adapter is tracked") if git_tracked(
    "scripts/local_mock_fixture_dashboard_preview_adapter_v0_8_1.py"
) else xx("M. V adapter is tracked")
ok("M. V readiness script exists") if V_READINESS_PATH.exists() else xx("M. V readiness script exists")
ok("M. V readiness script is tracked") if git_tracked(
    "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_v0_8_1_v.py"
) else xx("M. V readiness script is tracked")

print("[N] W runtime check script exists and is tracked")
ok("N. W runtime check script exists") if W_SCRIPT_PATH.exists() else xx("N. W runtime check script exists")
ok("N. W runtime check script is tracked") if git_tracked(
    "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_runtime_check_v0_8_1_w.py"
) else xx("N. W runtime check script is tracked")

# ---------------------------------------------------------------------------
# [O] current HEAD contains EXPECTED_BASE_HEAD in git history
# ---------------------------------------------------------------------------
print("[O] current HEAD contains EXPECTED_BASE_HEAD in git history")
ancestor_check = subprocess.run(
    ["git", "-C", str(REPO_ROOT), "merge-base", "--is-ancestor", EXPECTED_BASE_HEAD, "HEAD"],
    capture_output=True,
    text=True,
)
ok(f"O. HEAD contains {EXPECTED_BASE_HEAD} in git history") if ancestor_check.returncode == 0 else xx(
    f"O. HEAD contains {EXPECTED_BASE_HEAD} in git history（merge-base check failed）"
)

# ---------------------------------------------------------------------------
# [P-AQ] required doc phrases (title, base HEAD, plan-only positioning,
#        prohibitions, data entry point, safe output requirements, forbidden
#        actions, future candidate files, validation requirements, rollback
#        boundary, next step)
# ---------------------------------------------------------------------------
print("[P-AQ] required doc phrases")
ok("P. X doc contains v0.8.1-X title") if "v0.8.1-X" in doc and "Dashboard Preview Adapter Integration Boundary Plan" in doc else xx(
    "P. X doc contains v0.8.1-X title"
)
for phrase in REQUIRED_DOC_PHRASES:
    ok(f"doc contains「{phrase}」") if phrase in doc else xx(f"doc contains「{phrase}」")

# ---------------------------------------------------------------------------
# [AR] no tracked working-tree modifications
# ---------------------------------------------------------------------------
print("[AR] no tracked working-tree modifications")
diff_out = subprocess.run(
    ["git", "-C", str(REPO_ROOT), "diff", "--name-only"],
    capture_output=True,
    text=True,
)
tracked_changes = [l for l in diff_out.stdout.splitlines() if l.strip()]
ok("AR. no tracked working-tree modifications") if not tracked_changes else xx(
    f"AR. no tracked working-tree modifications（found {tracked_changes}）"
)

# ---------------------------------------------------------------------------
# [AS] no Dashboard/app/templates/static files changed (staged or unstaged)
# ---------------------------------------------------------------------------
print("[AS] no Dashboard/app/templates/static files changed")
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
ok("AS. no Dashboard/app/templates/static files changed") if not dashboard_changes else xx(
    f"AS. no Dashboard/app/templates/static files changed（found {dashboard_changes}）"
)

# ---------------------------------------------------------------------------
# [AT] no extra untracked files beyond allowed X files and existing patches/
# ---------------------------------------------------------------------------
print("[AT] no extra untracked files beyond allowed X files and patches/")
others_out = subprocess.run(
    ["git", "-C", str(REPO_ROOT), "ls-files", "--others", "--exclude-standard"],
    capture_output=True,
    text=True,
)
ALLOWED_UNTRACKED = {
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_DASHBOARD_PREVIEW_ADAPTER_INTEGRATION_BOUNDARY_PLAN_V0_8_1_X.md",
    "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_integration_boundary_plan_v0_8_1_x.py",
}
untracked = [l for l in others_out.stdout.splitlines() if l.strip()]
unexpected = [
    u for u in untracked if u not in ALLOWED_UNTRACKED and not u.startswith("patches/")
]
ok("AT. no unexpected untracked files") if not unexpected else xx(
    f"AT. no unexpected untracked files（found {unexpected}）"
)

# ---------------------------------------------------------------------------
# 結果
# ---------------------------------------------------------------------------
total = len(PASS) + len(FAIL)
print(f"\n合計：{len(PASS)}/{total} 通過")
if FAIL:
    print(f"\nXX v0.8.1-X readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print("PASS: v0.8.1-X dashboard preview adapter integration boundary plan")
    sys.exit(0)
