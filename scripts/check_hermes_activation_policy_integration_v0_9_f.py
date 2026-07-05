"""v0.9-F readiness check: Hermes Activation Policy Integration Check.

Pure local filesystem + git metadata validation, standard library only, plus direct
file-path imports of the local v0.9-B model, v0.9-C generator, and v0.9-E readback mock
(all already committed in prior rounds — this round adds no new app/ module) so their
accumulated safety guarantees can be exercised end-to-end with synthetic input. It does
NOT import any other application module, does not import QueueStore/Worker/OpenClaw
SDK/Hermes/Google/network clients, does not read secrets or `.env`, does not touch the
real queue DB, does not write the audit trail, and does not perform a network call. Its
only subprocess use is read-only git plumbing (status, diff, ls-files, tag).
"""
from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

MAIN_PY_REL = "app/main.py"
SYSTEM_HTML_REL = "templates/system.html"
DASHBOARD_CSS_REL = "static/dashboard.css"
CLAUDE_MD_REL = "CLAUDE.md"

DOC_REL = "docs/HERMES_ACTIVATION_POLICY_INTEGRATION_CHECK_V0_9_F.md"
DOC_PATH = REPO_ROOT / DOC_REL

SELF_SCRIPT_REL = "scripts/check_hermes_activation_policy_integration_v0_9_f.py"
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

FORBIDDEN_RUNTIME_FILES = (
    MAIN_PY_REL,
    SYSTEM_HTML_REL,
    DASHBOARD_CSS_REL,
    CLAUDE_MD_REL,
)

REQUIRED_DOC_SAFETY_SENTENCES = (
    "Hermes activation policy integration check is not Hermes activation.",
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


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALID_SOURCE_CONTEXT = {
    "task_id": "task-synthetic-0001",
    "source_message_ids": ["msg-synthetic-0001"],
    "source_result_ids": ["result-synthetic-0001"],
    "source_decision_ids": ["decision-synthetic-0001"],
    "strategy_summary": "synthetic strategy summary, advisory only",
    "recommended_action": "describe a hypothetical next step, never executed",
    "risk_assessment": "low",
    "missing_information": "none",
    "owner_question": "does the Owner want to proceed with this synthetic plan?",
    "suggested_next_step": "await Owner confirmation before any further action",
    "confidence": "medium",
}

VALID_RESULT_MESSAGE = {
    "result_id": "result-synthetic-0001",
    "task_id": "task-synthetic-0001",
    "status": "completed",
    "source": "synthetic_local_only",
    "mock_gateway": True,
    "worker_dry_run": True,
    "real_openclaw_called": False,
    "worker_dispatched": False,
    "external_side_effects_performed": False,
    "queue_written": False,
    "audit_trail_written": False,
}

B_REQUIRED_SAFE_FIELDS = {
    "must_not_execute": True,
    "requires_owner_confirmation": True,
    "blackboard_write_allowed": False,
    "worker_dispatch_allowed": False,
    "openclaw_call_allowed": False,
    "external_side_effects_allowed": False,
}

C_REQUIRED_SAFE_FIELDS = {
    "mock_hermes": True,
    "real_hermes_called": False,
    "hermes_runtime_activated": False,
    "hermes_memory_read": False,
    "hermes_tool_called": False,
    "must_not_execute": True,
    "requires_owner_confirmation": True,
    "blackboard_write_allowed": False,
    "queue_write_allowed": False,
    "audit_trail_write_allowed": False,
    "worker_dispatch_allowed": False,
    "openclaw_call_allowed": False,
    "external_side_effects_allowed": False,
}

E_REQUIRED_SAFE_FIELDS = dict(C_REQUIRED_SAFE_FIELDS)
E_REQUIRED_SAFE_FIELDS.update(
    {
        "result_readback_only": True,
        "follow_up_task_auto_create_allowed": False,
    }
)


def _has_safe_fields(obj: dict, required: dict) -> bool:
    return all(obj.get(key) is value for key, value in required.items())


def main() -> None:
    doc_text = read_text(DOC_PATH)

    print("[A] v0.9-F doc exists")
    check("A. v0.9-F doc exists", DOC_PATH.is_file())

    print("[B] v0.9-F readiness script exists")
    check("B. v0.9-F readiness script exists", SELF_SCRIPT_PATH.is_file())

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

    print("[P] doc contains required safety sentences")
    missing_sentences = [s for s in REQUIRED_DOC_SAFETY_SENTENCES if s not in doc_text]
    check(
        f"P. doc contains required safety sentences（missing {missing_sentences}）"
        if missing_sentences
        else "P. doc contains required safety sentences",
        not missing_sentences,
    )

    print("[Q] doc contains v0.9-A/B/C/D/E/F phase labels")
    missing_labels = [label for label in REQUIRED_DOC_PHASE_LABELS if label not in doc_text]
    check(
        f"Q. doc contains v0.9-A/B/C/D/E/F phase labels（missing {missing_labels}）"
        if missing_labels
        else "Q. doc contains v0.9-A/B/C/D/E/F phase labels",
        not missing_labels,
    )

    print("[R] v0.9-B model produces safe strategy suggestion from synthetic context")
    try:
        b_module = load_module("hermes_strategy_suggestion_model_v0_9_f", REPO_ROOT / B_MODEL_REL)
        b_suggestion = b_module.build_hermes_strategy_suggestion(VALID_SOURCE_CONTEXT)
        b_ok = (
            isinstance(b_suggestion, dict)
            and b_suggestion.get("accepted") is True
            and _has_safe_fields(b_suggestion, B_REQUIRED_SAFE_FIELDS)
        )
    except Exception as exc:  # pragma: no cover - surfaced as a check failure
        b_suggestion = {}
        b_ok = False
        print(f"  !! exception while exercising v0.9-B model: {exc!r}")
    check(
        "R. v0.9-B model produces safe strategy suggestion from synthetic context"
        if b_ok
        else f"R. v0.9-B model produces safe strategy suggestion from synthetic context（got {b_suggestion!r}）",
        b_ok,
    )

    print("[S] v0.9-C generator produces safe mock Hermes advice from synthetic context")
    try:
        c_module = load_module("mock_hermes_generator_v0_9_f", REPO_ROOT / C_GENERATOR_REL)
        c_advice = c_module.build_mock_hermes_advice(VALID_SOURCE_CONTEXT)
        c_ok = (
            isinstance(c_advice, dict)
            and c_advice.get("accepted") is True
            and _has_safe_fields(c_advice, C_REQUIRED_SAFE_FIELDS)
        )
    except Exception as exc:  # pragma: no cover - surfaced as a check failure
        c_advice = {}
        c_ok = False
        print(f"  !! exception while exercising v0.9-C generator: {exc!r}")
    check(
        "S. v0.9-C generator produces safe mock Hermes advice from synthetic context"
        if c_ok
        else f"S. v0.9-C generator produces safe mock Hermes advice from synthetic context（got {c_advice!r}）",
        c_ok,
    )

    print("[T] v0.9-E readback mock produces safe readback advice from synthetic result message")
    try:
        e_module = load_module("hermes_result_readback_mock_v0_9_f", REPO_ROOT / E_MOCK_REL)
        e_readback = e_module.build_hermes_result_readback_advice(VALID_RESULT_MESSAGE)
        e_ok = (
            isinstance(e_readback, dict)
            and e_readback.get("accepted") is True
            and _has_safe_fields(e_readback, E_REQUIRED_SAFE_FIELDS)
        )
    except Exception as exc:  # pragma: no cover - surfaced as a check failure
        e_readback = {}
        e_ok = False
        print(f"  !! exception while exercising v0.9-E readback mock: {exc!r}")
    check(
        "T. v0.9-E readback mock produces safe readback advice from synthetic result message"
        if e_ok
        else f"T. v0.9-E readback mock produces safe readback advice from synthetic result message（got {e_readback!r}）",
        e_ok,
    )

    print("[U] forbidden runtime files absent from working diff and staged diff")
    working_diff_files = set(git_lines(["diff", "--name-only"]))
    staged_diff_files = set(git_lines(["diff", "--cached", "--name-only"]))
    touched_forbidden = sorted(
        (working_diff_files | staged_diff_files) & set(FORBIDDEN_RUNTIME_FILES)
    )
    check(
        f"U. forbidden runtime files absent from working diff and staged diff（found {touched_forbidden}）"
        if touched_forbidden
        else "U. forbidden runtime files absent from working diff and staged diff",
        not touched_forbidden,
    )

    print("[V] readiness script only invokes read-only git plumbing as subprocess")
    self_text = read_text(SELF_SCRIPT_PATH)
    self_subprocess_targets = re.findall(r'subprocess\.run\(\s*\[\s*"([^"]+)"', self_text)
    check(
        f"V. readiness script only invokes read-only git plumbing as subprocess（found {self_subprocess_targets}）"
        if any(t != "git" for t in self_subprocess_targets)
        else "V. readiness script only invokes read-only git plumbing as subprocess",
        all(t == "git" for t in self_subprocess_targets),
    )

    print("[W] readiness script imports no os/network/db module")
    forbidden_self_imports = ("os", "socket", "requests", "httpx", "urllib", "sqlite3")
    found_forbidden_self_imports = [
        m for m in forbidden_self_imports
        if re.search(r"^\s*import\s+" + re.escape(m) + r"\b", self_text, flags=re.MULTILINE)
        or re.search(r"^\s*from\s+" + re.escape(m) + r"\b", self_text, flags=re.MULTILINE)
    ]
    check(
        f"W. readiness script imports no os/network/db module（found {found_forbidden_self_imports}）"
        if found_forbidden_self_imports
        else "W. readiness script imports no os/network/db module",
        not found_forbidden_self_imports,
    )

    print("[X] patches/ remains untracked")
    patches_tracked = git_lines(["ls-files", "--", "patches/"])
    check(
        f"X. patches/ remains untracked（found tracked {patches_tracked}）"
        if patches_tracked
        else "X. patches/ remains untracked",
        not patches_tracked,
    )

    print("[Y] no tag at HEAD")
    tags_at_head = git_lines(["tag", "--points-at", "HEAD"])
    check(
        f"Y. no tag at HEAD（found {tags_at_head}）" if tags_at_head else "Y. no tag at HEAD",
        not tags_at_head,
    )

    total = len(PASS) + len(FAIL)
    print(f"\n合計：{len(PASS)}/{total} 通過")
    if FAIL:
        print(f"\nXX v0.9-F readiness 失敗 {len(FAIL)} 項：")
        for f in FAIL:
            print(f"   - {f}")
        sys.exit(1)
    else:
        print("PASS: v0.9-F Hermes activation policy integration check")
        sys.exit(0)


if __name__ == "__main__":
    main()
