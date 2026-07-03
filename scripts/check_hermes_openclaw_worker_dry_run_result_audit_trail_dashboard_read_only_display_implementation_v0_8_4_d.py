"""v0.8.4-D readiness check: Worker Dry-run Result / Audit Trail Dashboard Read-only Display
Implementation.

Pure local filesystem + git metadata validation. Reads the working-tree contents of
`app/main.py`, `templates/system.html`, and `static/dashboard.css` directly and checks for the
required v0.8.4-B wiring and the absence of forbidden route/control patterns in the newly added
`worker-dry-run-result-audit-trail` display block. It also re-runs the v0.8.4-B standalone
builder (read-only reference check) to confirm its returned model stays synthetic local-only /
preview-only / all flags false, and re-runs the v0.8.4-C readiness script, the v0.8.3-F
validator, and the v0.8.3-B builder as regression observations.

It does NOT import app runtime, Dashboard runtime, QueueStore, Worker/OpenClaw/Hermes/Google
Sheets integration; it never starts a server; it reads no real queue DB, sends no POST, makes no
network call, reads no secrets, writes no repo file, and modifies no git index. It only imports
the v0.8.4-B builder module (standard library only) to call its public function and inspect the
returned dict, and invokes other readiness/builder scripts as read-only subprocesses.
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

D_SCRIPT_REL = (
    "scripts/check_hermes_openclaw_worker_dry_run_result_audit_trail_dashboard_read_only_"
    "display_implementation_v0_8_4_d.py"
)
D_SCRIPT_PATH = REPO_ROOT / D_SCRIPT_REL

C_SCRIPT_REL = (
    "scripts/check_hermes_openclaw_worker_dry_run_result_audit_trail_dashboard_read_only_"
    "display_plan_v0_8_4_c.py"
)
C_SCRIPT_PATH = REPO_ROOT / C_SCRIPT_REL

B_BUILDER_REL = "scripts/worker_dry_run_result_audit_trail_boundary_v0_8_4_b.py"
B_BUILDER_PATH = REPO_ROOT / B_BUILDER_REL
B_FIXTURE_REL = "fixtures/local_mock_data/hermes_openclaw_worker_dry_run_result_audit_trail_v0_8_4_b.json"

F_SCRIPT_REL = (
    "scripts/check_hermes_openclaw_worker_dry_run_preview_dashboard_display_"
    "validation_hardening_v0_8_3_f.py"
)
F_SCRIPT_PATH = REPO_ROOT / F_SCRIPT_REL

B083_BUILDER_REL = "scripts/worker_dry_run_preview_boundary_v0_8_3_b.py"
B083_BUILDER_PATH = REPO_ROOT / B083_BUILDER_REL

# v0.8.4-C commit — the base this round starts from (origin/master tip at round start).
EXPECTED_BASE_HEAD = "71caedfeaadfe8e123e30bc9327e940ce0904122"

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

REQUIRED_MODEL_REFERENCES = (
    "dry_run_result",
    "audit_trail_record",
    "owner_review_event",
    "readback_summary",
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
    ("queue write", " enabled"),
    ("POST", " enabled"),
    ("secrets", " read"),
    ("webhook", " created"),
    ("endpoint", " created"),
    ("connector", " created"),
    ("production DB", " created"),
    ("Remote Blackboard API runtime", " created"),
    ("v0.8.4-E", " started"),
    ("tag", " created"),
)
UNSAFE_DONE_CLAIMS = tuple(prefix + suffix for prefix, suffix in UNSAFE_DONE_CLAIM_PARTS)

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

ALLOWED_GIT_SUBCOMMANDS = {"rev-parse", "status", "diff", "ls-files", "log", "merge-base", "tag"}
GIT_CALL_SITE_PATTERN = re.compile(r'(?:run_git|git_lines)\(\s*\[\s*"([a-zA-Z][a-zA-Z\-]*)"')

# Substrings that make an Owner-Review-phase FAIL line from an *older* readiness/validator script
# acceptable: it must be about the three files this round legitimately touches, about this
# script's own untracked presence, or a generic "untracked"/"modified" observation phrase.
ACCEPTABLE_OWNER_REVIEW_SUBSTRINGS = (
    "app/main.py",
    "templates/system.html",
    "static/dashboard.css",
    "v0.8.4-D",
    D_SCRIPT_REL,
    "worker_dry_run_result_audit_trail",
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
    d_tracked = is_tracked(D_SCRIPT_REL)
    if not d_tracked:
        return "owner_review"
    head = git_rev_parse("HEAD")
    origin = git_rev_parse("origin/master")
    if head != origin:
        return "post_commit_or_ahead"
    return "post_push_or_synced"


def find_forbidden_calls(source_text: str) -> list[str]:
    return [needle for needle in SELF_FORBIDDEN_CALL_SUBSTRINGS if needle in source_text]


def find_forbidden_imports(source_text: str) -> list[str]:
    return [line.strip() for line in source_text.splitlines() if SELF_FORBIDDEN_IMPORT_PATTERN.match(line)]


def find_git_subcommands(source_text: str) -> list[str]:
    return GIT_CALL_SITE_PATTERN.findall(source_text)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_subprocess_script(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(path)], cwd=str(REPO_ROOT), capture_output=True, text=True)


def fail_lines_of(stdout: str) -> list[str]:
    return [line.strip(" -") for line in stdout.splitlines() if line.strip().startswith("- ")]


def only_acceptable_owner_review_fails(stdout: str) -> bool:
    lines = fail_lines_of(stdout)
    if not lines:
        return True
    return all(any(sub in line for sub in ACCEPTABLE_OWNER_REVIEW_SUBSTRINGS) for line in lines)


def main() -> None:
    main_text = read_text(REPO_ROOT / MAIN_PY_REL)
    system_text = read_text(REPO_ROOT / SYSTEM_HTML_REL)
    css_text = read_text(REPO_ROOT / DASHBOARD_CSS_REL)
    self_text = read_text(D_SCRIPT_PATH)

    tracked_changed = working_tree_change_names()
    untracked = untracked_names()

    phase = detect_phase()
    print(f"INFO: detected phase = {phase}")

    # -----------------------------------------------------------------
    print("[A] current HEAD contains EXPECTED_BASE_HEAD in git history")
    is_ancestor = run_git(["merge-base", "--is-ancestor", EXPECTED_BASE_HEAD, "HEAD"]).returncode == 0
    check(f"A. HEAD contains {EXPECTED_BASE_HEAD} in git history", is_ancestor)

    # -----------------------------------------------------------------
    print("[B] app/main.py is modified in Owner Review phase")
    b_cond = (MAIN_PY_REL in tracked_changed) if phase == "owner_review" else is_tracked(MAIN_PY_REL)
    check("B. app/main.py is modified in Owner Review phase", b_cond)

    print("[C] templates/system.html is modified in Owner Review phase")
    c_cond = (SYSTEM_HTML_REL in tracked_changed) if phase == "owner_review" else is_tracked(SYSTEM_HTML_REL)
    check("C. templates/system.html is modified in Owner Review phase", c_cond)

    print("[D] static/dashboard.css is modified in Owner Review phase")
    d_cond = (DASHBOARD_CSS_REL in tracked_changed) if phase == "owner_review" else is_tracked(DASHBOARD_CSS_REL)
    check("D. static/dashboard.css is modified in Owner Review phase", d_cond)

    # -----------------------------------------------------------------
    print("[E] v0.8.4-D validation script exists and is untracked")
    e_cond = D_SCRIPT_PATH.is_file() and (phase != "owner_review" or D_SCRIPT_REL in untracked)
    check("E. v0.8.4-D validation script exists and is untracked", e_cond)

    print("[F] no other tracked files modified")
    other_modified = tracked_changed - {MAIN_PY_REL, SYSTEM_HTML_REL, DASHBOARD_CSS_REL}
    check(
        f"F. no other tracked files modified（found {sorted(other_modified)}）"
        if other_modified else "F. no other tracked files modified",
        not other_modified,
    )

    print("[G] untracked only v0.8.4-D validation script and patches/*")
    allowed_untracked = {D_SCRIPT_REL} if phase == "owner_review" else set()
    unexpected_untracked = {p for p in untracked if p not in allowed_untracked and not p.startswith("patches/")}
    check(
        f"G. no unexpected untracked files（found {sorted(unexpected_untracked)}）"
        if unexpected_untracked else "G. no unexpected untracked files",
        not unexpected_untracked,
    )

    # -----------------------------------------------------------------
    # Route checks
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

    print('[H] app/main.py still has existing /dashboard/system route')
    check(
        'H. app/main.py still has existing /dashboard/system route',
        bool(re.search(r'@app\.get\(\s*["\']\/dashboard\/system["\']', main_text)),
    )

    print("[I] /dashboard/system route remains GET-only")
    get_route_count = len(re.findall(r'@app\.get\(\s*["\']\/dashboard\/system["\']', main_text))
    check("I. /dashboard/system route remains GET-only", get_route_count == 1)

    print('[J] no POST/PUT/PATCH/DELETE route variant for "/dashboard/system"')
    check(
        'J. no POST/PUT/PATCH/DELETE route variant for "/dashboard/system"',
        not re.search(r'@app\.(post|put|delete|patch)\(\s*["\']\/dashboard\/system["\']', main_text, re.IGNORECASE),
    )

    print("[K] app/main.py references v0.8.4-B builder script by file-path import")
    check(
        "K. app/main.py references v0.8.4-B builder script by file-path import",
        "worker_dry_run_result_audit_trail_boundary_v0_8_4_b.py" in main_text
        and "spec_from_file_location" in loader_block,
    )

    print("[L] app/main.py calls build_worker_dry_run_result_audit_trail_model")
    check(
        "L. app/main.py calls build_worker_dry_run_result_audit_trail_model",
        "build_worker_dry_run_result_audit_trail_model()" in route_wiring_block,
    )

    print("[M] app/main.py passes worker_dry_run_result_audit_trail to template context")
    check(
        "M. app/main.py passes worker_dry_run_result_audit_trail to template context",
        '"worker_dry_run_result_audit_trail": worker_dry_run_result_audit_trail' in main_text,
    )

    print("[N] app/main.py does not directly read v0.8.4-B fixture JSON filename in route")
    check(
        "N. app/main.py does not directly read v0.8.4-B fixture JSON filename in route",
        "hermes_openclaw_worker_dry_run_result_audit_trail_v0_8_4_b.json" not in main_text,
    )

    print("[O] app/main.py does not import QueueStore / OpenClaw / Hermes / Google Sheets in display path")
    forbidden_o = [
        p for p in ("QueueStore(", "QUEUE_DB_PATH", "run_openclaw_cli(", "GOOGLE_SHEETS_ENABLED", "google_sheets", "hermes_endpoint", "openclaw_endpoint")
        if p in display_path_text
    ]
    check(
        f"O. app/main.py does not import QueueStore / OpenClaw / Hermes / Google Sheets in display path（found {forbidden_o}）"
        if forbidden_o else "O. app/main.py does not import QueueStore / OpenClaw / Hermes / Google Sheets in display path",
        not forbidden_o,
    )

    print("[P] app/main.py has no subprocess / requests / urllib / os.environ use in the route path")
    forbidden_p = [p for p in MAIN_FORBIDDEN_DISPLAY_PATH_PATTERNS if p in display_path_text]
    check(
        f"P. app/main.py has no subprocess / requests / urllib / os.environ use in the route path（found {forbidden_p}）"
        if forbidden_p else "P. app/main.py has no subprocess / requests / urllib / os.environ use in the route path",
        not forbidden_p,
    )

    # -----------------------------------------------------------------
    # Template checks
    # -----------------------------------------------------------------
    section = extract_block(system_text, '<section id="worker-dry-run-result-audit-trail"', "</section>")

    print("[Q] templates/system.html contains worker-dry-run-result-audit-trail section")
    check("Q. templates/system.html contains worker-dry-run-result-audit-trail section", bool(section))

    print("[R] template contains dry_run_result / audit_trail_record / owner_review_event / readback_summary references")
    missing_refs = [ref for ref in REQUIRED_MODEL_REFERENCES if ref not in section]
    check(
        f"R. template contains dry_run_result / audit_trail_record / owner_review_event / readback_summary references（missing {missing_refs}）"
        if missing_refs else "R. template contains dry_run_result / audit_trail_record / owner_review_event / readback_summary references",
        not missing_refs,
    )

    print("[S] template contains all required display labels")
    missing_labels = [label for label in REQUIRED_DISPLAY_LABELS if label not in section]
    check(
        f"S. template contains all required display labels（missing {missing_labels}）"
        if missing_labels else "S. template contains all required display labels",
        not missing_labels,
    )

    print("[T] template contains no form/button/action/method/onclick/control URLs in the new section")
    forbidden_t = [p for p in TEMPLATE_FORBIDDEN_PATTERNS if p in section]
    check(
        f"T. template contains no form/button/action/method/onclick/control URLs in the new section（found {forbidden_t}）"
        if forbidden_t else "T. template contains no form/button/action/method/onclick/control URLs in the new section",
        not forbidden_t,
    )

    print("[U] template displays permission flags")
    missing_perm = [key for key in REQUIRED_PERMISSION_KEYS if key not in section]
    check(
        f"U. template displays permission flags（missing {missing_perm}）"
        if missing_perm else "U. template displays permission flags",
        not missing_perm,
    )

    print("[V] template displays runtime flags")
    missing_runtime = [key for key in REQUIRED_RUNTIME_KEYS if key not in section]
    check(
        f"V. template displays runtime flags（missing {missing_runtime}）"
        if missing_runtime else "V. template displays runtime flags",
        not missing_runtime,
    )

    # -----------------------------------------------------------------
    # CSS checks
    # -----------------------------------------------------------------
    css_block = extract_block(
        css_text, "/* v0.8.4-D: read-only worker dry-run result / audit trail display", "\0\0\0__unused_end_marker__\0\0\0"
    )

    print("[W] CSS contains v0.8.4-D display classes")
    missing_css = [c for c in REQUIRED_CSS_CLASSES if c not in css_block]
    check(
        f"W. CSS contains v0.8.4-D display classes（missing {missing_css}）"
        if missing_css else "W. CSS contains v0.8.4-D display classes",
        not missing_css,
    )

    print("[X] CSS has no cursor:pointer or interactive affordance for these classes")
    forbidden_css = [p for p in CSS_FORBIDDEN_PATTERNS if p in css_block]
    interactive = "pointer-events" in css_block or "display: none" in css_block or "display:none" in css_block
    check(
        f"X. CSS has no cursor:pointer or interactive affordance for these classes（found {forbidden_css}, interactive={interactive}）"
        if (forbidden_css or interactive) else "X. CSS has no cursor:pointer or interactive affordance for these classes",
        not forbidden_css and not interactive,
    )

    # -----------------------------------------------------------------
    # v0.8.4-B builder checks (read-only reference)
    # -----------------------------------------------------------------
    b_module = load_module("worker_dry_run_result_audit_trail_boundary_v0_8_4_b", B_BUILDER_PATH)
    model = b_module.build_worker_dry_run_result_audit_trail_model()
    permissions = model.get("permissions", {})
    runtime_state = model.get("runtime_state", {})

    print("[Y] v0.8.4-B builder output remains safe")
    y_cond = (
        model.get("source") == "synthetic_local_only"
        and model.get("preview_only") is True
        and model.get("dry_run_result", {}).get("result_status") == "preview_result_not_executed"
        and model.get("audit_trail_record", {}).get("audit_status") == "preview_audit_not_persisted"
        and model.get("owner_review_event", {}).get("review_status") == "owner_review_required"
        and model.get("readback_summary", {}).get("summary_status") == "preview_readback_only"
    )
    check("Y. v0.8.4-B builder output remains safe", y_cond)

    print("[Z] all v0.8.4-B permission flags false")
    check(
        "Z. all v0.8.4-B permission flags false",
        isinstance(permissions, dict) and all(permissions.get(key) is False for key in REQUIRED_PERMISSION_KEYS),
    )

    print("[AA] all v0.8.4-B runtime flags false")
    check(
        "AA. all v0.8.4-B runtime flags false",
        isinstance(runtime_state, dict) and all(runtime_state.get(key) is False for key in REQUIRED_RUNTIME_KEYS),
    )

    # -----------------------------------------------------------------
    # Regression observations (other scripts, run read-only as subprocesses)
    # -----------------------------------------------------------------
    print("[AB] v0.8.4-C readiness PASS or only acceptable Owner Review modified/untracked observation")
    c_result = run_subprocess_script(C_SCRIPT_PATH)
    ab_cond = c_result.returncode == 0 or only_acceptable_owner_review_fails(c_result.stdout)
    check(
        f"AB. v0.8.4-C readiness PASS or only acceptable Owner Review modified/untracked observation（rc={c_result.returncode}）"
        if not ab_cond else "AB. v0.8.4-C readiness PASS or only acceptable Owner Review modified/untracked observation",
        ab_cond,
    )

    print("[AC] v0.8.3-F validator PASS or only acceptable Owner Review modified/untracked observation")
    f_result = run_subprocess_script(F_SCRIPT_PATH)
    ac_cond = f_result.returncode == 0 or only_acceptable_owner_review_fails(f_result.stdout)
    check(
        f"AC. v0.8.3-F validator PASS or only acceptable Owner Review modified/untracked observation（rc={f_result.returncode}）"
        if not ac_cond else "AC. v0.8.3-F validator PASS or only acceptable Owner Review modified/untracked observation",
        ac_cond,
    )

    print("[AD] v0.8.3-B builder still all permission/runtime flags false")
    b083_module = load_module("worker_dry_run_preview_boundary_v0_8_3_b", B083_BUILDER_PATH)
    b083_model = b083_module.build_worker_dry_run_preview_model()
    b083_permissions = b083_model.get("permissions", {})
    b083_runtime = b083_model.get("runtime_state", {})
    ad_perm_keys = ("execution_permission", "dispatch_permission", "external_side_effects_permission")
    ad_runtime_keys = (
        "worker_started", "worker_loop_started", "openclaw_called", "hermes_called",
        "google_sheets_enabled", "real_queue_db_read", "queue_written", "post_enabled",
        "secrets_read", "webhook_created", "endpoint_created", "connector_created",
        "production_db_created", "remote_blackboard_api_runtime_created",
    )
    check(
        "AD. v0.8.3-B builder still all permission/runtime flags false",
        all(b083_permissions.get(k) is False for k in ad_perm_keys)
        and all(b083_runtime.get(k) is False for k in ad_runtime_keys),
    )

    # -----------------------------------------------------------------
    # Safety negative checks
    # -----------------------------------------------------------------
    print("[AE] no unsafe grep findings")
    combined_text = main_text + "\n" + system_text + "\n" + css_text + "\n" + self_text
    found_unsafe = [c for c in UNSAFE_DONE_CLAIMS if c in combined_text]
    self_forbidden_imports = find_forbidden_imports(self_text)
    self_forbidden_calls = find_forbidden_calls(self_text)
    self_git_subcommands = find_git_subcommands(self_text)
    self_disallowed_git_subcommands = [s for s in self_git_subcommands if s not in ALLOWED_GIT_SUBCOMMANDS]
    ae_findings = found_unsafe + self_forbidden_imports + self_forbidden_calls + self_disallowed_git_subcommands
    check(
        f"AE. no unsafe grep findings（found {ae_findings}）" if ae_findings else "AE. no unsafe grep findings",
        not ae_findings,
    )

    print("[AF] patches/ remains untracked")
    patches_tracked = git_lines(["ls-files", "--", "patches/"])
    check(
        f"AF. patches/ remains untracked（found tracked {patches_tracked}）"
        if patches_tracked else "AF. patches/ remains untracked",
        not patches_tracked,
    )

    print("[AG] no tag")
    tags_at_head = git_lines(["tag", "--points-at", "HEAD"])
    check(
        f"AG. no tag（found {tags_at_head}）" if tags_at_head else "AG. no tag",
        not tags_at_head,
    )

    # -----------------------------------------------------------------
    total = len(PASS) + len(FAIL)
    print(f"\n合計：{len(PASS)}/{total} 通過")
    if FAIL:
        print(f"\nXX v0.8.4-D readiness 失敗 {len(FAIL)} 項：")
        for f in FAIL:
            print(f"   - {f}")
        sys.exit(1)
    else:
        print("PASS: v0.8.4-D worker dry-run result audit trail dashboard read-only display implementation")
        sys.exit(0)


if __name__ == "__main__":
    main()
