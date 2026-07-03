"""v0.8.4-A readiness check: Worker Dry-run Result / Audit Trail Boundary Plan.

Pure local filesystem + git metadata validation, standard library only. It reads the
v0.8.4-A plan doc and this script's own source directly from the working tree, checks that
no existing tracked file was modified by this round, and re-runs two existing read-only
reference checks (the v0.8.3-F validator as a subprocess, and the v0.8.3-B standalone
builder via direct import) purely to confirm the underlying series still stands.

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

A4_DOC_REL = (
    "docs/HERMES_OPENCLAW_WORKER_DRY_RUN_RESULT_AUDIT_TRAIL_BOUNDARY_PLAN_V0_8_4_A.md"
)
A4_DOC_PATH = REPO_ROOT / A4_DOC_REL

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

# v0.8.3-G commit — the base this round starts from (HEAD == origin/master at round start).
EXPECTED_BASE_HEAD = "dca6393e0d400266d6725298831394013eb3b0f1"

REQUIRED_SERIES_DONE_LINES = tuple(f"v0.8.3-{letter} = DONE / PUSHED / CLOSED" for letter in "ABCDEFG")

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

# The future v0.8.4-B exact Owner authorization phrase (must appear exactly once).
V0_8_4_B_AUTHORIZATION_PHRASE = (
    "批准實作 v0.8.4-B — Worker Dry-run Result / Audit Trail Boundary Implementation，"
    "僅允許新增 synthetic local-only 的 Worker dry-run result、audit trail、owner review "
    "event 與 readback summary artifacts，用於描述 preview-only result boundary；"
    "不得啟動 Worker，不得執行 Worker loop，不得執行任務，不得呼叫 OpenClaw，"
    "不得啟動或連接 Hermes，不得讀寫 Google Sheets，不得讀 real queue DB，不得寫 queue，"
    "不得新增 POST，不得新增 form/button/action URL，不得讀 secrets，"
    "不得建立 webhook/endpoint/connector，不得建立 production/shared DB 或 "
    "Remote Blackboard API runtime。"
)

REQUIRED_BOUNDARY_SECTION_HEADINGS = (
    "Future Dry-run Result Object Shape",
    "Future Audit Trail Record Shape",
    "Future Owner Review Event Shape",
    "Future Readback Summary Shape",
    "Future Synthetic Local-only Fixture Boundary",
    "Future Validation Boundary",
    "Future Dashboard Display Boundary",
)

# Built from (prefix, suffix) pairs and joined at runtime so the *contiguous* phrase never
# appears literally in this script's own source (avoids this check self-tripping when it
# scans its own file as part of the combined-text scan below). Mirrors the v0.8.3-F/G
# readiness scripts' UNSAFE_DONE_CLAIM_PARTS approach.
UNSAFE_DONE_CLAIM_PARTS = (
    ("Worker", " started"),
    ("Worker loop", " started"),
    ("OpenClaw", " connected"),
    ("OpenClaw", " called"),
    ("Hermes", " connected"),
    ("Hermes", " called"),
    ("Google Sheets", " enabled"),
    ("real queue DB", " read"),
    ("queue", " written"),
    ("POST", " enabled"),
    ("task", " executed"),
    ("dispatch", " sent"),
    ("webhook", " created"),
    ("endpoint", " created"),
    ("connector", " created"),
    ("production DB", " created"),
    ("Remote Blackboard API runtime", " created"),
    ("v0.8.4-B", " started"),
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
    a4_tracked = is_tracked(A4_SCRIPT_REL)
    if not a4_tracked:
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
    doc_text = read_text(A4_DOC_PATH)
    self_text = read_text(A4_SCRIPT_PATH)

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
    # [B] v0.8.4-A plan doc exists
    # -----------------------------------------------------------------
    print("[B] v0.8.4-A plan doc exists")
    check("B. v0.8.4-A plan doc exists", A4_DOC_PATH.is_file())

    # -----------------------------------------------------------------
    # [C] v0.8.4-A readiness script exists
    # -----------------------------------------------------------------
    print("[C] v0.8.4-A readiness script exists")
    check("C. v0.8.4-A readiness script exists", A4_SCRIPT_PATH.is_file())

    # -----------------------------------------------------------------
    # [D] plan doc is untracked in Owner Review phase
    # -----------------------------------------------------------------
    print("[D] plan doc is untracked in Owner Review phase")
    check(
        "D. plan doc is untracked in Owner Review phase",
        phase != "owner_review" or not is_tracked(A4_DOC_REL),
    )

    # -----------------------------------------------------------------
    # [E] readiness script is untracked in Owner Review phase
    # -----------------------------------------------------------------
    print("[E] readiness script is untracked in Owner Review phase")
    check(
        "E. readiness script is untracked in Owner Review phase",
        phase != "owner_review" or not is_tracked(A4_SCRIPT_REL),
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
    # [G] untracked only v0.8.4-A doc, v0.8.4-A script, patches/*
    # -----------------------------------------------------------------
    print("[G] untracked only v0.8.4-A doc, v0.8.4-A script, patches/*")
    allowed_untracked = {A4_DOC_REL, A4_SCRIPT_REL} if phase == "owner_review" else set()
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

    print("[K] v0.8.3-G report/readiness not modified")
    check("K. v0.8.3-G report/readiness not modified", not_modified(G_DOC_REL, G_SCRIPT_REL))

    print("[L] v0.8.3-F validator not modified")
    check("L. v0.8.3-F validator not modified", not_modified(F_SCRIPT_REL))

    print("[M] v0.8.3-E/D/C/B/A artifacts not modified")
    check(
        "M. v0.8.3-E/D/C/B/A artifacts not modified",
        not_modified(
            E_DOC_REL, E_SCRIPT_REL, D_SCRIPT_REL, C_DOC_REL, C_SCRIPT_REL,
            B_DOC_REL, B_FIXTURE_REL, B_BUILDER_REL, B_SCRIPT_REL, A_DOC_REL, A_SCRIPT_REL,
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
    # [P]-[X] plan doc closeout / current-state content checks
    # -----------------------------------------------------------------
    print("[P] plan doc contains v0.8.3-A through v0.8.3-G DONE / PUSHED / CLOSED")
    missing_done_lines = [line for line in REQUIRED_SERIES_DONE_LINES if line not in doc_text]
    check(
        f"P. plan doc contains v0.8.3-A through v0.8.3-G DONE / PUSHED / CLOSED（missing {missing_done_lines}）"
        if missing_done_lines
        else "P. plan doc contains v0.8.3-A through v0.8.3-G DONE / PUSHED / CLOSED",
        not missing_done_lines,
    )

    print("[Q] plan doc contains latest HEAD dca6393e0d400266d6725298831394013eb3b0f1")
    check(
        "Q. plan doc contains latest HEAD dca6393e0d400266d6725298831394013eb3b0f1",
        EXPECTED_BASE_HEAD in doc_text,
    )

    print("[R] plan doc says plan-only")
    check("R. plan doc says plan-only", "plan-only" in doc_text)

    print("[S] plan doc says Dashboard display remains read-only")
    check(
        "S. plan doc says Dashboard display remains read-only",
        "Dashboard display" in doc_text and "read-only" in doc_text,
    )

    print("[T] plan doc says source remains synthetic_local_only")
    check("T. plan doc says source remains synthetic_local_only", "synthetic_local_only" in doc_text)

    print("[U] plan doc says dry_run_status remains preview_only_not_executed")
    check(
        "U. plan doc says dry_run_status remains preview_only_not_executed",
        "preview_only_not_executed" in doc_text,
    )

    print("[V] plan doc says owner_review_required remains true")
    check(
        "V. plan doc says owner_review_required remains true",
        "owner_review_required" in doc_text and "remains true" in doc_text,
    )

    print("[W] plan doc says all permission flags false")
    check(
        "W. plan doc says all permission flags false",
        "all permission flags on the current model remain false" in doc_text,
    )

    print("[X] plan doc says all runtime flags false")
    check(
        "X. plan doc says all runtime flags false",
        "all runtime flags on the current model remain false" in doc_text,
    )

    # -----------------------------------------------------------------
    # [Y]-[AE] future shape / boundary section checks
    # -----------------------------------------------------------------
    letters = ["Y", "Z", "AA", "AB", "AC", "AD", "AE"]
    for letter, heading in zip(letters, REQUIRED_BOUNDARY_SECTION_HEADINGS):
        print(f"[{letter}] plan doc defines {heading}")
        check(f"{letter}. plan doc defines {heading}", heading in doc_text)

    # -----------------------------------------------------------------
    # [AF] exact v0.8.4-B authorization phrase appears exactly once
    # -----------------------------------------------------------------
    print("[AF] plan doc contains the future v0.8.4-B exact authorization phrase exactly once")
    phrase_count = doc_text.count(V0_8_4_B_AUTHORIZATION_PHRASE)
    check(
        f"AF. plan doc contains the future v0.8.4-B exact authorization phrase exactly once（found {phrase_count}）"
        if phrase_count != 1
        else "AF. plan doc contains the future v0.8.4-B exact authorization phrase exactly once",
        phrase_count == 1,
    )

    # -----------------------------------------------------------------
    # [AG]-[AI] v0.8.4-B boundary statement checks
    # -----------------------------------------------------------------
    print("[AG] plan doc says v0.8.4-B must not start real Worker")
    check(
        "AG. plan doc says v0.8.4-B must not start real Worker",
        "v0.8.4-B must not start a real Worker" in doc_text,
    )

    print("[AH] plan doc says v0.8.4-B must not execute tasks")
    check(
        "AH. plan doc says v0.8.4-B must not execute tasks",
        "v0.8.4-B must not execute any task" in doc_text,
    )

    print("[AI] plan doc says v0.8.4-B must not call OpenClaw / Hermes / Google Sheets")
    check(
        "AI. plan doc says v0.8.4-B must not call OpenClaw / Hermes / Google Sheets",
        "v0.8.4-B must not call OpenClaw" in doc_text
        and "v0.8.4-B must not activate Hermes" in doc_text
        and "v0.8.4-B must not read or write Google Sheets" in doc_text,
    )

    # -----------------------------------------------------------------
    # [AJ] no unsafe done-claims (scan doc + this script's own source)
    # -----------------------------------------------------------------
    print("[AJ] plan doc contains no unsafe done-claims")
    combined_text = doc_text + "\n" + self_text
    found_unsafe = [c for c in UNSAFE_DONE_CLAIMS if c in combined_text]
    check(
        f"AJ. plan doc contains no unsafe done-claims（found {found_unsafe}）"
        if found_unsafe
        else "AJ. plan doc contains no unsafe done-claims",
        not found_unsafe,
    )

    # -----------------------------------------------------------------
    # [AK] F validator runs with only acceptable Owner Review untracked-file
    # observation, or full PASS.
    #
    # Known Owner Review phase artifact: the F validator's own untracked-files check
    # predates this round, so it has no way to know this round's new v0.8.4-A plan
    # doc/script are expected. If the *only* F failure is its untracked-files check, and
    # the only untracked paths it names are this round's own plan doc/script, that is
    # this round's untracked-file footprint tripping an older script's strict
    # untracked-file check — not a Dashboard content or safety-boundary regression. Any
    # other F failure (content, safety, or a different/extra untracked path) still fails
    # this check.
    # -----------------------------------------------------------------
    print("[AK] F validator runs with only acceptable Owner Review untracked-file observation or PASS")
    f_run = subprocess.run(
        [sys.executable, str(F_SCRIPT_PATH)],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    f_stdout = f_run.stdout
    f_full_pass = f_run.returncode == 0 and "65/65" in f_stdout and "PASS: v0.8.3-F" in f_stdout

    f_only_a4_untracked_fail = False
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
            f_only_a4_untracked_fail = bool(found_paths) and found_paths <= {A4_DOC_REL, A4_SCRIPT_REL}

    check(
        "AK. F validator runs with only acceptable Owner Review untracked-file observation or PASS"
        if f_full_pass
        else (
            "AK. F validator runs with only acceptable Owner Review untracked-file "
            "observation or PASS (accepted: F failed only its own untracked-file check, "
            "tripped solely by this round's new v0.8.4-A plan doc/script — an Owner "
            "Review phase artifact, not a content/safety-boundary failure)"
            if f_only_a4_untracked_fail
            else f"AK. F validator runs with only acceptable Owner Review untracked-file "
            f"observation or PASS（returncode={f_run.returncode}, stdout tail={f_stdout[-800:]!r}）"
        ),
        f_full_pass or f_only_a4_untracked_fail,
    )

    # -----------------------------------------------------------------
    # [AL] B builder local preview all permission/runtime flags false
    # -----------------------------------------------------------------
    print("[AL] B builder local preview all permission/runtime flags false")
    b_module = load_b_builder()
    model = b_module.build_worker_dry_run_preview_model()
    permissions = model.get("permissions", {})
    runtime_state = model.get("runtime_state", {})
    check(
        "AL. B builder local preview all permission/runtime flags false",
        isinstance(permissions, dict)
        and all(permissions.get(key) is False for key in REQUIRED_PERMISSION_KEYS)
        and isinstance(runtime_state, dict)
        and all(runtime_state.get(key) is False for key in REQUIRED_RUNTIME_KEYS),
    )

    # -----------------------------------------------------------------
    # [AM] patches/ remains untracked
    # -----------------------------------------------------------------
    print("[AM] patches/ remains untracked")
    patches_tracked = git_lines(["ls-files", "--", "patches/"])
    check(
        f"AM. patches/ remains untracked（found tracked {patches_tracked}）"
        if patches_tracked
        else "AM. patches/ remains untracked",
        not patches_tracked,
    )

    # -----------------------------------------------------------------
    # [AN] no tag
    # -----------------------------------------------------------------
    print("[AN] no tag")
    tags_at_head = git_lines(["tag", "--points-at", "HEAD"])
    check(
        f"AN. no tag（found {tags_at_head}）" if tags_at_head else "AN. no tag",
        not tags_at_head,
    )

    # -----------------------------------------------------------------
    # 結果
    # -----------------------------------------------------------------
    total = len(PASS) + len(FAIL)
    print(f"\n合計：{len(PASS)}/{total} 通過")
    if FAIL:
        print(f"\nXX v0.8.4-A readiness 失敗 {len(FAIL)} 項：")
        for f in FAIL:
            print(f"   - {f}")
        sys.exit(1)
    else:
        print("PASS: v0.8.4-A worker dry-run result audit trail boundary plan")
        sys.exit(0)


if __name__ == "__main__":
    main()
