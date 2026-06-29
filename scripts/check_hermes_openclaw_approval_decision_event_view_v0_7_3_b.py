"""v0.7.3-B readiness check: Read-only Approval Event View.

Verifies the read-only Owner approval decision event view: the view doc and the
pure helper exist, the task_detail / reviews surfaces render the "Owner 決策紀錄"
markers and the read-only indicator, main.py attaches the view as read-only
context, and the required markers / decision-event separation reminders are
present — and that the display surfaces (helper + doc + templates + css + test)
contain no unsafe "enabled / connected / execution-granting / approve-triggers /
decision-event-dispatches" claim and no secret.

This script only reads the F-3-B view surfaces and wiring. It does NOT read .env,
credentials, tokens, or secrets, makes no network call, imports no app logic (no
app.main, no QueueStore), starts no Worker, and calls no OpenClaw / Hermes /
Google Sheets.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
PASS = []
FAIL = []

HELPER_PATH = ROOT / "app" / "approval_decision_events_v0_7.py"
DOC_PATH = ROOT / "docs" / "HERMES_OPENCLAW_APPROVAL_DECISION_EVENT_VIEW_V0_7_3_B.md"
MAIN_PATH = ROOT / "app" / "main.py"
TASK_DETAIL_PATH = ROOT / "templates" / "task_detail.html"
REVIEWS_PATH = ROOT / "templates" / "reviews.html"
CSS_PATH = ROOT / "static" / "dashboard.css"
TEST_PATH = ROOT / "scripts" / "test_approval_decision_event_view_readonly_v0_7_3_b.py"


def ok(label):
    PASS.append(label)
    print(f"  ok : {label}")


def xx(label):
    FAIL.append(label)
    print(f"  XX : {label}")


# ---------------------------------------------------------------------------
# [1] 必要檔案存在
# ---------------------------------------------------------------------------
print("[1] v0.7.3-B 必要檔案存在")
required_files = {
    "app/approval_decision_events_v0_7.py": HELPER_PATH,
    "docs/HERMES_OPENCLAW_APPROVAL_DECISION_EVENT_VIEW_V0_7_3_B.md": DOC_PATH,
    "app/main.py": MAIN_PATH,
    "templates/task_detail.html": TASK_DETAIL_PATH,
    "templates/reviews.html": REVIEWS_PATH,
    "static/dashboard.css": CSS_PATH,
    "scripts/test_approval_decision_event_view_readonly_v0_7_3_b.py": TEST_PATH,
}
missing = False
for label, path in required_files.items():
    if path.exists():
        ok(f"{label} 存在")
    else:
        xx(f"{label} 存在")
        missing = True
if missing:
    print("\nXX v0.7.3-B 必要檔案缺失，無法繼續")
    sys.exit(1)

helper_src = HELPER_PATH.read_text(encoding="utf-8")
doc_src = DOC_PATH.read_text(encoding="utf-8")
main_src = MAIN_PATH.read_text(encoding="utf-8")
detail_src = TASK_DETAIL_PATH.read_text(encoding="utf-8")
reviews_src = REVIEWS_PATH.read_text(encoding="utf-8")
css_src = CSS_PATH.read_text(encoding="utf-8")
test_src = TEST_PATH.read_text(encoding="utf-8")

# 正向掃描：doc + helper + templates + main wiring + test。
positive = "\n".join([doc_src, helper_src, detail_src, reviews_src, main_src, test_src])
# 禁止字掃描：只掃顯示面 + helper + doc + test（不掃 main.py 既有 worker/callback 程式碼）。
display_only = "\n".join([helper_src, doc_src, detail_src, reviews_src, css_src, test_src])

# ---------------------------------------------------------------------------
# [2] 必須包含的 markers
# ---------------------------------------------------------------------------
print("[2] 必須包含的 markers")
REQUIRED = [
    "v0.7.3-B",
    "Read-only Approval Event View",
    "Approval Decision Event Plan",
    "v0.7.3-A",
    "e3167601378739dae3ecc7d7fbd0dc5fd86f087d",
    "docs: plan approval decision events",
    "Owner 決策紀錄",
    "Approval Decision Events",
    "尚無 Owner 決策事件紀錄",
    "v0.7.3-B 只讀顯示",
    "v0.7.3-C 才會規劃 local recorder",
    "approve is not execute",
    "Owner decision event is not Worker dispatch",
    "Owner approval does not automatically imply Worker execution",
    "Decision and execution dispatch remain separate",
    "Approval readiness is not execution permission",
    "execution_permission = False",
    "dispatch_allowed = False",
    "No QueueStore runtime behavior changes",
    "No approval wiring changes",
    "No Worker execution",
    "No OpenClaw call",
    "No Hermes call",
    "No Google Sheets write",
    "No external side effects",
    "No --apply",
    "No demo task cleanup",
    "No approve/reject/cancel/retry/archive clicks",
]
for token in REQUIRED:
    ok(f"含「{token}」") if token in positive else xx(f"含「{token}」")

# ---------------------------------------------------------------------------
# [3] task_detail.html 含 Owner 決策紀錄 markers
# ---------------------------------------------------------------------------
print("[3] task_detail.html 含 Owner 決策紀錄 markers")
for token in (
    "Owner 決策紀錄",
    "Approval Decision Events",
    "只讀顯示",
    "approve is not execute",
    "Owner decision event is not Worker dispatch",
    "execution_permission = False",
    "dispatch_allowed = False",
):
    ok(f"task_detail 含「{token}」") if token in detail_src else xx(f"task_detail 含「{token}」")

# ---------------------------------------------------------------------------
# [4] reviews.html 含 decision event indicator markers
# ---------------------------------------------------------------------------
print("[4] reviews.html 含 decision event indicator markers")
for token in ("決策紀錄", "只讀", "未派工", "dispatch_allowed = False"):
    ok(f"reviews 含「{token}」") if token in reviews_src else xx(f"reviews 含「{token}」")

# ---------------------------------------------------------------------------
# [5] helper / main.py read-only wiring
# ---------------------------------------------------------------------------
print("[5] read-only view wiring")
ok("helper 提供 derive_approval_decision_event_view") if re.search(
    r"def\s+derive_approval_decision_event_view\s*\(", helper_src
) else xx("helper 提供 derive_approval_decision_event_view")
ok("main.py import derive_approval_decision_event_view") if re.search(
    r"from app\.approval_decision_events_v0_7 import derive_approval_decision_event_view", main_src
) else xx("main.py import derive_approval_decision_event_view")
ok("main.py 在 context 附加 decision_events") if re.search(
    r'"decision_events"\s*:\s*derive_approval_decision_event_view\(', main_src
) else xx("main.py 在 context 附加 decision_events")

# helper 不得 import app.main / QueueStore（只比對 import 陳述句）。
for token in ("app.main", "app.queue_store", "app.worker"):
    mod = re.escape(token)
    found = bool(
        re.search(rf"^\s*import\s+{mod}\b", helper_src, re.MULTILINE)
        or re.search(rf"^\s*from\s+{mod}\b", helper_src, re.MULTILINE)
    )
    xx(f"helper 不得 import「{token}」") if found else ok(f"helper 不 import「{token}」")

# helper 固定 execution_permission/dispatch_allowed False。
ok("helper 設定 execution_permission False") if re.search(
    r'"execution_permission"\s*:\s*False', helper_src
) else xx("helper 設定 execution_permission False")
ok("helper 設定 dispatch_allowed False") if re.search(
    r'"dispatch_allowed"\s*:\s*False', helper_src
) else xx("helper 設定 dispatch_allowed False")

# ---------------------------------------------------------------------------
# [6] 禁止包含的不安全聲明 / 機密（只掃顯示面 + helper + doc + test）
# ---------------------------------------------------------------------------
print("[6] 禁止包含的不安全聲明 / 機密")
FORBIDDEN_SUBSTR = [
    "GOOGLE_SHEETS_ENABLED=true",
    "Worker enabled",
    "OpenClaw connected",
    "Hermes connected",
    "Google Sheets live write enabled",
    "execution_permission = True",
    "dispatch_allowed = True",
    "Owner approval triggers Worker execution",
    "approve triggers dispatch",
    "approve calls OpenClaw",
    "approve calls Hermes",
    "approve writes Google Sheets",
    "decision event dispatches Worker",
]
for token in FORBIDDEN_SUBSTR:
    xx(f"顯示面不得含「{token}」") if token in display_only else ok(f"顯示面無「{token}」")

FORBIDDEN_PATTERNS = [
    (r"spreadsheets/d/[A-Za-z0-9_-]{20,}", "real spreadsheet URL"),
    (r'"?refresh_token"?\s*[:=]\s*"[^"]+"', "refresh token value"),
    (r'"?client_secret"?\s*[:=]\s*"[^"]+"', "client secret value"),
    (r"-----BEGIN[ A-Z]*PRIVATE KEY-----", "private key value"),
]
for pat, label in FORBIDDEN_PATTERNS:
    found = bool(re.search(pat, display_only, re.IGNORECASE))
    ok(f"顯示面無「{label}」") if not found else xx(f"顯示面不得含「{label}」")

# ---------------------------------------------------------------------------
# [7] approval route 行為未被破壞（POST routes 仍存在）
# ---------------------------------------------------------------------------
print("[7] approval route 行為未被破壞")
for route in (
    '"/dashboard/tasks/{task_id}/approve"',
    '"/dashboard/tasks/{task_id}/reject"',
    '"/dashboard/tasks/{task_id}/cancel"',
    '"/dashboard/tasks/{task_id}/retry"',
    '"/dashboard/tasks/{task_id}/archive"',
):
    ok(f"main.py 保留 route {route}") if route in main_src else xx(f"main.py 保留 route {route}")

# ---------------------------------------------------------------------------
# 結果
# ---------------------------------------------------------------------------
total = len(PASS) + len(FAIL)
print(f"\n合計：{len(PASS)}/{total} 通過")
if FAIL:
    print(f"\nXX v0.7.3-B readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print("\nv0.7.3-B Read-only Approval Event View readiness: ALL PASS")
    sys.exit(0)
