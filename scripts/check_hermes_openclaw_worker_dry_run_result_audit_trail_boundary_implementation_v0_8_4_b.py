"""v0.8.4-B readiness check: Worker Dry-run Result / Audit Trail Boundary Implementation.

Pure local filesystem + git metadata validation, standard library only. It reads the
v0.8.4-B doc, fixture, builder, and this script's own source directly from the working
tree, checks that no existing tracked file was modified by this round, and re-runs several
existing read-only reference checks (the v0.8.4-A readiness script, the v0.8.3-F validator,
and the v0.8.3-B builder, all as subprocesses / direct imports) purely to confirm the
underlying series still stands. It also imports and runs the new v0.8.4-B builder directly.

It does NOT modify any file, does NOT start a server, sends no POST, makes no network call,
reads no secrets, reads no real queue DB, writes no queue, and does not call
Worker/OpenClaw/Hermes/Google Sheets. Its only subprocess use is invoking the current Python
interpreter on existing read-only check scripts already used elsewhere in this series; its
only git usage is read-only plumbing (rev-parse, status, diff, ls-files, log, merge-base,
tag).
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

MAIN_PY_REL = "app/main.py"
SYSTEM_HTML_REL = "templates/system.html"
DASHBOARD_CSS_REL = "static/dashboard.css"

B4_DOC_REL = (
    "docs/HERMES_OPENCLAW_WORKER_DRY_RUN_RESULT_AUDIT_TRAIL_BOUNDARY_IMPLEMENTATION_V0_8_4_B.md"
)
B4_DOC_PATH = REPO_ROOT / B4_DOC_REL

B4_FIXTURE_REL = (
    "fixtures/local_mock_data/hermes_openclaw_worker_dry_run_result_audit_trail_v0_8_4_b.json"
)
B4_FIXTURE_PATH = REPO_ROOT / B4_FIXTURE_REL

B4_BUILDER_REL = "scripts/worker_dry_run_result_audit_trail_boundary_v0_8_4_b.py"
B4_BUILDER_PATH = REPO_ROOT / B4_BUILDER_REL

B4_SCRIPT_REL = (
    "scripts/check_hermes_openclaw_worker_dry_run_result_audit_trail_boundary_"
    "implementation_v0_8_4_b.py"
)
B4_SCRIPT_PATH = REPO_ROOT / B4_SCRIPT_REL

B4_ALL_FILES = (B4_DOC_REL, B4_FIXTURE_REL, B4_BUILDER_REL, B4_SCRIPT_REL)

A4_DOC_REL = (
    "docs/HERMES_OPENCLAW_WORKER_DRY_RUN_RESULT_AUDIT_TRAIL_BOUNDARY_PLAN_V0_8_4_A.md"
)
A4_SCRIPT_REL = (
    "scripts/check_hermes_openclaw_worker_dry_run_result_audit_trail_boundary_plan_v0_8_4_a.py"
)
A4_SCRIPT_PATH = REPO_ROOT / A4_SCRIPT_REL

G_DOC_REL = (
    "docs/HERMES_OPENCLAW_WORKER_DRY_RUN_PREVIEW_DASHBOARD_DISPLAY_CLOSEOUT_REPORT_V0_8_3_G.md"
)
G_SCRIPT_REL = (
    "scripts/check_hermes_openclaw_worker_dry_run_preview_dashboard_display_"
    "closeout_report_v0_8_3_g.py"
)

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

# v0.8.4-A commit — the base this round starts from (HEAD == origin/master at round start).
EXPECTED_BASE_HEAD = "ef17cefa3f28d32997758010c72d0ef25be7b0a7"

PERMISSION_KEYS = (
    "execution_permission",
    "dispatch_permission",
    "external_side_effects_permission",
    "result_persistence_permission",
    "audit_trail_write_permission",
)

RUNTIME_STATE_KEYS = (
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

FORBIDDEN_CONTROL_URL_KEYS = (
    "action_url",
    "post_url",
    "webhook_url",
    "endpoint_url",
    "execute_url",
    "dispatch_url",
    "send_url",
)

FORBIDDEN_REAL_VALUE_PATTERNS = (
    re.compile(r"spreadsheets/d/[A-Za-z0-9_-]{20,}"),
    re.compile(r"refresh_token"),
    re.compile(r"client_secret"),
    re.compile(r"private_key"),
    re.compile(r"-----BEGIN[ A-Z]*PRIVATE KEY-----"),
    re.compile(r"webhook_url"),
    re.compile(r"openclaw_endpoint"),
    re.compile(r"hermes_endpoint"),
    re.compile(r"production_db_url"),
    re.compile(r"remote_blackboard_api_url"),
    re.compile(r"real_queue_id"),
    re.compile(r"real_task_id"),
    re.compile(r"real_user_secret"),
    re.compile(r"spreadsheet_id"),
)

FORBIDDEN_BUILDER_IMPORT_PATTERN = re.compile(
    r"^\s*(import|from)\s+"
    r"(app(\.\w+)?|queue_store|QueueStore"
    r"|openclaw|hermes|google|sheets|requests|httpx|socket|urllib\.request|flask|uvicorn)\b",
    re.IGNORECASE,
)

FORBIDDEN_BUILDER_CALL_SUBSTRINGS = (
    "os.environ" + "[",
    "os.environ.get" + "(",
    "requests.get" + "(",
    "requests.post" + "(",
    "httpx.get" + "(",
    "httpx.post" + "(",
    "socket.socket" + "(",
    "urllib.request" + ".",
    "subprocess." + "run",
)

REQUIRED_ARTIFACT_SHAPE_KEYS = (
    "dry_run_result",
    "audit_trail_record",
    "owner_review_event",
    "readback_summary",
)

# Built from (prefix, suffix) pairs and joined at runtime so the *contiguous* phrase never
# appears literally in this script's own source (avoids this check self-tripping when it
# scans its own file as part of the combined-text scan below). Mirrors the v0.8.3-F/G and
# v0.8.4-A readiness scripts' UNSAFE_DONE_CLAIM_PARTS approach.
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
    ("v0.8.4-C", " started"),
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
    b4_tracked = is_tracked(B4_SCRIPT_REL)
    if not b4_tracked:
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
    return subprocess.run(
        [sys.executable, str(path)],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )


def _line_is_known_untracked_cascade_failure(fail_line: str, allowed_untracked: set[str]) -> bool:
    """A failure line is a tolerated cascade failure if every 'found [...]' path list
    appearing anywhere in it (including inside an embedded nested-script stdout tail
    dump, since a target script's own AK/AP/AQ-style tolerance check embeds its
    sub-script's full output on failure) is a subset of this round's own new v0.8.4-B
    files. This mirrors, one level deeper, the exact tolerance already used by the
    v0.8.3-G and v0.8.4-A readiness scripts for their own round's files."""
    if "no unexpected untracked files" not in fail_line and "untracked-file" not in fail_line:
        return False
    found_groups = re.findall(r"found (\[[^\]]*\])", fail_line)
    if not found_groups:
        return False
    for group in found_groups:
        paths = set(re.findall(r"'([^']*)'", group))
        if not paths or not paths <= allowed_untracked:
            return False
    return True


def check_tolerant_pass(
    letter: str,
    label_base: str,
    run: subprocess.CompletedProcess[str],
    full_pass_marker: str,
    allowed_untracked: set[str],
) -> None:
    """Accept full PASS, or a failure set where every failure (possibly nested one level
    through an inner tolerance check like v0.8.4-A's own AK check) traces only to this
    round's new v0.8.4-B files tripping an untracked-files self-check — the same known
    Owner Review phase artifact documented in the v0.8.3-G and v0.8.4-A readiness
    scripts, extended to tolerate the cascade those scripts' own tolerance logic causes
    when it doesn't yet know about *this* round's specific new files."""
    stdout = run.stdout
    full_pass = run.returncode == 0 and full_pass_marker in stdout

    only_b4_untracked_fail = False
    if not full_pass and run.returncode == 1:
        fail_summary_lines = re.findall(r"^\s{3}-\s*(.+)$", stdout, flags=re.MULTILINE)
        only_b4_untracked_fail = bool(fail_summary_lines) and all(
            _line_is_known_untracked_cascade_failure(line, allowed_untracked) for line in fail_summary_lines
        )

    check(
        f"{letter}. {label_base}"
        if full_pass
        else (
            f"{letter}. {label_base} (accepted: every failure traces only to this round's "
            f"new v0.8.4-B files tripping an untracked-file check, directly or via a nested "
            f"tolerance check — an Owner Review phase artifact, not a content/safety-boundary "
            f"failure)"
            if only_b4_untracked_fail
            else f"{letter}. {label_base}（returncode={run.returncode}, stdout tail={stdout[-800:]!r}）"
        ),
        full_pass or only_b4_untracked_fail,
    )


def main() -> None:
    doc_text = read_text(B4_DOC_PATH)
    self_text = read_text(B4_SCRIPT_PATH)
    builder_text = read_text(B4_BUILDER_PATH)
    fixture_raw_text = read_text(B4_FIXTURE_PATH)

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
    # [B]-[E] the four v0.8.4-B files exist
    # -----------------------------------------------------------------
    print("[B] v0.8.4-B doc exists")
    check("B. v0.8.4-B doc exists", B4_DOC_PATH.is_file())

    print("[C] v0.8.4-B fixture exists")
    check("C. v0.8.4-B fixture exists", B4_FIXTURE_PATH.is_file())

    print("[D] v0.8.4-B builder exists")
    check("D. v0.8.4-B builder exists", B4_BUILDER_PATH.is_file())

    print("[E] v0.8.4-B readiness exists")
    check("E. v0.8.4-B readiness exists", B4_SCRIPT_PATH.is_file())

    # -----------------------------------------------------------------
    # [F] all four v0.8.4-B files are untracked in Owner Review phase
    # -----------------------------------------------------------------
    print("[F] all four v0.8.4-B files are untracked in Owner Review phase")
    check(
        "F. all four v0.8.4-B files are untracked in Owner Review phase",
        phase != "owner_review" or all(not is_tracked(rel) for rel in B4_ALL_FILES),
    )

    # -----------------------------------------------------------------
    # [G] no tracked file is modified
    # -----------------------------------------------------------------
    print("[G] no tracked files modified")
    check(
        f"G. no tracked files modified（found {sorted(tracked_changed)}）"
        if tracked_changed
        else "G. no tracked files modified",
        not tracked_changed,
    )

    # -----------------------------------------------------------------
    # [H] untracked only v0.8.4-B files and patches/*
    # -----------------------------------------------------------------
    print("[H] untracked only v0.8.4-B files and patches/*")
    allowed_untracked = set(B4_ALL_FILES) if phase == "owner_review" else set()
    unexpected_untracked = {
        p for p in untracked if p not in allowed_untracked and not p.startswith("patches/")
    }
    check(
        f"H. no unexpected untracked files（found {sorted(unexpected_untracked)}）"
        if unexpected_untracked
        else "H. no unexpected untracked files",
        not unexpected_untracked,
    )

    # -----------------------------------------------------------------
    # [I]-[O] protected tracked files are not modified
    # -----------------------------------------------------------------
    def not_modified(*rels: str) -> bool:
        return all(rel not in tracked_changed for rel in rels)

    print("[I] app/main.py not modified")
    check("I. app/main.py not modified", not_modified(MAIN_PY_REL))

    print("[J] templates/system.html not modified")
    check("J. templates/system.html not modified", not_modified(SYSTEM_HTML_REL))

    print("[K] static/dashboard.css not modified")
    check("K. static/dashboard.css not modified", not_modified(DASHBOARD_CSS_REL))

    print("[L] v0.8.4-A plan/readiness not modified")
    check("L. v0.8.4-A plan/readiness not modified", not_modified(A4_DOC_REL, A4_SCRIPT_REL))

    print("[M] v0.8.3-G/F/E/D/C/B/A artifacts not modified")
    check(
        "M. v0.8.3-G/F/E/D/C/B/A artifacts not modified",
        not_modified(
            G_DOC_REL, G_SCRIPT_REL, F_SCRIPT_REL, E_DOC_REL, E_SCRIPT_REL, D_SCRIPT_REL,
            C_DOC_REL, C_SCRIPT_REL, B_DOC_REL, B_FIXTURE_REL, B_BUILDER_REL, B_SCRIPT_REL,
            A_DOC_REL, A_SCRIPT_REL,
        ),
    )

    print("[N] v0.8.2 artifacts not modified")
    check(
        "N. v0.8.2 artifacts not modified",
        not_modified(
            F082_DOC_REL, F082_SCRIPT_REL, E082_SCRIPT_REL, D082_DOC_REL, D082_SCRIPT_REL,
            C082_SCRIPT_REL, B082_DOC_REL, B082_SCRIPT_REL, A082_SCRIPT_REL,
        ),
    )

    print("[O] P loader / V adapter / W/X/Y/Z / fixtures not modified except the new v0.8.4-B fixture")
    check(
        "O. P loader / V adapter / W/X/Y/Z / fixtures not modified except the new v0.8.4-B fixture",
        not_modified(P_LOADER_REL, V_ADAPTER_REL, OLD_FIXTURE_JSON_REL, B_FIXTURE_REL, *WXYZ_REL),
    )

    # -----------------------------------------------------------------
    # [P]-[Y] doc content checks
    # -----------------------------------------------------------------
    print("[P] doc contains required title")
    check(
        "P. doc contains required title",
        "# Hermes × OpenClaw v0.8.4-B" in doc_text
        and "# Worker Dry-run Result / Audit Trail Boundary Implementation" in doc_text,
    )

    print("[Q] doc states synthetic local-only implementation")
    check(
        "Q. doc states synthetic local-only implementation",
        "synthetic local-only implementation" in doc_text,
    )

    print("[R] doc states v0.8.4-A DONE / PUSHED / CLOSED")
    check("R. doc states v0.8.4-A DONE / PUSHED / CLOSED", "v0.8.4-A = DONE / PUSHED / CLOSED" in doc_text)

    print("[S] doc contains latest HEAD ef17cefa3f28d32997758010c72d0ef25be7b0a7")
    check(
        "S. doc contains latest HEAD ef17cefa3f28d32997758010c72d0ef25be7b0a7",
        EXPECTED_BASE_HEAD in doc_text,
    )

    print("[T] doc describes dry_run_result / audit_trail_record / owner_review_event / readback_summary")
    missing_shapes = [key for key in REQUIRED_ARTIFACT_SHAPE_KEYS if key not in doc_text]
    check(
        f"T. doc describes dry_run_result / audit_trail_record / owner_review_event / readback_summary（missing {missing_shapes}）"
        if missing_shapes
        else "T. doc describes dry_run_result / audit_trail_record / owner_review_event / readback_summary",
        not missing_shapes,
    )

    print("[U] doc describes all permission flags false")
    missing_perm_lines = [f"{key} = false" for key in PERMISSION_KEYS if f"{key} = false" not in doc_text]
    check(
        f"U. doc describes all permission flags false（missing {missing_perm_lines}）"
        if missing_perm_lines
        else "U. doc describes all permission flags false",
        not missing_perm_lines,
    )

    print("[V] doc describes all runtime flags false")
    missing_runtime_lines = [f"{key} = false" for key in RUNTIME_STATE_KEYS if f"{key} = false" not in doc_text]
    check(
        f"V. doc describes all runtime flags false（missing {missing_runtime_lines}）"
        if missing_runtime_lines
        else "V. doc describes all runtime flags false",
        not missing_runtime_lines,
    )

    print("[W] doc contains future v0.8.4-C handoff")
    check(
        "W. doc contains future v0.8.4-C handoff",
        "v0.8.4-C" in doc_text
        and "Worker Dry-run Result / Audit Trail Dashboard Read-only Display Plan" in doc_text,
    )

    print("[X] doc says v0.8.4-C must not start Worker / call OpenClaw / activate Hermes / use Google Sheets / read or write real queue DB")
    check(
        "X. doc says v0.8.4-C must not start Worker / call OpenClaw / activate Hermes / use "
        "Google Sheets / read or write real queue DB",
        "v0.8.4-C must not start Worker" in doc_text
        and "v0.8.4-C must not call OpenClaw" in doc_text
        and "v0.8.4-C must not activate Hermes" in doc_text
        and "v0.8.4-C must not read/write Google Sheets" in doc_text
        and "v0.8.4-C must not read or write real queue DB" in doc_text,
    )

    print("[Y] doc contains no unsafe done-claims")
    combined_text = doc_text + "\n" + self_text
    found_unsafe = [c for c in UNSAFE_DONE_CLAIMS if c in combined_text]
    check(
        f"Y. doc contains no unsafe done-claims（found {found_unsafe}）"
        if found_unsafe
        else "Y. doc contains no unsafe done-claims",
        not found_unsafe,
    )

    # -----------------------------------------------------------------
    # [Z]-[AK] fixture content checks
    # -----------------------------------------------------------------
    print("[Z] fixture is valid JSON object")
    fixture_obj = None
    fixture_parse_error = None
    try:
        fixture_obj = json.loads(fixture_raw_text)
    except Exception as exc:  # noqa: BLE001
        fixture_parse_error = str(exc)
    check(
        f"Z. fixture is valid JSON object（error {fixture_parse_error}）"
        if fixture_parse_error or not isinstance(fixture_obj, dict)
        else "Z. fixture is valid JSON object",
        fixture_parse_error is None and isinstance(fixture_obj, dict),
    )

    fixture_obj = fixture_obj if isinstance(fixture_obj, dict) else {}

    print("[AA] fixture version = v0.8.4-B")
    check("AA. fixture version = v0.8.4-B", fixture_obj.get("version") == "v0.8.4-B")

    print("[AB] fixture source = synthetic_local_only")
    check("AB. fixture source = synthetic_local_only", fixture_obj.get("source") == "synthetic_local_only")

    print("[AC] fixture preview_only = true")
    check("AC. fixture preview_only = true", fixture_obj.get("preview_only") is True)

    print("[AD] fixture contains dry_run_result / audit_trail_record / owner_review_event / readback_summary")
    missing_fixture_shapes = [key for key in REQUIRED_ARTIFACT_SHAPE_KEYS if not isinstance(fixture_obj.get(key), dict)]
    check(
        f"AD. fixture contains dry_run_result / audit_trail_record / owner_review_event / readback_summary（missing {missing_fixture_shapes}）"
        if missing_fixture_shapes
        else "AD. fixture contains dry_run_result / audit_trail_record / owner_review_event / readback_summary",
        not missing_fixture_shapes,
    )

    dry_run_result = fixture_obj.get("dry_run_result") if isinstance(fixture_obj.get("dry_run_result"), dict) else {}
    audit_trail_record = fixture_obj.get("audit_trail_record") if isinstance(fixture_obj.get("audit_trail_record"), dict) else {}
    owner_review_event = fixture_obj.get("owner_review_event") if isinstance(fixture_obj.get("owner_review_event"), dict) else {}
    readback_summary = fixture_obj.get("readback_summary") if isinstance(fixture_obj.get("readback_summary"), dict) else {}
    fixture_permissions = fixture_obj.get("permissions") if isinstance(fixture_obj.get("permissions"), dict) else {}
    fixture_runtime_state = fixture_obj.get("runtime_state") if isinstance(fixture_obj.get("runtime_state"), dict) else {}

    print("[AE] fixture result_status = preview_result_not_executed")
    check(
        "AE. fixture result_status = preview_result_not_executed",
        dry_run_result.get("result_status") == "preview_result_not_executed",
    )

    print("[AF] fixture audit_status = preview_audit_not_persisted")
    check(
        "AF. fixture audit_status = preview_audit_not_persisted",
        audit_trail_record.get("audit_status") == "preview_audit_not_persisted",
    )

    print("[AG] fixture review_status = owner_review_required")
    check(
        "AG. fixture review_status = owner_review_required",
        owner_review_event.get("review_status") == "owner_review_required",
    )

    print("[AH] fixture summary_status = preview_readback_only")
    check(
        "AH. fixture summary_status = preview_readback_only",
        readback_summary.get("summary_status") == "preview_readback_only",
    )

    print("[AI] all fixture permission flags false")
    bad_perm = [key for key in PERMISSION_KEYS if fixture_permissions.get(key) is not False]
    check(
        f"AI. all fixture permission flags false（bad {bad_perm}）" if bad_perm else "AI. all fixture permission flags false",
        not bad_perm,
    )

    print("[AJ] all fixture runtime flags false")
    bad_runtime = [key for key in RUNTIME_STATE_KEYS if fixture_runtime_state.get(key) is not False]
    check(
        f"AJ. all fixture runtime flags false（bad {bad_runtime}）" if bad_runtime else "AJ. all fixture runtime flags false",
        not bad_runtime,
    )

    print("[AK] fixture contains no real secrets / endpoints / spreadsheet ids / queue ids / tokens")
    forbidden_hits = [
        pattern.pattern for pattern in FORBIDDEN_REAL_VALUE_PATTERNS if pattern.search(fixture_raw_text)
    ]
    forbidden_key_hits = [key for key in FORBIDDEN_CONTROL_URL_KEYS if key in fixture_raw_text]
    all_forbidden_hits = forbidden_hits + forbidden_key_hits
    check(
        f"AK. fixture contains no real secrets / endpoints / spreadsheet ids / queue ids / tokens（found {all_forbidden_hits}）"
        if all_forbidden_hits
        else "AK. fixture contains no real secrets / endpoints / spreadsheet ids / queue ids / tokens",
        not all_forbidden_hits,
    )

    # -----------------------------------------------------------------
    # [AL]-[AO] builder self-safety and behavior checks
    # -----------------------------------------------------------------
    print("[AL] builder imports only standard library")
    builder_forbidden_imports = [
        line.strip() for line in builder_text.splitlines() if FORBIDDEN_BUILDER_IMPORT_PATTERN.match(line)
    ]
    check(
        f"AL. builder imports only standard library（found {builder_forbidden_imports}）"
        if builder_forbidden_imports
        else "AL. builder imports only standard library",
        not builder_forbidden_imports,
    )

    print("[AM] builder does not import app/main.py / QueueStore / Worker / OpenClaw / Hermes / Google Sheets")
    check(
        "AM. builder does not import app/main.py / QueueStore / Worker / OpenClaw / Hermes / Google Sheets",
        not builder_forbidden_imports,
    )

    print("[AN] builder performs no network / POST / git mutation / file writes / os.environ secret reads")
    builder_forbidden_calls = [needle for needle in FORBIDDEN_BUILDER_CALL_SUBSTRINGS if needle and needle in builder_text]
    builder_write_mode_open = bool(re.search(r'open\([^)]*["\'][wax]\+?b?["\']', builder_text))
    check(
        f"AN. builder performs no network / POST / git mutation / file writes / os.environ "
        f"secret reads（forbidden calls {builder_forbidden_calls}, write-mode open="
        f"{builder_write_mode_open}）"
        if builder_forbidden_calls or builder_write_mode_open
        else "AN. builder performs no network / POST / git mutation / file writes / os.environ secret reads",
        not builder_forbidden_calls and not builder_write_mode_open,
    )

    # -----------------------------------------------------------------
    # [AO] builder output passes validation (direct import + call)
    # -----------------------------------------------------------------
    print("[AO] builder output passes validation")
    builder_ok = False
    builder_error = None
    b4_model = None
    try:
        b4_module = load_module("worker_dry_run_result_audit_trail_boundary_v0_8_4_b", B4_BUILDER_PATH)
        b4_model = b4_module.build_worker_dry_run_result_audit_trail_model()
        b4_module.validate_worker_dry_run_result_audit_trail_model(b4_model)
        builder_ok = (
            b4_model.get("source") == "synthetic_local_only"
            and b4_model.get("preview_only") is True
            and b4_model.get("dry_run_result", {}).get("result_status") == "preview_result_not_executed"
            and b4_model.get("audit_trail_record", {}).get("audit_status") == "preview_audit_not_persisted"
            and b4_model.get("owner_review_event", {}).get("review_status") == "owner_review_required"
            and b4_model.get("readback_summary", {}).get("summary_status") == "preview_readback_only"
            and all(b4_model.get("permissions", {}).get(key) is False for key in PERMISSION_KEYS)
            and all(b4_model.get("runtime_state", {}).get(key) is False for key in RUNTIME_STATE_KEYS)
        )
    except Exception as exc:  # noqa: BLE001
        builder_error = str(exc)
    check(
        f"AO. builder output passes validation（error {builder_error}）" if not builder_ok else "AO. builder output passes validation",
        builder_ok,
    )

    # -----------------------------------------------------------------
    # [AP] v0.8.4-A readiness PASS or only acceptable Owner Review untracked observation
    # -----------------------------------------------------------------
    print("[AP] v0.8.4-A readiness PASS or only acceptable Owner Review untracked observation")
    a4_run = run_reference_script(A4_SCRIPT_PATH)
    check_tolerant_pass(
        "AP",
        "v0.8.4-A readiness PASS or only acceptable Owner Review untracked observation",
        a4_run,
        full_pass_marker="PASS: v0.8.4-A worker dry-run result audit trail boundary plan",
        allowed_untracked=set(B4_ALL_FILES),
    )

    # -----------------------------------------------------------------
    # [AQ] v0.8.3-F validator PASS or only acceptable Owner Review untracked observation
    # -----------------------------------------------------------------
    print("[AQ] v0.8.3-F validator PASS or only acceptable Owner Review untracked observation")
    f_run = run_reference_script(F_SCRIPT_PATH)
    check_tolerant_pass(
        "AQ",
        "v0.8.3-F validator PASS or only acceptable Owner Review untracked observation",
        f_run,
        full_pass_marker="PASS: v0.8.3-F worker dry-run preview dashboard display validation hardening",
        allowed_untracked=set(B4_ALL_FILES),
    )

    # -----------------------------------------------------------------
    # [AR] v0.8.3-B builder still all permission/runtime flags false
    # -----------------------------------------------------------------
    print("[AR] v0.8.3-B builder still all permission/runtime flags false")
    b3_module = load_module("worker_dry_run_preview_boundary_v0_8_3_b", B_BUILDER_PATH)
    b3_model = b3_module.build_worker_dry_run_preview_model()
    b3_permissions = b3_model.get("permissions", {})
    b3_runtime_state = b3_model.get("runtime_state", {})
    b3_permission_keys = ("execution_permission", "dispatch_permission", "external_side_effects_permission")
    b3_runtime_keys = (
        "worker_started", "worker_loop_started", "openclaw_called", "hermes_called",
        "google_sheets_enabled", "real_queue_db_read", "queue_written", "post_enabled",
        "secrets_read", "webhook_created", "endpoint_created", "connector_created",
        "production_db_created", "remote_blackboard_api_runtime_created",
    )
    check(
        "AR. v0.8.3-B builder still all permission/runtime flags false",
        isinstance(b3_permissions, dict)
        and all(b3_permissions.get(key) is False for key in b3_permission_keys)
        and isinstance(b3_runtime_state, dict)
        and all(b3_runtime_state.get(key) is False for key in b3_runtime_keys),
    )

    # -----------------------------------------------------------------
    # [AS] patches/ remains untracked
    # -----------------------------------------------------------------
    print("[AS] patches/ remains untracked")
    patches_tracked = git_lines(["ls-files", "--", "patches/"])
    check(
        f"AS. patches/ remains untracked（found tracked {patches_tracked}）"
        if patches_tracked
        else "AS. patches/ remains untracked",
        not patches_tracked,
    )

    # -----------------------------------------------------------------
    # [AT] no tag
    # -----------------------------------------------------------------
    print("[AT] no tag")
    tags_at_head = git_lines(["tag", "--points-at", "HEAD"])
    check(
        f"AT. no tag（found {tags_at_head}）" if tags_at_head else "AT. no tag",
        not tags_at_head,
    )

    # -----------------------------------------------------------------
    # 結果
    # -----------------------------------------------------------------
    total = len(PASS) + len(FAIL)
    print(f"\n合計：{len(PASS)}/{total} 通過")
    if FAIL:
        print(f"\nXX v0.8.4-B readiness 失敗 {len(FAIL)} 項：")
        for f in FAIL:
            print(f"   - {f}")
        sys.exit(1)
    else:
        print("PASS: v0.8.4-B worker dry-run result audit trail boundary implementation")
        sys.exit(0)


if __name__ == "__main__":
    main()
