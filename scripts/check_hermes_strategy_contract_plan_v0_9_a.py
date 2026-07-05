"""v0.9-A readiness check: Hermes Strategy Contract Plan.

Pure local filesystem + git metadata validation, standard library only. This script does
NOT modify any file, does NOT start a server, sends no POST, makes no network call, reads
no secrets, reads no real queue DB, writes no queue, writes no audit trail, and does not
call Worker/OpenClaw/Hermes/Google Sheets. Its only subprocess use is read-only git
plumbing (status, diff, ls-files, tag).
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

DOC_REL = "docs/HERMES_STRATEGY_CONTRACT_PLAN_V0_9_A.md"
DOC_PATH = REPO_ROOT / DOC_REL

SELF_SCRIPT_REL = "scripts/check_hermes_strategy_contract_plan_v0_9_a.py"
SELF_SCRIPT_PATH = REPO_ROOT / SELF_SCRIPT_REL

FORBIDDEN_RUNTIME_FILES = (
    MAIN_PY_REL,
    SYSTEM_HTML_REL,
    DASHBOARD_CSS_REL,
    CLAUDE_MD_REL,
)

REQUIRED_DOC_STRINGS = (
    "v0.9-A",
    "Hermes Strategy Contract Plan",
    "suggestion_id",
    "task_id",
    "strategy_summary",
    "recommended_action",
    "risk_assessment",
    "owner_question",
    "suggested_next_step",
    "must_not_execute",
    "requires_owner_confirmation",
    "blackboard_write_allowed",
    "worker_dispatch_allowed",
    "openclaw_call_allowed",
    "external_side_effects_allowed",
    "must_not_execute = true",
    "requires_owner_confirmation = true",
    "blackboard_write_allowed = false",
    "worker_dispatch_allowed = false",
    "openclaw_call_allowed = false",
    "external_side_effects_allowed = false",
    "Hermes strategy contract is not Hermes activation.",
    "Hermes suggestion is not Blackboard write.",
    "Hermes advice is not Owner approval.",
    "Hermes readback is not automatic follow-up execution.",
    "Hermes strategy suggestion is not Worker dispatch.",
    "Hermes strategy suggestion is not OpenClaw call.",
    "Hermes cannot bypass Owner Review.",
    "Hermes cannot bypass Blackboard Activation Policy.",
    "External side effects remain forbidden by default.",
)

PASS: list[str] = []
FAIL: list[str] = []
_counter = 0


def _next_id() -> int:
    global _counter
    _counter += 1
    return _counter


def ok(label: str) -> None:
    PASS.append(label)
    print(f"  ok : {label}")


def xx(label: str) -> None:
    FAIL.append(label)
    print(f"  XX : {label}")


def check(label: str, condition: bool) -> None:
    numbered = f"{_next_id():02d}. {label}"
    ok(numbered) if condition else xx(numbered)


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

    print("[doc] v0.9-A plan doc exists")
    check("v0.9-A plan doc exists", DOC_PATH.is_file())

    print("[script] v0.9-A readiness script exists")
    check("v0.9-A readiness script exists", SELF_SCRIPT_PATH.is_file())

    for required in REQUIRED_DOC_STRINGS:
        print(f"[content] doc contains: {required}")
        check(f"doc contains: {required}", required in doc_text)

    print("[diff] forbidden runtime files absent from working diff and staged diff")
    working_diff_files = set(git_lines(["diff", "--name-only"]))
    staged_diff_files = set(git_lines(["diff", "--cached", "--name-only"]))
    touched_forbidden = sorted(
        (working_diff_files | staged_diff_files) & set(FORBIDDEN_RUNTIME_FILES)
    )
    check(
        f"forbidden runtime files absent from working diff and staged diff（found {touched_forbidden}）"
        if touched_forbidden
        else "forbidden runtime files absent from working diff and staged diff",
        not touched_forbidden,
    )

    print("[self] readiness script only invokes read-only git plumbing as subprocess")
    self_subprocess_targets = re.findall(r'subprocess\.run\(\s*\[\s*"([^"]+)"', self_text)
    check(
        f"readiness script only invokes read-only git plumbing as subprocess（found {self_subprocess_targets}）"
        if any(t != "git" for t in self_subprocess_targets)
        else "readiness script only invokes read-only git plumbing as subprocess",
        all(t == "git" for t in self_subprocess_targets),
    )

    print("[self] readiness script imports no os/network/db module")
    forbidden_imports = ("os", "socket", "requests", "httpx", "urllib", "sqlite3")
    found_forbidden_imports = [
        m for m in forbidden_imports
        if re.search(r"^\s*import\s+" + re.escape(m) + r"\b", self_text, flags=re.MULTILINE)
        or re.search(r"^\s*from\s+" + re.escape(m) + r"\b", self_text, flags=re.MULTILINE)
    ]
    check(
        f"readiness script imports no os/network/db module（found {found_forbidden_imports}）"
        if found_forbidden_imports
        else "readiness script imports no os/network/db module",
        not found_forbidden_imports,
    )

    print("[git] patches/ remains untracked")
    patches_tracked = git_lines(["ls-files", "--", "patches/"])
    check(
        f"patches/ remains untracked（found tracked {patches_tracked}）"
        if patches_tracked
        else "patches/ remains untracked",
        not patches_tracked,
    )

    print("[git] no tag at HEAD")
    tags_at_head = git_lines(["tag", "--points-at", "HEAD"])
    check(
        f"no tag at HEAD（found {tags_at_head}）" if tags_at_head else "no tag at HEAD",
        not tags_at_head,
    )

    total = len(PASS) + len(FAIL)
    print(f"\n合計：{len(PASS)}/{total} 通過")
    if FAIL:
        print(f"\nXX v0.9-A readiness 失敗 {len(FAIL)} 項：")
        for f in FAIL:
            print(f"   - {f}")
        sys.exit(1)
    else:
        print("PASS: v0.9-A Hermes strategy contract plan")
        sys.exit(0)


if __name__ == "__main__":
    main()
