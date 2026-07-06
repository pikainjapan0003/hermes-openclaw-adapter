"""v0.9.5-A readiness check: Limited Connector Trial Boundary Plan.

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

DOC_REL = "docs/HERMES_LIMITED_CONNECTOR_TRIAL_BOUNDARY_PLAN_V0_9_5_A.md"
DOC_PATH = REPO_ROOT / DOC_REL

SELF_SCRIPT_REL = "scripts/check_hermes_limited_connector_trial_boundary_plan_v0_9_5_a.py"
SELF_SCRIPT_PATH = REPO_ROOT / SELF_SCRIPT_REL

BASELINE_REFRESH_COMMIT = "52e96bec19bb78ceceb1996af703c2d12128d2bc"

ALLOWED_STAGED_FILES = {DOC_REL, SELF_SCRIPT_REL}

FORBIDDEN_RUNTIME_FILES = (
    MAIN_PY_REL,
    SYSTEM_HTML_REL,
    DASHBOARD_CSS_REL,
    CLAUDE_MD_REL,
)

REQUIRED_PHASE_TITLE = "v0.9.5-A Limited Connector Trial Boundary Plan"
REQUIRED_CORRECTION_SENTENCE = "This phase must not be called Limited External Action Plan."

REQUIRED_DOC_SUBSTRINGS = (
    "Limited Connector Trial Boundary Plan",
    "L0",
    "L1",
    "L2",
    "v0.9.5-A is L0 only.",
    "v0.9.5-A does not authorize L1.",
    "v0.9.5-A does not authorize L2.",
    "No connector call is performed in this phase.",
    "No connector metadata read is performed in this phase.",
    "No connector content read is performed in this phase.",
    "No connector write is performed in this phase.",
    "No external side effects are performed in this phase.",
    "Owner approval is required for every connector scope.",
    "Owner approval is required for every connector action.",
    "Ambiguous permission must fail closed.",
    "No Dashboard controls, POST, form, button, or action URL are added in this phase.",
    "No Hermes runtime activation occurs in this phase.",
    "No Worker call occurs in this phase.",
    "No OpenClaw call occurs in this phase.",
    "No Blackboard write occurs in this phase.",
    "No queue write occurs in this phase.",
    "No audit trail write occurs in this phase.",
    "No production/shared DB or Remote Blackboard API runtime is created in this phase.",
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

    print("[A] v0.9.5-A doc exists")
    check("A. v0.9.5-A doc exists", DOC_PATH.is_file())

    print("[B] v0.9.5-A readiness script exists")
    check("B. v0.9.5-A readiness script exists", SELF_SCRIPT_PATH.is_file())

    print("[C] doc contains exact phase title")
    check(
        "C. doc contains exact phase title",
        REQUIRED_PHASE_TITLE in doc_text,
    )

    print("[D] doc contains 'Limited Connector Trial Boundary Plan'")
    check(
        "D. doc contains 'Limited Connector Trial Boundary Plan'",
        "Limited Connector Trial Boundary Plan" in doc_text,
    )

    print("[E] doc does not use 'Limited External Action Plan' as the phase name")
    title_line = next((line for line in doc_text.splitlines() if line.strip()), "")
    title_is_wrong_name = title_line.strip().lstrip("# ").strip() == "Limited External Action Plan"
    has_correction_sentence = REQUIRED_CORRECTION_SENTENCE in doc_text
    check(
        "E. doc does not use 'Limited External Action Plan' as the phase name",
        (not title_is_wrong_name) and has_correction_sentence,
    )

    print("[F] doc contains all required safety/definition substrings")
    missing_substrings = [s for s in REQUIRED_DOC_SUBSTRINGS if s not in doc_text]
    check(
        f"F. doc contains all required safety/definition substrings（missing {missing_substrings}）"
        if missing_substrings
        else "F. doc contains all required safety/definition substrings",
        not missing_substrings,
    )

    print("[G] intervening baseline commit inspected and accepted as docs/check-only")
    baseline_commit_files = git_lines(["show", "--name-only", "--format=", BASELINE_REFRESH_COMMIT])
    baseline_touches_forbidden = sorted(set(baseline_commit_files) & set(FORBIDDEN_RUNTIME_FILES))
    baseline_referenced_in_doc = BASELINE_REFRESH_COMMIT in doc_text
    check(
        "G. intervening baseline commit inspected and accepted as docs/check-only"
        if (not baseline_touches_forbidden and baseline_referenced_in_doc)
        else (
            "G. intervening baseline commit inspected and accepted as docs/check-only"
            f"（touched_forbidden={baseline_touches_forbidden}, referenced_in_doc={baseline_referenced_in_doc}）"
        ),
        not baseline_touches_forbidden and baseline_referenced_in_doc,
    )

    print("[H] only allowed v0.9.5-A files are staged")
    staged_files = set(git_lines(["diff", "--cached", "--name-only"]))
    unexpected_staged = sorted(staged_files - ALLOWED_STAGED_FILES)
    check(
        f"H. only allowed v0.9.5-A files are staged（unexpected {unexpected_staged}）"
        if unexpected_staged
        else "H. only allowed v0.9.5-A files are staged",
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

    print("[N] no route/endpoint/webhook/connector runtime file is staged")
    runtime_path_markers = ("routes", "endpoint", "webhook", "connector")
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

    print("[O] no forbidden connector/action keywords appear as implementation in this script")
    found_action_keywords = [kw for kw in FORBIDDEN_CONNECTOR_ACTION_KEYWORDS if kw in self_text]
    check(
        f"O. no forbidden connector/action keywords appear as implementation in this script（found {found_action_keywords}）"
        if found_action_keywords
        else "O. no forbidden connector/action keywords appear as implementation in this script",
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

    print("[U] cached diff gate: staged diff is empty or exactly the allowed v0.9.5-A files")
    cached_diff_ok = (not staged_files) or (staged_files == ALLOWED_STAGED_FILES)
    check(
        f"U. cached diff gate: staged diff is empty or exactly the allowed v0.9.5-A files（found {sorted(staged_files)}）"
        if not cached_diff_ok
        else "U. cached diff gate: staged diff is empty or exactly the allowed v0.9.5-A files",
        cached_diff_ok,
    )

    total = len(PASS) + len(FAIL)
    print(f"\nv0.9.5-A Limited Connector Trial Boundary Plan readiness")
    print(f"合計：{len(PASS)}/{total} 通過")
    if FAIL:
        print(f"\nXX v0.9.5-A readiness 失敗 {len(FAIL)} 項：")
        for f in FAIL:
            print(f"   - {f}")
        print("Final result: FAIL")
        sys.exit(1)
    else:
        print("Final result: PASS")
        sys.exit(0)


if __name__ == "__main__":
    main()
