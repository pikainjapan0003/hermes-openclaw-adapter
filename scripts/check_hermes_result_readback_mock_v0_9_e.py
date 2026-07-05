"""v0.9-E readiness check: Hermes Reads Result Message Mock.

Pure local filesystem + git metadata validation, standard library only, plus a direct
file-path import of the local v0.9-E readback mock
(`app/hermes_result_readback_mock.py`) this round adds, so it can be exercised
end-to-end (it in turn dynamically loads the local v0.9-C generator itself, unrelated to
this script). It does NOT import any other application module, does not import
QueueStore/Worker/OpenClaw SDK/Hermes/Google/network clients, does not read secrets or
`.env`, does not touch the real queue DB, does not write the audit trail, and does not
perform a network call. Its only subprocess use is read-only git plumbing (status, diff,
ls-files, tag).
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

DOC_REL = "docs/HERMES_RESULT_READBACK_MOCK_V0_9_E.md"
DOC_PATH = REPO_ROOT / DOC_REL

MOCK_REL = "app/hermes_result_readback_mock.py"
MOCK_PATH = REPO_ROOT / MOCK_REL

SELF_SCRIPT_REL = "scripts/check_hermes_result_readback_mock_v0_9_e.py"
SELF_SCRIPT_PATH = REPO_ROOT / SELF_SCRIPT_REL

B_MODEL_REL = "app/hermes_strategy_suggestion_model.py"
C_GENERATOR_REL = "app/mock_hermes_generator.py"
D_DOC_REL = "docs/HERMES_DASHBOARD_ADVICE_PANEL_V0_9_D.md"
D_SCRIPT_REL = "scripts/check_hermes_dashboard_advice_panel_v0_9_d.py"

FORBIDDEN_RUNTIME_FILES = (
    MAIN_PY_REL,
    SYSTEM_HTML_REL,
    DASHBOARD_CSS_REL,
    CLAUDE_MD_REL,
)

REQUIRED_DOC_SAFETY_SENTENCES = (
    "Hermes result readback mock is not Hermes activation.",
    "Hermes result readback mock is not real Hermes readback.",
    "Hermes result readback mock does not read Hermes memory.",
    "Hermes result readback mock does not call Hermes tools.",
    "Hermes readback is not Blackboard write.",
    "Hermes readback is not Owner approval.",
    "Hermes readback is not automatic follow-up execution.",
    "Hermes readback is not automatic follow-up task creation.",
    "Hermes readback is not Worker dispatch.",
    "Hermes readback is not OpenClaw call.",
    "Hermes cannot bypass Owner Review.",
    "Hermes cannot bypass Blackboard Activation Policy.",
    "External side effects remain forbidden by default.",
)

REQUIRED_MOCK_FIELD_MARKERS = (
    "readback_id",
    "advice_id",
    "suggestion_id",
    "task_id",
    "source_result_id",
    "source_result_status",
    "readback_source",
    "readback_summary",
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
    "result_readback_only",
    "must_not_execute",
    "requires_owner_confirmation",
    "blackboard_write_allowed",
    "queue_write_allowed",
    "audit_trail_write_allowed",
    "follow_up_task_auto_create_allowed",
    "worker_dispatch_allowed",
    "openclaw_call_allowed",
    "external_side_effects_allowed",
)

# Built from (key-with-quotes, ": Value") pairs matching the mock's dict-literal
# formatting exactly, joined at runtime.
REQUIRED_MOCK_FORCED_VALUE_PARTS = (
    ('"mock_hermes"', ": True"),
    ('"real_hermes_called"', ": False"),
    ('"hermes_runtime_activated"', ": False"),
    ('"hermes_memory_read"', ": False"),
    ('"hermes_tool_called"', ": False"),
    ('"result_readback_only"', ": True"),
    ('"must_not_execute"', ": True"),
    ('"requires_owner_confirmation"', ": True"),
    ('"blackboard_write_allowed"', ": False"),
    ('"queue_write_allowed"', ": False"),
    ('"audit_trail_write_allowed"', ": False"),
    ('"follow_up_task_auto_create_allowed"', ": False"),
    ('"worker_dispatch_allowed"', ": False"),
    ('"openclaw_call_allowed"', ": False"),
    ('"external_side_effects_allowed"', ": False"),
)
REQUIRED_MOCK_FORCED_VALUES = tuple(a + b for a, b in REQUIRED_MOCK_FORCED_VALUE_PARTS)

# Dangerous strings forbidden anywhere in the mock's *code* (module docstring excluded
# before scanning). Assembled from parts at runtime so this script's own tuple literal
# never forms the forbidden substring itself.
FORBIDDEN_MOCK_STRING_PARTS = (
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
FORBIDDEN_MOCK_STRINGS = tuple(a + b for a, b in FORBIDDEN_MOCK_STRING_PARTS)

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


def load_mock_module():
    spec = importlib.util.spec_from_file_location("hermes_result_readback_mock_v0_9_e", MOCK_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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

REQUIRED_SAFE_READBACK_FIELDS = {
    "mock_hermes": True,
    "real_hermes_called": False,
    "hermes_runtime_activated": False,
    "hermes_memory_read": False,
    "hermes_tool_called": False,
    "result_readback_only": True,
    "must_not_execute": True,
    "requires_owner_confirmation": True,
    "blackboard_write_allowed": False,
    "queue_write_allowed": False,
    "audit_trail_write_allowed": False,
    "follow_up_task_auto_create_allowed": False,
    "worker_dispatch_allowed": False,
    "openclaw_call_allowed": False,
    "external_side_effects_allowed": False,
}


def _has_safe_fields(readback: dict) -> bool:
    return all(readback.get(key) is value for key, value in REQUIRED_SAFE_READBACK_FIELDS.items())


def main() -> None:
    doc_text = read_text(DOC_PATH)
    mock_text = read_text(MOCK_PATH)
    self_text = read_text(SELF_SCRIPT_PATH)

    print("[doc] v0.9-E doc exists")
    check("v0.9-E doc exists", DOC_PATH.is_file())

    print("[mock] v0.9-E readback mock exists")
    check("v0.9-E readback mock exists", MOCK_PATH.is_file())

    print("[script] v0.9-E readiness script exists")
    check("v0.9-E readiness script exists", SELF_SCRIPT_PATH.is_file())

    print("[b] v0.9-B model exists")
    check("v0.9-B model exists", (REPO_ROOT / B_MODEL_REL).is_file())

    print("[c] v0.9-C mock generator exists")
    check("v0.9-C mock generator exists", (REPO_ROOT / C_GENERATOR_REL).is_file())

    print("[d] v0.9-D doc exists")
    check("v0.9-D doc exists", (REPO_ROOT / D_DOC_REL).is_file())

    print("[d] v0.9-D readiness script exists")
    check("v0.9-D readiness script exists", (REPO_ROOT / D_SCRIPT_REL).is_file())

    for sentence in REQUIRED_DOC_SAFETY_SENTENCES:
        print(f"[content] doc contains: {sentence}")
        check(f"doc contains: {sentence}", sentence in doc_text)

    print("[mock] mock contains required field name markers")
    missing_field_markers = [m for m in REQUIRED_MOCK_FIELD_MARKERS if m not in mock_text]
    check(
        f"mock contains required field name markers（missing {missing_field_markers}）"
        if missing_field_markers
        else "mock contains required field name markers",
        not missing_field_markers,
    )

    print("[mock] mock contains forced mandatory safety values")
    missing_forced_values = [v for v in REQUIRED_MOCK_FORCED_VALUES if v not in mock_text]
    check(
        f"mock contains forced mandatory safety values（missing {missing_forced_values}）"
        if missing_forced_values
        else "mock contains forced mandatory safety values",
        not missing_forced_values,
    )

    print("[mock] mock contains no forbidden dangerous strings")
    try:
        mock_tree = ast.parse(mock_text)
        mock_docstring = ast.get_docstring(mock_tree) or ""
    except SyntaxError:
        mock_docstring = ""
    mock_code_only_text = mock_text.replace(mock_docstring, "") if mock_docstring else mock_text
    found_dangerous = [s for s in FORBIDDEN_MOCK_STRINGS if s in mock_code_only_text]
    check(
        f"mock contains no forbidden dangerous strings（found {found_dangerous}）"
        if found_dangerous
        else "mock contains no forbidden dangerous strings",
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

    print("[mock] mock accepts a valid synthetic result message with safe readback fields")
    try:
        mock_module = load_mock_module()
        accepted_readback = mock_module.build_hermes_result_readback_advice(VALID_RESULT_MESSAGE)
        accepted_ok = (
            isinstance(accepted_readback, dict)
            and accepted_readback.get("accepted") is True
            and _has_safe_fields(accepted_readback)
        )
    except Exception as exc:  # pragma: no cover - surfaced as a check failure
        accepted_readback = {}
        accepted_ok = False
        print(f"  !! exception while exercising mock: {exc!r}")
    check(
        "mock accepts a valid synthetic result message with safe readback fields"
        if accepted_ok
        else f"mock accepts a valid synthetic result message with safe readback fields（got {accepted_readback!r}）",
        accepted_ok,
    )

    print("[mock] mock rejects an unsafe result message without calling the generator")
    try:
        unsafe_result_message = dict(VALID_RESULT_MESSAGE)
        unsafe_result_message["real_openclaw_called"] = True
        unsafe_result_message["worker_dispatched"] = True
        rejected_readback = mock_module.build_hermes_result_readback_advice(unsafe_result_message)
        rejected_ok = (
            isinstance(rejected_readback, dict)
            and rejected_readback.get("accepted") is False
            and _has_safe_fields(rejected_readback)
        )
    except Exception as exc:  # pragma: no cover - surfaced as a check failure
        rejected_readback = {}
        rejected_ok = False
        print(f"  !! exception while exercising mock: {exc!r}")
    check(
        "mock rejects an unsafe result message without calling the generator"
        if rejected_ok
        else f"mock rejects an unsafe result message without calling the generator（got {rejected_readback!r}）",
        rejected_ok,
    )

    print("[mock] mock rejects a result message with wrong source without calling the generator")
    try:
        wrong_source_message = dict(VALID_RESULT_MESSAGE)
        wrong_source_message["source"] = "not_synthetic"
        wrong_source_readback = mock_module.build_hermes_result_readback_advice(wrong_source_message)
        wrong_source_ok = (
            isinstance(wrong_source_readback, dict)
            and wrong_source_readback.get("accepted") is False
            and _has_safe_fields(wrong_source_readback)
        )
    except Exception as exc:  # pragma: no cover - surfaced as a check failure
        wrong_source_readback = {}
        wrong_source_ok = False
        print(f"  !! exception while exercising mock: {exc!r}")
    check(
        "mock rejects a result message with wrong source without calling the generator"
        if wrong_source_ok
        else f"mock rejects a result message with wrong source without calling the generator（got {wrong_source_readback!r}）",
        wrong_source_ok,
    )

    print("[mock] validator accepts the valid readback advice built above")
    try:
        valid_validation = mock_module.validate_hermes_result_readback_advice(accepted_readback)
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
        "validator accepts the valid readback advice built above"
        if valid_validation_ok
        else f"validator accepts the valid readback advice built above（got {valid_validation!r}）",
        valid_validation_ok,
    )

    print("[mock] validator fail-safe rejects an unsafe readback advice without executing anything")
    try:
        unsafe_readback = dict(accepted_readback)
        unsafe_readback["must_not_execute"] = False
        unsafe_readback["requires_owner_confirmation"] = False
        unsafe_readback["blackboard_write_allowed"] = True
        unsafe_readback["queue_write_allowed"] = True
        unsafe_readback["audit_trail_write_allowed"] = True
        unsafe_readback["follow_up_task_auto_create_allowed"] = True
        unsafe_readback["worker_dispatch_allowed"] = True
        unsafe_readback["openclaw_call_allowed"] = True
        unsafe_readback["external_side_effects_allowed"] = True
        unsafe_readback["real_hermes_called"] = True
        unsafe_readback["hermes_runtime_activated"] = True
        unsafe_readback["hermes_memory_read"] = True
        unsafe_readback["hermes_tool_called"] = True
        unsafe_validation = mock_module.validate_hermes_result_readback_advice(unsafe_readback)
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
        "validator fail-safe rejects an unsafe readback advice without executing anything"
        if unsafe_validation_ok
        else f"validator fail-safe rejects an unsafe readback advice without executing anything（got {unsafe_validation!r}）",
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
        print(f"\nXX v0.9-E readiness 失敗 {len(FAIL)} 項：")
        for f in FAIL:
            print(f"   - {f}")
        sys.exit(1)
    else:
        print("PASS: v0.9-E Hermes result readback mock")
        sys.exit(0)


if __name__ == "__main__":
    main()
