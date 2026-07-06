"""v0.9.5-B readiness check: Limited Connector Trial Scope Selection.

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

DOC_REL = "docs/HERMES_LIMITED_CONNECTOR_TRIAL_SCOPE_SELECTION_V0_9_5_B.md"
DOC_PATH = REPO_ROOT / DOC_REL

SELF_SCRIPT_REL = "scripts/check_hermes_limited_connector_trial_scope_selection_v0_9_5_b.py"
SELF_SCRIPT_PATH = REPO_ROOT / SELF_SCRIPT_REL

ALLOWED_STAGED_FILES = {DOC_REL, SELF_SCRIPT_REL}

FORBIDDEN_RUNTIME_FILES = (
    MAIN_PY_REL,
    SYSTEM_HTML_REL,
    DASHBOARD_CSS_REL,
    CLAUDE_MD_REL,
)

REQUIRED_PHASE_TITLE = "v0.9.5-B Limited Connector Trial Scope Selection"

REQUIRED_OWNER_FIELDS = (
    "connector name",
    "exact allowed operation",
    "read-only vs write-capable classification",
    "data scope",
    "time range",
    "max result count",
    "whether private content may be read",
    "whether only metadata may be read",
    "forbidden actions",
    "expected output format",
    "stop condition",
    "rollback note",
    "audit note",
    "safety classification",
    "Owner approval statement",
)

REQUIRED_DOC_SUBSTRINGS = (
    "v0.9.5-B is L0 documentation-only / check-only.",
    "v0.9.5-B does not authorize connector execution.",
    "v0.9.5-B does not authorize L1 metadata preview.",
    "v0.9.5-B does not authorize L2 content preview.",
    "This phase must not select the actual connector.",
    "Ambiguous operations fail closed.",
    "Read-only metadata preview requires later Owner instruction.",
    "Content preview requires later Owner instruction.",
    "Write-capable actions remain out of scope by default.",
    "No Dashboard controls, POST, form, button, or action URL are added in this phase.",
    "No Hermes runtime activation occurs in this phase.",
    "No Worker call occurs in this phase.",
    "No OpenClaw call occurs in this phase.",
    "No Blackboard write occurs in this phase.",
    "No queue write occurs in this phase.",
    "No audit trail write occurs in this phase.",
    "No production/shared DB or Remote Blackboard API runtime is created in this phase.",
    "v0.9.5-C",
    "v0.9.5-D",
    "v0.9.5-E",
    "v0.9.5-R",
)

FORBIDDEN_FORBIDDEN_ACTION_PHRASES = (
    "send email",
    "create draft",
    "send draft",
    "forward email",
    "archive email",
    "delete email",
    "apply Gmail label",
    "bulk label matching emails",
    "create calendar event",
    "update calendar event",
    "delete calendar event",
    "respond calendar invitation",
    "write Google Drive",
    "write Google Sheets",
    "write Slack",
    "write GitHub issue / PR / commit",
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

    print("[A] v0.9.5-B doc exists")
    check("A. v0.9.5-B doc exists", DOC_PATH.is_file())

    print("[B] v0.9.5-B readiness script exists")
    check("B. v0.9.5-B readiness script exists", SELF_SCRIPT_PATH.is_file())

    print("[C] doc contains exact phase title")
    check("C. doc contains exact phase title", REQUIRED_PHASE_TITLE in doc_text)

    print("[D] doc contains all required safety/definition substrings")
    missing_substrings = [s for s in REQUIRED_DOC_SUBSTRINGS if s not in doc_text]
    check(
        f"D. doc contains all required safety/definition substrings（missing {missing_substrings}）"
        if missing_substrings
        else "D. doc contains all required safety/definition substrings",
        not missing_substrings,
    )

    print("[E] doc defines all required Owner-specified scope fields")
    missing_fields = [f for f in REQUIRED_OWNER_FIELDS if f not in doc_text]
    check(
        f"E. doc defines all required Owner-specified scope fields（missing {missing_fields}）"
        if missing_fields
        else "E. doc defines all required Owner-specified scope fields",
        not missing_fields,
    )

    print("[F] doc lists forbidden-by-default write/external actions")
    missing_forbidden_phrases = [p for p in FORBIDDEN_FORBIDDEN_ACTION_PHRASES if p not in doc_text]
    check(
        f"F. doc lists forbidden-by-default write/external actions（missing {missing_forbidden_phrases}）"
        if missing_forbidden_phrases
        else "F. doc lists forbidden-by-default write/external actions",
        not missing_forbidden_phrases,
    )

    print("[G] only allowed v0.9.5-B files are staged")
    staged_files = set(git_lines(["diff", "--cached", "--name-only"]))
    unexpected_staged = sorted(staged_files - ALLOWED_STAGED_FILES)
    check(
        f"G. only allowed v0.9.5-B files are staged（unexpected {unexpected_staged}）"
        if unexpected_staged
        else "G. only allowed v0.9.5-B files are staged",
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
    runtime_path_markers = ("routes", "endpoint", "webhook", "connector")
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

    print("[N] no forbidden connector/action keywords appear as implementation in this script")
    found_action_keywords = [kw for kw in FORBIDDEN_CONNECTOR_ACTION_KEYWORDS if kw in self_text]
    check(
        f"N. no forbidden connector/action keywords appear as implementation in this script（found {found_action_keywords}）"
        if found_action_keywords
        else "N. no forbidden connector/action keywords appear as implementation in this script",
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

    print("[T] cached diff gate: staged diff is empty or exactly the allowed v0.9.5-B files")
    cached_diff_ok = (not staged_files) or (staged_files == ALLOWED_STAGED_FILES)
    check(
        f"T. cached diff gate: staged diff is empty or exactly the allowed v0.9.5-B files（found {sorted(staged_files)}）"
        if not cached_diff_ok
        else "T. cached diff gate: staged diff is empty or exactly the allowed v0.9.5-B files",
        cached_diff_ok,
    )

    total = len(PASS) + len(FAIL)
    print(f"\nv0.9.5-B Limited Connector Trial Scope Selection readiness")
    print(f"合計：{len(PASS)}/{total} 通過")
    if FAIL:
        print(f"\nXX v0.9.5-B readiness 失敗 {len(FAIL)} 項：")
        for f in FAIL:
            print(f"   - {f}")
        print("Final result: FAIL")
        sys.exit(1)
    else:
        print("Final result: PASS")
        sys.exit(0)


if __name__ == "__main__":
    main()
