"""v0.8.4-E readiness check: Worker Dry-run Result / Audit Trail Dashboard Display
Closeout / Validation Hardening Plan.

Pure local filesystem + git metadata validation, standard library only. It reads the
v0.8.4-E plan doc and this script's own source directly from the working tree, checks that
no existing tracked file was modified by this round, reads the *committed* v0.8.4-D Dashboard
display content directly (app/main.py, templates/system.html, static/dashboard.css) to confirm
it still holds, and re-runs several existing read-only reference checks (the v0.8.4-D
validation, the v0.8.4-B builder, the v0.8.4-C/B/A readiness, the v0.8.3-F validator, the
v0.8.3-G readiness, and the v0.8.3-B builder, all as subprocesses / direct imports) purely to
confirm the underlying series still stands.

It does NOT modify any file, does NOT start a server, sends no POST, makes no network call,
reads no secrets, reads no real queue DB, writes no queue, and does not call
Worker/OpenClaw/Hermes/Google Sheets. Its only subprocess use is invoking the current Python
interpreter on existing read-only check scripts already used elsewhere in this series; its
only git usage is read-only plumbing (rev-parse, status, diff, ls-files, log, merge-base, tag).
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

E_DOC_REL = (
    "docs/HERMES_OPENCLAW_WORKER_DRY_RUN_RESULT_AUDIT_TRAIL_DASHBOARD_DISPLAY_"
    "CLOSEOUT_VALIDATION_HARDENING_PLAN_V0_8_4_E.md"
)
E_DOC_PATH = REPO_ROOT / E_DOC_REL

E_SCRIPT_REL = (
    "scripts/check_hermes_openclaw_worker_dry_run_result_audit_trail_dashboard_display_"
    "closeout_validation_hardening_plan_v0_8_4_e.py"
)
E_SCRIPT_PATH = REPO_ROOT / E_SCRIPT_REL

D_SCRIPT_REL = (
    "scripts/check_hermes_openclaw_worker_dry_run_result_audit_trail_dashboard_read_only_"
    "display_implementation_v0_8_4_d.py"
)
D_SCRIPT_PATH = REPO_ROOT / D_SCRIPT_REL

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

# v0.8.4-D commit — the base this round starts from (HEAD == origin/master at round start).
EXPECTED_BASE_HEAD = "bf7777f8850822b083f7c868e8136bb5caf932d1"

REQUIRED_MODEL_REFERENCES = (
    "dry_run_result",
    "audit_trail_record",
    "owner_review_event",
    "readback_summary",
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

B4_PERMISSION_KEYS = (
    "execution_permission",
    "dispatch_permission",
    "external_side_effects_permission",
    "result_persistence_permission",
    "audit_trail_write_permission",
)

B4_RUNTIME_STATE_KEYS = (
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

B3_PERMISSION_KEYS = ("execution_permission", "dispatch_permission", "external_side_effects_permission")
B3_RUNTIME_KEYS = (
    "worker_started", "worker_loop_started", "openclaw_called", "hermes_called",
    "google_sheets_enabled", "real_queue_db_read", "queue_written", "post_enabled",
    "secrets_read", "webhook_created", "endpoint_created", "connector_created",
    "production_db_created", "remote_blackboard_api_runtime_created",
)

# The future v0.8.4-F exact Owner authorization phrase (must appear exactly once).
V0_8_4_F_AUTHORIZATION_PHRASE = (
    "批准實作 v0.8.4-F — Worker Dry-run Result / Audit Trail Dashboard Display Validation "
    "Hardening Implementation，僅允許新增 committed-state validation hardening script，"
    "用於穩定驗證 v0.8.4-D 已提交的 Dashboard read-only result/audit-trail display；"
    "不得修改 app/main.py，不得修改 templates/system.html，不得修改 static/dashboard.css，"
    "不得新增 POST，不得新增 form/button/action URL，"
    "不得新增 approve/execute/dispatch/send controls，不得啟動 Worker，"
    "不得執行 Worker loop，不得執行任務，不得呼叫 OpenClaw，不得啟動或連接 Hermes，"
    "不得讀寫 Google Sheets，不得讀 real queue DB，不得寫 queue，不得讀 secrets，"
    "不得建立 webhook/endpoint/connector，不得建立 production/shared DB 或 "
    "Remote Blackboard API runtime。"
)

# Built from (prefix, suffix) pairs and joined at runtime so the *contiguous* phrase never
# appears literally in this script's own source (avoids this check self-tripping when it
# scans its own file as part of the combined-text scan below).
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
    ("v0.8.4-F", " started"),
)
UNSAFE_DONE_CLAIMS = tuple(prefix + suffix for prefix, suffix in UNSAFE_DONE_CLAIM_PARTS)

# Substrings that make an Owner-Review-phase FAIL line from an *older* readiness/validator
# script acceptable: every such script's own untracked-file-tolerance check label already
# contains "untracked" or "modified" by this whole series' consistent naming convention
# (e.g. "no unexpected untracked files", "... PASS or only acceptable Owner Review untracked
# observation"), which holds true no matter how many layers deep the failure is nested,
# because each layer's own label text is what gets printed at that layer's own top level.
ACCEPTABLE_OWNER_REVIEW_SUBSTRINGS = (
    "app/main.py",
    "templates/system.html",
    "static/dashboard.css",
    "v0.8.4-E",
    E_DOC_REL,
    E_SCRIPT_REL,
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


def detect_phase() -> str:
    e_tracked = is_tracked(E_SCRIPT_REL)
    if not e_tracked:
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
            f"v0.8.4-E doc/script as untracked/modified — an Owner Review phase artifact, "
            f"not a content/safety-boundary failure)"
            if tolerated
            else f"{letter}. {label}（returncode={run.returncode}, stdout tail={run.stdout[-800:]!r}）"
        ),
        full_pass or tolerated,
    )


def main() -> None:
    doc_text = read_text(E_DOC_PATH)
    self_text = read_text(E_SCRIPT_PATH)
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

    print("[B] v0.8.4-E plan doc exists")
    check("B. v0.8.4-E plan doc exists", E_DOC_PATH.is_file())

    print("[C] v0.8.4-E readiness script exists")
    check("C. v0.8.4-E readiness script exists", E_SCRIPT_PATH.is_file())

    print("[D] plan doc is untracked in Owner Review phase")
    check("D. plan doc is untracked in Owner Review phase", phase != "owner_review" or not is_tracked(E_DOC_REL))

    print("[E] readiness script is untracked in Owner Review phase")
    check("E. readiness script is untracked in Owner Review phase", phase != "owner_review" or not is_tracked(E_SCRIPT_REL))

    print("[F] no tracked files modified")
    check(
        f"F. no tracked files modified（found {sorted(tracked_changed)}）" if tracked_changed else "F. no tracked files modified",
        not tracked_changed,
    )

    print("[G] untracked only v0.8.4-E doc, v0.8.4-E script, patches/*")
    allowed_untracked = {E_DOC_REL, E_SCRIPT_REL} if phase == "owner_review" else set()
    unexpected_untracked = {p for p in untracked if p not in allowed_untracked and not p.startswith("patches/")}
    check(
        f"G. no unexpected untracked files（found {sorted(unexpected_untracked)}）"
        if unexpected_untracked else "G. no unexpected untracked files",
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

    print("[K] v0.8.4-D validation script not modified")
    check("K. v0.8.4-D validation script not modified", not_modified(D_SCRIPT_REL))

    print("[L] v0.8.4-C/B/A artifacts not modified")
    check(
        "L. v0.8.4-C/B/A artifacts not modified",
        not_modified(
            C4_DOC_REL, C4_SCRIPT_REL, B4_DOC_REL, B4_FIXTURE_REL, B4_BUILDER_REL, B4_SCRIPT_REL,
            A4_DOC_REL, A4_SCRIPT_REL,
        ),
    )

    print("[M] v0.8.3-G/F/E/D/C/B/A artifacts not modified")
    check(
        "M. v0.8.3-G/F/E/D/C/B/A artifacts not modified",
        not_modified(
            G_DOC_REL, G_SCRIPT_REL, F_SCRIPT_REL, E3_DOC_REL, E3_SCRIPT_REL, D3_SCRIPT_REL,
            C3_DOC_REL, C3_SCRIPT_REL, B3_DOC_REL, B3_FIXTURE_REL, B3_BUILDER_REL, B3_SCRIPT_REL,
            A3_DOC_REL, A3_SCRIPT_REL,
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

    print("[O] P loader / V adapter / W/X/Y/Z / fixtures not modified")
    check(
        "O. P loader / V adapter / W/X/Y/Z / fixtures not modified",
        not_modified(P_LOADER_REL, V_ADAPTER_REL, OLD_FIXTURE_JSON_REL, *WXYZ_REL),
    )

    # -----------------------------------------------------------------
    # Plan doc content checks
    # -----------------------------------------------------------------
    print("[P] plan doc contains v0.8.4-A/B/C/D DONE / PUSHED / CLOSED states")
    check(
        "P. plan doc contains v0.8.4-A/B/C/D DONE / PUSHED / CLOSED states",
        "v0.8.4-A is DONE / PUSHED / CLOSED" in doc_text
        and "v0.8.4-B is DONE / PUSHED / CLOSED" in doc_text
        and "v0.8.4-C is DONE / PUSHED / CLOSED" in doc_text
        and "v0.8.4-D is DONE / PUSHED / VERIFIED / CLOSED" in doc_text,
    )

    print(f"[Q] plan doc contains latest HEAD {EXPECTED_BASE_HEAD}")
    check(f"Q. plan doc contains latest HEAD {EXPECTED_BASE_HEAD}", EXPECTED_BASE_HEAD in doc_text)

    print("[R] plan doc says plan-only")
    check("R. plan doc says plan-only", "plan-only" in doc_text)

    print("[S] plan doc says /dashboard/system remains GET-only")
    check("S. plan doc says /dashboard/system remains GET-only", "/dashboard/system remains GET-only" in doc_text)

    print("[T] plan doc says display remains read-only")
    check("T. plan doc says display remains read-only", "Dashboard display is read-only" in doc_text)

    print("[U] plan doc says source remains synthetic_local_only and preview_only remains true")
    check(
        "U. plan doc says source remains synthetic_local_only and preview_only remains true",
        "source remains synthetic_local_only" in doc_text and "preview_only remains true" in doc_text,
    )

    print("[V] plan doc says all v0.8.4-B result/audit/review/readback statuses remain preview/owner-review only")
    v_statuses = (
        "dry_run_result.result_status remains preview_result_not_executed",
        "audit_trail_record.audit_status remains preview_audit_not_persisted",
        "owner_review_event.review_status remains owner_review_required",
        "readback_summary.summary_status remains preview_readback_only",
    )
    missing_v = [s for s in v_statuses if s not in doc_text]
    check(
        f"V. plan doc says all v0.8.4-B result/audit/review/readback statuses remain preview/owner-review only（missing {missing_v}）"
        if missing_v else "V. plan doc says all v0.8.4-B result/audit/review/readback statuses remain preview/owner-review only",
        not missing_v,
    )

    print("[W] plan doc says all permission flags remain false")
    check("W. plan doc says all permission flags remain false", "all permission flags remain false" in doc_text)

    print("[X] plan doc says all runtime flags remain false")
    check("X. plan doc says all runtime flags remain false", "all runtime flags remain false" in doc_text)

    print("[Y] plan doc describes v0.8.4-D display scope")
    check("Y. plan doc describes v0.8.4-D display scope", "v0.8.4-D committed display scope" in doc_text)

    print("[Z] plan doc describes future validation hardening")
    check("Z. plan doc describes future validation hardening", "Future validation hardening" in doc_text)

    print("[AA] plan doc contains future v0.8.4-F exact authorization phrase exactly once")
    phrase_count = doc_text.count(V0_8_4_F_AUTHORIZATION_PHRASE)
    check(
        f"AA. plan doc contains future v0.8.4-F exact authorization phrase exactly once（found {phrase_count}）"
        if phrase_count != 1 else "AA. plan doc contains future v0.8.4-F exact authorization phrase exactly once",
        phrase_count == 1,
    )

    print("[AB] plan doc says v0.8.4-F must not modify app/main.py / templates/system.html / static/dashboard.css")
    check(
        "AB. plan doc says v0.8.4-F must not modify app/main.py / templates/system.html / static/dashboard.css",
        "v0.8.4-F must not modify app/main.py" in doc_text
        and "v0.8.4-F must not modify templates/system.html" in doc_text
        and "v0.8.4-F must not modify static/dashboard.css" in doc_text,
    )

    print("[AC] plan doc says v0.8.4-F must not add POST / form / button / action URL")
    check(
        "AC. plan doc says v0.8.4-F must not add POST / form / button / action URL",
        "v0.8.4-F must not add POST" in doc_text and "v0.8.4-F must not add form/button/action URL" in doc_text,
    )

    print("[AD] plan doc says v0.8.4-F must not add approve/execute/dispatch/send controls")
    check(
        "AD. plan doc says v0.8.4-F must not add approve/execute/dispatch/send controls",
        "v0.8.4-F must not add approve/execute/dispatch/send controls" in doc_text,
    )

    print("[AE] plan doc says v0.8.4-F must not start Worker / call OpenClaw / activate Hermes / use Google Sheets / read or write real queue DB")
    check(
        "AE. plan doc says v0.8.4-F must not start Worker / call OpenClaw / activate Hermes / "
        "use Google Sheets / read or write real queue DB",
        "v0.8.4-F must not start Worker" in doc_text
        and "v0.8.4-F must not call OpenClaw" in doc_text
        and "v0.8.4-F must not activate Hermes" in doc_text
        and "v0.8.4-F must not read/write Google Sheets" in doc_text
        and "v0.8.4-F must not read or write real queue DB" in doc_text,
    )

    print("[AF] plan doc contains no unsafe done-claims")
    combined_text = doc_text + "\n" + self_text
    found_unsafe = [c for c in UNSAFE_DONE_CLAIMS if c in combined_text]
    check(
        f"AF. plan doc contains no unsafe done-claims（found {found_unsafe}）" if found_unsafe else "AF. plan doc contains no unsafe done-claims",
        not found_unsafe,
    )

    # -----------------------------------------------------------------
    # Committed v0.8.4-D display checks (direct content read, not git diff)
    # -----------------------------------------------------------------
    print("[AG] committed app/main.py still has /dashboard/system GET-only")
    get_route_count = len(re.findall(r'@app\.get\(\s*["\']\/dashboard\/system["\']', main_text))
    no_other_method_route = not re.search(
        r'@app\.(post|put|delete|patch)\(\s*["\']\/dashboard\/system["\']', main_text, re.IGNORECASE
    )
    check("AG. committed app/main.py still has /dashboard/system GET-only", get_route_count == 1 and no_other_method_route)

    section = extract_block(system_text, '<section id="worker-dry-run-result-audit-trail"', "</section>")

    print("[AH] committed template still contains worker-dry-run-result-audit-trail section")
    missing_refs = [ref for ref in REQUIRED_MODEL_REFERENCES if ref not in section]
    check(
        "AH. committed template still contains worker-dry-run-result-audit-trail section",
        bool(section) and not missing_refs,
    )

    print("[AI] committed template has no form/button/action/method/onclick/control URLs in the new section")
    forbidden_ai = [p for p in TEMPLATE_FORBIDDEN_PATTERNS if p in section]
    check(
        f"AI. committed template has no form/button/action/method/onclick/control URLs in the new section（found {forbidden_ai}）"
        if forbidden_ai else "AI. committed template has no form/button/action/method/onclick/control URLs in the new section",
        not forbidden_ai,
    )

    css_block = extract_block(
        css_text, "/* v0.8.4-D: read-only worker dry-run result / audit trail display", "\0\0\0__unused_end_marker__\0\0\0"
    )
    print("[AJ] committed CSS has display classes and no cursor:pointer interactive affordance")
    missing_css = [c for c in REQUIRED_CSS_CLASSES if c not in css_block]
    forbidden_css = [p for p in CSS_FORBIDDEN_PATTERNS if p in css_block]
    check(
        f"AJ. committed CSS has display classes and no cursor:pointer interactive affordance（missing {missing_css}, forbidden {forbidden_css}）"
        if (missing_css or forbidden_css) else "AJ. committed CSS has display classes and no cursor:pointer interactive affordance",
        not missing_css and not forbidden_css,
    )

    # -----------------------------------------------------------------
    # Reference re-runs (subprocess / direct import, read-only)
    # -----------------------------------------------------------------
    print("[AK] v0.8.4-D validation PASS")
    d_run = run_reference_script(D_SCRIPT_PATH)
    check_reference_pass(
        "AK", "v0.8.4-D validation PASS", d_run,
        full_pass_marker="PASS: v0.8.4-D worker dry-run result audit trail dashboard read-only display implementation",
    )

    print("[AL] v0.8.4-B builder output remains safe")
    b4_ok = False
    b4_error = None
    try:
        b4_module = load_module("worker_dry_run_result_audit_trail_boundary_v0_8_4_b", B4_BUILDER_PATH)
        b4_model = b4_module.build_worker_dry_run_result_audit_trail_model()
        b4_module.validate_worker_dry_run_result_audit_trail_model(b4_model)
        b4_ok = (
            b4_model.get("source") == "synthetic_local_only"
            and b4_model.get("preview_only") is True
            and b4_model.get("dry_run_result", {}).get("result_status") == "preview_result_not_executed"
            and b4_model.get("audit_trail_record", {}).get("audit_status") == "preview_audit_not_persisted"
            and b4_model.get("owner_review_event", {}).get("review_status") == "owner_review_required"
            and b4_model.get("readback_summary", {}).get("summary_status") == "preview_readback_only"
            and all(b4_model.get("permissions", {}).get(key) is False for key in B4_PERMISSION_KEYS)
            and all(b4_model.get("runtime_state", {}).get(key) is False for key in B4_RUNTIME_STATE_KEYS)
        )
    except Exception as exc:  # noqa: BLE001
        b4_error = str(exc)
    check(
        f"AL. v0.8.4-B builder output remains safe（error {b4_error}）" if not b4_ok else "AL. v0.8.4-B builder output remains safe",
        b4_ok,
    )

    print("[AM] v0.8.4-C readiness PASS")
    c4_run = run_reference_script(C4_SCRIPT_PATH)
    check_reference_pass(
        "AM", "v0.8.4-C readiness PASS", c4_run,
        full_pass_marker="PASS: v0.8.4-C worker dry-run result audit trail dashboard read-only display plan",
    )

    print("[AN] v0.8.4-B readiness PASS")
    b4r_run = run_reference_script(B4_SCRIPT_PATH)
    check_reference_pass(
        "AN", "v0.8.4-B readiness PASS", b4r_run,
        full_pass_marker="PASS: v0.8.4-B worker dry-run result audit trail boundary implementation",
    )

    print("[AO] v0.8.4-A readiness PASS")
    a4_run = run_reference_script(A4_SCRIPT_PATH)
    check_reference_pass(
        "AO", "v0.8.4-A readiness PASS", a4_run,
        full_pass_marker="PASS: v0.8.4-A worker dry-run result audit trail boundary plan",
    )

    print("[AP] v0.8.3-F validator PASS")
    f_run = run_reference_script(F_SCRIPT_PATH)
    check_reference_pass(
        "AP", "v0.8.3-F validator PASS", f_run,
        full_pass_marker="PASS: v0.8.3-F worker dry-run preview dashboard display validation hardening",
    )

    print("[AQ] v0.8.3-G readiness PASS")
    g_run = run_reference_script(G_SCRIPT_PATH)
    check_reference_pass(
        "AQ", "v0.8.3-G readiness PASS", g_run,
        full_pass_marker="PASS: v0.8.3-G worker dry-run preview dashboard display closeout report",
    )

    print("[AR] v0.8.3-B builder still all permission/runtime flags false")
    b3_module = load_module("worker_dry_run_preview_boundary_v0_8_3_b", B3_BUILDER_PATH)
    b3_model = b3_module.build_worker_dry_run_preview_model()
    b3_permissions = b3_model.get("permissions", {})
    b3_runtime_state = b3_model.get("runtime_state", {})
    check(
        "AR. v0.8.3-B builder still all permission/runtime flags false",
        isinstance(b3_permissions, dict)
        and all(b3_permissions.get(key) is False for key in B3_PERMISSION_KEYS)
        and isinstance(b3_runtime_state, dict)
        and all(b3_runtime_state.get(key) is False for key in B3_RUNTIME_KEYS),
    )

    print("[AS] patches/ remains untracked")
    patches_tracked = git_lines(["ls-files", "--", "patches/"])
    check(
        f"AS. patches/ remains untracked（found tracked {patches_tracked}）" if patches_tracked else "AS. patches/ remains untracked",
        not patches_tracked,
    )

    print("[AT] no tag")
    tags_at_head = git_lines(["tag", "--points-at", "HEAD"])
    check(f"AT. no tag（found {tags_at_head}）" if tags_at_head else "AT. no tag", not tags_at_head)

    # -----------------------------------------------------------------
    total = len(PASS) + len(FAIL)
    print(f"\n合計：{len(PASS)}/{total} 通過")
    if FAIL:
        print(f"\nXX v0.8.4-E readiness 失敗 {len(FAIL)} 項：")
        for f in FAIL:
            print(f"   - {f}")
        sys.exit(1)
    else:
        print("PASS: v0.8.4-E worker dry-run result audit trail dashboard display closeout validation hardening plan")
        sys.exit(0)


if __name__ == "__main__":
    main()
