"""v0.9.6-E readiness check: Result-driven Follow-up Suggestion Guard.

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

DOC_REL = "docs/HERMES_RESULT_DRIVEN_FOLLOW_UP_SUGGESTION_GUARD_V0_9_6_E.md"
DOC_PATH = REPO_ROOT / DOC_REL

SELF_SCRIPT_REL = "scripts/check_hermes_result_driven_follow_up_suggestion_guard_v0_9_6_e.py"
SELF_SCRIPT_PATH = REPO_ROOT / SELF_SCRIPT_REL

ALLOWED_STAGED_FILES = {DOC_REL, SELF_SCRIPT_REL}

FORBIDDEN_RUNTIME_FILES = (
    MAIN_PY_REL,
    SYSTEM_HTML_REL,
    DASHBOARD_CSS_REL,
    RESULT_FEEDBACK_PREVIEW_REL,
    CLAUDE_MD_REL,
)

REQUIRED_PHASE_TITLE = "v0.9.6-E Result-driven Follow-up Suggestion Guard"

REQUIRED_SEQUENCE_LABELS = ("v0.9.6-R",)

REQUIRED_MESSAGE_FIELDS = (
    "suggestion_id",
    "source_callback_id",
    "source_task_id",
    "source_command_id",
    "source_result_status",
    "source_validation_status",
    "summary",
    "recommended_next_step",
    "owner_question",
    "missing_information",
    "risk_assessment",
    "safety_flags",
    "confidence",
    "must_not_execute",
    "requires_owner_confirmation",
    "follow_up_task_creation_allowed",
    "blackboard_write_allowed",
    "queue_write_allowed",
    "audit_trail_write_allowed",
    "worker_dispatch_allowed",
    "openclaw_call_allowed",
    "hermes_runtime_allowed",
    "connector_call_allowed",
    "google_sheets_write_allowed",
    "external_side_effects_allowed",
)

REQUIRED_DOC_SUBSTRINGS = (
    "v0.9.6-E is docs / check-only guard plan.",
    "v0.9.6-E does not implement Hermes runtime.",
    "v0.9.6-E does not create follow-up task.",
    "No Blackboard write occurs in this phase.",
    "No queue write occurs in this phase.",
    "No audit trail write occurs in this phase.",
    "No Worker dispatch occurs in this phase.",
    "No OpenClaw call occurs in this phase.",
    "No connector call occurs in this phase.",
    "No Google Sheets write occurs in this phase.",
    "No Dashboard controls are added in this phase.",
    "No external side effects occur in this phase.",
    "Suggestion itself never grants execution permission.",
    "Hermes readback is advisory only.",
    "must_not_execute = true",
    "requires_owner_confirmation = true",
    "follow_up_task_creation_allowed = false",
    "blackboard_write_allowed = false",
    "queue_write_allowed = false",
    "audit_trail_write_allowed = false",
    "worker_dispatch_allowed = false",
    "openclaw_call_allowed = false",
    "hermes_runtime_allowed = false",
    "connector_call_allowed = false",
    "google_sheets_write_allowed = false",
    "external_side_effects_allowed = false",
    "Any automatic follow-up wording = HOLD.",
    "Any write-capable implication = HOLD.",
    "Any Dashboard control implication = HOLD.",
)

REQUIRED_SECTION_HEADINGS = (
    "Core Guard Principle",
    "Future Follow-up Suggestion Message Type",
    "Required Future Follow-up Suggestion Message Fields",
    "Required Future Safety Flags",
    "Future Allowed Behavior",
    "Future Forbidden Behavior",
    "Fail-Closed Rules",
    "Future Owner Decision Boundary",
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

    print("[A] v0.9.6-E guard doc exists")
    check("A. v0.9.6-E guard doc exists", DOC_PATH.is_file())

    print("[B] v0.9.6-E readiness script exists")
    check("B. v0.9.6-E readiness script exists", SELF_SCRIPT_PATH.is_file())

    print("[C] doc contains exact phase title")
    check("C. doc contains exact phase title", REQUIRED_PHASE_TITLE in doc_text)

    print("[D] doc contains all required safety/guard substrings")
    missing_substrings = [s for s in REQUIRED_DOC_SUBSTRINGS if s not in doc_text]
    check(
        f"D. doc contains all required safety/guard substrings（missing {missing_substrings}）"
        if missing_substrings
        else "D. doc contains all required safety/guard substrings",
        not missing_substrings,
    )

    print("[E] doc defines required section headings (guard principle/message type/fields/flags/behavior/fail-closed/owner boundary)")
    missing_headings = [h for h in REQUIRED_SECTION_HEADINGS if h not in doc_text]
    check(
        f"E. doc defines required section headings（missing {missing_headings}）"
        if missing_headings
        else "E. doc defines required section headings",
        not missing_headings,
    )

    print("[F] doc defines required future Follow-up Suggestion Message fields")
    missing_fields = [f for f in REQUIRED_MESSAGE_FIELDS if f not in doc_text]
    check(
        f"F. doc defines required future Follow-up Suggestion Message fields（missing {missing_fields}）"
        if missing_fields
        else "F. doc defines required future Follow-up Suggestion Message fields",
        not missing_fields,
    )

    print("[G] doc lists future sequence v0.9.6-R")
    missing_labels = [label for label in REQUIRED_SEQUENCE_LABELS if label not in doc_text]
    check(
        f"G. doc lists future sequence v0.9.6-R（missing {missing_labels}）"
        if missing_labels
        else "G. doc lists future sequence v0.9.6-R",
        not missing_labels,
    )

    print("[H] only allowed v0.9.6-E files are staged")
    staged_files = set(git_lines(["diff", "--cached", "--name-only"]))
    unexpected_staged = sorted(staged_files - ALLOWED_STAGED_FILES)
    check(
        f"H. only allowed v0.9.6-E files are staged（unexpected {unexpected_staged}）"
        if unexpected_staged
        else "H. only allowed v0.9.6-E files are staged",
        not unexpected_staged,
    )

    print("[I] patches/ is not staged")
    staged_patches = [f for f in staged_files if f.startswith(PATCHES_REL)]
    check(
        f"I. patches/ is not staged（found {staged_patches}）" if staged_patches else "I. patches/ is not staged",
        not staged_patches,
    )

    print("[J] CLAUDE.md is not staged")
    check("J. CLAUDE.md is not staged", CLAUDE_MD_REL not in staged_files)

    print("[K] app/main.py is not staged")
    check("K. app/main.py is not staged", MAIN_PY_REL not in staged_files)

    print("[L] templates/system.html is not staged")
    check("L. templates/system.html is not staged", SYSTEM_HTML_REL not in staged_files)

    print("[M] static/dashboard.css is not staged")
    check("M. static/dashboard.css is not staged", DASHBOARD_CSS_REL not in staged_files)

    print("[N] app/result_feedback_preview.py is not staged")
    check("N. app/result_feedback_preview.py is not staged", RESULT_FEEDBACK_PREVIEW_REL not in staged_files)

    print("[O] no route/endpoint/webhook/connector runtime file is staged")
    runtime_path_markers = ("routes", "endpoint", "webhook", "connector", "callback")
    suspicious_staged = sorted(
        f for f in staged_files
        if f not in ALLOWED_STAGED_FILES and any(marker in f.lower() for marker in runtime_path_markers)
    )
    check(
        f"O. no route/endpoint/webhook/connector runtime file is staged（found {suspicious_staged}）"
        if suspicious_staged
        else "O. no route/endpoint/webhook/connector runtime file is staged",
        not suspicious_staged,
    )

    print("[P] no forbidden follow-up/runtime/control keywords appear as implementation in this script")
    found_action_keywords = [kw for kw in FORBIDDEN_CONNECTOR_ACTION_KEYWORDS if kw in self_text]
    check(
        f"P. no forbidden follow-up/runtime/control keywords appear as implementation in this script（found {found_action_keywords}）"
        if found_action_keywords
        else "P. no forbidden follow-up/runtime/control keywords appear as implementation in this script",
        not found_action_keywords,
    )

    print("[Q] forbidden runtime files absent from working diff and staged diff")
    working_diff_files = set(git_lines(["diff", "--name-only"]))
    touched_forbidden = sorted((working_diff_files | staged_files) & set(FORBIDDEN_RUNTIME_FILES))
    check(
        f"Q. forbidden runtime files absent from working diff and staged diff（found {touched_forbidden}）"
        if touched_forbidden
        else "Q. forbidden runtime files absent from working diff and staged diff",
        not touched_forbidden,
    )

    print("[R] readiness script only invokes read-only git plumbing as subprocess")
    self_subprocess_targets = re.findall(r'subprocess\.run\(\s*\[\s*"([^"]+)"', self_text)
    check(
        f"R. readiness script only invokes read-only git plumbing as subprocess（found {self_subprocess_targets}）"
        if any(t != "git" for t in self_subprocess_targets)
        else "R. readiness script only invokes read-only git plumbing as subprocess",
        all(t == "git" for t in self_subprocess_targets),
    )

    print("[S] readiness script imports no os/network/db/connector module")
    found_forbidden_self_imports = [
        m for m in FORBIDDEN_SELF_IMPORTS
        if re.search(r"^\s*import\s+" + re.escape(m) + r"\b", self_text, flags=re.MULTILINE)
        or re.search(r"^\s*from\s+" + re.escape(m) + r"\b", self_text, flags=re.MULTILINE)
    ]
    check(
        f"S. readiness script imports no os/network/db/connector module（found {found_forbidden_self_imports}）"
        if found_forbidden_self_imports
        else "S. readiness script imports no os/network/db/connector module",
        not found_forbidden_self_imports,
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

    print("[V] cached diff gate: staged diff is empty or exactly the allowed v0.9.6-E files")
    cached_diff_ok = (not staged_files) or (staged_files == ALLOWED_STAGED_FILES)
    check(
        f"V. cached diff gate: staged diff is empty or exactly the allowed v0.9.6-E files（found {sorted(staged_files)}）"
        if not cached_diff_ok
        else "V. cached diff gate: staged diff is empty or exactly the allowed v0.9.6-E files",
        cached_diff_ok,
    )

    total = len(PASS) + len(FAIL)
    print(f"\nv0.9.6-E Result-driven Follow-up Suggestion Guard readiness")
    print(f"合計：{len(PASS)}/{total} 通過")
    if FAIL:
        print(f"\nXX v0.9.6-E readiness 失敗 {len(FAIL)} 項：")
        for f in FAIL:
            print(f"   - {f}")
        print("Final result: FAIL")
        sys.exit(1)
    else:
        print("Final result: PASS")
        sys.exit(0)


if __name__ == "__main__":
    main()
