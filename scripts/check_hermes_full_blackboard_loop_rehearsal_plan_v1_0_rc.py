"""v1.0-RC readiness check: Full Blackboard Loop Rehearsal Plan.

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

DOC_REL = "docs/HERMES_FULL_BLACKBOARD_LOOP_REHEARSAL_PLAN_V1_0_RC.md"
DOC_PATH = REPO_ROOT / DOC_REL

SELF_SCRIPT_REL = "scripts/check_hermes_full_blackboard_loop_rehearsal_plan_v1_0_rc.py"
SELF_SCRIPT_PATH = REPO_ROOT / SELF_SCRIPT_REL

ALLOWED_STAGED_FILES = {DOC_REL, SELF_SCRIPT_REL}

FORBIDDEN_RUNTIME_FILES = (
    MAIN_PY_REL,
    SYSTEM_HTML_REL,
    DASHBOARD_CSS_REL,
    RESULT_FEEDBACK_PREVIEW_REL,
    CLAUDE_MD_REL,
)

REQUIRED_PHASE_TITLE = "v1.0-RC Full Blackboard Loop Rehearsal Plan"

REQUIRED_SECTION_HEADINGS = (
    "Future Rehearsal Flow",
    "Required Future Rehearsal Artifacts",
    "Required Future Safety Flags",
    "Future Dashboard Boundary",
    "Future Hermes Boundary",
    "Future Worker Boundary",
    "Future OpenClaw Boundary",
    "Future Blackboard / Queue / Audit Boundary",
    "Future Connector Boundary",
    "Fail-Closed Rules",
)

REQUIRED_DOC_SUBSTRINGS = (
    "v1.0-RC is docs / check-only rehearsal plan.",
    "v1.0-RC does not implement Full Blackboard Loop.",
    "No Blackboard write occurs in this phase.",
    "No queue write occurs in this phase.",
    "No audit trail write occurs in this phase.",
    "No Dashboard controls are added in this phase.",
    "No Hermes runtime activation occurs in this phase.",
    "No Worker dispatch occurs in this phase.",
    "No OpenClaw call occurs in this phase.",
    "No connector call occurs in this phase.",
    "No external side effects occur in this phase.",
    "external_side_effects_allowed = false",
    "blackboard_write_allowed = false",
    "queue_write_allowed = false",
    "audit_trail_write_allowed = false",
    "worker_dispatch_allowed = false",
    "openclaw_call_allowed = false",
    "hermes_runtime_allowed = false",
    "connector_call_allowed = false",
    "follow_up_task_creation_allowed = false",
    "Any automatic follow-up implication = HOLD.",
    "Any Dashboard control implication = HOLD.",
)

FORBIDDEN_SELF_IMPORTS = (
    "os",
    "socket",
    "requests",
    "httpx",
    "urllib",
    "sqlite3",
    "google",
    "slack_sdk",
    "github",
)

FORBIDDEN_CONNECTOR_ACTION_KEYWORDS = (
    "smtplib.SMTP" + "(",
    "requests" + ".post(",
    "requests" + ".get(",
    "httpx" + ".post(",
    "httpx" + ".get(",
    "@app" + ".route(",
    "@app" + ".post(",
    "QueueStore" + "(",
    "BlackboardStore" + "(",
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

    print("[A] v1.0-RC plan doc exists")
    check("A. v1.0-RC plan doc exists", DOC_PATH.is_file())

    print("[B] v1.0-RC readiness script exists")
    check("B. v1.0-RC readiness script exists", SELF_SCRIPT_PATH.is_file())

    print("[C] doc contains exact phase title")
    check("C. doc contains exact phase title", REQUIRED_PHASE_TITLE in doc_text)

    print("[D] doc contains all required safety/plan substrings")
    missing_substrings = [s for s in REQUIRED_DOC_SUBSTRINGS if s not in doc_text]
    check(
        f"D. doc contains all required safety/plan substrings（missing {missing_substrings}）"
        if missing_substrings
        else "D. doc contains all required safety/plan substrings",
        not missing_substrings,
    )

    print("[E] doc defines required section headings (flow/artifacts/flags/boundaries/fail-closed)")
    missing_headings = [h for h in REQUIRED_SECTION_HEADINGS if h not in doc_text]
    check(
        f"E. doc defines required section headings（missing {missing_headings}）"
        if missing_headings
        else "E. doc defines required section headings",
        not missing_headings,
    )

    print("[F] doc includes safe next recommendation")
    check("F. doc includes safe next recommendation", "Safe Next Recommendation" in doc_text)

    print("[G] only allowed v1.0-RC files are staged")
    staged_files = set(git_lines(["diff", "--cached", "--name-only"]))
    unexpected_staged = sorted(staged_files - ALLOWED_STAGED_FILES)
    check(
        f"G. only allowed v1.0-RC files are staged（unexpected {unexpected_staged}）"
        if unexpected_staged
        else "G. only allowed v1.0-RC files are staged",
        not unexpected_staged,
    )

    print("[H] patches/ is not staged")
    staged_patches = [f for f in staged_files if f.startswith(PATCHES_REL)]
    check(
        f"H. patches/ is not staged（found {staged_patches}）" if staged_patches else "H. patches/ is not staged",
        not staged_patches,
    )

    print("[I] CLAUDE.md is not staged")
    check("I. CLAUDE.md is not staged", CLAUDE_MD_REL not in staged_files)

    print("[J] app/main.py is not staged")
    check("J. app/main.py is not staged", MAIN_PY_REL not in staged_files)

    print("[K] templates/system.html is not staged")
    check("K. templates/system.html is not staged", SYSTEM_HTML_REL not in staged_files)

    print("[L] static/dashboard.css is not staged")
    check("L. static/dashboard.css is not staged", DASHBOARD_CSS_REL not in staged_files)

    print("[M] app/result_feedback_preview.py is not staged")
    check("M. app/result_feedback_preview.py is not staged", RESULT_FEEDBACK_PREVIEW_REL not in staged_files)

    print("[N] no route/endpoint/webhook/connector runtime file is staged")
    runtime_path_markers = ("routes", "endpoint", "webhook", "connector", "callback_receiver")
    suspicious_staged = sorted(
        f for f in staged_files
        if f not in ALLOWED_STAGED_FILES and any(marker in f.lower() for marker in runtime_path_markers)
    )
    check(
        f"N. no route/endpoint/webhook/connector runtime file is staged（found {suspicious_staged}）"
        if suspicious_staged
        else "N. no route/endpoint/webhook/connector runtime file is staged",
        not suspicious_staged,
    )

    print("[O] no forbidden runtime/control keywords appear as implementation in this script")
    found_action_keywords = [kw for kw in FORBIDDEN_CONNECTOR_ACTION_KEYWORDS if kw in self_text]
    check(
        f"O. no forbidden runtime/control keywords appear as implementation in this script（found {found_action_keywords}）"
        if found_action_keywords
        else "O. no forbidden runtime/control keywords appear as implementation in this script",
        not found_action_keywords,
    )

    print("[P] forbidden runtime files absent from working diff and staged diff")
    working_diff_files = set(git_lines(["diff", "--name-only"]))
    touched_forbidden = sorted((working_diff_files | staged_files) & set(FORBIDDEN_RUNTIME_FILES))
    check(
        f"P. forbidden runtime files absent from working diff and staged diff（found {touched_forbidden}）"
        if touched_forbidden
        else "P. forbidden runtime files absent from working diff and staged diff",
        not touched_forbidden,
    )

    print("[Q] readiness script only invokes read-only git plumbing as subprocess")
    self_subprocess_targets = re.findall(r'subprocess\.run\(\s*\[\s*"([^"]+)"', self_text)
    check(
        f"Q. readiness script only invokes read-only git plumbing as subprocess（found {self_subprocess_targets}）"
        if any(t != "git" for t in self_subprocess_targets)
        else "Q. readiness script only invokes read-only git plumbing as subprocess",
        all(t == "git" for t in self_subprocess_targets),
    )

    print("[R] readiness script imports no os/network/db/connector module")
    found_forbidden_self_imports = [
        m for m in FORBIDDEN_SELF_IMPORTS
        if re.search(r"^\s*import\s+" + re.escape(m) + r"\b", self_text, flags=re.MULTILINE)
        or re.search(r"^\s*from\s+" + re.escape(m) + r"\b", self_text, flags=re.MULTILINE)
    ]
    check(
        f"R. readiness script imports no os/network/db/connector module（found {found_forbidden_self_imports}）"
        if found_forbidden_self_imports
        else "R. readiness script imports no os/network/db/connector module",
        not found_forbidden_self_imports,
    )

    print("[S] patches/ remains untracked")
    patches_tracked = git_lines(["ls-files", "--", "patches/"])
    check(
        f"S. patches/ remains untracked（found tracked {patches_tracked}）"
        if patches_tracked
        else "S. patches/ remains untracked",
        not patches_tracked,
    )

    print("[T] no tag at HEAD")
    tags_at_head = git_lines(["tag", "--points-at", "HEAD"])
    check(
        f"T. no tag at HEAD（found {tags_at_head}）" if tags_at_head else "T. no tag at HEAD",
        not tags_at_head,
    )

    print("[U] cached diff gate: staged diff is empty or exactly the allowed v1.0-RC files")
    cached_diff_ok = (not staged_files) or (staged_files == ALLOWED_STAGED_FILES)
    check(
        f"U. cached diff gate: staged diff is empty or exactly the allowed v1.0-RC files（found {sorted(staged_files)}）"
        if not cached_diff_ok
        else "U. cached diff gate: staged diff is empty or exactly the allowed v1.0-RC files",
        cached_diff_ok,
    )

    total = len(PASS) + len(FAIL)
    print(f"\nv1.0-RC Full Blackboard Loop Rehearsal Plan readiness")
    print(f"合計：{len(PASS)}/{total} 通過")
    if FAIL:
        print(f"\nXX v1.0-RC readiness 失敗 {len(FAIL)} 項：")
        for f in FAIL:
            print(f"   - {f}")
        print("Final result: FAIL")
        sys.exit(1)
    else:
        print("Final result: PASS")
        sys.exit(0)


if __name__ == "__main__":
    main()
