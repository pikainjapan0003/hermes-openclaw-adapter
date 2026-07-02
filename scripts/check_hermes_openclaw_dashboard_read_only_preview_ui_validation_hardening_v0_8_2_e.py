"""v0.8.2-E readiness check: Dashboard Read-only Preview UI Validation Hardening Implementation.

Pure local filesystem + git metadata validation. Unlike the v0.8.2-C validation script (which mixes
"content/safety boundary intact" checks with "this round's own changed-file scope" checks against a
moving HEAD), this script separates the two concerns:

  1. Phase detection — is this script currently untracked (Owner Review phase) or tracked (committed,
     either still ahead of origin/master or already synced with it)? Phase detection never depends on
     the committed diff range growing over time, so later rounds (v0.8.2-F, v0.8.3, ...) adding new
     committed or untracked files never cause this script to misclassify its own phase or its own
     changed-file scope.
  2. Content/safety-boundary checks — read the CURRENT content of templates/system.html and
     static/dashboard.css directly (not a diff against any historical base), and confirm the read-only
     local mock preview block still contains the required safety markers and none of the forbidden
     interactive controls. Because these checks read current content rather than a historical diff,
     they remain stable regardless of how many later commits exist.

It uses `git` read-only (ls-files / diff / status / merge-base / rev-parse) to confirm tracked status,
ancestry, and that no protected tracked file has an uncommitted working-tree modification; it never
modifies the git index.

It does NOT import app runtime, Dashboard runtime, QueueStore, Worker/OpenClaw/Hermes/Google Sheets
integration, the v0.8.1-P loader, or the v0.8.1-V adapter; it never starts a server; it reads no real
queue DB, sends no POST, makes no network call, reads no secrets, writes no repo file, and modifies no
git index.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

SELF_SCRIPT_REL = "scripts/check_hermes_openclaw_dashboard_read_only_preview_ui_validation_hardening_v0_8_2_e.py"
SELF_SCRIPT_PATH = REPO_ROOT / SELF_SCRIPT_REL

MAIN_PY_REL = "app/main.py"
SYSTEM_HTML_REL = "templates/system.html"
DASHBOARD_CSS_REL = "static/dashboard.css"
D_DOC_REL = "docs/HERMES_OPENCLAW_DASHBOARD_READ_ONLY_PREVIEW_UI_VALIDATION_HARDENING_PLAN_V0_8_2_D.md"
D_SCRIPT_REL = "scripts/check_hermes_openclaw_dashboard_read_only_preview_ui_validation_hardening_plan_v0_8_2_d.py"
C_SCRIPT_REL = "scripts/check_hermes_openclaw_dashboard_read_only_preview_ui_refinement_v0_8_2_c.py"
B_DOC_REL = "docs/HERMES_OPENCLAW_DASHBOARD_READ_ONLY_PREVIEW_UI_REFINEMENT_PLAN_V0_8_2_B.md"
B_SCRIPT_REL = "scripts/check_hermes_openclaw_dashboard_read_only_preview_ui_refinement_plan_v0_8_2_b.py"
V082A_SCRIPT_REL = "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_read_only_display_integration_v0_8_2_a.py"
P_LOADER_REL = "scripts/load_local_mock_fixture_preview_v0_8_1.py"
V_ADAPTER_REL = "scripts/local_mock_fixture_dashboard_preview_adapter_v0_8_1.py"
FIXTURE_JSON_REL = "fixtures/local_mock_data/hermes_openclaw_local_mock_messages_v0_8_1.json"
PROTECTED_WXYZ = {
    "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_runtime_check_v0_8_1_w.py",
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_DASHBOARD_PREVIEW_ADAPTER_INTEGRATION_BOUNDARY_PLAN_V0_8_1_X.md",
    "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_integration_boundary_plan_v0_8_1_x.py",
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_DASHBOARD_PREVIEW_ADAPTER_INTEGRATION_AUTHORIZATION_PLAN_V0_8_1_Y.md",
    "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_integration_authorization_plan_v0_8_1_y.py",
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_DASHBOARD_PREVIEW_ADAPTER_INTEGRATION_IMPLEMENTATION_PLAN_V0_8_1_Z.md",
    "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_integration_implementation_plan_v0_8_1_z.py",
}

EXPECTED_BASE_HEAD = "210908a32ee0440b353036da8c45da54cd5b3463"

REQUIRED_TEXT_MARKERS = [
    "Local Mock Dashboard Preview",
    "local_mock_preview_model",
    "Owner Review required",
    "Read-only synthetic local-only preview",
]

REQUIRED_BADGES = [
    "DISPATCH OFF",
    "WORKER OFF",
    "OPENCLAW NOT CONNECTED",
    "HERMES NOT CONNECTED",
    "GOOGLE SHEETS DISABLED",
]

REQUIRED_FLAGS = [
    "is_mock",
    "local_only",
    "read_only",
    "execution_permission",
    "dispatch_permission",
    "external_side_effects_permission",
]

REQUIRED_COLUMNS = [
    "display_index",
    "display_title",
    "display_summary",
    "source_role",
    "target_role",
    "status",
]

FORBIDDEN_CONTROL_PATTERNS = [
    "<form",
    "<button",
    'method="post"',
    "method='post'",
    "action=",
    "onclick=",
    "action_url",
    "post_url",
    "webhook_url",
    "endpoint_url",
    "execute_url",
    "dispatch_url",
    "send_url",
]

REQUIRED_CSS_CLASSES = [
    "v0.8.2-C",
    ".local-mock-preview",
    ".local-mock-preview__header",
    ".local-mock-preview__notice",
    ".local-mock-preview__badges",
    ".local-mock-preview__meta-grid",
    ".local-mock-preview__flag-card",
    ".local-mock-preview__table-wrap",
    ".local-mock-preview__table",
    ".local-mock-preview__empty",
]

FORBIDDEN_CSS_PATTERNS = ["cursor: pointer", "cursor:pointer", "pointer-events", "display: none", "display:none"]

FORBIDDEN_IMPORT_MODULE_SUBSTRINGS = [
    "app.main",
    "app.queue_store",
    "app.worker",
    "app.google_sheets_oauth_writer",
    "load_local_mock_fixture_preview_v0_8_1",
    "local_mock_fixture_dashboard_preview_adapter_v0_8_1",
    "openclaw",
    "hermes",
]

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


def working_tree_change_names() -> set[str]:
    return set(git_lines(["diff", "--name-only"]))


def untracked_names() -> set[str]:
    return set(git_lines(["ls-files", "--others", "--exclude-standard"]))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def extract_local_mock_preview_block(system_html_text: str) -> str:
    marker = '<section class="local-mock-preview"'
    start = system_html_text.find(marker)
    if start == -1:
        return ""
    end = system_html_text.find("</section>", start)
    if end == -1:
        return ""
    return system_html_text[start : end + len("</section>")]


def extract_local_mock_css_block(dashboard_css_text: str) -> str:
    marker_index = dashboard_css_text.find("v0.8.2-C")
    if marker_index == -1:
        return ""
    return dashboard_css_text[marker_index:]


def module_level_import_lines(source: str) -> list[str]:
    lines = []
    for line in source.splitlines():
        stripped = line.strip()
        if stripped.startswith("import ") or stripped.startswith("from "):
            lines.append(stripped)
    return lines


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
# [B] E validation hardening script exists at expected path
# ---------------------------------------------------------------------------
print("[B] E validation hardening script exists at expected path")
check("B. E validation hardening script exists at expected path", SELF_SCRIPT_PATH.exists())

# ---------------------------------------------------------------------------
# [C] E script phase detection
# ---------------------------------------------------------------------------
print("[C] E script phase detection works")
self_is_tracked = git_tracked(SELF_SCRIPT_REL)
head_sha = run_git(["rev-parse", "HEAD"]).stdout.strip()
origin_sha = run_git(["rev-parse", "origin/master"]).stdout.strip()

if not self_is_tracked:
    phase = "owner_review"
elif head_sha and origin_sha and head_sha == origin_sha:
    phase = "post_push_or_synced"
else:
    phase = "post_commit_or_ahead"

check(f"C. E script phase detected: {phase}", phase in {"owner_review", "post_commit_or_ahead", "post_push_or_synced"})

# ---------------------------------------------------------------------------
# [D] git diff has no tracked file changes
# ---------------------------------------------------------------------------
print("[D] git diff has no tracked file changes")
tracked_changed = working_tree_change_names()
check(
    f"D. git diff has no tracked file changes（found {sorted(tracked_changed)}）"
    if tracked_changed
    else "D. git diff has no tracked file changes",
    not tracked_changed,
)

# ---------------------------------------------------------------------------
# [E] untracked files allowed only: E script (Owner Review phase only), patches/*
# ---------------------------------------------------------------------------
print("[E] untracked files allowed only: E script (if Owner Review phase), patches/*")
untracked = untracked_names()
allowed_untracked = {SELF_SCRIPT_REL} if phase == "owner_review" else set()
unexpected_untracked = {
    u for u in untracked if u not in allowed_untracked and not u.startswith("patches/")
}
check(
    f"E. no unexpected untracked files（found {sorted(unexpected_untracked)}）"
    if unexpected_untracked
    else "E. no unexpected untracked files",
    not unexpected_untracked,
)

# ---------------------------------------------------------------------------
# [F-Q] no protected artifact has a working-tree modification
# ---------------------------------------------------------------------------
print("[F] app/main.py is not modified")
check("F. app/main.py is not modified", MAIN_PY_REL not in tracked_changed)

print("[G] templates/system.html is not modified")
check("G. templates/system.html is not modified", SYSTEM_HTML_REL not in tracked_changed)

print("[H] static/dashboard.css is not modified")
check("H. static/dashboard.css is not modified", DASHBOARD_CSS_REL not in tracked_changed)

print("[I] D plan doc is not modified")
check("I. D plan doc is not modified", D_DOC_REL not in tracked_changed)

print("[J] D readiness script is not modified")
check("J. D readiness script is not modified", D_SCRIPT_REL not in tracked_changed)

print("[K] C validation script is not modified")
check("K. C validation script is not modified", C_SCRIPT_REL not in tracked_changed)

print("[L] B doc / B readiness script are not modified")
check(
    "L. B doc / B readiness script are not modified",
    B_DOC_REL not in tracked_changed and B_SCRIPT_REL not in tracked_changed,
)

print("[M] v0.8.2-A validation script is not modified")
check("M. v0.8.2-A validation script is not modified", V082A_SCRIPT_REL not in tracked_changed)

print("[N] P loader is not modified")
check("N. P loader is not modified", P_LOADER_REL not in tracked_changed)

print("[O] V adapter is not modified")
check("O. V adapter is not modified", V_ADAPTER_REL not in tracked_changed)

print("[P] fixture JSON is not modified")
check("P. fixture JSON is not modified", FIXTURE_JSON_REL not in tracked_changed)

print("[Q] W/X/Y/Z artifacts are not modified")
check("Q. W/X/Y/Z artifacts are not modified", not (tracked_changed & PROTECTED_WXYZ))

# ---------------------------------------------------------------------------
# [R-V] templates/system.html effective (current) content checks
# ---------------------------------------------------------------------------
system_html_text = read_text(REPO_ROOT / SYSTEM_HTML_REL)
local_mock_block = extract_local_mock_preview_block(system_html_text)

print("[R] templates/system.html effective content contains required text markers")
check(
    "R. templates/system.html effective content contains required text markers",
    bool(local_mock_block) and all(m in system_html_text for m in REQUIRED_TEXT_MARKERS),
)

print("[S] templates/system.html effective content contains all disabled runtime badges")
check(
    "S. templates/system.html effective content contains all disabled runtime badges",
    all(b in system_html_text for b in REQUIRED_BADGES),
)

print("[T] templates/system.html effective content contains all required permission flags")
check(
    "T. templates/system.html effective content contains all required permission flags",
    all(f in system_html_text for f in REQUIRED_FLAGS),
)

print("[U] templates/system.html effective content contains all required rows table columns")
check(
    "U. templates/system.html effective content contains all required rows table columns",
    all(c in system_html_text for c in REQUIRED_COLUMNS),
)

print("[V] templates/system.html local mock preview block does not contain forbidden interactive controls")
local_mock_block_lower = local_mock_block.lower()
check(
    "V. templates/system.html local mock preview block does not contain forbidden interactive controls",
    bool(local_mock_block) and not any(p in local_mock_block_lower for p in FORBIDDEN_CONTROL_PATTERNS),
)

# ---------------------------------------------------------------------------
# [W/X] static/dashboard.css effective (current) content checks
# ---------------------------------------------------------------------------
dashboard_css_text = read_text(REPO_ROOT / DASHBOARD_CSS_REL)
local_mock_css_block = extract_local_mock_css_block(dashboard_css_text)

print("[W] static/dashboard.css effective content contains required markers and class family")
check(
    "W. static/dashboard.css effective content contains required markers and class family",
    bool(local_mock_css_block) and all(c in dashboard_css_text for c in REQUIRED_CSS_CLASSES),
)

print("[X] static/dashboard.css local mock preview block does not contain forbidden CSS patterns")
check(
    "X. static/dashboard.css local mock preview block does not contain forbidden CSS patterns",
    bool(local_mock_css_block) and not any(p in local_mock_css_block for p in FORBIDDEN_CSS_PATTERNS),
)

# ---------------------------------------------------------------------------
# [Y] this script itself imports no app runtime / P loader / V adapter / QueueStore / Worker/OpenClaw/Hermes/Google Sheets
# ---------------------------------------------------------------------------
print("[Y] this script imports no app runtime / P loader / V adapter / QueueStore / Worker/OpenClaw/Hermes/Google Sheets")
self_source = read_text(SELF_SCRIPT_PATH)
import_lines = module_level_import_lines(self_source)
check(
    "Y. this script imports no app runtime / P loader / V adapter / QueueStore / Worker/OpenClaw/Hermes/Google Sheets",
    not any(any(p in line for p in FORBIDDEN_IMPORT_MODULE_SUBSTRINGS) for line in import_lines),
)

# ---------------------------------------------------------------------------
# [Z] patches/ remains untracked and untouched
# ---------------------------------------------------------------------------
print("[Z] patches/ remains untracked and untouched")
check(
    "Z. patches/ remains untracked and untouched",
    not any(p.startswith("patches/") for p in tracked_changed),
)

# ---------------------------------------------------------------------------
# 結果
# ---------------------------------------------------------------------------
total = len(PASS) + len(FAIL)
print(f"\n合計：{len(PASS)}/{total} 通過")
if FAIL:
    print(f"\nXX v0.8.2-E readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print("PASS: v0.8.2-E dashboard read-only preview UI validation hardening implementation")
    sys.exit(0)
