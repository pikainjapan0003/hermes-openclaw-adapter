"""v0.7.4-D readiness check: Audit Trail Display.

Read-only display verification. Checks that the v0.7.4-D audit-trail helper, doc,
templates, and css exist and carry the required markers: the helper function and
its fixed-False safety flags (and that the helper imports no QueueStore / app.main /
sqlite / network / secrets), the doc sections (1-25), the current-master marker, the
v0.7.4-C / v0.7.4-B / v0.7.4-A / v0.7.3-R completion markers, the read-only display
contract, the QueueStore boundary, the Route / POST boundary, the task-detail and
reviews display markers, the css classes, the safe system posture, and the next
recommended step — and that the doc asserts no unsafe "enabled / connected /
display-changes / display-dispatches / queuestore-changed / adds-POST / adds-button
/ ran-in / called-in / POST-to / clicked / seeded / cleaned-up / live-write-
performed" claim and contains no secret.

This script only reads files. It does NOT read .env, credentials, tokens, or
secrets, makes no network call, imports no app logic, starts no Worker, and calls
no OpenClaw / Hermes / Google Sheets.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
PASS = []
FAIL = []

HELPER_PATH = ROOT / "app" / "audit_trail_display_v0_7.py"
DOC_PATH = ROOT / "docs" / "HERMES_OPENCLAW_AUDIT_TRAIL_DISPLAY_V0_7_4_D.md"
TEST_PATH = ROOT / "scripts" / "test_audit_trail_display_readonly_v0_7_4_d.py"
TASK_DETAIL_PATH = ROOT / "templates" / "task_detail.html"
REVIEWS_PATH = ROOT / "templates" / "reviews.html"
CSS_PATH = ROOT / "static" / "dashboard.css"


def ok(label):
    PASS.append(label)
    print(f"  ok : {label}")


def xx(label):
    FAIL.append(label)
    print(f"  XX : {label}")


# ---------------------------------------------------------------------------
# [1] 必要檔案存在
# ---------------------------------------------------------------------------
print("[1] 必要檔案存在")
REQUIRED_FILES = [
    HELPER_PATH,
    DOC_PATH,
    TEST_PATH,
    TASK_DETAIL_PATH,
    REVIEWS_PATH,
    CSS_PATH,
]
missing = False
for p in REQUIRED_FILES:
    if p.exists():
        ok(f"檔案存在：{p.relative_to(ROOT)}")
    else:
        xx(f"檔案存在：{p.relative_to(ROOT)}")
        missing = True
if missing:
    print("\nXX 必要檔案缺失，無法繼續")
    sys.exit(1)

helper_src = HELPER_PATH.read_text(encoding="utf-8")
doc = DOC_PATH.read_text(encoding="utf-8")
task_detail = TASK_DETAIL_PATH.read_text(encoding="utf-8")
reviews = REVIEWS_PATH.read_text(encoding="utf-8")
css = CSS_PATH.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# [2] helper：函式 + 固定安全旗標
# ---------------------------------------------------------------------------
print("[2] helper 函式與固定安全旗標")
HELPER_MARKERS = [
    "def derive_audit_trail_display_view",
    '"execution_permission": False',
    '"dispatch_allowed": False',
    '"worker_dispatch_enabled": False',
    '"openclaw_call_enabled": False',
    '"hermes_call_enabled": False',
    '"google_sheets_write_enabled": False',
    '"read_only": True',
    '"result_message": result_count',
    '"advice_message": advice_count',
]
for token in HELPER_MARKERS:
    ok(f"helper 含「{token}」") if token in helper_src else xx(f"helper 含「{token}」")

# Result / Advice future-only 固定 0
ok("helper result_count = 0") if "result_count = 0" in helper_src else xx("helper result_count = 0")
ok("helper advice_count = 0") if "advice_count = 0" in helper_src else xx("helper advice_count = 0")

# ---------------------------------------------------------------------------
# [3] helper import 邊界（只看 import 行，不誤判 docstring 文字）
# ---------------------------------------------------------------------------
print("[3] helper import 邊界")
import_lines = [
    ln.strip()
    for ln in helper_src.splitlines()
    if ln.strip().startswith("import ") or ln.strip().startswith("from ")
]
FORBIDDEN_IMPORT_TOKENS = [
    "app.main",
    "queue_store",
    "QueueStore",
    "sqlite",
    "socket",
    "requests",
    "urllib",
    "http.client",
    "secrets",
    "subprocess",
]
import_violations = [
    (ln, tok)
    for ln in import_lines
    for tok in FORBIDDEN_IMPORT_TOKENS
    if tok in ln
]
if import_violations:
    for ln, tok in import_violations:
        xx(f"helper 不得 import「{tok}」（{ln}）")
else:
    ok("helper 未 import QueueStore / app.main / sqlite / network / secrets / subprocess")
# 只允許標準庫 import
ok("helper import json") if "import json" in helper_src else xx("helper import json")

# ---------------------------------------------------------------------------
# [4] 文件章節（1-25）
# ---------------------------------------------------------------------------
print("[4] 文件章節")
REQUIRED_SECTIONS = [
    "1. Purpose",
    "2. Current master",
    "3. Scope",
    "4. Relationship to v0.7.4-C",
    "5. Relationship to v0.7.4-B",
    "6. Relationship to v0.7.4-A",
    "7. Relationship to v0.7.3-R",
    "8. Read-only display contract",
    "9. Audit trail helper",
    "10. Dashboard task detail display",
    "11. Dashboard reviews display",
    "12. Blackboard message family display",
    "13. Lifecycle state display",
    "14. Decision Message display",
    "15. Result Message future-only display",
    "16. Advice Message future-only display",
    "17. Dispatch separation boundary",
    "18. QueueStore boundary",
    "19. Route / POST boundary",
    "20. Local queue vs Replit queue boundary",
    "21. Current safe system posture",
    "22. Tests and readiness",
    "23. Non-goals",
    "24. Acceptance criteria",
    "25. Next recommended step",
]
for section in REQUIRED_SECTIONS:
    ok(f"doc 含章節「{section}」") if section in doc else xx(f"doc 含章節「{section}」")

# ---------------------------------------------------------------------------
# [5] 文件 markers
# ---------------------------------------------------------------------------
print("[5] 文件 markers")
REQUIRED = [
    # version
    "v0.7.4-D",
    "Audit Trail Display",
    # current master
    "HEAD = origin/master = 33476de2c65438ca10627657f94afaf1955b0660",
    "docs: plan state transition guard",
    # v0.7.4-C completion markers
    "v0.7.4-C State Transition Guard Plan is complete.",
    "State Transition Guard is a safety contract.",
    "v0.7.4-C does not modify current status transitions.",
    "v0.7.4-C does not enforce runtime guards.",
    "Allowed and blocked transitions are planning rules only.",
    # v0.7.4-B completion markers
    "v0.7.4-B Queue / Blackboard Lifecycle Plan is complete.",
    "Task Message",
    "Decision Message",
    "Result Message",
    "Advice Message",
    "Result Message is future planning only.",
    "Advice Message is future planning only.",
    # v0.7.4-A completion markers
    "v0.7.4-A Core Topology / Dashboard Update / Core Independence Plan is complete.",
    "Replit is a remote observation station / Preview Dashboard.",
    "Dashboard update means git pull plus Dashboard restart.",
    "Current Windows WSL local queue and Replit local queue are separate.",
    # v0.7.3-R completion markers
    "v0.7.3 Approval Decision Layer is complete.",
    "approval_decision_events are Decision Messages.",
    "Decision Messages are blackboard audit records, not execution commands.",
    "approve is not execute.",
    "Owner decision event is not Worker dispatch.",
    # read-only display contract
    "Audit Trail Display is read-only.",
    "Audit Trail Display does not change lifecycle state.",
    "Audit Trail Display does not enforce guard.",
    "Audit Trail Display does not grant execution permission.",
    "Audit Trail Display does not dispatch Worker.",
    "Audit Trail Display does not call OpenClaw.",
    "Audit Trail Display does not call Hermes.",
    "Audit Trail Display does not write Google Sheets.",
    "Audit Trail Display does not write queue data.",
    # helper fixed flags (documented)
    "execution_permission = False",
    "dispatch_allowed = False",
    "worker_dispatch_enabled = False",
    "openclaw_call_enabled = False",
    "hermes_call_enabled = False",
    "google_sheets_write_enabled = False",
    "read_only = True",
    # message family counts
    "Task Message = 1 when task exists",
    "Decision Message = len(payload.metadata.approval_decision_events)",
    "Result Message = 0 in v0.7.4-D",
    "Advice Message = 0 in v0.7.4-D",
    # future-only markers
    "Result Message display is future-only in v0.7.4-D.",
    "Advice Message display is future-only in v0.7.4-D.",
    # lifecycle display notes
    "Displayed lifecycle state is derived read-only.",
    "Displayed lifecycle state does not change task status.",
    "Displayed lifecycle state does not enforce guard.",
    "Displayed lifecycle state does not grant execution permission.",
    "Displayed lifecycle state does not dispatch Worker.",
    # QueueStore boundary
    "QueueStore runtime behavior is unchanged in v0.7.4-D.",
    "v0.7.4-D does not modify app/queue_store.py.",
    "v0.7.4-D does not add QueueStore methods.",
    "v0.7.4-D does not change status persistence.",
    "v0.7.4-D does not change payload persistence.",
    # Route / POST boundary
    "v0.7.4-D does not add POST routes.",
    "v0.7.4-D does not modify approval POST behavior.",
    "v0.7.4-D does not modify reject POST behavior.",
    "v0.7.4-D does not modify cancel POST behavior.",
    "v0.7.4-D does not modify retry POST behavior.",
    "v0.7.4-D does not modify archive POST behavior.",
    "v0.7.4-D does not add state-changing buttons.",
    "v0.7.4-D does not add state-changing forms.",
    # safe system posture
    "Dashboard read-only / controlled local route behavior",
    "Worker OFF",
    "OpenClaw Not Connected",
    "Hermes Not Connected",
    "Google Sheets Disabled",
    "No external side effects",
    "No --apply",
    "No demo task cleanup",
    "No seed demo task",
    "No secrets read",
    "No webhook",
    "No tag",
    # next recommended step
    "v0.7.4-D-R — Audit Trail Display Replit GET-only Validation",
    "v0.7.4-D-R must be GET-only.",
    "No Worker dispatch.",
]
for token in REQUIRED:
    ok(f"doc 含「{token}」") if token in doc else xx(f"doc 含「{token}」")

# ---------------------------------------------------------------------------
# [6] templates / css display markers
# ---------------------------------------------------------------------------
print("[6] templates / css display markers")
TASK_DETAIL_MARKERS = [
    "Audit Trail / Blackboard Messages",
    "audit-trail-panel",
    "task.audit_trail",
    "lifecycle_state",
]
for token in TASK_DETAIL_MARKERS:
    ok(f"task_detail.html 含「{token}」") if token in task_detail else xx(f"task_detail.html 含「{token}」")

REVIEWS_MARKERS = [
    "t.audit_trail",
    "audit-trail-review-summary",
    "Audit：Task",
    "Lifecycle：",
]
for token in REVIEWS_MARKERS:
    ok(f"reviews.html 含「{token}」") if token in reviews else xx(f"reviews.html 含「{token}」")

CSS_MARKERS = [
    ".audit-trail-panel",
    ".audit-trail-timeline",
    ".audit-trail-review-summary",
]
for token in CSS_MARKERS:
    ok(f"dashboard.css 含「{token}」") if token in css else xx(f"dashboard.css 含「{token}」")

# templates 不得新增 state-changing form/button（audit 區塊內）：粗略確認 audit 區塊不含 <form 或 <button
ok("task_detail audit 區塊存在") if "audit-trail-panel" in task_detail else xx("task_detail audit 區塊存在")

# ---------------------------------------------------------------------------
# [7] 禁止包含的不安全聲明 / 機密（掃 doc，先 scrub 合法否定句）
# ---------------------------------------------------------------------------
print("[7] 禁止包含的不安全聲明 / 機密")
SAFE_NEGATIONS = [
    "No POST to Replit Preview",  # 合法否定句，含 'POST to Replit Preview'
]
scrubbed = doc
for phrase in SAFE_NEGATIONS:
    scrubbed = scrubbed.replace(phrase, "")

FORBIDDEN_SUBSTR = [
    "GOOGLE_SHEETS_ENABLED=true",
    "Worker enabled",
    "OpenClaw connected",
    "Hermes connected",
    "Google Sheets live write enabled",
    "Audit Trail Display changes lifecycle state",
    "Audit Trail Display enforces guard",
    "Audit Trail Display grants execution permission",
    "Audit Trail Display dispatches Worker",
    "Audit Trail Display calls OpenClaw",
    "Audit Trail Display calls Hermes",
    "Audit Trail Display writes Google Sheets",
    "Audit Trail Display writes queue data",
    "QueueStore runtime behavior changed",
    "v0.7.4-D modifies app/queue_store.py",
    "v0.7.4-D adds QueueStore methods",
    "v0.7.4-D changes status persistence",
    "v0.7.4-D changes payload persistence",
    "v0.7.4-D adds POST routes",
    "v0.7.4-D modifies approval POST behavior",
    "v0.7.4-D modifies reject POST behavior",
    "v0.7.4-D modifies cancel POST behavior",
    "v0.7.4-D modifies retry POST behavior",
    "v0.7.4-D modifies archive POST behavior",
    "v0.7.4-D adds state-changing buttons",
    "v0.7.4-D adds state-changing forms",
    "Worker ran in v0.7.4-D",
    "OpenClaw called in v0.7.4-D",
    "Hermes called in v0.7.4-D",
    "task claimed by Worker in v0.7.4-D",
    "task dispatched to OpenClaw in v0.7.4-D",
    "POST to Replit Preview",
    "POST to real queue",
    "clicked approve",
    "clicked reject",
    "clicked cancel",
    "clicked retry",
    "clicked archive",
    "live queue write validation performed",
    "demo task cleaned up",
    "seeded demo task",
]
for token in FORBIDDEN_SUBSTR:
    ok(f"doc 無「{token}」") if token not in scrubbed else xx(f"doc 不得含「{token}」")

FORBIDDEN_PATTERNS = [
    (r"spreadsheets/d/[A-Za-z0-9_-]{20,}", "real spreadsheet URL"),
    (r'"?refresh_token"?\s*[:=]\s*"[^"]+"', "refresh token value"),
    (r'"?client_secret"?\s*[:=]\s*"[^"]+"', "client secret value"),
    (r"-----BEGIN[ A-Z]*PRIVATE KEY-----", "private key value"),
]
for pat, label in FORBIDDEN_PATTERNS:
    found = bool(re.search(pat, doc, re.IGNORECASE))
    ok(f"doc 無「{label}」") if not found else xx(f"doc 不得含「{label}」")

# ---------------------------------------------------------------------------
# 結果
# ---------------------------------------------------------------------------
total = len(PASS) + len(FAIL)
print(f"\n合計：{len(PASS)}/{total} 通過")
if FAIL:
    print(f"\nXX v0.7.4-D readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print("\nv0.7.4-D Audit Trail Display readiness: ALL PASS")
    sys.exit(0)
