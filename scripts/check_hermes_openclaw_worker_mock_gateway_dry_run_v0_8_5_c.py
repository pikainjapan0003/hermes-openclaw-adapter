"""v0.8.5-C readiness check: Worker → Mock Gateway Dry-run.

Pure local filesystem + git metadata validation, standard library only, plus two direct
file-path imports of local helper modules this series adds
(`app/mock_openclaw_gateway.py` from v0.8.5-B, `app/worker_mock_gateway_dry_run.py` from
this round) so the dry-run result can be exercised end-to-end. It does NOT import any
other application module, does not import QueueStore/Worker/OpenClaw SDK/Hermes/Google/
network clients, does not read secrets or `.env`, does not touch the real queue DB, does
not write the audit trail, and does not perform a network call. Its only subprocess use
is read-only git plumbing (rev-parse, status, diff, ls-files, tag, merge-base).
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

DOC_REL = "docs/HERMES_OPENCLAW_WORKER_MOCK_GATEWAY_DRY_RUN_V0_8_5_C.md"
DOC_PATH = REPO_ROOT / DOC_REL

HELPER_REL = "app/worker_mock_gateway_dry_run.py"
HELPER_PATH = REPO_ROOT / HELPER_REL

GATEWAY_HELPER_REL = "app/mock_openclaw_gateway.py"
GATEWAY_HELPER_PATH = REPO_ROOT / GATEWAY_HELPER_REL

SELF_SCRIPT_REL = "scripts/check_hermes_openclaw_worker_mock_gateway_dry_run_v0_8_5_c.py"
SELF_SCRIPT_PATH = REPO_ROOT / SELF_SCRIPT_REL

REQUIRED_DOC_SAFETY_SENTENCES = (
    "Worker to mock gateway dry-run is not Worker execution.",
    "Worker to mock gateway dry-run is not Worker dispatch.",
    "Mock gateway call is not real OpenClaw call.",
    "Mock gateway response is not actual execution result.",
    "Dry-run result is not audit trail persistence.",
    "Command envelope validation is not execution permission.",
    "External side effects remain forbidden by default.",
)

REQUIRED_HELPER_TEXT_MARKERS = (
    "mock_only",
    "dry_run",
    "external_side_effects_allowed",
    "dispatch_allowed",
    "worker_allowed",
    "openclaw_allowed",
    "source",
    "worker_dry_run",
    "worker_loop_started",
    "worker_dispatched",
    "mock_gateway_called",
    "real_openclaw_called",
    "external_side_effects_performed",
    "queue_written",
    "audit_trail_written",
    "dashboard_control_added",
)

# Import-module denylist for the *helper* (checked via AST import-node inspection, not a
# raw substring scan, so a docstring that says "does not import subprocess/socket/..." —
# the established convention elsewhere in app/ — does not trip this check).
FORBIDDEN_HELPER_IMPORT_PREFIXES = (
    "requests",
    "httpx",
    "urllib",
    "subprocess",
    "socket",
    "flask",
    "fastapi",
)

# Call/decorator/constant patterns forbidden anywhere in the helper's *code* (module
# docstring excluded before scanning, since the docstring legitimately names these
# patterns in prose while declaring it does not use them). Assembled from parts at
# runtime so this script's own tuple literal never forms the forbidden substring itself.
FORBIDDEN_HELPER_CALL_PATTERN_PARTS = (
    (".pos", "t("),
    ("@app.rou", "te"),
    ("os.sys", "tem("),
    ("OPENCLAW_API_K", "EY"),
    ("GOOG", "LE"),
    ("SHEE", "TS"),
)
FORBIDDEN_HELPER_CALL_PATTERNS = tuple(a + b for a, b in FORBIDDEN_HELPER_CALL_PATTERN_PARTS)

# Forbidden import-module prefixes for *this readiness script's own* source (not the
# helpers it loads). Checked via AST import-node inspection, not a raw substring scan.
FORBIDDEN_SELF_IMPORT_MODULE_PREFIXES = (
    "worker",
    "openclaw",
    "hermes",
    "google",
    "googleapiclient",
    "requests",
    "httpx",
    "socket",
    "urllib",
    "http",
)

FORBIDDEN_STRING_CONSTANT_PARTS = (
    (".", "env"),
    (".", "env.local"),
    ("secrets", ".json"),
    ("credentials", ".json"),
)
FORBIDDEN_STRING_CONSTANTS = tuple(a + b for a, b in FORBIDDEN_STRING_CONSTANT_PARTS)

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


def working_tree_change_names() -> set[str]:
    return set(git_lines(["diff", "--name-only"]))


def staged_change_names() -> set[str]:
    return set(git_lines(["diff", "--cached", "--name-only"]))


def untracked_names() -> set[str]:
    return set(git_lines(["ls-files", "--others", "--exclude-standard"]))


def is_tracked(rel: str) -> bool:
    return run_git(["ls-files", "--error-unmatch", rel]).returncode == 0


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _helper_dangerous_findings(helper_text: str) -> list[str]:
    try:
        helper_tree = ast.parse(helper_text)
    except SyntaxError:
        return ["helper source does not parse"]

    helper_imported_modules: list[str] = []
    for node in ast.walk(helper_tree):
        if isinstance(node, ast.Import):
            helper_imported_modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            helper_imported_modules.append(node.module)
    helper_docstring = ast.get_docstring(helper_tree) or ""

    forbidden_helper_imports = [
        m for m in helper_imported_modules
        if any(m == p or m.startswith(p + ".") for p in FORBIDDEN_HELPER_IMPORT_PREFIXES)
    ]
    helper_code_only_text = helper_text.replace(helper_docstring, "") if helper_docstring else helper_text
    found_call_patterns = [p for p in FORBIDDEN_HELPER_CALL_PATTERNS if p in helper_code_only_text]
    return forbidden_helper_imports + found_call_patterns


SAFE_RESULT_FIELD_EXPECTATIONS = {
    "source": "synthetic_local_only",
    "worker_dry_run": True,
    "worker_loop_started": False,
    "worker_dispatched": False,
    "mock_gateway_called": True,
    "real_openclaw_called": False,
    "external_side_effects_performed": False,
    "queue_written": False,
    "audit_trail_written": False,
    "dashboard_control_added": False,
}


def _result_has_safe_fields(result: dict) -> bool:
    return all(result.get(key) == value for key, value in SAFE_RESULT_FIELD_EXPECTATIONS.items())


def main() -> None:
    doc_text = read_text(DOC_PATH)
    helper_text = read_text(HELPER_PATH)
    gateway_helper_text = read_text(GATEWAY_HELPER_PATH)
    self_text = read_text(SELF_SCRIPT_PATH)

    tracked_changed = working_tree_change_names()
    staged_changed = staged_change_names()
    untracked = untracked_names()

    doc_tracked = is_tracked(DOC_REL)
    helper_tracked = is_tracked(HELPER_REL)
    self_tracked = is_tracked(SELF_SCRIPT_REL)
    phase = "owner_review" if not (doc_tracked and helper_tracked and self_tracked) else "post_commit_or_later"
    print(f"INFO: detected phase = {phase}")

    print("[A] v0.8.5-C doc exists")
    check("A. v0.8.5-C doc exists", DOC_PATH.is_file())

    print("[B] v0.8.5-C helper exists")
    check("B. v0.8.5-C helper exists", HELPER_PATH.is_file())

    print("[C] v0.8.5-C readiness script exists")
    check("C. v0.8.5-C readiness script exists", SELF_SCRIPT_PATH.is_file())

    print("[D] doc is untracked in Owner Review phase")
    check("D. doc is untracked in Owner Review phase", phase != "owner_review" or not doc_tracked)

    print("[E] helper is untracked in Owner Review phase")
    check("E. helper is untracked in Owner Review phase", phase != "owner_review" or not helper_tracked)

    print("[F] readiness script is untracked in Owner Review phase")
    check("F. readiness script is untracked in Owner Review phase", phase != "owner_review" or not self_tracked)

    def not_modified(*rels: str) -> bool:
        return all(rel not in tracked_changed and rel not in staged_changed for rel in rels)

    print("[G] app/main.py not modified (working or staged diff)")
    check("G. app/main.py not modified (working or staged diff)", not_modified(MAIN_PY_REL))

    print("[H] templates/system.html not modified (working or staged diff)")
    check("H. templates/system.html not modified (working or staged diff)", not_modified(SYSTEM_HTML_REL))

    print("[I] static/dashboard.css not modified (working or staged diff)")
    check("I. static/dashboard.css not modified (working or staged diff)", not_modified(DASHBOARD_CSS_REL))

    print("[J] CLAUDE.md not modified (working or staged diff)")
    check("J. CLAUDE.md not modified (working or staged diff)", not_modified(CLAUDE_MD_REL))

    print("[K] v0.8.5-B gateway helper not modified (working or staged diff)")
    check(
        "K. v0.8.5-B gateway helper not modified (working or staged diff)",
        not_modified(GATEWAY_HELPER_REL),
    )

    print("[L] untracked only v0.8.5-C doc/helper/script, patches/*")
    allowed_untracked = {DOC_REL, HELPER_REL, SELF_SCRIPT_REL} if phase == "owner_review" else set()
    unexpected_untracked = {
        p for p in untracked if p not in allowed_untracked and not p.startswith("patches/")
    }
    check(
        f"L. no unexpected untracked files（found {sorted(unexpected_untracked)}）"
        if unexpected_untracked
        else "L. no unexpected untracked files",
        not unexpected_untracked,
    )

    letters_sentences = ["M", "N", "O", "P", "Q", "R", "S"]
    for letter, sentence in zip(letters_sentences, REQUIRED_DOC_SAFETY_SENTENCES):
        print(f"[{letter}] doc contains: {sentence}")
        check(f"{letter}. doc contains: {sentence}", sentence in doc_text)

    print("[T] helper contains required safety flag / response field markers")
    missing_markers = [m for m in REQUIRED_HELPER_TEXT_MARKERS if m not in helper_text]
    check(
        f"T. helper contains required safety flag / response field markers（missing {missing_markers}）"
        if missing_markers
        else "T. helper contains required safety flag / response field markers",
        not missing_markers,
    )

    print("[U] helper contains no forbidden dangerous strings")
    found_dangerous = _helper_dangerous_findings(helper_text)
    check(
        f"U. helper contains no forbidden dangerous strings（found {found_dangerous}）"
        if found_dangerous
        else "U. helper contains no forbidden dangerous strings",
        not found_dangerous,
    )

    # -----------------------------------------------------------------
    try:
        self_tree = ast.parse(self_text)
    except SyntaxError:
        self_tree = None

    self_imported_modules: list[str] = []
    self_string_constants: list[str] = []
    if self_tree is not None:
        for node in ast.walk(self_tree):
            if isinstance(node, ast.Import):
                self_imported_modules.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                self_imported_modules.append(node.module)
            elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                self_string_constants.append(node.value)

    print("[V] readiness script itself contains no forbidden network/connector imports")
    forbidden_self_imports = [
        m for m in self_imported_modules
        if any(m == p or m.startswith(p + ".") for p in FORBIDDEN_SELF_IMPORT_MODULE_PREFIXES)
    ]
    check(
        f"V. readiness script itself contains no forbidden network/connector imports（found {forbidden_self_imports}）"
        if forbidden_self_imports
        else "V. readiness script itself contains no forbidden network/connector imports",
        not forbidden_self_imports,
    )

    print("[W] readiness script does not reference secrets/.env files")
    forbidden_constants_found = [s for s in self_string_constants if s in FORBIDDEN_STRING_CONSTANTS]
    check(
        f"W. readiness script does not reference secrets/.env files（found {forbidden_constants_found}）"
        if forbidden_constants_found or "os" in self_imported_modules
        else "W. readiness script does not reference secrets/.env files",
        not forbidden_constants_found and "os" not in self_imported_modules,
    )

    print("[X] readiness script only invokes read-only git plumbing as subprocess")
    self_subprocess_targets = re.findall(r'subprocess\.run\(\s*\[\s*"([^"]+)"', self_text)
    check(
        f"X. readiness script only invokes read-only git plumbing as subprocess（found {self_subprocess_targets}）"
        if any(t != "git" for t in self_subprocess_targets)
        else "X. readiness script only invokes read-only git plumbing as subprocess",
        all(t == "git" for t in self_subprocess_targets),
    )

    # -----------------------------------------------------------------
    print("[Y] dry-run helper accepts a valid synthetic command envelope with safe result fields")
    valid_envelope = {
        "command_id": "cmd-synthetic-0001",
        "task_id": "task-synthetic-0001",
        "tool_target": "example.tool",
        "requested_action": "describe a hypothetical action, never executed",
        "risk_level": "low",
        "approval_snapshot": {"owner_review_required": True},
        "execution_mode": "mock_only",
        "dry_run": True,
        "mock_only": True,
        "external_touchpoints": [],
        "rollback_plan": "no rollback needed; nothing is executed",
        "external_side_effects_allowed": False,
    }
    try:
        dry_run_module = load_module("worker_mock_gateway_dry_run_v0_8_5_c", HELPER_PATH)
        accepted_result = dry_run_module.run_worker_to_mock_gateway_dry_run(valid_envelope)
        accepted_ok = (
            isinstance(accepted_result, dict)
            and accepted_result.get("accepted") is True
            and _result_has_safe_fields(accepted_result)
        )
    except Exception as exc:  # pragma: no cover - surfaced as a check failure
        accepted_result = {}
        accepted_ok = False
        print(f"  !! exception while exercising helper: {exc!r}")
    check(
        "Y. dry-run helper accepts a valid synthetic command envelope with safe result fields"
        if accepted_ok
        else f"Y. dry-run helper accepts a valid synthetic command envelope with safe result fields（got {accepted_result!r}）",
        accepted_ok,
    )

    print("[Z] dry-run helper rejects an unsafe command envelope without calling the gateway")
    try:
        unsafe_envelope = dict(valid_envelope)
        unsafe_envelope["external_side_effects_allowed"] = True
        rejected_result = dry_run_module.run_worker_to_mock_gateway_dry_run(unsafe_envelope)
        rejected_ok = (
            isinstance(rejected_result, dict)
            and rejected_result.get("accepted") is False
            and rejected_result.get("mock_gateway_called") is False
            and rejected_result.get("source") == "synthetic_local_only"
            and rejected_result.get("worker_loop_started") is False
            and rejected_result.get("worker_dispatched") is False
            and rejected_result.get("real_openclaw_called") is False
        )
    except Exception as exc:  # pragma: no cover - surfaced as a check failure
        rejected_result = {}
        rejected_ok = False
        print(f"  !! exception while exercising helper: {exc!r}")
    check(
        "Z. dry-run helper rejects an unsafe command envelope without calling the gateway"
        if rejected_ok
        else f"Z. dry-run helper rejects an unsafe command envelope without calling the gateway（got {rejected_result!r}）",
        rejected_ok,
    )

    print("[AA] v0.8.5-B gateway helper itself still importable and safe")
    try:
        gateway_module = load_module("mock_openclaw_gateway_v0_8_5_b", GATEWAY_HELPER_PATH)
        gateway_response = gateway_module.build_mock_openclaw_response(valid_envelope)
        gateway_ok = (
            isinstance(gateway_response, dict)
            and gateway_response.get("accepted") is True
            and gateway_response.get("mock_gateway") is True
            and gateway_response.get("production_gateway") is False
            and gateway_response.get("real_openclaw_called") is False
        )
    except Exception as exc:  # pragma: no cover - surfaced as a check failure
        gateway_response = {}
        gateway_ok = False
        print(f"  !! exception while exercising gateway helper: {exc!r}")
    check(
        "AA. v0.8.5-B gateway helper itself still importable and safe"
        if gateway_ok
        else f"AA. v0.8.5-B gateway helper itself still importable and safe（got {gateway_response!r}）",
        gateway_ok,
    )

    # -----------------------------------------------------------------
    print("[AB] patches/ remains untracked")
    patches_tracked = git_lines(["ls-files", "--", "patches/"])
    check(
        f"AB. patches/ remains untracked（found tracked {patches_tracked}）"
        if patches_tracked
        else "AB. patches/ remains untracked",
        not patches_tracked,
    )

    print("[AC] no tag")
    tags_at_head = git_lines(["tag", "--points-at", "HEAD"])
    check(
        f"AC. no tag（found {tags_at_head}）" if tags_at_head else "AC. no tag",
        not tags_at_head,
    )

    # -----------------------------------------------------------------
    total = len(PASS) + len(FAIL)
    print(f"\n合計：{len(PASS)}/{total} 通過")
    if FAIL:
        print(f"\nXX v0.8.5-C readiness 失敗 {len(FAIL)} 項：")
        for f in FAIL:
            print(f"   - {f}")
        sys.exit(1)
    else:
        print("PASS: v0.8.5-C worker mock gateway dry-run")
        sys.exit(0)


if __name__ == "__main__":
    main()
