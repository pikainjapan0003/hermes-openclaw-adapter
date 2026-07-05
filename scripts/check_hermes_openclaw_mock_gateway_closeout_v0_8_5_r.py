"""v0.8.5-R readiness check: OpenClaw Mock Gateway Closeout.

Pure local filesystem + git metadata validation, standard library only. This script does
NOT modify any file, does NOT start a server, sends no POST, makes no network call, reads
no secrets, reads no real queue DB, writes no queue, writes no audit trail, and does not
call Worker/OpenClaw/Hermes/Google Sheets. Its only subprocess use is read-only git
plumbing (rev-parse, status, diff, ls-files, tag).
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

DOC_REL = "docs/HERMES_OPENCLAW_MOCK_GATEWAY_CLOSEOUT_V0_8_5_R.md"
DOC_PATH = REPO_ROOT / DOC_REL

SELF_SCRIPT_REL = "scripts/check_hermes_openclaw_mock_gateway_closeout_v0_8_5_r.py"
SELF_SCRIPT_PATH = REPO_ROOT / SELF_SCRIPT_REL

A_DOC_REL = "docs/HERMES_OPENCLAW_COMMAND_ENVELOPE_PLAN_V0_8_5_A.md"
A_SCRIPT_REL = "scripts/check_hermes_openclaw_command_envelope_plan_v0_8_5_a.py"

B_DOC_REL = "docs/HERMES_OPENCLAW_MOCK_GATEWAY_HELPER_V0_8_5_B.md"
B_HELPER_REL = "app/mock_openclaw_gateway.py"
B_SCRIPT_REL = "scripts/check_hermes_openclaw_mock_gateway_helper_v0_8_5_b.py"

C_DOC_REL = "docs/HERMES_OPENCLAW_WORKER_MOCK_GATEWAY_DRY_RUN_V0_8_5_C.md"
C_HELPER_REL = "app/worker_mock_gateway_dry_run.py"
C_SCRIPT_REL = "scripts/check_hermes_openclaw_worker_mock_gateway_dry_run_v0_8_5_c.py"

D_DOC_REL = "docs/HERMES_OPENCLAW_DASHBOARD_MOCK_RESULT_VIEW_V0_8_5_D.md"
D_SCRIPT_REL = "scripts/check_hermes_openclaw_dashboard_mock_result_view_v0_8_5_d.py"

# HEAD at the start of this round, before any v0.8.5-R file was added.
EXPECTED_BASE_HEAD = "830b8d3ea9d90481cab213c678ae55de5f3eb814"

REQUIRED_DOC_SAFETY_SENTENCES = (
    "OpenClaw mock gateway closeout is not production readiness.",
    "Mock gateway is not production gateway.",
    "Command envelope is not an OpenClaw call.",
    "Worker to mock gateway dry-run is not Worker execution.",
    "Dashboard mock result view is not execution permission.",
    "Mock result preview is not actual execution result.",
    "Mock result preview is not audit trail persistence.",
    "Mock result preview is not queue write.",
    "Owner approval is not Worker execution.",
    "Decision event is not dispatch.",
    "External side effects remain forbidden by default.",
)

REQUIRED_DOC_PHASE_LABELS = (
    "v0.8.5-A",
    "v0.8.5-B",
    "v0.8.5-C",
    "v0.8.5-D",
    "v0.8.5-R",
)

FORBIDDEN_RUNTIME_FILES = (
    MAIN_PY_REL,
    SYSTEM_HTML_REL,
    DASHBOARD_CSS_REL,
    CLAUDE_MD_REL,
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

    print("[A] v0.8.5-R closeout doc exists")
    check("A. v0.8.5-R closeout doc exists", DOC_PATH.is_file())

    print("[B] v0.8.5-R readiness script exists")
    check("B. v0.8.5-R readiness script exists", SELF_SCRIPT_PATH.is_file())

    print("[C] v0.8.5-A doc exists")
    check("C. v0.8.5-A doc exists", (REPO_ROOT / A_DOC_REL).is_file())

    print("[D] v0.8.5-A readiness script exists")
    check("D. v0.8.5-A readiness script exists", (REPO_ROOT / A_SCRIPT_REL).is_file())

    print("[E] v0.8.5-B doc exists")
    check("E. v0.8.5-B doc exists", (REPO_ROOT / B_DOC_REL).is_file())

    print("[F] v0.8.5-B mock gateway helper exists")
    check("F. v0.8.5-B mock gateway helper exists", (REPO_ROOT / B_HELPER_REL).is_file())

    print("[G] v0.8.5-B readiness script exists")
    check("G. v0.8.5-B readiness script exists", (REPO_ROOT / B_SCRIPT_REL).is_file())

    print("[H] v0.8.5-C doc exists")
    check("H. v0.8.5-C doc exists", (REPO_ROOT / C_DOC_REL).is_file())

    print("[I] v0.8.5-C worker-to-mock-gateway dry-run helper exists")
    check("I. v0.8.5-C worker-to-mock-gateway dry-run helper exists", (REPO_ROOT / C_HELPER_REL).is_file())

    print("[J] v0.8.5-C readiness script exists")
    check("J. v0.8.5-C readiness script exists", (REPO_ROOT / C_SCRIPT_REL).is_file())

    print("[K] v0.8.5-D doc exists")
    check("K. v0.8.5-D doc exists", (REPO_ROOT / D_DOC_REL).is_file())

    print("[L] v0.8.5-D readiness script exists")
    check("L. v0.8.5-D readiness script exists", (REPO_ROOT / D_SCRIPT_REL).is_file())

    print("[M] app/main.py exists")
    check("M. app/main.py exists", (REPO_ROOT / MAIN_PY_REL).is_file())

    print("[N] templates/system.html exists")
    check("N. templates/system.html exists", (REPO_ROOT / SYSTEM_HTML_REL).is_file())

    print("[O] static/dashboard.css exists")
    check("O. static/dashboard.css exists", (REPO_ROOT / DASHBOARD_CSS_REL).is_file())

    print("[P] closeout doc contains required safety sentences")
    missing_sentences = [s for s in REQUIRED_DOC_SAFETY_SENTENCES if s not in doc_text]
    check(
        f"P. closeout doc contains required safety sentences（missing {missing_sentences}）"
        if missing_sentences
        else "P. closeout doc contains required safety sentences",
        not missing_sentences,
    )

    print("[Q] closeout doc contains v0.8.5-A/B/C/D/R phase labels")
    missing_labels = [label for label in REQUIRED_DOC_PHASE_LABELS if label not in doc_text]
    check(
        f"Q. closeout doc contains v0.8.5-A/B/C/D/R phase labels（missing {missing_labels}）"
        if missing_labels
        else "Q. closeout doc contains v0.8.5-A/B/C/D/R phase labels",
        not missing_labels,
    )

    print("[R] closeout doc contains latest base HEAD")
    check(
        "R. closeout doc contains latest base HEAD",
        EXPECTED_BASE_HEAD in doc_text,
    )

    print("[S] forbidden runtime files absent from working diff and staged diff")
    working_diff_files = set(git_lines(["diff", "--name-only"]))
    staged_diff_files = set(git_lines(["diff", "--cached", "--name-only"]))
    touched_forbidden = sorted(
        (working_diff_files | staged_diff_files) & set(FORBIDDEN_RUNTIME_FILES)
    )
    check(
        f"S. forbidden runtime files absent from working diff and staged diff（found {touched_forbidden}）"
        if touched_forbidden
        else "S. forbidden runtime files absent from working diff and staged diff",
        not touched_forbidden,
    )

    # -----------------------------------------------------------------
    print("[T] readiness script only invokes read-only git plumbing as subprocess")
    self_text = read_text(SELF_SCRIPT_PATH)
    self_subprocess_targets = re.findall(r'subprocess\.run\(\s*\[\s*"([^"]+)"', self_text)
    check(
        f"T. readiness script only invokes read-only git plumbing as subprocess（found {self_subprocess_targets}）"
        if any(t != "git" for t in self_subprocess_targets)
        else "T. readiness script only invokes read-only git plumbing as subprocess",
        all(t == "git" for t in self_subprocess_targets),
    )

    print("[U] readiness script imports no os/network/db module")
    forbidden_imports = ("os", "socket", "requests", "httpx", "urllib", "sqlite3")
    found_forbidden_imports = [
        m for m in forbidden_imports
        if re.search(r"^\s*import\s+" + re.escape(m) + r"\b", self_text, flags=re.MULTILINE)
        or re.search(r"^\s*from\s+" + re.escape(m) + r"\b", self_text, flags=re.MULTILINE)
    ]
    check(
        f"U. readiness script imports no os/network/db module（found {found_forbidden_imports}）"
        if found_forbidden_imports
        else "U. readiness script imports no os/network/db module",
        not found_forbidden_imports,
    )

    print("[V] patches/ remains untracked")
    patches_tracked = git_lines(["ls-files", "--", "patches/"])
    check(
        f"V. patches/ remains untracked（found tracked {patches_tracked}）"
        if patches_tracked
        else "V. patches/ remains untracked",
        not patches_tracked,
    )

    print("[W] no tag at HEAD")
    tags_at_head = git_lines(["tag", "--points-at", "HEAD"])
    check(
        f"W. no tag at HEAD（found {tags_at_head}）" if tags_at_head else "W. no tag at HEAD",
        not tags_at_head,
    )

    # -----------------------------------------------------------------
    total = len(PASS) + len(FAIL)
    print(f"\n合計：{len(PASS)}/{total} 通過")
    if FAIL:
        print(f"\nXX v0.8.5-R readiness 失敗 {len(FAIL)} 項：")
        for f in FAIL:
            print(f"   - {f}")
        sys.exit(1)
    else:
        print("PASS: v0.8.5-R OpenClaw mock gateway closeout")
        sys.exit(0)


if __name__ == "__main__":
    main()
