"""v0.8.3-D readiness check: Worker Dry-run Preview Dashboard Read-only Display Implementation.

Pure local filesystem + git metadata validation. This script confirms the tracked/untracked state of
this round's files, inspects ONLY the *added* lines of `app/main.py`, `templates/system.html`, and
`static/dashboard.css` (via `git diff --unified=0`) for the required v0.8.3-B wiring and the absence
of any forbidden route/control/integration pattern, and re-runs the v0.8.3-B standalone builder
(read-only reference check) to confirm its returned model stays safe. It never diffs or scans
unrelated pre-existing lines in those files, so pre-existing QueueStore usage or other routes
elsewhere in app/main.py cannot trip this check.

This round is Owner-Review-phase only (nothing is committed yet), so all "added lines" come from the
plain working-tree diff (`git diff --unified=0 -- <file>` against the index/HEAD).

It does NOT import app runtime, Dashboard runtime, QueueStore, Worker/OpenClaw/Hermes/Google Sheets
integration, the v0.8.1-P loader, or the v0.8.1-V adapter; it never starts a server; it reads no real
queue DB, sends no POST, makes no network call, reads no secrets, writes no repo file, and modifies no
git index. It only imports the v0.8.3-B builder module (standard library only) to call its public
function and inspect the returned dict, as a read-only reference re-check.
"""
from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

MAIN_PY_REL = "app/main.py"
SYSTEM_HTML_REL = "templates/system.html"
DASHBOARD_CSS_REL = "static/dashboard.css"
D_SCRIPT_REL = "scripts/check_hermes_openclaw_worker_dry_run_preview_dashboard_read_only_display_implementation_v0_8_3_d.py"
D_SCRIPT_PATH = REPO_ROOT / D_SCRIPT_REL

B_DOC_REL = "docs/HERMES_OPENCLAW_WORKER_DRY_RUN_PREVIEW_BOUNDARY_IMPLEMENTATION_V0_8_3_B.md"
B_FIXTURE_REL = "fixtures/local_mock_data/hermes_openclaw_worker_dry_run_preview_v0_8_3_b.json"
B_BUILDER_REL = "scripts/worker_dry_run_preview_boundary_v0_8_3_b.py"
B_BUILDER_PATH = REPO_ROOT / B_BUILDER_REL
B_SCRIPT_REL = "scripts/check_hermes_openclaw_worker_dry_run_preview_boundary_implementation_v0_8_3_b.py"

C_DOC_REL = "docs/HERMES_OPENCLAW_WORKER_DRY_RUN_PREVIEW_DASHBOARD_READ_ONLY_DISPLAY_PLAN_V0_8_3_C.md"
C_SCRIPT_REL = "scripts/check_hermes_openclaw_worker_dry_run_preview_dashboard_read_only_display_plan_v0_8_3_c.py"

A_DOC_REL = "docs/HERMES_OPENCLAW_WORKER_DRY_RUN_PREVIEW_BOUNDARY_PLAN_V0_8_3_A.md"
A_SCRIPT_REL = "scripts/check_hermes_openclaw_worker_dry_run_preview_boundary_plan_v0_8_3_a.py"

F_DOC_REL = "docs/HERMES_OPENCLAW_DASHBOARD_READ_ONLY_PREVIEW_VALIDATION_CLOSEOUT_HANDOFF_PLAN_V0_8_2_F.md"
F_SCRIPT_REL = "scripts/check_hermes_openclaw_dashboard_read_only_preview_validation_closeout_handoff_plan_v0_8_2_f.py"

E_SCRIPT_REL = "scripts/check_hermes_openclaw_dashboard_read_only_preview_ui_validation_hardening_v0_8_2_e.py"

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

EXPECTED_BASE_HEAD = "e6bed86aead116800c21830a14d7c946bf3f8b3d"

REQUIRED_D_MODIFIED = {MAIN_PY_REL, SYSTEM_HTML_REL, DASHBOARD_CSS_REL}
ALLOWED_NEW_UNTRACKED = {D_SCRIPT_REL}

REQUIRED_DISPLAY_LABELS = (
    "Dry-run ID",
    "Source",
    "Task title",
    "Task summary",
    "Source role",
    "Target role",
    "Proposed worker action",
    "Dry-run status",
    "Review notice",
    "Boundary summary",
)

REQUIRED_PERMISSION_KEYS = (
    "execution_permission",
    "dispatch_permission",
    "external_side_effects_permission",
)

REQUIRED_RUNTIME_KEYS = (
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

SYSTEM_FORBIDDEN_CONTROL_PATTERNS = (
    "<form",
    "<button",
    'method="post"',
    "method='post'",
    'action="',
    "action='",
    "onclick=",
    "action_url",
    "post_url",
    "webhook_url",
    "endpoint_url",
    "execute_url",
    "dispatch_url",
    "send_url",
)

MAIN_FORBIDDEN_ROUTE_PATTERNS = ("@app.post(", "@app.put(", "@app.delete(", "@app.patch(")

MAIN_FORBIDDEN_QUEUE_PATTERNS = ("QueueStore(", "QUEUE_DB_PATH", "get_blackboard(", ".execute(")

MAIN_FORBIDDEN_INTEGRATION_PATTERNS = (
    "run_openclaw_cli(",
    "subprocess.",
    "GOOGLE_SHEETS_ENABLED",
    "google_sheets",
    "hermes_endpoint",
    "openclaw_endpoint",
)

MAIN_FORBIDDEN_SECRET_PATTERNS = ("os.getenv(", "os.environ", ".env", "webhook", "connector")

CSS_FORBIDDEN_PATTERNS = ("cursor: pointer", "cursor:pointer", "pointer-events", "execute", "dispatch", "onclick")

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
    "v0.8.3-E started",
    "tag created",
]

# Deliberately specific (real call syntax, not bare module/attribute names) so this self-check never
# collides with the *other* forbidden-pattern tuples above (e.g. MAIN_FORBIDDEN_SECRET_PATTERNS'
# bare "os.environ" or MAIN_FORBIDDEN_ROUTE_PATTERNS' "@app.post(") which legitimately need those
# bare substrings to scan app/main.py's added lines and would otherwise make this script self-trip.
# Built via concatenation (not literal contiguous substrings) so this tuple's own definition does not
# trip its own self-scan below - only an *actual* dangerous call elsewhere in the file would match.
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


def working_tree_change_names() -> set[str]:
    return set(git_lines(["diff", "--name-only"]))


def untracked_names() -> set[str]:
    return set(git_lines(["ls-files", "--others", "--exclude-standard"]))


def diff_added_lines(rel: str) -> str:
    out = run_git(["diff", "--unified=0", "--", rel])
    added: list[str] = []
    for line in out.stdout.splitlines():
        if line.startswith("+++"):
            continue
        if line.startswith("+"):
            added.append(line[1:])
    return "\n".join(added)


def find_forbidden_calls(source_text: str) -> list[str]:
    return [needle for needle in SELF_FORBIDDEN_CALL_SUBSTRINGS if needle in source_text]


def find_forbidden_imports(source_text: str) -> list[str]:
    found = []
    for line in source_text.splitlines():
        if SELF_FORBIDDEN_IMPORT_PATTERN.match(line):
            found.append(line.strip())
    return found


# ---------------------------------------------------------------------------
# [A] current HEAD contains EXPECTED_BASE_HEAD in git history
# ---------------------------------------------------------------------------
print("[A] current HEAD contains EXPECTED_BASE_HEAD in git history")
ancestor_check = run_git(["merge-base", "--is-ancestor", EXPECTED_BASE_HEAD, "HEAD"])
check(
    f"A. HEAD contains {EXPECTED_BASE_HEAD} in git history",
    ancestor_check.returncode == 0,
)

tracked_changed = working_tree_change_names()
untracked = untracked_names()

# ---------------------------------------------------------------------------
# [B-D] app/main.py, templates/system.html, static/dashboard.css exist and are modified
# ---------------------------------------------------------------------------
print("[B] app/main.py exists and is modified in working tree for D")
check(
    "B. app/main.py exists and is modified in working tree for D",
    (REPO_ROOT / MAIN_PY_REL).exists() and MAIN_PY_REL in tracked_changed,
)

print("[C] templates/system.html exists and is modified in working tree for D")
check(
    "C. templates/system.html exists and is modified in working tree for D",
    (REPO_ROOT / SYSTEM_HTML_REL).exists() and SYSTEM_HTML_REL in tracked_changed,
)

print("[D] static/dashboard.css exists and is modified in working tree for D")
check(
    "D. static/dashboard.css exists and is modified in working tree for D",
    (REPO_ROOT / DASHBOARD_CSS_REL).exists() and DASHBOARD_CSS_REL in tracked_changed,
)

# ---------------------------------------------------------------------------
# [E] D validation script exists and is currently untracked in Owner Review phase
# ---------------------------------------------------------------------------
print("[E] D validation script exists and is currently untracked in Owner Review phase")
check(
    "E. D validation script exists and is currently untracked in Owner Review phase",
    D_SCRIPT_PATH.exists() and D_SCRIPT_REL in untracked,
)

# ---------------------------------------------------------------------------
# [F] only allowed tracked modified files are app/main.py, templates/system.html, static/dashboard.css
# ---------------------------------------------------------------------------
print("[F] only allowed tracked modified files are app/main.py, templates/system.html, static/dashboard.css")
unexpected_tracked = tracked_changed - REQUIRED_D_MODIFIED
check(
    f"F. only allowed tracked modified files are changed（unexpected={sorted(unexpected_tracked)}）"
    if unexpected_tracked
    else "F. only allowed tracked modified files are changed",
    not unexpected_tracked,
)

# ---------------------------------------------------------------------------
# [G] allowed untracked files only: D validation script, patches/*
# ---------------------------------------------------------------------------
print("[G] allowed untracked files only: D validation script, patches/*")
unexpected_untracked = {u for u in untracked if u not in ALLOWED_NEW_UNTRACKED and not u.startswith("patches/")}
check(
    f"G. no unexpected untracked files（found {sorted(unexpected_untracked)}）"
    if unexpected_untracked
    else "G. no unexpected untracked files",
    not unexpected_untracked,
)

# ---------------------------------------------------------------------------
# [H] no other tracked files modified (all three required files were actually modified)
# ---------------------------------------------------------------------------
print("[H] no other tracked files modified (all three D files present in diff)")
missing_tracked = REQUIRED_D_MODIFIED - tracked_changed
check(
    f"H. all three D-authorized files show a working-tree diff（missing={sorted(missing_tracked)}）"
    if missing_tracked
    else "H. all three D-authorized files show a working-tree diff",
    not missing_tracked,
)

# ---------------------------------------------------------------------------
# [I-U] no protected artifact modified
# ---------------------------------------------------------------------------
print("[I] C plan doc/readiness are not modified")
check("I. C plan doc/readiness are not modified", C_DOC_REL not in tracked_changed and C_SCRIPT_REL not in tracked_changed)

print("[J] B implementation doc / fixture / builder / readiness script are not modified")
check(
    "J. B implementation doc / fixture / builder / readiness script are not modified",
    B_DOC_REL not in tracked_changed
    and B_FIXTURE_REL not in tracked_changed
    and B_BUILDER_REL not in tracked_changed
    and B_SCRIPT_REL not in tracked_changed,
)

print("[K] A plan doc/readiness are not modified")
check("K. A plan doc/readiness are not modified", A_DOC_REL not in tracked_changed and A_SCRIPT_REL not in tracked_changed)

print("[L] F closeout doc/readiness are not modified")
check("L. F closeout doc/readiness are not modified", F_DOC_REL not in tracked_changed and F_SCRIPT_REL not in tracked_changed)

print("[M] E validation script is not modified")
check("M. E validation script is not modified", E_SCRIPT_REL not in tracked_changed)

print("[N] D v0.8.2 plan/readiness are not modified")
check("N. D v0.8.2 plan/readiness are not modified", D082_DOC_REL not in tracked_changed and D082_SCRIPT_REL not in tracked_changed)

print("[O] C v0.8.2 validation script is not modified")
check("O. C v0.8.2 validation script is not modified", C082_SCRIPT_REL not in tracked_changed)

print("[P] B v0.8.2 doc/readiness are not modified")
check("P. B v0.8.2 doc/readiness are not modified", B082_DOC_REL not in tracked_changed and B082_SCRIPT_REL not in tracked_changed)

print("[Q] v0.8.2-A validation script is not modified")
check("Q. v0.8.2-A validation script is not modified", A082_SCRIPT_REL not in tracked_changed)

print("[R] P loader is not modified")
check("R. P loader is not modified", P_LOADER_REL not in tracked_changed)

print("[S] V adapter is not modified")
check("S. V adapter is not modified", V_ADAPTER_REL not in tracked_changed)

print("[T] old v0.8.1 fixture JSON is not modified")
check("T. old v0.8.1 fixture JSON is not modified", OLD_FIXTURE_JSON_REL not in tracked_changed)

print("[U] W/X/Y/Z artifacts are not modified")
check("U. W/X/Y/Z artifacts are not modified", not (tracked_changed & PROTECTED_WXYZ))

# ---------------------------------------------------------------------------
# app/main.py added-lines checks [V-AB]
# ---------------------------------------------------------------------------
main_added = diff_added_lines(MAIN_PY_REL)

print("[V] app/main.py added lines reference build_worker_dry_run_preview_model")
check(
    "V. app/main.py added lines reference build_worker_dry_run_preview_model",
    "build_worker_dry_run_preview_model" in main_added
    and "worker_dry_run_preview_boundary_v0_8_3_b" in main_added,
)

print("[W] app/main.py passes worker_dry_run_preview into the system.html template context")
check(
    "W. app/main.py passes worker_dry_run_preview into the system.html template context",
    '"worker_dry_run_preview"' in main_added,
)

print("[X] app/main.py does not directly read hermes_openclaw_worker_dry_run_preview_v0_8_3_b.json")
check(
    "X. app/main.py does not directly read hermes_openclaw_worker_dry_run_preview_v0_8_3_b.json",
    "hermes_openclaw_worker_dry_run_preview_v0_8_3_b.json" not in main_added,
)

print("[Y] app/main.py does not import QueueStore / Worker / OpenClaw / Hermes / Google Sheets")
main_forbidden_integration = [
    p for p in (*MAIN_FORBIDDEN_QUEUE_PATTERNS, *MAIN_FORBIDDEN_INTEGRATION_PATTERNS) if p in main_added
]
check(
    f"Y. app/main.py does not import QueueStore / Worker / OpenClaw / Hermes / Google Sheets（found {main_forbidden_integration}）"
    if main_forbidden_integration
    else "Y. app/main.py does not import QueueStore / Worker / OpenClaw / Hermes / Google Sheets",
    not main_forbidden_integration,
)

print("[Z] app/main.py does not add POST route / method / endpoint / webhook / connector / dispatch / execute / send control")
main_forbidden_route = [
    p for p in (*MAIN_FORBIDDEN_ROUTE_PATTERNS, *MAIN_FORBIDDEN_SECRET_PATTERNS) if p in main_added
]
check(
    f"Z. app/main.py does not add POST route / method / endpoint / webhook / connector / dispatch / execute / send control（found {main_forbidden_route}）"
    if main_forbidden_route
    else "Z. app/main.py does not add POST route / method / endpoint / webhook / connector / dispatch / execute / send control",
    not main_forbidden_route,
)

print("[AA] app/main.py does not call load_local_mock_fixture_preview() in the new worker dry-run display path")
check(
    "AA. app/main.py does not call load_local_mock_fixture_preview() in the new worker dry-run display path",
    "load_local_mock_fixture_preview" not in main_added,
)

print("[AB] app/main.py does not call validate_local_mock_fixture_preview_object() in the new worker dry-run display path")
check(
    "AB. app/main.py does not call validate_local_mock_fixture_preview_object() in the new worker dry-run display path",
    "validate_local_mock_fixture_preview_object" not in main_added,
)

# ---------------------------------------------------------------------------
# templates/system.html added-lines checks [AC-AP]
# ---------------------------------------------------------------------------
system_added = diff_added_lines(SYSTEM_HTML_REL)
system_added_lower = system_added.lower()

print("[AC] templates/system.html contains section id or class worker-dry-run-preview")
check(
    "AC. templates/system.html contains section id or class worker-dry-run-preview",
    "worker-dry-run-preview" in system_added,
)

print("[AD] templates/system.html renders worker_dry_run_preview")
check(
    "AD. templates/system.html renders worker_dry_run_preview",
    "worker_dry_run_preview" in system_added,
)

print('[AE] templates/system.html contains "Synthetic local-only"')
check('AE. templates/system.html contains "Synthetic local-only"', "Synthetic local-only" in system_added)

print('[AF] templates/system.html contains "Preview only"')
check('AF. templates/system.html contains "Preview only"', "Preview only" in system_added)

print('[AG] templates/system.html contains "Owner Review required"')
check('AG. templates/system.html contains "Owner Review required"', "Owner Review required" in system_added)

print("[AH] templates/system.html contains all required display field labels")
missing_labels = [label for label in REQUIRED_DISPLAY_LABELS if label not in system_added]
check(
    f"AH. templates/system.html contains all required display field labels（missing {missing_labels}）"
    if missing_labels
    else "AH. templates/system.html contains all required display field labels",
    not missing_labels,
)

print("[AI] templates/system.html contains all required permission flag keys")
missing_permission_keys = [k for k in REQUIRED_PERMISSION_KEYS if k not in system_added]
check(
    f"AI. templates/system.html contains all required permission flag keys（missing {missing_permission_keys}）"
    if missing_permission_keys
    else "AI. templates/system.html contains all required permission flag keys",
    not missing_permission_keys,
)

print("[AJ] templates/system.html contains all required runtime flag keys")
missing_runtime_keys = [k for k in REQUIRED_RUNTIME_KEYS if k not in system_added]
check(
    f"AJ. templates/system.html contains all required runtime flag keys（missing {missing_runtime_keys}）"
    if missing_runtime_keys
    else "AJ. templates/system.html contains all required runtime flag keys",
    not missing_runtime_keys,
)

print("[AK] worker-dry-run-preview section contains no button")
check("AK. worker-dry-run-preview section contains no button", "<button" not in system_added_lower)

print("[AL] worker-dry-run-preview section contains no form")
check("AL. worker-dry-run-preview section contains no form", "<form" not in system_added_lower)

print("[AM] worker-dry-run-preview section contains no action=")
check(
    "AM. worker-dry-run-preview section contains no action=",
    'action="' not in system_added_lower and "action='" not in system_added_lower,
)

print("[AN] worker-dry-run-preview section contains no method=")
check(
    "AN. worker-dry-run-preview section contains no method=",
    'method="' not in system_added_lower and "method='" not in system_added_lower,
)

print("[AO] worker-dry-run-preview section contains no onclick")
check("AO. worker-dry-run-preview section contains no onclick", "onclick=" not in system_added_lower)

print("[AP] worker-dry-run-preview section contains no forbidden control URL keys")
found_control_patterns = [p for p in SYSTEM_FORBIDDEN_CONTROL_PATTERNS if p in system_added_lower]
check(
    f"AP. worker-dry-run-preview section contains no forbidden control URL keys（found {found_control_patterns}）"
    if found_control_patterns
    else "AP. worker-dry-run-preview section contains no forbidden control URL keys",
    not found_control_patterns,
)

# ---------------------------------------------------------------------------
# static/dashboard.css added-lines checks [AQ-AS]
# ---------------------------------------------------------------------------
css_added = diff_added_lines(DASHBOARD_CSS_REL)
css_added_lower = css_added.lower()

print("[AQ] static/dashboard.css contains worker-dry-run-preview styling")
check("AQ. static/dashboard.css contains worker-dry-run-preview styling", "worker-dry-run-preview" in css_added)

print("[AR] static/dashboard.css does not contain cursor: pointer within worker-dry-run-preview block")
check(
    "AR. static/dashboard.css does not contain cursor: pointer within worker-dry-run-preview block",
    "cursor: pointer" not in css_added_lower and "cursor:pointer" not in css_added_lower,
)

print("[AS] static/dashboard.css does not contain execute / dispatch / send / action control styling for worker-dry-run-preview")
css_forbidden_found = [p for p in CSS_FORBIDDEN_PATTERNS if p in css_added_lower]
check(
    f"AS. static/dashboard.css does not contain execute / dispatch / send / action control styling（found {css_forbidden_found}）"
    if css_forbidden_found
    else "AS. static/dashboard.css does not contain execute / dispatch / send / action control styling",
    not css_forbidden_found,
)

# ---------------------------------------------------------------------------
# [AT-AW] B builder local preview re-check (read-only reference)
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

print("[AT] B builder local preview still returns source == synthetic_local_only")
check(
    f"AT. B builder local preview still returns source == synthetic_local_only（error: {builder_import_error}）"
    if builder_import_error
    else "AT. B builder local preview still returns source == synthetic_local_only",
    builder_import_error is None and built_model.get("source") == "synthetic_local_only",
)

print("[AU] B builder local preview still returns dry_run_status == preview_only_not_executed")
check(
    "AU. B builder local preview still returns dry_run_status == preview_only_not_executed",
    builder_import_error is None
    and built_model.get("dry_run_status") == "preview_only_not_executed",
)

print("[AV] B builder local preview permissions are all false")
built_permissions = built_model.get("permissions", {}) if isinstance(built_model, dict) else {}
check(
    "AV. B builder local preview permissions are all false",
    isinstance(built_permissions, dict)
    and all(built_permissions.get(key) is False for key in REQUIRED_PERMISSION_KEYS),
)

print("[AW] B builder local preview runtime_state flags are all false")
built_runtime_state = built_model.get("runtime_state", {}) if isinstance(built_model, dict) else {}
check(
    "AW. B builder local preview runtime_state flags are all false",
    isinstance(built_runtime_state, dict)
    and all(built_runtime_state.get(key) is False for key in REQUIRED_RUNTIME_KEYS),
)

# ---------------------------------------------------------------------------
# [AX] combined app/template/css contains no unsafe done-claims
# ---------------------------------------------------------------------------
self_text = D_SCRIPT_PATH.read_text(encoding="utf-8") if D_SCRIPT_PATH.exists() else ""
combined_text = main_added + "\n" + system_added + "\n" + css_added
found_unsafe = [c for c in UNSAFE_DONE_CLAIMS if c in combined_text]

print("[AX] combined app/template/css/script contains no unsafe done-claims")
check(
    f"AX. combined app/template/css/script contains no unsafe done-claims（found {found_unsafe}）"
    if found_unsafe
    else "AX. combined app/template/css/script contains no unsafe done-claims",
    not found_unsafe,
)

# ---------------------------------------------------------------------------
# [AY] D validation script itself contains no forbidden imports / runtime calls
# ---------------------------------------------------------------------------
self_forbidden_imports = find_forbidden_imports(self_text)
self_forbidden_calls = find_forbidden_calls(self_text)

print("[AY] D validation script itself contains no forbidden imports / runtime calls")
check(
    f"AY. D validation script itself contains no forbidden imports / runtime calls"
    f"（imports {self_forbidden_imports}, calls {self_forbidden_calls}）"
    if (self_forbidden_imports or self_forbidden_calls)
    else "AY. D validation script itself contains no forbidden imports / runtime calls",
    not self_forbidden_imports and not self_forbidden_calls,
)

# ---------------------------------------------------------------------------
# [AZ] patches/ remains untracked and untouched
# ---------------------------------------------------------------------------
print("[AZ] patches/ remains untracked and untouched")
check(
    "AZ. patches/ remains untracked and untouched",
    not any(p.startswith("patches/") for p in tracked_changed),
)

# ---------------------------------------------------------------------------
# 結果
# ---------------------------------------------------------------------------
total = len(PASS) + len(FAIL)
print(f"\n合計：{len(PASS)}/{total} 通過")
if FAIL:
    print(f"\nXX v0.8.3-D readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print("PASS: v0.8.3-D worker dry-run preview dashboard read-only display implementation")
    sys.exit(0)
