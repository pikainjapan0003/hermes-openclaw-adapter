"""v0.8.2-D readiness check: Dashboard Read-only Preview UI Validation Hardening Plan (plan-only).

Pure local filesystem + git metadata validation. This script reads only the v0.8.2-D plan doc and
confirms the tracked/untracked state of the v0.8.2-D plan doc/readiness script and the surfaces it
plans over (app/main.py, templates/system.html, static/dashboard.css, the v0.8.2-C validation script,
the v0.8.2-B plan doc/readiness script, the v0.8.2-A validation script, the P loader, the V adapter,
the fixture JSON, and the W/X/Y/Z artifacts). It uses `git` read-only (ls-files / diff / status /
merge-base) to confirm tracked status, ancestry, and that no tracked file was modified; it never
modifies the git index.

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

D_DOC_REL = "docs/HERMES_OPENCLAW_DASHBOARD_READ_ONLY_PREVIEW_UI_VALIDATION_HARDENING_PLAN_V0_8_2_D.md"
D_DOC_PATH = REPO_ROOT / D_DOC_REL
D_SCRIPT_REL = "scripts/check_hermes_openclaw_dashboard_read_only_preview_ui_validation_hardening_plan_v0_8_2_d.py"
D_SCRIPT_PATH = REPO_ROOT / D_SCRIPT_REL

MAIN_PY_REL = "app/main.py"
SYSTEM_HTML_REL = "templates/system.html"
DASHBOARD_CSS_REL = "static/dashboard.css"
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

EXPECTED_BASE_HEAD = "1ee0bd597eb3d5f56028482389eb33a6cf9ccc97"

ALLOWED_NEW_UNTRACKED = {D_DOC_REL, D_SCRIPT_REL}

EXACT_V082E_PHRASE = (
    "批准實作 v0.8.2-E — Dashboard Read-only Preview UI Validation Hardening Implementation，"
    "僅允許新增或調整 validation hardening artifacts，以更穩定驗證 v0.8.2-C 已完成的 "
    "/dashboard/system read-only preview UI；必須保持 GET-only、read-only、synthetic local-only、"
    "permission flags false、disabled runtime badges visible；"
    "不得修改 Dashboard route，不得修改資料來源，不得呼叫 P loader，不得直接讀 fixture JSON，"
    "不得讀 real queue DB，不得 POST，"
    "不得新增 button/form/action URL/webhook/endpoint/execute/dispatch/send controls，"
    "不得啟 Worker/OpenClaw/Hermes/Google Sheets，不得讀 secrets，"
    "不得建立 production/shared DB 或 Remote Blackboard API runtime。"
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
    "E implemented",
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
# [B/C] D plan doc / D readiness script exist at expected path
# ---------------------------------------------------------------------------
print("[B] D plan doc exists at expected path")
check("B. D plan doc exists at expected path", D_DOC_PATH.exists())

print("[C] D readiness script exists at expected path")
check("C. D readiness script exists at expected path", D_SCRIPT_PATH.exists())

# ---------------------------------------------------------------------------
# [D/E] D plan doc / D readiness script are currently untracked (Owner Review phase)
# ---------------------------------------------------------------------------
print("[D] D plan doc is currently untracked in Owner Review phase")
check("D. D plan doc is currently untracked in Owner Review phase", not git_tracked(D_DOC_REL))

print("[E] D readiness script is currently untracked in Owner Review phase")
check(
    "E. D readiness script is currently untracked in Owner Review phase",
    not git_tracked(D_SCRIPT_REL),
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
# [G] untracked files allowed only: D doc, D script, patches/*
# ---------------------------------------------------------------------------
print("[G] untracked files allowed only: D doc, D script, patches/*")
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
# [H-Q] no protected artifact modified
# ---------------------------------------------------------------------------
print("[H] app/main.py is not modified")
check("H. app/main.py is not modified", MAIN_PY_REL not in tracked_changed)

print("[I] templates/system.html is not modified")
check("I. templates/system.html is not modified", SYSTEM_HTML_REL not in tracked_changed)

print("[J] static/dashboard.css is not modified")
check("J. static/dashboard.css is not modified", DASHBOARD_CSS_REL not in tracked_changed)

print("[K] C validation script is not modified")
check("K. C validation script is not modified", C_SCRIPT_REL not in tracked_changed)

print("[L] B doc / B readiness script are not modified")
check(
    "L. B doc / B readiness script are not modified",
    B_DOC_REL not in tracked_changed and B_SCRIPT_REL not in tracked_changed,
)

print("[M] v0.8.2-A validation script is not modified")
check("M. v0.8.2-A validation script is not modified", V082A_SCRIPT_REL not in tracked_changed)

print("[N] P loader is not modified")
check("N. P loader is not modified", P_LOADER_REL not in tracked_changed)

print("[O] V adapter is not modified")
check("O. V adapter is not modified", V_ADAPTER_REL not in tracked_changed)

print("[P] fixture JSON is not modified")
check("P. fixture JSON is not modified", FIXTURE_JSON_REL not in tracked_changed)

print("[Q] W/X/Y/Z artifacts are not modified")
check("Q. W/X/Y/Z artifacts are not modified", not (tracked_changed & PROTECTED_WXYZ))

# ---------------------------------------------------------------------------
# [R-Y] D plan doc content checks
# ---------------------------------------------------------------------------
d_doc_text = D_DOC_PATH.read_text(encoding="utf-8") if D_DOC_PATH.exists() else ""

print('[R] D plan doc contains "plan-only"')
check('R. D plan doc contains "plan-only"', "plan-only" in d_doc_text)

print('[S] D plan doc contains "NOT IMPLEMENTED"')
check('S. D plan doc contains "NOT IMPLEMENTED"', "NOT IMPLEMENTED" in d_doc_text)

print('[T] D plan doc contains "v0.8.2-C = DONE / PUSHED / CLOSED"')
check(
    'T. D plan doc contains "v0.8.2-C = DONE / PUSHED / CLOSED"',
    "v0.8.2-C = DONE / PUSHED / CLOSED" in d_doc_text,
)

print('[U] D plan doc contains "Validation Hardening Problems To Solve"')
check(
    'U. D plan doc contains "Validation Hardening Problems To Solve"',
    "Validation Hardening Problems To Solve" in d_doc_text,
)

print('[V] D plan doc contains "Proposed Future v0.8.2-E Scope"')
check(
    'V. D plan doc contains "Proposed Future v0.8.2-E Scope"',
    "Proposed Future v0.8.2-E Scope" in d_doc_text,
)

print("[W] D plan doc contains the exact future v0.8.2-E authorization phrase exactly once")
check(
    "W. D plan doc contains the exact future v0.8.2-E authorization phrase exactly once",
    d_doc_text.count(EXACT_V082E_PHRASE) == 1,
)

print("[X] D plan doc contains all required safety boundaries")
check(
    "X. D plan doc contains all required safety boundaries",
    all(b in d_doc_text for b in REQUIRED_SAFETY_BOUNDARIES),
)

print("[Y] D plan doc does not contain unsafe done-claims")
check(
    "Y. D plan doc does not contain unsafe done-claims",
    not any(c in d_doc_text for c in UNSAFE_DONE_CLAIMS),
)

# ---------------------------------------------------------------------------
# [Z] patches/ remains untracked and untouched
# ---------------------------------------------------------------------------
print("[Z] patches/ remains untracked and untouched")
check(
    "Z. patches/ remains untracked and untouched",
    not any(p.startswith("patches/") for p in tracked_changed),
)

# ---------------------------------------------------------------------------
# 結果
# ---------------------------------------------------------------------------
total = len(PASS) + len(FAIL)
print(f"\n合計：{len(PASS)}/{total} 通過")
if FAIL:
    print(f"\nXX v0.8.2-D readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print("PASS: v0.8.2-D dashboard read-only preview UI validation hardening plan")
    sys.exit(0)
