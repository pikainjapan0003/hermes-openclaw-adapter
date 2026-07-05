"""v0.9-R readiness check: Hermes Strategy Mock Closeout.

Pure local filesystem + git metadata validation, standard library only. This script does
NOT modify any file, does NOT start a server, sends no POST, makes no network call, reads
no secrets, reads no real queue DB, writes no queue, writes no audit trail, and does not
call Worker/OpenClaw/Hermes/Google Sheets. Its only subprocess use is read-only git
plumbing (status, diff, ls-files, tag).

Per Owner instruction, this round intentionally does NOT re-run the v0.9-A/B/C/D/E/F
readiness scripts (each of those has its own "no unexpected untracked files" gate that
would spuriously trip on this round's own still-untracked doc/script before commit —
a structural, self-resolving artifact, not a real defect). This script only checks that
those prior phases' artifacts still *exist*.
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

DOC_REL = "docs/HERMES_STRATEGY_MOCK_CLOSEOUT_V0_9_R.md"
DOC_PATH = REPO_ROOT / DOC_REL

SELF_SCRIPT_REL = "scripts/check_hermes_strategy_mock_closeout_v0_9_r.py"
SELF_SCRIPT_PATH = REPO_ROOT / SELF_SCRIPT_REL

A_DOC_REL = "docs/HERMES_STRATEGY_CONTRACT_PLAN_V0_9_A.md"
A_SCRIPT_REL = "scripts/check_hermes_strategy_contract_plan_v0_9_a.py"

B_DOC_REL = "docs/HERMES_STRATEGY_SUGGESTION_MODEL_V0_9_B.md"
B_MODEL_REL = "app/hermes_strategy_suggestion_model.py"
B_SCRIPT_REL = "scripts/check_hermes_strategy_suggestion_model_v0_9_b.py"

C_DOC_REL = "docs/HERMES_MOCK_GENERATOR_V0_9_C.md"
C_GENERATOR_REL = "app/mock_hermes_generator.py"
C_SCRIPT_REL = "scripts/check_hermes_mock_generator_v0_9_c.py"

D_DOC_REL = "docs/HERMES_DASHBOARD_ADVICE_PANEL_V0_9_D.md"
D_SCRIPT_REL = "scripts/check_hermes_dashboard_advice_panel_v0_9_d.py"

E_DOC_REL = "docs/HERMES_RESULT_READBACK_MOCK_V0_9_E.md"
E_MOCK_REL = "app/hermes_result_readback_mock.py"
E_SCRIPT_REL = "scripts/check_hermes_result_readback_mock_v0_9_e.py"

F_DOC_REL = "docs/HERMES_ACTIVATION_POLICY_INTEGRATION_CHECK_V0_9_F.md"
F_SCRIPT_REL = "scripts/check_hermes_activation_policy_integration_v0_9_f.py"

FORBIDDEN_RUNTIME_FILES = (
    MAIN_PY_REL,
    SYSTEM_HTML_REL,
    DASHBOARD_CSS_REL,
    CLAUDE_MD_REL,
)

REQUIRED_DOC_SAFETY_SENTENCES = (
    "Hermes strategy mock closeout is not Hermes activation.",
    "Hermes remains mock-only and advisory-only.",
    "Hermes suggestion is not Blackboard write.",
    "Hermes advice is not Owner approval.",
    "Hermes readback is not automatic follow-up execution.",
    "Hermes readback is not automatic follow-up task creation.",
    "Hermes strategy suggestion is not Worker dispatch.",
    "Hermes strategy suggestion is not OpenClaw call.",
    "Dashboard Hermes advice panel is read-only.",
    "Hermes cannot bypass Owner Review.",
    "Hermes cannot bypass Blackboard Activation Policy.",
    "External side effects remain forbidden by default.",
)

REQUIRED_DOC_PHASE_LABELS = (
    "v0.9-A",
    "v0.9-B",
    "v0.9-C",
    "v0.9-D",
    "v0.9-E",
    "v0.9-F",
    "v0.9-R",
)

REQUIRED_DOC_POST_STATE_SENTENCES = (
    "Hermes strategy contract exists.",
    "Strategy suggestion model exists.",
    "Mock Hermes generator exists.",
    "Dashboard Hermes advice read-only panel exists.",
    "Hermes result readback mock exists.",
    "Hermes activation policy integration check exists.",
    "Hermes runtime activation remains forbidden.",
    "Owner supervision remains required.",
)

REQUIRED_DOC_NOT_STARTED_SENTENCES = (
    "v0.9-R does not start v0.9.5.",
    "v0.9-R does not start Limited Connector Trial.",
    "v0.9-R does not start Callback Contract.",
)

EXPECTED_BASE_HEAD = "1be0592fb368fec5b4f95c403017b02cc1294404"

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

    print("[A] v0.9-R closeout doc exists")
    check("A. v0.9-R closeout doc exists", DOC_PATH.is_file())

    print("[B] v0.9-R readiness script exists")
    check("B. v0.9-R readiness script exists", SELF_SCRIPT_PATH.is_file())

    print("[C] v0.9-A doc exists")
    check("C. v0.9-A doc exists", (REPO_ROOT / A_DOC_REL).is_file())

    print("[D] v0.9-A readiness script exists")
    check("D. v0.9-A readiness script exists", (REPO_ROOT / A_SCRIPT_REL).is_file())

    print("[E] v0.9-B doc exists")
    check("E. v0.9-B doc exists", (REPO_ROOT / B_DOC_REL).is_file())

    print("[F] v0.9-B model exists")
    check("F. v0.9-B model exists", (REPO_ROOT / B_MODEL_REL).is_file())

    print("[G] v0.9-B readiness script exists")
    check("G. v0.9-B readiness script exists", (REPO_ROOT / B_SCRIPT_REL).is_file())

    print("[H] v0.9-C doc exists")
    check("H. v0.9-C doc exists", (REPO_ROOT / C_DOC_REL).is_file())

    print("[I] v0.9-C mock generator exists")
    check("I. v0.9-C mock generator exists", (REPO_ROOT / C_GENERATOR_REL).is_file())

    print("[J] v0.9-C readiness script exists")
    check("J. v0.9-C readiness script exists", (REPO_ROOT / C_SCRIPT_REL).is_file())

    print("[K] v0.9-D doc exists")
    check("K. v0.9-D doc exists", (REPO_ROOT / D_DOC_REL).is_file())

    print("[L] v0.9-D readiness script exists")
    check("L. v0.9-D readiness script exists", (REPO_ROOT / D_SCRIPT_REL).is_file())

    print("[M] v0.9-E doc exists")
    check("M. v0.9-E doc exists", (REPO_ROOT / E_DOC_REL).is_file())

    print("[N] v0.9-E readback mock exists")
    check("N. v0.9-E readback mock exists", (REPO_ROOT / E_MOCK_REL).is_file())

    print("[O] v0.9-E readiness script exists")
    check("O. v0.9-E readiness script exists", (REPO_ROOT / E_SCRIPT_REL).is_file())

    print("[P] v0.9-F doc exists")
    check("P. v0.9-F doc exists", (REPO_ROOT / F_DOC_REL).is_file())

    print("[Q] v0.9-F readiness script exists")
    check("Q. v0.9-F readiness script exists", (REPO_ROOT / F_SCRIPT_REL).is_file())

    print("[R] closeout doc contains v0.9-A/B/C/D/E/F/R phase labels")
    missing_labels = [label for label in REQUIRED_DOC_PHASE_LABELS if label not in doc_text]
    check(
        f"R. closeout doc contains v0.9-A/B/C/D/E/F/R phase labels（missing {missing_labels}）"
        if missing_labels
        else "R. closeout doc contains v0.9-A/B/C/D/E/F/R phase labels",
        not missing_labels,
    )

    print("[S] closeout doc contains latest base HEAD")
    check("S. closeout doc contains latest base HEAD", EXPECTED_BASE_HEAD in doc_text)

    print("[T] closeout doc contains required safety sentences")
    missing_sentences = [s for s in REQUIRED_DOC_SAFETY_SENTENCES if s not in doc_text]
    check(
        f"T. closeout doc contains required safety sentences（missing {missing_sentences}）"
        if missing_sentences
        else "T. closeout doc contains required safety sentences",
        not missing_sentences,
    )

    print("[U] closeout doc contains v0.9 post-completion state sentences")
    missing_post_state = [s for s in REQUIRED_DOC_POST_STATE_SENTENCES if s not in doc_text]
    check(
        f"U. closeout doc contains v0.9 post-completion state sentences（missing {missing_post_state}）"
        if missing_post_state
        else "U. closeout doc contains v0.9 post-completion state sentences",
        not missing_post_state,
    )

    print("[V] closeout doc states v0.9-R does not start v0.9.5 / Limited Connector Trial / Callback Contract")
    missing_not_started = [s for s in REQUIRED_DOC_NOT_STARTED_SENTENCES if s not in doc_text]
    check(
        f"V. closeout doc states v0.9-R does not start v0.9.5 / Limited Connector Trial / Callback Contract（missing {missing_not_started}）"
        if missing_not_started
        else "V. closeout doc states v0.9-R does not start v0.9.5 / Limited Connector Trial / Callback Contract",
        not missing_not_started,
    )

    print("[W] forbidden runtime files absent from working diff and staged diff")
    working_diff_files = set(git_lines(["diff", "--name-only"]))
    staged_diff_files = set(git_lines(["diff", "--cached", "--name-only"]))
    touched_forbidden = sorted(
        (working_diff_files | staged_diff_files) & set(FORBIDDEN_RUNTIME_FILES)
    )
    check(
        f"W. forbidden runtime files absent from working diff and staged diff（found {touched_forbidden}）"
        if touched_forbidden
        else "W. forbidden runtime files absent from working diff and staged diff",
        not touched_forbidden,
    )

    print("[X] readiness script only invokes read-only git plumbing as subprocess")
    self_text = read_text(SELF_SCRIPT_PATH)
    self_subprocess_targets = re.findall(r'subprocess\.run\(\s*\[\s*"([^"]+)"', self_text)
    check(
        f"X. readiness script only invokes read-only git plumbing as subprocess（found {self_subprocess_targets}）"
        if any(t != "git" for t in self_subprocess_targets)
        else "X. readiness script only invokes read-only git plumbing as subprocess",
        all(t == "git" for t in self_subprocess_targets),
    )

    print("[Y] readiness script imports no os/network/db module")
    forbidden_self_imports = ("os", "socket", "requests", "httpx", "urllib", "sqlite3")
    found_forbidden_self_imports = [
        m for m in forbidden_self_imports
        if re.search(r"^\s*import\s+" + re.escape(m) + r"\b", self_text, flags=re.MULTILINE)
        or re.search(r"^\s*from\s+" + re.escape(m) + r"\b", self_text, flags=re.MULTILINE)
    ]
    check(
        f"Y. readiness script imports no os/network/db module（found {found_forbidden_self_imports}）"
        if found_forbidden_self_imports
        else "Y. readiness script imports no os/network/db module",
        not found_forbidden_self_imports,
    )

    print("[Z] patches/ remains untracked")
    patches_tracked = git_lines(["ls-files", "--", "patches/"])
    check(
        f"Z. patches/ remains untracked（found tracked {patches_tracked}）"
        if patches_tracked
        else "Z. patches/ remains untracked",
        not patches_tracked,
    )

    print("[AA] no tag at HEAD")
    tags_at_head = git_lines(["tag", "--points-at", "HEAD"])
    check(
        f"AA. no tag at HEAD（found {tags_at_head}）" if tags_at_head else "AA. no tag at HEAD",
        not tags_at_head,
    )

    total = len(PASS) + len(FAIL)
    print(f"\n合計：{len(PASS)}/{total} 通過")
    if FAIL:
        print(f"\nXX v0.9-R readiness 失敗 {len(FAIL)} 項：")
        for f in FAIL:
            print(f"   - {f}")
        sys.exit(1)
    else:
        print("PASS: v0.9-R Hermes strategy mock closeout")
        sys.exit(0)


if __name__ == "__main__":
    main()
