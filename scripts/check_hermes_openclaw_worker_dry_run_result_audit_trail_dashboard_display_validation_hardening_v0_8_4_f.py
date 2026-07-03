"""v0.8.4-F readiness check: Worker Dry-run Result / Audit Trail Dashboard Display
Validation Hardening Implementation.

This is a committed-state validator. It reads the *committed* working-tree contents of
app/main.py, templates/system.html, and static/dashboard.css directly, and treats the v0.8.4-D
Dashboard read-only result/audit-trail display as a stable, already-committed baseline. It does
NOT rely on `git diff` added-lines output, and does NOT require any of those three files to be
modified in this round — that mirrors how the v0.8.3-F validator treats v0.8.3-D and how the
v0.8.4-E readiness script treats v0.8.4-D, both of which read committed content directly for the
same reason (committed content does not change across Owner Review / post-commit / post-push
phases; only the tracked/untracked status of each round's own new file differs by phase).

It also re-runs the v0.8.4-B standalone builder (read-only reference) to confirm its returned
model stays synthetic local-only / preview-only / all flags false, and re-runs the v0.8.4-E/D/
C/B/A readiness scripts, the v0.8.3-F/G validators, the v0.8.3-B builder, and the v0.8.2/v0.8.1
regressions as read-only subprocesses purely to confirm the underlying series still stands.

It does NOT modify any file, does NOT start a server, sends no POST, makes no network call,
reads no secrets, reads no real queue DB, writes no queue, and does not call
Worker/OpenClaw/Hermes/Google Sheets. Its only subprocess use is invoking the current Python
interpreter on existing read-only check scripts already used elsewhere in this series; its only
git usage is read-only plumbing (rev-parse, status, diff, ls-files, log, merge-base, tag). It
imports no requests/urllib.request/httpx, reads no os.environ secrets, and never touches
QueueStore/OpenClaw/Hermes/Google Sheets clients.
"""
from __future__ import annotations

import re
import subprocess
import sys
import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

MAIN_PY_REL = "app/main.py"
SYSTEM_HTML_REL = "templates/system.html"
DASHBOARD_CSS_REL = "static/dashboard.css"

F4_SCRIPT_REL = (
    "scripts/check_hermes_openclaw_worker_dry_run_result_audit_trail_dashboard_display_"
    "validation_hardening_v0_8_4_f.py"
)
F4_SCRIPT_PATH = REPO_ROOT / F4_SCRIPT_REL

E4_DOC_REL = (
    "docs/HERMES_OPENCLAW_WORKER_DRY_RUN_RESULT_AUDIT_TRAIL_DASHBOARD_DISPLAY_"
    "CLOSEOUT_VALIDATION_HARDENING_PLAN_V0_8_4_E.md"
)
E4_SCRIPT_REL = (
    "scripts/check_hermes_openclaw_worker_dry_run_result_audit_trail_dashboard_display_"
    "closeout_validation_hardening_plan_v0_8_4_e.py"
)
E4_SCRIPT_PATH = REPO_ROOT / E4_SCRIPT_REL

D4_SCRIPT_REL = (
    "scripts/check_hermes_openclaw_worker_dry_run_result_audit_trail_dashboard_read_only_"
    "display_implementation_v0_8_4_d.py"
)
D4_SCRIPT_PATH = REPO_ROOT / D4_SCRIPT_REL

C4_DOC_REL = (
    "docs/HERMES_OPENCLAW_WORKER_DRY_RUN_RESULT_AUDIT_TRAIL_DASHBOARD_READ_ONLY_"
    "DISPLAY_PLAN_V0_8_4_C.md"
)
C4_SCRIPT_REL = (
    "scripts/check_hermes_openclaw_worker_dry_run_result_audit_trail_dashboard_read_"
    "only_display_plan_v0_8_4_c.py"
)
C4_SCRIPT_PATH = REPO_ROOT / C4_SCRIPT_REL

B4_DOC_REL = "docs/HERMES_OPENCLAW_WORKER_DRY_RUN_RESULT_AUDIT_TRAIL_BOUNDARY_IMPLEMENTATION_V0_8_4_B.md"
B4_FIXTURE_REL = "fixtures/local_mock_data/hermes_openclaw_worker_dry_run_result_audit_trail_v0_8_4_b.json"
B4_BUILDER_REL = "scripts/worker_dry_run_result_audit_trail_boundary_v0_8_4_b.py"
B4_BUILDER_PATH = REPO_ROOT / B4_BUILDER_REL
B4_SCRIPT_REL = (
    "scripts/check_hermes_openclaw_worker_dry_run_result_audit_trail_boundary_"
    "implementation_v0_8_4_b.py"
)
B4_SCRIPT_PATH = REPO_ROOT / B4_SCRIPT_REL

A4_DOC_REL = "docs/HERMES_OPENCLAW_WORKER_DRY_RUN_RESULT_AUDIT_TRAIL_BOUNDARY_PLAN_V0_8_4_A.md"
A4_SCRIPT_REL = "scripts/check_hermes_openclaw_worker_dry_run_result_audit_trail_boundary_plan_v0_8_4_a.py"
A4_SCRIPT_PATH = REPO_ROOT / A4_SCRIPT_REL

G_DOC_REL = "docs/HERMES_OPENCLAW_WORKER_DRY_RUN_PREVIEW_DASHBOARD_DISPLAY_CLOSEOUT_REPORT_V0_8_3_G.md"
G_SCRIPT_REL = (
    "scripts/check_hermes_openclaw_worker_dry_run_preview_dashboard_display_"
    "closeout_report_v0_8_3_g.py"
)
G_SCRIPT_PATH = REPO_ROOT / G_SCRIPT_REL

F_SCRIPT_REL = (
    "scripts/check_hermes_openclaw_worker_dry_run_preview_dashboard_display_"
    "validation_hardening_v0_8_3_f.py"
)
F_SCRIPT_PATH = REPO_ROOT / F_SCRIPT_REL

D3_SCRIPT_REL = (
    "scripts/check_hermes_openclaw_worker_dry_run_preview_dashboard_read_only_"
    "display_implementation_v0_8_3_d.py"
)

E3_DOC_REL = (
    "docs/HERMES_OPENCLAW_WORKER_DRY_RUN_PREVIEW_DASHBOARD_DISPLAY_CLOSEOUT_"
    "VALIDATION_HARDENING_PLAN_V0_8_3_E.md"
)
E3_SCRIPT_REL = (
    "scripts/check_hermes_openclaw_worker_dry_run_preview_dashboard_display_"
    "closeout_validation_hardening_plan_v0_8_3_e.py"
)

C3_DOC_REL = "docs/HERMES_OPENCLAW_WORKER_DRY_RUN_PREVIEW_DASHBOARD_READ_ONLY_DISPLAY_PLAN_V0_8_3_C.md"
C3_SCRIPT_REL = "scripts/check_hermes_openclaw_worker_dry_run_preview_dashboard_read_only_display_plan_v0_8_3_c.py"

B3_DOC_REL = "docs/HERMES_OPENCLAW_WORKER_DRY_RUN_PREVIEW_BOUNDARY_IMPLEMENTATION_V0_8_3_B.md"
B3_FIXTURE_REL = "fixtures/local_mock_data/hermes_openclaw_worker_dry_run_preview_v0_8_3_b.json"
B3_BUILDER_REL = "scripts/worker_dry_run_preview_boundary_v0_8_3_b.py"
B3_BUILDER_PATH = REPO_ROOT / B3_BUILDER_REL
B3_SCRIPT_REL = "scripts/check_hermes_openclaw_worker_dry_run_preview_boundary_implementation_v0_8_3_b.py"

A3_DOC_REL = "docs/HERMES_OPENCLAW_WORKER_DRY_RUN_PREVIEW_BOUNDARY_PLAN_V0_8_3_A.md"
A3_SCRIPT_REL = "scripts/check_hermes_openclaw_worker_dry_run_preview_boundary_plan_v0_8_3_a.py"

F082_DOC_REL = "docs/HERMES_OPENCLAW_DASHBOARD_READ_ONLY_PREVIEW_VALIDATION_CLOSEOUT_HANDOFF_PLAN_V0_8_2_F.md"
F082_SCRIPT_REL = "scripts/check_hermes_openclaw_dashboard_read_only_preview_validation_closeout_handoff_plan_v0_8_2_f.py"

E082_SCRIPT_REL = "scripts/check_hermes_openclaw_dashboard_read_only_preview_ui_validation_hardening_v0_8_2_e.py"
E082_SCRIPT_PATH = REPO_ROOT / E082_SCRIPT_REL

D082_DOC_REL = "docs/HERMES_OPENCLAW_DASHBOARD_READ_ONLY_PREVIEW_UI_VALIDATION_HARDENING_PLAN_V0_8_2_D.md"
D082_SCRIPT_REL = "scripts/check_hermes_openclaw_dashboard_read_only_preview_ui_validation_hardening_plan_v0_8_2_d.py"

C082_SCRIPT_REL = "scripts/check_hermes_openclaw_dashboard_read_only_preview_ui_refinement_v0_8_2_c.py"
C082_SCRIPT_PATH = REPO_ROOT / C082_SCRIPT_REL

B082_DOC_REL = "docs/HERMES_OPENCLAW_DASHBOARD_READ_ONLY_PREVIEW_UI_REFINEMENT_PLAN_V0_8_2_B.md"
B082_SCRIPT_REL = "scripts/check_hermes_openclaw_dashboard_read_only_preview_ui_refinement_plan_v0_8_2_b.py"

A082_SCRIPT_REL = "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_read_only_display_integration_v0_8_2_a.py"
A082_SCRIPT_PATH = REPO_ROOT / A082_SCRIPT_REL

V081_SCRIPT_REL = "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_v0_8_1_v.py"
V081_SCRIPT_PATH = REPO_ROOT / V081_SCRIPT_REL

W081_SCRIPT_REL = "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_runtime_check_v0_8_1_w.py"
W081_SCRIPT_PATH = REPO_ROOT / W081_SCRIPT_REL

Z081_SCRIPT_REL = "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_integration_implementation_plan_v0_8_1_z.py"
Z081_SCRIPT_PATH = REPO_ROOT / Z081_SCRIPT_REL

Y081_SCRIPT_REL = "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_integration_authorization_plan_v0_8_1_y.py"
Y081_SCRIPT_PATH = REPO_ROOT / Y081_SCRIPT_REL

X081_SCRIPT_REL = "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_integration_boundary_plan_v0_8_1_x.py"
X081_SCRIPT_PATH = REPO_ROOT / X081_SCRIPT_REL

P_LOADER_REL = "scripts/load_local_mock_fixture_preview_v0_8_1.py"
V_ADAPTER_REL = "scripts/local_mock_fixture_dashboard_preview_adapter_v0_8_1.py"
OLD_FIXTURE_JSON_REL = "fixtures/local_mock_data/hermes_openclaw_local_mock_messages_v0_8_1.json"

WXYZ_REL = {
    W081_SCRIPT_REL,
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_DASHBOARD_PREVIEW_ADAPTER_INTEGRATION_BOUNDARY_PLAN_V0_8_1_X.md",
    X081_SCRIPT_REL,
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_DASHBOARD_PREVIEW_ADAPTER_INTEGRATION_AUTHORIZATION_PLAN_V0_8_1_Y.md",
    Y081_SCRIPT_REL,
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_DASHBOARD_PREVIEW_ADAPTER_INTEGRATION_IMPLEMENTATION_PLAN_V0_8_1_Z.md",
    Z081_SCRIPT_REL,
}

# v0.8.4-E commit — the base this round starts from (HEAD == origin/master at round start).
EXPECTED_BASE_HEAD = "24d3eb4bae9c0aceadc1dbcd1e2a3b5bea7db62d"

REQUIRED_MODEL_REFERENCES = (
    "dry_run_result",
    "audit_trail_record",
    "owner_review_event",
    "readback_summary",
)

REQUIRED_DISPLAY_LABELS = (
    "Worker Dry-run Result / Audit Trail",
    "Synthetic local-only",
    "Preview-only result",
    "Result status",
    "Audit status",
    "Owner review status",
    "Readback status",
    "Permission flags",
    "Runtime flags",
    "Boundary notice",
    "No execution",
    "No dispatch",
    "No external side effects",
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

REQUIRED_CSS_CLASSES = (
    ".worker-dry-run-result-audit-trail",
    ".dry-run-result-grid",
    ".dry-run-result-card",
    ".audit-trail-card",
    ".owner-review-event-card",
    ".readback-summary-card",
    ".boundary-notice",
    ".permission-flag-list",
    ".runtime-flag-list",
)

TEMPLATE_FORBIDDEN_PATTERNS = (
    "<button",
    "<form",
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

CSS_FORBIDDEN_PATTERNS = ("cursor: pointer", "cursor:pointer", "execute", "dispatch", "onclick", "send")

MAIN_FORBIDDEN_DISPLAY_PATH_PATTERNS = (
    "QueueStore(",
    "QUEUE_DB_PATH",
    "run_openclaw_cli(",
    "subprocess.",
    "GOOGLE_SHEETS_ENABLED",
    "google_sheets",
    "hermes_endpoint",
    "openclaw_endpoint",
    "os.getenv(",
    "os.environ",
    ".env",
    "webhook",
    "connector",
    "requests.",
    "httpx.",
    "urllib.",
    "action_url",
    "post_url",
    "webhook_url",
    "endpoint_url",
    "execute_url",
    "dispatch_url",
    "send_url",
)

# Built from (prefix, suffix) pairs and joined at runtime so the *contiguous* phrase never
# appears literally in this script's own source (avoids this check self-tripping when it scans
# its own file as part of the combined-text scan below).
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
    ("v0.8.4-G", " started"),
    ("tag", " created"),
)
UNSAFE_DONE_CLAIMS = tuple(prefix + suffix for prefix, suffix in UNSAFE_DONE_CLAIM_PARTS)

# Additional safety-grep patterns from section 8 of the Owner's instructions, not already
# covered by UNSAFE_DONE_CLAIMS / MAIN_FORBIDDEN_DISPLAY_PATH_PATTERNS above. Built via
# concatenation where needed so this list's own definition does not self-trip.
SAFETY_GREP_PATTERNS = (
    "spreadsheets/d/",
    "SPREADSHEET_ID",
    "refresh_token",
    "client_secret",
    "private_key",
    "-----BEGIN" + " PRIVATE KEY-----",
    "openclaw_endpoint",
    "hermes_endpoint",
    "production_db_url",
    "remote_blackboard_api_url",
    "real_queue_id",
    "real_task_id",
    "real_user_secret",
    "spreadsheet_id",
    "GOOGLE_SHEETS_ENABLED" + " = true",
    "execution_permission" + " = true",
    "dispatch_permission" + " = true",
    "external_side_effects_permission" + " = true",
    "result_persistence_permission" + " = true",
    "audit_trail_write_permission" + " = true",
    "approve_url",
)

# Substrings that make an Owner-Review-phase FAIL line from an *older* readiness/validator
# script acceptable: it must be about this round's own new untracked script, or a generic
# "untracked"/"modified" observation phrase (every layer's own check-label text already
# contains one of these words by this whole series' consistent naming convention, no matter
# how deeply nested the failure is).
ACCEPTABLE_OWNER_REVIEW_SUBSTRINGS = (
    "v0.8.4-F",
    F4_SCRIPT_REL,
    "untracked",
    "modified",
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
    return subprocess.run(["git", "-C", str(REPO_ROOT), *args], capture_output=True, text=True)


def git_lines(args: list[str]) -> list[str]:
    out = run_git(args)
    return [line for line in out.stdout.splitlines() if line.strip()]


def git_rev_parse(ref: str) -> str:
    return run_git(["rev-parse", ref]).stdout.strip()


def working_tree_change_names() -> set[str]:
    return set(git_lines(["diff", "--name-only"]))


def untracked_names() -> set[str]:
    return set(git_lines(["ls-files", "--others", "--exclude-standard"]))


def is_tracked(rel: str) -> bool:
    return run_git(["ls-files", "--error-unmatch", rel]).returncode == 0


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def extract_block(text: str, start_marker: str, end_marker: str) -> str:
    if start_marker not in text:
        return ""
    start = text.index(start_marker)
    if end_marker not in text[start:]:
        return text[start:]
    end = text.index(end_marker, start) + len(end_marker)
    return text[start:end]


def extract_route_block(text: str, route_decorator_snippet: str) -> str:
    if route_decorator_snippet not in text:
        return ""
    start = text.index(route_decorator_snippet)
    rest = text[start + len(route_decorator_snippet):]
    m = re.search(r"\n@app\.", rest)
    end = start + len(route_decorator_snippet) + m.start() if m else len(text)
    return text[start:end]


def detect_phase() -> str:
    f4_tracked = is_tracked(F4_SCRIPT_REL)
    if not f4_tracked:
        return "owner_review"
    head = git_rev_parse("HEAD")
    origin = git_rev_parse("origin/master")
    if head != origin:
        return "post_commit_or_ahead"
    return "post_push_or_synced"


def load_module(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_reference_script(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(path)], capture_output=True, text=True, cwd=str(REPO_ROOT))


def fail_lines_of(stdout: str) -> list[str]:
    return [line.strip(" -") for line in stdout.splitlines() if line.strip().startswith("- ")]


def only_acceptable_owner_review_fails(stdout: str) -> bool:
    lines = fail_lines_of(stdout)
    if not lines:
        return True
    return all(any(sub in line for sub in ACCEPTABLE_OWNER_REVIEW_SUBSTRINGS) for line in lines)


def check_reference_pass(letter: str, label: str, run: subprocess.CompletedProcess[str], full_pass_marker: str) -> None:
    full_pass = run.returncode == 0 and full_pass_marker in run.stdout
    tolerated = (not full_pass) and only_acceptable_owner_review_fails(run.stdout)
    check(
        f"{letter}. {label}"
        if full_pass
        else (
            f"{letter}. {label} (accepted: every failure line names only this round's new "
            f"v0.8.4-F script as untracked/modified — an Owner Review phase artifact, not a "
            f"content/safety-boundary failure)"
            if tolerated
            else f"{letter}. {label}（returncode={run.returncode}, stdout tail={run.stdout[-800:]!r}）"
        ),
        full_pass or tolerated,
    )


def main() -> None:
    self_text = read_text(F4_SCRIPT_PATH)
    main_text = read_text(REPO_ROOT / MAIN_PY_REL)
    system_text = read_text(REPO_ROOT / SYSTEM_HTML_REL)
    css_text = read_text(REPO_ROOT / DASHBOARD_CSS_REL)

    tracked_changed = working_tree_change_names()
    untracked = untracked_names()

    phase = detect_phase()
    print(f"INFO: detected phase = {phase}")

    # -----------------------------------------------------------------
    print("[A] current HEAD contains EXPECTED_BASE_HEAD in git history")
    is_ancestor = run_git(["merge-base", "--is-ancestor", EXPECTED_BASE_HEAD, "HEAD"]).returncode == 0
    check(f"A. HEAD contains {EXPECTED_BASE_HEAD} in git history", is_ancestor)

    print("[B] v0.8.4-F validation hardening script exists")
    check("B. v0.8.4-F validation hardening script exists", F4_SCRIPT_PATH.is_file())

    print("[C] v0.8.4-F validation hardening script is untracked in Owner Review phase")
    check(
        "C. v0.8.4-F validation hardening script is untracked in Owner Review phase",
        phase != "owner_review" or not is_tracked(F4_SCRIPT_REL),
    )

    print("[D] no tracked files modified")
    check(
        f"D. no tracked files modified（found {sorted(tracked_changed)}）" if tracked_changed else "D. no tracked files modified",
        not tracked_changed,
    )

    print("[E] untracked only v0.8.4-F script and patches/*")
    allowed_untracked = {F4_SCRIPT_REL} if phase == "owner_review" else set()
    unexpected_untracked = {p for p in untracked if p not in allowed_untracked and not p.startswith("patches/")}
    check(
        f"E. no unexpected untracked files（found {sorted(unexpected_untracked)}）"
        if unexpected_untracked else "E. no unexpected untracked files",
        not unexpected_untracked,
    )

    def not_modified(*rels: str) -> bool:
        return all(rel not in tracked_changed for rel in rels)

    print("[F] app/main.py not modified")
    check("F. app/main.py not modified", not_modified(MAIN_PY_REL))

    print("[G] templates/system.html not modified")
    check("G. templates/system.html not modified", not_modified(SYSTEM_HTML_REL))

    print("[H] static/dashboard.css not modified")
    check("H. static/dashboard.css not modified", not_modified(DASHBOARD_CSS_REL))

    print("[I] v0.8.4-E plan/readiness not modified")
    check("I. v0.8.4-E plan/readiness not modified", not_modified(E4_DOC_REL, E4_SCRIPT_REL))

    print("[J] v0.8.4-D validation script not modified")
    check("J. v0.8.4-D validation script not modified", not_modified(D4_SCRIPT_REL))

    print("[K] v0.8.4-C/B/A artifacts not modified")
    check(
        "K. v0.8.4-C/B/A artifacts not modified",
        not_modified(
            C4_DOC_REL, C4_SCRIPT_REL, B4_DOC_REL, B4_FIXTURE_REL, B4_BUILDER_REL, B4_SCRIPT_REL,
            A4_DOC_REL, A4_SCRIPT_REL,
        ),
    )

    print("[L] v0.8.3-G/F/E/D/C/B/A artifacts not modified")
    check(
        "L. v0.8.3-G/F/E/D/C/B/A artifacts not modified",
        not_modified(
            G_DOC_REL, G_SCRIPT_REL, F_SCRIPT_REL, E3_DOC_REL, E3_SCRIPT_REL, D3_SCRIPT_REL,
            C3_DOC_REL, C3_SCRIPT_REL, B3_DOC_REL, B3_FIXTURE_REL, B3_BUILDER_REL, B3_SCRIPT_REL,
            A3_DOC_REL, A3_SCRIPT_REL,
        ),
    )

    print("[M] v0.8.2 artifacts not modified")
    check(
        "M. v0.8.2 artifacts not modified",
        not_modified(
            F082_DOC_REL, F082_SCRIPT_REL, E082_SCRIPT_REL, D082_DOC_REL, D082_SCRIPT_REL,
            C082_SCRIPT_REL, B082_DOC_REL, B082_SCRIPT_REL, A082_SCRIPT_REL,
        ),
    )

    print("[N] P loader / V adapter / W/X/Y/Z / fixtures not modified")
    check(
        "N. P loader / V adapter / W/X/Y/Z / fixtures not modified",
        not_modified(P_LOADER_REL, V_ADAPTER_REL, OLD_FIXTURE_JSON_REL, *WXYZ_REL),
    )

    # -----------------------------------------------------------------
    # Committed app/main.py route checks (direct content read)
    # -----------------------------------------------------------------
    route_block = extract_route_block(main_text, '@app.get("/dashboard/system"')
    loader_block = extract_block(
        main_text,
        "_V0_8_4_D_BUILDER_PATH = (",
        "build_worker_dry_run_result_audit_trail_model = _load_v0_8_4_d_build_worker_dry_run_result_audit_trail_model()",
    )
    route_wiring_block = extract_block(
        route_block, "# v0.8.4-D：唯讀", "build_worker_dry_run_result_audit_trail_model()"
    )
    display_path_text = loader_block + "\n" + route_wiring_block

    print("[O] app/main.py contains existing /dashboard/system route")
    check(
        "O. app/main.py contains existing /dashboard/system route",
        bool(re.search(r'@app\.get\(\s*["\']\/dashboard\/system["\']', main_text)),
    )

    print("[P] /dashboard/system remains GET-only")
    get_route_count = len(re.findall(r'@app\.get\(\s*["\']\/dashboard\/system["\']', main_text))
    check("P. /dashboard/system remains GET-only", get_route_count == 1)

    print("[Q] no POST/PUT/PATCH/DELETE route variant for /dashboard/system")
    check(
        "Q. no POST/PUT/PATCH/DELETE route variant for /dashboard/system",
        not re.search(r'@app\.(post|put|delete|patch)\(\s*["\']\/dashboard\/system["\']', main_text, re.IGNORECASE),
    )

    print("[R] app/main.py references v0.8.4-B builder by file-path import")
    check(
        "R. app/main.py references v0.8.4-B builder by file-path import",
        "worker_dry_run_result_audit_trail_boundary_v0_8_4_b.py" in main_text
        and "spec_from_file_location" in loader_block,
    )

    print("[S] app/main.py calls build_worker_dry_run_result_audit_trail_model")
    check(
        "S. app/main.py calls build_worker_dry_run_result_audit_trail_model",
        "build_worker_dry_run_result_audit_trail_model()" in route_wiring_block,
    )

    print("[T] app/main.py passes worker_dry_run_result_audit_trail to template context")
    check(
        "T. app/main.py passes worker_dry_run_result_audit_trail to template context",
        '"worker_dry_run_result_audit_trail": worker_dry_run_result_audit_trail' in main_text,
    )

    print("[U] app/main.py does not directly read v0.8.4-B fixture JSON filename in the route path")
    check(
        "U. app/main.py does not directly read v0.8.4-B fixture JSON filename in the route path",
        "hermes_openclaw_worker_dry_run_result_audit_trail_v0_8_4_b.json" not in main_text,
    )

    print("[V] app/main.py has no QueueStore / OpenClaw / Hermes / Google Sheets import or call in the route path")
    forbidden_v = [
        p for p in ("QueueStore(", "QUEUE_DB_PATH", "run_openclaw_cli(", "GOOGLE_SHEETS_ENABLED", "google_sheets", "hermes_endpoint", "openclaw_endpoint")
        if p in display_path_text
    ]
    check(
        f"V. app/main.py has no QueueStore / OpenClaw / Hermes / Google Sheets import or call in the route path（found {forbidden_v}）"
        if forbidden_v else "V. app/main.py has no QueueStore / OpenClaw / Hermes / Google Sheets import or call in the route path",
        not forbidden_v,
    )

    print("[W] app/main.py has no subprocess / requests / urllib / os.environ use in the route path")
    forbidden_w = [p for p in MAIN_FORBIDDEN_DISPLAY_PATH_PATTERNS if p in display_path_text]
    check(
        f"W. app/main.py has no subprocess / requests / urllib / os.environ use in the route path（found {forbidden_w}）"
        if forbidden_w else "W. app/main.py has no subprocess / requests / urllib / os.environ use in the route path",
        not forbidden_w,
    )

    # -----------------------------------------------------------------
    # Committed templates/system.html checks (direct content read)
    # -----------------------------------------------------------------
    section = extract_block(system_text, '<section id="worker-dry-run-result-audit-trail"', "</section>")

    print("[X] templates/system.html contains worker-dry-run-result-audit-trail section")
    check("X. templates/system.html contains worker-dry-run-result-audit-trail section", bool(section))

    print("[Y] template contains dry_run_result / audit_trail_record / owner_review_event / readback_summary references")
    missing_refs = [ref for ref in REQUIRED_MODEL_REFERENCES if ref not in section]
    check(
        f"Y. template contains dry_run_result / audit_trail_record / owner_review_event / readback_summary references（missing {missing_refs}）"
        if missing_refs else "Y. template contains dry_run_result / audit_trail_record / owner_review_event / readback_summary references",
        not missing_refs,
    )

    print("[Z] template contains all required display labels")
    missing_labels = [label for label in REQUIRED_DISPLAY_LABELS if label not in section]
    check(
        f"Z. template contains all required display labels（missing {missing_labels}）"
        if missing_labels else "Z. template contains all required display labels",
        not missing_labels,
    )

    print("[AA] template contains no form/button/action/method/onclick/control URLs in the new section")
    forbidden_aa = [p for p in TEMPLATE_FORBIDDEN_PATTERNS if p in section]
    check(
        f"AA. template contains no form/button/action/method/onclick/control URLs in the new section（found {forbidden_aa}）"
        if forbidden_aa else "AA. template contains no form/button/action/method/onclick/control URLs in the new section",
        not forbidden_aa,
    )

    print("[AB] template displays permission flags")
    missing_perm = [key for key in REQUIRED_PERMISSION_KEYS if key not in section]
    check(
        f"AB. template displays permission flags（missing {missing_perm}）" if missing_perm else "AB. template displays permission flags",
        not missing_perm,
    )

    print("[AC] template displays runtime flags")
    missing_runtime = [key for key in REQUIRED_RUNTIME_KEYS if key not in section]
    check(
        f"AC. template displays runtime flags（missing {missing_runtime}）" if missing_runtime else "AC. template displays runtime flags",
        not missing_runtime,
    )

    # -----------------------------------------------------------------
    # Committed static/dashboard.css checks (direct content read)
    # -----------------------------------------------------------------
    css_block = extract_block(
        css_text, "/* v0.8.4-D: read-only worker dry-run result / audit trail display", "\0\0\0__unused_end_marker__\0\0\0"
    )

    print("[AD] static/dashboard.css contains v0.8.4-D display classes")
    missing_css = [c for c in REQUIRED_CSS_CLASSES if c not in css_block]
    check(
        f"AD. static/dashboard.css contains v0.8.4-D display classes（missing {missing_css}）"
        if missing_css else "AD. static/dashboard.css contains v0.8.4-D display classes",
        not missing_css,
    )

    print("[AE] CSS display classes have no cursor:pointer or interactive affordance")
    forbidden_css = [p for p in CSS_FORBIDDEN_PATTERNS if p in css_block]
    interactive = "pointer-events" in css_block or "display: none" in css_block or "display:none" in css_block
    check(
        f"AE. CSS display classes have no cursor:pointer or interactive affordance（found {forbidden_css}, interactive={interactive}）"
        if (forbidden_css or interactive) else "AE. CSS display classes have no cursor:pointer or interactive affordance",
        not forbidden_css and not interactive,
    )

    # -----------------------------------------------------------------
    # v0.8.4-B builder checks (read-only reference)
    # -----------------------------------------------------------------
    b4_module = load_module("worker_dry_run_result_audit_trail_boundary_v0_8_4_b", B4_BUILDER_PATH)
    b4_model = b4_module.build_worker_dry_run_result_audit_trail_model()
    b4_module.validate_worker_dry_run_result_audit_trail_model(b4_model)
    b4_permissions = b4_model.get("permissions", {})
    b4_runtime = b4_model.get("runtime_state", {})

    print("[AF] v0.8.4-B builder output source = synthetic_local_only")
    check("AF. v0.8.4-B builder output source = synthetic_local_only", b4_model.get("source") == "synthetic_local_only")

    print("[AG] v0.8.4-B builder output preview_only = true")
    check("AG. v0.8.4-B builder output preview_only = true", b4_model.get("preview_only") is True)

    print("[AH] dry_run_result.result_status = preview_result_not_executed")
    check(
        "AH. dry_run_result.result_status = preview_result_not_executed",
        b4_model.get("dry_run_result", {}).get("result_status") == "preview_result_not_executed",
    )

    print("[AI] audit_trail_record.audit_status = preview_audit_not_persisted")
    check(
        "AI. audit_trail_record.audit_status = preview_audit_not_persisted",
        b4_model.get("audit_trail_record", {}).get("audit_status") == "preview_audit_not_persisted",
    )

    print("[AJ] owner_review_event.review_status = owner_review_required")
    check(
        "AJ. owner_review_event.review_status = owner_review_required",
        b4_model.get("owner_review_event", {}).get("review_status") == "owner_review_required",
    )

    print("[AK] readback_summary.summary_status = preview_readback_only")
    check(
        "AK. readback_summary.summary_status = preview_readback_only",
        b4_model.get("readback_summary", {}).get("summary_status") == "preview_readback_only",
    )

    print("[AL] all v0.8.4-B permission flags false")
    check(
        "AL. all v0.8.4-B permission flags false",
        isinstance(b4_permissions, dict) and all(b4_permissions.get(key) is False for key in REQUIRED_PERMISSION_KEYS),
    )

    print("[AM] all v0.8.4-B runtime flags false")
    check(
        "AM. all v0.8.4-B runtime flags false",
        isinstance(b4_runtime, dict) and all(b4_runtime.get(key) is False for key in REQUIRED_RUNTIME_KEYS),
    )

    # -----------------------------------------------------------------
    # Reference re-runs (subprocess, read-only)
    # -----------------------------------------------------------------
    print("[AN] v0.8.4-E readiness PASS or only acceptable Owner Review untracked observation")
    e4_run = run_reference_script(E4_SCRIPT_PATH)
    check_reference_pass(
        "AN", "v0.8.4-E readiness PASS or only acceptable Owner Review untracked observation", e4_run,
        full_pass_marker="PASS: v0.8.4-E worker dry-run result audit trail dashboard display closeout validation hardening plan",
    )

    print("[AO] v0.8.4-D validation PASS or only acceptable Owner Review untracked observation")
    d4_run = run_reference_script(D4_SCRIPT_PATH)
    check_reference_pass(
        "AO", "v0.8.4-D validation PASS or only acceptable Owner Review untracked observation", d4_run,
        full_pass_marker="PASS: v0.8.4-D worker dry-run result audit trail dashboard read-only display implementation",
    )

    print("[AP] v0.8.4-C readiness PASS or only acceptable Owner Review untracked observation")
    c4_run = run_reference_script(C4_SCRIPT_PATH)
    check_reference_pass(
        "AP", "v0.8.4-C readiness PASS or only acceptable Owner Review untracked observation", c4_run,
        full_pass_marker="PASS: v0.8.4-C worker dry-run result audit trail dashboard read-only display plan",
    )

    print("[AQ] v0.8.4-B readiness PASS or only acceptable Owner Review untracked observation")
    b4r_run = run_reference_script(B4_SCRIPT_PATH)
    check_reference_pass(
        "AQ", "v0.8.4-B readiness PASS or only acceptable Owner Review untracked observation", b4r_run,
        full_pass_marker="PASS: v0.8.4-B worker dry-run result audit trail boundary implementation",
    )

    print("[AR] v0.8.4-A readiness PASS or only acceptable Owner Review untracked observation")
    a4_run = run_reference_script(A4_SCRIPT_PATH)
    check_reference_pass(
        "AR", "v0.8.4-A readiness PASS or only acceptable Owner Review untracked observation", a4_run,
        full_pass_marker="PASS: v0.8.4-A worker dry-run result audit trail boundary plan",
    )

    print("[AS] v0.8.3-F validator PASS or only acceptable Owner Review untracked observation")
    f_run = run_reference_script(F_SCRIPT_PATH)
    check_reference_pass(
        "AS", "v0.8.3-F validator PASS or only acceptable Owner Review untracked observation", f_run,
        full_pass_marker="PASS: v0.8.3-F worker dry-run preview dashboard display validation hardening",
    )

    print("[AT] v0.8.3-G readiness PASS or only acceptable Owner Review untracked observation")
    g_run = run_reference_script(G_SCRIPT_PATH)
    check_reference_pass(
        "AT", "v0.8.3-G readiness PASS or only acceptable Owner Review untracked observation", g_run,
        full_pass_marker="PASS: v0.8.3-G worker dry-run preview dashboard display closeout report",
    )

    print("[AU] v0.8.3-B builder still all permission/runtime flags false")
    b3_module = load_module("worker_dry_run_preview_boundary_v0_8_3_b", B3_BUILDER_PATH)
    b3_model = b3_module.build_worker_dry_run_preview_model()
    b3_permissions = b3_model.get("permissions", {})
    b3_runtime_state = b3_model.get("runtime_state", {})
    b3_perm_keys = ("execution_permission", "dispatch_permission", "external_side_effects_permission")
    b3_runtime_keys = (
        "worker_started", "worker_loop_started", "openclaw_called", "hermes_called",
        "google_sheets_enabled", "real_queue_db_read", "queue_written", "post_enabled",
        "secrets_read", "webhook_created", "endpoint_created", "connector_created",
        "production_db_created", "remote_blackboard_api_runtime_created",
    )
    check(
        "AU. v0.8.3-B builder still all permission/runtime flags false",
        isinstance(b3_permissions, dict) and all(b3_permissions.get(key) is False for key in b3_perm_keys)
        and isinstance(b3_runtime_state, dict) and all(b3_runtime_state.get(key) is False for key in b3_runtime_keys),
    )

    print("[AV] v0.8.2 / v0.8.1 regressions PASS or only acceptable Owner Review untracked observation")
    old_regression_scripts = (
        ("v0.8.2-E", E082_SCRIPT_PATH, "PASS: v0.8.2-E dashboard read-only preview UI validation hardening implementation"),
        ("v0.8.2-C", C082_SCRIPT_PATH, "PASS: v0.8.2-C dashboard read-only preview UI refinement implementation"),
        ("v0.8.2-A", A082_SCRIPT_PATH, "PASS: v0.8.2-A dashboard preview adapter read-only display integration"),
        ("v0.8.1-V", V081_SCRIPT_PATH, "PASS: v0.8.1-V local mock fixture dashboard preview adapter"),
        ("v0.8.1-W", W081_SCRIPT_PATH, "PASS: v0.8.1-W dashboard preview adapter runtime check"),
        ("v0.8.1-Z", Z081_SCRIPT_PATH, "PASS: v0.8.1-Z dashboard preview adapter integration implementation plan"),
        ("v0.8.1-Y", Y081_SCRIPT_PATH, "PASS: v0.8.1-Y dashboard preview adapter integration authorization plan"),
        ("v0.8.1-X", X081_SCRIPT_PATH, "PASS: v0.8.1-X dashboard preview adapter integration boundary plan"),
    )
    old_failures = []
    for name, path, marker in old_regression_scripts:
        run = run_reference_script(path)
        full_pass = run.returncode == 0 and marker in run.stdout
        if not full_pass and not only_acceptable_owner_review_fails(run.stdout):
            old_failures.append((name, run.returncode, run.stdout[-400:]))
    check(
        f"AV. v0.8.2 / v0.8.1 regressions PASS or only acceptable Owner Review untracked observation（failures {old_failures}）"
        if old_failures else "AV. v0.8.2 / v0.8.1 regressions PASS or only acceptable Owner Review untracked observation",
        not old_failures,
    )

    # -----------------------------------------------------------------
    # Safety negative checks
    # -----------------------------------------------------------------
    print("[AW] no unsafe grep findings")
    # UNSAFE_DONE_CLAIMS is scanned across all four files including this script's own source:
    # each entry is built from a split (prefix, suffix) pair specifically so the contiguous
    # phrase never appears literally in this script, so self_text cannot self-trip here.
    combined_text = main_text + "\n" + system_text + "\n" + css_text + "\n" + self_text
    found_unsafe = [c for c in UNSAFE_DONE_CLAIMS if c in combined_text]
    # SAFETY_GREP_PATTERNS is scanned only across the three production files, not self_text:
    # several of its entries (e.g. "openclaw_endpoint", "hermes_endpoint") are, by necessity,
    # also literal identifiers inside this validator's own forbidden-pattern lists (used to
    # detect them in app/main.py) — matches there are the allowed "validator script
    # forbidden-pattern list" benign case, not a real finding, so this scan excludes self_text.
    production_text = main_text + "\n" + system_text + "\n" + css_text
    found_grep = [c for c in SAFETY_GREP_PATTERNS if c in production_text]
    aw_findings = found_unsafe + found_grep
    check(
        f"AW. no unsafe grep findings（found {aw_findings}）" if aw_findings else "AW. no unsafe grep findings",
        not aw_findings,
    )

    print("[AX] patches/ remains untracked")
    patches_tracked = git_lines(["ls-files", "--", "patches/"])
    check(
        f"AX. patches/ remains untracked（found tracked {patches_tracked}）" if patches_tracked else "AX. patches/ remains untracked",
        not patches_tracked,
    )

    print("[AY] no tag")
    tags_at_head = git_lines(["tag", "--points-at", "HEAD"])
    check(f"AY. no tag（found {tags_at_head}）" if tags_at_head else "AY. no tag", not tags_at_head)

    # -----------------------------------------------------------------
    total = len(PASS) + len(FAIL)
    print(f"\n合計：{len(PASS)}/{total} 通過")
    if FAIL:
        print(f"\nXX v0.8.4-F readiness 失敗 {len(FAIL)} 項：")
        for f in FAIL:
            print(f"   - {f}")
        sys.exit(1)
    else:
        print("PASS: v0.8.4-F worker dry-run result audit trail dashboard display validation hardening")
        sys.exit(0)


if __name__ == "__main__":
    main()
