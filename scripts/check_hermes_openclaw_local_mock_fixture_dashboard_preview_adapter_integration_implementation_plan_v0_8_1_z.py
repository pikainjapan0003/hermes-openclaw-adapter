"""v0.8.1-Z readiness check: Local Mock Fixture Dashboard Preview Adapter Integration Implementation Plan
(implementation plan-only).

Pure local filesystem + git metadata validation. This script reads only the v0.8.1-Z implementation
plan doc and confirms the tracked state of the L/P/V/W/X/Y artifacts. It uses `git` read-only
(ls-files / diff / status / merge-base) to confirm tracked status, ancestry, and that no extra repo
files exist; it never modifies the git index.

It does NOT import Dashboard, app runtime, QueueStore, Worker/OpenClaw/Hermes/Google Sheets
integration, the v0.8.1-V adapter, or the v0.8.1-P loader; it reads no real queue DB, sends no POST,
makes no network call, reads no secrets, writes no repo file, modifies no adapter, modifies no loader,
and modifies no Dashboard. It does not read the fixture JSON directly.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

Z_DOC_PATH = REPO_ROOT / "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_DASHBOARD_PREVIEW_ADAPTER_INTEGRATION_IMPLEMENTATION_PLAN_V0_8_1_Z.md"
Z_SCRIPT_PATH = REPO_ROOT / "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_integration_implementation_plan_v0_8_1_z.py"

FIXTURE_PATH = REPO_ROOT / "fixtures/local_mock_data/hermes_openclaw_local_mock_messages_v0_8_1.json"
P_LOADER_PATH = REPO_ROOT / "scripts/load_local_mock_fixture_preview_v0_8_1.py"

V_ADAPTER_PATH = REPO_ROOT / "scripts/local_mock_fixture_dashboard_preview_adapter_v0_8_1.py"
V_READINESS_PATH = REPO_ROOT / "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_v0_8_1_v.py"

W_SCRIPT_PATH = REPO_ROOT / "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_runtime_check_v0_8_1_w.py"

X_DOC_PATH = REPO_ROOT / "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_DASHBOARD_PREVIEW_ADAPTER_INTEGRATION_BOUNDARY_PLAN_V0_8_1_X.md"
X_SCRIPT_PATH = REPO_ROOT / "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_integration_boundary_plan_v0_8_1_x.py"

Y_DOC_PATH = REPO_ROOT / "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_DASHBOARD_PREVIEW_ADAPTER_INTEGRATION_AUTHORIZATION_PLAN_V0_8_1_Y.md"
Y_SCRIPT_PATH = REPO_ROOT / "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_integration_authorization_plan_v0_8_1_y.py"

EXPECTED_BASE_HEAD = "dc71aa73cbe162cab5a0e913d6d05701e9e69fc6"

EXACT_Y_AUTHORIZATION_PHRASE = (
    "批准進入 v0.8.1 Dashboard preview adapter integration 下一步，"
    "僅允許未來 Dashboard 透過 build_dashboard_preview_model() 從 v0.8.1-V read-only preview adapter "
    "取得 synthetic local-only read-only preview model，並以 read-only display 呈現；"
    "不直接讀 fixture JSON，不呼叫 load_local_mock_fixture_preview()，不讀 real queue DB，不 POST，"
    "不啟 Worker/OpenClaw/Hermes/Google Sheets，不讀 secrets，"
    "不暴露 execution/dispatch/external action controls，不建立 production/shared DB，"
    "不建立 Remote Blackboard API runtime。"
)

DASHBOARD_PROTECTED_PREFIXES = [
    "app/",
    "templates/",
    "static/",
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


def git_tracked(rel: str) -> bool:
    out = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "ls-files", "--", rel],
        capture_output=True,
        text=True,
    )
    return out.returncode == 0 and out.stdout.strip() != ""


# ---------------------------------------------------------------------------
# [A/B] Z implementation plan doc + readiness script exist
# ---------------------------------------------------------------------------
print("[A] Z doc exists")
check("A. Z doc exists", Z_DOC_PATH.exists())
if not Z_DOC_PATH.exists():
    print("\nXX Z implementation plan doc 不存在，無法繼續")
    sys.exit(1)

print("[B] Z readiness script path is correct")
check("B. Z readiness script exists at expected path", Z_SCRIPT_PATH.exists())

doc = Z_DOC_PATH.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# [C-H] L/P/V/W/X/Y artifacts exist and are tracked
# ---------------------------------------------------------------------------
print("[C] L fixture JSON exists and is tracked")
check("C. L fixture JSON exists", FIXTURE_PATH.exists())
check(
    "C. L fixture JSON is tracked",
    git_tracked("fixtures/local_mock_data/hermes_openclaw_local_mock_messages_v0_8_1.json"),
)

print("[D] P loader exists and is tracked")
check("D. P loader exists", P_LOADER_PATH.exists())
check("D. P loader is tracked", git_tracked("scripts/load_local_mock_fixture_preview_v0_8_1.py"))

print("[E] V adapter/readiness script exist and are tracked")
check("E. V adapter exists", V_ADAPTER_PATH.exists())
check(
    "E. V adapter is tracked",
    git_tracked("scripts/local_mock_fixture_dashboard_preview_adapter_v0_8_1.py"),
)
check("E. V readiness script exists", V_READINESS_PATH.exists())
check(
    "E. V readiness script is tracked",
    git_tracked("scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_v0_8_1_v.py"),
)

print("[F] W runtime check exists and is tracked")
check("F. W runtime check script exists", W_SCRIPT_PATH.exists())
check(
    "F. W runtime check script is tracked",
    git_tracked("scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_runtime_check_v0_8_1_w.py"),
)

print("[G] X boundary doc/script exist and are tracked")
check("G. X boundary doc exists", X_DOC_PATH.exists())
check(
    "G. X boundary doc is tracked",
    git_tracked(
        "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_DASHBOARD_PREVIEW_ADAPTER_INTEGRATION_BOUNDARY_PLAN_V0_8_1_X.md"
    ),
)
check("G. X readiness script exists", X_SCRIPT_PATH.exists())
check(
    "G. X readiness script is tracked",
    git_tracked(
        "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_integration_boundary_plan_v0_8_1_x.py"
    ),
)

print("[H] Y authorization doc/script exist and are tracked")
check("H. Y authorization doc exists", Y_DOC_PATH.exists())
check(
    "H. Y authorization doc is tracked",
    git_tracked(
        "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_DASHBOARD_PREVIEW_ADAPTER_INTEGRATION_AUTHORIZATION_PLAN_V0_8_1_Y.md"
    ),
)
check("H. Y readiness script exists", Y_SCRIPT_PATH.exists())
check(
    "H. Y readiness script is tracked",
    git_tracked(
        "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_integration_authorization_plan_v0_8_1_y.py"
    ),
)

# ---------------------------------------------------------------------------
# [I] current HEAD contains EXPECTED_BASE_HEAD in git history
# ---------------------------------------------------------------------------
print("[I] current HEAD contains EXPECTED_BASE_HEAD in git history")
ancestor_check = subprocess.run(
    ["git", "-C", str(REPO_ROOT), "merge-base", "--is-ancestor", EXPECTED_BASE_HEAD, "HEAD"],
    capture_output=True,
    text=True,
)
check(
    f"I. HEAD contains {EXPECTED_BASE_HEAD} in git history",
    ancestor_check.returncode == 0,
)

# ---------------------------------------------------------------------------
# [J-AM] required doc content
# ---------------------------------------------------------------------------
print("[J] Z doc contains v0.8.1-Z title")
check(
    "J. Z doc contains v0.8.1-Z title",
    "v0.8.1-Z" in doc and "Dashboard Preview Adapter Integration Implementation Plan" in doc,
)

print("[K] Z doc contains base HEAD")
check("K. Z doc contains base HEAD", f"Base HEAD / origin/master:\n{EXPECTED_BASE_HEAD}" in doc)

print("[L] Z doc states implementation-plan-only positioning")
check("L. Z doc states implementation-plan-only positioning", "v0.8.1-Z is an implementation plan only." in doc)

print("[M] Z doc states Z does not modify Dashboard")
check("M. Z doc states Z does not modify Dashboard", "v0.8.1-Z does not modify Dashboard." in doc)

print("[N] Z doc states Z does not modify adapter")
check("N. Z doc states Z does not modify adapter", "v0.8.1-Z does not modify adapter." in doc)

print("[O] Z doc states Z does not modify loader")
check("O. Z doc states Z does not modify loader", "v0.8.1-Z does not modify loader." in doc)

print("[P] Z doc states Z does not create or modify route/endpoint/template/static asset")
check(
    "P. Z doc states Z does not create or modify route/endpoint/template/static asset",
    "v0.8.1-Z does not create or modify route, endpoint, template, static asset, QueueStore, approval route, Worker, OpenClaw, Hermes, or Google Sheets integration."
    in doc,
)

print("[Q] Z doc states dependency on Y")
check("Q. Z doc states dependency on Y", "v0.8.1-Z depends on v0.8.1-Y." in doc)

print("[R] Z doc contains the Y exact explicit Owner authorization phrase exactly once")
check(
    "R. Z doc contains the Y exact explicit Owner authorization phrase exactly once",
    doc.count(EXACT_Y_AUTHORIZATION_PHRASE) == 1,
)

print("[S] Z doc defines future data source as build_dashboard_preview_model()")
check(
    "S. Z doc defines future data source as build_dashboard_preview_model()",
    "Future Dashboard integration must import only:\nbuild_dashboard_preview_model()" in doc,
)

print("[T] Z doc allows only V adapter source module")
check(
    "T. Z doc allows only V adapter source module",
    "Allowed source module:\nscripts/local_mock_fixture_dashboard_preview_adapter_v0_8_1.py" in doc,
)

print("[U] Z doc optionally allows build_dashboard_preview_rows()")
check(
    "U. Z doc optionally allows build_dashboard_preview_rows()",
    "Optional display-only helper:\nbuild_dashboard_preview_rows()" in doc,
)

print("[V] Z doc forbids load_local_mock_fixture_preview()")
check(
    "V. Z doc forbids load_local_mock_fixture_preview()",
    "Future Dashboard integration must not import or call:\nload_local_mock_fixture_preview()" in doc,
)

print("[W] Z doc forbids validate_local_mock_fixture_preview_object()")
check("W. Z doc forbids validate_local_mock_fixture_preview_object()", "validate_local_mock_fixture_preview_object()" in doc)

print("[X] Z doc forbids fixture JSON direct read")
check("X. Z doc forbids fixture JSON direct read", "fixture JSON path" in doc)

print("[Y] Z doc forbids QueueStore / real queue DB")
check("Y. Z doc forbids QueueStore / real queue DB", "QueueStore" in doc and "real queue DB" in doc)

print("[Z] Z doc forbids Worker/OpenClaw/Hermes/Google Sheets")
check(
    "Z. Z doc forbids Worker/OpenClaw/Hermes/Google Sheets",
    "Worker" in doc and "OpenClaw" in doc and "Hermes" in doc and "Google Sheets" in doc,
)

print("[AA] Z doc defines future Dashboard display contract")
check(
    "AA. Z doc defines future Dashboard display contract",
    "## 7. Future Dashboard display contract, plan-only" in doc
    and "The future Dashboard display must be read-only." in doc,
)

print("[AB] Z doc requires disabled runtime badges")
check(
    "AB. Z doc requires disabled runtime badges",
    "DISPATCH OFF" in doc
    and "WORKER OFF" in doc
    and "OPENCLAW NOT CONNECTED" in doc
    and "HERMES NOT CONNECTED" in doc
    and "GOOGLE SHEETS DISABLED" in doc,
)

print("[AC] Z doc forbids Run/Execute/Dispatch/Approve and Dispatch/Send/POST controls")
check(
    "AC. Z doc forbids Run/Execute/Dispatch/Approve and Dispatch/Send/POST controls",
    "No Run button." in doc
    and "No Execute button." in doc
    and "No Dispatch button." in doc
    and "No Approve and Dispatch button." in doc
    and "No Send button." in doc
    and "No POST form." in doc,
)

print("[AD] Z doc forbids action_url/post_url/webhook_url/endpoint_url/execute_url/dispatch_url")
check(
    "AD. Z doc forbids action_url/post_url/webhook_url/endpoint_url/execute_url/dispatch_url",
    "No action_url." in doc
    and "No post_url." in doc
    and "No webhook_url." in doc
    and "No endpoint_url." in doc
    and "No execute_url." in doc
    and "No dispatch_url." in doc,
)

print("[AE] Z doc contains Future candidate files section")
check(
    "AE. Z doc contains Future candidate files section",
    "## Future candidate files from read-only repository inspection" in doc,
)

print("[AF] Z doc states candidate files are not modified by Z")
check(
    "AF. Z doc states candidate files are not modified by Z",
    "These candidate files are not modified by v0.8.1-Z." in doc,
)

print("[AG] Z doc states candidate files are not authorized for modification by Z")
check(
    "AG. Z doc states candidate files are not authorized for modification by Z",
    "These candidate files are not authorized for modification by v0.8.1-Z." in doc,
)

print("[AH] Z doc defines future minimum implementation steps")
check(
    "AH. Z doc defines future minimum implementation steps",
    "## 10. Future minimum implementation steps, plan-only" in doc
    and "1. Import build_dashboard_preview_model() from scripts/local_mock_fixture_dashboard_preview_adapter_v0_8_1.py"
    in doc,
)

print("[AI] Z doc defines future validation requirements")
check(
    "AI. Z doc defines future validation requirements",
    "## 11. Future validation requirements, plan-only" in doc
    and "Future implementation validation must confirm:" in doc,
)

print("[AJ] Z doc defines rollback boundary")
check(
    "AJ. Z doc defines rollback boundary",
    "## 12. Future rollback boundary, plan-only" in doc
    and "Rollback must not modify Z implementation plan." in doc,
)

print("[AK] Z doc defines v0.8.2-A exact future implementation authorization phrase")
EXACT_V082A_PHRASE = (
    "批准實作 v0.8.2-A — Dashboard Preview Adapter Read-only Display Integration，"
    "僅允許在已於 v0.8.1-Z 列明並經 Owner Review 的 Dashboard display-only surface 中呼叫 "
    "build_dashboard_preview_model()，將 v0.8.1-V read-only preview adapter 回傳的 synthetic "
    "local-only read-only preview model 以 read-only rows / disabled badges / false permission "
    "flags 呈現；不直接讀 fixture JSON，不呼叫 P loader，不讀 real queue DB，不 POST，"
    "不暴露 execution/dispatch/external action controls，不啟 Worker/OpenClaw/Hermes/Google Sheets，"
    "不讀 secrets，不建立 production/shared DB，不建立 Remote Blackboard API runtime。"
)
check(
    "AK. Z doc defines v0.8.2-A exact future implementation authorization phrase",
    doc.count(EXACT_V082A_PHRASE) == 1,
)

print("[AL] Z doc says v0.8.2-A is not started")
check("AL. Z doc says v0.8.2-A is not started", "v0.8.2-A is not started by v0.8.1-Z." in doc)

print("[AM] Z doc says only exact v0.8.2-A phrase may authorize future implementation")
check(
    "AM. Z doc says only exact v0.8.2-A phrase may authorize future implementation",
    "Only the exact v0.8.2-A phrase above may authorize future implementation." in doc,
)

# ---------------------------------------------------------------------------
# [AN] no tracked working-tree modifications
# ---------------------------------------------------------------------------
print("[AN] no tracked working-tree modifications")
diff_out = subprocess.run(
    ["git", "-C", str(REPO_ROOT), "diff", "--name-only"],
    capture_output=True,
    text=True,
)
tracked_changes = [l for l in diff_out.stdout.splitlines() if l.strip()]
check(
    f"AN. no tracked working-tree modifications（found {tracked_changes}）"
    if tracked_changes
    else "AN. no tracked working-tree modifications",
    not tracked_changes,
)

# ---------------------------------------------------------------------------
# [AO] no Dashboard/app/templates/static files changed (staged or unstaged)
# ---------------------------------------------------------------------------
print("[AO] no Dashboard/app/templates/static files changed")
status_out = subprocess.run(
    ["git", "-C", str(REPO_ROOT), "status", "--porcelain"],
    capture_output=True,
    text=True,
)
changed_paths = []
for line in status_out.stdout.splitlines():
    if not line.strip():
        continue
    # porcelain format: XY <path>  (path starts at column 3)
    path = line[3:].strip()
    changed_paths.append(path)
dashboard_changes = [
    p for p in changed_paths if any(p.startswith(pref) for pref in DASHBOARD_PROTECTED_PREFIXES)
]
check(
    f"AO. no Dashboard/app/templates/static files changed（found {dashboard_changes}）"
    if dashboard_changes
    else "AO. no Dashboard/app/templates/static files changed",
    not dashboard_changes,
)

# ---------------------------------------------------------------------------
# [AP] no extra untracked files beyond allowed Z files and existing patches/
# ---------------------------------------------------------------------------
print("[AP] no extra untracked files beyond allowed Z files and patches/")
others_out = subprocess.run(
    ["git", "-C", str(REPO_ROOT), "ls-files", "--others", "--exclude-standard"],
    capture_output=True,
    text=True,
)
ALLOWED_UNTRACKED = {
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_DASHBOARD_PREVIEW_ADAPTER_INTEGRATION_IMPLEMENTATION_PLAN_V0_8_1_Z.md",
    "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_integration_implementation_plan_v0_8_1_z.py",
}
untracked = [l for l in others_out.stdout.splitlines() if l.strip()]
unexpected = [u for u in untracked if u not in ALLOWED_UNTRACKED and not u.startswith("patches/")]
check(
    f"AP. no unexpected untracked files（found {unexpected}）" if unexpected else "AP. no unexpected untracked files",
    not unexpected,
)

# ---------------------------------------------------------------------------
# 結果
# ---------------------------------------------------------------------------
total = len(PASS) + len(FAIL)
print(f"\n合計：{len(PASS)}/{total} 通過")
if FAIL:
    print(f"\nXX v0.8.1-Z readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print("PASS: v0.8.1-Z dashboard preview adapter integration implementation plan")
    sys.exit(0)
