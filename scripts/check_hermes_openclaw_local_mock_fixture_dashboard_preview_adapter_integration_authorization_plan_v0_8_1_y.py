"""v0.8.1-Y readiness check: Local Mock Fixture Dashboard Preview Adapter Integration Authorization Plan
(authorization plan-only).

Pure local filesystem + git metadata validation. This script reads only the v0.8.1-Y authorization plan
doc and confirms the tracked state of the L/M/N/O/P/Q/R/S/T/U/V/W/X artifacts. It uses `git` read-only
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

Y_DOC_PATH = REPO_ROOT / "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_DASHBOARD_PREVIEW_ADAPTER_INTEGRATION_AUTHORIZATION_PLAN_V0_8_1_Y.md"
Y_SCRIPT_PATH = REPO_ROOT / "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_integration_authorization_plan_v0_8_1_y.py"

FIXTURE_PATH = REPO_ROOT / "fixtures/local_mock_data/hermes_openclaw_local_mock_messages_v0_8_1.json"
P_LOADER_PATH = REPO_ROOT / "scripts/load_local_mock_fixture_preview_v0_8_1.py"

M_DOC_PATH = REPO_ROOT / "docs/HERMES_OPENCLAW_LOCAL_MOCK_DATA_FIXTURE_JSON_ARTIFACT_VALIDATION_V0_8_1_M.md"
M_SCRIPT_PATH = REPO_ROOT / "scripts/check_hermes_openclaw_local_mock_data_fixture_json_artifact_validation_v0_8_1_m.py"

N_DOC_PATH = REPO_ROOT / "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_PLAN_V0_8_1_N.md"
N_SCRIPT_PATH = REPO_ROOT / "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_plan_v0_8_1_n.py"

O_DOC_PATH = REPO_ROOT / "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_IMPLEMENTATION_AUTHORIZATION_PLAN_V0_8_1_O.md"
O_SCRIPT_PATH = REPO_ROOT / "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_implementation_authorization_plan_v0_8_1_o.py"

Q_DOC_PATH = REPO_ROOT / "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_VALIDATION_PLAN_V0_8_1_Q.md"
Q_SCRIPT_PATH = REPO_ROOT / "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_validation_plan_v0_8_1_q.py"

R_SCRIPT_PATH = REPO_ROOT / "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_runtime_check_v0_8_1_r.py"

S_DOC_PATH = REPO_ROOT / "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_DASHBOARD_INTEGRATION_BOUNDARY_PLAN_V0_8_1_S.md"
S_SCRIPT_PATH = REPO_ROOT / "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_dashboard_integration_boundary_plan_v0_8_1_s.py"

T_DOC_PATH = REPO_ROOT / "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_DASHBOARD_INTEGRATION_AUTHORIZATION_PLAN_V0_8_1_T.md"
T_SCRIPT_PATH = REPO_ROOT / "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_dashboard_integration_authorization_plan_v0_8_1_t.py"

U_DOC_PATH = REPO_ROOT / "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_DASHBOARD_PREVIEW_INTEGRATION_IMPLEMENTATION_PLAN_V0_8_1_U.md"
U_SCRIPT_PATH = REPO_ROOT / "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_dashboard_preview_integration_implementation_plan_v0_8_1_u.py"

V_ADAPTER_PATH = REPO_ROOT / "scripts/local_mock_fixture_dashboard_preview_adapter_v0_8_1.py"
V_READINESS_PATH = REPO_ROOT / "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_v0_8_1_v.py"

W_SCRIPT_PATH = REPO_ROOT / "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_runtime_check_v0_8_1_w.py"

X_DOC_PATH = REPO_ROOT / "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_DASHBOARD_PREVIEW_ADAPTER_INTEGRATION_BOUNDARY_PLAN_V0_8_1_X.md"
X_SCRIPT_PATH = REPO_ROOT / "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_integration_boundary_plan_v0_8_1_x.py"

EXPECTED_BASE_HEAD = "be4de0a902328efdb81ecf737037d3951b060b8e"

EXACT_AUTHORIZATION_PHRASE = (
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
# [A/B] Y authorization plan doc + readiness script exist
# ---------------------------------------------------------------------------
print("[A] Y doc exists")
check("A. Y doc exists", Y_DOC_PATH.exists())
if not Y_DOC_PATH.exists():
    print("\nXX Y authorization plan doc 不存在，無法繼續")
    sys.exit(1)

print("[B] Y readiness script path is correct")
check("B. Y readiness script exists at expected path", Y_SCRIPT_PATH.exists())

doc = Y_DOC_PATH.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# [C-O] L/M/N/O/P/Q/R/S/T/U/V/W/X artifacts exist and are tracked
# ---------------------------------------------------------------------------
print("[C] L fixture JSON exists and is tracked")
check("C. L fixture JSON exists", FIXTURE_PATH.exists())
check(
    "C. L fixture JSON is tracked",
    git_tracked("fixtures/local_mock_data/hermes_openclaw_local_mock_messages_v0_8_1.json"),
)

print("[D] M validation doc/script exist and are tracked")
check("D. M validation doc exists", M_DOC_PATH.exists())
check(
    "D. M validation doc is tracked",
    git_tracked("docs/HERMES_OPENCLAW_LOCAL_MOCK_DATA_FIXTURE_JSON_ARTIFACT_VALIDATION_V0_8_1_M.md"),
)
check("D. M validation script exists", M_SCRIPT_PATH.exists())
check(
    "D. M validation script is tracked",
    git_tracked("scripts/check_hermes_openclaw_local_mock_data_fixture_json_artifact_validation_v0_8_1_m.py"),
)

print("[E] N plan doc/script exist and are tracked")
check("E. N plan doc exists", N_DOC_PATH.exists())
check(
    "E. N plan doc is tracked",
    git_tracked("docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_PLAN_V0_8_1_N.md"),
)
check("E. N readiness script exists", N_SCRIPT_PATH.exists())
check(
    "E. N readiness script is tracked",
    git_tracked("scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_plan_v0_8_1_n.py"),
)

print("[F] O authorization doc/script exist and are tracked")
check("F. O authorization doc exists", O_DOC_PATH.exists())
check(
    "F. O authorization doc is tracked",
    git_tracked(
        "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_IMPLEMENTATION_AUTHORIZATION_PLAN_V0_8_1_O.md"
    ),
)
check("F. O readiness script exists", O_SCRIPT_PATH.exists())
check(
    "F. O readiness script is tracked",
    git_tracked(
        "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_implementation_authorization_plan_v0_8_1_o.py"
    ),
)

print("[G] P loader exists and is tracked")
check("G. P loader exists", P_LOADER_PATH.exists())
check("G. P loader is tracked", git_tracked("scripts/load_local_mock_fixture_preview_v0_8_1.py"))

print("[H] Q validation doc/script exist and are tracked")
check("H. Q validation doc exists", Q_DOC_PATH.exists())
check(
    "H. Q validation doc is tracked",
    git_tracked("docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_VALIDATION_PLAN_V0_8_1_Q.md"),
)
check("H. Q readiness script exists", Q_SCRIPT_PATH.exists())
check(
    "H. Q readiness script is tracked",
    git_tracked("scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_validation_plan_v0_8_1_q.py"),
)

print("[I] R runtime check script exists and is tracked")
check("I. R runtime check script exists", R_SCRIPT_PATH.exists())
check(
    "I. R runtime check script is tracked",
    git_tracked("scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_runtime_check_v0_8_1_r.py"),
)

print("[J] S boundary doc/script exist and are tracked")
check("J. S boundary doc exists", S_DOC_PATH.exists())
check(
    "J. S boundary doc is tracked",
    git_tracked(
        "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_DASHBOARD_INTEGRATION_BOUNDARY_PLAN_V0_8_1_S.md"
    ),
)
check("J. S readiness script exists", S_SCRIPT_PATH.exists())
check(
    "J. S readiness script is tracked",
    git_tracked(
        "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_dashboard_integration_boundary_plan_v0_8_1_s.py"
    ),
)

print("[K] T authorization doc/script exist and are tracked")
check("K. T authorization doc exists", T_DOC_PATH.exists())
check(
    "K. T authorization doc is tracked",
    git_tracked(
        "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_DASHBOARD_INTEGRATION_AUTHORIZATION_PLAN_V0_8_1_T.md"
    ),
)
check("K. T readiness script exists", T_SCRIPT_PATH.exists())
check(
    "K. T readiness script is tracked",
    git_tracked(
        "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_dashboard_integration_authorization_plan_v0_8_1_t.py"
    ),
)

print("[L] U implementation plan doc/script exist and are tracked")
check("L. U implementation plan doc exists", U_DOC_PATH.exists())
check(
    "L. U implementation plan doc is tracked",
    git_tracked(
        "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_DASHBOARD_PREVIEW_INTEGRATION_IMPLEMENTATION_PLAN_V0_8_1_U.md"
    ),
)
check("L. U readiness script exists", U_SCRIPT_PATH.exists())
check(
    "L. U readiness script is tracked",
    git_tracked(
        "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_dashboard_preview_integration_implementation_plan_v0_8_1_u.py"
    ),
)

print("[M] V adapter/readiness script exist and are tracked")
check("M. V adapter exists", V_ADAPTER_PATH.exists())
check(
    "M. V adapter is tracked",
    git_tracked("scripts/local_mock_fixture_dashboard_preview_adapter_v0_8_1.py"),
)
check("M. V readiness script exists", V_READINESS_PATH.exists())
check(
    "M. V readiness script is tracked",
    git_tracked("scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_v0_8_1_v.py"),
)

print("[N] W runtime check script exists and is tracked")
check("N. W runtime check script exists", W_SCRIPT_PATH.exists())
check(
    "N. W runtime check script is tracked",
    git_tracked("scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_runtime_check_v0_8_1_w.py"),
)

print("[O] X boundary doc/script exist and are tracked")
check("O. X boundary doc exists", X_DOC_PATH.exists())
check(
    "O. X boundary doc is tracked",
    git_tracked(
        "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_DASHBOARD_PREVIEW_ADAPTER_INTEGRATION_BOUNDARY_PLAN_V0_8_1_X.md"
    ),
)
check("O. X readiness script exists", X_SCRIPT_PATH.exists())
check(
    "O. X readiness script is tracked",
    git_tracked(
        "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_integration_boundary_plan_v0_8_1_x.py"
    ),
)

# ---------------------------------------------------------------------------
# [P] current HEAD contains EXPECTED_BASE_HEAD in git history
# ---------------------------------------------------------------------------
print("[P] current HEAD contains EXPECTED_BASE_HEAD in git history")
ancestor_check = subprocess.run(
    ["git", "-C", str(REPO_ROOT), "merge-base", "--is-ancestor", EXPECTED_BASE_HEAD, "HEAD"],
    capture_output=True,
    text=True,
)
check(
    f"P. HEAD contains {EXPECTED_BASE_HEAD} in git history",
    ancestor_check.returncode == 0,
)

# ---------------------------------------------------------------------------
# [Q-BB] required doc content (title, base HEAD, positioning, dependency on X,
#        exact authorization phrase, non-authorization statements,
#        non-authorizing phrase list, future allowed scope, forbidden
#        actions, preflight gate, rollback boundary, next step)
# ---------------------------------------------------------------------------
print("[Q] Y doc contains v0.8.1-Y title")
check(
    "Q. Y doc contains v0.8.1-Y title",
    "v0.8.1-Y" in doc and "Dashboard Preview Adapter Integration Authorization Plan" in doc,
)

print("[R] Y doc contains base HEAD")
check("R. Y doc contains base HEAD", f"Base HEAD / origin/master:\n{EXPECTED_BASE_HEAD}" in doc)

print("[S] Y doc states authorization-plan-only positioning")
check("S. Y doc states authorization-plan-only positioning", "v0.8.1-Y is an authorization plan only." in doc)

print("[T] Y doc states Y does not modify Dashboard")
check("T. Y doc states Y does not modify Dashboard", "v0.8.1-Y does not modify Dashboard." in doc)

print("[U] Y doc states Y does not modify adapter")
check("U. Y doc states Y does not modify adapter", "v0.8.1-Y does not modify adapter." in doc)

print("[V] Y doc states Y does not modify loader")
check("V. Y doc states Y does not modify loader", "v0.8.1-Y does not modify loader." in doc)

print("[W] Y doc states dependency on X")
check("W. Y doc states dependency on X", "v0.8.1-Y depends on v0.8.1-X." in doc)

print("[X] Y doc contains the exact explicit Owner authorization phrase exactly once")
check(
    "X. Y doc contains the exact explicit Owner authorization phrase exactly once",
    doc.count(EXACT_AUTHORIZATION_PHRASE) == 1,
)

print("[Y] Y doc states only the exact phrase may authorize the future next step")
check(
    "Y. Y doc states only the exact phrase may authorize the future next step",
    "Only the exact explicit Owner authorization phrase above may authorize the future Dashboard preview\nadapter integration next step."
    in doc,
)

print("[Z] Y doc states paraphrases do not authorize")
check("Z. Y doc states paraphrases do not authorize", "Paraphrases do not authorize future implementation planning." in doc)

print("[AA] Y doc states general approval does not authorize")
check(
    "AA. Y doc states general approval does not authorize",
    "General approval does not authorize future implementation planning." in doc,
)

print("[AB] Y doc states readiness PASS does not authorize")
check(
    "AB. Y doc states readiness PASS does not authorize",
    "Readiness PASS does not authorize future implementation planning." in doc,
)

print("[AC] Y doc states Owner Review PASS does not authorize")
check(
    "AC. Y doc states Owner Review PASS does not authorize",
    "Owner Review PASS does not authorize future implementation planning." in doc,
)

print("[AD] Y doc states commit approval does not authorize")
check(
    "AD. Y doc states commit approval does not authorize",
    "Commit approval does not authorize future implementation planning." in doc,
)

print("[AE] Y doc states push approval does not authorize")
check(
    "AE. Y doc states push approval does not authorize",
    "Push approval does not authorize future implementation planning." in doc,
)

print("[AF] Y doc lists non-authorizing phrases")
NON_AUTHORIZING_PHRASES = [
    "可以接 Dashboard",
    "開始接 Dashboard",
    "可以實作 Dashboard",
    "可以改 Dashboard",
    "可以進入下一步",
    "開始 v0.8.1-Z",
    "Dashboard 可以用了",
    "Owner Review passed",
    "readiness passed",
    "push 後繼續",
    "照原計畫做",
    "可以繼續",
    "批准 Dashboard integration",
    "批准實作",
]
check(
    "AF. Y doc lists non-authorizing phrases",
    all(phrase in doc for phrase in NON_AUTHORIZING_PHRASES),
)

print("[AG] Y doc defines future allowed scope")
check(
    "AG. Y doc defines future allowed scope",
    "## 7. Future allowed scope, plan-only" in doc
    and "Future separately authorized next step may only plan or implement a read-only Dashboard integration"
    in doc,
)

print("[AH] Y doc allows build_dashboard_preview_model()")
check("AH. Y doc allows build_dashboard_preview_model()", "build_dashboard_preview_model()" in doc)

print("[AI] Y doc optionally allows build_dashboard_preview_rows()")
check(
    "AI. Y doc optionally allows build_dashboard_preview_rows()",
    "Optional display-only use:\nbuild_dashboard_preview_rows()" in doc,
)

print("[AJ] Y doc requires is_mock/local_only/read_only preservation")
check(
    "AJ. Y doc requires is_mock/local_only/read_only preservation",
    "is_mock = True" in doc and "local_only = True" in doc and "read_only = True" in doc,
)

print("[AK] Y doc requires execution_permission/dispatch_permission/external_side_effects_permission False")
check(
    "AK. Y doc requires execution_permission/dispatch_permission/external_side_effects_permission False",
    "execution_permission = False" in doc
    and "dispatch_permission = False" in doc
    and "external_side_effects_permission = False" in doc,
)

print("[AL] Y doc requires disabled runtime badges")
check(
    "AL. Y doc requires disabled runtime badges",
    "DISPATCH OFF" in doc
    and "WORKER OFF" in doc
    and "OPENCLAW NOT CONNECTED" in doc
    and "HERMES NOT CONNECTED" in doc
    and "GOOGLE SHEETS DISABLED" in doc,
)

print("[AM] Y doc forbids Dashboard calling load_local_mock_fixture_preview()")
check(
    "AM. Y doc forbids Dashboard calling load_local_mock_fixture_preview()",
    "Do not call load_local_mock_fixture_preview() from Dashboard." in doc,
)

print("[AN] Y doc forbids Dashboard calling validate_local_mock_fixture_preview_object()")
check(
    "AN. Y doc forbids Dashboard calling validate_local_mock_fixture_preview_object()",
    "Do not call validate_local_mock_fixture_preview_object() from Dashboard." in doc,
)

print("[AO] Y doc forbids Dashboard reading fixture JSON directly")
check(
    "AO. Y doc forbids Dashboard reading fixture JSON directly",
    "Do not read fixture JSON directly from Dashboard." in doc,
)

print("[AP] Y doc forbids real queue DB")
check("AP. Y doc forbids real queue DB", "Do not read real queue DB." in doc and "Do not write queue data." in doc)

print("[AQ] Y doc forbids QueueStore")
check("AQ. Y doc forbids QueueStore", "Do not call QueueStore." in doc)

print("[AR] Y doc forbids POST/network")
check("AR. Y doc forbids POST/network", "Do not POST." in doc and "Do not make network calls." in doc)

print("[AS] Y doc forbids Worker/OpenClaw/Hermes/Google Sheets")
check(
    "AS. Y doc forbids Worker/OpenClaw/Hermes/Google Sheets",
    "Do not start Worker." in doc
    and "Do not call OpenClaw." in doc
    and "Do not activate Hermes." in doc
    and "Do not read Google Sheets." in doc
    and "Do not write Google Sheets." in doc,
)

print("[AT] Y doc forbids secrets/.env/webhook/connector")
check(
    "AT. Y doc forbids secrets/.env/webhook/connector",
    "Do not read secrets." in doc
    and "Do not create .env." in doc
    and "Do not create webhook." in doc
    and "Do not create connector." in doc,
)

print("[AU] Y doc forbids production/shared DB/Remote Blackboard API runtime")
check(
    "AU. Y doc forbids production/shared DB/Remote Blackboard API runtime",
    "Do not create production DB." in doc
    and "Do not create shared DB." in doc
    and "Do not create Remote Blackboard API runtime." in doc,
)

print("[AV] Y doc forbids execution/dispatch/external action controls")
check(
    "AV. Y doc forbids execution/dispatch/external action controls",
    "Do not expose execution controls." in doc
    and "Do not expose dispatch controls." in doc
    and "Do not expose external action controls." in doc,
)

print("[AW] Y doc forbids action_url/post_url/webhook_url/endpoint_url/execute_url/dispatch_url")
check(
    "AW. Y doc forbids action_url/post_url/webhook_url/endpoint_url/execute_url/dispatch_url",
    "Do not expose action_url, post_url, webhook_url, endpoint_url, execute_url, dispatch_url." in doc,
)

print("[AX] Y doc defines future implementation preflight gate")
check(
    "AX. Y doc defines future implementation preflight gate",
    "## 9. Future implementation preflight gate, plan-only" in doc
    and "The exact explicit Owner authorization phrase must be present." in doc,
)

print("[AY] Y doc defines rollback boundary")
check(
    "AY. Y doc defines rollback boundary",
    "## 10. Rollback boundary, plan-only" in doc
    and "Rollback must not modify Y authorization plan." in doc,
)

print("[AZ] Y doc says v0.8.1-Z is recommended next step")
check(
    "AZ. Y doc says v0.8.1-Z is recommended next step",
    "Recommended next step:\nv0.8.1-Z — Dashboard Preview Adapter Integration Implementation Plan" in doc,
)

print("[BA] Y doc says v0.8.1-Z is not started")
check("BA. Y doc says v0.8.1-Z is not started", "v0.8.1-Z is not started by v0.8.1-Y." in doc)

print("[BB] Y doc says v0.8.1-Z requires the exact phrase")
check(
    "BB. Y doc says v0.8.1-Z requires the exact phrase",
    "v0.8.1-Z requires the exact explicit Owner authorization phrase defined in v0.8.1-Y." in doc,
)

# ---------------------------------------------------------------------------
# [BC] no tracked working-tree modifications
# ---------------------------------------------------------------------------
print("[BC] no tracked working-tree modifications")
diff_out = subprocess.run(
    ["git", "-C", str(REPO_ROOT), "diff", "--name-only"],
    capture_output=True,
    text=True,
)
tracked_changes = [l for l in diff_out.stdout.splitlines() if l.strip()]
check(f"BC. no tracked working-tree modifications（found {tracked_changes}）" if tracked_changes else "BC. no tracked working-tree modifications", not tracked_changes)

# ---------------------------------------------------------------------------
# [BD] no Dashboard/app/templates/static files changed (staged or unstaged)
# ---------------------------------------------------------------------------
print("[BD] no Dashboard/app/templates/static files changed")
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
    f"BD. no Dashboard/app/templates/static files changed（found {dashboard_changes}）"
    if dashboard_changes
    else "BD. no Dashboard/app/templates/static files changed",
    not dashboard_changes,
)

# ---------------------------------------------------------------------------
# [BE] no extra untracked files beyond allowed Y files and existing patches/
# ---------------------------------------------------------------------------
print("[BE] no extra untracked files beyond allowed Y files and patches/")
others_out = subprocess.run(
    ["git", "-C", str(REPO_ROOT), "ls-files", "--others", "--exclude-standard"],
    capture_output=True,
    text=True,
)
ALLOWED_UNTRACKED = {
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_DASHBOARD_PREVIEW_ADAPTER_INTEGRATION_AUTHORIZATION_PLAN_V0_8_1_Y.md",
    "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_integration_authorization_plan_v0_8_1_y.py",
}
untracked = [l for l in others_out.stdout.splitlines() if l.strip()]
unexpected = [u for u in untracked if u not in ALLOWED_UNTRACKED and not u.startswith("patches/")]
check(
    f"BE. no unexpected untracked files（found {unexpected}）" if unexpected else "BE. no unexpected untracked files",
    not unexpected,
)

# ---------------------------------------------------------------------------
# 結果
# ---------------------------------------------------------------------------
total = len(PASS) + len(FAIL)
print(f"\n合計：{len(PASS)}/{total} 通過")
if FAIL:
    print(f"\nXX v0.8.1-Y readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print("PASS: v0.8.1-Y dashboard preview adapter integration authorization plan")
    sys.exit(0)
