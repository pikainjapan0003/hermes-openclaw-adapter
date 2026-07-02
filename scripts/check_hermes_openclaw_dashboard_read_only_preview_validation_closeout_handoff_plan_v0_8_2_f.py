"""v0.8.2-F readiness check: Dashboard Read-only Preview Validation Closeout / Handoff Plan (plan-only).

Pure local filesystem + git metadata validation. This script reads only the v0.8.2-F closeout/handoff
doc and confirms the tracked/untracked state of the v0.8.2-F doc/readiness script and the surfaces it
summarizes over (app/main.py, templates/system.html, static/dashboard.css, the v0.8.2-E validation
script, the v0.8.2-D plan doc/readiness script, the v0.8.2-C validation script, the v0.8.2-B plan
doc/readiness script, the v0.8.2-A validation script, the P loader, the V adapter, the fixture JSON,
and the W/X/Y/Z artifacts). It uses `git` read-only (ls-files / diff / status / merge-base) to confirm
tracked status, ancestry, and that no tracked file was modified; it never modifies the git index.

It does NOT import app runtime, Dashboard runtime, QueueStore, Worker/OpenClaw/Hermes/Google Sheets
integration, the v0.8.1-P loader, or the v0.8.1-V adapter; it never starts a server; it reads no real
queue DB, sends no POST, makes no network call, reads no secrets, writes no repo file, and modifies no
git index.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

F_DOC_REL = "docs/HERMES_OPENCLAW_DASHBOARD_READ_ONLY_PREVIEW_VALIDATION_CLOSEOUT_HANDOFF_PLAN_V0_8_2_F.md"
F_DOC_PATH = REPO_ROOT / F_DOC_REL
F_SCRIPT_REL = "scripts/check_hermes_openclaw_dashboard_read_only_preview_validation_closeout_handoff_plan_v0_8_2_f.py"
F_SCRIPT_PATH = REPO_ROOT / F_SCRIPT_REL

MAIN_PY_REL = "app/main.py"
SYSTEM_HTML_REL = "templates/system.html"
DASHBOARD_CSS_REL = "static/dashboard.css"
E_SCRIPT_REL = "scripts/check_hermes_openclaw_dashboard_read_only_preview_ui_validation_hardening_v0_8_2_e.py"
D_DOC_REL = "docs/HERMES_OPENCLAW_DASHBOARD_READ_ONLY_PREVIEW_UI_VALIDATION_HARDENING_PLAN_V0_8_2_D.md"
D_SCRIPT_REL = "scripts/check_hermes_openclaw_dashboard_read_only_preview_ui_validation_hardening_plan_v0_8_2_d.py"
C_SCRIPT_REL = "scripts/check_hermes_openclaw_dashboard_read_only_preview_ui_refinement_v0_8_2_c.py"
B_DOC_REL = "docs/HERMES_OPENCLAW_DASHBOARD_READ_ONLY_PREVIEW_UI_REFINEMENT_PLAN_V0_8_2_B.md"
B_SCRIPT_REL = "scripts/check_hermes_openclaw_dashboard_read_only_preview_ui_refinement_plan_v0_8_2_b.py"
V082A_SCRIPT_REL = "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_read_only_display_integration_v0_8_2_a.py"
P_LOADER_REL = "scripts/load_local_mock_fixture_preview_v0_8_1.py"
V_ADAPTER_REL = "scripts/local_mock_fixture_dashboard_preview_adapter_v0_8_1.py"
FIXTURE_JSON_REL = "fixtures/local_mock_data/hermes_openclaw_local_mock_messages_v0_8_1.json"
PROTECTED_WXYZ = {
    "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_runtime_check_v0_8_1_w.py",
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_DASHBOARD_PREVIEW_ADAPTER_INTEGRATION_BOUNDARY_PLAN_V0_8_1_X.md",
    "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_integration_boundary_plan_v0_8_1_x.py",
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_DASHBOARD_PREVIEW_ADAPTER_INTEGRATION_AUTHORIZATION_PLAN_V0_8_1_Y.md",
    "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_integration_authorization_plan_v0_8_1_y.py",
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_DASHBOARD_PREVIEW_ADAPTER_INTEGRATION_IMPLEMENTATION_PLAN_V0_8_1_Z.md",
    "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_integration_implementation_plan_v0_8_1_z.py",
}

EXPECTED_BASE_HEAD = "98cf8115ee7389742a9763dc3660911ea220115a"

ALLOWED_NEW_UNTRACKED = {F_DOC_REL, F_SCRIPT_REL}

EXACT_V083A_PHRASE = (
    "批准規劃 v0.8.3-A — Worker Dry-run Preview Boundary Plan，"
    "僅允許建立 Worker dry-run preview 的邊界計畫與 readiness 檢查設計；"
    "不得啟動 Worker，不得呼叫 OpenClaw，不得啟動或連接 Hermes，不得讀寫 Google Sheets，"
    "不得讀 real queue DB，不得 POST，不得新增 execute/dispatch/send controls，"
    "不得讀 secrets，不得建立 production/shared DB 或 Remote Blackboard API runtime。"
)

REQUIRED_SAFETY_BOUNDARIES = [
    "GET-only",
    "read-only",
    "synthetic local-only",
    "permission flags false",
    "disabled runtime badges visible",
    "no POST",
    "no button/form/action URL",
    "no Worker/OpenClaw/Hermes/Google Sheets",
    "no secrets",
    "no real queue DB",
    "no Remote Blackboard API runtime",
]

UNSAFE_DONE_CLAIMS = [
    "v0.8.3 started",
    "Worker started",
    "OpenClaw connected",
    "Hermes connected",
    "Google Sheets enabled",
    "POST enabled",
    "production DB created",
    "tag created",
]

PASS: list[str] = []
FAIL: list[str] = []


def ok(label: str) -> None:
    PASS.append(label)
    print(f"  ok : {label}")


def xx(label: str) -> None:
    FAIL.append(label)
    print(f"  XX : {label}")


def check(label: str, condition: bool) -> None:
    ok(label) if condition else xx(label)


def run_git(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args],
        capture_output=True,
        text=True,
    )


def git_lines(args: list[str]) -> list[str]:
    out = run_git(args)
    return [line for line in out.stdout.splitlines() if line.strip()]


def git_tracked(rel: str) -> bool:
    out = run_git(["ls-files", "--", rel])
    return out.returncode == 0 and out.stdout.strip() != ""


def working_tree_change_names() -> set[str]:
    return set(git_lines(["diff", "--name-only"]))


def untracked_names() -> set[str]:
    return set(git_lines(["ls-files", "--others", "--exclude-standard"]))


# ---------------------------------------------------------------------------
# [A] current HEAD contains EXPECTED_BASE_HEAD in git history
# ---------------------------------------------------------------------------
print("[A] current HEAD contains EXPECTED_BASE_HEAD in git history")
ancestor_check = run_git(["merge-base", "--is-ancestor", EXPECTED_BASE_HEAD, "HEAD"])
check(
    f"A. HEAD contains {EXPECTED_BASE_HEAD} in git history",
    ancestor_check.returncode == 0,
)

# ---------------------------------------------------------------------------
# [B/C] F closeout handoff doc / F readiness script exist at expected path
# ---------------------------------------------------------------------------
print("[B] F closeout handoff doc exists at expected path")
check("B. F closeout handoff doc exists at expected path", F_DOC_PATH.exists())

print("[C] F readiness script exists at expected path")
check("C. F readiness script exists at expected path", F_SCRIPT_PATH.exists())

# ---------------------------------------------------------------------------
# [D/E] F doc / F readiness script are currently untracked (Owner Review phase)
# ---------------------------------------------------------------------------
print("[D] F closeout handoff doc is currently untracked in Owner Review phase")
check(
    "D. F closeout handoff doc is currently untracked in Owner Review phase",
    not git_tracked(F_DOC_REL),
)

print("[E] F readiness script is currently untracked in Owner Review phase")
check(
    "E. F readiness script is currently untracked in Owner Review phase",
    not git_tracked(F_SCRIPT_REL),
)

# ---------------------------------------------------------------------------
# [F] git diff has no tracked file changes
# ---------------------------------------------------------------------------
print("[F] git diff has no tracked file changes")
tracked_changed = working_tree_change_names()
check(
    f"F. git diff has no tracked file changes（found {sorted(tracked_changed)}）"
    if tracked_changed
    else "F. git diff has no tracked file changes",
    not tracked_changed,
)

# ---------------------------------------------------------------------------
# [G] untracked files allowed only: F doc, F script, patches/*
# ---------------------------------------------------------------------------
print("[G] untracked files allowed only: F doc, F script, patches/*")
untracked = untracked_names()
unexpected_untracked = {
    u for u in untracked if u not in ALLOWED_NEW_UNTRACKED and not u.startswith("patches/")
}
check(
    f"G. no unexpected untracked files（found {sorted(unexpected_untracked)}）"
    if unexpected_untracked
    else "G. no unexpected untracked files",
    not unexpected_untracked,
)

# ---------------------------------------------------------------------------
# [H-S] no protected artifact modified
# ---------------------------------------------------------------------------
print("[H] app/main.py is not modified")
check("H. app/main.py is not modified", MAIN_PY_REL not in tracked_changed)

print("[I] templates/system.html is not modified")
check("I. templates/system.html is not modified", SYSTEM_HTML_REL not in tracked_changed)

print("[J] static/dashboard.css is not modified")
check("J. static/dashboard.css is not modified", DASHBOARD_CSS_REL not in tracked_changed)

print("[K] E validation script is not modified")
check("K. E validation script is not modified", E_SCRIPT_REL not in tracked_changed)

print("[L] D plan/readiness script are not modified")
check(
    "L. D plan/readiness script are not modified",
    D_DOC_REL not in tracked_changed and D_SCRIPT_REL not in tracked_changed,
)

print("[M] C validation script is not modified")
check("M. C validation script is not modified", C_SCRIPT_REL not in tracked_changed)

print("[N] B doc/readiness script are not modified")
check(
    "N. B doc/readiness script are not modified",
    B_DOC_REL not in tracked_changed and B_SCRIPT_REL not in tracked_changed,
)

print("[O] v0.8.2-A validation script is not modified")
check("O. v0.8.2-A validation script is not modified", V082A_SCRIPT_REL not in tracked_changed)

print("[P] P loader is not modified")
check("P. P loader is not modified", P_LOADER_REL not in tracked_changed)

print("[Q] V adapter is not modified")
check("Q. V adapter is not modified", V_ADAPTER_REL not in tracked_changed)

print("[R] fixture JSON is not modified")
check("R. fixture JSON is not modified", FIXTURE_JSON_REL not in tracked_changed)

print("[S] W/X/Y/Z artifacts are not modified")
check("S. W/X/Y/Z artifacts are not modified", not (tracked_changed & PROTECTED_WXYZ))

# ---------------------------------------------------------------------------
# [T-AA] F doc content checks
# ---------------------------------------------------------------------------
f_doc_text = F_DOC_PATH.read_text(encoding="utf-8") if F_DOC_PATH.exists() else ""

print('[T] F doc contains "plan-only / closeout / handoff"')
check('T. F doc contains "plan-only / closeout / handoff"', "plan-only / closeout / handoff" in f_doc_text)

print('[U] F doc contains "v0.8.2-E = DONE / PUSHED / CLOSED"')
check(
    'U. F doc contains "v0.8.2-E = DONE / PUSHED / CLOSED"',
    "v0.8.2-E = DONE / PUSHED / CLOSED" in f_doc_text,
)

print('[V] F doc contains "Stable Validation Gates"')
check('V. F doc contains "Stable Validation Gates"', "Stable Validation Gates" in f_doc_text)

print('[W] F doc contains "Owner Review-only / Phase-limited Gates"')
check(
    'W. F doc contains "Owner Review-only / Phase-limited Gates"',
    "Owner Review-only / Phase-limited Gates" in f_doc_text,
)

print('[X] F doc contains "v0.8.3 status: NOT STARTED"')
check('X. F doc contains "v0.8.3 status: NOT STARTED"', "v0.8.3 status: NOT STARTED" in f_doc_text)

print("[Y] F doc contains exact future v0.8.3-A authorization phrase exactly once")
check(
    "Y. F doc contains exact future v0.8.3-A authorization phrase exactly once",
    f_doc_text.count(EXACT_V083A_PHRASE) == 1,
)

print("[Z] F doc contains all required safety boundaries")
check(
    "Z. F doc contains all required safety boundaries",
    all(b in f_doc_text for b in REQUIRED_SAFETY_BOUNDARIES),
)

print("[AA] F doc does not contain unsafe done-claims")
check(
    "AA. F doc does not contain unsafe done-claims",
    not any(c in f_doc_text for c in UNSAFE_DONE_CLAIMS),
)

# ---------------------------------------------------------------------------
# [AC-AE] F doc describes the E gate nuance accurately
# ---------------------------------------------------------------------------
print('[AC] F doc contains "Important nuance for the E gate"')
check(
    'AC. F doc contains "Important nuance for the E gate"',
    "Important nuance for the E gate" in f_doc_text,
)

print('[AD] F doc contains "not as a Dashboard content or safety-boundary failure"')
check(
    'AD. F doc contains "not as a Dashboard content or safety-boundary failure"',
    "not as a Dashboard content or safety-boundary failure" in f_doc_text,
)

print('[AE] F doc contains "not fully immune to later Owner Review untracked artifacts"')
check(
    'AE. F doc contains "not fully immune to later Owner Review untracked artifacts"',
    "not fully immune to later Owner Review untracked artifacts" in f_doc_text,
)

# ---------------------------------------------------------------------------
# [AB] patches/ remains untracked and untouched
# ---------------------------------------------------------------------------
print("[AB] patches/ remains untracked and untouched")
check(
    "AB. patches/ remains untracked and untouched",
    not any(p.startswith("patches/") for p in tracked_changed),
)

# ---------------------------------------------------------------------------
# 結果
# ---------------------------------------------------------------------------
total = len(PASS) + len(FAIL)
print(f"\n合計：{len(PASS)}/{total} 通過")
if FAIL:
    print(f"\nXX v0.8.2-F readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print("PASS: v0.8.2-F dashboard read-only preview validation closeout handoff plan")
    sys.exit(0)
