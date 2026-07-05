"""v0.9-C readiness check: Mock Hermes Generator.

Pure local filesystem + git metadata validation, standard library only, plus direct
file-path imports of the local v0.9-B model (`app/hermes_strategy_suggestion_model.py`)
and the local v0.9-C generator (`app/mock_hermes_generator.py`) this round adds, so the
generator can be exercised end-to-end. It does NOT import any other application module,
does not import QueueStore/Worker/OpenClaw SDK/Hermes/Google/network clients, does not
read secrets or `.env`, does not touch the real queue DB, does not write the audit trail,
and does not perform a network call. Its only subprocess use is read-only git plumbing
(status, diff, ls-files, tag).
"""
from __future__ import annotations

import ast
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

DOC_REL = "docs/HERMES_MOCK_GENERATOR_V0_9_C.md"
DOC_PATH = REPO_ROOT / DOC_REL

GENERATOR_REL = "app/mock_hermes_generator.py"
GENERATOR_PATH = REPO_ROOT / GENERATOR_REL

SELF_SCRIPT_REL = "scripts/check_hermes_mock_generator_v0_9_c.py"
SELF_SCRIPT_PATH = REPO_ROOT / SELF_SCRIPT_REL

A_DOC_REL = "docs/HERMES_STRATEGY_CONTRACT_PLAN_V0_9_A.md"
A_SCRIPT_REL = "scripts/check_hermes_strategy_contract_plan_v0_9_a.py"

B_DOC_REL = "docs/HERMES_STRATEGY_SUGGESTION_MODEL_V0_9_B.md"
B_MODEL_REL = "app/hermes_strategy_suggestion_model.py"
B_SCRIPT_REL = "scripts/check_hermes_strategy_suggestion_model_v0_9_b.py"

FORBIDDEN_RUNTIME_FILES = (
    MAIN_PY_REL,
    SYSTEM_HTML_REL,
    DASHBOARD_CSS_REL,
    CLAUDE_MD_REL,
)

REQUIRED_DOC_SAFETY_SENTENCES = (
    "Mock Hermes generator is not Hermes activation.",
    "Mock Hermes generator is not real Hermes.",
    "Mock Hermes advice is not Blackboard write.",
    "Mock Hermes advice is not Owner approval.",
    "Mock Hermes advice is not automatic follow-up execution.",
    "Mock Hermes advice is not Worker dispatch.",
    "Mock Hermes advice is not OpenClaw call.",
    "Mock Hermes cannot bypass Owner Review.",
    "Mock Hermes cannot bypass Blackboard Activation Policy.",
    "External side effects remain forbidden by default.",
)

REQUIRED_GENERATOR_FIELD_MARKERS = (
    "advice_id",
    "suggestion_id",
    "task_id",
    "source_message_ids",
    "source_result_ids",
    "source_decision_ids",
    "advice_source",
    "strategy_summary",
    "recommended_action",
    "risk_assessment",
    "missing_information",
    "owner_question",
    "suggested_next_step",
    "confidence",
    "mock_hermes",
    "real_hermes_called",
    "hermes_runtime_activated",
    "hermes_memory_read",
    "hermes_tool_called",
    "must_not_execute",
    "requires_owner_confirmation",
    "blackboard_write_allowed",
    "queue_write_allowed",
    "audit_trail_write_allowed",
    "worker_dispatch_allowed",
    "openclaw_call_allowed",
    "external_side_effects_allowed",
)

# Built from (key-with-quotes, ": Value") pairs matching the generator's dict-literal
# formatting exactly, joined at runtime.
REQUIRED_GENERATOR_FORCED_VALUE_PARTS = (
    ('"mock_hermes"', ": True"),
    ('"real_hermes_called"', ": False"),
    ('"hermes_runtime_activated"', ": False"),
    ('"hermes_memory_read"', ": False"),
    ('"hermes_tool_called"', ": False"),
    ('"must_not_execute"', ": True"),
    ('"requires_owner_confirmation"', ": True"),
    ('"blackboard_write_allowed"', ": False"),
    ('"queue_write_allowed"', ": False"),
    ('"audit_trail_write_allowed"', ": False"),
    ('"worker_dispatch_allowed"', ": False"),
    ('"openclaw_call_allowed"', ": False"),
    ('"external_side_effects_allowed"', ": False"),
)
REQUIRED_GENERATOR_FORCED_VALUES = tuple(a + b for a, b in REQUIRED_GENERATOR_FORCED_VALUE_PARTS)

# Dangerous strings forbidden anywhere in the generator's *code* (module docstring
# excluded before scanning). Assembled from parts at runtime so this script's own tuple
# literal never forms the forbidden substring itself.
FORBIDDEN_GENERATOR_STRING_PARTS = (
    ("reques", "ts."),
    ("http", "x."),
    ("urlli", "b."),
    ("subproc", "ess"),
    ("os.sys", "tem"),
    ("sock", "et"),
    ("flas", "k"),
    ("FastAP", "I"),
    ("@app.rou", "te"),
    (".pos", "t("),
    ("OPENCLAW_API_K", "EY"),
    ("GOOG", "LE"),
    ("SHEE", "TS"),
)
FORBIDDEN_GENERATOR_STRINGS = tuple(a + b for a, b in FORBIDDEN_GENERATOR_STRING_PARTS)

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


def load_generator_module():
    spec = importlib.util.spec_from_file_location("mock_hermes_generator_v0_9_c", GENERATOR_PATH)
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

REQUIRED_SAFE_ADVICE_FIELDS = {
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


def _has_safe_fields(advice: dict) -> bool:
    return all(advice.get(key) is value for key, value in REQUIRED_SAFE_ADVICE_FIELDS.items())


def main() -> None:
    doc_text = read_text(DOC_PATH)
    generator_text = read_text(GENERATOR_PATH)
    self_text = read_text(SELF_SCRIPT_PATH)

    print("[doc] v0.9-C doc exists")
    check("v0.9-C doc exists", DOC_PATH.is_file())

    print("[generator] v0.9-C generator exists")
    check("v0.9-C generator exists", GENERATOR_PATH.is_file())

    print("[script] v0.9-C readiness script exists")
    check("v0.9-C readiness script exists", SELF_SCRIPT_PATH.is_file())

    print("[a] v0.9-A doc exists")
    check("v0.9-A doc exists", (REPO_ROOT / A_DOC_REL).is_file())

    print("[a] v0.9-A readiness script exists")
    check("v0.9-A readiness script exists", (REPO_ROOT / A_SCRIPT_REL).is_file())

    print("[b] v0.9-B doc exists")
    check("v0.9-B doc exists", (REPO_ROOT / B_DOC_REL).is_file())

    print("[b] v0.9-B model exists")
    check("v0.9-B model exists", (REPO_ROOT / B_MODEL_REL).is_file())

    print("[b] v0.9-B readiness script exists")
    check("v0.9-B readiness script exists", (REPO_ROOT / B_SCRIPT_REL).is_file())

    for sentence in REQUIRED_DOC_SAFETY_SENTENCES:
        print(f"[content] doc contains: {sentence}")
        check(f"doc contains: {sentence}", sentence in doc_text)

    print("[generator] generator contains required field name markers")
    missing_field_markers = [m for m in REQUIRED_GENERATOR_FIELD_MARKERS if m not in generator_text]
    check(
        f"generator contains required field name markers（missing {missing_field_markers}）"
        if missing_field_markers
        else "generator contains required field name markers",
        not missing_field_markers,
    )

    print("[generator] generator contains forced mandatory safety values")
    missing_forced_values = [v for v in REQUIRED_GENERATOR_FORCED_VALUES if v not in generator_text]
    check(
        f"generator contains forced mandatory safety values（missing {missing_forced_values}）"
        if missing_forced_values
        else "generator contains forced mandatory safety values",
        not missing_forced_values,
    )

    print("[generator] generator contains no forbidden dangerous strings")
    try:
        generator_tree = ast.parse(generator_text)
        generator_docstring = ast.get_docstring(generator_tree) or ""
    except SyntaxError:
        generator_docstring = ""
    generator_code_only_text = (
        generator_text.replace(generator_docstring, "") if generator_docstring else generator_text
    )
    found_dangerous = [s for s in FORBIDDEN_GENERATOR_STRINGS if s in generator_code_only_text]
    check(
        f"generator contains no forbidden dangerous strings（found {found_dangerous}）"
        if found_dangerous
        else "generator contains no forbidden dangerous strings",
        not found_dangerous,
    )

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

    print("[generator] generator accepts a valid synthetic source context with safe advice fields")
    try:
        generator_module = load_generator_module()
        accepted_advice = generator_module.build_mock_hermes_advice(VALID_SOURCE_CONTEXT)
        accepted_ok = (
            isinstance(accepted_advice, dict)
            and accepted_advice.get("accepted") is True
            and _has_safe_fields(accepted_advice)
        )
    except Exception as exc:  # pragma: no cover - surfaced as a check failure
        accepted_advice = {}
        accepted_ok = False
        print(f"  !! exception while exercising generator: {exc!r}")
    check(
        "generator accepts a valid synthetic source context with safe advice fields"
        if accepted_ok
        else f"generator accepts a valid synthetic source context with safe advice fields（got {accepted_advice!r}）",
        accepted_ok,
    )

    print("[generator] generator rejects an incomplete synthetic source context while keeping safe fields")
    try:
        incomplete_context = dict(VALID_SOURCE_CONTEXT)
        del incomplete_context["strategy_summary"]
        rejected_advice = generator_module.build_mock_hermes_advice(incomplete_context)
        rejected_ok = (
            isinstance(rejected_advice, dict)
            and rejected_advice.get("accepted") is False
            and _has_safe_fields(rejected_advice)
        )
    except Exception as exc:  # pragma: no cover - surfaced as a check failure
        rejected_advice = {}
        rejected_ok = False
        print(f"  !! exception while exercising generator: {exc!r}")
    check(
        "generator rejects an incomplete synthetic source context while keeping safe fields"
        if rejected_ok
        else f"generator rejects an incomplete synthetic source context while keeping safe fields（got {rejected_advice!r}）",
        rejected_ok,
    )

    print("[generator] validator accepts the valid advice built above")
    try:
        valid_validation = generator_module.validate_mock_hermes_advice(accepted_advice)
        valid_validation_ok = (
            isinstance(valid_validation, dict)
            and valid_validation.get("valid") is True
            and valid_validation.get("violations") == []
        )
    except Exception as exc:  # pragma: no cover - surfaced as a check failure
        valid_validation = {}
        valid_validation_ok = False
        print(f"  !! exception while exercising validator: {exc!r}")
    check(
        "validator accepts the valid advice built above"
        if valid_validation_ok
        else f"validator accepts the valid advice built above（got {valid_validation!r}）",
        valid_validation_ok,
    )

    print("[generator] validator fail-safe rejects an unsafe advice without executing anything")
    try:
        unsafe_advice = dict(accepted_advice)
        unsafe_advice["must_not_execute"] = False
        unsafe_advice["requires_owner_confirmation"] = False
        unsafe_advice["blackboard_write_allowed"] = True
        unsafe_advice["queue_write_allowed"] = True
        unsafe_advice["audit_trail_write_allowed"] = True
        unsafe_advice["worker_dispatch_allowed"] = True
        unsafe_advice["openclaw_call_allowed"] = True
        unsafe_advice["external_side_effects_allowed"] = True
        unsafe_advice["real_hermes_called"] = True
        unsafe_advice["hermes_runtime_activated"] = True
        unsafe_advice["hermes_memory_read"] = True
        unsafe_advice["hermes_tool_called"] = True
        unsafe_validation = generator_module.validate_mock_hermes_advice(unsafe_advice)
        unsafe_validation_ok = (
            isinstance(unsafe_validation, dict)
            and unsafe_validation.get("valid") is False
            and len(unsafe_validation.get("violations", [])) >= 12
        )
    except Exception as exc:  # pragma: no cover - surfaced as a check failure
        unsafe_validation = {}
        unsafe_validation_ok = False
        print(f"  !! exception while exercising validator: {exc!r}")
    check(
        "validator fail-safe rejects an unsafe advice without executing anything"
        if unsafe_validation_ok
        else f"validator fail-safe rejects an unsafe advice without executing anything（got {unsafe_validation!r}）",
        unsafe_validation_ok,
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
    forbidden_self_imports = ("os", "socket", "requests", "httpx", "urllib", "sqlite3")
    found_forbidden_self_imports = [
        m for m in forbidden_self_imports
        if re.search(r"^\s*import\s+" + re.escape(m) + r"\b", self_text, flags=re.MULTILINE)
        or re.search(r"^\s*from\s+" + re.escape(m) + r"\b", self_text, flags=re.MULTILINE)
    ]
    check(
        f"readiness script imports no os/network/db module（found {found_forbidden_self_imports}）"
        if found_forbidden_self_imports
        else "readiness script imports no os/network/db module",
        not found_forbidden_self_imports,
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
        print(f"\nXX v0.9-C readiness 失敗 {len(FAIL)} 項：")
        for f in FAIL:
            print(f"   - {f}")
        sys.exit(1)
    else:
        print("PASS: v0.9-C mock Hermes generator")
        sys.exit(0)


if __name__ == "__main__":
    main()
