"""v1.0-RC-E readiness check: Owner Review / Safety Matrix Check.

Local filesystem + git metadata validation, standard library only (plus reading the
fixture JSON and scanning app/main.py, templates/system.html, app/full_loop_preview_adapter.py
as plain text). Does NOT import app.main, Hermes runtime, Worker runtime, OpenClaw
runtime, or any connector runtime module. Does not call network, does not read
secrets, does not read connector data, does not write the queue, audit trail, or
Blackboard, and does not modify any file. Its only subprocess use is read-only git
plumbing (status, diff, ls-files, tag).
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
ADAPTER_REL = "app/full_loop_preview_adapter.py"
FIXTURE_REL = "fixtures/local_mock_data/hermes_full_blackboard_loop_rehearsal_v1_0_rc_d.json"
CLAUDE_MD_REL = "CLAUDE.md"
PATCHES_REL = "patches/"
FIXTURES_DIR_REL = "fixtures/local_mock_data/"

DOC_REL = "docs/HERMES_FULL_LOOP_OWNER_REVIEW_SAFETY_MATRIX_V1_0_RC_E.md"
DOC_PATH = REPO_ROOT / DOC_REL

SELF_SCRIPT_REL = "scripts/check_hermes_full_loop_owner_review_safety_matrix_v1_0_rc_e.py"
SELF_SCRIPT_PATH = REPO_ROOT / SELF_SCRIPT_REL

ALLOWED_STAGED_FILES = {DOC_REL, SELF_SCRIPT_REL}

FORBIDDEN_UNTOUCHED_FILES = (
    MAIN_PY_REL,
    SYSTEM_HTML_REL,
    DASHBOARD_CSS_REL,
    RESULT_FEEDBACK_PREVIEW_REL,
    ADAPTER_REL,
    FIXTURE_REL,
    CLAUDE_MD_REL,
)

REVIEWED_ARTIFACT_PATHS = (
    "docs/HERMES_FULL_LOOP_READ_ONLY_REHEARSAL_IMPLEMENTATION_V1_0_RC_D.md",
    "scripts/check_hermes_full_loop_read_only_rehearsal_implementation_v1_0_rc_d.py",
    FIXTURE_REL,
    ADAPTER_REL,
    SYSTEM_HTML_REL,
    DASHBOARD_CSS_REL,
    MAIN_PY_REL,
)

REQUIRED_PHASE_TITLE = "v1.0-RC-E Owner Review / Safety Matrix Check"

REQUIRED_SEQUENCE_LABELS = ("v1.0-RC-R",)

REQUIRED_SECTION_HEADINGS = (
    "Safety Matrix Columns",
    "Safety Matrix",
    "Required PASS Criteria",
    "Required HOLD Criteria",
    "Owner Decision Boundary",
    "Required Final Safety Conclusion",
)

REQUIRED_DOC_SUBSTRINGS = (
    "v1.0-RC-E is docs / check-only Owner Review and Safety Matrix.",
    "v1.0-RC-E does not modify fixture.",
    "v1.0-RC-E does not modify preview adapter.",
    "v1.0-RC-E does not modify Dashboard display.",
    "v1.0-RC-E does not modify app/main.py.",
    "No Full Blackboard Loop implementation occurs in this phase.",
    "No Dashboard controls are added in this phase.",
    "No Hermes runtime activation occurs in this phase.",
    "No Worker dispatch occurs in this phase.",
    "No OpenClaw call occurs in this phase.",
    "No Blackboard write occurs in this phase.",
    "No queue write occurs in this phase.",
    "No audit trail write occurs in this phase.",
    "No connector call occurs in this phase.",
    "No external side effects occur in this phase.",
)

REQUIRED_TOP_LEVEL_FIXTURE_FIELDS = (
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
    "timeline",
    "safety_flags",
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

REQUIRED_DASHBOARD_LABELS = (
    "FULL BLACKBOARD LOOP REHEARSAL TIMELINE",
    "READ ONLY",
    "SYNTHETIC / MOCK ONLY",
)

FORBIDDEN_CONTROL_TOKENS = (
    "<form",
    "<button",
    "action=",
    "method=\"post\"",
    "method='post'",
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
    adapter_text = read_text(REPO_ROOT / ADAPTER_REL)
    adapter_code_only = strip_docstrings_and_comments(adapter_text)
    html_text = read_text(REPO_ROOT / SYSTEM_HTML_REL)
    main_py_text = read_text(REPO_ROOT / MAIN_PY_REL)

    print("[A] v1.0-RC-E matrix doc exists")
    check("A. v1.0-RC-E matrix doc exists", DOC_PATH.is_file())

    print("[B] v1.0-RC-E readiness script exists")
    check("B. v1.0-RC-E readiness script exists", SELF_SCRIPT_PATH.is_file())

    print("[C] doc contains exact phase title")
    check("C. doc contains exact phase title", REQUIRED_PHASE_TITLE in doc_text)

    print("[D] doc contains all required safety/review substrings")
    missing_substrings = [s for s in REQUIRED_DOC_SUBSTRINGS if s not in doc_text]
    check(
        f"D. doc contains all required safety/review substrings（missing {missing_substrings}）"
        if missing_substrings
        else "D. doc contains all required safety/review substrings",
        not missing_substrings,
    )

    print("[E] doc defines required section headings (matrix/pass/hold/owner-boundary/conclusion)")
    missing_headings = [h for h in REQUIRED_SECTION_HEADINGS if h not in doc_text]
    check(
        f"E. doc defines required section headings（missing {missing_headings}）"
        if missing_headings
        else "E. doc defines required section headings",
        not missing_headings,
    )

    print("[F] doc lists future sequence v1.0-RC-R")
    missing_labels = [label for label in REQUIRED_SEQUENCE_LABELS if label not in doc_text]
    check(
        f"F. doc lists future sequence v1.0-RC-R（missing {missing_labels}）"
        if missing_labels
        else "F. doc lists future sequence v1.0-RC-R",
        not missing_labels,
    )

    print("[G] doc lists all reviewed v1.0-RC-D artifacts")
    missing_artifacts_in_doc = [p for p in REVIEWED_ARTIFACT_PATHS if p not in doc_text]
    check(
        f"G. doc lists all reviewed v1.0-RC-D artifacts（missing {missing_artifacts_in_doc}）"
        if missing_artifacts_in_doc
        else "G. doc lists all reviewed v1.0-RC-D artifacts",
        not missing_artifacts_in_doc,
    )

    print("[H] all reviewed v1.0-RC-D artifacts actually exist on disk")
    missing_artifact_files = [p for p in REVIEWED_ARTIFACT_PATHS if not (REPO_ROOT / p).is_file()]
    check(
        f"H. all reviewed v1.0-RC-D artifacts actually exist on disk（missing {missing_artifact_files}）"
        if missing_artifact_files
        else "H. all reviewed v1.0-RC-D artifacts actually exist on disk",
        not missing_artifact_files,
    )

    try:
        fixture_data = json.loads(read_text(REPO_ROOT / FIXTURE_REL) or "{}")
    except json.JSONDecodeError:
        fixture_data = {}

    print("[I] fixture remains synthetic/local-only (re-verified)")
    missing_top_level = [f for f in REQUIRED_TOP_LEVEL_FIXTURE_FIELDS if f not in fixture_data]
    synthetic_ok = (
        fixture_data.get("synthetic_local_only") is True
        and fixture_data.get("mock_only") is True
        and fixture_data.get("dry_run") is True
        and fixture_data.get("read_only") is True
        and fixture_data.get("external_side_effects_allowed") is False
        and fixture_data.get("external_side_effects_occurred") is False
    )
    check(
        f"I. fixture remains synthetic/local-only (re-verified)（missing {missing_top_level}, synthetic_ok={synthetic_ok}）"
        if (missing_top_level or not synthetic_ok)
        else "I. fixture remains synthetic/local-only (re-verified)",
        not missing_top_level and synthetic_ok,
    )

    print("[J] fixture safety flags remain safe (re-verified)")
    safety_flags = fixture_data.get("safety_flags") if isinstance(fixture_data.get("safety_flags"), dict) else {}
    required_true = ("synthetic_local_only", "mock_only", "dry_run", "read_only", "owner_review_required")
    required_false = (
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
    flag_violations = [f"{f} must be true" for f in required_true if safety_flags.get(f) is not True]
    flag_violations += [f"{f} must be false" for f in required_false if safety_flags.get(f) is not False]
    check(
        f"J. fixture safety flags remain safe (re-verified)（violations {flag_violations}）"
        if flag_violations
        else "J. fixture safety flags remain safe (re-verified)",
        not flag_violations,
    )

    print("[K] fixture timeline has all 13 required steps (re-verified)")
    timeline = fixture_data.get("timeline") if isinstance(fixture_data.get("timeline"), list) else []
    found_step_ids = [s.get("step_id") for s in timeline if isinstance(s, dict)]
    missing_steps = [s for s in REQUIRED_TIMELINE_STEP_IDS if s not in found_step_ids]
    check(
        f"K. fixture timeline has all 13 required steps (re-verified)（missing {missing_steps}）"
        if missing_steps
        else "K. fixture timeline has all 13 required steps (re-verified)",
        not missing_steps,
    )

    print("[L] preview adapter exists")
    check("L. preview adapter exists", (REPO_ROOT / ADAPTER_REL).is_file())

    print("[M] preview adapter does not import app/Hermes/Worker/OpenClaw/connector runtime")
    found_forbidden_imports = [
        m for m in FORBIDDEN_ADAPTER_IMPORTS
        if re.search(r"^\s*import\s+" + re.escape(m) + r"\b", adapter_code_only, flags=re.MULTILINE)
        or re.search(r"^\s*from\s+" + re.escape(m) + r"\b", adapter_code_only, flags=re.MULTILINE)
    ]
    check(
        f"M. preview adapter does not import app/Hermes/Worker/OpenClaw/connector runtime（found {found_forbidden_imports}）"
        if found_forbidden_imports
        else "M. preview adapter does not import app/Hermes/Worker/OpenClaw/connector runtime",
        not found_forbidden_imports,
    )

    print("[N] preview adapter does not call network")
    check(
        "N. preview adapter does not call network",
        "requests" not in adapter_code_only and "httpx" not in adapter_code_only and "socket" not in adapter_code_only,
    )

    print("[O] preview adapter does not read secrets")
    check(
        "O. preview adapter does not read secrets",
        "os.environ" not in adapter_code_only and "getenv" not in adapter_code_only,
    )

    print("[P] preview adapter does not write files")
    check(
        "P. preview adapter does not write files",
        ".write_text(" not in adapter_code_only and ".write_bytes(" not in adapter_code_only,
    )

    print("[Q] preview adapter has fail-closed behavior")
    check(
        "Q. preview adapter has fail-closed behavior",
        "unsafe_rejected" in adapter_text and "fail_closed_reasons" in adapter_text,
    )

    print("[R] templates/system.html exists")
    check("R. templates/system.html exists", (REPO_ROOT / SYSTEM_HTML_REL).is_file())

    section_html = extract_section(html_text, "full-loop-rehearsal-timeline")

    print("[S] templates/system.html contains full-loop timeline section title")
    check(
        "S. templates/system.html contains full-loop timeline section title",
        "FULL BLACKBOARD LOOP REHEARSAL TIMELINE" in section_html,
    )

    print("[T] templates/system.html contains required safety labels")
    missing_dashboard_labels = [label for label in REQUIRED_DASHBOARD_LABELS if label not in section_html]
    check(
        f"T. templates/system.html contains required safety labels（missing {missing_dashboard_labels}）"
        if missing_dashboard_labels
        else "T. templates/system.html contains required safety labels",
        not missing_dashboard_labels,
    )

    print("[U] templates/system.html section contains no form/button/action-url/POST")
    found_control_tokens = [t for t in FORBIDDEN_CONTROL_TOKENS if t.lower() in section_html.lower()]
    check(
        f"U. templates/system.html section contains no form/button/action-url/POST（found {found_control_tokens}）"
        if found_control_tokens
        else "U. templates/system.html section contains no form/button/action-url/POST",
        not found_control_tokens,
    )

    print("[V] templates/system.html section contains no approve/reject/execute/dispatch/send/retry/follow-up controls")
    forbidden_action_words = ("approve", "reject", "execute", "dispatch", "retry", "archive", "delete")
    found_action_words = [
        w for w in forbidden_action_words
        if re.search(r'<(button|input)[^>]*' + w, section_html, flags=re.IGNORECASE)
    ]
    check(
        f"V. templates/system.html section contains no approve/reject/execute/dispatch/send/retry/follow-up controls（found {found_action_words}）"
        if found_action_words
        else "V. templates/system.html section contains no approve/reject/execute/dispatch/send/retry/follow-up controls",
        not found_action_words,
    )

    print("[W] static/dashboard.css exists")
    check("W. static/dashboard.css exists", (REPO_ROOT / DASHBOARD_CSS_REL).is_file())

    print("[X] app/main.py exists")
    check("X. app/main.py exists", (REPO_ROOT / MAIN_PY_REL).is_file())

    print("[Y] /dashboard/system remains GET-only")
    get_count = len(re.findall(r'@app\.get\("/dashboard/system"', main_py_text))
    post_count = len(re.findall(r'@app\.post\("/dashboard/system"', main_py_text))
    check(
        f"Y. /dashboard/system remains GET-only（get_count={get_count}, post_count={post_count}）"
        if (get_count != 1 or post_count != 0)
        else "Y. /dashboard/system remains GET-only",
        get_count == 1 and post_count == 0,
    )

    print("[Z] no new route/endpoint/webhook/callback receiver added (working+staged diff)")
    working_diff_main_py = "\n".join(git_lines(["diff", "--", MAIN_PY_REL]))
    staged_diff_main_py = "\n".join(git_lines(["diff", "--cached", "--", MAIN_PY_REL]))
    combined_main_py_diff = working_diff_main_py + "\n" + staged_diff_main_py
    added_route_decorators = re.findall(
        r'^\+\s*@app\.(get|post|put|delete|patch)\(', combined_main_py_diff, flags=re.MULTILINE
    )
    check(
        f"Z. no new route/endpoint/webhook/callback receiver added (working+staged diff)（found {added_route_decorators}）"
        if added_route_decorators
        else "Z. no new route/endpoint/webhook/callback receiver added (working+staged diff)",
        not added_route_decorators,
    )

    print("[AA] only allowed v1.0-RC-E files are staged")
    staged_files = set(git_lines(["diff", "--cached", "--name-only"]))
    unexpected_staged = sorted(staged_files - ALLOWED_STAGED_FILES)
    check(
        f"AA. only allowed v1.0-RC-E files are staged（unexpected {unexpected_staged}）"
        if unexpected_staged
        else "AA. only allowed v1.0-RC-E files are staged",
        not unexpected_staged,
    )

    print("[AB] patches/ is not staged")
    staged_patches = [f for f in staged_files if f.startswith(PATCHES_REL)]
    check(
        f"AB. patches/ is not staged（found {staged_patches}）" if staged_patches else "AB. patches/ is not staged",
        not staged_patches,
    )

    print("[AC] CLAUDE.md is not staged")
    check("AC. CLAUDE.md is not staged", CLAUDE_MD_REL not in staged_files)

    print("[AD] fixtures/local_mock_data/ is not staged")
    staged_fixtures_dir = [f for f in staged_files if f.startswith(FIXTURES_DIR_REL)]
    check(
        f"AD. fixtures/local_mock_data/ is not staged（found {staged_fixtures_dir}）"
        if staged_fixtures_dir
        else "AD. fixtures/local_mock_data/ is not staged",
        not staged_fixtures_dir,
    )

    print("[AE] app/full_loop_preview_adapter.py is not staged")
    check("AE. app/full_loop_preview_adapter.py is not staged", ADAPTER_REL not in staged_files)

    print("[AF] app/main.py is not staged")
    check("AF. app/main.py is not staged", MAIN_PY_REL not in staged_files)

    print("[AG] templates/system.html is not staged")
    check("AG. templates/system.html is not staged", SYSTEM_HTML_REL not in staged_files)

    print("[AH] static/dashboard.css is not staged")
    check("AH. static/dashboard.css is not staged", DASHBOARD_CSS_REL not in staged_files)

    print("[AI] app/result_feedback_preview.py is not staged")
    check("AI. app/result_feedback_preview.py is not staged", RESULT_FEEDBACK_PREVIEW_REL not in staged_files)

    print("[AJ] no forbidden runtime file is staged (outside allowed set)")
    runtime_path_markers = ("connector", "webhook", "endpoint", "callback_receiver", "worker.py", "openclaw", "hermes_runtime")
    suspicious_staged = sorted(
        f for f in staged_files
        if f not in ALLOWED_STAGED_FILES and any(marker in f.lower() for marker in runtime_path_markers)
    )
    check(
        f"AJ. no forbidden runtime file is staged (outside allowed set)（found {suspicious_staged}）"
        if suspicious_staged
        else "AJ. no forbidden runtime file is staged (outside allowed set)",
        not suspicious_staged,
    )

    print("[AK] no v1.0-RC-D reviewed file appears in working or staged diff (untouched)")
    working_diff_files = set(git_lines(["diff", "--name-only"]))
    touched_reviewed = sorted((working_diff_files | staged_files) & set(FORBIDDEN_UNTOUCHED_FILES))
    check(
        f"AK. no v1.0-RC-D reviewed file appears in working or staged diff (untouched)（found {touched_reviewed}）"
        if touched_reviewed
        else "AK. no v1.0-RC-D reviewed file appears in working or staged diff (untouched)",
        not touched_reviewed,
    )

    print("[AL] readiness script only invokes read-only git plumbing as subprocess")
    self_subprocess_targets = re.findall(r'subprocess\.run\(\s*\[\s*"([^"]+)"', self_text)
    check(
        f"AL. readiness script only invokes read-only git plumbing as subprocess（found {self_subprocess_targets}）"
        if any(t != "git" for t in self_subprocess_targets)
        else "AL. readiness script only invokes read-only git plumbing as subprocess",
        all(t == "git" for t in self_subprocess_targets),
    )

    print("[AM] no tag at HEAD")
    tags_at_head = git_lines(["tag", "--points-at", "HEAD"])
    check(
        f"AM. no tag at HEAD（found {tags_at_head}）" if tags_at_head else "AM. no tag at HEAD",
        not tags_at_head,
    )

    print("[AN] cached diff gate: staged diff is empty or exactly the allowed v1.0-RC-E files")
    cached_diff_ok = (not staged_files) or (staged_files == ALLOWED_STAGED_FILES)
    check(
        f"AN. cached diff gate: staged diff is empty or exactly the allowed v1.0-RC-E files（found {sorted(staged_files)}）"
        if not cached_diff_ok
        else "AN. cached diff gate: staged diff is empty or exactly the allowed v1.0-RC-E files",
        cached_diff_ok,
    )

    total = len(PASS) + len(FAIL)
    print(f"\nv1.0-RC-E Owner Review / Safety Matrix Check readiness")
    print(f"合計：{len(PASS)}/{total} 通過")
    if FAIL:
        print(f"\nXX v1.0-RC-E readiness 失敗 {len(FAIL)} 項：")
        for f in FAIL:
            print(f"   - {f}")
        print("Final result: FAIL")
        sys.exit(1)
    else:
        print("Final result: PASS")
        sys.exit(0)


if __name__ == "__main__":
    main()
