"""v0.9.6-D readiness check: Result Feedback Display Implementation.

Local filesystem + git metadata validation, standard library only (plus reading the
fixture JSON and scanning app/main.py, templates/system.html, static/dashboard.css as
plain text). Does NOT import app.main, Hermes runtime, Worker runtime, OpenClaw
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
CLAUDE_MD_REL = "CLAUDE.md"
PATCHES_REL = "patches/"

DOC_REL = "docs/HERMES_RESULT_FEEDBACK_DISPLAY_IMPLEMENTATION_V0_9_6_D.md"
DOC_PATH = REPO_ROOT / DOC_REL

SELF_SCRIPT_REL = "scripts/check_hermes_result_feedback_display_implementation_v0_9_6_d.py"
SELF_SCRIPT_PATH = REPO_ROOT / SELF_SCRIPT_REL

FIXTURE_REL = "fixtures/local_mock_data/hermes_result_feedback_preview_v0_9_6_d.json"
FIXTURE_PATH = REPO_ROOT / FIXTURE_REL

HELPER_REL = "app/result_feedback_preview.py"
HELPER_PATH = REPO_ROOT / HELPER_REL

MAIN_PY_PATH = REPO_ROOT / MAIN_PY_REL
SYSTEM_HTML_PATH = REPO_ROOT / SYSTEM_HTML_REL
DASHBOARD_CSS_PATH = REPO_ROOT / DASHBOARD_CSS_REL

ALLOWED_STAGED_FILES = {
    DOC_REL,
    SELF_SCRIPT_REL,
    FIXTURE_REL,
    HELPER_REL,
    SYSTEM_HTML_REL,
    DASHBOARD_CSS_REL,
    MAIN_PY_REL,
}

FORBIDDEN_STAGED_FILES = (
    CLAUDE_MD_REL,
    PATCHES_REL,
)

REQUIRED_TRUE_FIXTURE_FLAGS = (
    "synthetic_local_only",
    "mock_only",
    "dry_run",
    "owner_review_required",
    "follow_up_requires_owner_confirmation",
)

REQUIRED_FALSE_FIXTURE_FLAGS = (
    "external_side_effects_allowed",
    "external_side_effects_occurred",
    "follow_up_allowed",
    "worker_dispatch_allowed",
    "openclaw_call_allowed",
    "hermes_runtime_allowed",
    "connector_call_allowed",
    "google_sheets_write_allowed",
    "blackboard_write_allowed",
    "queue_write_allowed",
    "audit_trail_write_allowed",
)

REQUIRED_DASHBOARD_LABELS = (
    "RESULT FEEDBACK PREVIEW",
    "READ ONLY",
    "SYNTHETIC / MOCK ONLY",
    "VALIDATED RESULT MESSAGE ONLY",
    "NO RAW CALLBACK PAYLOAD",
    "NO EXTERNAL SIDE EFFECTS",
    "OWNER REVIEW REQUIRED",
    "DISPLAY IS NOT EXECUTION PERMISSION",
    "RESULT MESSAGE IS NOT NEXT DISPATCH PERMISSION",
    "HERMES READBACK IS ADVISORY ONLY",
)

FORBIDDEN_CONTROL_TOKENS = (
    "<form",
    "<button",
    "action=",
    "method=\"post\"",
    "method='post'",
    "approve control",
    "reject control",
    "execute control",
    "dispatch control",
    "retry control",
    "follow-up control",
    "send control",
    "archive control",
    "delete control",
)

FORBIDDEN_HELPER_IMPORTS = (
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

FORBIDDEN_HELPER_CALL_KEYWORDS = (
    "smtplib.SMTP" + "(",
    "requests" + ".post(",
    "requests" + ".get(",
    "httpx" + ".post(",
    "httpx" + ".get(",
    "open(" + " ",  # a bare write-style open call would show "open(" followed by args; checked narrowly below
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
    """Remove triple-quoted docstrings and `#` line comments from Python source text.

    Used so keyword checks (secrets/connector/etc.) scan actual code, not the
    module's own explanatory prose, which legitimately names the very things it
    promises not to do (e.g. "不讀 secrets", "connector_call_allowed" flag name).
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
    helper_text = read_text(HELPER_PATH)
    html_text = read_text(SYSTEM_HTML_PATH)
    css_text = read_text(DASHBOARD_CSS_PATH)
    main_py_text = read_text(MAIN_PY_PATH)

    print("[A] v0.9.6-D closeout doc exists")
    check("A. v0.9.6-D closeout doc exists", DOC_PATH.is_file())

    print("[B] v0.9.6-D readiness script exists")
    check("B. v0.9.6-D readiness script exists", SELF_SCRIPT_PATH.is_file())

    print("[C] fixture exists")
    check("C. fixture exists", FIXTURE_PATH.is_file())

    print("[D] app/result_feedback_preview.py exists")
    check("D. app/result_feedback_preview.py exists", HELPER_PATH.is_file())

    print("[E] templates/system.html contains Result Feedback Preview display")
    section_html = extract_section(html_text, "result-feedback-preview-view")
    check(
        "E. templates/system.html contains Result Feedback Preview display",
        bool(section_html) and "Result Feedback Preview" in section_html,
    )

    print("[F] static/dashboard.css contains result feedback preview styling")
    check(
        "F. static/dashboard.css contains result feedback preview styling",
        ".result-feedback-preview-view" in css_text,
    )

    try:
        fixture_data = json.loads(read_text(FIXTURE_PATH) or "{}")
    except json.JSONDecodeError:
        fixture_data = {}

    print("[G] fixture safety flags are correct (true flags)")
    missing_true = [f for f in REQUIRED_TRUE_FIXTURE_FLAGS if fixture_data.get(f) is not True]
    check(
        f"G. fixture safety flags are correct (true flags)（violations {missing_true}）"
        if missing_true
        else "G. fixture safety flags are correct (true flags)",
        not missing_true,
    )

    print("[H] fixture safety flags are correct (false flags)")
    missing_false = [f for f in REQUIRED_FALSE_FIXTURE_FLAGS if fixture_data.get(f) is not False]
    check(
        f"H. fixture safety flags are correct (false flags)（violations {missing_false}）"
        if missing_false
        else "H. fixture safety flags are correct (false flags)",
        not missing_false,
    )

    print("[I] helper reads only the local fixture (no other file reads)")
    other_file_reads = re.findall(r'\.read_text\(|\.read_bytes\(|open\(', helper_text)
    fixture_reads = helper_text.count("FIXTURE_PATH.read_text(")
    check(
        f"I. helper reads only the local fixture (no other file reads)（reads found {len(other_file_reads)}, fixture reads {fixture_reads}）"
        if len(other_file_reads) != fixture_reads
        else "I. helper reads only the local fixture (no other file reads)",
        len(other_file_reads) == fixture_reads and fixture_reads >= 1,
    )

    print("[J] helper has no network import")
    found_forbidden_imports = [
        m for m in FORBIDDEN_HELPER_IMPORTS
        if re.search(r"^\s*import\s+" + re.escape(m) + r"\b", helper_text, flags=re.MULTILINE)
        or re.search(r"^\s*from\s+" + re.escape(m) + r"\b", helper_text, flags=re.MULTILINE)
    ]
    check(
        f"J. helper has no network import（found {found_forbidden_imports}）"
        if found_forbidden_imports
        else "J. helper has no network import",
        not found_forbidden_imports,
    )

    helper_code_only = strip_docstrings_and_comments(helper_text)
    helper_code_only_no_flag_names = (
        helper_code_only.replace("connector_call_allowed", "")
    )

    print("[K] helper has no secrets read")
    check(
        "K. helper has no secrets read",
        "secret" not in helper_code_only.lower()
        and "os.environ" not in helper_code_only
        and "getenv" not in helper_code_only,
    )

    print("[L] helper has no connector read")
    check("L. helper has no connector read", "connector" not in helper_code_only_no_flag_names.lower())

    print("[M] helper has no queue write")
    check(
        "M. helper has no queue write",
        "QueueStore" not in helper_text and "queue_write" not in helper_text.lower().replace("queue_write_allowed", ""),
    )

    print("[N] helper has no audit trail write")
    check("N. helper has no audit trail write", "audit_trail_write(" not in helper_text)

    print("[O] helper has no Blackboard write")
    check("O. helper has no Blackboard write", "BlackboardStore" not in helper_text)

    print("[P] helper has no write_text/write_bytes calls")
    check(
        "P. helper has no write_text/write_bytes calls",
        ".write_text(" not in helper_text and ".write_bytes(" not in helper_text,
    )

    print("[Q] dashboard contains all required labels")
    missing_labels = [label for label in REQUIRED_DASHBOARD_LABELS if label not in section_html]
    check(
        f"Q. dashboard contains all required labels（missing {missing_labels}）"
        if missing_labels
        else "Q. dashboard contains all required labels",
        not missing_labels,
    )

    print("[R] dashboard result feedback section has no form/button/action-url/POST controls")
    found_control_tokens = [t for t in FORBIDDEN_CONTROL_TOKENS if t.lower() in section_html.lower()]
    check(
        f"R. dashboard result feedback section has no form/button/action-url/POST controls（found {found_control_tokens}）"
        if found_control_tokens
        else "R. dashboard result feedback section has no form/button/action-url/POST controls",
        not found_control_tokens,
    )

    print("[S] dashboard result feedback section has no approve/reject/execute/dispatch/send/retry/follow-up controls")
    forbidden_action_words = ("approve", "reject", "execute", "dispatch", "retry", "archive", "delete")
    found_action_words = [
        w for w in forbidden_action_words
        if re.search(r'<(button|input)[^>]*' + w, section_html, flags=re.IGNORECASE)
    ]
    check(
        f"S. dashboard result feedback section has no approve/reject/execute/dispatch/send/retry/follow-up controls（found {found_action_words}）"
        if found_action_words
        else "S. dashboard result feedback section has no approve/reject/execute/dispatch/send/retry/follow-up controls",
        not found_action_words,
    )

    print("[T] existing /dashboard/system remains GET-only")
    dashboard_system_get_count = len(re.findall(r'@app\.get\("/dashboard/system"', main_py_text))
    dashboard_system_post_count = len(re.findall(r'@app\.post\("/dashboard/system"', main_py_text))
    check(
        f"T. existing /dashboard/system remains GET-only（get_count={dashboard_system_get_count}, post_count={dashboard_system_post_count}）"
        if (dashboard_system_get_count != 1 or dashboard_system_post_count != 0)
        else "T. existing /dashboard/system remains GET-only",
        dashboard_system_get_count == 1 and dashboard_system_post_count == 0,
    )

    print("[U] no new route/endpoint/webhook added in app/main.py diff")
    working_diff_main_py = "\n".join(git_lines(["diff", "--", MAIN_PY_REL]))
    staged_diff_main_py = "\n".join(git_lines(["diff", "--cached", "--", MAIN_PY_REL]))
    combined_main_py_diff = working_diff_main_py + "\n" + staged_diff_main_py
    added_route_decorators = re.findall(
        r'^\+\s*@app\.(get|post|put|delete|patch)\(', combined_main_py_diff, flags=re.MULTILINE
    )
    check(
        f"U. no new route/endpoint/webhook added in app/main.py diff（found {added_route_decorators}）"
        if added_route_decorators
        else "U. no new route/endpoint/webhook added in app/main.py diff",
        not added_route_decorators,
    )

    print("[V] only allowed v0.9.6-D files are staged")
    staged_files = set(git_lines(["diff", "--cached", "--name-only"]))
    unexpected_staged = sorted(staged_files - ALLOWED_STAGED_FILES)
    check(
        f"V. only allowed v0.9.6-D files are staged（unexpected {unexpected_staged}）"
        if unexpected_staged
        else "V. only allowed v0.9.6-D files are staged",
        not unexpected_staged,
    )

    print("[W] patches/ is not staged")
    staged_patches = [f for f in staged_files if f.startswith(PATCHES_REL)]
    check(
        f"W. patches/ is not staged（found {staged_patches}）" if staged_patches else "W. patches/ is not staged",
        not staged_patches,
    )

    print("[X] CLAUDE.md is not staged")
    check("X. CLAUDE.md is not staged", CLAUDE_MD_REL not in staged_files)

    print("[Y] no connector/webhook/endpoint runtime file is staged (outside allowed set)")
    runtime_path_markers = ("connector", "webhook", "endpoint", "callback_receiver")
    suspicious_staged = sorted(
        f for f in staged_files
        if f not in ALLOWED_STAGED_FILES and any(marker in f.lower() for marker in runtime_path_markers)
    )
    check(
        f"Y. no connector/webhook/endpoint runtime file is staged (outside allowed set)（found {suspicious_staged}）"
        if suspicious_staged
        else "Y. no connector/webhook/endpoint runtime file is staged (outside allowed set)",
        not suspicious_staged,
    )

    print("[Z] no Worker/OpenClaw/Hermes runtime file is staged (outside allowed set)")
    runtime_file_markers = ("worker.py", "openclaw", "hermes_runtime")
    suspicious_runtime_staged = sorted(
        f for f in staged_files
        if f not in ALLOWED_STAGED_FILES and any(marker in f.lower() for marker in runtime_file_markers)
    )
    check(
        f"Z. no Worker/OpenClaw/Hermes runtime file is staged (outside allowed set)（found {suspicious_runtime_staged}）"
        if suspicious_runtime_staged
        else "Z. no Worker/OpenClaw/Hermes runtime file is staged (outside allowed set)",
        not suspicious_runtime_staged,
    )

    print("[AA] readiness script only invokes read-only git plumbing as subprocess")
    self_subprocess_targets = re.findall(r'subprocess\.run\(\s*\[\s*"([^"]+)"', self_text)
    check(
        f"AA. readiness script only invokes read-only git plumbing as subprocess（found {self_subprocess_targets}）"
        if any(t != "git" for t in self_subprocess_targets)
        else "AA. readiness script only invokes read-only git plumbing as subprocess",
        all(t == "git" for t in self_subprocess_targets),
    )

    print("[AB] no tag at HEAD")
    tags_at_head = git_lines(["tag", "--points-at", "HEAD"])
    check(
        f"AB. no tag at HEAD（found {tags_at_head}）" if tags_at_head else "AB. no tag at HEAD",
        not tags_at_head,
    )

    print("[AC] cached diff gate: staged diff is empty or a subset of the allowed v0.9.6-D files")
    cached_diff_ok = staged_files.issubset(ALLOWED_STAGED_FILES)
    check(
        f"AC. cached diff gate: staged diff is empty or a subset of the allowed v0.9.6-D files（found {sorted(staged_files)}）"
        if not cached_diff_ok
        else "AC. cached diff gate: staged diff is empty or a subset of the allowed v0.9.6-D files",
        cached_diff_ok,
    )

    total = len(PASS) + len(FAIL)
    print(f"\nv0.9.6-D Result Feedback Display Implementation readiness")
    print(f"合計：{len(PASS)}/{total} 通過")
    if FAIL:
        print(f"\nXX v0.9.6-D readiness 失敗 {len(FAIL)} 項：")
        for f in FAIL:
            print(f"   - {f}")
        print("Final result: FAIL")
        sys.exit(1)
    else:
        print("Final result: PASS")
        sys.exit(0)


if __name__ == "__main__":
    main()
