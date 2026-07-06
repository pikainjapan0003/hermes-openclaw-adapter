"""v1.0-RC-B readiness check: Full Loop Preview Adapter Plan.

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
FIXTURES_DIR_REL = "fixtures/local_mock_data/"

DOC_REL = "docs/HERMES_FULL_LOOP_PREVIEW_ADAPTER_PLAN_V1_0_RC_B.md"
DOC_PATH = REPO_ROOT / DOC_REL

SELF_SCRIPT_REL = "scripts/check_hermes_full_loop_preview_adapter_plan_v1_0_rc_b.py"
SELF_SCRIPT_PATH = REPO_ROOT / SELF_SCRIPT_REL

ALLOWED_STAGED_FILES = {DOC_REL, SELF_SCRIPT_REL}

FORBIDDEN_RUNTIME_FILES = (
    MAIN_PY_REL,
    SYSTEM_HTML_REL,
    DASHBOARD_CSS_REL,
    RESULT_FEEDBACK_PREVIEW_REL,
    CLAUDE_MD_REL,
)

REQUIRED_PHASE_TITLE = "v1.0-RC-B Full Loop Preview Adapter Plan"

REQUIRED_SECTION_HEADINGS = (
    "Future Adapter File Recommendation",
    "Future Adapter Fixture Input Recommendation",
    "Future Adapter Output Recommendation",
    "Future Adapter Responsibilities",
    "Future Adapter Forbidden Responsibilities",
    "Required Adapter Input Checks",
    "Required Timeline Validation Checks",
    "Required Display-Safe Output Fields",
    "Required Output Labels",
    "Future Adapter Fail-Closed Rules",
    "Future Adapter Import Boundary",
    "Future Dashboard Boundary",
)

REQUIRED_SEQUENCE_LABELS = (
    "v1.0-RC-C",
    "v1.0-RC-D",
    "v1.0-RC-E",
    "v1.0-RC-R",
)

REQUIRED_DOC_SUBSTRINGS = (
    "v1.0-RC-B is docs / check-only adapter plan.",
    "v1.0-RC-B does not create fixture file.",
    "No preview adapter implementation occurs in this phase.",
    "No Full Blackboard Loop implementation occurs in this phase.",
    "No Dashboard timeline display implementation occurs in this phase.",
    "No Dashboard controls are added in this phase.",
    "No Hermes runtime activation occurs in this phase.",
    "No Worker dispatch occurs in this phase.",
    "No OpenClaw call occurs in this phase.",
    "No Blackboard write occurs in this phase.",
    "No queue write occurs in this phase.",
    "No audit trail write occurs in this phase.",
    "No connector call occurs in this phase.",
    "No external side effects occur in this phase.",
    "external_side_effects_allowed is false",
    "blackboard_write_allowed is false",
    "queue_write_allowed is false",
    "audit_trail_write_allowed is false",
    "worker_dispatch_allowed is false",
    "openclaw_call_allowed is false",
    "hermes_runtime_allowed is false",
    "connector_call_allowed is false",
    "follow_up_task_creation_allowed is false",
    "dashboard_controls_allowed is false",
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

    print("[A] v1.0-RC-B plan doc exists")
    check("A. v1.0-RC-B plan doc exists", DOC_PATH.is_file())

    print("[B] v1.0-RC-B readiness script exists")
    check("B. v1.0-RC-B readiness script exists", SELF_SCRIPT_PATH.is_file())

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

    print("[E] doc defines required section headings (responsibilities/checks/output/labels/fail-closed/import/dashboard)")
    missing_headings = [h for h in REQUIRED_SECTION_HEADINGS if h not in doc_text]
    check(
        f"E. doc defines required section headings（missing {missing_headings}）"
        if missing_headings
        else "E. doc defines required section headings",
        not missing_headings,
    )

    print("[F] doc lists future sequence v1.0-RC-C/D/E/R")
    missing_labels = [label for label in REQUIRED_SEQUENCE_LABELS if label not in doc_text]
    check(
        f"F. doc lists future sequence v1.0-RC-C/D/E/R（missing {missing_labels}）"
        if missing_labels
        else "F. doc lists future sequence v1.0-RC-C/D/E/R",
        not missing_labels,
    )

    print("[G] doc includes safe next recommendation")
    check("G. doc includes safe next recommendation", "Safe Next Recommendation" in doc_text)

    print("[H] adapter file is not created (recommended path does not exist on disk)")
    recommended_adapter_path = REPO_ROOT / "app" / "full_loop_preview_adapter.py"
    check(
        "H. adapter file is not created (recommended path does not exist on disk)",
        not recommended_adapter_path.exists(),
    )

    print("[I] fixture is not created (recommended path does not exist on disk)")
    recommended_fixture_path = (
        REPO_ROOT / "fixtures" / "local_mock_data" / "hermes_full_blackboard_loop_rehearsal_v1_0_rc_d.json"
    )
    check(
        "I. fixture is not created (recommended path does not exist on disk)",
        not recommended_fixture_path.exists(),
    )

    print("[J] only allowed v1.0-RC-B files are staged")
    staged_files = set(git_lines(["diff", "--cached", "--name-only"]))
    unexpected_staged = sorted(staged_files - ALLOWED_STAGED_FILES)
    check(
        f"J. only allowed v1.0-RC-B files are staged（unexpected {unexpected_staged}）"
        if unexpected_staged
        else "J. only allowed v1.0-RC-B files are staged",
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

    print("[M] fixtures/local_mock_data/ is not staged")
    staged_fixtures_dir = [f for f in staged_files if f.startswith(FIXTURES_DIR_REL)]
    check(
        f"M. fixtures/local_mock_data/ is not staged（found {staged_fixtures_dir}）"
        if staged_fixtures_dir
        else "M. fixtures/local_mock_data/ is not staged",
        not staged_fixtures_dir,
    )

    print("[N] app/main.py is not staged")
    check("N. app/main.py is not staged", MAIN_PY_REL not in staged_files)

    print("[O] templates/system.html is not staged")
    check("O. templates/system.html is not staged", SYSTEM_HTML_REL not in staged_files)

    print("[P] static/dashboard.css is not staged")
    check("P. static/dashboard.css is not staged", DASHBOARD_CSS_REL not in staged_files)

    print("[Q] app/result_feedback_preview.py is not staged")
    check("Q. app/result_feedback_preview.py is not staged", RESULT_FEEDBACK_PREVIEW_REL not in staged_files)

    print("[R] no route/endpoint/webhook/connector runtime file is staged")
    runtime_path_markers = ("routes", "endpoint", "webhook", "connector", "callback_receiver")
    suspicious_staged = sorted(
        f for f in staged_files
        if f not in ALLOWED_STAGED_FILES and any(marker in f.lower() for marker in runtime_path_markers)
    )
    check(
        f"R. no route/endpoint/webhook/connector runtime file is staged（found {suspicious_staged}）"
        if suspicious_staged
        else "R. no route/endpoint/webhook/connector runtime file is staged",
        not suspicious_staged,
    )

    print("[S] no forbidden runtime/control keywords appear as implementation in this script")
    found_action_keywords = [kw for kw in FORBIDDEN_CONNECTOR_ACTION_KEYWORDS if kw in self_text]
    check(
        f"S. no forbidden runtime/control keywords appear as implementation in this script（found {found_action_keywords}）"
        if found_action_keywords
        else "S. no forbidden runtime/control keywords appear as implementation in this script",
        not found_action_keywords,
    )

    print("[T] forbidden runtime files absent from working diff and staged diff")
    working_diff_files = set(git_lines(["diff", "--name-only"]))
    touched_forbidden = sorted((working_diff_files | staged_files) & set(FORBIDDEN_RUNTIME_FILES))
    check(
        f"T. forbidden runtime files absent from working diff and staged diff（found {touched_forbidden}）"
        if touched_forbidden
        else "T. forbidden runtime files absent from working diff and staged diff",
        not touched_forbidden,
    )

    print("[U] readiness script only invokes read-only git plumbing as subprocess")
    self_subprocess_targets = re.findall(r'subprocess\.run\(\s*\[\s*"([^"]+)"', self_text)
    check(
        f"U. readiness script only invokes read-only git plumbing as subprocess（found {self_subprocess_targets}）"
        if any(t != "git" for t in self_subprocess_targets)
        else "U. readiness script only invokes read-only git plumbing as subprocess",
        all(t == "git" for t in self_subprocess_targets),
    )

    print("[V] readiness script imports no os/network/db/connector module")
    found_forbidden_self_imports = [
        m for m in FORBIDDEN_SELF_IMPORTS
        if re.search(r"^\s*import\s+" + re.escape(m) + r"\b", self_text, flags=re.MULTILINE)
        or re.search(r"^\s*from\s+" + re.escape(m) + r"\b", self_text, flags=re.MULTILINE)
    ]
    check(
        f"V. readiness script imports no os/network/db/connector module（found {found_forbidden_self_imports}）"
        if found_forbidden_self_imports
        else "V. readiness script imports no os/network/db/connector module",
        not found_forbidden_self_imports,
    )

    print("[W] patches/ remains untracked")
    patches_tracked = git_lines(["ls-files", "--", "patches/"])
    check(
        f"W. patches/ remains untracked（found tracked {patches_tracked}）"
        if patches_tracked
        else "W. patches/ remains untracked",
        not patches_tracked,
    )

    print("[X] no tag at HEAD")
    tags_at_head = git_lines(["tag", "--points-at", "HEAD"])
    check(
        f"X. no tag at HEAD（found {tags_at_head}）" if tags_at_head else "X. no tag at HEAD",
        not tags_at_head,
    )

    print("[Y] cached diff gate: staged diff is empty or exactly the allowed v1.0-RC-B files")
    cached_diff_ok = (not staged_files) or (staged_files == ALLOWED_STAGED_FILES)
    check(
        f"Y. cached diff gate: staged diff is empty or exactly the allowed v1.0-RC-B files（found {sorted(staged_files)}）"
        if not cached_diff_ok
        else "Y. cached diff gate: staged diff is empty or exactly the allowed v1.0-RC-B files",
        cached_diff_ok,
    )

    total = len(PASS) + len(FAIL)
    print(f"\nv1.0-RC-B Full Loop Preview Adapter Plan readiness")
    print(f"合計：{len(PASS)}/{total} 通過")
    if FAIL:
        print(f"\nXX v1.0-RC-B readiness 失敗 {len(FAIL)} 項：")
        for f in FAIL:
            print(f"   - {f}")
        print("Final result: FAIL")
        sys.exit(1)
    else:
        print("Final result: PASS")
        sys.exit(0)


if __name__ == "__main__":
    main()
