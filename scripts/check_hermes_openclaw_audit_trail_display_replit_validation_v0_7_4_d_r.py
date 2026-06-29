"""v0.7.4-D-R readiness check: Audit Trail Display Replit GET-only Validation Closeout.

Closeout / current-state verification. Checks that the v0.7.4-D-R Replit GET-only
validation closeout document exists and contains the required sections (1-19), the
current-master marker, the v0.7.4-D completion markers, the Replit validation-passed
markers, the pull / overlay / checks / Dashboard-restart record, the GET-only
validation, the task-detail audit-trail markers, the reviews audit-summary markers,
the authentication note, the safety boundary, and the next recommended step — and
that it asserts no unsafe "enabled / connected / POST-was-sent / clicked / form-
submitted / validation-performed / started / called / written / created / added /
staged / changed / implemented / recorded / committed" claim and contains no secret.

The document is allowed to contain safe negations (e.g. "No POST to Replit
Preview.", "No force push.", "No push tags."); those are scrubbed before the
forbidden scan so they are not mis-flagged.

This script only reads the closeout document. It does NOT read .env, credentials,
tokens, or secrets, makes no network call, imports no app logic (no app.main, no
QueueStore), starts no Worker, and calls no OpenClaw / Hermes / Google Sheets.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
PASS = []
FAIL = []

DOC_PATH = (
    ROOT
    / "docs"
    / "HERMES_OPENCLAW_AUDIT_TRAIL_DISPLAY_REPLIT_VALIDATION_V0_7_4_D_R.md"
)


def ok(label):
    PASS.append(label)
    print(f"  ok : {label}")


def xx(label):
    FAIL.append(label)
    print(f"  XX : {label}")


# ---------------------------------------------------------------------------
# [1] closeout 文件存在
# ---------------------------------------------------------------------------
print("[1] closeout 文件存在")
ok("v0.7.4-D-R closeout doc 存在") if DOC_PATH.exists() else xx("v0.7.4-D-R closeout doc 存在")
if not DOC_PATH.exists():
    print("\nXX closeout doc 不存在，無法繼續")
    sys.exit(1)

doc = DOC_PATH.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# [2] 必須包含的章節（1-19）
# ---------------------------------------------------------------------------
print("[2] 必須包含的章節")
REQUIRED_SECTIONS = [
    "1. Purpose",
    "2. Current master",
    "3. Scope",
    "4. Relationship to v0.7.4-D",
    "5. Replit environment",
    "6. Pull result",
    "7. Replit overlay status",
    "8. Checks executed",
    "9. Dashboard restart",
    "10. GET-only Preview validation",
    "11. Audit Trail task detail validation",
    "12. Audit summary reviews validation",
    "13. Authentication note",
    "14. POST / queue-write boundary",
    "15. Runtime / external side-effect boundary",
    "16. Safety confirmations",
    "17. Non-goals",
    "18. Acceptance criteria",
    "19. Next recommended step",
]
for section in REQUIRED_SECTIONS:
    ok(f"doc 含章節「{section}」") if section in doc else xx(f"doc 含章節「{section}」")

# ---------------------------------------------------------------------------
# [3] 必須包含的 markers
# ---------------------------------------------------------------------------
print("[3] 必須包含的 markers")
REQUIRED = [
    # version
    "v0.7.4-D-R",
    "Audit Trail Display Replit GET-only Validation",
    # current master
    "HEAD = origin/master = a35b76661fce093132b8c656fe6e0042793ae38c",
    "feat: add read-only audit trail display",
    # v0.7.4-D completion markers
    "v0.7.4-D Audit Trail Display is complete.",
    "Audit Trail Display is read-only.",
    "Audit Trail Display does not change lifecycle state.",
    "Audit Trail Display does not enforce guard.",
    "Audit Trail Display does not dispatch Worker.",
    "Audit Trail Display does not call OpenClaw.",
    "Audit Trail Display does not call Hermes.",
    "Audit Trail Display does not write Google Sheets.",
    # Replit validation passed
    "v0.7.4-D-R Replit GET-only Validation passed.",
    "Replit fast-forward pull succeeded.",
    "Replit HEAD after pull = a35b76661fce093132b8c656fe6e0042793ae38c.",
    "Replit origin/master after pull = a35b76661fce093132b8c656fe6e0042793ae38c.",
    "Replit status after pull had only accepted overlays: modified .replit, untracked .claude/, and untracked patches/.",
    "No overlay file was staged.",
    "No overlay file was committed.",
    # pull result / start
    "Replit starting HEAD was c0417b46c81528ffd8997978bd8190edb636c101.",
    "Replit origin/master after fetch was a35b76661fce093132b8c656fe6e0042793ae38c.",
    "Pull was fast-forward.",
    "Pull changed 18 files with 4632 insertions.",
    # checks
    "v0.7.4-D readiness: 182/182 ALL PASS.",
    "v0.7.4-D readonly helper test: 29/29 ALL PASS.",
    "v0.7.4-C check: 221/221 ALL PASS.",
    "v0.7.4-B check: 197/197 ALL PASS.",
    "v0.7.4-A check: 151/151 ALL PASS.",
    "v0.7.3-R check: 120/120 ALL PASS.",
    "v0.7.3-C-R check: 133/133 ALL PASS.",
    "v0.7.3-C readiness: 77/77 ALL PASS.",
    "v0.7.3-C local append-only test: 33/33 ALL PASS.",
    "v0.7.3-B readiness: 76/76 ALL PASS.",
    "v0.7.3-B readonly test: 42/42 ALL PASS.",
    "v0.7.3-B-R check: 112/112 ALL PASS.",
    "v0.7.3-A check: 89/89 ALL PASS.",
    "F-R check: 80/80 ALL PASS.",
    "F-C-R check: 64/64 ALL PASS.",
    "F-C check: 69/69 ALL PASS.",
    "F-B check: 57/57 ALL PASS.",
    "F-A check: 65/65 ALL PASS.",
    "compileall app + scripts: PASS.",
    # Dashboard restart
    "Dashboard restarted with uvicorn app.main:app --host 0.0.0.0 --port 8000.",
    "Application startup complete.",
    "Uvicorn running on http://0.0.0.0:8000.",
    "Worker was not started.",
    # GET-only validation
    "GET / returned 303 to /dashboard/login and then 200.",
    "GET /dashboard/reviews returned 200.",
    "GET /dashboard/tasks/demo-ui-e-b-review-001 returned 200.",
    "Only GET requests were used.",
    "No POST request was sent.",
    "No approve/reject/cancel/retry/archive click was performed.",
    "No form was submitted.",
    "No queue write validation was performed.",
    # task detail audit trail
    "Task detail showed Audit Trail / Blackboard Messages.",
    "Task detail showed lifecycle_state.",
    "Task detail showed Task Message / Decision Messages / Result Messages / Advice Messages.",
    "Task detail showed execution_permission = False.",
    "Task detail showed dispatch_allowed = False.",
    "Task detail showed Worker Dispatch: Disabled.",
    "Task detail showed OpenClaw: Not Called.",
    "Task detail showed Hermes: Not Called.",
    "Task detail showed Google Sheets: Disabled.",
    "Task detail showed read_only = True.",
    "Task detail showed Result 0 / Advice 0 future-only.",
    # reviews audit summary
    "Reviews page showed Audit summary.",
    "Reviews page showed Audit: Task 1 / Decision 0 / Result 0 / Advice 0.",
    "Reviews page showed Lifecycle: owner_review.",
    # auth note
    "DASHBOARD_AUTH_ENABLED=true was active on Replit.",
    "GET validation used the existing dashboard_token query parameter supported by app.main auth middleware.",
    "No token value is recorded in this closeout.",
    "No token value was committed.",
    "No secret was printed into repository files.",
    # safety boundary
    "No commit.",
    "No push.",
    "No tag.",
    "No force push.",
    "No push tags.",
    "patches/ was not staged.",
    ".replit was not staged.",
    ".claude/ was not staged.",
    "No cleanup demo task.",
    "No seed demo task.",
    "No --apply.",
    "No Worker.",
    "No OpenClaw.",
    "No Hermes.",
    "No Google Sheets.",
    "No webhook.",
    "No POST to Replit Preview.",
    "No POST to real queue.",
    "No live local queue write validation.",
    "No production DB.",
    "No remote shared DB.",
    "No Remote Blackboard API runtime.",
    "No webhook receiver.",
    "No connector.",
    "No app/queue_store.py change.",
    "No QueueStore runtime behavior change.",
    "No approval routes method/path/redirect/status result change.",
    "No dashboard auth change.",
    "No status transition change.",
    "No runtime guard.",
    "No existing transition result change.",
    "No state-changing button.",
    "No state-changing form.",
    "GET-only Preview validation only.",
    # next recommended step
    "v0.7.4-D-R commit and push after Owner review.",
    "Next feature step after D-R closeout: v0.7.4-E — Demo Task Cleanup Plan.",
    "v0.7.4-E must be plan-first.",
    "No cleanup execution unless separately approved.",
    "No --apply unless separately approved.",
]
for token in REQUIRED:
    ok(f"doc 含「{token}」") if token in doc else xx(f"doc 含「{token}」")

# ---------------------------------------------------------------------------
# [4] 禁止包含的不安全聲明 / 機密
#     先移除合法的安全否定句（其字面含 forbidden 子字串），再掃 forbidden。
# ---------------------------------------------------------------------------
print("[4] 禁止包含的不安全聲明 / 機密")
SAFE_NEGATIONS = [
    "No POST to Replit Preview",  # 含 'POST to Replit Preview'
    "No POST to real queue",      # 含 'POST to real queue'
    "No force push",              # 含 'force push'
    "No push tags",               # 含 'push tags'
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
    "POST to Replit Preview was sent",
    "POST to real queue was sent",
    "approve clicked",
    "reject clicked",
    "cancel clicked",
    "retry clicked",
    "archive clicked",
    "form submitted",
    "queue write validation performed",
    "live local queue write validation performed",
    "cleanup demo task performed",
    "seeded demo task",
    "--apply executed",
    "Worker started",
    "OpenClaw called",
    "Hermes called",
    "Google Sheets written",
    "webhook created",
    "production DB created",
    "remote shared DB created",
    "Remote Blackboard API runtime created",
    "webhook receiver created",
    "connector added",
    "patches staged",
    ".replit staged",
    ".claude staged",
    "tag created",
    "force push",
    "push tags",
    "app/queue_store.py changed",
    "QueueStore runtime behavior changed",
    "approval routes changed",
    "dashboard auth changed",
    "status transition changed",
    "runtime guard implemented",
    "existing transition result changed",
    "state-changing button added",
    "state-changing form added",
    "token value recorded",
    "secret committed",
]
for token in FORBIDDEN_SUBSTR:
    ok(f"doc 無「{token}」") if token not in scrubbed else xx(f"doc 不得含「{token}」")

FORBIDDEN_PATTERNS = [
    (r"spreadsheets/d/[A-Za-z0-9_-]{20,}", "real spreadsheet URL"),
    (r'"?refresh_token"?\s*[:=]\s*"[^"]+"', "refresh token value"),
    (r'"?client_secret"?\s*[:=]\s*"[^"]+"', "client secret value"),
    (r"-----BEGIN[ A-Z]*PRIVATE KEY-----", "private key value"),
    (r"dashboard_token\s*=\s*[A-Za-z0-9_\-]{8,}", "dashboard token value"),
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
    print(f"\nXX v0.7.4-D-R readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print(
        "\nv0.7.4-D-R Audit Trail Display Replit GET-only Validation Closeout readiness: ALL PASS"
    )
    sys.exit(0)
