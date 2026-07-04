"""v0.8.4-G readiness check: Worker Dry-run Result / Audit Trail Dashboard Display
Closeout Report.

Pure local filesystem + git metadata validation, standard library only. It reads the
v0.8.4-G closeout report doc and this script's own source directly from the working tree,
checks that no existing tracked file was modified by this round, and re-runs existing
read-only reference checks (the v0.8.4-F/E/D/C/B/A validators, the v0.8.3-F/G validators,
the v0.8.2/v0.8.1 regression suite as subprocesses, and the v0.8.4-B / v0.8.3-B standalone
builders via direct import) purely to confirm the series still stands.

It does NOT modify any file, does NOT start a server, sends no POST, makes no network call,
reads no secrets, reads no real queue DB, writes no queue, and does not call
Worker/OpenClaw/Hermes/Google Sheets. Its only subprocess use is invoking the current Python
interpreter on existing read-only validator scripts already used elsewhere in this series;
its only git usage is read-only plumbing (rev-parse, status, diff, ls-files, log,
merge-base, tag).
"""
from __future__ import annotations

import re
import subprocess
import sys
import importlib.util
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

MAIN_PY_REL = "app/main.py"
SYSTEM_HTML_REL = "templates/system.html"
DASHBOARD_CSS_REL = "static/dashboard.css"

MAIN_PY_PATH = REPO_ROOT / MAIN_PY_REL
SYSTEM_HTML_PATH = REPO_ROOT / SYSTEM_HTML_REL
DASHBOARD_CSS_PATH = REPO_ROOT / DASHBOARD_CSS_REL

# -----------------------------------------------------------------------------------
# v0.8.4-G (this round)
# -----------------------------------------------------------------------------------
G_DOC_REL = (
    "docs/HERMES_OPENCLAW_WORKER_DRY_RUN_RESULT_AUDIT_TRAIL_DASHBOARD_DISPLAY_"
    "CLOSEOUT_REPORT_V0_8_4_G.md"
)
G_DOC_PATH = REPO_ROOT / G_DOC_REL

G_SCRIPT_REL = (
    "scripts/check_hermes_openclaw_worker_dry_run_result_audit_trail_dashboard_"
    "display_closeout_report_v0_8_4_g.py"
)
G_SCRIPT_PATH = REPO_ROOT / G_SCRIPT_REL

# -----------------------------------------------------------------------------------
# v0.8.4-A..F (this series)
# -----------------------------------------------------------------------------------
A_DOC_REL = "docs/HERMES_OPENCLAW_WORKER_DRY_RUN_RESULT_AUDIT_TRAIL_BOUNDARY_PLAN_V0_8_4_A.md"
A_SCRIPT_REL = "scripts/check_hermes_openclaw_worker_dry_run_result_audit_trail_boundary_plan_v0_8_4_a.py"
A_SCRIPT_PATH = REPO_ROOT / A_SCRIPT_REL

B_DOC_REL = "docs/HERMES_OPENCLAW_WORKER_DRY_RUN_RESULT_AUDIT_TRAIL_BOUNDARY_IMPLEMENTATION_V0_8_4_B.md"
B_FIXTURE_REL = "fixtures/local_mock_data/hermes_openclaw_worker_dry_run_result_audit_trail_v0_8_4_b.json"
B_BUILDER_REL = "scripts/worker_dry_run_result_audit_trail_boundary_v0_8_4_b.py"
B_BUILDER_PATH = REPO_ROOT / B_BUILDER_REL
B_SCRIPT_REL = "scripts/check_hermes_openclaw_worker_dry_run_result_audit_trail_boundary_implementation_v0_8_4_b.py"
B_SCRIPT_PATH = REPO_ROOT / B_SCRIPT_REL

C_DOC_REL = "docs/HERMES_OPENCLAW_WORKER_DRY_RUN_RESULT_AUDIT_TRAIL_DASHBOARD_READ_ONLY_DISPLAY_PLAN_V0_8_4_C.md"
C_SCRIPT_REL = "scripts/check_hermes_openclaw_worker_dry_run_result_audit_trail_dashboard_read_only_display_plan_v0_8_4_c.py"
C_SCRIPT_PATH = REPO_ROOT / C_SCRIPT_REL

D_SCRIPT_REL = "scripts/check_hermes_openclaw_worker_dry_run_result_audit_trail_dashboard_read_only_display_implementation_v0_8_4_d.py"
D_SCRIPT_PATH = REPO_ROOT / D_SCRIPT_REL

E_DOC_REL = (
    "docs/HERMES_OPENCLAW_WORKER_DRY_RUN_RESULT_AUDIT_TRAIL_DASHBOARD_DISPLAY_"
    "CLOSEOUT_VALIDATION_HARDENING_PLAN_V0_8_4_E.md"
)
E_SCRIPT_REL = (
    "scripts/check_hermes_openclaw_worker_dry_run_result_audit_trail_dashboard_"
    "display_closeout_validation_hardening_plan_v0_8_4_e.py"
)
E_SCRIPT_PATH = REPO_ROOT / E_SCRIPT_REL

F_SCRIPT_REL = (
    "scripts/check_hermes_openclaw_worker_dry_run_result_audit_trail_dashboard_"
    "display_validation_hardening_v0_8_4_f.py"
)
F_SCRIPT_PATH = REPO_ROOT / F_SCRIPT_REL

# -----------------------------------------------------------------------------------
# v0.8.3-A..G (prior series)
# -----------------------------------------------------------------------------------
V083_A_DOC_REL = "docs/HERMES_OPENCLAW_WORKER_DRY_RUN_PREVIEW_BOUNDARY_PLAN_V0_8_3_A.md"
V083_A_SCRIPT_REL = "scripts/check_hermes_openclaw_worker_dry_run_preview_boundary_plan_v0_8_3_a.py"

V083_B_DOC_REL = "docs/HERMES_OPENCLAW_WORKER_DRY_RUN_PREVIEW_BOUNDARY_IMPLEMENTATION_V0_8_3_B.md"
V083_B_FIXTURE_REL = "fixtures/local_mock_data/hermes_openclaw_worker_dry_run_preview_v0_8_3_b.json"
V083_B_BUILDER_REL = "scripts/worker_dry_run_preview_boundary_v0_8_3_b.py"
V083_B_BUILDER_PATH = REPO_ROOT / V083_B_BUILDER_REL
V083_B_SCRIPT_REL = "scripts/check_hermes_openclaw_worker_dry_run_preview_boundary_implementation_v0_8_3_b.py"

V083_C_DOC_REL = "docs/HERMES_OPENCLAW_WORKER_DRY_RUN_PREVIEW_DASHBOARD_READ_ONLY_DISPLAY_PLAN_V0_8_3_C.md"
V083_C_SCRIPT_REL = "scripts/check_hermes_openclaw_worker_dry_run_preview_dashboard_read_only_display_plan_v0_8_3_c.py"

V083_D_SCRIPT_REL = "scripts/check_hermes_openclaw_worker_dry_run_preview_dashboard_read_only_display_implementation_v0_8_3_d.py"

V083_E_DOC_REL = "docs/HERMES_OPENCLAW_WORKER_DRY_RUN_PREVIEW_DASHBOARD_DISPLAY_CLOSEOUT_VALIDATION_HARDENING_PLAN_V0_8_3_E.md"
V083_E_SCRIPT_REL = "scripts/check_hermes_openclaw_worker_dry_run_preview_dashboard_display_closeout_validation_hardening_plan_v0_8_3_e.py"

V083_F_SCRIPT_REL = "scripts/check_hermes_openclaw_worker_dry_run_preview_dashboard_display_validation_hardening_v0_8_3_f.py"
V083_F_SCRIPT_PATH = REPO_ROOT / V083_F_SCRIPT_REL

V083_G_DOC_REL = "docs/HERMES_OPENCLAW_WORKER_DRY_RUN_PREVIEW_DASHBOARD_DISPLAY_CLOSEOUT_REPORT_V0_8_3_G.md"
V083_G_SCRIPT_REL = "scripts/check_hermes_openclaw_worker_dry_run_preview_dashboard_display_closeout_report_v0_8_3_g.py"
V083_G_SCRIPT_PATH = REPO_ROOT / V083_G_SCRIPT_REL

# -----------------------------------------------------------------------------------
# v0.8.2-A..F
# -----------------------------------------------------------------------------------
V082_F_DOC_REL = "docs/HERMES_OPENCLAW_DASHBOARD_READ_ONLY_PREVIEW_VALIDATION_CLOSEOUT_HANDOFF_PLAN_V0_8_2_F.md"
V082_F_SCRIPT_REL = "scripts/check_hermes_openclaw_dashboard_read_only_preview_validation_closeout_handoff_plan_v0_8_2_f.py"

V082_E_SCRIPT_REL = "scripts/check_hermes_openclaw_dashboard_read_only_preview_ui_validation_hardening_v0_8_2_e.py"
V082_E_SCRIPT_PATH = REPO_ROOT / V082_E_SCRIPT_REL

V082_D_DOC_REL = "docs/HERMES_OPENCLAW_DASHBOARD_READ_ONLY_PREVIEW_UI_VALIDATION_HARDENING_PLAN_V0_8_2_D.md"
V082_D_SCRIPT_REL = "scripts/check_hermes_openclaw_dashboard_read_only_preview_ui_validation_hardening_plan_v0_8_2_d.py"

V082_C_SCRIPT_REL = "scripts/check_hermes_openclaw_dashboard_read_only_preview_ui_refinement_v0_8_2_c.py"
V082_C_SCRIPT_PATH = REPO_ROOT / V082_C_SCRIPT_REL

V082_B_DOC_REL = "docs/HERMES_OPENCLAW_DASHBOARD_READ_ONLY_PREVIEW_UI_REFINEMENT_PLAN_V0_8_2_B.md"
V082_B_SCRIPT_REL = "scripts/check_hermes_openclaw_dashboard_read_only_preview_ui_refinement_plan_v0_8_2_b.py"
V082_B_SCRIPT_PATH = REPO_ROOT / V082_B_SCRIPT_REL

V082_A_SCRIPT_REL = (
    "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_"
    "read_only_display_integration_v0_8_2_a.py"
)
V082_A_SCRIPT_PATH = REPO_ROOT / V082_A_SCRIPT_REL

# -----------------------------------------------------------------------------------
# v0.8.1 P loader / V adapter / W/X/Y/Z / fixtures
# -----------------------------------------------------------------------------------
P_LOADER_REL = "scripts/load_local_mock_fixture_preview_v0_8_1.py"
V_ADAPTER_REL = "scripts/local_mock_fixture_dashboard_preview_adapter_v0_8_1.py"
OLD_FIXTURE_JSON_REL = "fixtures/local_mock_data/hermes_openclaw_local_mock_messages_v0_8_1.json"

V_SCRIPT_REL = "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_v0_8_1_v.py"
V_SCRIPT_PATH = REPO_ROOT / V_SCRIPT_REL

W_SCRIPT_REL = "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_runtime_check_v0_8_1_w.py"
W_SCRIPT_PATH = REPO_ROOT / W_SCRIPT_REL

X_SCRIPT_REL = (
    "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_"
    "integration_boundary_plan_v0_8_1_x.py"
)
X_SCRIPT_PATH = REPO_ROOT / X_SCRIPT_REL

Y_SCRIPT_REL = (
    "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_"
    "integration_authorization_plan_v0_8_1_y.py"
)
Y_SCRIPT_PATH = REPO_ROOT / Y_SCRIPT_REL

Z_SCRIPT_REL = (
    "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_"
    "integration_implementation_plan_v0_8_1_z.py"
)
Z_SCRIPT_PATH = REPO_ROOT / Z_SCRIPT_REL

WXYZ_REL = {
    W_SCRIPT_REL,
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_DASHBOARD_PREVIEW_ADAPTER_INTEGRATION_BOUNDARY_PLAN_V0_8_1_X.md",
    X_SCRIPT_REL,
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_DASHBOARD_PREVIEW_ADAPTER_INTEGRATION_AUTHORIZATION_PLAN_V0_8_1_Y.md",
    Y_SCRIPT_REL,
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_DASHBOARD_PREVIEW_ADAPTER_INTEGRATION_IMPLEMENTATION_PLAN_V0_8_1_Z.md",
    Z_SCRIPT_REL,
}

# v0.8.4-F commit — HEAD at the start of this round.
EXPECTED_HEAD = "b388147126a763bee8f5d11594e72035aafed04c"
EXPECTED_COMMIT_MESSAGE = "test: add worker dry-run result dashboard validation hardening"

REQUIRED_SERIES_DONE_LINES = (
    "v0.8.4-A = DONE / PUSHED / CLOSED",
    "v0.8.4-B = DONE / PUSHED / CLOSED",
    "v0.8.4-C = DONE / PUSHED / CLOSED",
    "v0.8.4-D = DONE / PUSHED / VERIFIED / CLOSED",
    "v0.8.4-E = DONE / PUSHED / CLOSED",
    "v0.8.4-F = DONE / PUSHED / VERIFIED / CLOSED",
)

REQUIRED_PERMISSION_LINES = (
    "execution_permission = false",
    "dispatch_permission = false",
    "external_side_effects_permission = false",
    "result_persistence_permission = false",
    "audit_trail_write_permission = false",
)

REQUIRED_RUNTIME_LINES = (
    "worker_started = false",
    "worker_loop_started = false",
    "task_executed = false",
    "openclaw_called = false",
    "hermes_called = false",
    "google_sheets_enabled = false",
    "real_queue_db_read = false",
    "queue_written = false",
    "post_enabled = false",
    "secrets_read = false",
    "webhook_created = false",
    "endpoint_created = false",
    "connector_created = false",
    "production_db_created = false",
    "remote_blackboard_api_runtime_created = false",
)

REQUIRED_PERMISSION_KEYS = (
    "execution_permission",
    "dispatch_permission",
    "external_side_effects_permission",
    "result_persistence_permission",
    "audit_trail_write_permission",
)

REQUIRED_RUNTIME_KEYS = (
    "worker_started",
    "worker_loop_started",
    "task_executed",
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

# v0.8.3-B model has fewer keys (no result_persistence_permission / audit_trail_write_permission /
# task_executed) — kept separate so the AO check reflects that older model's actual shape.
V083_PERMISSION_KEYS = (
    "execution_permission",
    "dispatch_permission",
    "external_side_effects_permission",
)
V083_RUNTIME_KEYS = (
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

SAFETY_BOUNDARY_LINES = (
    "Hermes NOT CONNECTED",
    "OpenClaw NOT CONNECTED",
    "Worker OFF",
    "Worker loop OFF",
    "Google Sheets DISABLED",
    "No real queue DB read/write",
    "No queue write",
    "No POST",
    "No execution / dispatch",
    "No secrets",
    "No webhook",
    "No endpoint",
    "No connector",
    "No production/shared DB",
    "No Remote Blackboard API runtime",
)

# Built from (prefix, suffix) pairs and joined at runtime so the *contiguous* phrase never
# appears literally in this script's own source (avoids this check self-tripping when it
# scans its own file as part of the combined-text scan below). Mirrors the v0.8.3-G
# readiness script's UNSAFE_DONE_CLAIM_PARTS approach.
UNSAFE_DONE_CLAIM_PARTS = (
    ("Worker", " started"),
    ("Worker loop", " started"),
    ("task", " executed"),
    ("OpenClaw", " connected"),
    ("OpenClaw", " called"),
    ("Hermes", " connected"),
    ("Hermes", " called"),
    ("Google Sheets", " enabled"),
    ("real queue DB", " read"),
    ("queue", " written"),
    ("POST", " enabled"),
    ("secrets", " read"),
    ("webhook", " created"),
    ("endpoint", " created"),
    ("connector", " created"),
    ("production DB", " created"),
    ("Remote Blackboard API runtime", " created"),
    ("v0.8.5", " started"),
)
UNSAFE_DONE_CLAIMS = tuple(prefix + suffix for prefix, suffix in UNSAFE_DONE_CLAIM_PARTS)

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


def git_rev_parse(ref: str) -> str:
    out = run_git(["rev-parse", ref])
    return out.stdout.strip()


def working_tree_change_names() -> set[str]:
    return set(git_lines(["diff", "--name-only"]))


def untracked_names() -> set[str]:
    return set(git_lines(["ls-files", "--others", "--exclude-standard"]))


def is_tracked(rel: str) -> bool:
    return run_git(["ls-files", "--error-unmatch", rel]).returncode == 0


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def detect_phase() -> str:
    g_tracked = is_tracked(G_SCRIPT_REL)
    if not g_tracked:
        return "owner_review"
    head = git_rev_parse("HEAD")
    origin = git_rev_parse("origin/master")
    if head != origin:
        return "post_commit_or_ahead"
    return "post_push_or_synced"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_validator_script(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(path)],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )


# Matches bare repo-relative path tokens (docs/FOO.md, scripts/bar.py, ...) directly by
# character shape rather than by surrounding quotes. Older readiness scripts in this
# series recursively re-run *earlier* readiness scripts as reference checks, and each
# extra layer of subprocess-output repr() escapes quotes again — a naive '...'-delimited
# extraction breaks a couple of levels deep because the escaping backslashes end up
# inside the captured group. Path characters themselves (letters/digits/._/-) are never
# altered by that escaping, so matching the path shape directly stays correct at any
# nesting depth.
PATH_TOKEN_RE = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_./-]*\.(?:py|md|json)")


def only_g_untracked_fail(stdout: str, returncode: int) -> bool:
    """True if the only reported failures — at any nesting depth of re-run earlier
    readiness scripts — are an untracked-file check tripped solely by this round's new
    v0.8.4-G doc/script. An Owner Review phase artifact, not a content/safety-boundary
    failure."""
    if returncode != 1:
        return False
    fail_lines = re.findall(r"^\s*-\s*(.+)$", stdout, flags=re.MULTILINE)
    if not fail_lines:
        return False
    if not all(("untracked" in line.lower() or "unexpected" in line.lower()) for line in fail_lines):
        return False
    mentioned_paths = set(PATH_TOKEN_RE.findall("\n".join(fail_lines)))
    allowed = {G_DOC_REL, G_SCRIPT_REL, Path(G_DOC_REL).name, Path(G_SCRIPT_REL).name}
    return bool(mentioned_paths) and mentioned_paths <= allowed


def evaluate_validator(path: Path, expected_count: str) -> tuple[bool, bool, str]:
    result = run_validator_script(path)
    stdout = result.stdout
    full_pass = result.returncode == 0 and expected_count in stdout
    accepted = (not full_pass) and only_g_untracked_fail(stdout, result.returncode)
    return full_pass, accepted, stdout


def main() -> None:
    g_doc_text = read_text(G_DOC_PATH)
    self_text = read_text(G_SCRIPT_PATH)

    tracked_changed = working_tree_change_names()
    untracked = untracked_names()

    phase = detect_phase()
    print(f"INFO: detected phase = {phase}")

    # -----------------------------------------------------------------
    print("[A] current HEAD contains EXPECTED_HEAD in git history")
    is_ancestor = run_git(["merge-base", "--is-ancestor", EXPECTED_HEAD, "HEAD"]).returncode == 0
    check(f"A. HEAD contains {EXPECTED_HEAD} in git history", is_ancestor)

    print("[B] G report exists")
    check("B. G report exists", G_DOC_PATH.is_file())

    print("[C] G readiness script exists")
    check("C. G readiness script exists", G_SCRIPT_PATH.is_file())

    print("[D] G report is untracked in Owner Review phase")
    check(
        "D. G report is untracked in Owner Review phase",
        phase != "owner_review" or not is_tracked(G_DOC_REL),
    )

    print("[E] G readiness script is untracked in Owner Review phase")
    check(
        "E. G readiness script is untracked in Owner Review phase",
        phase != "owner_review" or not is_tracked(G_SCRIPT_REL),
    )

    print("[F] no tracked files modified")
    check(
        f"F. no tracked files modified（found {sorted(tracked_changed)}）"
        if tracked_changed
        else "F. no tracked files modified",
        not tracked_changed,
    )

    print("[G] untracked only G report, G script, patches/*")
    allowed_untracked = {G_DOC_REL, G_SCRIPT_REL} if phase == "owner_review" else set()
    unexpected_untracked = {
        p for p in untracked if p not in allowed_untracked and not p.startswith("patches/")
    }
    check(
        f"G. no unexpected untracked files（found {sorted(unexpected_untracked)}）"
        if unexpected_untracked
        else "G. no unexpected untracked files",
        not unexpected_untracked,
    )

    def not_modified(*rels: str) -> bool:
        return all(rel not in tracked_changed for rel in rels)

    print("[H] app/main.py not modified")
    check("H. app/main.py not modified", not_modified(MAIN_PY_REL))

    print("[I] templates/system.html not modified")
    check("I. templates/system.html not modified", not_modified(SYSTEM_HTML_REL))

    print("[J] static/dashboard.css not modified")
    check("J. static/dashboard.css not modified", not_modified(DASHBOARD_CSS_REL))

    print("[K] v0.8.4-F/E/D/C/B/A artifacts not modified")
    check(
        "K. v0.8.4-F/E/D/C/B/A artifacts not modified",
        not_modified(
            F_SCRIPT_REL,
            E_DOC_REL, E_SCRIPT_REL,
            D_SCRIPT_REL,
            C_DOC_REL, C_SCRIPT_REL,
            B_DOC_REL, B_FIXTURE_REL, B_BUILDER_REL, B_SCRIPT_REL,
            A_DOC_REL, A_SCRIPT_REL,
        ),
    )

    print("[L] v0.8.3-G/F/E/D/C/B/A artifacts not modified")
    check(
        "L. v0.8.3-G/F/E/D/C/B/A artifacts not modified",
        not_modified(
            V083_G_DOC_REL, V083_G_SCRIPT_REL,
            V083_F_SCRIPT_REL,
            V083_E_DOC_REL, V083_E_SCRIPT_REL,
            V083_D_SCRIPT_REL,
            V083_C_DOC_REL, V083_C_SCRIPT_REL,
            V083_B_DOC_REL, V083_B_FIXTURE_REL, V083_B_BUILDER_REL, V083_B_SCRIPT_REL,
            V083_A_DOC_REL, V083_A_SCRIPT_REL,
        ),
    )

    print("[M] v0.8.2 artifacts not modified")
    check(
        "M. v0.8.2 artifacts not modified",
        not_modified(
            V082_F_DOC_REL, V082_F_SCRIPT_REL,
            V082_E_SCRIPT_REL,
            V082_D_DOC_REL, V082_D_SCRIPT_REL,
            V082_C_SCRIPT_REL,
            V082_B_DOC_REL, V082_B_SCRIPT_REL,
            V082_A_SCRIPT_REL,
        ),
    )

    # -----------------------------------------------------------------
    print("[N] G report contains closeout title")
    check(
        "N. G report contains closeout title",
        "# Hermes × OpenClaw v0.8.4-G" in g_doc_text
        and "Worker Dry-run Result / Audit Trail Dashboard Display Closeout Report" in g_doc_text,
    )

    print("[O] G report contains v0.8.4-A..F done/pushed/closed statuses")
    missing_done_lines = [line for line in REQUIRED_SERIES_DONE_LINES if line not in g_doc_text]
    check(
        f"O. G report contains v0.8.4-A..F done/pushed/closed statuses（missing {missing_done_lines}）"
        if missing_done_lines
        else "O. G report contains v0.8.4-A..F done/pushed/closed statuses",
        not missing_done_lines,
    )

    print(f"[P] G report contains final HEAD {EXPECTED_HEAD}")
    check(f"P. G report contains final HEAD {EXPECTED_HEAD}", EXPECTED_HEAD in g_doc_text)

    print("[Q] G report contains final commit message")
    check("Q. G report contains final commit message", EXPECTED_COMMIT_MESSAGE in g_doc_text)

    print("[R] G report says /dashboard/system remains GET-only")
    check(
        "R. G report says /dashboard/system remains GET-only",
        "GET-only" in g_doc_text and "/dashboard/system" in g_doc_text,
    )

    print("[S] G report says Dashboard remains read-only")
    check("S. G report says Dashboard remains read-only", "Dashboard remains read-only" in g_doc_text)

    print("[T] G report says source remains synthetic_local_only")
    check(
        "T. G report says source remains synthetic_local_only",
        "`source` remains `synthetic_local_only`" in g_doc_text,
    )

    print("[U] G report says preview_only remains true")
    check(
        "U. G report says preview_only remains true",
        "`preview_only` remains `true`" in g_doc_text,
    )

    print("[V] G report records dry_run_result/audit_trail_record/owner_review_event/readback_summary preview statuses")
    required_status_values = (
        "preview_result_not_executed",
        "preview_audit_not_persisted",
        "owner_review_required",
        "preview_readback_only",
    )
    missing_status_values = [v for v in required_status_values if v not in g_doc_text]
    check(
        "V. G report records dry_run_result/audit_trail_record/owner_review_event/"
        f"readback_summary preview statuses（missing {missing_status_values}）"
        if missing_status_values
        else "V. G report records dry_run_result/audit_trail_record/owner_review_event/readback_summary preview statuses",
        not missing_status_values,
    )

    print("[W] G report says all permission flags remain false")
    missing_perm_lines = [line for line in REQUIRED_PERMISSION_LINES if line not in g_doc_text]
    check(
        f"W. G report says all permission flags remain false（missing {missing_perm_lines}）"
        if missing_perm_lines
        else "W. G report says all permission flags remain false",
        not missing_perm_lines,
    )

    print("[X] G report says all runtime flags remain false")
    missing_runtime_lines = [line for line in REQUIRED_RUNTIME_LINES if line not in g_doc_text]
    check(
        f"X. G report says all runtime flags remain false（missing {missing_runtime_lines}）"
        if missing_runtime_lines
        else "X. G report says all runtime flags remain false",
        not missing_runtime_lines,
    )

    print("[Y] G report contains safety boundary list")
    missing_boundary_lines = [line for line in SAFETY_BOUNDARY_LINES if line not in g_doc_text]
    check(
        f"Y. G report contains safety boundary list（missing {missing_boundary_lines}）"
        if missing_boundary_lines
        else "Y. G report contains safety boundary list",
        not missing_boundary_lines,
    )

    print("[Z] G report contains future v0.8.5 handoff as NOT STARTED")
    check(
        "Z. G report contains future v0.8.5 handoff as NOT STARTED",
        "v0.8.5" in g_doc_text
        and "Owner Review Decision Boundary Plan" in g_doc_text
        and "NOT STARTED" in g_doc_text,
    )

    print("[AA] G report contains no unsafe done-claims")
    combined_text = g_doc_text + "\n" + self_text

    def is_unsafe_claim_present(claim: str, text: str) -> bool:
        # A claim preceded immediately by "No "/"no " (e.g. "No real queue DB read/write")
        # is a negated safety-boundary statement, not an assertion that it happened.
        return bool(re.search(r"(?<![Nn]o )" + re.escape(claim), text))

    found_unsafe = [c for c in UNSAFE_DONE_CLAIMS if is_unsafe_claim_present(c, combined_text)]
    check(
        f"AA. G report contains no unsafe done-claims（found {found_unsafe}）"
        if found_unsafe
        else "AA. G report contains no unsafe done-claims",
        not found_unsafe,
    )

    # -----------------------------------------------------------------
    print("[AB] committed app/main.py still has /dashboard/system GET-only")
    main_py_text = read_text(MAIN_PY_PATH)
    check(
        "AB. committed app/main.py still has /dashboard/system GET-only",
        '@app.get("/dashboard/system"' in main_py_text,
    )

    print("[AC] committed template still contains worker-dry-run-result-audit-trail section")
    system_html_text = read_text(SYSTEM_HTML_PATH)
    check(
        "AC. committed template still contains worker-dry-run-result-audit-trail section",
        'id="worker-dry-run-result-audit-trail"' in system_html_text,
    )

    print("[AD] committed template has no form/button/action/method/onclick/control URLs in the section")
    section_match = re.search(
        r'<section[^>]*id="worker-dry-run-result-audit-trail".*?</section>',
        system_html_text,
        flags=re.DOTALL,
    )
    section_text = section_match.group(0) if section_match else ""
    forbidden_markup = re.findall(
        r"<form|<button|action=|method=|onclick=",
        section_text,
        flags=re.IGNORECASE,
    )
    check(
        f"AD. committed template has no form/button/action/method/onclick/control URLs in the section（found {forbidden_markup}）"
        if not section_match or forbidden_markup
        else "AD. committed template has no form/button/action/method/onclick/control URLs in the section",
        bool(section_match) and not forbidden_markup,
    )

    print("[AE] committed CSS has display classes and no cursor:pointer interactive affordance")
    css_text = read_text(DASHBOARD_CSS_PATH)
    css_idx = css_text.find(".worker-dry-run-result-audit-trail")
    css_tail = css_text[css_idx:] if css_idx != -1 else ""
    check(
        "AE. committed CSS has display classes and no cursor:pointer interactive affordance",
        css_idx != -1 and "cursor:pointer" not in css_tail.replace(" ", ""),
    )

    # -----------------------------------------------------------------
    # [AF]-[AJ], [AL] — v0.8.4-F/E/D/C/B/A validators
    # -----------------------------------------------------------------
    v084_targets = (
        ("AF", "v0.8.4-F validator", F_SCRIPT_PATH, "51/51", "PASS: v0.8.4-F"),
        ("AG", "v0.8.4-E readiness", E_SCRIPT_PATH, "46/46", "PASS: v0.8.4-E"),
        ("AH", "v0.8.4-D validation", D_SCRIPT_PATH, "33/33", "PASS: v0.8.4-D"),
        ("AI", "v0.8.4-C readiness", C_SCRIPT_PATH, "42/42", "PASS: v0.8.4-C"),
        ("AJ", "v0.8.4-B readiness", B_SCRIPT_PATH, "46/46", "PASS: v0.8.4-B"),
        ("AL", "v0.8.4-A readiness", A_SCRIPT_PATH, "40/40", "PASS: v0.8.4-A"),
    )
    for letter, name, path, expected_count, expected_marker in v084_targets:
        print(f"[{letter}] {name} PASS or only acceptable Owner Review untracked observation")
        full_pass, accepted, stdout = evaluate_validator(path, expected_count)
        full_pass = full_pass and expected_marker in stdout
        label = f"{letter}. {name} PASS or only acceptable Owner Review untracked observation"
        check(
            label
            if (full_pass or accepted)
            else f"{label}（stdout tail={stdout[-500:]!r}）",
            full_pass or accepted,
        )

    # -----------------------------------------------------------------
    # [AK] v0.8.4-B builder output remains safe (direct import, read-only reference)
    # -----------------------------------------------------------------
    print("[AK] v0.8.4-B builder output remains safe")
    b_module = load_module("worker_dry_run_result_audit_trail_boundary_v0_8_4_b", B_BUILDER_PATH)
    model = b_module.build_worker_dry_run_result_audit_trail_model()
    permissions = model.get("permissions", {})
    runtime_state = model.get("runtime_state", {})
    check(
        "AK. v0.8.4-B builder output remains safe",
        model.get("source") == "synthetic_local_only"
        and model.get("preview_only") is True
        and model.get("dry_run_result", {}).get("result_status") == "preview_result_not_executed"
        and model.get("audit_trail_record", {}).get("audit_status") == "preview_audit_not_persisted"
        and model.get("owner_review_event", {}).get("review_status") == "owner_review_required"
        and model.get("readback_summary", {}).get("summary_status") == "preview_readback_only"
        and isinstance(permissions, dict)
        and all(permissions.get(key) is False for key in REQUIRED_PERMISSION_KEYS)
        and isinstance(runtime_state, dict)
        and all(runtime_state.get(key) is False for key in REQUIRED_RUNTIME_KEYS),
    )

    # -----------------------------------------------------------------
    # [AM]-[AN] v0.8.3-F validator / v0.8.3-G readiness
    # -----------------------------------------------------------------
    v083_targets = (
        ("AM", "v0.8.3-F validator", V083_F_SCRIPT_PATH, "65/65", "PASS: v0.8.3-F"),
        ("AN", "v0.8.3-G readiness", V083_G_SCRIPT_PATH, "31/31", "PASS: v0.8.3-G"),
    )
    for letter, name, path, expected_count, expected_marker in v083_targets:
        print(f"[{letter}] {name} PASS or only acceptable Owner Review untracked observation")
        full_pass, accepted, stdout = evaluate_validator(path, expected_count)
        full_pass = full_pass and expected_marker in stdout
        label = f"{letter}. {name} PASS or only acceptable Owner Review untracked observation"
        check(
            label
            if (full_pass or accepted)
            else f"{label}（stdout tail={stdout[-500:]!r}）",
            full_pass or accepted,
        )

    # -----------------------------------------------------------------
    # [AO] v0.8.3-B builder still all permission/runtime flags false
    # -----------------------------------------------------------------
    print("[AO] v0.8.3-B builder still all permission/runtime flags false")
    v083_b_module = load_module("worker_dry_run_preview_boundary_v0_8_3_b", V083_B_BUILDER_PATH)
    v083_model = v083_b_module.build_worker_dry_run_preview_model()
    v083_permissions = v083_model.get("permissions", {})
    v083_runtime_state = v083_model.get("runtime_state", {})
    check(
        "AO. v0.8.3-B builder still all permission/runtime flags false",
        isinstance(v083_permissions, dict)
        and all(v083_permissions.get(key) is False for key in V083_PERMISSION_KEYS)
        and isinstance(v083_runtime_state, dict)
        and all(v083_runtime_state.get(key) is False for key in V083_RUNTIME_KEYS),
    )

    # -----------------------------------------------------------------
    # [AP] v0.8.2 / v0.8.1 regressions
    # -----------------------------------------------------------------
    print("[AP] v0.8.2 / v0.8.1 regressions PASS or only acceptable Owner Review untracked observation")
    regression_targets = (
        (V082_E_SCRIPT_PATH, "26/26", "PASS: v0.8.2-E"),
        (V082_C_SCRIPT_PATH, "37/37", "PASS: v0.8.2-C"),
        (V082_A_SCRIPT_PATH, "30/30", "PASS: v0.8.2-A"),
        (V082_B_SCRIPT_PATH, "35/35", "PASS: v0.8.2-B"),
        (V_SCRIPT_PATH, "72/72", "PASS: v0.8.1-V"),
        (W_SCRIPT_PATH, "88/88", "PASS: v0.8.1-W"),
        (Z_SCRIPT_PATH, "54/54", "PASS: v0.8.1-Z"),
        (Y_SCRIPT_PATH, "88/88", "PASS: v0.8.1-Y"),
        (X_SCRIPT_PATH, "98/98", "PASS: v0.8.1-X"),
    )
    regression_failures: list[str] = []
    for path, expected_count, expected_marker in regression_targets:
        full_pass, accepted, stdout = evaluate_validator(path, expected_count)
        full_pass = full_pass and expected_marker in stdout
        if not (full_pass or accepted):
            regression_failures.append(f"{path.name}: {stdout[-300:]!r}")
    check(
        "AP. v0.8.2 / v0.8.1 regressions PASS or only acceptable Owner Review untracked observation"
        if not regression_failures
        else f"AP. v0.8.2 / v0.8.1 regressions PASS or only acceptable Owner Review untracked observation（failures {regression_failures}）",
        not regression_failures,
    )

    # -----------------------------------------------------------------
    # [AQ] patches/ remains untracked
    # -----------------------------------------------------------------
    print("[AQ] patches/ remains untracked")
    patches_tracked = git_lines(["ls-files", "--", "patches/"])
    check(
        f"AQ. patches/ remains untracked（found tracked {patches_tracked}）"
        if patches_tracked
        else "AQ. patches/ remains untracked",
        not patches_tracked,
    )

    # -----------------------------------------------------------------
    # [AR] no tag
    # -----------------------------------------------------------------
    print("[AR] no tag")
    tags_at_head = git_lines(["tag", "--points-at", "HEAD"])
    check(
        f"AR. no tag（found {tags_at_head}）" if tags_at_head else "AR. no tag",
        not tags_at_head,
    )

    # -----------------------------------------------------------------
    total = len(PASS) + len(FAIL)
    print(f"\n合計：{len(PASS)}/{total} 通過")
    if FAIL:
        print(f"\nXX v0.8.4-G readiness 失敗 {len(FAIL)} 項：")
        for f in FAIL:
            print(f"   - {f}")
        sys.exit(1)
    else:
        print("PASS: v0.8.4-G worker dry-run result audit trail dashboard display closeout report")
        sys.exit(0)


if __name__ == "__main__":
    main()
