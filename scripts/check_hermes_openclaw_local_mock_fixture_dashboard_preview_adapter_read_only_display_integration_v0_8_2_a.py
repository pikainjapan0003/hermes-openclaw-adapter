"""v0.8.2-A readiness check: Dashboard Preview Adapter Read-only Display Integration.

Pure local filesystem + git metadata validation. This script confirms the tracked state of the
v0.8.1-V/Z artifacts, confirms the tracked-diff scope (`git diff --name-only` / `git status
--porcelain` / `git ls-files --others --exclude-standard`), and inspects ONLY the *added* lines of
`app/main.py` and `templates/system.html` (via `git diff --unified=0`) for the required
build_dashboard_preview_model() wiring and the absence of any forbidden call/route/control pattern.
It never diffs or scans unrelated pre-existing lines in those files, so pre-existing POST routes /
QueueStore usage elsewhere in app/main.py cannot trip this check.

It does NOT import app runtime, Dashboard runtime, QueueStore, Worker/OpenClaw/Hermes/Google Sheets
integration, or the v0.8.1-P loader; it never starts a server; it reads no real queue DB, sends no
POST, makes no network call, reads no secrets, writes no repo file, and modifies no git index.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

SELF_SCRIPT_PATH = REPO_ROOT / "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_read_only_display_integration_v0_8_2_a.py"

V_ADAPTER_PATH = REPO_ROOT / "scripts/local_mock_fixture_dashboard_preview_adapter_v0_8_1.py"
Z_DOC_PATH = REPO_ROOT / "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_DASHBOARD_PREVIEW_ADAPTER_INTEGRATION_IMPLEMENTATION_PLAN_V0_8_1_Z.md"

MAIN_PY_PATH = REPO_ROOT / "app/main.py"
SYSTEM_HTML_PATH = REPO_ROOT / "templates/system.html"

EXPECTED_BASE_HEAD = "9fb42bc1dde7d9a0b6a9ea33842cfa6f3c7a56df"

ALLOWED_MODIFIED_TRACKED = {"app/main.py", "templates/system.html"}
ALLOWED_NEW_UNTRACKED = {
    "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_read_only_display_integration_v0_8_2_a.py"
}

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


def git_tracked(rel: str) -> bool:
    out = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "ls-files", "--", rel],
        capture_output=True,
        text=True,
    )
    return out.returncode == 0 and out.stdout.strip() != ""


def git_added_lines(rel: str) -> str:
    """Return only the '+' added lines (excluding the '+++' file header) for a tracked file's diff."""
    out = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "diff", "--unified=0", "--", rel],
        capture_output=True,
        text=True,
    )
    added = []
    for line in out.stdout.splitlines():
        if line.startswith("+++"):
            continue
        if line.startswith("+"):
            added.append(line[1:])
    return "\n".join(added)


# ---------------------------------------------------------------------------
# [A] current HEAD contains EXPECTED_BASE_HEAD in git history
# ---------------------------------------------------------------------------
print("[A] current HEAD contains EXPECTED_BASE_HEAD in git history")
ancestor_check = subprocess.run(
    ["git", "-C", str(REPO_ROOT), "merge-base", "--is-ancestor", EXPECTED_BASE_HEAD, "HEAD"],
    capture_output=True,
    text=True,
)
check(
    f"A. HEAD contains {EXPECTED_BASE_HEAD} in git history",
    ancestor_check.returncode == 0,
)

# ---------------------------------------------------------------------------
# [B] V adapter file exists and is tracked
# ---------------------------------------------------------------------------
print("[B] V adapter file exists and is tracked")
check("B. V adapter exists", V_ADAPTER_PATH.exists())
check(
    "B. V adapter is tracked",
    git_tracked("scripts/local_mock_fixture_dashboard_preview_adapter_v0_8_1.py"),
)

# ---------------------------------------------------------------------------
# [C] Z implementation plan exists and is tracked
# ---------------------------------------------------------------------------
print("[C] Z implementation plan exists and is tracked")
check("C. Z implementation plan doc exists", Z_DOC_PATH.exists())
check(
    "C. Z implementation plan doc is tracked",
    git_tracked(
        "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_DASHBOARD_PREVIEW_ADAPTER_INTEGRATION_IMPLEMENTATION_PLAN_V0_8_1_Z.md"
    ),
)

# ---------------------------------------------------------------------------
# [D/E/F] app/main.py, templates/system.html, this script exist
# ---------------------------------------------------------------------------
print("[D] app/main.py exists")
check("D. app/main.py exists", MAIN_PY_PATH.exists())

print("[E] templates/system.html exists")
check("E. templates/system.html exists", SYSTEM_HTML_PATH.exists())

print("[F] v0.8.2-A validation script exists")
check("F. v0.8.2-A validation script exists at expected path", SELF_SCRIPT_PATH.exists())

# ---------------------------------------------------------------------------
# [G] git diff only touches allowed files
# ---------------------------------------------------------------------------
print("[G] git diff only touches allowed files")
diff_names_out = subprocess.run(
    ["git", "-C", str(REPO_ROOT), "diff", "--name-only"],
    capture_output=True,
    text=True,
)
modified_tracked = {l for l in diff_names_out.stdout.splitlines() if l.strip()}
unexpected_modified = modified_tracked - ALLOWED_MODIFIED_TRACKED
missing_modified = ALLOWED_MODIFIED_TRACKED - modified_tracked
check(
    f"G. only app/main.py and templates/system.html are modified（unexpected={sorted(unexpected_modified)}, missing={sorted(missing_modified)}）"
    if (unexpected_modified or missing_modified)
    else "G. only app/main.py and templates/system.html are modified",
    not unexpected_modified and not missing_modified,
)

others_out = subprocess.run(
    ["git", "-C", str(REPO_ROOT), "ls-files", "--others", "--exclude-standard"],
    capture_output=True,
    text=True,
)
untracked = {l for l in others_out.stdout.splitlines() if l.strip()}
unexpected_untracked = {
    u for u in untracked if u not in ALLOWED_NEW_UNTRACKED and not u.startswith("patches/")
}
check(
    f"G. no unexpected untracked files（found {sorted(unexpected_untracked)}）"
    if unexpected_untracked
    else "G. no unexpected untracked files",
    not unexpected_untracked,
)

# ---------------------------------------------------------------------------
# app/main.py added-lines-only checks [H-N]
# ---------------------------------------------------------------------------
main_added = git_added_lines("app/main.py")

print("[H] app/main.py imports build_dashboard_preview_model from V adapter module")
check(
    "H. app/main.py imports build_dashboard_preview_model from V adapter module",
    "build_dashboard_preview_model" in main_added
    and "local_mock_fixture_dashboard_preview_adapter_v0_8_1" in main_added,
)

print("[I] app/main.py does not import P loader")
check(
    "I. app/main.py does not import P loader",
    "load_local_mock_fixture_preview" not in main_added,
)

print("[J] app/main.py added lines do not contain fixture JSON path")
check(
    "J. app/main.py added lines do not contain fixture JSON path",
    "hermes_openclaw_local_mock_messages_v0_8_1.json" not in main_added
    and "fixtures/local_mock_data" not in main_added,
)

print("[K] app/main.py added lines do not define POST route")
MAIN_FORBIDDEN_ROUTE_PATTERNS = ["@app.post(", "@app.put(", "@app.delete(", "@app.patch("]
check(
    "K. app/main.py added lines do not define POST route",
    not any(p in main_added for p in MAIN_FORBIDDEN_ROUTE_PATTERNS),
)

print("[L] app/main.py added lines do not call QueueStore / real queue DB")
MAIN_FORBIDDEN_QUEUE_PATTERNS = ["QueueStore(", "QUEUE_DB_PATH", "get_blackboard(", ".execute("]
check(
    "L. app/main.py added lines do not call QueueStore / real queue DB",
    not any(p in main_added for p in MAIN_FORBIDDEN_QUEUE_PATTERNS),
)

print("[M] app/main.py added lines do not call Worker/OpenClaw/Hermes/Google Sheets")
MAIN_FORBIDDEN_INTEGRATION_PATTERNS = [
    "run_openclaw_cli(",
    "subprocess.",
    "GOOGLE_SHEETS_ENABLED",
    "google_sheets",
    "hermes_endpoint",
    "openclaw_endpoint",
]
check(
    "M. app/main.py added lines do not call Worker/OpenClaw/Hermes/Google Sheets",
    not any(p in main_added for p in MAIN_FORBIDDEN_INTEGRATION_PATTERNS),
)

print("[N] app/main.py added lines do not read secrets / .env / webhook / connector")
MAIN_FORBIDDEN_SECRET_PATTERNS = ["os.getenv(", "os.environ", ".env", "webhook", "connector"]
check(
    "N. app/main.py added lines do not read secrets / .env / webhook / connector",
    not any(p in main_added for p in MAIN_FORBIDDEN_SECRET_PATTERNS),
)

# ---------------------------------------------------------------------------
# templates/system.html added-lines-only checks [O-S]
# ---------------------------------------------------------------------------
system_added = git_added_lines("templates/system.html")

print("[O] templates/system.html added lines contain Local Mock Dashboard Preview")
check(
    "O. templates/system.html added lines contain Local Mock Dashboard Preview",
    "Local Mock Dashboard Preview" in system_added,
)

print("[P] templates/system.html added lines contain all disabled badges")
REQUIRED_BADGES = [
    "DISPATCH OFF",
    "WORKER OFF",
    "OPENCLAW NOT CONNECTED",
    "HERMES NOT CONNECTED",
    "GOOGLE SHEETS DISABLED",
]
check(
    "P. templates/system.html added lines contain all disabled badges",
    all(b in system_added for b in REQUIRED_BADGES),
)

print("[Q] templates/system.html added lines contain is_mock/local_only/read_only")
check(
    "Q. templates/system.html added lines contain is_mock/local_only/read_only",
    "is_mock" in system_added and "local_only" in system_added and "read_only" in system_added,
)

print("[R] templates/system.html added lines contain execution_permission/dispatch_permission/external_side_effects_permission")
check(
    "R. templates/system.html added lines contain execution_permission/dispatch_permission/external_side_effects_permission",
    "execution_permission" in system_added
    and "dispatch_permission" in system_added
    and "external_side_effects_permission" in system_added,
)

print("[S] templates/system.html added lines do not contain form/button/action/POST/execute/dispatch/send/webhook/endpoint/*_url controls")
SYSTEM_FORBIDDEN_CONTROL_PATTERNS = [
    "<form",
    "<button",
    'method="post"',
    "method='post'",
    'action="',
    "action='",
    ">run<",
    ">execute<",
    ">dispatch<",
    ">approve and dispatch<",
    ">send<",
    "post_url",
    "webhook_url",
    "endpoint_url",
    "execute_url",
    "dispatch_url",
    "action_url",
    "onclick=",
]
system_added_lower = system_added.lower()
check(
    "S. templates/system.html added lines do not contain form/button/action/POST/execute/dispatch/send/webhook/endpoint/*_url controls",
    not any(p in system_added_lower for p in SYSTEM_FORBIDDEN_CONTROL_PATTERNS),
)

# ---------------------------------------------------------------------------
# [T-X] no other protected artifact changed
# ---------------------------------------------------------------------------
print("[T] no static file changed")
check("T. no static file changed", not any(p.startswith("static/") for p in modified_tracked))

print("[U] no fixture JSON changed")
check(
    "U. no fixture JSON changed",
    "fixtures/local_mock_data/hermes_openclaw_local_mock_messages_v0_8_1.json" not in modified_tracked,
)

print("[V] no P loader changed")
check("V. no P loader changed", "scripts/load_local_mock_fixture_preview_v0_8_1.py" not in modified_tracked)

print("[W] no V adapter changed")
check(
    "W. no V adapter changed",
    "scripts/local_mock_fixture_dashboard_preview_adapter_v0_8_1.py" not in modified_tracked,
)

print("[X] no W/X/Y/Z artifacts changed")
PROTECTED_WXYZ = {
    "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_runtime_check_v0_8_1_w.py",
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_DASHBOARD_PREVIEW_ADAPTER_INTEGRATION_BOUNDARY_PLAN_V0_8_1_X.md",
    "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_integration_boundary_plan_v0_8_1_x.py",
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_DASHBOARD_PREVIEW_ADAPTER_INTEGRATION_AUTHORIZATION_PLAN_V0_8_1_Y.md",
    "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_integration_authorization_plan_v0_8_1_y.py",
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_DASHBOARD_PREVIEW_ADAPTER_INTEGRATION_IMPLEMENTATION_PLAN_V0_8_1_Z.md",
    "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_integration_implementation_plan_v0_8_1_z.py",
}
check(
    "X. no W/X/Y/Z artifacts changed",
    not (modified_tracked & PROTECTED_WXYZ),
)

# ---------------------------------------------------------------------------
# [Y] patches/ remains untracked and untouched
# ---------------------------------------------------------------------------
print("[Y] patches/ remains untracked and untouched")
check(
    "Y. patches/ remains untracked and untouched",
    not any(p.startswith("patches/") for p in modified_tracked),
)

# ---------------------------------------------------------------------------
# 結果
# ---------------------------------------------------------------------------
total = len(PASS) + len(FAIL)
print(f"\n合計：{len(PASS)}/{total} 通過")
if FAIL:
    print(f"\nXX v0.8.2-A readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print("PASS: v0.8.2-A dashboard preview adapter read-only display integration")
    sys.exit(0)
