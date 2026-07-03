"""v0.8.3-E readiness check: Worker Dry-run Preview Dashboard Display Closeout / Validation
Hardening Plan (plan-only).

Pure local filesystem + git metadata validation, plus a local import of the v0.8.3-B standalone
builder module (read-only reference check) to confirm its returned model stays safe, and a plain
read of the currently committed `app/main.py` / `templates/system.html` / `static/dashboard.css`
(read-only text scan, not a diff) to confirm the v0.8.3-D Dashboard display is still present. This
script reads only the v0.8.3-E doc/readiness-script and the v0.8.3-D/C/B/A/F/D(v0.8.2)/... artifacts
for read-only reference, and confirms the tracked/untracked state of the v0.8.3-E files and the
surfaces they must not touch (app/main.py, templates/system.html, static/dashboard.css, the v0.8.3-D
validation script, the v0.8.3-C plan doc/readiness script, the v0.8.3-B doc/fixture/builder/readiness
script, the v0.8.3-A plan doc/readiness script, the v0.8.2-F closeout doc/readiness script, the
v0.8.2-E validation script, the v0.8.2-D plan doc/readiness script, the v0.8.2-C validation script,
the v0.8.2-B plan doc/readiness script, the v0.8.2-A validation script, the P loader, the V adapter,
the old v0.8.1 fixture JSON, and the W/X/Y/Z artifacts). It uses `git` read-only (ls-files / diff /
status / merge-base) to confirm tracked status, ancestry, and that no tracked file was modified; it
never modifies the git index.

It does NOT import app runtime, Dashboard runtime, QueueStore, Worker/OpenClaw/Hermes/Google Sheets
integration, the v0.8.1-P loader, or the v0.8.1-V adapter; it never starts a server; it reads no real
queue DB, sends no POST, makes no network call, reads no secrets, writes no repo file, and modifies no
git index. It only imports the v0.8.3-B builder module (standard library only) to call its public
function and inspect the returned dict, as a read-only reference re-check. It never modifies
app/main.py, templates/system.html, static/dashboard.css, or the v0.8.3-D validation script - it only
reads their current committed text.
"""
from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

E_DOC_REL = "docs/HERMES_OPENCLAW_WORKER_DRY_RUN_PREVIEW_DASHBOARD_DISPLAY_CLOSEOUT_VALIDATION_HARDENING_PLAN_V0_8_3_E.md"
E_DOC_PATH = REPO_ROOT / E_DOC_REL
E_SCRIPT_REL = "scripts/check_hermes_openclaw_worker_dry_run_preview_dashboard_display_closeout_validation_hardening_plan_v0_8_3_e.py"
E_SCRIPT_PATH = REPO_ROOT / E_SCRIPT_REL

MAIN_PY_REL = "app/main.py"
MAIN_PY_PATH = REPO_ROOT / MAIN_PY_REL
SYSTEM_HTML_REL = "templates/system.html"
SYSTEM_HTML_PATH = REPO_ROOT / SYSTEM_HTML_REL
DASHBOARD_CSS_REL = "static/dashboard.css"
DASHBOARD_CSS_PATH = REPO_ROOT / DASHBOARD_CSS_REL

D_SCRIPT_REL = "scripts/check_hermes_openclaw_worker_dry_run_preview_dashboard_read_only_display_implementation_v0_8_3_d.py"

C_DOC_REL = "docs/HERMES_OPENCLAW_WORKER_DRY_RUN_PREVIEW_DASHBOARD_READ_ONLY_DISPLAY_PLAN_V0_8_3_C.md"
C_SCRIPT_REL = "scripts/check_hermes_openclaw_worker_dry_run_preview_dashboard_read_only_display_plan_v0_8_3_c.py"

B_DOC_REL = "docs/HERMES_OPENCLAW_WORKER_DRY_RUN_PREVIEW_BOUNDARY_IMPLEMENTATION_V0_8_3_B.md"
B_FIXTURE_REL = "fixtures/local_mock_data/hermes_openclaw_worker_dry_run_preview_v0_8_3_b.json"
B_BUILDER_REL = "scripts/worker_dry_run_preview_boundary_v0_8_3_b.py"
B_BUILDER_PATH = REPO_ROOT / B_BUILDER_REL
B_SCRIPT_REL = "scripts/check_hermes_openclaw_worker_dry_run_preview_boundary_implementation_v0_8_3_b.py"

A_DOC_REL = "docs/HERMES_OPENCLAW_WORKER_DRY_RUN_PREVIEW_BOUNDARY_PLAN_V0_8_3_A.md"
A_SCRIPT_REL = "scripts/check_hermes_openclaw_worker_dry_run_preview_boundary_plan_v0_8_3_a.py"

F_DOC_REL = "docs/HERMES_OPENCLAW_DASHBOARD_READ_ONLY_PREVIEW_VALIDATION_CLOSEOUT_HANDOFF_PLAN_V0_8_2_F.md"
F_SCRIPT_REL = "scripts/check_hermes_openclaw_dashboard_read_only_preview_validation_closeout_handoff_plan_v0_8_2_f.py"

E082_SCRIPT_REL = "scripts/check_hermes_openclaw_dashboard_read_only_preview_ui_validation_hardening_v0_8_2_e.py"

D082_DOC_REL = "docs/HERMES_OPENCLAW_DASHBOARD_READ_ONLY_PREVIEW_UI_VALIDATION_HARDENING_PLAN_V0_8_2_D.md"
D082_SCRIPT_REL = "scripts/check_hermes_openclaw_dashboard_read_only_preview_ui_validation_hardening_plan_v0_8_2_d.py"

C082_SCRIPT_REL = "scripts/check_hermes_openclaw_dashboard_read_only_preview_ui_refinement_v0_8_2_c.py"

B082_DOC_REL = "docs/HERMES_OPENCLAW_DASHBOARD_READ_ONLY_PREVIEW_UI_REFINEMENT_PLAN_V0_8_2_B.md"
B082_SCRIPT_REL = "scripts/check_hermes_openclaw_dashboard_read_only_preview_ui_refinement_plan_v0_8_2_b.py"

A082_SCRIPT_REL = "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_read_only_display_integration_v0_8_2_a.py"

P_LOADER_REL = "scripts/load_local_mock_fixture_preview_v0_8_1.py"
V_ADAPTER_REL = "scripts/local_mock_fixture_dashboard_preview_adapter_v0_8_1.py"
OLD_FIXTURE_JSON_REL = "fixtures/local_mock_data/hermes_openclaw_local_mock_messages_v0_8_1.json"
PROTECTED_WXYZ = {
    "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_runtime_check_v0_8_1_w.py",
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_DASHBOARD_PREVIEW_ADAPTER_INTEGRATION_BOUNDARY_PLAN_V0_8_1_X.md",
    "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_integration_boundary_plan_v0_8_1_x.py",
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_DASHBOARD_PREVIEW_ADAPTER_INTEGRATION_AUTHORIZATION_PLAN_V0_8_1_Y.md",
    "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_integration_authorization_plan_v0_8_1_y.py",
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_DASHBOARD_PREVIEW_ADAPTER_INTEGRATION_IMPLEMENTATION_PLAN_V0_8_1_Z.md",
    "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_integration_implementation_plan_v0_8_1_z.py",
}

EXPECTED_BASE_HEAD = "58194a1b17392e050dd8c27f6cee8f8b761d3f4e"

ALLOWED_NEW_UNTRACKED = {E_DOC_REL, E_SCRIPT_REL}

EXACT_V083F_PHRASE = (
    "批准實作 v0.8.3-F — Worker Dry-run Preview Dashboard Display Validation Hardening Implementation，"
    "僅允許新增或調整 validation hardening artifacts，以穩定驗證已完成的 v0.8.3-D "
    "`/dashboard/system` Worker dry-run preview read-only display 是否維持 GET-only、read-only、"
    "synthetic local-only，且 v0.8.3-B Worker dry-run preview model 僅作為顯示用途；"
    "不得修改 Dashboard route，不得新增 POST，不得新增 button/form/action URL，不得啟動 Worker，"
    "不得執行 Worker loop，不得呼叫 OpenClaw，不得啟動或連接 Hermes，不得讀寫 Google Sheets，"
    "不得讀 real queue DB，不得寫 queue，不得讀 secrets，不得建立 webhook/endpoint/connector，"
    "不得建立 production/shared DB 或 Remote Blackboard API runtime。"
)

REQUIRED_TEXT_MARKERS = [
    "plan-only / closeout and validation hardening plan",
    "Base commit: 58194a1b17392e050dd8c27f6cee8f8b761d3f4e",
    "v0.8.3-D = DONE / PUSHED / CLOSED",
    "Dashboard route status: NOT MODIFIED IN THIS PHASE",
    "Dashboard template status: NOT MODIFIED IN THIS PHASE",
    "Dashboard CSS status: NOT MODIFIED IN THIS PHASE",
    "Worker status: OFF / NOT STARTED",
    "OpenClaw status: NOT CONNECTED / NOT CALLED",
    "Hermes status: NOT CONNECTED / NOT CALLED",
    "Google Sheets status: DISABLED / NOT READ / NOT WRITTEN",
]

REQUIRED_LIMITATION_MARKERS = [
    "36/52",
    "git diff --unified=0",
    "added-lines",
    "not a Dashboard content",
    "not a safety-boundary",
    "100% PASS",
    "avoid depending on uncommitted",
]

REQUIRED_STABLE_DASHBOARD_MARKERS = [
    "GET-only `/dashboard/system`",
    "no new route",
    "no POST",
    "no form",
    "no button",
    "no action URL",
    "no webhook/endpoint/execute/dispatch/send control",
    "worker_dry_run_preview",
    "build_worker_dry_run_preview_model",
    "does not directly read the fixture JSON",
    "v0.8.2 Dashboard preview call path",
]

REQUIRED_TEMPLATE_MARKERS = [
    "worker-dry-run-preview",
    "Synthetic local-only",
    "Preview only",
    "Owner Review required",
    "execution_permission",
    "dispatch_permission",
    "external_side_effects_permission",
    "worker_started",
    "worker_loop_started",
    "openclaw_called",
    "hermes_called",
    "google_sheets_enabled",
    "real_queue_db_read",
    "queue_written",
    "post_enabled",
    "secrets_read",
    "webhook_created",
    "endpoint_created",
    "connector_created",
    "production_db_created",
    "remote_blackboard_api_runtime_created",
]

REQUIRED_B_BUILDER_MARKERS = [
    "source == synthetic_local_only",
    "dry_run_status == preview_only_not_executed",
    "owner_review_required == true",
    "execution_permission == false",
    "dispatch_permission == false",
    "external_side_effects_permission == false",
]

REQUIRED_NON_GOAL_MARKERS = [
    "no Dashboard route change",
    "no template change in this phase",
    "no CSS change in this phase",
    "no v0.8.3-D validator fix in this phase",
    "no Worker runtime",
    "no Worker loop",
    "no queue read/write",
    "no execution",
    "no dispatch",
    "no OpenClaw",
    "no Hermes",
    "no Google Sheets",
    "no secrets",
    "no v0.8.3-F work",
]

PERMISSION_KEYS = (
    "execution_permission",
    "dispatch_permission",
    "external_side_effects_permission",
)

RUNTIME_STATE_KEYS = (
    "worker_started",
    "worker_loop_started",
    "openclaw_called",
    "hermes_called",
    "google_sheets_enabled",
    "real_queue_db_read",
    "queue_written",
    "post_enabled",
    "secrets_read",
    "webhook_created",
    "endpoint_created",
    "connector_created",
    "production_db_created",
    "remote_blackboard_api_runtime_created",
)

UNSAFE_DONE_CLAIMS = [
    "Worker started",
    "Worker loop started",
    "OpenClaw connected",
    "OpenClaw called",
    "Hermes connected",
    "Hermes called",
    "Google Sheets enabled",
    "real queue DB read",
    "queue write enabled",
    "POST enabled",
    "secrets read",
    "webhook created",
    "endpoint created",
    "connector created",
    "production DB created",
    "Remote Blackboard API runtime created",
    "v0.8.3-F started",
    "tag created",
]

# Deliberately specific (real call syntax, not bare module/attribute names) so this self-check never
# collides with any legitimate literal substring this script might otherwise need elsewhere. Built via
# concatenation (not literal contiguous substrings) so this tuple's own definition does not trip its
# own self-scan below - only an *actual* dangerous call elsewhere in the file would match.
SELF_FORBIDDEN_CALL_SUBSTRINGS = (
    "os.environ" + "[",
    "os.environ.get" + "(",
    "requests.get" + "(",
    "requests.post" + "(",
    "httpx.get" + "(",
    "httpx.post" + "(",
    "socket.socket" + "(",
    "urllib.request" + ".",
)

SELF_FORBIDDEN_IMPORT_PATTERN = re.compile(
    r"^\s*(import|from)\s+"
    r"(app(\.\w+)?|queue_store|QueueStore|worker(?!_dry_run_preview_boundary)\b"
    r"|openclaw|hermes|google|sheets|requests|httpx|socket|urllib)\b",
    re.IGNORECASE,
)

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


def find_forbidden_calls(source_text: str) -> list[str]:
    return [needle for needle in SELF_FORBIDDEN_CALL_SUBSTRINGS if needle in source_text]


def find_forbidden_imports(source_text: str) -> list[str]:
    found = []
    for line in source_text.splitlines():
        if SELF_FORBIDDEN_IMPORT_PATTERN.match(line):
            found.append(line.strip())
    return found


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


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
# [B-C] v0.8.3-E files exist at expected paths
# ---------------------------------------------------------------------------
print("[B] E plan doc exists at expected path")
check("B. E plan doc exists at expected path", E_DOC_PATH.exists())

print("[C] E readiness script exists at expected path")
check("C. E readiness script exists at expected path", E_SCRIPT_PATH.exists())

# ---------------------------------------------------------------------------
# [D-E] v0.8.3-E files are currently untracked (Owner Review phase)
# ---------------------------------------------------------------------------
print("[D] E plan doc is currently untracked in Owner Review phase")
check("D. E plan doc is currently untracked in Owner Review phase", not git_tracked(E_DOC_REL))

print("[E] E readiness script is currently untracked in Owner Review phase")
check("E. E readiness script is currently untracked in Owner Review phase", not git_tracked(E_SCRIPT_REL))

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
# [G] untracked files allowed only: E doc, E script, patches/*
# ---------------------------------------------------------------------------
print("[G] untracked files allowed only: E doc, E script, patches/*")
untracked = untracked_names()
unexpected_untracked = {u for u in untracked if u not in ALLOWED_NEW_UNTRACKED and not u.startswith("patches/")}
check(
    f"G. no unexpected untracked files（found {sorted(unexpected_untracked)}）"
    if unexpected_untracked
    else "G. no unexpected untracked files",
    not unexpected_untracked,
)

# ---------------------------------------------------------------------------
# [H-X] no protected artifact modified
# ---------------------------------------------------------------------------
print("[H] app/main.py is not modified")
check("H. app/main.py is not modified", MAIN_PY_REL not in tracked_changed)

print("[I] templates/system.html is not modified")
check("I. templates/system.html is not modified", SYSTEM_HTML_REL not in tracked_changed)

print("[J] static/dashboard.css is not modified")
check("J. static/dashboard.css is not modified", DASHBOARD_CSS_REL not in tracked_changed)

print("[K] D validation script is not modified")
check("K. D validation script is not modified", D_SCRIPT_REL not in tracked_changed)

print("[L] C plan doc/readiness are not modified")
check("L. C plan doc/readiness are not modified", C_DOC_REL not in tracked_changed and C_SCRIPT_REL not in tracked_changed)

print("[M] B implementation doc / fixture / builder / readiness are not modified")
check(
    "M. B implementation doc / fixture / builder / readiness are not modified",
    B_DOC_REL not in tracked_changed
    and B_FIXTURE_REL not in tracked_changed
    and B_BUILDER_REL not in tracked_changed
    and B_SCRIPT_REL not in tracked_changed,
)

print("[N] A plan doc/readiness are not modified")
check("N. A plan doc/readiness are not modified", A_DOC_REL not in tracked_changed and A_SCRIPT_REL not in tracked_changed)

print("[O] F closeout doc/readiness are not modified")
check("O. F closeout doc/readiness are not modified", F_DOC_REL not in tracked_changed and F_SCRIPT_REL not in tracked_changed)

print("[P] E v0.8.2 validation script is not modified")
check("P. E v0.8.2 validation script is not modified", E082_SCRIPT_REL not in tracked_changed)

print("[Q] D v0.8.2 plan/readiness are not modified")
check("Q. D v0.8.2 plan/readiness are not modified", D082_DOC_REL not in tracked_changed and D082_SCRIPT_REL not in tracked_changed)

print("[R] C v0.8.2 validation script is not modified")
check("R. C v0.8.2 validation script is not modified", C082_SCRIPT_REL not in tracked_changed)

print("[S] B v0.8.2 doc/readiness are not modified")
check("S. B v0.8.2 doc/readiness are not modified", B082_DOC_REL not in tracked_changed and B082_SCRIPT_REL not in tracked_changed)

print("[T] v0.8.2-A validation script is not modified")
check("T. v0.8.2-A validation script is not modified", A082_SCRIPT_REL not in tracked_changed)

print("[U] P loader is not modified")
check("U. P loader is not modified", P_LOADER_REL not in tracked_changed)

print("[V] V adapter is not modified")
check("V. V adapter is not modified", V_ADAPTER_REL not in tracked_changed)

print("[W] old v0.8.1 fixture JSON is not modified")
check("W. old v0.8.1 fixture JSON is not modified", OLD_FIXTURE_JSON_REL not in tracked_changed)

print("[X] W/X/Y/Z artifacts are not modified")
check("X. W/X/Y/Z artifacts are not modified", not (tracked_changed & PROTECTED_WXYZ))

# ---------------------------------------------------------------------------
# [Y-AI] E doc status/type content checks
# ---------------------------------------------------------------------------
e_doc_text = read_text(E_DOC_PATH)

print('[Y] E doc contains "plan-only / closeout and validation hardening plan"')
check('Y. E doc contains "plan-only / closeout and validation hardening plan"', REQUIRED_TEXT_MARKERS[0] in e_doc_text)

print('[Z] E doc contains "Base commit: 58194a1b17392e050dd8c27f6cee8f8b761d3f4e"')
check('Z. E doc contains "Base commit: 58194a1b17392e050dd8c27f6cee8f8b761d3f4e"', REQUIRED_TEXT_MARKERS[1] in e_doc_text)

print('[AA] E doc contains "v0.8.3-D = DONE / PUSHED / CLOSED"')
check('AA. E doc contains "v0.8.3-D = DONE / PUSHED / CLOSED"', REQUIRED_TEXT_MARKERS[2] in e_doc_text)

print('[AB] E doc contains "Dashboard route status: NOT MODIFIED IN THIS PHASE"')
check('AB. E doc contains "Dashboard route status: NOT MODIFIED IN THIS PHASE"', REQUIRED_TEXT_MARKERS[3] in e_doc_text)

print('[AC] E doc contains "Dashboard template status: NOT MODIFIED IN THIS PHASE"')
check('AC. E doc contains "Dashboard template status: NOT MODIFIED IN THIS PHASE"', REQUIRED_TEXT_MARKERS[4] in e_doc_text)

print('[AD] E doc contains "Dashboard CSS status: NOT MODIFIED IN THIS PHASE"')
check('AD. E doc contains "Dashboard CSS status: NOT MODIFIED IN THIS PHASE"', REQUIRED_TEXT_MARKERS[5] in e_doc_text)

print('[AE] E doc contains "Worker status: OFF / NOT STARTED"')
check('AE. E doc contains "Worker status: OFF / NOT STARTED"', REQUIRED_TEXT_MARKERS[6] in e_doc_text)

print('[AF] E doc contains "OpenClaw status: NOT CONNECTED / NOT CALLED"')
check('AF. E doc contains "OpenClaw status: NOT CONNECTED / NOT CALLED"', REQUIRED_TEXT_MARKERS[7] in e_doc_text)

print('[AG] E doc contains "Hermes status: NOT CONNECTED / NOT CALLED"')
check('AG. E doc contains "Hermes status: NOT CONNECTED / NOT CALLED"', REQUIRED_TEXT_MARKERS[8] in e_doc_text)

print('[AH] E doc contains "Google Sheets status: DISABLED / NOT READ / NOT WRITTEN"')
check('AH. E doc contains "Google Sheets status: DISABLED / NOT READ / NOT WRITTEN"', REQUIRED_TEXT_MARKERS[9] in e_doc_text)

print("[AI] E doc contains exact future v0.8.3-F authorization phrase exactly once")
check(
    "AI. E doc contains exact future v0.8.3-F authorization phrase exactly once",
    e_doc_text.count(EXACT_V083F_PHRASE) == 1,
)

# ---------------------------------------------------------------------------
# [AJ-AP] E doc explains the v0.8.3-D validation limitation
# ---------------------------------------------------------------------------
missing_limitation = [m for m in REQUIRED_LIMITATION_MARKERS if m not in e_doc_text]
limitation_labels = [
    'AJ. E doc explains v0.8.3-D readiness post-push observation "36/52"',
    'AK. E doc explains "git diff --unified=0"',
    'AL. E doc explains "added-lines"',
    "AM. E doc explains this is not a Dashboard content failure",
    "AN. E doc explains this is not a safety-boundary failure",
    "AO. E doc explains full regression suite was 100% PASS",
    "AP. E doc says future hardening should avoid depending on uncommitted diff",
]
for marker, label in zip(REQUIRED_LIMITATION_MARKERS, limitation_labels):
    print(f"[{label.split('.')[0]}] {label}")
    check(label, marker in e_doc_text)

# ---------------------------------------------------------------------------
# [AQ] E doc contains stable future validation checks for Dashboard
# ---------------------------------------------------------------------------
missing_dashboard_markers = [m for m in REQUIRED_STABLE_DASHBOARD_MARKERS if m not in e_doc_text]
print("[AQ] E doc contains stable future validation checks for Dashboard")
check(
    f"AQ. E doc contains stable future validation checks for Dashboard（missing {missing_dashboard_markers}）"
    if missing_dashboard_markers
    else "AQ. E doc contains stable future validation checks for Dashboard",
    not missing_dashboard_markers,
)

# ---------------------------------------------------------------------------
# [AR] E doc contains required template checks
# ---------------------------------------------------------------------------
missing_template_markers = [m for m in REQUIRED_TEMPLATE_MARKERS if m not in e_doc_text]
print("[AR] E doc contains required template checks")
check(
    f"AR. E doc contains required template checks（missing {missing_template_markers}）"
    if missing_template_markers
    else "AR. E doc contains required template checks",
    not missing_template_markers,
)

# ---------------------------------------------------------------------------
# [AS] E doc contains required B builder checks
# ---------------------------------------------------------------------------
missing_builder_markers = [m for m in REQUIRED_B_BUILDER_MARKERS if m not in e_doc_text]
print("[AS] E doc contains required B builder checks")
check(
    f"AS. E doc contains required B builder checks（missing {missing_builder_markers}）"
    if missing_builder_markers
    else "AS. E doc contains required B builder checks",
    not missing_builder_markers,
)

# ---------------------------------------------------------------------------
# [AT] E doc contains non-goals
# ---------------------------------------------------------------------------
missing_non_goals = [m for m in REQUIRED_NON_GOAL_MARKERS if m not in e_doc_text]
print("[AT] E doc contains non-goals")
check(
    f"AT. E doc contains non-goals（missing {missing_non_goals}）"
    if missing_non_goals
    else "AT. E doc contains non-goals",
    not missing_non_goals,
)

# ---------------------------------------------------------------------------
# [AU-AX] B builder local preview re-check (read-only reference)
# ---------------------------------------------------------------------------
built_model: dict[str, object] = {}
builder_import_error: str | None = None
if B_BUILDER_PATH.exists():
    try:
        spec = importlib.util.spec_from_file_location(
            "worker_dry_run_preview_boundary_v0_8_3_b", B_BUILDER_PATH
        )
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        built_model = module.build_worker_dry_run_preview_model()
    except Exception as exc:  # noqa: BLE001 - readiness check wants to report, not raise
        builder_import_error = f"{type(exc).__name__}: {exc}"
else:
    builder_import_error = "B builder not found"

print("[AU] B builder local preview still returns source == synthetic_local_only")
check(
    f"AU. B builder local preview still returns source == synthetic_local_only（error: {builder_import_error}）"
    if builder_import_error
    else "AU. B builder local preview still returns source == synthetic_local_only",
    builder_import_error is None and built_model.get("source") == "synthetic_local_only",
)

print("[AV] B builder local preview still returns dry_run_status == preview_only_not_executed")
check(
    "AV. B builder local preview still returns dry_run_status == preview_only_not_executed",
    builder_import_error is None
    and built_model.get("dry_run_status") == "preview_only_not_executed",
)

print("[AW] B builder local preview permissions are all false")
built_permissions = built_model.get("permissions", {}) if isinstance(built_model, dict) else {}
check(
    "AW. B builder local preview permissions are all false",
    isinstance(built_permissions, dict)
    and all(built_permissions.get(key) is False for key in PERMISSION_KEYS),
)

print("[AX] B builder local preview runtime_state flags are all false")
built_runtime_state = built_model.get("runtime_state", {}) if isinstance(built_model, dict) else {}
check(
    "AX. B builder local preview runtime_state flags are all false",
    isinstance(built_runtime_state, dict)
    and all(built_runtime_state.get(key) is False for key in RUNTIME_STATE_KEYS),
)

# ---------------------------------------------------------------------------
# [AY-BA] committed Dashboard files still contain the v0.8.3-D display (read-only text scan)
# ---------------------------------------------------------------------------
main_py_text = read_text(MAIN_PY_PATH)
system_html_text = read_text(SYSTEM_HTML_PATH)

print("[AY] D dashboard files currently contain worker-dry-run-preview and worker_dry_run_preview")
check(
    "AY. D dashboard files currently contain worker-dry-run-preview and worker_dry_run_preview",
    "worker-dry-run-preview" in system_html_text and "worker_dry_run_preview" in main_py_text,
)

print("[AZ] D dashboard files currently contain no obvious button/form/action URL inside worker-dry-run-preview section")
system_html_lower = system_html_text.lower()
forbidden_control_found = [
    p
    for p in ("<button", "<form", 'action="', "action='", 'method="post"', "onclick=", "action_url", "post_url", "webhook_url", "endpoint_url", "execute_url", "dispatch_url", "send_url")
    if p in system_html_lower
]
check(
    f"AZ. D dashboard files currently contain no obvious button/form/action URL（found {forbidden_control_found}）"
    if forbidden_control_found
    else "AZ. D dashboard files currently contain no obvious button/form/action URL",
    not forbidden_control_found,
)

print('[BA] D route reference still indicates existing GET-only "/dashboard/system"')
check(
    'BA. D route reference still indicates existing GET-only "/dashboard/system"',
    '@app.get("/dashboard/system"' in main_py_text,
)

# ---------------------------------------------------------------------------
# [BB] E doc / script contain no unsafe done-claims
# ---------------------------------------------------------------------------
self_text = read_text(E_SCRIPT_PATH)
combined_text = e_doc_text
found_unsafe = [c for c in UNSAFE_DONE_CLAIMS if c in combined_text]

print("[BB] E doc / script contain no unsafe done-claims")
check(
    f"BB. E doc / script contain no unsafe done-claims（found {found_unsafe}）"
    if found_unsafe
    else "BB. E doc / script contain no unsafe done-claims",
    not found_unsafe,
)

# ---------------------------------------------------------------------------
# [BC] E readiness script itself contains no forbidden imports / runtime calls
# ---------------------------------------------------------------------------
self_forbidden_imports = find_forbidden_imports(self_text)
self_forbidden_calls = find_forbidden_calls(self_text)

print("[BC] E readiness script itself contains no forbidden imports / runtime calls")
check(
    f"BC. E readiness script itself contains no forbidden imports / runtime calls"
    f"（imports {self_forbidden_imports}, calls {self_forbidden_calls}）"
    if (self_forbidden_imports or self_forbidden_calls)
    else "BC. E readiness script itself contains no forbidden imports / runtime calls",
    not self_forbidden_imports and not self_forbidden_calls,
)

# ---------------------------------------------------------------------------
# [BD] patches/ remains untracked and untouched
# ---------------------------------------------------------------------------
print("[BD] patches/ remains untracked and untouched")
check(
    "BD. patches/ remains untracked and untouched",
    not any(p.startswith("patches/") for p in tracked_changed),
)

# ---------------------------------------------------------------------------
# 結果
# ---------------------------------------------------------------------------
total = len(PASS) + len(FAIL)
print(f"\n合計：{len(PASS)}/{total} 通過")
if FAIL:
    print(f"\nXX v0.8.3-E readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print("PASS: v0.8.3-E worker dry-run preview dashboard display closeout validation hardening plan")
    sys.exit(0)
