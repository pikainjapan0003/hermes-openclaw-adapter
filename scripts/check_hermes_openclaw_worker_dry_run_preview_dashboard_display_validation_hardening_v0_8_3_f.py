"""v0.8.3-F readiness check: Worker Dry-run Preview Dashboard Display Validation Hardening.

Pure local filesystem + git metadata validation. Unlike the v0.8.3-D readiness script, this
validator does NOT rely on `git diff --unified=0` added-lines output as its primary content
source (see the v0.8.3-E plan doc's explanation of the v0.8.3-D post-push 36/52 observation).
Instead it reads the *committed* contents of `app/main.py`, `templates/system.html`, and
`static/dashboard.css` directly from the working tree and checks for the required v0.8.3-B/D
wiring and the absence of forbidden route/control patterns. Because committed file content does
not change across Owner Review / local-commit / post-push phases (this round only adds a new,
independent script), the same content checks stay valid in all three phases. Only the *tracked
vs. untracked* status of this script itself (and HEAD vs. origin/master) differs by phase, which
is handled separately via `detect_phase()`.

It also re-runs the v0.8.3-B standalone builder (read-only reference check) to confirm its
returned model stays synthetic local-only / preview-only / all flags false.

It does NOT import app runtime, Dashboard runtime, QueueStore, Worker/OpenClaw/Hermes/Google
Sheets integration, the v0.8.1-P loader, or the v0.8.1-V adapter; it never starts a server; it
reads no real queue DB, sends no POST, makes no network call, reads no secrets, writes no repo
file, and modifies no git index. It only imports the v0.8.3-B builder module (standard library
only) to call its public function and inspect the returned dict.
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

F_SCRIPT_REL = (
    "scripts/check_hermes_openclaw_worker_dry_run_preview_dashboard_display_"
    "validation_hardening_v0_8_3_f.py"
)
F_SCRIPT_PATH = REPO_ROOT / F_SCRIPT_REL

D_SCRIPT_REL = (
    "scripts/check_hermes_openclaw_worker_dry_run_preview_dashboard_read_only_"
    "display_implementation_v0_8_3_d.py"
)

E_DOC_REL = (
    "docs/HERMES_OPENCLAW_WORKER_DRY_RUN_PREVIEW_DASHBOARD_DISPLAY_CLOSEOUT_"
    "VALIDATION_HARDENING_PLAN_V0_8_3_E.md"
)
E_SCRIPT_REL = (
    "scripts/check_hermes_openclaw_worker_dry_run_preview_dashboard_display_"
    "closeout_validation_hardening_plan_v0_8_3_e.py"
)

C_DOC_REL = "docs/HERMES_OPENCLAW_WORKER_DRY_RUN_PREVIEW_DASHBOARD_READ_ONLY_DISPLAY_PLAN_V0_8_3_C.md"
C_SCRIPT_REL = "scripts/check_hermes_openclaw_worker_dry_run_preview_dashboard_read_only_display_plan_v0_8_3_c.py"

B_DOC_REL = "docs/HERMES_OPENCLAW_WORKER_DRY_RUN_PREVIEW_BOUNDARY_IMPLEMENTATION_V0_8_3_B.md"
B_FIXTURE_REL = "fixtures/local_mock_data/hermes_openclaw_worker_dry_run_preview_v0_8_3_b.json"
B_BUILDER_REL = "scripts/worker_dry_run_preview_boundary_v0_8_3_b.py"
B_BUILDER_PATH = REPO_ROOT / B_BUILDER_REL
B_SCRIPT_REL = "scripts/check_hermes_openclaw_worker_dry_run_preview_boundary_implementation_v0_8_3_b.py"

A_DOC_REL = "docs/HERMES_OPENCLAW_WORKER_DRY_RUN_PREVIEW_BOUNDARY_PLAN_V0_8_3_A.md"
A_SCRIPT_REL = "scripts/check_hermes_openclaw_worker_dry_run_preview_boundary_plan_v0_8_3_a.py"

F082_DOC_REL = "docs/HERMES_OPENCLAW_DASHBOARD_READ_ONLY_PREVIEW_VALIDATION_CLOSEOUT_HANDOFF_PLAN_V0_8_2_F.md"
F082_SCRIPT_REL = "scripts/check_hermes_openclaw_dashboard_read_only_preview_validation_closeout_handoff_plan_v0_8_2_f.py"

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

WXYZ_REL = {
    "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_runtime_check_v0_8_1_w.py",
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_DASHBOARD_PREVIEW_ADAPTER_INTEGRATION_BOUNDARY_PLAN_V0_8_1_X.md",
    "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_integration_boundary_plan_v0_8_1_x.py",
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_DASHBOARD_PREVIEW_ADAPTER_INTEGRATION_AUTHORIZATION_PLAN_V0_8_1_Y.md",
    "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_integration_authorization_plan_v0_8_1_y.py",
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_DASHBOARD_PREVIEW_ADAPTER_INTEGRATION_IMPLEMENTATION_PLAN_V0_8_1_Z.md",
    "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_integration_implementation_plan_v0_8_1_z.py",
}

# v0.8.3-E commit — the base this round starts from (current origin/master tip at round start).
EXPECTED_BASE_HEAD = "11e0093c7e056aaddd0650cdc6a9d7c7302c90da"

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
    "load_local_mock_fixture_preview(",
    "validate_local_mock_fixture_preview_object(",
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
    ("OpenClaw", " connected"),
    ("OpenClaw", " called"),
    ("Hermes", " connected"),
    ("Hermes", " called"),
    ("Google Sheets", " enabled"),
    ("real queue DB", " read"),
    ("queue write", " enabled"),
    ("POST", " enabled"),
    ("secrets", " read"),
    ("webhook", " created"),
    ("endpoint", " created"),
    ("connector", " created"),
    ("production DB", " created"),
    ("Remote Blackboard API runtime", " created"),
    ("v0.8.3-G", " started"),
    ("tag", " created"),
)
UNSAFE_DONE_CLAIMS = tuple(prefix + suffix for prefix, suffix in UNSAFE_DONE_CLAIM_PARTS)

# Deliberately specific (real call syntax, not bare module/attribute names) and built via
# concatenation so this tuple's own definition does not trip its own self-scan below. Note:
# "QueueStore(" is intentionally NOT included here — that literal is already used (correctly)
# in MAIN_FORBIDDEN_DISPLAY_PATH_PATTERNS below to scan app/main.py, and re-including it here
# would make this tuple's own definition self-trip against that other tuple's literal. Import-
# level QueueStore protection is instead covered by SELF_FORBIDDEN_IMPORT_PATTERN below.
SELF_FORBIDDEN_CALL_SUBSTRINGS = (
    "os.environ" + "[",
    "os.environ.get" + "(",
    "requests.get" + "(",
    "requests.post" + "(",
    "httpx.get" + "(",
    "httpx.post" + "(",
    "socket.socket" + "(",
    "urllib.request" + ".",
    "uvicorn.run" + "(",
    "app.run" + "(",
)

SELF_FORBIDDEN_IMPORT_PATTERN = re.compile(
    r"^\s*(import|from)\s+"
    r"(app(\.\w+)?|queue_store|QueueStore"
    r"|openclaw|hermes|google|sheets|requests|httpx|socket|urllib\.request|flask|uvicorn)\b",
    re.IGNORECASE,
)

# This script's own git wrapper (run_git / git_lines) must only ever be called with read-only
# git plumbing subcommands. Checked by parsing actual call sites below (find_git_subcommands),
# NOT by scanning for forbidden quoted literals like '"commit"' — a literal-scan approach would
# self-trip, since any Python string literal for a git subcommand name is necessarily written
# with quote characters around it in source, including in a "forbidden literals" list itself.
ALLOWED_GIT_SUBCOMMANDS = {"rev-parse", "status", "diff", "ls-files", "log", "merge-base", "tag"}

GIT_CALL_SITE_PATTERN = re.compile(r'(?:run_git|git_lines)\(\s*\[\s*"([a-zA-Z][a-zA-Z\-]*)"')

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
    rest = text[start + len(route_decorator_snippet) :]
    m = re.search(r"\n@app\.", rest)
    end = start + len(route_decorator_snippet) + m.start() if m else len(text)
    return text[start:end]


def detect_phase() -> str:
    f_tracked = is_tracked(F_SCRIPT_REL)
    if not f_tracked:
        return "owner_review"
    head = git_rev_parse("HEAD")
    origin = git_rev_parse("origin/master")
    if head != origin:
        return "post_commit_or_ahead"
    return "post_push_or_synced"


def find_forbidden_calls(source_text: str) -> list[str]:
    return [needle for needle in SELF_FORBIDDEN_CALL_SUBSTRINGS if needle in source_text]


def find_forbidden_imports(source_text: str) -> list[str]:
    found = []
    for line in source_text.splitlines():
        if SELF_FORBIDDEN_IMPORT_PATTERN.match(line):
            found.append(line.strip())
    return found


def find_git_subcommands(source_text: str) -> list[str]:
    return GIT_CALL_SITE_PATTERN.findall(source_text)


def load_b_builder():
    spec = importlib.util.spec_from_file_location("worker_dry_run_preview_boundary_v0_8_3_b", B_BUILDER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    main_text = read_text(REPO_ROOT / MAIN_PY_REL)
    system_text = read_text(REPO_ROOT / SYSTEM_HTML_REL)
    css_text = read_text(REPO_ROOT / DASHBOARD_CSS_REL)
    e_doc_text = read_text(REPO_ROOT / E_DOC_REL)
    self_text = read_text(F_SCRIPT_PATH)

    tracked_changed = working_tree_change_names()
    untracked = untracked_names()

    phase = detect_phase()
    print(f"INFO: detected phase = {phase}")

    # -----------------------------------------------------------------
    # [A] current HEAD contains EXPECTED_BASE_HEAD in git history
    # -----------------------------------------------------------------
    print("[A] current HEAD contains EXPECTED_BASE_HEAD in git history")
    is_ancestor = run_git(["merge-base", "--is-ancestor", EXPECTED_BASE_HEAD, "HEAD"]).returncode == 0
    check(f"A. HEAD contains {EXPECTED_BASE_HEAD} in git history", is_ancestor)

    # -----------------------------------------------------------------
    # [B] F script exists at expected path
    # -----------------------------------------------------------------
    print("[B] F script exists at expected path")
    check("B. F script exists at expected path", F_SCRIPT_PATH.is_file())

    # -----------------------------------------------------------------
    # [C] phase detection works
    # -----------------------------------------------------------------
    print("[C] phase detection works")
    check(
        f"C. F script phase detected: {phase}",
        phase in {"owner_review", "post_commit_or_ahead", "post_push_or_synced"},
    )

    # -----------------------------------------------------------------
    # [D] no tracked file is modified
    # -----------------------------------------------------------------
    print("[D] no tracked file is modified")
    check(
        f"D. no tracked file is modified（found {sorted(tracked_changed)}）"
        if tracked_changed
        else "D. no tracked file is modified",
        not tracked_changed,
    )

    # -----------------------------------------------------------------
    # [E] allowed untracked files by phase: F script (owner_review only), patches/*
    # -----------------------------------------------------------------
    print("[E] allowed untracked files only: F script (if Owner Review phase), patches/*")
    allowed_untracked = {F_SCRIPT_REL} if phase == "owner_review" else set()
    unexpected_untracked = {
        p for p in untracked if p not in allowed_untracked and not p.startswith("patches/")
    }
    check(
        f"E. no unexpected untracked files（found {sorted(unexpected_untracked)}）"
        if unexpected_untracked
        else "E. no unexpected untracked files",
        not unexpected_untracked,
    )

    # -----------------------------------------------------------------
    # [F]-[W] protected tracked files are not modified
    # -----------------------------------------------------------------
    def not_modified(*rels: str) -> bool:
        return all(rel not in tracked_changed for rel in rels)

    print("[F] app/main.py is not modified")
    check("F. app/main.py is not modified", not_modified(MAIN_PY_REL))

    print("[G] templates/system.html is not modified")
    check("G. templates/system.html is not modified", not_modified(SYSTEM_HTML_REL))

    print("[H] static/dashboard.css is not modified")
    check("H. static/dashboard.css is not modified", not_modified(DASHBOARD_CSS_REL))

    print("[I] v0.8.3-D validation script is not modified")
    check("I. v0.8.3-D validation script is not modified", not_modified(D_SCRIPT_REL))

    print("[J] v0.8.3-E plan doc / readiness script are not modified")
    check(
        "J. v0.8.3-E plan doc / readiness script are not modified",
        not_modified(E_DOC_REL, E_SCRIPT_REL),
    )

    print("[K] v0.8.3-C plan doc/readiness are not modified")
    check("K. v0.8.3-C plan doc/readiness are not modified", not_modified(C_DOC_REL, C_SCRIPT_REL))

    print("[L] v0.8.3-B implementation doc / fixture / builder / readiness are not modified")
    check(
        "L. v0.8.3-B implementation doc / fixture / builder / readiness are not modified",
        not_modified(B_DOC_REL, B_FIXTURE_REL, B_BUILDER_REL, B_SCRIPT_REL),
    )

    print("[M] v0.8.3-A plan/readiness are not modified")
    check("M. v0.8.3-A plan/readiness are not modified", not_modified(A_DOC_REL, A_SCRIPT_REL))

    print("[N] F v0.8.2 closeout doc/readiness are not modified")
    check(
        "N. F v0.8.2 closeout doc/readiness are not modified",
        not_modified(F082_DOC_REL, F082_SCRIPT_REL),
    )

    print("[O] E v0.8.2 validation script is not modified")
    check("O. E v0.8.2 validation script is not modified", not_modified(E082_SCRIPT_REL))

    print("[P] D v0.8.2 plan/readiness are not modified")
    check("P. D v0.8.2 plan/readiness are not modified", not_modified(D082_DOC_REL, D082_SCRIPT_REL))

    print("[Q] C v0.8.2 validation script is not modified")
    check("Q. C v0.8.2 validation script is not modified", not_modified(C082_SCRIPT_REL))

    print("[R] B v0.8.2 doc/readiness are not modified")
    check("R. B v0.8.2 doc/readiness are not modified", not_modified(B082_DOC_REL, B082_SCRIPT_REL))

    print("[S] v0.8.2-A validation script is not modified")
    check("S. v0.8.2-A validation script is not modified", not_modified(A082_SCRIPT_REL))

    print("[T] P loader is not modified")
    check("T. P loader is not modified", not_modified(P_LOADER_REL))

    print("[U] V adapter is not modified")
    check("U. V adapter is not modified", not_modified(V_ADAPTER_REL))

    print("[V] old v0.8.1 fixture JSON is not modified")
    check("V. old v0.8.1 fixture JSON is not modified", not_modified(OLD_FIXTURE_JSON_REL))

    print("[W] W/X/Y/Z artifacts are not modified")
    check("W. W/X/Y/Z artifacts are not modified", not_modified(*WXYZ_REL))

    # -----------------------------------------------------------------
    # Dashboard route / app checks — read committed app/main.py content directly
    # -----------------------------------------------------------------
    route_block = extract_route_block(main_text, '@app.get("/dashboard/system"')
    loader_block = extract_block(
        main_text,
        "_V0_8_3_D_BUILDER_PATH = (",
        "build_worker_dry_run_preview_model = _load_v0_8_3_d_build_worker_dry_run_preview_model()",
    )
    # Narrow, worker-dry-run-preview-specific slice of the route body only (the wiring comment
    # + the build_worker_dry_run_preview_model() call), NOT the whole route function. The route
    # also contains pre-existing, unrelated lines (e.g. `Path(QUEUE_DB_PATH).exists()` for the
    # db_exists status display) that legitimately contain forbidden-looking substrings; scanning
    # the full function body would falsely flag those. This mirrors the v0.8.3-D readiness
    # script's principle of never letting pre-existing unrelated code trip this check.
    route_wiring_block = extract_block(
        route_block, "# v0.8.3-D：唯讀", "build_worker_dry_run_preview_model()"
    )
    display_path_text = loader_block + "\n" + route_wiring_block

    print('[X] app/main.py contains existing GET-only route for "/dashboard/system"')
    check(
        'X. app/main.py contains existing GET-only route for "/dashboard/system"',
        bool(re.search(r'@app\.get\(\s*["\']\/dashboard\/system["\']', main_text)),
    )

    print('[Y] app/main.py does not contain a POST/PUT/DELETE/PATCH route for "/dashboard/system"')
    check(
        'Y. app/main.py does not contain a POST/PUT/DELETE/PATCH route for "/dashboard/system"',
        not re.search(r'@app\.(post|put|delete|patch)\(\s*["\']\/dashboard\/system["\']', main_text, re.IGNORECASE),
    )

    print("[Z] app/main.py references build_worker_dry_run_preview_model")
    check(
        "Z. app/main.py references build_worker_dry_run_preview_model",
        "build_worker_dry_run_preview_model" in main_text,
    )

    print("[AA] app/main.py passes worker_dry_run_preview into system.html template context")
    check(
        "AA. app/main.py passes worker_dry_run_preview into system.html template context",
        '"worker_dry_run_preview": worker_dry_run_preview' in main_text,
    )

    print("[AB] app/main.py does not directly read the v0.8.3-B fixture JSON filename")
    check(
        "AB. app/main.py does not directly read the v0.8.3-B fixture JSON filename",
        "hermes_openclaw_worker_dry_run_preview_v0_8_3_b.json" not in main_text,
    )

    print("[AC] worker dry-run display path (route + loader) has no forbidden queue/worker/openclaw/hermes/sheets identifiers")
    forbidden_ac = [
        p
        for p in (
            "QueueStore(",
            "QUEUE_DB_PATH",
            "run_openclaw_cli(",
            "subprocess.",
            "GOOGLE_SHEETS_ENABLED",
            "google_sheets",
            "hermes_endpoint",
            "openclaw_endpoint",
        )
        if p in display_path_text
    ]
    check(
        f"AC. worker dry-run display path has no forbidden queue/worker/openclaw/hermes/sheets identifiers（found {forbidden_ac}）"
        if forbidden_ac
        else "AC. worker dry-run display path has no forbidden queue/worker/openclaw/hermes/sheets identifiers",
        not forbidden_ac,
    )

    print("[AD] worker dry-run display path does not call load_local_mock_fixture_preview()")
    check(
        "AD. worker dry-run display path does not call load_local_mock_fixture_preview()",
        "load_local_mock_fixture_preview(" not in display_path_text,
    )

    print("[AE] worker dry-run display path does not call validate_local_mock_fixture_preview_object()")
    check(
        "AE. worker dry-run display path does not call validate_local_mock_fixture_preview_object()",
        "validate_local_mock_fixture_preview_object(" not in display_path_text,
    )

    print("[AF] worker dry-run display path contains no POST/webhook/connector/dispatch/execute/send control additions")
    forbidden_af = [p for p in MAIN_FORBIDDEN_DISPLAY_PATH_PATTERNS if p in display_path_text]
    check(
        f"AF. worker dry-run display path contains no POST/webhook/connector/dispatch/execute/send control additions（found {forbidden_af}）"
        if forbidden_af
        else "AF. worker dry-run display path contains no POST/webhook/connector/dispatch/execute/send control additions",
        not forbidden_af,
    )

    # -----------------------------------------------------------------
    # Template checks — read committed templates/system.html content directly
    # -----------------------------------------------------------------
    worker_section = extract_block(system_text, '<section id="worker-dry-run-preview"', "</section>")

    print("[AG] templates/system.html contains worker-dry-run-preview")
    check("AG. templates/system.html contains worker-dry-run-preview", "worker-dry-run-preview" in worker_section)

    print("[AH] templates/system.html contains worker_dry_run_preview")
    check("AH. templates/system.html contains worker_dry_run_preview", "worker_dry_run_preview" in worker_section)

    print('[AI] templates/system.html contains visible text "Synthetic local-only"')
    check(
        'AI. templates/system.html contains visible text "Synthetic local-only"',
        "Synthetic local-only" in worker_section,
    )

    print('[AJ] templates/system.html contains visible text "Preview only"')
    check('AJ. templates/system.html contains visible text "Preview only"', "Preview only" in worker_section)

    print('[AK] templates/system.html contains visible text "Owner Review required"')
    check(
        'AK. templates/system.html contains visible text "Owner Review required"',
        "Owner Review required" in worker_section,
    )

    print("[AL] templates/system.html contains all required display field labels")
    missing_labels = [label for label in REQUIRED_DISPLAY_LABELS if label not in worker_section]
    check(
        f"AL. templates/system.html contains all required display field labels（missing {missing_labels}）"
        if missing_labels
        else "AL. templates/system.html contains all required display field labels",
        not missing_labels,
    )

    print("[AM] templates/system.html contains all required permission flag keys")
    missing_perm = [key for key in REQUIRED_PERMISSION_KEYS if key not in worker_section]
    check(
        f"AM. templates/system.html contains all required permission flag keys（missing {missing_perm}）"
        if missing_perm
        else "AM. templates/system.html contains all required permission flag keys",
        not missing_perm,
    )

    print("[AN] templates/system.html contains all required runtime flag keys")
    missing_runtime = [key for key in REQUIRED_RUNTIME_KEYS if key not in worker_section]
    check(
        f"AN. templates/system.html contains all required runtime flag keys（missing {missing_runtime}）"
        if missing_runtime
        else "AN. templates/system.html contains all required runtime flag keys",
        not missing_runtime,
    )

    print("[AO] worker-dry-run-preview section contains no <button")
    check("AO. worker-dry-run-preview section contains no <button", "<button" not in worker_section)

    print("[AP] worker-dry-run-preview section contains no <form")
    check("AP. worker-dry-run-preview section contains no <form", "<form" not in worker_section)

    print("[AQ] worker-dry-run-preview section contains no action=")
    check(
        "AQ. worker-dry-run-preview section contains no action=",
        'action="' not in worker_section and "action='" not in worker_section,
    )

    print("[AR] worker-dry-run-preview section contains no method=")
    check(
        "AR. worker-dry-run-preview section contains no method=",
        'method="' not in worker_section and "method='" not in worker_section,
    )

    print("[AS] worker-dry-run-preview section contains no onclick")
    check("AS. worker-dry-run-preview section contains no onclick", "onclick" not in worker_section)

    print("[AT] worker-dry-run-preview section contains no forbidden control URL keys")
    forbidden_urls = [
        p
        for p in ("action_url", "post_url", "webhook_url", "endpoint_url", "execute_url", "dispatch_url", "send_url")
        if p in worker_section
    ]
    check(
        f"AT. worker-dry-run-preview section contains no forbidden control URL keys（found {forbidden_urls}）"
        if forbidden_urls
        else "AT. worker-dry-run-preview section contains no forbidden control URL keys",
        not forbidden_urls,
    )

    # -----------------------------------------------------------------
    # CSS checks — read committed static/dashboard.css content directly
    # -----------------------------------------------------------------
    css_block = extract_block(
        css_text, "/* v0.8.3-D: read-only worker dry-run preview display", "\0\0\0__unused_end_marker__\0\0\0"
    )

    print("[AU] static/dashboard.css contains worker-dry-run-preview styling")
    check("AU. static/dashboard.css contains worker-dry-run-preview styling", ".worker-dry-run-preview" in css_block)

    print("[AV] worker-dry-run-preview CSS block does not contain cursor: pointer")
    check(
        "AV. worker-dry-run-preview CSS block does not contain cursor: pointer",
        "cursor: pointer" not in css_block and "cursor:pointer" not in css_block,
    )

    print("[AW] worker-dry-run-preview CSS block does not contain execute / dispatch / send / onclick control styling")
    forbidden_css = [p for p in CSS_FORBIDDEN_PATTERNS if p in css_block]
    check(
        f"AW. worker-dry-run-preview CSS block does not contain execute / dispatch / send / onclick control styling（found {forbidden_css}）"
        if forbidden_css
        else "AW. worker-dry-run-preview CSS block does not contain execute / dispatch / send / onclick control styling",
        not forbidden_css,
    )

    print("[AX] static/dashboard.css does not create hidden interactive affordance for worker-dry-run-preview")
    check(
        "AX. static/dashboard.css does not create hidden interactive affordance for worker-dry-run-preview",
        "pointer-events" not in css_block and "display: none" not in css_block and "display:none" not in css_block,
    )

    # -----------------------------------------------------------------
    # B builder checks — re-run the standalone v0.8.3-B builder (read-only reference)
    # -----------------------------------------------------------------
    b_module = load_b_builder()
    model = b_module.build_worker_dry_run_preview_model()
    permissions = model.get("permissions", {})
    runtime_state = model.get("runtime_state", {})

    print("[AY] B builder local preview returns source == synthetic_local_only")
    check("AY. B builder local preview returns source == synthetic_local_only", model.get("source") == "synthetic_local_only")

    print("[AZ] B builder local preview returns dry_run_status == preview_only_not_executed")
    check(
        "AZ. B builder local preview returns dry_run_status == preview_only_not_executed",
        model.get("dry_run_status") == "preview_only_not_executed",
    )

    print("[BA] B builder local preview returns owner_review_required == true")
    check("BA. B builder local preview returns owner_review_required == true", model.get("owner_review_required") is True)

    print("[BB] B builder local preview permissions are all false")
    check(
        "BB. B builder local preview permissions are all false",
        isinstance(permissions, dict) and all(permissions.get(key) is False for key in REQUIRED_PERMISSION_KEYS),
    )

    print("[BC] B builder local preview runtime_state flags are all false")
    check(
        "BC. B builder local preview runtime_state flags are all false",
        isinstance(runtime_state, dict) and all(runtime_state.get(key) is False for key in REQUIRED_RUNTIME_KEYS),
    )

    # -----------------------------------------------------------------
    # D validation limitation / E plan checks — read committed E plan doc directly
    # -----------------------------------------------------------------
    print("[BD] E plan doc explains the v0.8.3-D readiness post-push observation (36/52)")
    check("BD. E plan doc explains the v0.8.3-D readiness post-push observation (36/52)", "36/52" in e_doc_text)

    print("[BE] E plan doc explains git diff --unified=0")
    check("BE. E plan doc explains git diff --unified=0", "git diff --unified=0" in e_doc_text)

    print("[BF] E plan doc explains the added-lines limitation")
    check(
        "BF. E plan doc explains the added-lines limitation",
        "added-lines" in e_doc_text or "added lines" in e_doc_text,
    )

    print("[BG] E plan doc states this is not a Dashboard content failure")
    check(
        "BG. E plan doc states this is not a Dashboard content failure",
        "not a Dashboard content failure" in e_doc_text,
    )

    print("[BH] E plan doc states this is not a safety-boundary failure")
    check(
        "BH. E plan doc states this is not a safety-boundary failure",
        "not a safety-boundary failure" in e_doc_text,
    )

    print("[BI] E plan doc says future validator should avoid depending on uncommitted diff")
    check(
        "BI. E plan doc says future validator should avoid depending on uncommitted diff",
        "uncommitted diff" in e_doc_text,
    )

    # -----------------------------------------------------------------
    # Safety negative checks
    # -----------------------------------------------------------------
    print("[BJ] combined app/template/css/F-script contains no unsafe done-claims")
    combined_text = main_text + "\n" + system_text + "\n" + css_text + "\n" + self_text
    found_unsafe = [c for c in UNSAFE_DONE_CLAIMS if c in combined_text]
    check(
        f"BJ. combined app/template/css/F-script contains no unsafe done-claims（found {found_unsafe}）"
        if found_unsafe
        else "BJ. combined app/template/css/F-script contains no unsafe done-claims",
        not found_unsafe,
    )

    print("[BK] F script itself contains no forbidden imports / runtime calls")
    self_forbidden_imports = find_forbidden_imports(self_text)
    self_forbidden_calls = find_forbidden_calls(self_text)
    self_git_subcommands = find_git_subcommands(self_text)
    self_disallowed_git_subcommands = [s for s in self_git_subcommands if s not in ALLOWED_GIT_SUBCOMMANDS]
    check(
        f"BK. F script itself contains no forbidden imports / runtime calls"
        f"（imports {self_forbidden_imports}, calls {self_forbidden_calls},"
        f" disallowed_git_subcommands {self_disallowed_git_subcommands}）"
        if (self_forbidden_imports or self_forbidden_calls or self_disallowed_git_subcommands)
        else "BK. F script itself contains no forbidden imports / runtime calls",
        not self_forbidden_imports and not self_forbidden_calls and not self_disallowed_git_subcommands,
    )

    print("[BL] patches/ remains untracked and untouched")
    patches_tracked = git_lines(["ls-files", "--", "patches/"])
    check(
        f"BL. patches/ remains untracked and untouched（found tracked {patches_tracked}）"
        if patches_tracked
        else "BL. patches/ remains untracked and untouched",
        not patches_tracked,
    )

    print("[BM] Bridgiron is not referenced in Dashboard / app / CSS artifacts")
    bridgiron_hits = [
        name
        for name, text in (
            ("app/main.py", main_text),
            ("templates/system.html", system_text),
            ("static/dashboard.css", css_text),
        )
        if "bridgiron" in text.lower()
    ]
    check(
        f"BM. Bridgiron is not referenced in Dashboard / app / CSS artifacts（found in {bridgiron_hits}）"
        if bridgiron_hits
        else "BM. Bridgiron is not referenced in Dashboard / app / CSS artifacts",
        not bridgiron_hits,
    )

    # -----------------------------------------------------------------
    # 結果
    # -----------------------------------------------------------------
    total = len(PASS) + len(FAIL)
    print(f"\n合計：{len(PASS)}/{total} 通過")
    if FAIL:
        print(f"\nXX v0.8.3-F readiness 失敗 {len(FAIL)} 項：")
        for f in FAIL:
            print(f"   - {f}")
        sys.exit(1)
    else:
        print("PASS: v0.8.3-F worker dry-run preview dashboard display validation hardening")
        sys.exit(0)


if __name__ == "__main__":
    main()
