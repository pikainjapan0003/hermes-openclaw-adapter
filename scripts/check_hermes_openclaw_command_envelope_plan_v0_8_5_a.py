"""v0.8.5-A readiness check: OpenClaw Command Envelope Plan.

Pure local filesystem + git metadata validation, standard library only. It reads the
v0.8.5-A plan doc and this script's own source directly from the working tree, and checks
that no existing tracked file was modified by this round.

v0.8.5-A is a plan-only round with no builder and no fixture, so this script does *not*
import any application module, does not import any earlier builder module, does not
re-run any other script as a subprocess, and does not touch the queue, secrets, or the
network. It is file content / path / marker validation only. Its only subprocess use is
read-only git plumbing (rev-parse, status, diff, ls-files, tag, merge-base).
"""
from __future__ import annotations

import ast
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

MAIN_PY_REL = "app/main.py"
SYSTEM_HTML_REL = "templates/system.html"
DASHBOARD_CSS_REL = "static/dashboard.css"

# -----------------------------------------------------------------------------------
# v0.8.5-A (this round)
# -----------------------------------------------------------------------------------
A5_DOC_REL = "docs/HERMES_OPENCLAW_COMMAND_ENVELOPE_PLAN_V0_8_5_A.md"
A5_DOC_PATH = REPO_ROOT / A5_DOC_REL

A5_SCRIPT_REL = "scripts/check_hermes_openclaw_command_envelope_plan_v0_8_5_a.py"
A5_SCRIPT_PATH = REPO_ROOT / A5_SCRIPT_REL

# -----------------------------------------------------------------------------------
# v0.8.4-A..I (prior series)
# -----------------------------------------------------------------------------------
A_DOC_REL = "docs/HERMES_OPENCLAW_WORKER_DRY_RUN_RESULT_AUDIT_TRAIL_BOUNDARY_PLAN_V0_8_4_A.md"
A_SCRIPT_REL = "scripts/check_hermes_openclaw_worker_dry_run_result_audit_trail_boundary_plan_v0_8_4_a.py"

B_DOC_REL = "docs/HERMES_OPENCLAW_WORKER_DRY_RUN_RESULT_AUDIT_TRAIL_BOUNDARY_IMPLEMENTATION_V0_8_4_B.md"
B_FIXTURE_REL = "fixtures/local_mock_data/hermes_openclaw_worker_dry_run_result_audit_trail_v0_8_4_b.json"
B_BUILDER_REL = "scripts/worker_dry_run_result_audit_trail_boundary_v0_8_4_b.py"
B_SCRIPT_REL = "scripts/check_hermes_openclaw_worker_dry_run_result_audit_trail_boundary_implementation_v0_8_4_b.py"

C_DOC_REL = "docs/HERMES_OPENCLAW_WORKER_DRY_RUN_RESULT_AUDIT_TRAIL_DASHBOARD_READ_ONLY_DISPLAY_PLAN_V0_8_4_C.md"
C_SCRIPT_REL = "scripts/check_hermes_openclaw_worker_dry_run_result_audit_trail_dashboard_read_only_display_plan_v0_8_4_c.py"

D_SCRIPT_REL = "scripts/check_hermes_openclaw_worker_dry_run_result_audit_trail_dashboard_read_only_display_implementation_v0_8_4_d.py"

E_DOC_REL = (
    "docs/HERMES_OPENCLAW_WORKER_DRY_RUN_RESULT_AUDIT_TRAIL_DASHBOARD_DISPLAY_"
    "CLOSEOUT_VALIDATION_HARDENING_PLAN_V0_8_4_E.md"
)
E_SCRIPT_REL = (
    "scripts/check_hermes_openclaw_worker_dry_run_result_audit_trail_dashboard_"
    "display_closeout_validation_hardening_plan_v0_8_4_e.py"
)

F_SCRIPT_REL = (
    "scripts/check_hermes_openclaw_worker_dry_run_result_audit_trail_dashboard_"
    "display_validation_hardening_v0_8_4_f.py"
)

G_DOC_REL = (
    "docs/HERMES_OPENCLAW_WORKER_DRY_RUN_RESULT_AUDIT_TRAIL_DASHBOARD_DISPLAY_"
    "CLOSEOUT_REPORT_V0_8_4_G.md"
)
G_SCRIPT_REL = (
    "scripts/check_hermes_openclaw_worker_dry_run_result_audit_trail_dashboard_"
    "display_closeout_report_v0_8_4_g.py"
)

H_DOC_REL = "docs/HERMES_OPENCLAW_OWNER_REVIEW_DECISION_BOUNDARY_ADDENDUM_PLAN_V0_8_4_H.md"
H_SCRIPT_REL = (
    "scripts/check_hermes_openclaw_owner_review_decision_boundary_addendum_plan_v0_8_4_h.py"
)

I_DOC_REL = "docs/HERMES_OPENCLAW_ROADMAP_AMENDMENT_FINAL_CLOSEOUT_ADDENDUM_V0_8_4_I.md"
I_SCRIPT_REL = (
    "scripts/check_hermes_openclaw_roadmap_amendment_final_closeout_addendum_v0_8_4_i.py"
)

# -----------------------------------------------------------------------------------
# v0.8.3-A..G
# -----------------------------------------------------------------------------------
V083_A_DOC_REL = "docs/HERMES_OPENCLAW_WORKER_DRY_RUN_PREVIEW_BOUNDARY_PLAN_V0_8_3_A.md"
V083_A_SCRIPT_REL = "scripts/check_hermes_openclaw_worker_dry_run_preview_boundary_plan_v0_8_3_a.py"

V083_B_DOC_REL = "docs/HERMES_OPENCLAW_WORKER_DRY_RUN_PREVIEW_BOUNDARY_IMPLEMENTATION_V0_8_3_B.md"
V083_B_FIXTURE_REL = "fixtures/local_mock_data/hermes_openclaw_worker_dry_run_preview_v0_8_3_b.json"
V083_B_BUILDER_REL = "scripts/worker_dry_run_preview_boundary_v0_8_3_b.py"
V083_B_SCRIPT_REL = "scripts/check_hermes_openclaw_worker_dry_run_preview_boundary_implementation_v0_8_3_b.py"

V083_C_DOC_REL = "docs/HERMES_OPENCLAW_WORKER_DRY_RUN_PREVIEW_DASHBOARD_READ_ONLY_DISPLAY_PLAN_V0_8_3_C.md"
V083_C_SCRIPT_REL = "scripts/check_hermes_openclaw_worker_dry_run_preview_dashboard_read_only_display_plan_v0_8_3_c.py"

V083_D_SCRIPT_REL = "scripts/check_hermes_openclaw_worker_dry_run_preview_dashboard_read_only_display_implementation_v0_8_3_d.py"

V083_E_DOC_REL = "docs/HERMES_OPENCLAW_WORKER_DRY_RUN_PREVIEW_DASHBOARD_DISPLAY_CLOSEOUT_VALIDATION_HARDENING_PLAN_V0_8_3_E.md"
V083_E_SCRIPT_REL = "scripts/check_hermes_openclaw_worker_dry_run_preview_dashboard_display_closeout_validation_hardening_plan_v0_8_3_e.py"

V083_F_SCRIPT_REL = "scripts/check_hermes_openclaw_worker_dry_run_preview_dashboard_display_validation_hardening_v0_8_3_f.py"

V083_G_DOC_REL = "docs/HERMES_OPENCLAW_WORKER_DRY_RUN_PREVIEW_DASHBOARD_DISPLAY_CLOSEOUT_REPORT_V0_8_3_G.md"
V083_G_SCRIPT_REL = "scripts/check_hermes_openclaw_worker_dry_run_preview_dashboard_display_closeout_report_v0_8_3_g.py"

# -----------------------------------------------------------------------------------
# v0.8.2-A..F
# -----------------------------------------------------------------------------------
V082_F_DOC_REL = "docs/HERMES_OPENCLAW_DASHBOARD_READ_ONLY_PREVIEW_VALIDATION_CLOSEOUT_HANDOFF_PLAN_V0_8_2_F.md"
V082_F_SCRIPT_REL = "scripts/check_hermes_openclaw_dashboard_read_only_preview_validation_closeout_handoff_plan_v0_8_2_f.py"

V082_E_SCRIPT_REL = "scripts/check_hermes_openclaw_dashboard_read_only_preview_ui_validation_hardening_v0_8_2_e.py"

V082_D_DOC_REL = "docs/HERMES_OPENCLAW_DASHBOARD_READ_ONLY_PREVIEW_UI_VALIDATION_HARDENING_PLAN_V0_8_2_D.md"
V082_D_SCRIPT_REL = "scripts/check_hermes_openclaw_dashboard_read_only_preview_ui_validation_hardening_plan_v0_8_2_d.py"

V082_C_SCRIPT_REL = "scripts/check_hermes_openclaw_dashboard_read_only_preview_ui_refinement_v0_8_2_c.py"

V082_B_DOC_REL = "docs/HERMES_OPENCLAW_DASHBOARD_READ_ONLY_PREVIEW_UI_REFINEMENT_PLAN_V0_8_2_B.md"
V082_B_SCRIPT_REL = "scripts/check_hermes_openclaw_dashboard_read_only_preview_ui_refinement_plan_v0_8_2_b.py"

V082_A_SCRIPT_REL = (
    "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_"
    "read_only_display_integration_v0_8_2_a.py"
)

# -----------------------------------------------------------------------------------
# v0.8.1 P loader / V adapter / W/X/Y/Z / fixtures
# -----------------------------------------------------------------------------------
P_LOADER_REL = "scripts/load_local_mock_fixture_preview_v0_8_1.py"
V_ADAPTER_REL = "scripts/local_mock_fixture_dashboard_preview_adapter_v0_8_1.py"
OLD_FIXTURE_JSON_REL = "fixtures/local_mock_data/hermes_openclaw_local_mock_messages_v0_8_1.json"

V_SCRIPT_REL = "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_v0_8_1_v.py"

WXYZ_REL = {
    "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_runtime_check_v0_8_1_w.py",
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_DASHBOARD_PREVIEW_ADAPTER_INTEGRATION_BOUNDARY_PLAN_V0_8_1_X.md",
    "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_integration_boundary_plan_v0_8_1_x.py",
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_DASHBOARD_PREVIEW_ADAPTER_INTEGRATION_AUTHORIZATION_PLAN_V0_8_1_Y.md",
    "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_integration_authorization_plan_v0_8_1_y.py",
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_DASHBOARD_PREVIEW_ADAPTER_INTEGRATION_IMPLEMENTATION_PLAN_V0_8_1_Z.md",
    "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_integration_implementation_plan_v0_8_1_z.py",
}

# v0.8.4-I commit — HEAD at the start of this round.
EXPECTED_BASE_HEAD = "7d9030c071ecc3fa9f75b13e2348005beaa465f5"

REQUIRED_TEXT_MARKERS = (
    "v0.8.5-A",
    "OpenClaw Command Envelope Plan",
    "v0.8.4-A through v0.8.4-I = DONE / PUSHED / CLOSED",
    EXPECTED_BASE_HEAD,
    "v0.8.5 is reserved for the OpenClaw Mock Gateway",
    "`command_id`",
    "`task_id`",
    "`tool_target`",
    "`requested_action`",
    "`risk_level`",
    "`approval_snapshot`",
    "`execution_mode`",
    "`dry_run`",
    "`mock_only`",
    "`external_touchpoints`",
    "`rollback_plan`",
    "`external_side_effects_allowed`",
    "`mock_only` must always be `true`.",
    "`dry_run` must always be `true`.",
    "`external_side_effects_allowed` must always be `false`.",
    "A command envelope is not a call to real OpenClaw.",
    "A command envelope is not a call to Worker.",
    "A command envelope is not a call to Hermes.",
    "A command envelope does not touch Google Sheets.",
    "A command envelope does not read or write the real queue DB.",
    "A command envelope does not write the audit trail.",
    "A command envelope does not add a Dashboard control.",
    "A command envelope is not an execution.",
    "A command envelope is not a dispatch.",
    "v0.8.5-A does not implement the OpenClaw Mock Gateway Helper.",
    "v0.8.5-A does not start v0.8.5-B.",
)

# Forbidden import-module prefixes for *this* script's own source. Checked via AST
# import-node inspection (not a raw substring scan), so this denylist can name the
# actual module fragments without the check tripping on its own source text.
FORBIDDEN_IMPORT_MODULE_PREFIXES = (
    "app",
    "worker",
    "openclaw",
    "hermes",
    "google",
    "googleapiclient",
    "requests",
    "socket",
    "urllib",
    "http",
)

# String constants forbidden anywhere in this script's own AST (exact match, not
# substring). Assembled from parts at runtime so the denylist's own tuple literals
# never form the forbidden constant themselves.
FORBIDDEN_STRING_CONSTANT_PARTS = (
    (".", "env"),
    (".", "env.local"),
    ("secrets", ".json"),
    ("credentials", ".json"),
)
FORBIDDEN_STRING_CONSTANTS = tuple(a + b for a, b in FORBIDDEN_STRING_CONSTANT_PARTS)

# Built from (prefix, suffix) pairs and joined at runtime so the *contiguous* phrase never
# appears literally in this script's own source (avoids this check self-tripping when it
# scans its own file as part of the combined-text scan below).
UNSAFE_DONE_CLAIM_PARTS = (
    ("Worker", " called"),
    ("real OpenClaw", " called"),
    ("OpenClaw", " called"),
    ("Hermes", " called"),
    ("Google Sheets", " enabled"),
    ("real queue DB", " read"),
    ("queue", " written"),
    ("audit trail", " written"),
    ("Dashboard control", " added"),
    ("command envelope", " executed"),
    ("command envelope", " dispatched"),
    ("mock gateway helper", " created"),
    ("secrets", " read"),
    ("webhook", " created"),
    ("endpoint", " created"),
    ("connector", " created"),
    ("production DB", " created"),
    ("Remote Blackboard API runtime", " created"),
    ("v0.8.5-B", " started"),
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
    a5_tracked = is_tracked(A5_SCRIPT_REL)
    if not a5_tracked:
        return "owner_review"
    head = git_rev_parse("HEAD")
    origin = git_rev_parse("origin/master")
    if head != origin:
        return "post_commit_or_ahead"
    return "post_push_or_synced"


def main() -> None:
    doc_text = read_text(A5_DOC_PATH)
    self_text = read_text(A5_SCRIPT_PATH)

    tracked_changed = working_tree_change_names()
    untracked = untracked_names()

    phase = detect_phase()
    print(f"INFO: detected phase = {phase}")

    print("[A] current HEAD contains EXPECTED_BASE_HEAD in git history")
    is_ancestor = run_git(["merge-base", "--is-ancestor", EXPECTED_BASE_HEAD, "HEAD"]).returncode == 0
    check(f"A. HEAD contains {EXPECTED_BASE_HEAD} in git history", is_ancestor)

    print("[B] v0.8.5-A plan doc exists")
    check("B. v0.8.5-A plan doc exists", A5_DOC_PATH.is_file())

    print("[C] v0.8.5-A readiness script exists")
    check("C. v0.8.5-A readiness script exists", A5_SCRIPT_PATH.is_file())

    print("[D] plan doc is untracked in Owner Review phase")
    check(
        "D. plan doc is untracked in Owner Review phase",
        phase != "owner_review" or not is_tracked(A5_DOC_REL),
    )

    print("[E] readiness script is untracked in Owner Review phase")
    check(
        "E. readiness script is untracked in Owner Review phase",
        phase != "owner_review" or not is_tracked(A5_SCRIPT_REL),
    )

    print("[F] no tracked files modified")
    check(
        f"F. no tracked files modified（found {sorted(tracked_changed)}）"
        if tracked_changed
        else "F. no tracked files modified",
        not tracked_changed,
    )

    print("[G] untracked only v0.8.5-A doc, v0.8.5-A script, patches/*")
    allowed_untracked = {A5_DOC_REL, A5_SCRIPT_REL} if phase == "owner_review" else set()
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

    print("[K] v0.8.4-I/H artifacts not modified")
    check(
        "K. v0.8.4-I/H artifacts not modified",
        not_modified(I_DOC_REL, I_SCRIPT_REL, H_DOC_REL, H_SCRIPT_REL),
    )

    print("[L] v0.8.4-G/F/E/D/C/B/A artifacts not modified")
    check(
        "L. v0.8.4-G/F/E/D/C/B/A artifacts not modified",
        not_modified(
            G_DOC_REL, G_SCRIPT_REL,
            F_SCRIPT_REL,
            E_DOC_REL, E_SCRIPT_REL,
            D_SCRIPT_REL,
            C_DOC_REL, C_SCRIPT_REL,
            B_DOC_REL, B_FIXTURE_REL, B_BUILDER_REL, B_SCRIPT_REL,
            A_DOC_REL, A_SCRIPT_REL,
        ),
    )

    print("[M] v0.8.3-G/F/E/D/C/B/A artifacts not modified")
    check(
        "M. v0.8.3-G/F/E/D/C/B/A artifacts not modified",
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

    print("[N] v0.8.2 artifacts not modified")
    check(
        "N. v0.8.2 artifacts not modified",
        not_modified(
            V082_F_DOC_REL, V082_F_SCRIPT_REL,
            V082_E_SCRIPT_REL,
            V082_D_DOC_REL, V082_D_SCRIPT_REL,
            V082_C_SCRIPT_REL,
            V082_B_DOC_REL, V082_B_SCRIPT_REL,
            V082_A_SCRIPT_REL,
        ),
    )

    print("[O] v0.8.1 P loader / V adapter / W/X/Y/Z / fixtures not modified")
    check(
        "O. v0.8.1 P loader / V adapter / W/X/Y/Z / fixtures not modified",
        not_modified(P_LOADER_REL, V_ADAPTER_REL, OLD_FIXTURE_JSON_REL, V_SCRIPT_REL, *WXYZ_REL),
    )

    # -----------------------------------------------------------------
    letters = [
        "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",
        "AA", "AB", "AC", "AD", "AE", "AF", "AG", "AH", "AI", "AJ",
        "AK", "AL", "AM", "AN", "AO", "AP", "AQ", "AR", "AS", "AT",
    ]
    for letter, marker in zip(letters, REQUIRED_TEXT_MARKERS):
        print(f"[{letter}] plan doc contains: {marker}")
        check(f"{letter}. plan doc contains: {marker}", marker in doc_text)

    print("[AU] plan doc contains no unsafe done-claims")
    combined_text = doc_text + "\n" + self_text

    def is_unsafe_claim_present(claim: str, text: str) -> bool:
        return bool(re.search(r"(?<![Nn]o )(?<![Dd]oes not )(?<![Ii]s not )" + re.escape(claim), text))

    found_unsafe = [c for c in UNSAFE_DONE_CLAIMS if is_unsafe_claim_present(c, combined_text)]
    check(
        f"AU. plan doc contains no unsafe done-claims（found {found_unsafe}）"
        if found_unsafe
        else "AU. plan doc contains no unsafe done-claims",
        not found_unsafe,
    )

    # -----------------------------------------------------------------
    try:
        self_tree = ast.parse(self_text)
    except SyntaxError:
        self_tree = None

    imported_modules: list[str] = []
    string_constants: list[str] = []
    if self_tree is not None:
        for node in ast.walk(self_tree):
            if isinstance(node, ast.Import):
                imported_modules.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_modules.append(node.module)
            elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                string_constants.append(node.value)

    print("[AV] readiness script contains no forbidden application/connector/network imports")
    forbidden_imports = [
        m for m in imported_modules
        if any(m == p or m.startswith(p + ".") for p in FORBIDDEN_IMPORT_MODULE_PREFIXES)
    ]
    check(
        f"AV. readiness script contains no forbidden application/connector/network imports（found {forbidden_imports}）"
        if forbidden_imports
        else "AV. readiness script contains no forbidden application/connector/network imports",
        not forbidden_imports,
    )

    print("[AW] readiness script does not reference secrets/.env files")
    forbidden_constants_found = [s for s in string_constants if s in FORBIDDEN_STRING_CONSTANTS]
    check(
        f"AW. readiness script does not reference secrets/.env files（found {forbidden_constants_found}）"
        if forbidden_constants_found or "os" in imported_modules
        else "AW. readiness script does not reference secrets/.env files",
        not forbidden_constants_found and "os" not in imported_modules,
    )

    print("[AX] readiness script only invokes read-only git plumbing as subprocess")
    self_subprocess_targets = re.findall(r'subprocess\.run\(\s*\[\s*"([^"]+)"', self_text)
    check(
        f"AX. readiness script only invokes read-only git plumbing as subprocess（found {self_subprocess_targets}）"
        if any(t != "git" for t in self_subprocess_targets)
        else "AX. readiness script only invokes read-only git plumbing as subprocess",
        all(t == "git" for t in self_subprocess_targets),
    )

    # -----------------------------------------------------------------
    print("[AY] patches/ remains untracked")
    patches_tracked = git_lines(["ls-files", "--", "patches/"])
    check(
        f"AY. patches/ remains untracked（found tracked {patches_tracked}）"
        if patches_tracked
        else "AY. patches/ remains untracked",
        not patches_tracked,
    )

    print("[AZ] no tag")
    tags_at_head = git_lines(["tag", "--points-at", "HEAD"])
    check(
        f"AZ. no tag（found {tags_at_head}）" if tags_at_head else "AZ. no tag",
        not tags_at_head,
    )

    # -----------------------------------------------------------------
    total = len(PASS) + len(FAIL)
    print(f"\n合計：{len(PASS)}/{total} 通過")
    if FAIL:
        print(f"\nXX v0.8.5-A readiness 失敗 {len(FAIL)} 項：")
        for f in FAIL:
            print(f"   - {f}")
        sys.exit(1)
    else:
        print("PASS: v0.8.5-A openclaw command envelope plan")
        sys.exit(0)


if __name__ == "__main__":
    main()
