"""v0.9.6-R readiness check: Result Feedback Closeout.

Pure local filesystem + git metadata validation, standard library only. Does NOT
import any application/Hermes/Worker/OpenClaw/connector runtime module, does not
call network, does not read secrets or `.env`, does not read connector data, does
not write the queue, audit trail, or Blackboard, and does not modify any file. Its
only subprocess use is read-only git plumbing (status, diff, ls-files, tag).
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
CLAUDE_MD_REL = "CLAUDE.md"
PATCHES_REL = "patches/"

DOC_REL = "docs/HERMES_RESULT_FEEDBACK_CLOSEOUT_V0_9_6_R.md"
DOC_PATH = REPO_ROOT / DOC_REL

SELF_SCRIPT_REL = "scripts/check_hermes_result_feedback_closeout_v0_9_6_r.py"
SELF_SCRIPT_PATH = REPO_ROOT / SELF_SCRIPT_REL

ALLOWED_STAGED_FILES = {DOC_REL, SELF_SCRIPT_REL}

FORBIDDEN_RUNTIME_FILES = (
    MAIN_PY_REL,
    SYSTEM_HTML_REL,
    DASHBOARD_CSS_REL,
    RESULT_FEEDBACK_PREVIEW_REL,
    CLAUDE_MD_REL,
)

REQUIRED_PHASE_TITLE = "v0.9.6-R Result Feedback Closeout"

REQUIRED_SEQUENCE_LABELS = (
    "v0.9.6-A",
    "v0.9.6-B",
    "v0.9.6-C",
    "v0.9.6-D",
    "v0.9.6-E",
)

A_DOC_REL = "docs/HERMES_CALLBACK_CONTRACT_PLAN_V0_9_6_A.md"
A_SCRIPT_REL = "scripts/check_hermes_callback_contract_plan_v0_9_6_a.py"

B_DOC_REL = "docs/HERMES_MOCK_CALLBACK_RECEIVER_BOUNDARY_V0_9_6_B.md"
B_SCRIPT_REL = "scripts/check_hermes_mock_callback_receiver_boundary_v0_9_6_b.py"

C_DOC_REL = "docs/HERMES_RESULT_FEEDBACK_DISPLAY_PLAN_V0_9_6_C.md"
C_SCRIPT_REL = "scripts/check_hermes_result_feedback_display_plan_v0_9_6_c.py"

D_DOC_REL = "docs/HERMES_RESULT_FEEDBACK_DISPLAY_IMPLEMENTATION_V0_9_6_D.md"
D_SCRIPT_REL = "scripts/check_hermes_result_feedback_display_implementation_v0_9_6_d.py"
D_FIXTURE_REL = "fixtures/local_mock_data/hermes_result_feedback_preview_v0_9_6_d.json"
D_HELPER_REL = "app/result_feedback_preview.py"

E_DOC_REL = "docs/HERMES_RESULT_DRIVEN_FOLLOW_UP_SUGGESTION_GUARD_V0_9_6_E.md"
E_SCRIPT_REL = "scripts/check_hermes_result_driven_follow_up_suggestion_guard_v0_9_6_e.py"

REQUIRED_ARTIFACT_PATHS = (
    A_DOC_REL,
    A_SCRIPT_REL,
    B_DOC_REL,
    B_SCRIPT_REL,
    C_DOC_REL,
    C_SCRIPT_REL,
    D_DOC_REL,
    D_SCRIPT_REL,
    D_FIXTURE_REL,
    D_HELPER_REL,
    E_DOC_REL,
    E_SCRIPT_REL,
)

REQUIRED_DOC_SUBSTRINGS = (
    "v0.9.6-R is docs / check-only closeout.",
    "/dashboard/system remained GET-only.",
    "v1.0 not started.",
    "v1.0-RC not started.",
    "No callback receiver is implemented in this phase.",
    "No webhook is created in this phase.",
    "No new route or endpoint is created in this phase.",
    "No POST/form/button/action URL/control is added in this phase.",
    "No Dashboard controls are added in this phase.",
    "No real callback data is read in this phase.",
    "No connector is selected, called, read, or written in this phase.",
    "No Hermes runtime activation occurs in this phase.",
    "No follow-up task creation occurs in this phase.",
    "No Worker call occurs in this phase.",
    "No OpenClaw call occurs in this phase.",
    "No Blackboard write occurs in this phase.",
    "No queue write occurs in this phase.",
    "No audit trail write occurs in this phase.",
    "No production/shared DB or Remote Blackboard API runtime is created in this phase.",
    "Result Message is not next dispatch permission.",
    "Result Feedback Display is not execution permission.",
    "Hermes readback is advisory only.",
    "Owner review required is not Owner approval.",
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

    print("[A] v0.9.6-R closeout doc exists")
    check("A. v0.9.6-R closeout doc exists", DOC_PATH.is_file())

    print("[B] v0.9.6-R readiness script exists")
    check("B. v0.9.6-R readiness script exists", SELF_SCRIPT_PATH.is_file())

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

    print("[E] doc lists v0.9.6-A/B/C/D/E as completed sequence")
    missing_labels = [label for label in REQUIRED_SEQUENCE_LABELS if label not in doc_text]
    check(
        f"E. doc lists v0.9.6-A/B/C/D/E as completed sequence（missing {missing_labels}）"
        if missing_labels
        else "E. doc lists v0.9.6-A/B/C/D/E as completed sequence",
        not missing_labels,
    )

    print("[F] doc summarizes v0.9.6-D implementation")
    check(
        "F. doc summarizes v0.9.6-D implementation",
        "v0.9.6-D Implementation Summary" in doc_text,
    )

    print("[G] doc lists all v0.9.6-A/B/C/D/E artifacts")
    missing_artifacts = [p for p in REQUIRED_ARTIFACT_PATHS if p not in doc_text]
    check(
        f"G. doc lists all v0.9.6-A/B/C/D/E artifacts（missing {missing_artifacts}）"
        if missing_artifacts
        else "G. doc lists all v0.9.6-A/B/C/D/E artifacts",
        not missing_artifacts,
    )

    print("[H] doc includes safe next recommendation")
    check("H. doc includes safe next recommendation", "Safe Next Recommendation" in doc_text)

    print("[I] all v0.9.6-A/B/C/D/E artifact files actually exist on disk")
    missing_artifact_files = [p for p in REQUIRED_ARTIFACT_PATHS if not (REPO_ROOT / p).is_file()]
    check(
        f"I. all v0.9.6-A/B/C/D/E artifact files actually exist on disk（missing {missing_artifact_files}）"
        if missing_artifact_files
        else "I. all v0.9.6-A/B/C/D/E artifact files actually exist on disk",
        not missing_artifact_files,
    )

    print("[J] only allowed v0.9.6-R files are staged")
    staged_files = set(git_lines(["diff", "--cached", "--name-only"]))
    unexpected_staged = sorted(staged_files - ALLOWED_STAGED_FILES)
    check(
        f"J. only allowed v0.9.6-R files are staged（unexpected {unexpected_staged}）"
        if unexpected_staged
        else "J. only allowed v0.9.6-R files are staged",
        not unexpected_staged,
    )

    print("[K] patches/ is not staged")
    staged_patches = [f for f in staged_files if f.startswith(PATCHES_REL)]
    check(
        f"K. patches/ is not staged（found {staged_patches}）" if staged_patches else "K. patches/ is not staged",
        not staged_patches,
    )

    print("[L] CLAUDE.md is not staged")
    check("L. CLAUDE.md is not staged", CLAUDE_MD_REL not in staged_files)

    print("[M] app/main.py is not staged")
    check("M. app/main.py is not staged", MAIN_PY_REL not in staged_files)

    print("[N] templates/system.html is not staged")
    check("N. templates/system.html is not staged", SYSTEM_HTML_REL not in staged_files)

    print("[O] static/dashboard.css is not staged")
    check("O. static/dashboard.css is not staged", DASHBOARD_CSS_REL not in staged_files)

    print("[P] app/result_feedback_preview.py is not staged")
    check("P. app/result_feedback_preview.py is not staged", RESULT_FEEDBACK_PREVIEW_REL not in staged_files)

    print("[Q] no route/endpoint/webhook/connector runtime file is staged")
    runtime_path_markers = ("routes", "endpoint", "webhook", "connector", "callback_receiver")
    suspicious_staged = sorted(
        f for f in staged_files
        if f not in ALLOWED_STAGED_FILES and any(marker in f.lower() for marker in runtime_path_markers)
    )
    check(
        f"Q. no route/endpoint/webhook/connector runtime file is staged（found {suspicious_staged}）"
        if suspicious_staged
        else "Q. no route/endpoint/webhook/connector runtime file is staged",
        not suspicious_staged,
    )

    print("[R] forbidden runtime files absent from working diff and staged diff")
    working_diff_files = set(git_lines(["diff", "--name-only"]))
    touched_forbidden = sorted((working_diff_files | staged_files) & set(FORBIDDEN_RUNTIME_FILES))
    check(
        f"R. forbidden runtime files absent from working diff and staged diff（found {touched_forbidden}）"
        if touched_forbidden
        else "R. forbidden runtime files absent from working diff and staged diff",
        not touched_forbidden,
    )

    print("[S] readiness script only invokes read-only git plumbing as subprocess")
    self_subprocess_targets = re.findall(r'subprocess\.run\(\s*\[\s*"([^"]+)"', self_text)
    check(
        f"S. readiness script only invokes read-only git plumbing as subprocess（found {self_subprocess_targets}）"
        if any(t != "git" for t in self_subprocess_targets)
        else "S. readiness script only invokes read-only git plumbing as subprocess",
        all(t == "git" for t in self_subprocess_targets),
    )

    print("[T] patches/ remains untracked")
    patches_tracked = git_lines(["ls-files", "--", "patches/"])
    check(
        f"T. patches/ remains untracked（found tracked {patches_tracked}）"
        if patches_tracked
        else "T. patches/ remains untracked",
        not patches_tracked,
    )

    print("[U] no tag at HEAD")
    tags_at_head = git_lines(["tag", "--points-at", "HEAD"])
    check(
        f"U. no tag at HEAD（found {tags_at_head}）" if tags_at_head else "U. no tag at HEAD",
        not tags_at_head,
    )

    print("[V] cached diff gate: staged diff is empty or exactly the allowed v0.9.6-R files")
    cached_diff_ok = (not staged_files) or (staged_files == ALLOWED_STAGED_FILES)
    check(
        f"V. cached diff gate: staged diff is empty or exactly the allowed v0.9.6-R files（found {sorted(staged_files)}）"
        if not cached_diff_ok
        else "V. cached diff gate: staged diff is empty or exactly the allowed v0.9.6-R files",
        cached_diff_ok,
    )

    total = len(PASS) + len(FAIL)
    print(f"\nv0.9.6-R Result Feedback Closeout readiness")
    print(f"合計：{len(PASS)}/{total} 通過")
    if FAIL:
        print(f"\nXX v0.9.6-R readiness 失敗 {len(FAIL)} 項：")
        for f in FAIL:
            print(f"   - {f}")
        print("Final result: FAIL")
        sys.exit(1)
    else:
        print("Final result: PASS")
        sys.exit(0)


if __name__ == "__main__":
    main()
