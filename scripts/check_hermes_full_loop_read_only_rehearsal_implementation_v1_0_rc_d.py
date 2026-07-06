"""v1.0-RC-D readiness check: Full Loop Read-only Rehearsal Implementation.

Local filesystem + git metadata validation, standard library only (plus reading the
fixture JSON and scanning app/main.py, templates/system.html, static/dashboard.css,
app/full_loop_preview_adapter.py as plain text). Does NOT import app.main, Hermes
runtime, Worker runtime, OpenClaw runtime, or any connector runtime module. Does not
call network, does not read secrets, does not read connector data, does not write
the queue, audit trail, or Blackboard, and does not modify any file. Its only
subprocess use is read-only git plumbing (status, diff, ls-files, tag).
"""
from __future__ import annotations

import json
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

DOC_REL = "docs/HERMES_FULL_LOOP_READ_ONLY_REHEARSAL_IMPLEMENTATION_V1_0_RC_D.md"
DOC_PATH = REPO_ROOT / DOC_REL

SELF_SCRIPT_REL = "scripts/check_hermes_full_loop_read_only_rehearsal_implementation_v1_0_rc_d.py"
SELF_SCRIPT_PATH = REPO_ROOT / SELF_SCRIPT_REL

FIXTURE_REL = "fixtures/local_mock_data/hermes_full_blackboard_loop_rehearsal_v1_0_rc_d.json"
FIXTURE_PATH = REPO_ROOT / FIXTURE_REL

ADAPTER_REL = "app/full_loop_preview_adapter.py"
ADAPTER_PATH = REPO_ROOT / ADAPTER_REL

MAIN_PY_PATH = REPO_ROOT / MAIN_PY_REL
SYSTEM_HTML_PATH = REPO_ROOT / SYSTEM_HTML_REL
DASHBOARD_CSS_PATH = REPO_ROOT / DASHBOARD_CSS_REL

ALLOWED_STAGED_FILES = {
    DOC_REL,
    SELF_SCRIPT_REL,
    FIXTURE_REL,
    ADAPTER_REL,
    SYSTEM_HTML_REL,
    DASHBOARD_CSS_REL,
    MAIN_PY_REL,
}

FORBIDDEN_ALWAYS_FILES = (CLAUDE_MD_REL, RESULT_FEEDBACK_PREVIEW_REL)

REQUIRED_TOP_LEVEL_FIELDS = (
    "fixture_id",
    "fixture_version",
    "fixture_kind",
    "synthetic_local_only",
    "mock_only",
    "dry_run",
    "read_only",
    "owner_review_required",
    "external_side_effects_allowed",
    "external_side_effects_occurred",
    "created_for_phase",
    "source_baseline",
    "loop_summary",
    "safety_flags",
    "timeline",
    "artifacts",
    "validation_expectations",
    "fail_closed_rules",
    "non_goals",
    "next_owner_review_question",
)

REQUIRED_TRUE_TOP_LEVEL_FLAGS = (
    "synthetic_local_only",
    "mock_only",
    "dry_run",
    "read_only",
    "owner_review_required",
)
REQUIRED_FALSE_TOP_LEVEL_FLAGS = ("external_side_effects_allowed", "external_side_effects_occurred")

REQUIRED_SAFETY_FLAG_KEYS = (
    "synthetic_local_only",
    "mock_only",
    "dry_run",
    "read_only",
    "owner_review_required",
    "external_side_effects_allowed",
    "external_side_effects_occurred",
    "blackboard_write_allowed",
    "queue_write_allowed",
    "audit_trail_write_allowed",
    "worker_dispatch_allowed",
    "openclaw_call_allowed",
    "hermes_runtime_allowed",
    "connector_call_allowed",
    "google_sheets_write_allowed",
    "follow_up_task_creation_allowed",
    "dashboard_controls_allowed",
)
REQUIRED_TRUE_SAFETY_FLAG_KEYS = (
    "synthetic_local_only",
    "mock_only",
    "dry_run",
    "read_only",
    "owner_review_required",
)

REQUIRED_TIMELINE_STEP_IDS = (
    "owner_rehearsal_request",
    "blackboard_task_draft",
    "annotation_preview",
    "approval_readiness_preview",
    "owner_decision_preview",
    "worker_dry_run_preview",
    "openclaw_mock_command_envelope",
    "openclaw_mock_gateway_result",
    "synthetic_result_message",
    "result_feedback_display_preview",
    "hermes_advisory_readback",
    "follow_up_suggestion_guard_output",
    "final_owner_review_summary",
)

REQUIRED_STEP_FIELDS = (
    "step_id",
    "step_order",
    "step_title",
    "source_component",
    "target_component",
    "synthetic_input",
    "synthetic_output",
    "allowed_behavior",
    "forbidden_behavior",
    "safety_flags",
    "validation_status",
    "owner_review_required",
    "next_step_allowed",
    "next_step_requires_owner_confirmation",
    "notes",
)

REQUIRED_DOC_SUBSTRINGS = (
    "v1.0-RC-D Full Loop Read-only Rehearsal Implementation",
    "This phase is synthetic_local_only, mock_only, dry_run_only, read_only.",
    "No real Full Blackboard Loop is implemented in this phase.",
    "No Blackboard write occurs in this phase.",
    "No queue write occurs in this phase.",
    "No audit trail write occurs in this phase.",
    "No Worker dispatch occurs in this phase.",
    "No OpenClaw call occurs in this phase.",
    "No Hermes runtime activation occurs in this phase.",
    "No connector call occurs in this phase.",
    "No external side effects occur in this phase.",
    "Existing /dashboard/system remains GET-only.",
)

REQUIRED_DASHBOARD_LABELS = (
    "FULL BLACKBOARD LOOP REHEARSAL TIMELINE",
    "FULL LOOP REHEARSAL PREVIEW",
    "READ ONLY",
    "SYNTHETIC / MOCK ONLY",
    "DRY RUN ONLY",
    "VALIDATED FIXTURE ONLY",
    "NO BLACKBOARD WRITE",
    "NO QUEUE WRITE",
    "NO AUDIT TRAIL WRITE",
    "NO WORKER DISPATCH",
    "NO OPENCLAW CALL",
    "NO HERMES RUNTIME",
    "NO CONNECTOR CALL",
    "NO EXTERNAL SIDE EFFECTS",
    "OWNER REVIEW REQUIRED",
    "DISPLAY IS NOT EXECUTION PERMISSION",
    "TIMELINE IS NOT DISPATCH PERMISSION",
    "HERMES READBACK IS ADVISORY ONLY",
)

FORBIDDEN_CONTROL_TOKENS = (
    "<form",
    "<button",
    "action=",
    "method=\"post\"",
    "method='post'",
)

FORBIDDEN_ADAPTER_IMPORTS = (
    "app.main",
    "app.worker",
    "app.queue_store",
    "app.blackboard_store",
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


def strip_docstrings_and_comments(source: str) -> str:
    """Remove triple-quoted docstrings and `#` line comments before keyword scans.

    Avoids self/legitimate-prose false positives (the adapter's own docstring
    legitimately says "不讀 secrets" / names "connector_call_allowed").
    """
    without_docstrings = re.sub(r'"""[\s\S]*?"""', "", source)
    without_comments = re.sub(r"#.*", "", without_docstrings)
    return without_comments


def extract_section(html: str, section_id: str) -> str:
    marker = f'<section id="{section_id}"'
    start = html.find(marker)
    if start == -1:
        return ""
    end = html.find("</section>", start)
    if end == -1:
        return html[start:]
    return html[start : end + len("</section>")]


def main() -> None:
    doc_text = read_text(DOC_PATH)
    self_text = read_text(SELF_SCRIPT_PATH)
    adapter_text = read_text(ADAPTER_PATH)
    adapter_code_only = strip_docstrings_and_comments(adapter_text)
    html_text = read_text(SYSTEM_HTML_PATH)
    css_text = read_text(DASHBOARD_CSS_PATH)
    main_py_text = read_text(MAIN_PY_PATH)

    print("[A] v1.0-RC-D doc exists")
    check("A. v1.0-RC-D doc exists", DOC_PATH.is_file())

    print("[B] v1.0-RC-D readiness script exists")
    check("B. v1.0-RC-D readiness script exists", SELF_SCRIPT_PATH.is_file())

    print("[C] fixture exists")
    check("C. fixture exists", FIXTURE_PATH.is_file())

    print("[D] preview adapter exists")
    check("D. preview adapter exists", ADAPTER_PATH.is_file())

    print("[E] templates/system.html exists")
    check("E. templates/system.html exists", SYSTEM_HTML_PATH.is_file())

    print("[F] static/dashboard.css exists")
    check("F. static/dashboard.css exists", DASHBOARD_CSS_PATH.is_file())

    print("[G] app/main.py exists")
    check("G. app/main.py exists", MAIN_PY_PATH.is_file())

    print("[H] doc contains exact phase title and required safety substrings")
    missing_doc_substrings = [s for s in REQUIRED_DOC_SUBSTRINGS if s not in doc_text]
    check(
        f"H. doc contains exact phase title and required safety substrings（missing {missing_doc_substrings}）"
        if missing_doc_substrings
        else "H. doc contains exact phase title and required safety substrings",
        not missing_doc_substrings,
    )

    try:
        fixture_data = json.loads(read_text(FIXTURE_PATH) or "{}")
    except json.JSONDecodeError:
        fixture_data = {}

    print("[I] fixture top-level required fields exist")
    missing_top_level = [f for f in REQUIRED_TOP_LEVEL_FIELDS if f not in fixture_data]
    check(
        f"I. fixture top-level required fields exist（missing {missing_top_level}）"
        if missing_top_level
        else "I. fixture top-level required fields exist",
        not missing_top_level,
    )

    print("[J] fixture top-level safety flags have safe values")
    top_level_violations = [
        f"{f} must be true" for f in REQUIRED_TRUE_TOP_LEVEL_FLAGS if fixture_data.get(f) is not True
    ] + [
        f"{f} must be false" for f in REQUIRED_FALSE_TOP_LEVEL_FLAGS if fixture_data.get(f) is not False
    ]
    check(
        f"J. fixture top-level safety flags have safe values（violations {top_level_violations}）"
        if top_level_violations
        else "J. fixture top-level safety flags have safe values",
        not top_level_violations,
    )

    print("[K] fixture safety_flags object has all required keys with safe values")
    safety_flags = fixture_data.get("safety_flags") if isinstance(fixture_data.get("safety_flags"), dict) else {}
    safety_flag_violations = []
    for key in REQUIRED_SAFETY_FLAG_KEYS:
        expected = key in REQUIRED_TRUE_SAFETY_FLAG_KEYS
        if safety_flags.get(key) is not expected:
            safety_flag_violations.append(f"safety_flags.{key} must be {expected}")
    check(
        f"K. fixture safety_flags object has all required keys with safe values（violations {safety_flag_violations}）"
        if safety_flag_violations
        else "K. fixture safety_flags object has all required keys with safe values",
        not safety_flag_violations,
    )

    timeline = fixture_data.get("timeline") if isinstance(fixture_data.get("timeline"), list) else []

    print("[L] fixture timeline has all 13 required steps")
    found_step_ids = [s.get("step_id") for s in timeline if isinstance(s, dict)]
    missing_steps = [s for s in REQUIRED_TIMELINE_STEP_IDS if s not in found_step_ids]
    check(
        f"L. fixture timeline has all 13 required steps（missing {missing_steps}）"
        if missing_steps
        else "L. fixture timeline has all 13 required steps",
        not missing_steps,
    )

    print("[M] fixture timeline order is deterministic")
    order_ok = found_step_ids == list(REQUIRED_TIMELINE_STEP_IDS)
    check(
        f"M. fixture timeline order is deterministic（found order {found_step_ids}）"
        if not order_ok
        else "M. fixture timeline order is deterministic",
        order_ok,
    )

    print("[N] each timeline step has required fields")
    step_field_violations = []
    for step in timeline:
        if not isinstance(step, dict):
            step_field_violations.append("a timeline entry is not an object")
            continue
        missing = [f for f in REQUIRED_STEP_FIELDS if f not in step]
        if missing:
            step_field_violations.append(f"step {step.get('step_id')} missing {missing}")
    check(
        f"N. each timeline step has required fields（violations {step_field_violations}）"
        if step_field_violations
        else "N. each timeline step has required fields",
        not step_field_violations,
    )

    print("[O] each timeline step has safe flags")
    step_flag_violations = []
    for step in timeline:
        if not isinstance(step, dict):
            continue
        step_flags = step.get("safety_flags")
        if not isinstance(step_flags, dict):
            step_flag_violations.append(f"step {step.get('step_id')} safety_flags not a mapping")
            continue
        for flag, value in step_flags.items():
            if flag.endswith("_allowed") and value is not False:
                step_flag_violations.append(f"step {step.get('step_id')} {flag} must be false")
    check(
        f"O. each timeline step has safe flags（violations {step_flag_violations}）"
        if step_flag_violations
        else "O. each timeline step has safe flags",
        not step_flag_violations,
    )

    print("[P] adapter uses only standard library / no forbidden imports")
    found_forbidden_imports = [
        m for m in FORBIDDEN_ADAPTER_IMPORTS
        if re.search(r"^\s*import\s+" + re.escape(m) + r"\b", adapter_code_only, flags=re.MULTILINE)
        or re.search(r"^\s*from\s+" + re.escape(m) + r"\b", adapter_code_only, flags=re.MULTILINE)
    ]
    check(
        f"P. adapter uses only standard library / no forbidden imports（found {found_forbidden_imports}）"
        if found_forbidden_imports
        else "P. adapter uses only standard library / no forbidden imports",
        not found_forbidden_imports,
    )

    print("[Q] adapter has no secrets read (no os.environ / getenv usage)")
    check(
        "Q. adapter has no secrets read (no os.environ / getenv usage)",
        "os.environ" not in adapter_code_only and "getenv" not in adapter_code_only,
    )

    print("[R] adapter has no file write calls")
    check(
        "R. adapter has no file write calls",
        ".write_text(" not in adapter_code_only and ".write_bytes(" not in adapter_code_only,
    )

    print("[S] adapter has no queue/Blackboard/audit-trail write")
    adapter_no_flag_names = adapter_code_only
    for flag_name in REQUIRED_SAFETY_FLAG_KEYS:
        adapter_no_flag_names = adapter_no_flag_names.replace(flag_name, "")
    check(
        "S. adapter has no queue/Blackboard/audit-trail write",
        "QueueStore" not in adapter_code_only
        and "BlackboardStore" not in adapter_code_only
        and "audit_trail_write(" not in adapter_code_only,
    )

    print("[T] adapter has no Worker dispatch / OpenClaw call / Hermes runtime activation")
    check(
        "T. adapter has no Worker dispatch / OpenClaw call / Hermes runtime activation",
        "dispatch_worker(" not in adapter_code_only
        and "run_openclaw" not in adapter_code_only
        and "hermes_gateway" not in adapter_code_only.lower(),
    )

    print("[U] adapter defines fail-closed HOLD behavior")
    check(
        "U. adapter defines fail-closed HOLD behavior",
        "unsafe_rejected" in adapter_text and "fail_closed_reasons" in adapter_text,
    )

    print("[V] adapter returns display-safe preview object with required output keys")
    required_output_keys = (
        "fixture_id",
        "fixture_version",
        "validation_status",
        "validation_summary",
        "safety_summary",
        "timeline_preview",
        "artifact_preview",
        "owner_review_required",
        "next_owner_review_question",
        "fail_closed_reasons",
        "non_goals",
        "labels",
    )
    missing_output_keys = [k for k in required_output_keys if f'"{k}"' not in adapter_text]
    check(
        f"V. adapter returns display-safe preview object with required output keys（missing {missing_output_keys}）"
        if missing_output_keys
        else "V. adapter returns display-safe preview object with required output keys",
        not missing_output_keys,
    )

    section_html = extract_section(html_text, "full-loop-rehearsal-timeline")

    print("[W] Dashboard template contains required section title")
    check(
        "W. Dashboard template contains required section title",
        "FULL BLACKBOARD LOOP REHEARSAL TIMELINE" in section_html,
    )

    print("[X] Dashboard template contains required labels")
    missing_labels = [label for label in REQUIRED_DASHBOARD_LABELS if label not in section_html]
    check(
        f"X. Dashboard template contains required labels（missing {missing_labels}）"
        if missing_labels
        else "X. Dashboard template contains required labels",
        not missing_labels,
    )

    print("[Y] Dashboard section has no form/button/action-url/POST controls")
    found_control_tokens = [t for t in FORBIDDEN_CONTROL_TOKENS if t.lower() in section_html.lower()]
    check(
        f"Y. Dashboard section has no form/button/action-url/POST controls（found {found_control_tokens}）"
        if found_control_tokens
        else "Y. Dashboard section has no form/button/action-url/POST controls",
        not found_control_tokens,
    )

    print("[Z] Dashboard section has no approve/reject/execute/dispatch/send/retry control elements")
    forbidden_action_words = ("approve", "reject", "execute", "dispatch", "retry", "archive", "delete")
    found_action_words = [
        w for w in forbidden_action_words
        if re.search(r'<(button|input)[^>]*' + w, section_html, flags=re.IGNORECASE)
    ]
    check(
        f"Z. Dashboard section has no approve/reject/execute/dispatch/send/retry control elements（found {found_action_words}）"
        if found_action_words
        else "Z. Dashboard section has no approve/reject/execute/dispatch/send/retry control elements",
        not found_action_words,
    )

    print("[AA] new CSS block for the read-only section adds no clickable/hidden styling")
    css_section_marker = "full-loop-rehearsal-timeline"
    css_block_start = css_text.find("v1.0-RC-D")
    css_block = css_text[css_block_start:] if css_block_start != -1 else ""
    check(
        "AA. new CSS block for the read-only section adds no clickable/hidden styling",
        css_section_marker in css_text
        and "cursor: pointer" not in css_block.lower()
        and "display: none" not in css_block.lower()
        and "display:none" not in css_block.lower(),
    )

    print("[AB] existing /dashboard/system remains GET-only")
    get_count = len(re.findall(r'@app\.get\("/dashboard/system"', main_py_text))
    post_count = len(re.findall(r'@app\.post\("/dashboard/system"', main_py_text))
    check(
        f"AB. existing /dashboard/system remains GET-only（get_count={get_count}, post_count={post_count}）"
        if (get_count != 1 or post_count != 0)
        else "AB. existing /dashboard/system remains GET-only",
        get_count == 1 and post_count == 0,
    )

    print("[AC] no new route/endpoint/webhook/callback receiver added in app/main.py diff")
    working_diff_main_py = "\n".join(git_lines(["diff", "--", MAIN_PY_REL]))
    staged_diff_main_py = "\n".join(git_lines(["diff", "--cached", "--", MAIN_PY_REL]))
    combined_main_py_diff = working_diff_main_py + "\n" + staged_diff_main_py
    added_route_decorators = re.findall(
        r'^\+\s*@app\.(get|post|put|delete|patch)\(', combined_main_py_diff, flags=re.MULTILINE
    )
    check(
        f"AC. no new route/endpoint/webhook/callback receiver added in app/main.py diff（found {added_route_decorators}）"
        if added_route_decorators
        else "AC. no new route/endpoint/webhook/callback receiver added in app/main.py diff",
        not added_route_decorators,
    )

    print("[AD] only allowed v1.0-RC-D files are staged")
    staged_files = set(git_lines(["diff", "--cached", "--name-only"]))
    unexpected_staged = sorted(staged_files - ALLOWED_STAGED_FILES)
    check(
        f"AD. only allowed v1.0-RC-D files are staged（unexpected {unexpected_staged}）"
        if unexpected_staged
        else "AD. only allowed v1.0-RC-D files are staged",
        not unexpected_staged,
    )

    print("[AE] patches/ is not staged")
    staged_patches = [f for f in staged_files if f.startswith(PATCHES_REL)]
    check(
        f"AE. patches/ is not staged（found {staged_patches}）" if staged_patches else "AE. patches/ is not staged",
        not staged_patches,
    )

    print("[AF] CLAUDE.md is not staged")
    check("AF. CLAUDE.md is not staged", CLAUDE_MD_REL not in staged_files)

    print("[AG] app/result_feedback_preview.py is not staged")
    check("AG. app/result_feedback_preview.py is not staged", RESULT_FEEDBACK_PREVIEW_REL not in staged_files)

    print("[AH] no forbidden runtime file is staged (outside allowed set)")
    runtime_path_markers = ("connector", "webhook", "endpoint", "callback_receiver", "worker.py", "openclaw", "hermes_runtime")
    suspicious_staged = sorted(
        f for f in staged_files
        if f not in ALLOWED_STAGED_FILES and any(marker in f.lower() for marker in runtime_path_markers)
    )
    check(
        f"AH. no forbidden runtime file is staged (outside allowed set)（found {suspicious_staged}）"
        if suspicious_staged
        else "AH. no forbidden runtime file is staged (outside allowed set)",
        not suspicious_staged,
    )

    print("[AI] readiness script only invokes read-only git plumbing as subprocess")
    self_subprocess_targets = re.findall(r'subprocess\.run\(\s*\[\s*"([^"]+)"', self_text)
    check(
        f"AI. readiness script only invokes read-only git plumbing as subprocess（found {self_subprocess_targets}）"
        if any(t != "git" for t in self_subprocess_targets)
        else "AI. readiness script only invokes read-only git plumbing as subprocess",
        all(t == "git" for t in self_subprocess_targets),
    )

    print("[AJ] no tag at HEAD")
    tags_at_head = git_lines(["tag", "--points-at", "HEAD"])
    check(
        f"AJ. no tag at HEAD（found {tags_at_head}）" if tags_at_head else "AJ. no tag at HEAD",
        not tags_at_head,
    )

    print("[AK] cached diff gate: staged diff is empty or a subset of the allowed v1.0-RC-D files")
    cached_diff_ok = staged_files.issubset(ALLOWED_STAGED_FILES)
    check(
        f"AK. cached diff gate: staged diff is empty or a subset of the allowed v1.0-RC-D files（found {sorted(staged_files)}）"
        if not cached_diff_ok
        else "AK. cached diff gate: staged diff is empty or a subset of the allowed v1.0-RC-D files",
        cached_diff_ok,
    )

    total = len(PASS) + len(FAIL)
    print(f"\nv1.0-RC-D Full Loop Read-only Rehearsal Implementation readiness")
    print(f"合計：{len(PASS)}/{total} 通過")
    if FAIL:
        print(f"\nXX v1.0-RC-D readiness 失敗 {len(FAIL)} 項：")
        for f in FAIL:
            print(f"   - {f}")
        print("Final result: FAIL")
        sys.exit(1)
    else:
        print("Final result: PASS")
        sys.exit(0)


if __name__ == "__main__":
    main()
