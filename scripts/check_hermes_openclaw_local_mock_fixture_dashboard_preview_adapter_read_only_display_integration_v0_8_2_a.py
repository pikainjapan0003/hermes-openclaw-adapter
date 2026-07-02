"""v0.8.2-A readiness check: Dashboard Preview Adapter Read-only Display Integration.

Pure local filesystem + git metadata validation. This script confirms the tracked state of the
v0.8.1-V/Z artifacts, confirms the effective changed-file scope, and inspects ONLY the *added* lines
of `app/main.py` and `templates/system.html` for the required build_dashboard_preview_model() wiring
and the absence of any forbidden call/route/control pattern. It never diffs or scans unrelated
pre-existing lines in those files, so pre-existing POST routes / QueueStore usage elsewhere in
app/main.py cannot trip this check.

Diff scope is post-commit-aware AND fixed-range-aware: the "effective changed paths" and "effective
added lines" for a file are the UNION of (a) `git diff --name-only EXPECTED_BASE_HEAD..TARGET` / `git
diff --unified=0 EXPECTED_BASE_HEAD..TARGET -- <file>` (the committed diff since the v0.8.1-Z base
commit) and (b) the bare working-tree `git diff --name-only` / `git diff --unified=0 -- <file>` (any
currently uncommitted change). TARGET is `EXPECTED_V0_8_2_A_FINAL_HEAD` once HEAD has grown past it
(i.e. once v0.8.2-A itself is fully committed), so later unrelated commits (v0.8.2-B and beyond) are
never pulled into the committed diff and never misclassified as v0.8.2-A changed files; TARGET falls
back to `HEAD` while HEAD has not yet reached `EXPECTED_V0_8_2_A_FINAL_HEAD` (pre-final history). This
means the script gives the same answer whether the v0.8.2-A implementation is still uncommitted
(pre-commit Owner Review), has already been committed (post-commit regression), has since been
followed by unrelated later commits (e.g. v0.8.2-B), or is in a mixed state (e.g. this validation
script itself has an uncommitted follow-up edit after app/main.py and templates/system.html were
already committed) — no separate mode flag is needed because the union naturally degrades to whichever
side is non-empty and the fixed range naturally excludes unrelated later history.

It does NOT import app runtime, Dashboard runtime, QueueStore, Worker/OpenClaw/Hermes/Google Sheets
integration, or the v0.8.1-P loader; it never starts a server; it reads no real queue DB, sends no
POST, makes no network call, reads no secrets, writes no repo file, and modifies no git index.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

SELF_SCRIPT_REL = "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_read_only_display_integration_v0_8_2_a.py"
SELF_SCRIPT_PATH = REPO_ROOT / SELF_SCRIPT_REL

V_ADAPTER_PATH = REPO_ROOT / "scripts/local_mock_fixture_dashboard_preview_adapter_v0_8_1.py"
Z_DOC_PATH = REPO_ROOT / "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_DASHBOARD_PREVIEW_ADAPTER_INTEGRATION_IMPLEMENTATION_PLAN_V0_8_1_Z.md"

MAIN_PY_PATH = REPO_ROOT / "app/main.py"
SYSTEM_HTML_PATH = REPO_ROOT / "templates/system.html"

EXPECTED_BASE_HEAD = "9fb42bc1dde7d9a0b6a9ea33842cfa6f3c7a56df"
EXPECTED_V0_8_2_A_FINAL_HEAD = "7206afa7ed000fbaab761a1f0018524849cc8815"

REQUIRED_IMPLEMENTATION_PATHS = {"app/main.py", "templates/system.html", SELF_SCRIPT_REL}
ALLOWED_NEW_UNTRACKED = {SELF_SCRIPT_REL}

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


def git_tracked(rel: str) -> bool:
    out = run_git(["ls-files", "--", rel])
    return out.returncode == 0 and out.stdout.strip() != ""


def committed_diff_target() -> str:
    """The upper end of the v0.8.2-A committed diff range.

    v0.8.2-A's finalized committed scope ends at EXPECTED_V0_8_2_A_FINAL_HEAD. Once HEAD has grown
    past that point (e.g. v0.8.2-B and later commits), the committed diff must stay pinned to
    EXPECTED_BASE_HEAD..EXPECTED_V0_8_2_A_FINAL_HEAD so later unrelated commits are never counted as
    v0.8.2-A changed files. If HEAD has not yet reached EXPECTED_V0_8_2_A_FINAL_HEAD (pre-final
    history, e.g. mid v0.8.2-A development), fall back to EXPECTED_BASE_HEAD..HEAD.
    """
    final_check = run_git(["merge-base", "--is-ancestor", EXPECTED_V0_8_2_A_FINAL_HEAD, "HEAD"])
    if final_check.returncode == 0:
        return EXPECTED_V0_8_2_A_FINAL_HEAD
    return "HEAD"


def committed_change_names_since_base() -> set[str]:
    """Files changed in the committed diff between EXPECTED_BASE_HEAD and committed_diff_target()."""
    target = committed_diff_target()
    return set(git_lines(["diff", "--name-only", f"{EXPECTED_BASE_HEAD}..{target}"]))


def working_tree_change_names() -> set[str]:
    """Files with an uncommitted (working-tree vs index/HEAD) change."""
    return set(git_lines(["diff", "--name-only"]))


def untracked_names() -> set[str]:
    return set(git_lines(["ls-files", "--others", "--exclude-standard"]))


def effective_changed_paths() -> set[str]:
    """Union of committed-since-base changes, uncommitted working-tree changes, and allowed new
    untracked files. Works whether this round is fully committed, fully uncommitted, or mixed."""
    committed = committed_change_names_since_base()
    working = working_tree_change_names()
    allowed_untracked = {p for p in untracked_names() if p in ALLOWED_NEW_UNTRACKED}
    return committed | working | allowed_untracked


def diff_added_lines(args: list[str]) -> str:
    out = run_git(args)
    added: list[str] = []
    for line in out.stdout.splitlines():
        if line.startswith("+++"):
            continue
        if line.startswith("+"):
            added.append(line[1:])
    return "\n".join(added)


def git_added_lines(rel: str) -> str:
    """Effective added lines for `rel`: union of committed-since-base added lines and any
    uncommitted working-tree added lines. Post-commit-aware (see module docstring)."""
    parts: list[str] = []
    target = committed_diff_target()

    if rel in committed_change_names_since_base():
        parts.append(diff_added_lines(["diff", "--unified=0", f"{EXPECTED_BASE_HEAD}..{target}", "--", rel]))

    if rel in working_tree_change_names():
        parts.append(diff_added_lines(["diff", "--unified=0", "--", rel]))

    return "\n".join(part for part in parts if part)


# ---------------------------------------------------------------------------
# [A] current HEAD contains EXPECTED_BASE_HEAD in git history
# ---------------------------------------------------------------------------
print("[A] current HEAD contains EXPECTED_BASE_HEAD in git history")
ancestor_check = run_git(["merge-base", "--is-ancestor", EXPECTED_BASE_HEAD, "HEAD"])
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
# [G] effective changed paths only touch allowed files
# ---------------------------------------------------------------------------
print("[G] effective changed paths only touch allowed files")
effective_changed = effective_changed_paths()
unexpected_changed = effective_changed - REQUIRED_IMPLEMENTATION_PATHS
missing_changed = REQUIRED_IMPLEMENTATION_PATHS - effective_changed
check(
    f"G. only app/main.py, templates/system.html, and the v0.8.2-A validation script are changed（unexpected={sorted(unexpected_changed)}, missing={sorted(missing_changed)}）"
    if (unexpected_changed or missing_changed)
    else "G. only app/main.py, templates/system.html, and the v0.8.2-A validation script are changed",
    not unexpected_changed and not missing_changed,
)

untracked = untracked_names()
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
# app/main.py effective-added-lines checks [H0, H-N]
# ---------------------------------------------------------------------------
main_added = git_added_lines("app/main.py")

print("[H0] app/main.py effective added lines are non-empty")
check("H0. app/main.py effective added lines are non-empty", bool(main_added.strip()))

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
# templates/system.html effective-added-lines checks [O0, O-S]
# ---------------------------------------------------------------------------
system_added = git_added_lines("templates/system.html")

print("[O0] templates/system.html effective added lines are non-empty")
check("O0. templates/system.html effective added lines are non-empty", bool(system_added.strip()))

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
# [T-X] no other protected artifact changed (using effective changed paths)
# ---------------------------------------------------------------------------
print("[T] no static file changed")
check("T. no static file changed", not any(p.startswith("static/") for p in effective_changed))

print("[U] no fixture JSON changed")
check(
    "U. no fixture JSON changed",
    "fixtures/local_mock_data/hermes_openclaw_local_mock_messages_v0_8_1.json" not in effective_changed,
)

print("[V] no P loader changed")
check("V. no P loader changed", "scripts/load_local_mock_fixture_preview_v0_8_1.py" not in effective_changed)

print("[W] no V adapter changed")
check(
    "W. no V adapter changed",
    "scripts/local_mock_fixture_dashboard_preview_adapter_v0_8_1.py" not in effective_changed,
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
    not (effective_changed & PROTECTED_WXYZ),
)

# ---------------------------------------------------------------------------
# [Y] patches/ remains untracked and untouched
# ---------------------------------------------------------------------------
print("[Y] patches/ remains untracked and untouched")
check(
    "Y. patches/ remains untracked and untouched",
    not any(p.startswith("patches/") for p in effective_changed),
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
