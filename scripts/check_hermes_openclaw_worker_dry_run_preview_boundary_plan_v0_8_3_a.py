"""v0.8.3-A readiness check: Worker Dry-run Preview Boundary Plan (plan-only).

Pure local filesystem + git metadata validation. This script reads only the v0.8.3-A boundary plan doc
and confirms the tracked/untracked state of the v0.8.3-A doc/readiness script and the surfaces it must
not touch (app/main.py, templates/system.html, static/dashboard.css, the v0.8.2-F closeout doc/readiness
script, the v0.8.2-E validation script, the v0.8.2-D plan doc/readiness script, the v0.8.2-C validation
script, the v0.8.2-B plan doc/readiness script, the v0.8.2-A validation script, the P loader, the V
adapter, the fixture JSON, and the W/X/Y/Z artifacts). It uses `git` read-only (ls-files / diff / status
/ merge-base) to confirm tracked status, ancestry, and that no tracked file was modified; it never
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

A_DOC_REL = "docs/HERMES_OPENCLAW_WORKER_DRY_RUN_PREVIEW_BOUNDARY_PLAN_V0_8_3_A.md"
A_DOC_PATH = REPO_ROOT / A_DOC_REL
A_SCRIPT_REL = "scripts/check_hermes_openclaw_worker_dry_run_preview_boundary_plan_v0_8_3_a.py"
A_SCRIPT_PATH = REPO_ROOT / A_SCRIPT_REL

MAIN_PY_REL = "app/main.py"
SYSTEM_HTML_REL = "templates/system.html"
DASHBOARD_CSS_REL = "static/dashboard.css"
F_DOC_REL = "docs/HERMES_OPENCLAW_DASHBOARD_READ_ONLY_PREVIEW_VALIDATION_CLOSEOUT_HANDOFF_PLAN_V0_8_2_F.md"
F_SCRIPT_REL = "scripts/check_hermes_openclaw_dashboard_read_only_preview_validation_closeout_handoff_plan_v0_8_2_f.py"
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

EXPECTED_BASE_HEAD = "706ad9c5eac0db37ab71f033c160effc71cfc7ba"

ALLOWED_NEW_UNTRACKED = {A_DOC_REL, A_SCRIPT_REL}

EXACT_V083B_PHRASE = (
    "批准實作 v0.8.3-B — Worker Dry-run Preview Boundary Implementation，"
    "僅允許新增 Worker dry-run preview boundary artifacts 與 read-only validation artifacts，"
    "用 synthetic local-only preview input 描述未來 Worker 可能檢查的任務，"
    "不得啟動 Worker，不得執行 Worker loop，不得呼叫 OpenClaw，不得啟動或連接 Hermes，"
    "不得讀寫 Google Sheets，不得讀 real queue DB，不得寫 queue，不得 POST，"
    "不得新增 execute/dispatch/send controls，不得讀 secrets，不得建立 webhook/endpoint/connector，"
    "不得建立 production/shared DB 或 Remote Blackboard API runtime。"
)

REQUIRED_DRY_RUN_CONTRACT_FIELDS = [
    "dry_run_id",
    "synthetic_local_only",
    "proposed_worker_action",
    "execution_permission = false",
    "dispatch_permission = false",
    "external_side_effects_permission = false",
    "worker_started = false",
    "openclaw_called = false",
    "hermes_called = false",
    "google_sheets_enabled = false",
]

REQUIRED_FORBIDDEN_BOUNDARY_PHRASES = [
    "no true Worker",
    "no Worker loop",
    "no OpenClaw call",
    "no Hermes activation",
    "no Google Sheets read/write",
    "no real queue DB read/write",
    "no POST",
    "no execute/dispatch/send controls",
    "no secrets",
    "no webhook/endpoint/connector",
    "no production/shared DB",
    "no Remote Blackboard API runtime",
]

UNSAFE_DONE_CLAIMS = [
    "Worker started",
    "OpenClaw connected",
    "Hermes connected",
    "Google Sheets enabled",
    "POST enabled",
    "queue write enabled",
    "secrets read",
    "production DB created",
    "Remote Blackboard API runtime created",
    "v0.8.3-B started",
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
# [B/C] v0.8.3-A doc / v0.8.3-A readiness script exist at expected path
# ---------------------------------------------------------------------------
print("[B] v0.8.3-A boundary plan doc exists at expected path")
check("B. v0.8.3-A boundary plan doc exists at expected path", A_DOC_PATH.exists())

print("[C] v0.8.3-A readiness script exists at expected path")
check("C. v0.8.3-A readiness script exists at expected path", A_SCRIPT_PATH.exists())

# ---------------------------------------------------------------------------
# [D/E] v0.8.3-A doc / readiness script are currently untracked (Owner Review phase)
# ---------------------------------------------------------------------------
print("[D] v0.8.3-A boundary plan doc is currently untracked in Owner Review phase")
check(
    "D. v0.8.3-A boundary plan doc is currently untracked in Owner Review phase",
    not git_tracked(A_DOC_REL),
)

print("[E] v0.8.3-A readiness script is currently untracked in Owner Review phase")
check(
    "E. v0.8.3-A readiness script is currently untracked in Owner Review phase",
    not git_tracked(A_SCRIPT_REL),
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
# [G] untracked files allowed only: v0.8.3-A doc, v0.8.3-A script, patches/*
# ---------------------------------------------------------------------------
print("[G] untracked files allowed only: v0.8.3-A doc, v0.8.3-A script, patches/*")
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
# [H-T] no protected artifact modified
# ---------------------------------------------------------------------------
print("[H] app/main.py is not modified")
check("H. app/main.py is not modified", MAIN_PY_REL not in tracked_changed)

print("[I] templates/system.html is not modified")
check("I. templates/system.html is not modified", SYSTEM_HTML_REL not in tracked_changed)

print("[J] static/dashboard.css is not modified")
check("J. static/dashboard.css is not modified", DASHBOARD_CSS_REL not in tracked_changed)

print("[K] F closeout doc/readiness script are not modified")
check(
    "K. F closeout doc/readiness script are not modified",
    F_DOC_REL not in tracked_changed and F_SCRIPT_REL not in tracked_changed,
)

print("[L] E validation script is not modified")
check("L. E validation script is not modified", E_SCRIPT_REL not in tracked_changed)

print("[M] D plan/readiness script are not modified")
check(
    "M. D plan/readiness script are not modified",
    D_DOC_REL not in tracked_changed and D_SCRIPT_REL not in tracked_changed,
)

print("[N] C validation script is not modified")
check("N. C validation script is not modified", C_SCRIPT_REL not in tracked_changed)

print("[O] B doc/readiness script are not modified")
check(
    "O. B doc/readiness script are not modified",
    B_DOC_REL not in tracked_changed and B_SCRIPT_REL not in tracked_changed,
)

print("[P] v0.8.2-A validation script is not modified")
check("P. v0.8.2-A validation script is not modified", V082A_SCRIPT_REL not in tracked_changed)

print("[Q] P loader is not modified")
check("Q. P loader is not modified", P_LOADER_REL not in tracked_changed)

print("[R] V adapter is not modified")
check("R. V adapter is not modified", V_ADAPTER_REL not in tracked_changed)

print("[S] fixture JSON is not modified")
check("S. fixture JSON is not modified", FIXTURE_JSON_REL not in tracked_changed)

print("[T] W/X/Y/Z artifacts are not modified")
check("T. W/X/Y/Z artifacts are not modified", not (tracked_changed & PROTECTED_WXYZ))

# ---------------------------------------------------------------------------
# [U-Z] v0.8.3-A doc content status markers
# ---------------------------------------------------------------------------
a_doc_text = A_DOC_PATH.read_text(encoding="utf-8") if A_DOC_PATH.exists() else ""

print('[U] v0.8.3-A doc contains "plan-only / boundary plan"')
check('U. v0.8.3-A doc contains "plan-only / boundary plan"', "plan-only / boundary plan" in a_doc_text)

print('[V] v0.8.3-A doc contains "Worker status: OFF / NOT STARTED"')
check(
    'V. v0.8.3-A doc contains "Worker status: OFF / NOT STARTED"',
    "Worker status: OFF / NOT STARTED" in a_doc_text,
)

print('[W] v0.8.3-A doc contains "OpenClaw status: NOT CONNECTED"')
check(
    'W. v0.8.3-A doc contains "OpenClaw status: NOT CONNECTED"',
    "OpenClaw status: NOT CONNECTED" in a_doc_text,
)

print('[X] v0.8.3-A doc contains "Hermes status: NOT CONNECTED"')
check(
    'X. v0.8.3-A doc contains "Hermes status: NOT CONNECTED"',
    "Hermes status: NOT CONNECTED" in a_doc_text,
)

print('[Y] v0.8.3-A doc contains "Google Sheets status: DISABLED"')
check(
    'Y. v0.8.3-A doc contains "Google Sheets status: DISABLED"',
    "Google Sheets status: DISABLED" in a_doc_text,
)

print('[Z] v0.8.3-A doc contains "v0.8.3-B status: NOT STARTED"')
check(
    'Z. v0.8.3-A doc contains "v0.8.3-B status: NOT STARTED"',
    "v0.8.3-B status: NOT STARTED" in a_doc_text,
)

# ---------------------------------------------------------------------------
# [AA] exact future v0.8.3-B authorization phrase exactly once
# ---------------------------------------------------------------------------
print("[AA] v0.8.3-A doc contains exact future v0.8.3-B authorization phrase exactly once")
check(
    "AA. v0.8.3-A doc contains exact future v0.8.3-B authorization phrase exactly once",
    a_doc_text.count(EXACT_V083B_PHRASE) == 1,
)

# ---------------------------------------------------------------------------
# [AB] required dry-run contract fields present
# ---------------------------------------------------------------------------
print("[AB] v0.8.3-A doc contains required dry-run contract fields")
missing_fields = [f for f in REQUIRED_DRY_RUN_CONTRACT_FIELDS if f not in a_doc_text]
check(
    f"AB. v0.8.3-A doc contains required dry-run contract fields（missing {missing_fields}）"
    if missing_fields
    else "AB. v0.8.3-A doc contains required dry-run contract fields",
    not missing_fields,
)

# ---------------------------------------------------------------------------
# [AC] required forbidden boundary phrases present
# ---------------------------------------------------------------------------
print("[AC] v0.8.3-A doc contains all required forbidden boundary phrases")
missing_forbidden = [p for p in REQUIRED_FORBIDDEN_BOUNDARY_PHRASES if p not in a_doc_text]
check(
    f"AC. v0.8.3-A doc contains all required forbidden boundary phrases（missing {missing_forbidden}）"
    if missing_forbidden
    else "AC. v0.8.3-A doc contains all required forbidden boundary phrases",
    not missing_forbidden,
)

# ---------------------------------------------------------------------------
# [AD] no unsafe done-claims present
# ---------------------------------------------------------------------------
print("[AD] v0.8.3-A doc does not contain unsafe done-claims")
found_unsafe = [c for c in UNSAFE_DONE_CLAIMS if c in a_doc_text]
check(
    f"AD. v0.8.3-A doc does not contain unsafe done-claims（found {found_unsafe}）"
    if found_unsafe
    else "AD. v0.8.3-A doc does not contain unsafe done-claims",
    not found_unsafe,
)

# ---------------------------------------------------------------------------
# [AE] patches/ remains untracked and untouched
# ---------------------------------------------------------------------------
print("[AE] patches/ remains untracked and untouched")
check(
    "AE. patches/ remains untracked and untouched",
    not any(p.startswith("patches/") for p in tracked_changed),
)

# ---------------------------------------------------------------------------
# 結果
# ---------------------------------------------------------------------------
total = len(PASS) + len(FAIL)
print(f"\n合計：{len(PASS)}/{total} 通過")
if FAIL:
    print(f"\nXX v0.8.3-A readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print("PASS: v0.8.3-A worker dry-run preview boundary plan")
    sys.exit(0)
