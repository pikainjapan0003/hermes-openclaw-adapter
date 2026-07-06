"""v0.9.5-R readiness check: Limited Connector Trial Closeout.

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

DOC_REL = "docs/HERMES_LIMITED_CONNECTOR_TRIAL_CLOSEOUT_V0_9_5_R.md"
DOC_PATH = REPO_ROOT / DOC_REL

SELF_SCRIPT_REL = "scripts/check_hermes_limited_connector_trial_closeout_v0_9_5_r.py"
SELF_SCRIPT_PATH = REPO_ROOT / SELF_SCRIPT_REL

A_DOC_REL = "docs/HERMES_LIMITED_CONNECTOR_TRIAL_BOUNDARY_PLAN_V0_9_5_A.md"
A_SCRIPT_REL = "scripts/check_hermes_limited_connector_trial_boundary_plan_v0_9_5_a.py"

B_DOC_REL = "docs/HERMES_LIMITED_CONNECTOR_TRIAL_SCOPE_SELECTION_V0_9_5_B.md"
B_SCRIPT_REL = "scripts/check_hermes_limited_connector_trial_scope_selection_v0_9_5_b.py"

C_DOC_REL = "docs/HERMES_SINGLE_CONNECTOR_METADATA_PREVIEW_GATE_V0_9_5_C.md"
C_SCRIPT_REL = "scripts/check_hermes_single_connector_metadata_preview_gate_v0_9_5_c.py"

D_DOC_REL = "docs/HERMES_CONNECTOR_TRIAL_DASHBOARD_READ_ONLY_VIEW_BOUNDARY_V0_9_5_D.md"
D_SCRIPT_REL = "scripts/check_hermes_connector_trial_dashboard_read_only_view_boundary_v0_9_5_d.py"

ALLOWED_STAGED_FILES = {DOC_REL, SELF_SCRIPT_REL}

FORBIDDEN_RUNTIME_FILES = (
    MAIN_PY_REL,
    SYSTEM_HTML_REL,
    DASHBOARD_CSS_REL,
    CLAUDE_MD_REL,
)

REQUIRED_PHASE_TITLE = "v0.9.5-R Limited Connector Trial Closeout"

REQUIRED_SEQUENCE_LABELS = (
    "v0.9.5-A",
    "v0.9.5-B",
    "v0.9.5-C",
    "v0.9.5-D",
)

REQUIRED_SCOPE_PACKET_FIELDS = (
    "connector name",
    "exact allowed operation",
    "read-only metadata only statement",
    "explicit no-content-read statement",
    "data scope",
    "time range",
    "max result count",
    "allowed metadata fields",
    "forbidden metadata fields",
    "private content exclusion",
    "expected output format",
    "stop condition",
    "rollback note",
    "audit note",
    "safety classification",
    "Owner approval statement",
)

REQUIRED_DOC_SUBSTRINGS = (
    "v0.9.5-R is docs / check-only closeout.",
    "v0.9.5-E Connector Content Preview Gate not started.",
    "v0.9.6 not started.",
    "no real connector trial started",
    "no connector selected",
    "no connector called",
    "no connector metadata read",
    "no connector content read",
    "no connector write",
    "no external side effects",
    "no Dashboard implementation",
    "no Dashboard controls",
    "no POST/form/button/action URL",
    "no Hermes runtime activation",
    "no Worker call",
    "no OpenClaw call",
    "no Blackboard write",
    "no queue write",
    "no audit trail write",
    "no production/shared DB or Remote Blackboard API runtime",
    "v0.9.5 completed only L0 boundary/gate work.",
    "v0.9.5 did not authorize L1.",
    "v0.9.5 did not authorize L2.",
    "any L1 metadata preview requires separate Owner instruction",
    "any L2 content preview requires separate Owner instruction",
    "any write-capable action remains out of scope by default",
)

REQUIRED_ARTIFACT_PATHS = (
    A_DOC_REL,
    A_SCRIPT_REL,
    B_DOC_REL,
    B_SCRIPT_REL,
    C_DOC_REL,
    C_SCRIPT_REL,
    D_DOC_REL,
    D_SCRIPT_REL,
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

    print("[A] v0.9.5-R closeout doc exists")
    check("A. v0.9.5-R closeout doc exists", DOC_PATH.is_file())

    print("[B] v0.9.5-R readiness script exists")
    check("B. v0.9.5-R readiness script exists", SELF_SCRIPT_PATH.is_file())

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

    print("[E] doc lists v0.9.5-A/B/C/D as completed sequence")
    missing_labels = [label for label in REQUIRED_SEQUENCE_LABELS if label not in doc_text]
    check(
        f"E. doc lists v0.9.5-A/B/C/D as completed sequence（missing {missing_labels}）"
        if missing_labels
        else "E. doc lists v0.9.5-A/B/C/D as completed sequence",
        not missing_labels,
    )

    print("[F] doc lists all v0.9.5-A/B/C/D artifacts")
    missing_artifacts = [p for p in REQUIRED_ARTIFACT_PATHS if p not in doc_text]
    check(
        f"F. doc lists all v0.9.5-A/B/C/D artifacts（missing {missing_artifacts}）"
        if missing_artifacts
        else "F. doc lists all v0.9.5-A/B/C/D artifacts",
        not missing_artifacts,
    )

    print("[G] doc defines required future Owner scope packet fields")
    missing_fields = [f for f in REQUIRED_SCOPE_PACKET_FIELDS if f not in doc_text]
    check(
        f"G. doc defines required future Owner scope packet fields（missing {missing_fields}）"
        if missing_fields
        else "G. doc defines required future Owner scope packet fields",
        not missing_fields,
    )

    print("[H] doc includes safe next recommendation")
    check("H. doc includes safe next recommendation", "Safe Next Recommendation" in doc_text)

    print("[I] all v0.9.5-A/B/C/D artifact files actually exist on disk")
    missing_artifact_files = [p for p in REQUIRED_ARTIFACT_PATHS if not (REPO_ROOT / p).is_file()]
    check(
        f"I. all v0.9.5-A/B/C/D artifact files actually exist on disk（missing {missing_artifact_files}）"
        if missing_artifact_files
        else "I. all v0.9.5-A/B/C/D artifact files actually exist on disk",
        not missing_artifact_files,
    )

    print("[J] only allowed v0.9.5-R files are staged")
    staged_files = set(git_lines(["diff", "--cached", "--name-only"]))
    unexpected_staged = sorted(staged_files - ALLOWED_STAGED_FILES)
    check(
        f"J. only allowed v0.9.5-R files are staged（unexpected {unexpected_staged}）"
        if unexpected_staged
        else "J. only allowed v0.9.5-R files are staged",
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

    print("[P] no route/endpoint/webhook/connector runtime file is staged")
    runtime_path_markers = ("routes", "endpoint", "webhook", "connector")
    suspicious_staged = sorted(
        f for f in staged_files
        if f not in ALLOWED_STAGED_FILES and any(marker in f.lower() for marker in runtime_path_markers)
    )
    check(
        f"P. no route/endpoint/webhook/connector runtime file is staged（found {suspicious_staged}）"
        if suspicious_staged
        else "P. no route/endpoint/webhook/connector runtime file is staged",
        not suspicious_staged,
    )

    print("[Q] no forbidden connector/action keywords appear as implementation in this script")
    found_action_keywords = [kw for kw in FORBIDDEN_CONNECTOR_ACTION_KEYWORDS if kw in self_text]
    check(
        f"Q. no forbidden connector/action keywords appear as implementation in this script（found {found_action_keywords}）"
        if found_action_keywords
        else "Q. no forbidden connector/action keywords appear as implementation in this script",
        not found_action_keywords,
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

    print("[T] readiness script imports no os/network/db/connector module")
    found_forbidden_self_imports = [
        m for m in FORBIDDEN_SELF_IMPORTS
        if re.search(r"^\s*import\s+" + re.escape(m) + r"\b", self_text, flags=re.MULTILINE)
        or re.search(r"^\s*from\s+" + re.escape(m) + r"\b", self_text, flags=re.MULTILINE)
    ]
    check(
        f"T. readiness script imports no os/network/db/connector module（found {found_forbidden_self_imports}）"
        if found_forbidden_self_imports
        else "T. readiness script imports no os/network/db/connector module",
        not found_forbidden_self_imports,
    )

    print("[U] patches/ remains untracked")
    patches_tracked = git_lines(["ls-files", "--", "patches/"])
    check(
        f"U. patches/ remains untracked（found tracked {patches_tracked}）"
        if patches_tracked
        else "U. patches/ remains untracked",
        not patches_tracked,
    )

    print("[V] no tag at HEAD")
    tags_at_head = git_lines(["tag", "--points-at", "HEAD"])
    check(
        f"V. no tag at HEAD（found {tags_at_head}）" if tags_at_head else "V. no tag at HEAD",
        not tags_at_head,
    )

    print("[W] cached diff gate: staged diff is empty or exactly the allowed v0.9.5-R files")
    cached_diff_ok = (not staged_files) or (staged_files == ALLOWED_STAGED_FILES)
    check(
        f"W. cached diff gate: staged diff is empty or exactly the allowed v0.9.5-R files（found {sorted(staged_files)}）"
        if not cached_diff_ok
        else "W. cached diff gate: staged diff is empty or exactly the allowed v0.9.5-R files",
        cached_diff_ok,
    )

    total = len(PASS) + len(FAIL)
    print(f"\nv0.9.5-R Limited Connector Trial Closeout readiness")
    print(f"合計：{len(PASS)}/{total} 通過")
    if FAIL:
        print(f"\nXX v0.9.5-R readiness 失敗 {len(FAIL)} 項：")
        for f in FAIL:
            print(f"   - {f}")
        print("Final result: FAIL")
        sys.exit(1)
    else:
        print("Final result: PASS")
        sys.exit(0)


if __name__ == "__main__":
    main()
