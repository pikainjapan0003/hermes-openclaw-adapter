"""v0.8.4-C readiness check: Worker Dry-run Result / Audit Trail Dashboard Read-only
Display Plan.

Pure local filesystem + git metadata validation, standard library only. It reads the
v0.8.4-C plan doc and this script's own source directly from the working tree, checks
that no existing tracked file was modified by this round, and re-runs several existing
read-only reference checks (the v0.8.4-B builder/readiness, the v0.8.4-A readiness, and
the v0.8.3-F validator, all as subprocesses / direct imports) purely to confirm the
underlying series still stands.

It does NOT modify any file, does NOT start a server, sends no POST, makes no network call,
reads no secrets, reads no real queue DB, writes no queue, and does not call
Worker/OpenClaw/Hermes/Google Sheets. Its only subprocess use is invoking the current Python
interpreter on existing read-only check scripts already used elsewhere in this series; its
only git usage is read-only plumbing (rev-parse, status, diff, ls-files, log, merge-base,
tag).
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

C4_DOC_REL = (
    "docs/HERMES_OPENCLAW_WORKER_DRY_RUN_RESULT_AUDIT_TRAIL_DASHBOARD_READ_ONLY_"
    "DISPLAY_PLAN_V0_8_4_C.md"
)
C4_DOC_PATH = REPO_ROOT / C4_DOC_REL

C4_SCRIPT_REL = (
    "scripts/check_hermes_openclaw_worker_dry_run_result_audit_trail_dashboard_read_"
    "only_display_plan_v0_8_4_c.py"
)
C4_SCRIPT_PATH = REPO_ROOT / C4_SCRIPT_REL

C4_ALL_FILES = (C4_DOC_REL, C4_SCRIPT_REL)

# Distinguishing filename fragments unique to this round's two new files — used to
# confirm a tolerated cascade failure really does trace back to this round (see
# check_tolerant_pass below).
C4_OWN_FILE_FRAGMENTS = ("V0_8_4_C.md", "v0_8_4_c.py")

B4_DOC_REL = (
    "docs/HERMES_OPENCLAW_WORKER_DRY_RUN_RESULT_AUDIT_TRAIL_BOUNDARY_IMPLEMENTATION_V0_8_4_B.md"
)
B4_FIXTURE_REL = (
    "fixtures/local_mock_data/hermes_openclaw_worker_dry_run_result_audit_trail_v0_8_4_b.json"
)
B4_BUILDER_REL = "scripts/worker_dry_run_result_audit_trail_boundary_v0_8_4_b.py"
B4_BUILDER_PATH = REPO_ROOT / B4_BUILDER_REL
B4_SCRIPT_REL = (
    "scripts/check_hermes_openclaw_worker_dry_run_result_audit_trail_boundary_"
    "implementation_v0_8_4_b.py"
)
B4_SCRIPT_PATH = REPO_ROOT / B4_SCRIPT_REL

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

# v0.8.4-B commit — the base this round starts from (HEAD == origin/master at round start).
EXPECTED_BASE_HEAD = "6d6d3ed6153e13ce4f1b155bc11e1c5248427d12"

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

# The future v0.8.4-D exact Owner authorization phrase (must appear exactly once).
V0_8_4_D_AUTHORIZATION_PHRASE = (
    "批准實作 v0.8.4-D — Worker Dry-run Result / Audit Trail Dashboard Read-only Display "
    "Implementation，僅允許在既有 Dashboard GET-only `/dashboard/system` 中以 read-only、"
    "synthetic local-only 方式顯示 v0.8.4-B 的 Worker dry-run result、audit trail、"
    "owner review event 與 readback summary artifacts；僅允許修改 app/main.py、"
    "templates/system.html、static/dashboard.css 與新增 v0.8.4-D validation script；"
    "不得新增 POST，不得新增 form/button/action URL，"
    "不得新增 approve/execute/dispatch/send controls，不得啟動 Worker，"
    "不得執行 Worker loop，不得執行任務，不得呼叫 OpenClaw，不得啟動或連接 Hermes，"
    "不得讀寫 Google Sheets，不得讀 real queue DB，不得寫 queue，不得讀 secrets，"
    "不得建立 webhook/endpoint/connector，不得建立 production/shared DB 或 "
    "Remote Blackboard API runtime。"
)

REQUIRED_CARD_HEADINGS = (
    "Future Dashboard read-only result card",
    "Future Dashboard read-only audit trail card",
    "Future Dashboard read-only owner review event card",
    "Future Dashboard read-only readback summary card",
)

REQUIRED_DISPLAY_LABELS = (
    "future permission flags display",
    "future runtime flags display",
    "future boundary notice display",
)

# Built from (prefix, suffix) pairs and joined at runtime so the *contiguous* phrase never
# appears literally in this script's own source (avoids this check self-tripping when it
# scans its own file as part of the combined-text scan below). Mirrors the v0.8.3-F/G and
# v0.8.4-A/B readiness scripts' UNSAFE_DONE_CLAIM_PARTS approach.
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
    ("v0.8.4-D", " started"),
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
    c4_tracked = is_tracked(C4_SCRIPT_REL)
    if not c4_tracked:
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


# Exact, plain-English check-label prefixes used across this whole series' readiness
# scripts for their own "does the target still hold, tolerating this round's own new
# untracked files" checks. Any failing line whose prefix (before its first parenthetical
# diagnostic) contains one of these markers is, by construction, never a content or
# safety-boundary check — only ever an untracked-file-cascade check. This is checked
# instead of parsing the nested "found [...]" path lists directly, because at 3+ levels
# of nesting (this script -> B4 -> A4 -> F) each layer's own `!r` repr of the inner
# stdout re-escapes quote characters (Python repr picks single- vs double-quote
# delimiters based on what's already inside the string, and escapes accordingly), so a
# naive quote-based parse silently mis-splits the nested content. Plain substring
# containment on this script's own un-escaped label text has no such failure mode.
KNOWN_TOLERANT_LABEL_MARKERS = (
    "no unexpected untracked files",
    "F validator runs with only acceptable Owner Review untracked-file observation or PASS",
    "PASS or only acceptable Owner Review untracked observation",
    "F validator runs and PASS 65/65",
)


def _line_is_known_untracked_cascade_failure(fail_line: str, own_file_fragments: tuple[str, ...]) -> bool:
    """A failure line is a tolerated cascade failure if (a) its own check label — the
    text before the first parenthetical diagnostic, never itself escaped/nested — is one
    of this series' known untracked-file-tolerance check names, and (b) this round's own
    new file basenames are still traceable somewhere in the line (at whatever nesting
    depth), confirming the failure really does implicate only this round's own files."""
    prefix = re.split(r"[（(]", fail_line, maxsplit=1)[0]
    label_ok = any(marker in prefix for marker in KNOWN_TOLERANT_LABEL_MARKERS)
    files_ok = all(fragment in fail_line for fragment in own_file_fragments)
    return label_ok and files_ok


def check_tolerant_pass(
    letter: str,
    label_base: str,
    run: subprocess.CompletedProcess[str],
    full_pass_marker: str,
    own_file_fragments: tuple[str, ...],
) -> None:
    """Accept full PASS, or a failure set where every failure (possibly nested through
    multiple inner tolerance checks) traces only to this round's new v0.8.4-C files
    tripping an untracked-files self-check — the same known Owner Review phase artifact
    documented in the v0.8.3-G and v0.8.4-A/B readiness scripts, extended to survive
    arbitrarily deep nesting."""
    stdout = run.stdout
    full_pass = run.returncode == 0 and full_pass_marker in stdout

    only_c4_untracked_fail = False
    if not full_pass and run.returncode == 1:
        fail_summary_lines = re.findall(r"^\s{3}-\s*(.+)$", stdout, flags=re.MULTILINE)
        only_c4_untracked_fail = bool(fail_summary_lines) and all(
            _line_is_known_untracked_cascade_failure(line, own_file_fragments) for line in fail_summary_lines
        )

    check(
        f"{letter}. {label_base}"
        if full_pass
        else (
            f"{letter}. {label_base} (accepted: every failure traces only to this round's "
            f"new v0.8.4-C files tripping an untracked-file check, directly or via a nested "
            f"tolerance check — an Owner Review phase artifact, not a content/safety-boundary "
            f"failure)"
            if only_c4_untracked_fail
            else f"{letter}. {label_base}（returncode={run.returncode}, stdout tail={stdout[-800:]!r}）"
        ),
        full_pass or only_c4_untracked_fail,
    )


def main() -> None:
    doc_text = read_text(C4_DOC_PATH)
    self_text = read_text(C4_SCRIPT_PATH)

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
    # [B] v0.8.4-C plan doc exists
    # -----------------------------------------------------------------
    print("[B] v0.8.4-C plan doc exists")
    check("B. v0.8.4-C plan doc exists", C4_DOC_PATH.is_file())

    # -----------------------------------------------------------------
    # [C] v0.8.4-C readiness script exists
    # -----------------------------------------------------------------
    print("[C] v0.8.4-C readiness script exists")
    check("C. v0.8.4-C readiness script exists", C4_SCRIPT_PATH.is_file())

    # -----------------------------------------------------------------
    # [D] plan doc is untracked in Owner Review phase
    # -----------------------------------------------------------------
    print("[D] plan doc is untracked in Owner Review phase")
    check(
        "D. plan doc is untracked in Owner Review phase",
        phase != "owner_review" or not is_tracked(C4_DOC_REL),
    )

    # -----------------------------------------------------------------
    # [E] readiness script is untracked in Owner Review phase
    # -----------------------------------------------------------------
    print("[E] readiness script is untracked in Owner Review phase")
    check(
        "E. readiness script is untracked in Owner Review phase",
        phase != "owner_review" or not is_tracked(C4_SCRIPT_REL),
    )

    # -----------------------------------------------------------------
    # [F] no tracked file is modified
    # -----------------------------------------------------------------
    print("[F] no tracked files modified")
    check(
        f"F. no tracked files modified（found {sorted(tracked_changed)}）"
        if tracked_changed
        else "F. no tracked files modified",
        not tracked_changed,
    )

    # -----------------------------------------------------------------
    # [G] untracked only v0.8.4-C doc, v0.8.4-C script, patches/*
    # -----------------------------------------------------------------
    print("[G] untracked only v0.8.4-C doc, v0.8.4-C script, patches/*")
    allowed_untracked = set(C4_ALL_FILES) if phase == "owner_review" else set()
    unexpected_untracked = {
        p for p in untracked if p not in allowed_untracked and not p.startswith("patches/")
    }
    check(
        f"G. no unexpected untracked files（found {sorted(unexpected_untracked)}）"
        if unexpected_untracked
        else "G. no unexpected untracked files",
        not unexpected_untracked,
    )

    # -----------------------------------------------------------------
    # [H]-[O] protected tracked files are not modified
    # -----------------------------------------------------------------
    def not_modified(*rels: str) -> bool:
        return all(rel not in tracked_changed for rel in rels)

    print("[H] app/main.py not modified")
    check("H. app/main.py not modified", not_modified(MAIN_PY_REL))

    print("[I] templates/system.html not modified")
    check("I. templates/system.html not modified", not_modified(SYSTEM_HTML_REL))

    print("[J] static/dashboard.css not modified")
    check("J. static/dashboard.css not modified", not_modified(DASHBOARD_CSS_REL))

    print("[K] v0.8.4-B doc/fixture/builder/readiness not modified")
    check(
        "K. v0.8.4-B doc/fixture/builder/readiness not modified",
        not_modified(B4_DOC_REL, B4_FIXTURE_REL, B4_BUILDER_REL, B4_SCRIPT_REL),
    )

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

    print("[O] P loader / V adapter / W/X/Y/Z / fixtures not modified")
    check(
        "O. P loader / V adapter / W/X/Y/Z / fixtures not modified",
        not_modified(P_LOADER_REL, V_ADAPTER_REL, OLD_FIXTURE_JSON_REL, *WXYZ_REL),
    )

    # -----------------------------------------------------------------
    # [P]-[AA] plan doc closeout / current-state content checks
    # -----------------------------------------------------------------
    print("[P] plan doc contains v0.8.4-A and v0.8.4-B DONE / PUSHED / CLOSED")
    check(
        "P. plan doc contains v0.8.4-A and v0.8.4-B DONE / PUSHED / CLOSED",
        "v0.8.4-A = DONE / PUSHED / CLOSED" in doc_text and "v0.8.4-B = DONE / PUSHED / CLOSED" in doc_text,
    )

    print("[Q] plan doc contains latest HEAD 6d6d3ed6153e13ce4f1b155bc11e1c5248427d12")
    check(
        "Q. plan doc contains latest HEAD 6d6d3ed6153e13ce4f1b155bc11e1c5248427d12",
        EXPECTED_BASE_HEAD in doc_text,
    )

    print("[R] plan doc says plan-only")
    check("R. plan doc says plan-only", "plan-only" in doc_text)

    print("[S] plan doc says existing /dashboard/system remains GET-only")
    check(
        "S. plan doc says existing /dashboard/system remains GET-only",
        "/dashboard/system" in doc_text and "GET-only" in doc_text,
    )

    print("[T] plan doc says result/audit model remains synthetic_local_only")
    check(
        "T. plan doc says result/audit model remains synthetic_local_only",
        "synthetic_local_only" in doc_text,
    )

    print("[U] plan doc says preview_only remains true")
    check(
        "U. plan doc says preview_only remains true",
        "`preview_only` remains `true`" in doc_text,
    )

    print("[V] plan doc says result_status remains preview_result_not_executed")
    check(
        "V. plan doc says result_status remains preview_result_not_executed",
        "`dry_run_result.result_status` remains `preview_result_not_executed`" in doc_text,
    )

    print("[W] plan doc says audit_status remains preview_audit_not_persisted")
    check(
        "W. plan doc says audit_status remains preview_audit_not_persisted",
        "`audit_trail_record.audit_status` remains `preview_audit_not_persisted`" in doc_text,
    )

    print("[X] plan doc says review_status remains owner_review_required")
    check(
        "X. plan doc says review_status remains owner_review_required",
        "`owner_review_event.review_status` remains `owner_review_required`" in doc_text,
    )

    print("[Y] plan doc says summary_status remains preview_readback_only")
    check(
        "Y. plan doc says summary_status remains preview_readback_only",
        "`readback_summary.summary_status` remains `preview_readback_only`" in doc_text,
    )

    print("[Z] plan doc says all permission flags false")
    check(
        "Z. plan doc says all permission flags false",
        "all permission flags remain false" in doc_text,
    )

    print("[AA] plan doc says all runtime flags false")
    check(
        "AA. plan doc says all runtime flags false",
        "all runtime flags remain false" in doc_text,
    )

    # -----------------------------------------------------------------
    # [AB]-[AD] future display / validation planning checks
    # -----------------------------------------------------------------
    print("[AB] plan doc defines future result card / audit card / review event card / readback summary card")
    missing_cards = [heading for heading in REQUIRED_CARD_HEADINGS if heading not in doc_text]
    check(
        f"AB. plan doc defines future result card / audit card / review event card / readback summary card（missing {missing_cards}）"
        if missing_cards
        else "AB. plan doc defines future result card / audit card / review event card / readback summary card",
        not missing_cards,
    )

    print("[AC] plan doc defines permission/runtime/boundary notice display")
    missing_display_labels = [label for label in REQUIRED_DISPLAY_LABELS if label not in doc_text]
    check(
        f"AC. plan doc defines permission/runtime/boundary notice display（missing {missing_display_labels}）"
        if missing_display_labels
        else "AC. plan doc defines permission/runtime/boundary notice display",
        not missing_display_labels,
    )

    print("[AD] plan doc defines validation hardening for committed Dashboard display")
    check(
        "AD. plan doc defines validation hardening for committed Dashboard display",
        "Future Validation Hardening for Committed Dashboard Display" in doc_text,
    )

    # -----------------------------------------------------------------
    # [AE] exact v0.8.4-D authorization phrase appears exactly once
    # -----------------------------------------------------------------
    print("[AE] plan doc contains future v0.8.4-D exact authorization phrase exactly once")
    phrase_count = doc_text.count(V0_8_4_D_AUTHORIZATION_PHRASE)
    check(
        f"AE. plan doc contains future v0.8.4-D exact authorization phrase exactly once（found {phrase_count}）"
        if phrase_count != 1
        else "AE. plan doc contains future v0.8.4-D exact authorization phrase exactly once",
        phrase_count == 1,
    )

    # -----------------------------------------------------------------
    # [AF]-[AH] v0.8.4-D boundary statement checks
    # -----------------------------------------------------------------
    print("[AF] plan doc says v0.8.4-D must not add POST / form / button / action URL")
    check(
        "AF. plan doc says v0.8.4-D must not add POST / form / button / action URL",
        "v0.8.4-D must not add POST" in doc_text and "v0.8.4-D must not add form/button/action URL" in doc_text,
    )

    print("[AG] plan doc says v0.8.4-D must not add approve/execute/dispatch/send controls")
    check(
        "AG. plan doc says v0.8.4-D must not add approve/execute/dispatch/send controls",
        "v0.8.4-D must not add approve/execute/dispatch/send controls" in doc_text,
    )

    print("[AH] plan doc says v0.8.4-D must not start Worker / call OpenClaw / activate Hermes / use Google Sheets / read or write real queue DB")
    check(
        "AH. plan doc says v0.8.4-D must not start Worker / call OpenClaw / activate Hermes / "
        "use Google Sheets / read or write real queue DB",
        "v0.8.4-D must not start a real Worker" in doc_text
        and "v0.8.4-D must not call OpenClaw" in doc_text
        and "v0.8.4-D must not activate Hermes" in doc_text
        and "v0.8.4-D must not read or write Google Sheets" in doc_text
        and "v0.8.4-D must not read or write real queue DB" in doc_text,
    )

    # -----------------------------------------------------------------
    # [AI] no unsafe done-claims (scan doc + this script's own source)
    # -----------------------------------------------------------------
    print("[AI] plan doc contains no unsafe done-claims")
    combined_text = doc_text + "\n" + self_text
    found_unsafe = [c for c in UNSAFE_DONE_CLAIMS if c in combined_text]
    check(
        f"AI. plan doc contains no unsafe done-claims（found {found_unsafe}）"
        if found_unsafe
        else "AI. plan doc contains no unsafe done-claims",
        not found_unsafe,
    )

    # -----------------------------------------------------------------
    # [AJ] v0.8.4-B builder output remains safe (direct import, read-only reference)
    # -----------------------------------------------------------------
    print("[AJ] v0.8.4-B builder output remains safe")
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
        f"AJ. v0.8.4-B builder output remains safe（error {b4_error}）" if not b4_ok else "AJ. v0.8.4-B builder output remains safe",
        b4_ok,
    )

    # -----------------------------------------------------------------
    # [AK] v0.8.4-B readiness PASS or only acceptable Owner Review untracked observation
    # -----------------------------------------------------------------
    print("[AK] v0.8.4-B readiness PASS or only acceptable Owner Review untracked observation")
    b4_run = run_reference_script(B4_SCRIPT_PATH)
    check_tolerant_pass(
        "AK",
        "v0.8.4-B readiness PASS or only acceptable Owner Review untracked observation",
        b4_run,
        full_pass_marker="PASS: v0.8.4-B worker dry-run result audit trail boundary implementation",
        own_file_fragments=C4_OWN_FILE_FRAGMENTS,
    )

    # -----------------------------------------------------------------
    # [AL] v0.8.4-A readiness PASS or only acceptable Owner Review untracked observation
    # -----------------------------------------------------------------
    print("[AL] v0.8.4-A readiness PASS or only acceptable Owner Review untracked observation")
    a4_run = run_reference_script(A4_SCRIPT_PATH)
    check_tolerant_pass(
        "AL",
        "v0.8.4-A readiness PASS or only acceptable Owner Review untracked observation",
        a4_run,
        full_pass_marker="PASS: v0.8.4-A worker dry-run result audit trail boundary plan",
        own_file_fragments=C4_OWN_FILE_FRAGMENTS,
    )

    # -----------------------------------------------------------------
    # [AM] v0.8.3-F validator PASS or only acceptable Owner Review untracked observation
    # -----------------------------------------------------------------
    print("[AM] v0.8.3-F validator PASS or only acceptable Owner Review untracked observation")
    f_run = run_reference_script(F_SCRIPT_PATH)
    check_tolerant_pass(
        "AM",
        "v0.8.3-F validator PASS or only acceptable Owner Review untracked observation",
        f_run,
        full_pass_marker="PASS: v0.8.3-F worker dry-run preview dashboard display validation hardening",
        own_file_fragments=C4_OWN_FILE_FRAGMENTS,
    )

    # -----------------------------------------------------------------
    # [AN] v0.8.3-B builder still all permission/runtime flags false
    # -----------------------------------------------------------------
    print("[AN] v0.8.3-B builder still all permission/runtime flags false")
    b3_module = load_module("worker_dry_run_preview_boundary_v0_8_3_b", B_BUILDER_PATH)
    b3_model = b3_module.build_worker_dry_run_preview_model()
    b3_permissions = b3_model.get("permissions", {})
    b3_runtime_state = b3_model.get("runtime_state", {})
    check(
        "AN. v0.8.3-B builder still all permission/runtime flags false",
        isinstance(b3_permissions, dict)
        and all(b3_permissions.get(key) is False for key in B3_PERMISSION_KEYS)
        and isinstance(b3_runtime_state, dict)
        and all(b3_runtime_state.get(key) is False for key in B3_RUNTIME_KEYS),
    )

    # -----------------------------------------------------------------
    # [AO] patches/ remains untracked
    # -----------------------------------------------------------------
    print("[AO] patches/ remains untracked")
    patches_tracked = git_lines(["ls-files", "--", "patches/"])
    check(
        f"AO. patches/ remains untracked（found tracked {patches_tracked}）"
        if patches_tracked
        else "AO. patches/ remains untracked",
        not patches_tracked,
    )

    # -----------------------------------------------------------------
    # [AP] no tag
    # -----------------------------------------------------------------
    print("[AP] no tag")
    tags_at_head = git_lines(["tag", "--points-at", "HEAD"])
    check(
        f"AP. no tag（found {tags_at_head}）" if tags_at_head else "AP. no tag",
        not tags_at_head,
    )

    # -----------------------------------------------------------------
    # 結果
    # -----------------------------------------------------------------
    total = len(PASS) + len(FAIL)
    print(f"\n合計：{len(PASS)}/{total} 通過")
    if FAIL:
        print(f"\nXX v0.8.4-C readiness 失敗 {len(FAIL)} 項：")
        for f in FAIL:
            print(f"   - {f}")
        sys.exit(1)
    else:
        print("PASS: v0.8.4-C worker dry-run result audit trail dashboard read-only display plan")
        sys.exit(0)


if __name__ == "__main__":
    main()
