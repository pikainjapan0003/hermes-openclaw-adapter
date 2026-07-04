"""v0.8.4-H readiness check: Owner Review Decision Boundary Addendum Plan.

Pure local filesystem + git metadata validation, standard library only. It reads the
v0.8.4-H plan doc and this script's own source directly from the working tree, and checks
that no existing tracked file was modified by this round.

Unlike earlier readiness scripts in this series, v0.8.4-H is a safety-addendum, plan-only
round with no builder and no fixture, so this script deliberately does *not* import any
application module, does not import any earlier builder module, does not re-run any other
script as a subprocess, and does not touch the queue, secrets, or the network. It is
file content / path / marker validation only. Its only subprocess use is read-only git
plumbing (rev-parse, status, diff, ls-files, tag, merge-base).
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
# v0.8.4-H (this round)
# -----------------------------------------------------------------------------------
H_DOC_REL = "docs/HERMES_OPENCLAW_OWNER_REVIEW_DECISION_BOUNDARY_ADDENDUM_PLAN_V0_8_4_H.md"
H_DOC_PATH = REPO_ROOT / H_DOC_REL

H_SCRIPT_REL = (
    "scripts/check_hermes_openclaw_owner_review_decision_boundary_addendum_plan_v0_8_4_h.py"
)
H_SCRIPT_PATH = REPO_ROOT / H_SCRIPT_REL

# -----------------------------------------------------------------------------------
# v0.8.4-A..G (this series)
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

# v0.8.4-G commit — HEAD at the start of this round.
EXPECTED_BASE_HEAD = "cd16c0157b55eb6901580eea20fd5d96f90afde3"
EXPECTED_COMMIT_MESSAGE = "docs: close out worker dry-run result dashboard display"

REQUIRED_SERIES_DONE_LINES = (
    "v0.8.4-A = DONE / PUSHED / CLOSED",
    "v0.8.4-B = DONE / PUSHED / CLOSED",
    "v0.8.4-C = DONE / PUSHED / CLOSED",
    "v0.8.4-D = DONE / PUSHED / VERIFIED / CLOSED",
    "v0.8.4-E = DONE / PUSHED / CLOSED",
    "v0.8.4-F = DONE / PUSHED / VERIFIED / CLOSED",
    "v0.8.4-G = DONE / PUSHED / CLOSED",
)

REQUIRED_BOUNDARY_STATEMENTS = (
    "Decision preview is not approval.",
    "Decision preview is not rejection.",
    "Decision preview is not execution.",
    "Decision preview is not dispatch.",
    "Decision preview is not a send action.",
    "Decision preview is not a queue write.",
    "Decision preview is not an audit trail write.",
    "`owner_review_required` is not Owner approval.",
    "Dry-run result preview is not actual execution result.",
    "Audit trail preview is not audit trail persistence.",
    "Readback summary preview is not Hermes activation.",
    "Owner reading the Dashboard is not Owner decision execution.",
    "v0.8.5 is reserved for the OpenClaw Mock Gateway.",
    "v0.8.4-H does not start v0.8.5.",
)

REQUIRED_PROHIBITION_STATEMENTS = (
    "v0.8.4-H does not add POST, form, button, action URL, approve control, reject\n"
    "  control, execute control, dispatch control, or send control.",
    "v0.8.4-H does not touch Worker, OpenClaw, Hermes, Google Sheets, the real queue DB,\n"
    "  webhook, endpoint, or connector.",
)

# Forbidden import-module prefixes for *this* script's own source — v0.8.4-H is a
# plan-only safety addendum, so its readiness script must stay a pure file/path/text
# checker with no application, queue, connector, or network surface. Checked via AST
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
# substring) — catches accidental secret-file/credential-store references without
# tripping on this script's own descriptive print/check labels. Assembled from parts at
# runtime so the denylist's own tuple literals never form the forbidden constant
# themselves (each part is its own separate AST string-constant node).
FORBIDDEN_STRING_CONSTANT_PARTS = (
    (".", "env"),
    (".", "env.local"),
    ("secrets", ".json"),
    ("credentials", ".json"),
)
FORBIDDEN_STRING_CONSTANTS = tuple(a + b for a, b in FORBIDDEN_STRING_CONSTANT_PARTS)

# Built from (prefix, suffix) pairs and joined at runtime so the *contiguous* phrase never
# appears literally in this script's own source (avoids this check self-tripping when it
# scans its own file as part of the combined-text scan below). Mirrors the earlier
# readiness scripts' UNSAFE_DONE_CLAIM_PARTS approach.
UNSAFE_DONE_CLAIM_PARTS = (
    ("Worker", " started"),
    ("Worker loop", " started"),
    ("task", " executed"),
    ("OpenClaw", " connected"),
    ("OpenClaw", " called"),
    ("Hermes", " connected"),
    ("Hermes", " called"),
    ("Hermes", " activated"),
    ("Google Sheets", " enabled"),
    ("real queue DB", " read"),
    ("queue", " written"),
    ("audit trail", " written"),
    ("POST", " enabled"),
    ("secrets", " read"),
    ("webhook", " created"),
    ("endpoint", " created"),
    ("connector", " created"),
    ("production DB", " created"),
    ("Remote Blackboard API runtime", " created"),
    ("decision", " approved"),
    ("decision", " executed"),
    ("decision", " dispatched"),
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
    h_tracked = is_tracked(H_SCRIPT_REL)
    if not h_tracked:
        return "owner_review"
    head = git_rev_parse("HEAD")
    origin = git_rev_parse("origin/master")
    if head != origin:
        return "post_commit_or_ahead"
    return "post_push_or_synced"


def main() -> None:
    doc_text = read_text(H_DOC_PATH)
    self_text = read_text(H_SCRIPT_PATH)

    tracked_changed = working_tree_change_names()
    untracked = untracked_names()

    phase = detect_phase()
    print(f"INFO: detected phase = {phase}")

    print("[A] current HEAD contains EXPECTED_BASE_HEAD in git history")
    is_ancestor = run_git(["merge-base", "--is-ancestor", EXPECTED_BASE_HEAD, "HEAD"]).returncode == 0
    check(f"A. HEAD contains {EXPECTED_BASE_HEAD} in git history", is_ancestor)

    print("[B] v0.8.4-H plan doc exists")
    check("B. v0.8.4-H plan doc exists", H_DOC_PATH.is_file())

    print("[C] v0.8.4-H readiness script exists")
    check("C. v0.8.4-H readiness script exists", H_SCRIPT_PATH.is_file())

    print("[D] plan doc is untracked in Owner Review phase")
    check(
        "D. plan doc is untracked in Owner Review phase",
        phase != "owner_review" or not is_tracked(H_DOC_REL),
    )

    print("[E] readiness script is untracked in Owner Review phase")
    check(
        "E. readiness script is untracked in Owner Review phase",
        phase != "owner_review" or not is_tracked(H_SCRIPT_REL),
    )

    print("[F] no tracked files modified")
    check(
        f"F. no tracked files modified（found {sorted(tracked_changed)}）"
        if tracked_changed
        else "F. no tracked files modified",
        not tracked_changed,
    )

    print("[G] untracked only v0.8.4-H doc, v0.8.4-H script, patches/*")
    allowed_untracked = {H_DOC_REL, H_SCRIPT_REL} if phase == "owner_review" else set()
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

    print("[K] v0.8.4-G/F/E/D/C/B/A artifacts not modified")
    check(
        "K. v0.8.4-G/F/E/D/C/B/A artifacts not modified",
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

    print("[N] v0.8.1 P loader / V adapter / W/X/Y/Z / fixtures not modified")
    check(
        "N. v0.8.1 P loader / V adapter / W/X/Y/Z / fixtures not modified",
        not_modified(P_LOADER_REL, V_ADAPTER_REL, OLD_FIXTURE_JSON_REL, V_SCRIPT_REL, *WXYZ_REL),
    )

    # -----------------------------------------------------------------
    print("[O] plan doc contains v0.8.4-H title")
    check(
        "O. plan doc contains v0.8.4-H title",
        "# Hermes × OpenClaw v0.8.4-H" in doc_text
        and "Owner Review Decision Boundary Addendum Plan" in doc_text,
    )

    print("[P] plan doc contains v0.8.4-A..G done/pushed/closed statuses")
    missing_done_lines = [line for line in REQUIRED_SERIES_DONE_LINES if line not in doc_text]
    check(
        f"P. plan doc contains v0.8.4-A..G done/pushed/closed statuses（missing {missing_done_lines}）"
        if missing_done_lines
        else "P. plan doc contains v0.8.4-A..G done/pushed/closed statuses",
        not missing_done_lines,
    )

    letters = ["Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "AA", "AB", "AC", "AD"]
    for letter, statement in zip(letters, REQUIRED_BOUNDARY_STATEMENTS):
        print(f"[{letter}] plan doc states: {statement}")
        check(f"{letter}. plan doc states: {statement}", statement in doc_text)

    print("[AE] plan doc prohibits POST/form/button/action URL/approve/reject/execute/dispatch/send controls")
    missing_prohibitions = [s for s in REQUIRED_PROHIBITION_STATEMENTS if s not in doc_text]
    check(
        "AE. plan doc prohibits POST/form/button/action URL/approve/reject/execute/dispatch/send controls"
        + (f"（missing {missing_prohibitions}）" if missing_prohibitions else ""),
        not missing_prohibitions,
    )

    print("[AF] plan doc contains no unsafe done-claims")
    combined_text = doc_text + "\n" + self_text

    def is_unsafe_claim_present(claim: str, text: str) -> bool:
        return bool(re.search(r"(?<![Nn]o )(?<![Dd]oes not )" + re.escape(claim), text))

    found_unsafe = [c for c in UNSAFE_DONE_CLAIMS if is_unsafe_claim_present(c, combined_text)]
    check(
        f"AF. plan doc contains no unsafe done-claims（found {found_unsafe}）"
        if found_unsafe
        else "AF. plan doc contains no unsafe done-claims",
        not found_unsafe,
    )

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

    print("[AG] readiness script contains no forbidden application/connector/network imports")
    forbidden_imports = [
        m for m in imported_modules
        if any(m == p or m.startswith(p + ".") for p in FORBIDDEN_IMPORT_MODULE_PREFIXES)
    ]
    check(
        f"AG. readiness script contains no forbidden application/connector/network imports（found {forbidden_imports}）"
        if forbidden_imports
        else "AG. readiness script contains no forbidden application/connector/network imports",
        not forbidden_imports,
    )

    print("[AH] readiness script does not reference secrets/.env files")
    forbidden_constants_found = [s for s in string_constants if s in FORBIDDEN_STRING_CONSTANTS]
    check(
        f"AH. readiness script does not reference secrets/.env files（found {forbidden_constants_found}）"
        if forbidden_constants_found or "os" in imported_modules
        else "AH. readiness script does not reference secrets/.env files",
        not forbidden_constants_found and "os" not in imported_modules,
    )

    print("[AI] readiness script only invokes read-only git plumbing as subprocess")
    self_subprocess_targets = re.findall(r'subprocess\.run\(\s*\[\s*"([^"]+)"', self_text)
    check(
        f"AI. readiness script only invokes read-only git plumbing as subprocess（found {self_subprocess_targets}）"
        if any(t != "git" for t in self_subprocess_targets)
        else "AI. readiness script only invokes read-only git plumbing as subprocess",
        all(t == "git" for t in self_subprocess_targets),
    )

    # -----------------------------------------------------------------
    print("[AJ] patches/ remains untracked")
    patches_tracked = git_lines(["ls-files", "--", "patches/"])
    check(
        f"AJ. patches/ remains untracked（found tracked {patches_tracked}）"
        if patches_tracked
        else "AJ. patches/ remains untracked",
        not patches_tracked,
    )

    print("[AK] no tag")
    tags_at_head = git_lines(["tag", "--points-at", "HEAD"])
    check(
        f"AK. no tag（found {tags_at_head}）" if tags_at_head else "AK. no tag",
        not tags_at_head,
    )

    # -----------------------------------------------------------------
    total = len(PASS) + len(FAIL)
    print(f"\n合計：{len(PASS)}/{total} 通過")
    if FAIL:
        print(f"\nXX v0.8.4-H readiness 失敗 {len(FAIL)} 項：")
        for f in FAIL:
            print(f"   - {f}")
        sys.exit(1)
    else:
        print("PASS: v0.8.4-H owner review decision boundary addendum plan")
        sys.exit(0)


if __name__ == "__main__":
    main()
