"""v0.9-B readiness check: Hermes Strategy Suggestion Model.

Pure local filesystem + git metadata validation, standard library only, plus one direct
file-path import of the local model module this round adds
(`app/hermes_strategy_suggestion_model.py`) so it can be exercised end-to-end. It does NOT
import any other application module, does not import QueueStore/Worker/OpenClaw
SDK/Hermes/Google/network clients, does not read secrets or `.env`, does not touch the
real queue DB, does not write the audit trail, and does not perform a network call. Its
only subprocess use is read-only git plumbing (status, diff, ls-files, tag).
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

DOC_REL = "docs/HERMES_STRATEGY_SUGGESTION_MODEL_V0_9_B.md"
DOC_PATH = REPO_ROOT / DOC_REL

MODEL_REL = "app/hermes_strategy_suggestion_model.py"
MODEL_PATH = REPO_ROOT / MODEL_REL

SELF_SCRIPT_REL = "scripts/check_hermes_strategy_suggestion_model_v0_9_b.py"
SELF_SCRIPT_PATH = REPO_ROOT / SELF_SCRIPT_REL

A_DOC_REL = "docs/HERMES_STRATEGY_CONTRACT_PLAN_V0_9_A.md"
A_SCRIPT_REL = "scripts/check_hermes_strategy_contract_plan_v0_9_a.py"

FORBIDDEN_RUNTIME_FILES = (
    MAIN_PY_REL,
    SYSTEM_HTML_REL,
    DASHBOARD_CSS_REL,
    CLAUDE_MD_REL,
)

REQUIRED_DOC_SAFETY_SENTENCES = (
    "Strategy suggestion model is not Hermes activation.",
    "Strategy suggestion model is not mock Hermes generator.",
    "Hermes suggestion is not Blackboard write.",
    "Hermes advice is not Owner approval.",
    "Hermes readback is not automatic follow-up execution.",
    "Hermes strategy suggestion is not Worker dispatch.",
    "Hermes strategy suggestion is not OpenClaw call.",
    "Hermes cannot bypass Owner Review.",
    "Hermes cannot bypass Blackboard Activation Policy.",
    "External side effects remain forbidden by default.",
)

REQUIRED_MODEL_FIELD_MARKERS = (
    "suggestion_id",
    "task_id",
    "source_message_ids",
    "source_result_ids",
    "source_decision_ids",
    "strategy_summary",
    "recommended_action",
    "risk_assessment",
    "missing_information",
    "owner_question",
    "suggested_next_step",
    "confidence",
    "must_not_execute",
    "requires_owner_confirmation",
    "blackboard_write_allowed",
    "worker_dispatch_allowed",
    "openclaw_call_allowed",
    "external_side_effects_allowed",
)

# Built from (prefix, suffix) pairs and joined at runtime so the *contiguous* phrase never
# appears literally in this script's own source.
REQUIRED_MODEL_FORCED_VALUE_PARTS = (
    ('"must_not_execute"', ": True"),
    ('"requires_owner_confirmation"', ": True"),
    ('"blackboard_write_allowed"', ": False"),
    ('"worker_dispatch_allowed"', ": False"),
    ('"openclaw_call_allowed"', ": False"),
    ('"external_side_effects_allowed"', ": False"),
)
REQUIRED_MODEL_FORCED_VALUES = tuple(a + b for a, b in REQUIRED_MODEL_FORCED_VALUE_PARTS)

# Dangerous strings forbidden anywhere in the model's *code* (module docstring excluded
# before scanning, since the docstring legitimately names these patterns in prose while
# declaring it does not use them). Assembled from parts at runtime so this script's own
# tuple literal never forms the forbidden substring itself.
FORBIDDEN_MODEL_STRING_PARTS = (
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
FORBIDDEN_MODEL_STRINGS = tuple(a + b for a, b in FORBIDDEN_MODEL_STRING_PARTS)

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


def load_model_module():
    spec = importlib.util.spec_from_file_location("hermes_strategy_suggestion_model_v0_9_b", MODEL_PATH)
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

REQUIRED_SAFE_SUGGESTION_FIELDS = {
    "must_not_execute": True,
    "requires_owner_confirmation": True,
    "blackboard_write_allowed": False,
    "worker_dispatch_allowed": False,
    "openclaw_call_allowed": False,
    "external_side_effects_allowed": False,
}


def _has_safe_fields(suggestion: dict) -> bool:
    return all(suggestion.get(key) is value for key, value in REQUIRED_SAFE_SUGGESTION_FIELDS.items())


def main() -> None:
    doc_text = read_text(DOC_PATH)
    model_text = read_text(MODEL_PATH)
    self_text = read_text(SELF_SCRIPT_PATH)

    print("[doc] v0.9-B doc exists")
    check("v0.9-B doc exists", DOC_PATH.is_file())

    print("[model] v0.9-B model exists")
    check("v0.9-B model exists", MODEL_PATH.is_file())

    print("[script] v0.9-B readiness script exists")
    check("v0.9-B readiness script exists", SELF_SCRIPT_PATH.is_file())

    print("[a] v0.9-A doc exists")
    check("v0.9-A doc exists", (REPO_ROOT / A_DOC_REL).is_file())

    print("[a] v0.9-A readiness script exists")
    check("v0.9-A readiness script exists", (REPO_ROOT / A_SCRIPT_REL).is_file())

    for sentence in REQUIRED_DOC_SAFETY_SENTENCES:
        print(f"[content] doc contains: {sentence}")
        check(f"doc contains: {sentence}", sentence in doc_text)

    print("[model] model contains required field name markers")
    missing_field_markers = [m for m in REQUIRED_MODEL_FIELD_MARKERS if m not in model_text]
    check(
        f"model contains required field name markers（missing {missing_field_markers}）"
        if missing_field_markers
        else "model contains required field name markers",
        not missing_field_markers,
    )

    print("[model] model contains forced mandatory safety values")
    missing_forced_values = [v for v in REQUIRED_MODEL_FORCED_VALUES if v not in model_text]
    check(
        f"model contains forced mandatory safety values（missing {missing_forced_values}）"
        if missing_forced_values
        else "model contains forced mandatory safety values",
        not missing_forced_values,
    )

    print("[model] model contains no forbidden dangerous strings")
    try:
        model_tree = ast.parse(model_text)
        model_docstring = ast.get_docstring(model_tree) or ""
    except SyntaxError:
        model_docstring = ""
    model_code_only_text = model_text.replace(model_docstring, "") if model_docstring else model_text
    found_dangerous = [s for s in FORBIDDEN_MODEL_STRINGS if s in model_code_only_text]
    check(
        f"model contains no forbidden dangerous strings（found {found_dangerous}）"
        if found_dangerous
        else "model contains no forbidden dangerous strings",
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

    print("[model] model accepts a valid synthetic source context with safe suggestion fields")
    try:
        model_module = load_model_module()
        accepted_suggestion = model_module.build_hermes_strategy_suggestion(VALID_SOURCE_CONTEXT)
        accepted_ok = (
            isinstance(accepted_suggestion, dict)
            and accepted_suggestion.get("accepted") is True
            and _has_safe_fields(accepted_suggestion)
        )
    except Exception as exc:  # pragma: no cover - surfaced as a check failure
        accepted_suggestion = {}
        accepted_ok = False
        print(f"  !! exception while exercising model: {exc!r}")
    check(
        "model accepts a valid synthetic source context with safe suggestion fields"
        if accepted_ok
        else f"model accepts a valid synthetic source context with safe suggestion fields（got {accepted_suggestion!r}）",
        accepted_ok,
    )

    print("[model] model rejects an incomplete synthetic source context while keeping safe fields")
    try:
        incomplete_context = dict(VALID_SOURCE_CONTEXT)
        del incomplete_context["strategy_summary"]
        rejected_suggestion = model_module.build_hermes_strategy_suggestion(incomplete_context)
        rejected_ok = (
            isinstance(rejected_suggestion, dict)
            and rejected_suggestion.get("accepted") is False
            and _has_safe_fields(rejected_suggestion)
        )
    except Exception as exc:  # pragma: no cover - surfaced as a check failure
        rejected_suggestion = {}
        rejected_ok = False
        print(f"  !! exception while exercising model: {exc!r}")
    check(
        "model rejects an incomplete synthetic source context while keeping safe fields"
        if rejected_ok
        else f"model rejects an incomplete synthetic source context while keeping safe fields（got {rejected_suggestion!r}）",
        rejected_ok,
    )

    print("[model] validator accepts the valid suggestion built above")
    try:
        valid_validation = model_module.validate_hermes_strategy_suggestion(accepted_suggestion)
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
        "validator accepts the valid suggestion built above"
        if valid_validation_ok
        else f"validator accepts the valid suggestion built above（got {valid_validation!r}）",
        valid_validation_ok,
    )

    print("[model] validator fail-safe rejects an unsafe suggestion without executing anything")
    try:
        unsafe_suggestion = dict(accepted_suggestion)
        unsafe_suggestion["must_not_execute"] = False
        unsafe_suggestion["requires_owner_confirmation"] = False
        unsafe_suggestion["blackboard_write_allowed"] = True
        unsafe_suggestion["worker_dispatch_allowed"] = True
        unsafe_suggestion["openclaw_call_allowed"] = True
        unsafe_suggestion["external_side_effects_allowed"] = True
        unsafe_validation = model_module.validate_hermes_strategy_suggestion(unsafe_suggestion)
        unsafe_validation_ok = (
            isinstance(unsafe_validation, dict)
            and unsafe_validation.get("valid") is False
            and len(unsafe_validation.get("violations", [])) >= 6
        )
    except Exception as exc:  # pragma: no cover - surfaced as a check failure
        unsafe_validation = {}
        unsafe_validation_ok = False
        print(f"  !! exception while exercising validator: {exc!r}")
    check(
        "validator fail-safe rejects an unsafe suggestion without executing anything"
        if unsafe_validation_ok
        else f"validator fail-safe rejects an unsafe suggestion without executing anything（got {unsafe_validation!r}）",
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
        print(f"\nXX v0.9-B readiness 失敗 {len(FAIL)} 項：")
        for f in FAIL:
            print(f"   - {f}")
        sys.exit(1)
    else:
        print("PASS: v0.9-B Hermes strategy suggestion model")
        sys.exit(0)


if __name__ == "__main__":
    main()
