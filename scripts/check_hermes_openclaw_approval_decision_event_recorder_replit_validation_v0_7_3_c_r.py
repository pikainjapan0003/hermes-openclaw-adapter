"""v0.7.3-C-R readiness check: Local Approval Event Recorder Replit GET-only Closeout.

Closeout / validation-record verification. Checks that the v0.7.3-C-R closeout
document exists and contains the required sections (1-19), the Replit pull /
restart / HTTP smoke markers, the /dashboard/reviews and
/dashboard/tasks/demo-ui-e-b-review-001 GET-only regression markers, the
"no live queue write validation" markers, and the safety confirmations — and that
it asserts no unsafe "enabled / connected / execution-granting / POST-to /
clicked / seeded / cleaned-up / live-write-performed" claim and contains no secret.

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
    / "HERMES_OPENCLAW_APPROVAL_DECISION_EVENT_RECORDER_REPLIT_VALIDATION_V0_7_3_C_R.md"
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
ok("v0.7.3-C-R closeout doc 存在") if DOC_PATH.exists() else xx("v0.7.3-C-R closeout doc 存在")
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
    "4. Relationship to v0.7.3-C",
    "5. Replit environment confirmation",
    "6. Pull result",
    "7. Replit overlay status",
    "8. Local checks on Replit",
    "9. Preview server restart",
    "10. HTTP smoke results",
    "11. /dashboard/reviews GET-only regression",
    "12. /dashboard/tasks/demo-ui-e-b-review-001 GET-only regression",
    "13. Required v0.7.3-C safety confirmations",
    "14. No live queue write validation",
    "15. Safety confirmations",
    "16. Non-goals",
    "17. Acceptance criteria",
    "18. Final closeout statement",
    "19. Next recommended step",
]
for section in REQUIRED_SECTIONS:
    ok(f"doc 含章節「{section}」") if section in doc else xx(f"doc 含章節「{section}」")

# ---------------------------------------------------------------------------
# [3] 必須包含的驗證 markers
# ---------------------------------------------------------------------------
print("[3] 必須包含的驗證 markers")
REQUIRED = [
    "v0.7.3-C-R",
    "Local Approval Event Recorder Replit GET-only Closeout",
    "v0.7.3-C Replit Preview GET-only regression",
    "HEAD = origin/master = c0417b46c81528ffd8997978bd8190edb636c101",
    "feat: add local approval decision event recorder",
    "Replit environment confirmed",
    "not Windows WSL",
    # pull markers
    "pull before HEAD = 7fd09df4e6a6a5a26d73fc8e64f9f786dca1066f",
    "pull after HEAD = c0417b46c81528ffd8997978bd8190edb636c101",
    "fast-forward pull succeeded",
    "8 files changed",
    "1452 insertions",
    # overlay
    "M .replit",
    "?? .claude/",
    "?? patches/",
    # local checks
    "v0.7.3-C readiness PASS",
    "77/77",
    "v0.7.3-C local append-only test PASS",
    "33/33",
    "local append-only test used temp SQLite / in-process TestClient only",
    "no POST to Replit Preview or real queue",
    "v0.7.3-B readiness PASS",
    "76/76",
    "v0.7.3-B readonly test PASS",
    "42/42",
    "v0.7.3-B-R readiness PASS",
    "112/112",
    "dashboard regression PASS",
    "compileall PASS",
    # restart
    "old PID 1458",
    "new PID 3720",
    "Application startup complete",
    "Uvicorn running on http://0.0.0.0:8000",
    # http smoke
    "GET / -> 303 /dashboard",
    "GET /dashboard -> 303 /dashboard/login",
    "GET /dashboard/login -> 200",
    "GET /dashbord -> 404",
    # regression pass
    "/dashboard/reviews GET-only regression PASS",
    "/dashboard/tasks/demo-ui-e-b-review-001 GET-only regression PASS",
    # UI markers
    "Owner 決策紀錄",
    "Approval Decision Events",
    "決策紀錄",
    "決策紀錄：0",
    "只讀",
    "未派工",
    "尚無 Owner 決策事件紀錄",
    "v0.7.3-B 只讀顯示；v0.7.3-C 才會規劃 local recorder",
    "執行權限：未授權",
    "execution_permission = False",
    "派工允許：未允許",
    "dispatch_allowed = False",
    "approve is not execute.",
    "Owner decision event is not Worker dispatch.",
    "Decision and execution dispatch remain separate.",
    # safety confirmations
    "no commit",
    "no push",
    "no tag",
    "no reset",
    "no stash",
    "no approve/reject/cancel/retry/archive clicks",
    "No QueueStore runtime behavior changes during validation",
    "No approval route path/method changes during validation",
    "No dashboard auth changes during validation",
    "No status transition changes during validation",
    "No Worker execution",
    "No OpenClaw call",
    "No Hermes call",
    "No Google Sheets write",
    "No external side effects",
    "No --apply",
    "No demo task cleanup",
    "No seed demo task",
    "No secrets read",
    "No webhook",
    "Owner visual confirmation not required",
    # no live queue write validation
    "Live local queue write validation not performed",
    "Live local queue write validation not required unless separately approved by Owner",
    # fixed safety values
    "execution_permission_at_decision = False",
    "dispatch_allowed_at_decision = False",
    # final statement
    "v0.7.3-C is pushed and has passed Replit Preview GET-only regression.",
    "The Local Approval Event Recorder remains local / append-only.",
    "The Replit Preview validation did not exercise live approval writes.",
    # next step
    "v0.7.3-R — Approval Decision Layer Full Closeout",
    "v0.7.3-R must remain docs / readiness only.",
]
for token in REQUIRED:
    ok(f"doc 含「{token}」") if token in doc else xx(f"doc 含「{token}」")

# ---------------------------------------------------------------------------
# [4] 禁止包含的不安全聲明 / 機密
#     先移除合法的安全否定句（其字面包含 forbidden 子字串），再掃 forbidden。
# ---------------------------------------------------------------------------
print("[4] 禁止包含的不安全聲明 / 機密")
SAFE_NEGATIONS = [
    # 合法否定句，其字面含 'POST to Replit Preview'（大小寫兩種寫法都要移除）。
    "no POST to Replit Preview or real queue",
    "No POST to Replit Preview or real queue",
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
    "execution_permission_at_decision = True",
    "dispatch_allowed_at_decision = True",
    "execution_permission = True",
    "dispatch_allowed = True",
    "Owner approval triggers Worker execution",
    "approve triggers dispatch",
    "approve calls OpenClaw",
    "approve calls Hermes",
    "approve writes Google Sheets",
    "decision event dispatches Worker",
    "POST to Replit Preview",
    "POST to real queue",
    "clicked approve",
    "clicked reject",
    "clicked cancel",
    "clicked retry",
    "clicked archive",
    "demo task cleaned up",
    "seeded demo task",
    "live queue write validation performed",
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
    print(f"\nXX v0.7.3-C-R readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print("\nv0.7.3-C-R Local Approval Event Recorder Replit GET-only Closeout readiness: ALL PASS")
    sys.exit(0)
