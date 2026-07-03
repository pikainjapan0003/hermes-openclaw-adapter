"""v0.8.3-G readiness check: Worker Dry-run Preview Dashboard Display Closeout Report.

Pure local filesystem + git metadata validation, standard library only. It reads the
v0.8.3-G closeout report doc and this script's own source directly from the working tree,
checks that no existing tracked file was modified by this round, and re-runs two existing
read-only reference checks (the v0.8.3-F validator as a subprocess, and the v0.8.3-B
standalone builder via direct import) purely to confirm the series still stands.

It does NOT modify any file, does NOT start a server, sends no POST, makes no network call,
reads no secrets, reads no real queue DB, writes no queue, and does not call
Worker/OpenClaw/Hermes/Google Sheets. Its only subprocess use is invoking the current Python
interpreter on the existing v0.8.3-F validator script (a read-only check already used
elsewhere in this series); its only git usage is read-only plumbing (rev-parse, status,
diff, ls-files, log, merge-base, tag).
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

G_DOC_REL = (
    "docs/HERMES_OPENCLAW_WORKER_DRY_RUN_PREVIEW_DASHBOARD_DISPLAY_CLOSEOUT_REPORT_V0_8_3_G.md"
)
G_DOC_PATH = REPO_ROOT / G_DOC_REL

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

# v0.8.3-F commit — the base this round starts from (HEAD == origin/master at round start).
EXPECTED_BASE_HEAD = "c6cf83330cd4468a3d78667dcc503539bd4db440"

REQUIRED_PERMISSION_LINES = (
    "execution_permission = false",
    "dispatch_permission = false",
    "external_side_effects_permission = false",
)

REQUIRED_RUNTIME_LINES = (
    "worker_started = false",
    "worker_loop_started = false",
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

REQUIRED_SERIES_DONE_LINES = tuple(f"v0.8.3-{letter} = DONE / PUSHED / CLOSED" for letter in "ABCDEF")

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

# Built from (prefix, suffix) pairs and joined at runtime so the *contiguous* phrase never
# appears literally in this script's own source (avoids this check self-tripping when it
# scans its own file as part of the combined-text scan below). Mirrors the v0.8.3-F
# readiness script's UNSAFE_DONE_CLAIM_PARTS approach.
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
    ("v0.8.4", " started"),
    ("tag", " created"),
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


def load_b_builder():
    spec = importlib.util.spec_from_file_location("worker_dry_run_preview_boundary_v0_8_3_b", B_BUILDER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    g_doc_text = read_text(G_DOC_PATH)
    self_text = read_text(G_SCRIPT_PATH)

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
    # [B] G report exists
    # -----------------------------------------------------------------
    print("[B] G report exists")
    check("B. G report exists", G_DOC_PATH.is_file())

    # -----------------------------------------------------------------
    # [C] G readiness script exists
    # -----------------------------------------------------------------
    print("[C] G readiness script exists")
    check("C. G readiness script exists", G_SCRIPT_PATH.is_file())

    # -----------------------------------------------------------------
    # [D] G report is untracked in Owner Review phase
    # -----------------------------------------------------------------
    print("[D] G report is untracked in Owner Review phase")
    check(
        "D. G report is untracked in Owner Review phase",
        phase != "owner_review" or not is_tracked(G_DOC_REL),
    )

    # -----------------------------------------------------------------
    # [E] G readiness script is untracked in Owner Review phase
    # -----------------------------------------------------------------
    print("[E] G readiness script is untracked in Owner Review phase")
    check(
        "E. G readiness script is untracked in Owner Review phase",
        phase != "owner_review" or not is_tracked(G_SCRIPT_REL),
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
    # [G] untracked only G report, G script, patches/*
    # -----------------------------------------------------------------
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

    # -----------------------------------------------------------------
    # [H]-[N] protected tracked files are not modified
    # -----------------------------------------------------------------
    def not_modified(*rels: str) -> bool:
        return all(rel not in tracked_changed for rel in rels)

    print("[H] app/main.py not modified")
    check("H. app/main.py not modified", not_modified(MAIN_PY_REL))

    print("[I] templates/system.html not modified")
    check("I. templates/system.html not modified", not_modified(SYSTEM_HTML_REL))

    print("[J] static/dashboard.css not modified")
    check("J. static/dashboard.css not modified", not_modified(DASHBOARD_CSS_REL))

    print("[K] F validator not modified")
    check("K. F validator not modified", not_modified(F_SCRIPT_REL))

    print("[L] E/D/C/B/A v0.8.3 artifacts not modified")
    check(
        "L. E/D/C/B/A v0.8.3 artifacts not modified",
        not_modified(
            E_DOC_REL, E_SCRIPT_REL, D_SCRIPT_REL, C_DOC_REL, C_SCRIPT_REL,
            B_DOC_REL, B_FIXTURE_REL, B_BUILDER_REL, B_SCRIPT_REL, A_DOC_REL, A_SCRIPT_REL,
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
    # [O]-[Z], [AA] G report content checks — read committed report text directly
    # -----------------------------------------------------------------
    print("[O] G report contains all v0.8.3 A-F DONE / PUSHED / CLOSED lines")
    missing_done_lines = [line for line in REQUIRED_SERIES_DONE_LINES if line not in g_doc_text]
    check(
        f"O. G report contains all v0.8.3 A-F DONE / PUSHED / CLOSED lines（missing {missing_done_lines}）"
        if missing_done_lines
        else "O. G report contains all v0.8.3 A-F DONE / PUSHED / CLOSED lines",
        not missing_done_lines,
    )

    print("[P] G report contains HEAD c6cf83330cd4468a3d78667dcc503539bd4db440")
    check(
        "P. G report contains HEAD c6cf83330cd4468a3d78667dcc503539bd4db440",
        EXPECTED_BASE_HEAD in g_doc_text,
    )

    print("[Q] G report contains Dashboard GET-only /dashboard/system")
    check(
        "Q. G report contains Dashboard GET-only /dashboard/system",
        "GET-only" in g_doc_text and "/dashboard/system" in g_doc_text,
    )

    print("[R] G report contains read-only Worker dry-run preview")
    check(
        "R. G report contains read-only Worker dry-run preview",
        "read-only" in g_doc_text and "Worker dry-run preview" in g_doc_text,
    )

    print("[S] G report contains synthetic_local_only")
    check("S. G report contains synthetic_local_only", "synthetic_local_only" in g_doc_text)

    print("[T] G report contains preview_only_not_executed")
    check("T. G report contains preview_only_not_executed", "preview_only_not_executed" in g_doc_text)

    print("[U] G report contains all permission flags false")
    missing_perm_lines = [line for line in REQUIRED_PERMISSION_LINES if line not in g_doc_text]
    check(
        f"U. G report contains all permission flags false（missing {missing_perm_lines}）"
        if missing_perm_lines
        else "U. G report contains all permission flags false",
        not missing_perm_lines,
    )

    print("[V] G report contains all runtime flags false")
    missing_runtime_lines = [line for line in REQUIRED_RUNTIME_LINES if line not in g_doc_text]
    check(
        f"V. G report contains all runtime flags false（missing {missing_runtime_lines}）"
        if missing_runtime_lines
        else "V. G report contains all runtime flags false",
        not missing_runtime_lines,
    )

    print("[W] G report contains F validator PASS 65/65")
    check(
        "W. G report contains F validator PASS 65/65",
        "PASS 65/65" in g_doc_text,
    )

    print("[X] G report contains full regression PASS")
    check(
        "X. G report contains full regression PASS",
        "full regression suite: PASS" in g_doc_text,
    )

    print("[Y] G report contains no unsafe done-claims")
    combined_text = g_doc_text + "\n" + self_text
    found_unsafe = [c for c in UNSAFE_DONE_CLAIMS if c in combined_text]
    check(
        f"Y. G report contains no unsafe done-claims（found {found_unsafe}）"
        if found_unsafe
        else "Y. G report contains no unsafe done-claims",
        not found_unsafe,
    )

    print("[Z] G report contains recommended next phase v0.8.4 Worker Dry-run Result / Audit Trail Boundary Plan")
    check(
        "Z. G report contains recommended next phase v0.8.4 Worker Dry-run Result / Audit Trail Boundary Plan",
        "Recommended next phase" in g_doc_text
        and "v0.8.4" in g_doc_text
        and "Worker Dry-run Result / Audit Trail Boundary Plan" in g_doc_text,
    )

    print("[AA] G report states v0.8.4 should not start real Worker")
    check(
        "AA. G report states v0.8.4 should not start real Worker",
        "v0.8.4 does not start a real Worker" in g_doc_text,
    )

    # -----------------------------------------------------------------
    # [AB] F validator runs and PASS 65/65 (invokes the existing, unmodified script)
    #
    # Known Owner Review phase artifact: the F validator's own untracked-files check ([E])
    # was written before this round existed, so during Owner Review it has no way to know
    # this round's new G report/script are expected. If the *only* F failure is its [E]
    # check, and the only untracked paths it names are this round's own G report/script,
    # that is this round's untracked-file footprint tripping an older script's strict
    # untracked-file check — not a Dashboard content or safety-boundary regression. Any
    # other F failure (content, safety, or a different/extra untracked path) still fails
    # this check.
    # -----------------------------------------------------------------
    print("[AB] F validator runs and PASS 65/65")
    f_run = subprocess.run(
        [sys.executable, str(F_SCRIPT_PATH)],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    f_stdout = f_run.stdout
    f_full_pass = f_run.returncode == 0 and "65/65" in f_stdout and "PASS: v0.8.3-F" in f_stdout

    f_only_g_untracked_fail = False
    if not f_full_pass and f_run.returncode == 1:
        fail_summary_lines = re.findall(r"^\s{3}-\s*(.+)$", f_stdout, flags=re.MULTILINE)
        e_found_match = re.search(r"E\. no unexpected untracked files（found (\[[^\]]*\])）", f_stdout)
        if (
            "64/65" in f_stdout
            and len(fail_summary_lines) == 1
            and fail_summary_lines[0].startswith("E. no unexpected untracked files")
            and e_found_match
        ):
            found_paths = set(re.findall(r"'([^']*)'", e_found_match.group(1)))
            f_only_g_untracked_fail = bool(found_paths) and found_paths <= {G_DOC_REL, G_SCRIPT_REL}

    check(
        "AB. F validator runs and PASS 65/65"
        if f_full_pass
        else (
            "AB. F validator runs and PASS 65/65 (accepted: F failed only its own "
            "untracked-file check, tripped solely by this round's new G report/script — "
            "an Owner Review phase artifact, not a content/safety-boundary failure)"
            if f_only_g_untracked_fail
            else f"AB. F validator runs and PASS 65/65（returncode={f_run.returncode}, "
            f"stdout tail={f_stdout[-800:]!r}）"
        ),
        f_full_pass or f_only_g_untracked_fail,
    )

    # -----------------------------------------------------------------
    # [AC] B builder local preview all flags false (direct import, read-only reference)
    # -----------------------------------------------------------------
    print("[AC] B builder local preview all flags false")
    b_module = load_b_builder()
    model = b_module.build_worker_dry_run_preview_model()
    permissions = model.get("permissions", {})
    runtime_state = model.get("runtime_state", {})
    check(
        "AC. B builder local preview all flags false",
        isinstance(permissions, dict)
        and all(permissions.get(key) is False for key in REQUIRED_PERMISSION_KEYS)
        and isinstance(runtime_state, dict)
        and all(runtime_state.get(key) is False for key in REQUIRED_RUNTIME_KEYS),
    )

    # -----------------------------------------------------------------
    # [AD] patches/ remains untracked
    # -----------------------------------------------------------------
    print("[AD] patches/ remains untracked")
    patches_tracked = git_lines(["ls-files", "--", "patches/"])
    check(
        f"AD. patches/ remains untracked（found tracked {patches_tracked}）"
        if patches_tracked
        else "AD. patches/ remains untracked",
        not patches_tracked,
    )

    # -----------------------------------------------------------------
    # [AE] no tag
    # -----------------------------------------------------------------
    print("[AE] no tag")
    tags_at_head = git_lines(["tag", "--points-at", "HEAD"])
    check(
        f"AE. no tag（found {tags_at_head}）" if tags_at_head else "AE. no tag",
        not tags_at_head,
    )

    # -----------------------------------------------------------------
    # 結果
    # -----------------------------------------------------------------
    total = len(PASS) + len(FAIL)
    print(f"\n合計：{len(PASS)}/{total} 通過")
    if FAIL:
        print(f"\nXX v0.8.3-G readiness 失敗 {len(FAIL)} 項：")
        for f in FAIL:
            print(f"   - {f}")
        sys.exit(1)
    else:
        print("PASS: v0.8.3-G worker dry-run preview dashboard display closeout report")
        sys.exit(0)


if __name__ == "__main__":
    main()
