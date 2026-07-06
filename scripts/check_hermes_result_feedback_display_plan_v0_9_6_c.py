"""v0.9.6-C readiness check: Result Feedback Display Plan.

Pure local filesystem + git metadata validation, standard library only. Does NOT
import any application/Hermes/Worker/OpenClaw/connector runtime module, does not
call network, does not read secrets or `.env`, does not read connector data, does
not write the queue or audit trail, and does not modify any file. Its only
subprocess use is read-only git plumbing (status, diff, ls-files, tag, show).
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
CLAUDE_MD_REL = "CLAUDE.md"
PATCHES_REL = "patches/"

DOC_REL = "docs/HERMES_RESULT_FEEDBACK_DISPLAY_PLAN_V0_9_6_C.md"
DOC_PATH = REPO_ROOT / DOC_REL

SELF_SCRIPT_REL = "scripts/check_hermes_result_feedback_display_plan_v0_9_6_c.py"
SELF_SCRIPT_PATH = REPO_ROOT / SELF_SCRIPT_REL

ALLOWED_STAGED_FILES = {DOC_REL, SELF_SCRIPT_REL}

FORBIDDEN_RUNTIME_FILES = (
    MAIN_PY_REL,
    SYSTEM_HTML_REL,
    DASHBOARD_CSS_REL,
    CLAUDE_MD_REL,
)

REQUIRED_PHASE_TITLE = "v0.9.6-C Result Feedback Display Plan"

REQUIRED_SECTION_HEADINGS = (
    "Future Display Source Boundary",
    "Future Allowed Display Fields",
    "Future Forbidden Display Fields",
    "Required Future Display Labels",
    "Future Forbidden Controls",
    "Future Rendering Rules",
    "Future Status Interpretation Rules",
    "Fail-Closed Rules",
)

REQUIRED_SEQUENCE_LABELS = (
    "v0.9.6-D",
    "v0.9.6-E",
    "v0.9.6-R",
)

REQUIRED_DOC_SUBSTRINGS = (
    "v0.9.6-C is docs / check-only display plan.",
    "v0.9.6-C does not implement Dashboard UI.",
    "No app/main.py modification occurs in this phase.",
    "No templates/system.html modification occurs in this phase.",
    "No static/dashboard.css modification occurs in this phase.",
    "No route or endpoint is created in this phase.",
    "No POST/form/button/action URL/control is added in this phase.",
    "No callback receiver is implemented in this phase.",
    "No webhook is created in this phase.",
    "No real callbacks are received in this phase.",
    "No Blackboard write occurs in this phase.",
    "No queue write occurs in this phase.",
    "No audit trail write occurs in this phase.",
    "No Hermes runtime activation occurs in this phase.",
    "No Worker call occurs in this phase.",
    "No OpenClaw call occurs in this phase.",
    "No automatic follow-up task creation occurs in this phase.",
    "result_status does not prove real execution success.",
    "result_status does not grant dispatch permission.",
    "owner_review_required is not Owner approval.",
    "output_preview is not external write confirmation.",
    "v0.9.6-D implementation requires separate authorization.",
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

    print("[A] v0.9.6-C display plan doc exists")
    check("A. v0.9.6-C display plan doc exists", DOC_PATH.is_file())

    print("[B] v0.9.6-C readiness script exists")
    check("B. v0.9.6-C readiness script exists", SELF_SCRIPT_PATH.is_file())

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

    print("[E] doc defines required section headings (source/fields/labels/controls/rendering/status/fail-closed)")
    missing_headings = [h for h in REQUIRED_SECTION_HEADINGS if h not in doc_text]
    check(
        f"E. doc defines required section headings（missing {missing_headings}）"
        if missing_headings
        else "E. doc defines required section headings",
        not missing_headings,
    )

    print("[F] doc lists future sequence v0.9.6-D/E/R")
    missing_labels = [label for label in REQUIRED_SEQUENCE_LABELS if label not in doc_text]
    check(
        f"F. doc lists future sequence v0.9.6-D/E/R（missing {missing_labels}）"
        if missing_labels
        else "F. doc lists future sequence v0.9.6-D/E/R",
        not missing_labels,
    )

    print("[G] only allowed v0.9.6-C files are staged")
    staged_files = set(git_lines(["diff", "--cached", "--name-only"]))
    unexpected_staged = sorted(staged_files - ALLOWED_STAGED_FILES)
    check(
        f"G. only allowed v0.9.6-C files are staged（unexpected {unexpected_staged}）"
        if unexpected_staged
        else "G. only allowed v0.9.6-C files are staged",
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

    print("[M] no route/endpoint/webhook/connector runtime file is staged")
    runtime_path_markers = ("routes", "endpoint", "webhook", "connector", "callback")
    suspicious_staged = sorted(
        f for f in staged_files
        if f not in ALLOWED_STAGED_FILES and any(marker in f.lower() for marker in runtime_path_markers)
    )
    check(
        f"M. no route/endpoint/webhook/connector runtime file is staged（found {suspicious_staged}）"
        if suspicious_staged
        else "M. no route/endpoint/webhook/connector runtime file is staged",
        not suspicious_staged,
    )

    print("[N] no forbidden display/runtime/control keywords appear as implementation in this script")
    found_action_keywords = [kw for kw in FORBIDDEN_CONNECTOR_ACTION_KEYWORDS if kw in self_text]
    check(
        f"N. no forbidden display/runtime/control keywords appear as implementation in this script（found {found_action_keywords}）"
        if found_action_keywords
        else "N. no forbidden display/runtime/control keywords appear as implementation in this script",
        not found_action_keywords,
    )

    print("[O] forbidden runtime files absent from working diff and staged diff")
    working_diff_files = set(git_lines(["diff", "--name-only"]))
    touched_forbidden = sorted((working_diff_files | staged_files) & set(FORBIDDEN_RUNTIME_FILES))
    check(
        f"O. forbidden runtime files absent from working diff and staged diff（found {touched_forbidden}）"
        if touched_forbidden
        else "O. forbidden runtime files absent from working diff and staged diff",
        not touched_forbidden,
    )

    print("[P] readiness script only invokes read-only git plumbing as subprocess")
    self_subprocess_targets = re.findall(r'subprocess\.run\(\s*\[\s*"([^"]+)"', self_text)
    check(
        f"P. readiness script only invokes read-only git plumbing as subprocess（found {self_subprocess_targets}）"
        if any(t != "git" for t in self_subprocess_targets)
        else "P. readiness script only invokes read-only git plumbing as subprocess",
        all(t == "git" for t in self_subprocess_targets),
    )

    print("[Q] readiness script imports no os/network/db/connector module")
    found_forbidden_self_imports = [
        m for m in FORBIDDEN_SELF_IMPORTS
        if re.search(r"^\s*import\s+" + re.escape(m) + r"\b", self_text, flags=re.MULTILINE)
        or re.search(r"^\s*from\s+" + re.escape(m) + r"\b", self_text, flags=re.MULTILINE)
    ]
    check(
        f"Q. readiness script imports no os/network/db/connector module（found {found_forbidden_self_imports}）"
        if found_forbidden_self_imports
        else "Q. readiness script imports no os/network/db/connector module",
        not found_forbidden_self_imports,
    )

    print("[R] patches/ remains untracked")
    patches_tracked = git_lines(["ls-files", "--", "patches/"])
    check(
        f"R. patches/ remains untracked（found tracked {patches_tracked}）"
        if patches_tracked
        else "R. patches/ remains untracked",
        not patches_tracked,
    )

    print("[S] no tag at HEAD")
    tags_at_head = git_lines(["tag", "--points-at", "HEAD"])
    check(
        f"S. no tag at HEAD（found {tags_at_head}）" if tags_at_head else "S. no tag at HEAD",
        not tags_at_head,
    )

    print("[T] cached diff gate: staged diff is empty or exactly the allowed v0.9.6-C files")
    cached_diff_ok = (not staged_files) or (staged_files == ALLOWED_STAGED_FILES)
    check(
        f"T. cached diff gate: staged diff is empty or exactly the allowed v0.9.6-C files（found {sorted(staged_files)}）"
        if not cached_diff_ok
        else "T. cached diff gate: staged diff is empty or exactly the allowed v0.9.6-C files",
        cached_diff_ok,
    )

    total = len(PASS) + len(FAIL)
    print(f"\nv0.9.6-C Result Feedback Display Plan readiness")
    print(f"合計：{len(PASS)}/{total} 通過")
    if FAIL:
        print(f"\nXX v0.9.6-C readiness 失敗 {len(FAIL)} 項：")
        for f in FAIL:
            print(f"   - {f}")
        print("Final result: FAIL")
        sys.exit(1)
    else:
        print("Final result: PASS")
        sys.exit(0)


if __name__ == "__main__":
    main()
