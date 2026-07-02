"""v0.8.2-C readiness check: Dashboard Read-only Preview UI Refinement Implementation.

Pure local filesystem + git metadata validation. This script confirms the tracked state of the
v0.8.2-B plan doc/readiness script and the v0.8.2-A validation script, confirms the exact v0.8.2-C
Owner authorization phrase is present in the v0.8.2-B plan doc exactly once, confirms the effective
changed-file scope is limited to templates/system.html and static/dashboard.css (plus this new,
still-untracked validation script), and inspects the current content of templates/system.html and
static/dashboard.css for the required read-only preview refinement markers and the absence of any
forbidden interactive control.

It uses `git` read-only (ls-files / diff / status / merge-base) to confirm tracked status, ancestry,
and effective changed-file scope; it never modifies the git index.

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

SELF_SCRIPT_REL = "scripts/check_hermes_openclaw_dashboard_read_only_preview_ui_refinement_v0_8_2_c.py"
SELF_SCRIPT_PATH = REPO_ROOT / SELF_SCRIPT_REL

B_DOC_REL = "docs/HERMES_OPENCLAW_DASHBOARD_READ_ONLY_PREVIEW_UI_REFINEMENT_PLAN_V0_8_2_B.md"
B_DOC_PATH = REPO_ROOT / B_DOC_REL
B_SCRIPT_REL = "scripts/check_hermes_openclaw_dashboard_read_only_preview_ui_refinement_plan_v0_8_2_b.py"
B_SCRIPT_PATH = REPO_ROOT / B_SCRIPT_REL

V082A_SCRIPT_REL = "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_read_only_display_integration_v0_8_2_a.py"
V082A_SCRIPT_PATH = REPO_ROOT / V082A_SCRIPT_REL

MAIN_PY_REL = "app/main.py"
MAIN_PY_PATH = REPO_ROOT / MAIN_PY_REL
SYSTEM_HTML_REL = "templates/system.html"
SYSTEM_HTML_PATH = REPO_ROOT / SYSTEM_HTML_REL
DASHBOARD_CSS_REL = "static/dashboard.css"
DASHBOARD_CSS_PATH = REPO_ROOT / DASHBOARD_CSS_REL

FIXTURE_JSON_REL = "fixtures/local_mock_data/hermes_openclaw_local_mock_messages_v0_8_1.json"
P_LOADER_REL = "scripts/load_local_mock_fixture_preview_v0_8_1.py"
V_ADAPTER_REL = "scripts/local_mock_fixture_dashboard_preview_adapter_v0_8_1.py"
PROTECTED_WXYZ = {
    "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_runtime_check_v0_8_1_w.py",
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_DASHBOARD_PREVIEW_ADAPTER_INTEGRATION_BOUNDARY_PLAN_V0_8_1_X.md",
    "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_integration_boundary_plan_v0_8_1_x.py",
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_DASHBOARD_PREVIEW_ADAPTER_INTEGRATION_AUTHORIZATION_PLAN_V0_8_1_Y.md",
    "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_integration_authorization_plan_v0_8_1_y.py",
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_DASHBOARD_PREVIEW_ADAPTER_INTEGRATION_IMPLEMENTATION_PLAN_V0_8_1_Z.md",
    "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_integration_implementation_plan_v0_8_1_z.py",
}

EXPECTED_BASE_HEAD = "b85e1caa3bebbef73db101cae68f9aa6924ef334"

ALLOWED_CHANGED_TRACKED = {SYSTEM_HTML_REL, DASHBOARD_CSS_REL}
ALLOWED_NEW_UNTRACKED = {SELF_SCRIPT_REL}

EXACT_V082C_PHRASE = (
    "批准實作 v0.8.2-C — Dashboard Read-only Preview UI Refinement Implementation，"
    "僅允許改善 v0.8.2-A 已存在的 /dashboard/system read-only preview display 的版面、"
    "標籤、說明文字、表格可讀性與 CSS 樣式；必須保持 GET-only、read-only、synthetic local-only、"
    "permission flags false、disabled runtime badges visible；"
    "不得修改資料來源，不得呼叫 P loader，不得直接讀 fixture JSON，不得讀 real queue DB，不得 POST，"
    "不得新增 button/form/action URL/webhook/endpoint/execute/dispatch/send controls，"
    "不得啟 Worker/OpenClaw/Hermes/Google Sheets，不得讀 secrets，"
    "不得建立 production/shared DB 或 Remote Blackboard API runtime。"
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


def git_tracked(rel: str) -> bool:
    out = run_git(["ls-files", "--", rel])
    return out.returncode == 0 and out.stdout.strip() != ""


def working_tree_change_names() -> set[str]:
    return set(git_lines(["diff", "--name-only"]))


def untracked_names() -> set[str]:
    return set(git_lines(["ls-files", "--others", "--exclude-standard"]))


def diff_added_lines(rel: str) -> str:
    out = run_git(["diff", "--unified=0", "--", rel])
    added: list[str] = []
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
ancestor_check = run_git(["merge-base", "--is-ancestor", EXPECTED_BASE_HEAD, "HEAD"])
check(
    f"A. HEAD contains {EXPECTED_BASE_HEAD} in git history",
    ancestor_check.returncode == 0,
)

# ---------------------------------------------------------------------------
# [B/C] B plan doc / B readiness script exist and are tracked
# ---------------------------------------------------------------------------
print("[B] B plan doc exists and is tracked")
check("B. B plan doc exists", B_DOC_PATH.exists())
check("B. B plan doc is tracked", git_tracked(B_DOC_REL))

print("[C] B readiness script exists and is tracked")
check("C. B readiness script exists", B_SCRIPT_PATH.exists())
check("C. B readiness script is tracked", git_tracked(B_SCRIPT_REL))

# ---------------------------------------------------------------------------
# [D] v0.8.2-A validation script exists and is tracked
# ---------------------------------------------------------------------------
print("[D] v0.8.2-A validation script exists and is tracked")
check("D. v0.8.2-A validation script exists", V082A_SCRIPT_PATH.exists())
check("D. v0.8.2-A validation script is tracked", git_tracked(V082A_SCRIPT_REL))

# ---------------------------------------------------------------------------
# [E/F/G] app/main.py, templates/system.html, static/dashboard.css exist and tracked
# ---------------------------------------------------------------------------
print("[E] app/main.py exists and is tracked")
check("E. app/main.py exists", MAIN_PY_PATH.exists())
check("E. app/main.py is tracked", git_tracked(MAIN_PY_REL))

print("[F] templates/system.html exists and is tracked")
check("F. templates/system.html exists", SYSTEM_HTML_PATH.exists())
check("F. templates/system.html is tracked", git_tracked(SYSTEM_HTML_REL))

print("[G] static/dashboard.css exists and is tracked")
check("G. static/dashboard.css exists", DASHBOARD_CSS_PATH.exists())
check("G. static/dashboard.css is tracked", git_tracked(DASHBOARD_CSS_REL))

# ---------------------------------------------------------------------------
# [H] C validation script exists
# ---------------------------------------------------------------------------
print("[H] C validation script exists")
check("H. C validation script exists at expected path", SELF_SCRIPT_PATH.exists())

# ---------------------------------------------------------------------------
# [I] exact v0.8.2-C authorization phrase exists in B doc exactly once
# ---------------------------------------------------------------------------
print("[I] exact v0.8.2-C authorization phrase exists in B doc exactly once")
b_doc_text = B_DOC_PATH.read_text(encoding="utf-8") if B_DOC_PATH.exists() else ""
check(
    "I. exact v0.8.2-C authorization phrase exists in B doc exactly once",
    b_doc_text.count(EXACT_V082C_PHRASE) == 1,
)

# ---------------------------------------------------------------------------
# [J] git diff only touches allowed tracked files
# ---------------------------------------------------------------------------
print("[J] git diff only touches allowed tracked files")
tracked_changed = working_tree_change_names()
unexpected_tracked_changed = tracked_changed - ALLOWED_CHANGED_TRACKED
check(
    f"J. git diff only touches allowed tracked files（found unexpected={sorted(unexpected_tracked_changed)}）"
    if unexpected_tracked_changed
    else "J. git diff only touches allowed tracked files",
    not unexpected_tracked_changed,
)

# ---------------------------------------------------------------------------
# [K] untracked files allowed only: C validation script, patches/*
# ---------------------------------------------------------------------------
print("[K] untracked files allowed only: C validation script, patches/*")
untracked = untracked_names()
unexpected_untracked = {
    u for u in untracked if u not in ALLOWED_NEW_UNTRACKED and not u.startswith("patches/")
}
check(
    f"K. no unexpected untracked files（found {sorted(unexpected_untracked)}）"
    if unexpected_untracked
    else "K. no unexpected untracked files",
    not unexpected_untracked,
)

# ---------------------------------------------------------------------------
# [L] app/main.py is not modified
# ---------------------------------------------------------------------------
print("[L] app/main.py is not modified")
check("L. app/main.py is not modified", MAIN_PY_REL not in tracked_changed)

# ---------------------------------------------------------------------------
# [M-S] templates/system.html effective content checks (read full current file)
# ---------------------------------------------------------------------------
system_html_text = SYSTEM_HTML_PATH.read_text(encoding="utf-8") if SYSTEM_HTML_PATH.exists() else ""

print("[M] templates/system.html effective content still contains Local Mock Dashboard Preview")
check(
    "M. templates/system.html effective content still contains Local Mock Dashboard Preview",
    "Local Mock Dashboard Preview" in system_html_text,
)

print("[N] templates/system.html effective content still contains local_mock_preview_model")
check(
    "N. templates/system.html effective content still contains local_mock_preview_model",
    "local_mock_preview_model" in system_html_text,
)

print("[O] templates/system.html effective content contains all disabled badges")
REQUIRED_BADGES = [
    "DISPATCH OFF",
    "WORKER OFF",
    "OPENCLAW NOT CONNECTED",
    "HERMES NOT CONNECTED",
    "GOOGLE SHEETS DISABLED",
]
check(
    "O. templates/system.html effective content contains all disabled badges",
    all(b in system_html_text for b in REQUIRED_BADGES),
)

print("[P] templates/system.html effective content contains all permission flags")
REQUIRED_FLAGS = [
    "is_mock",
    "local_only",
    "read_only",
    "execution_permission",
    "dispatch_permission",
    "external_side_effects_permission",
]
check(
    "P. templates/system.html effective content contains all permission flags",
    all(f in system_html_text for f in REQUIRED_FLAGS),
)

print("[Q] templates/system.html effective content contains Owner Review reminder wording")
check(
    "Q. templates/system.html effective content contains Owner Review reminder wording",
    "Owner Review required" in system_html_text,
)

print("[R] templates/system.html effective content contains read-only / local-only / synthetic explanation")
check(
    "R. templates/system.html effective content contains read-only / local-only / synthetic explanation",
    "Read-only synthetic local-only preview" in system_html_text,
)

print("[S] templates/system.html effective content contains rows table columns")
REQUIRED_COLUMNS = [
    "display_index",
    "display_title",
    "display_summary",
    "source_role",
    "target_role",
    "status",
]
check(
    "S. templates/system.html effective content contains rows table columns",
    all(c in system_html_text for c in REQUIRED_COLUMNS),
)

# ---------------------------------------------------------------------------
# [T] templates/system.html added lines do not contain forbidden controls
# ---------------------------------------------------------------------------
print("[T] templates/system.html added lines do not contain forbidden controls")
system_html_added = diff_added_lines(SYSTEM_HTML_REL)
system_html_added_lower = system_html_added.lower()
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
]
check(
    "T. templates/system.html added lines do not contain forbidden controls",
    not any(p in system_html_added_lower for p in FORBIDDEN_CONTROL_PATTERNS),
)

# ---------------------------------------------------------------------------
# [U/V/W] static/dashboard.css checks
# ---------------------------------------------------------------------------
dashboard_css_text = DASHBOARD_CSS_PATH.read_text(encoding="utf-8") if DASHBOARD_CSS_PATH.exists() else ""

print("[U] static/dashboard.css contains v0.8.2-C marker comment")
check(
    "U. static/dashboard.css contains v0.8.2-C marker comment",
    "v0.8.2-C" in dashboard_css_text,
)

print("[V] static/dashboard.css contains .local-mock-preview class family")
REQUIRED_CSS_CLASSES = [
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
check(
    "V. static/dashboard.css contains .local-mock-preview class family",
    all(c in dashboard_css_text for c in REQUIRED_CSS_CLASSES),
)

print(
    "[W] static/dashboard.css does not contain cursor: pointer / pointer-events / "
    "display: none for local mock preview safety info"
)
marker_index = dashboard_css_text.find("v0.8.2-C")
local_mock_css_block = dashboard_css_text[marker_index:] if marker_index != -1 else ""
FORBIDDEN_CSS_PATTERNS = ["cursor: pointer", "cursor:pointer", "pointer-events", "display: none", "display:none"]
check(
    "W. static/dashboard.css does not contain cursor: pointer / pointer-events / "
    "display: none for local mock preview safety info",
    marker_index != -1 and not any(p in local_mock_css_block for p in FORBIDDEN_CSS_PATTERNS),
)

# ---------------------------------------------------------------------------
# [X-AA] no other protected artifact changed
# ---------------------------------------------------------------------------
print("[X] no fixture JSON changed")
check("X. no fixture JSON changed", FIXTURE_JSON_REL not in tracked_changed)

print("[Y] no P loader changed")
check("Y. no P loader changed", P_LOADER_REL not in tracked_changed)

print("[Z] no V adapter changed")
check("Z. no V adapter changed", V_ADAPTER_REL not in tracked_changed)

print("[AA] no W/X/Y/Z artifacts changed")
check("AA. no W/X/Y/Z artifacts changed", not (tracked_changed & PROTECTED_WXYZ))

# ---------------------------------------------------------------------------
# [AB/AC/AD] no B doc / B readiness script / v0.8.2-A validation script changed
# ---------------------------------------------------------------------------
print("[AB] no B doc changed")
check("AB. no B doc changed", B_DOC_REL not in tracked_changed)

print("[AC] no B readiness script changed")
check("AC. no B readiness script changed", B_SCRIPT_REL not in tracked_changed)

print("[AD] no v0.8.2-A validation script changed")
check("AD. no v0.8.2-A validation script changed", V082A_SCRIPT_REL not in tracked_changed)

# ---------------------------------------------------------------------------
# [AE] patches/ remains untracked and untouched
# ---------------------------------------------------------------------------
print("[AE] patches/ remains untracked and untouched")
check(
    "AE. patches/ remains untracked and untouched",
    not any(p.startswith("patches/") for p in tracked_changed),
)

# ---------------------------------------------------------------------------
# 結果
# ---------------------------------------------------------------------------
total = len(PASS) + len(FAIL)
print(f"\n合計：{len(PASS)}/{total} 通過")
if FAIL:
    print(f"\nXX v0.8.2-C readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print("PASS: v0.8.2-C dashboard read-only preview UI refinement implementation")
    sys.exit(0)
