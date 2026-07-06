"""v1.0-RC-R readiness check: Full Blackboard Loop Rehearsal Closeout.

Local filesystem + git metadata validation, standard library only. Does NOT import
app.main, Hermes runtime, Worker runtime, OpenClaw runtime, or any connector runtime
module. Does not call network, does not read secrets, does not read connector data,
does not write the queue, audit trail, or Blackboard, and does not modify any file.
Its only subprocess use is read-only git plumbing (status, diff, ls-files, tag).
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

MAIN_PY_REL = "app/main.py"
SYSTEM_HTML_REL = "templates/system.html"
DASHBOARD_CSS_REL = "static/dashboard.css"
RESULT_FEEDBACK_PREVIEW_REL = "app/result_feedback_preview.py"
ADAPTER_REL = "app/full_loop_preview_adapter.py"
FIXTURE_D_REL = "fixtures/local_mock_data/hermes_full_blackboard_loop_rehearsal_v1_0_rc_d.json"
CLAUDE_MD_REL = "CLAUDE.md"
PATCHES_REL = "patches/"
FIXTURES_DIR_REL = "fixtures/local_mock_data/"

DOC_REL = "docs/HERMES_FULL_BLACKBOARD_LOOP_REHEARSAL_CLOSEOUT_V1_0_RC_R.md"
DOC_PATH = REPO_ROOT / DOC_REL

SELF_SCRIPT_REL = "scripts/check_hermes_full_blackboard_loop_rehearsal_closeout_v1_0_rc_r.py"
SELF_SCRIPT_PATH = REPO_ROOT / SELF_SCRIPT_REL

ALLOWED_STAGED_FILES = {DOC_REL, SELF_SCRIPT_REL}

FORBIDDEN_UNTOUCHED_FILES = (
    MAIN_PY_REL,
    SYSTEM_HTML_REL,
    DASHBOARD_CSS_REL,
    RESULT_FEEDBACK_PREVIEW_REL,
    ADAPTER_REL,
    FIXTURE_D_REL,
    CLAUDE_MD_REL,
)

RC_ARTIFACT_PATHS = (
    "docs/HERMES_FULL_BLACKBOARD_LOOP_REHEARSAL_PLAN_V1_0_RC.md",
    "scripts/check_hermes_full_blackboard_loop_rehearsal_plan_v1_0_rc.py",
    "docs/HERMES_SYNTHETIC_FULL_LOOP_FIXTURE_PLAN_V1_0_RC_A.md",
    "scripts/check_hermes_synthetic_full_loop_fixture_plan_v1_0_rc_a.py",
    "docs/HERMES_FULL_LOOP_PREVIEW_ADAPTER_PLAN_V1_0_RC_B.md",
    "scripts/check_hermes_full_loop_preview_adapter_plan_v1_0_rc_b.py",
    "docs/HERMES_FULL_LOOP_TIMELINE_DISPLAY_PLAN_V1_0_RC_C.md",
    "scripts/check_hermes_full_loop_timeline_display_plan_v1_0_rc_c.py",
    "docs/HERMES_FULL_LOOP_READ_ONLY_REHEARSAL_IMPLEMENTATION_V1_0_RC_D.md",
    "scripts/check_hermes_full_loop_read_only_rehearsal_implementation_v1_0_rc_d.py",
    FIXTURE_D_REL,
    ADAPTER_REL,
    "docs/HERMES_FULL_LOOP_OWNER_REVIEW_SAFETY_MATRIX_V1_0_RC_E.md",
    "scripts/check_hermes_full_loop_owner_review_safety_matrix_v1_0_rc_e.py",
)

REQUIRED_PHASE_TITLE = "v1.0-RC-R Full Blackboard Loop Rehearsal Closeout"

REQUIRED_SEQUENCE_LABELS = (
    "v1.0-RC Full Blackboard Loop Rehearsal Plan",
    "v1.0-RC-A Synthetic Full Loop Fixture Plan",
    "v1.0-RC-B Full Loop Preview Adapter Plan",
    "v1.0-RC-C Full Loop Timeline Display Plan",
    "v1.0-RC-D Full Loop Read-only Rehearsal Implementation",
    "v1.0-RC-E Owner Review / Safety Matrix Check",
)

REQUIRED_COMMIT_HASHES = (
    "12831bcb3cc2ca786c6d322330365c2b5f41b78e",
    "b477314d618eca6386d9c0ea669f50b2efd0e884",
    "8ef7fc5062cf375e192f7952b09ba47edcb9f417",
    "553e5edaa3e1e403f72af8925be45b604d9bb993",
    "5d632e781cc71715213dd5173b313a485927e4ce",
    "5c6f125866a7b4043f05cc67972321056497a931",
)

REQUIRED_SECTION_HEADINGS = (
    "v1.0-RC-D Implementation Summary",
    "Artifacts Created Across v1.0-RC",
    "Final v1.0-RC Safety Conclusion",
    "Dashboard Conclusion",
    "Owner Approval Boundary",
    "Hermes / Worker / OpenClaw Boundary",
    "Result / Follow-up Boundary",
    "Fable 5 Planning Handoff Note",
    "Explicitly Not Started",
    "Final Hard Boundary",
)

REQUIRED_DOC_SUBSTRINGS = (
    "v1.0-RC-R is docs / check-only closeout.",
    "No real Full Blackboard Loop is implemented in this phase.",
    "No Blackboard write occurs in this phase.",
    "No queue write occurs in this phase.",
    "No audit trail write occurs in this phase.",
    "No Worker dispatch occurs in this phase.",
    "No OpenClaw call occurs in this phase.",
    "No Hermes runtime activation occurs in this phase.",
    "No connector call occurs in this phase.",
    "No Dashboard controls are added in this phase.",
    "No external side effects occur in this phase.",
    "/dashboard/system remains GET-only.",
    "No fixture, preview adapter, Dashboard files, or app/main.py are modified in this phase.",
    "Fable 5 handoff prompt is not written in this phase.",
    "v1.0 and v1.0-A are not started in this phase.",
    "Fable 5 must not be instructed to directly modify code or activate runtime unless separately authorized by Owner.",
    "Ask ChatGPT to draft: Fable 5 Hermes",
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
    return subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args],
        capture_output=True,
        text=True,
    )


def git_lines(args: list[str]) -> list[str]:
    out = run_git(args)
    return [line for line in out.stdout.splitlines() if line.strip()]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def main() -> None:
    doc_text = read_text(DOC_PATH)
    self_text = read_text(SELF_SCRIPT_PATH)
    main_py_text = read_text(REPO_ROOT / MAIN_PY_REL)

    print("[A] v1.0-RC-R closeout doc exists")
    check("A. v1.0-RC-R closeout doc exists", DOC_PATH.is_file())

    print("[B] v1.0-RC-R readiness script exists")
    check("B. v1.0-RC-R readiness script exists", SELF_SCRIPT_PATH.is_file())

    print("[C] doc contains exact phase title")
    check("C. doc contains exact phase title", REQUIRED_PHASE_TITLE in doc_text)

    print("[D] doc contains all required safety/closeout substrings")
    missing_substrings = [s for s in REQUIRED_DOC_SUBSTRINGS if s not in doc_text]
    check(
        f"D. doc contains all required safety/closeout substrings（missing {missing_substrings}）"
        if missing_substrings
        else "D. doc contains all required safety/closeout substrings",
        not missing_substrings,
    )

    print("[E] doc defines required section headings")
    missing_headings = [h for h in REQUIRED_SECTION_HEADINGS if h not in doc_text]
    check(
        f"E. doc defines required section headings（missing {missing_headings}）"
        if missing_headings
        else "E. doc defines required section headings",
        not missing_headings,
    )

    print("[F] doc lists completed v1.0-RC sequence")
    missing_labels = [label for label in REQUIRED_SEQUENCE_LABELS if label not in doc_text]
    check(
        f"F. doc lists completed v1.0-RC sequence（missing {missing_labels}）"
        if missing_labels
        else "F. doc lists completed v1.0-RC sequence",
        not missing_labels,
    )

    print("[G] doc lists v1.0-RC sequence commit hashes")
    missing_hashes = [h for h in REQUIRED_COMMIT_HASHES if h not in doc_text]
    check(
        f"G. doc lists v1.0-RC sequence commit hashes（missing {missing_hashes}）"
        if missing_hashes
        else "G. doc lists v1.0-RC sequence commit hashes",
        not missing_hashes,
    )

    print("[H] doc lists all v1.0-RC artifacts")
    missing_artifacts_in_doc = [p for p in RC_ARTIFACT_PATHS if p not in doc_text]
    check(
        f"H. doc lists all v1.0-RC artifacts（missing {missing_artifacts_in_doc}）"
        if missing_artifacts_in_doc
        else "H. doc lists all v1.0-RC artifacts",
        not missing_artifacts_in_doc,
    )

    print("[I] all v1.0-RC artifacts (A-E) actually exist on disk")
    missing_artifact_files = [p for p in RC_ARTIFACT_PATHS if not (REPO_ROOT / p).is_file()]
    check(
        f"I. all v1.0-RC artifacts (A-E) actually exist on disk（missing {missing_artifact_files}）"
        if missing_artifact_files
        else "I. all v1.0-RC artifacts (A-E) actually exist on disk",
        not missing_artifact_files,
    )

    print("[J] doc includes safe next recommendation")
    check("J. doc includes safe next recommendation", "Safe Next Recommendation" in doc_text)

    print("[K] existing /dashboard/system remains GET-only")
    get_count = len(re.findall(r'@app\.get\("/dashboard/system"', main_py_text))
    post_count = len(re.findall(r'@app\.post\("/dashboard/system"', main_py_text))
    check(
        f"K. existing /dashboard/system remains GET-only（get_count={get_count}, post_count={post_count}）"
        if (get_count != 1 or post_count != 0)
        else "K. existing /dashboard/system remains GET-only",
        get_count == 1 and post_count == 0,
    )

    print("[L] no new route/endpoint/webhook/callback receiver added (working+staged diff)")
    working_diff_main_py = "\n".join(git_lines(["diff", "--", MAIN_PY_REL]))
    staged_diff_main_py = "\n".join(git_lines(["diff", "--cached", "--", MAIN_PY_REL]))
    combined_main_py_diff = working_diff_main_py + "\n" + staged_diff_main_py
    added_route_decorators = re.findall(
        r'^\+\s*@app\.(get|post|put|delete|patch)\(', combined_main_py_diff, flags=re.MULTILINE
    )
    check(
        f"L. no new route/endpoint/webhook/callback receiver added (working+staged diff)（found {added_route_decorators}）"
        if added_route_decorators
        else "L. no new route/endpoint/webhook/callback receiver added (working+staged diff)",
        not added_route_decorators,
    )

    print("[M] only allowed v1.0-RC-R files are staged")
    staged_files = set(git_lines(["diff", "--cached", "--name-only"]))
    unexpected_staged = sorted(staged_files - ALLOWED_STAGED_FILES)
    check(
        f"M. only allowed v1.0-RC-R files are staged（unexpected {unexpected_staged}）"
        if unexpected_staged
        else "M. only allowed v1.0-RC-R files are staged",
        not unexpected_staged,
    )

    print("[N] patches/ is not staged")
    staged_patches = [f for f in staged_files if f.startswith(PATCHES_REL)]
    check(
        f"N. patches/ is not staged（found {staged_patches}）" if staged_patches else "N. patches/ is not staged",
        not staged_patches,
    )

    print("[O] CLAUDE.md is not staged")
    check("O. CLAUDE.md is not staged", CLAUDE_MD_REL not in staged_files)

    print("[P] fixtures/local_mock_data/ is not staged")
    staged_fixtures_dir = [f for f in staged_files if f.startswith(FIXTURES_DIR_REL)]
    check(
        f"P. fixtures/local_mock_data/ is not staged（found {staged_fixtures_dir}）"
        if staged_fixtures_dir
        else "P. fixtures/local_mock_data/ is not staged",
        not staged_fixtures_dir,
    )

    print("[Q] app/full_loop_preview_adapter.py is not staged")
    check("Q. app/full_loop_preview_adapter.py is not staged", ADAPTER_REL not in staged_files)

    print("[R] app/main.py is not staged")
    check("R. app/main.py is not staged", MAIN_PY_REL not in staged_files)

    print("[S] templates/system.html is not staged")
    check("S. templates/system.html is not staged", SYSTEM_HTML_REL not in staged_files)

    print("[T] static/dashboard.css is not staged")
    check("T. static/dashboard.css is not staged", DASHBOARD_CSS_REL not in staged_files)

    print("[U] app/result_feedback_preview.py is not staged")
    check("U. app/result_feedback_preview.py is not staged", RESULT_FEEDBACK_PREVIEW_REL not in staged_files)

    print("[V] no forbidden runtime file is staged (outside allowed set)")
    runtime_path_markers = ("connector", "webhook", "endpoint", "callback_receiver", "worker.py", "openclaw", "hermes_runtime")
    suspicious_staged = sorted(
        f for f in staged_files
        if f not in ALLOWED_STAGED_FILES and any(marker in f.lower() for marker in runtime_path_markers)
    )
    check(
        f"V. no forbidden runtime file is staged (outside allowed set)（found {suspicious_staged}）"
        if suspicious_staged
        else "V. no forbidden runtime file is staged (outside allowed set)",
        not suspicious_staged,
    )

    print("[W] no v1.0-RC-D/E reviewed file appears in working or staged diff (untouched)")
    working_diff_files = set(git_lines(["diff", "--name-only"]))
    touched_reviewed = sorted((working_diff_files | staged_files) & set(FORBIDDEN_UNTOUCHED_FILES))
    check(
        f"W. no v1.0-RC-D/E reviewed file appears in working or staged diff (untouched)（found {touched_reviewed}）"
        if touched_reviewed
        else "W. no v1.0-RC-D/E reviewed file appears in working or staged diff (untouched)",
        not touched_reviewed,
    )

    print("[X] readiness script only invokes read-only git plumbing as subprocess")
    self_subprocess_targets = re.findall(r'subprocess\.run\(\s*\[\s*"([^"]+)"', self_text)
    check(
        f"X. readiness script only invokes read-only git plumbing as subprocess（found {self_subprocess_targets}）"
        if any(t != "git" for t in self_subprocess_targets)
        else "X. readiness script only invokes read-only git plumbing as subprocess",
        all(t == "git" for t in self_subprocess_targets),
    )

    print("[Y] no tag at HEAD")
    tags_at_head = git_lines(["tag", "--points-at", "HEAD"])
    check(
        f"Y. no tag at HEAD（found {tags_at_head}）" if tags_at_head else "Y. no tag at HEAD",
        not tags_at_head,
    )

    print("[Z] cached diff gate: staged diff is empty or exactly the allowed v1.0-RC-R files")
    cached_diff_ok = (not staged_files) or (staged_files == ALLOWED_STAGED_FILES)
    check(
        f"Z. cached diff gate: staged diff is empty or exactly the allowed v1.0-RC-R files（found {sorted(staged_files)}）"
        if not cached_diff_ok
        else "Z. cached diff gate: staged diff is empty or exactly the allowed v1.0-RC-R files",
        cached_diff_ok,
    )

    total = len(PASS) + len(FAIL)
    print(f"\nv1.0-RC-R Full Blackboard Loop Rehearsal Closeout readiness")
    print(f"合計：{len(PASS)}/{total} 通過")
    if FAIL:
        print(f"\nXX v1.0-RC-R readiness 失敗 {len(FAIL)} 項：")
        for f in FAIL:
            print(f"   - {f}")
        print("Final result: FAIL")
        sys.exit(1)
    else:
        print("Final result: PASS")
        sys.exit(0)


if __name__ == "__main__":
    main()
