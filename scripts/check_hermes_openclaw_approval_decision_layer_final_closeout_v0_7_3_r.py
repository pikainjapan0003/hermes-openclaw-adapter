"""v0.7.3-R readiness check: Approval Decision Layer Full Closeout.

Closeout / current-state verification. Checks that the v0.7.3 Approval Decision
Layer full closeout document exists and contains the required sections (1-22), the
commit chain, the A/B/B-R/C/C-R completion markers, the event contract fields, the
Decision Message positioning, the dispatch-separation safety principles, the C-R
GET-only markers, the safe system posture, and the next recommended step — and that
it asserts no unsafe "enabled / connected / execution-granting / decision-message-
is-command / POST-to / clicked / seeded / cleaned-up / live-write-performed" claim
and contains no secret.

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
    ROOT / "docs" / "HERMES_OPENCLAW_APPROVAL_DECISION_LAYER_FINAL_CLOSEOUT_V0_7_3_R.md"
)


def ok(label):
    PASS.append(label)
    print(f"  ok : {label}")


def xx(label):
    FAIL.append(label)
    print(f"  XX : {label}")


# ---------------------------------------------------------------------------
# [1] final closeout 文件存在
# ---------------------------------------------------------------------------
print("[1] final closeout 文件存在")
ok("v0.7.3-R closeout doc 存在") if DOC_PATH.exists() else xx("v0.7.3-R closeout doc 存在")
if not DOC_PATH.exists():
    print("\nXX closeout doc 不存在，無法繼續")
    sys.exit(1)

doc = DOC_PATH.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# [2] 必須包含的章節（1-22）
# ---------------------------------------------------------------------------
print("[2] 必須包含的章節")
REQUIRED_SECTIONS = [
    "1. Purpose",
    "2. Current master",
    "3. Scope",
    "4. v0.7.3 line summary",
    "5. v0.7.3-A closeout",
    "6. v0.7.3-B closeout",
    "7. v0.7.3-B-R closeout",
    "8. v0.7.3-C closeout",
    "9. v0.7.3-C-R closeout",
    "10. Approval decision event contract",
    "11. Read-only view summary",
    "12. Local append-only recorder summary",
    "13. Replit validation summary",
    "14. Decision Message positioning",
    "15. Dispatch separation boundary",
    "16. QueueStore boundary",
    "17. External side-effect boundary",
    "18. Safety confirmations",
    "19. Non-goals",
    "20. Acceptance criteria",
    "21. Final closeout statement",
    "22. Next recommended step",
]
for section in REQUIRED_SECTIONS:
    ok(f"doc 含章節「{section}」") if section in doc else xx(f"doc 含章節「{section}」")

# ---------------------------------------------------------------------------
# [3] 必須包含的 markers（current master + commit chain + 完成 + contract + ...）
# ---------------------------------------------------------------------------
print("[3] 必須包含的 markers")
REQUIRED = [
    "v0.7.3-R",
    "Approval Decision Layer Full Closeout",
    # current master
    "HEAD = origin/master = 329fcd836eeed2e02724eb78f4823ca378f9eb11",
    "docs: close out approval decision recorder validation",
    # commit chain
    "e316760 docs: plan approval decision events",
    "7fd09df feat: add read-only approval decision event view",
    "3414456 docs: close out approval decision event view validation",
    "c0417b4 feat: add local approval decision event recorder",
    "329fcd8 docs: close out approval decision recorder validation",
    # completion markers
    "v0.7.3-A Approval Decision Event Plan complete",
    "v0.7.3-B Read-only Approval Event View complete",
    "v0.7.3-B-R Replit Preview View Closeout complete",
    "v0.7.3-C Local Approval Event Recorder complete",
    "v0.7.3-C-R Replit GET-only Recorder Closeout complete",
    # event contract fields
    "decision_id",
    "task_id",
    "decision_type",
    "decided_by",
    "decided_at",
    "decision_reason",
    "previous_status",
    "next_status",
    "approval_readiness_at_decision",
    "execution_permission_at_decision",
    "dispatch_allowed_at_decision",
    "safety_snapshot",
    "annotation_snapshot",
    "audit_record",
    # Decision Message positioning
    "approval_decision_events are Decision Messages.",
    "Decision Messages are blackboard audit records.",
    "Decision Messages are not Worker commands.",
    "Decision Messages are not OpenClaw commands.",
    "Decision Messages are not Hermes instructions.",
    # safety principles
    "approve is not execute.",
    "Owner decision event is not Worker dispatch.",
    "Owner approval does not automatically imply Worker execution.",
    "Decision and execution dispatch remain separate.",
    "Approval readiness is not execution permission.",
    "execution_permission_at_decision = False",
    "dispatch_allowed_at_decision = False",
    "execution_permission = False",
    "dispatch_allowed = False",
    # C-R GET-only markers
    "v0.7.3-C pushed and passed Replit Preview GET-only regression.",
    "Live local queue write validation not performed.",
    "Live local queue write validation not required unless separately approved by Owner.",
    "No POST to Replit Preview or real queue.",
    "No approve/reject/cancel/retry/archive clicks.",
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
    # final statement
    "v0.7.3 Approval Decision Layer is complete.",
    "The system now has an Owner approval decision event contract, a read-only display, and a local append-only recorder.",
    "Decision Messages are blackboard audit records, not execution commands.",
    "No Worker / OpenClaw / Hermes / Google Sheets execution was enabled.",
    # next step
    "v0.7.4-A — Core Topology / Dashboard Update / Core Independence Plan",
    "v0.7.4-A must remain docs / readiness only.",
]
for token in REQUIRED:
    ok(f"doc 含「{token}」") if token in doc else xx(f"doc 含「{token}」")

# ---------------------------------------------------------------------------
# [4] 禁止包含的不安全聲明 / 機密
#     先移除合法的安全否定句（其字面含 forbidden 子字串），再掃 forbidden。
# ---------------------------------------------------------------------------
print("[4] 禁止包含的不安全聲明 / 機密")
SAFE_NEGATIONS = [
    "No POST to Replit Preview or real queue",  # 合法否定句，含 'POST to Replit Preview'
    "no POST to Replit Preview or real queue",
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
    "Decision Messages are Worker commands",
    "Decision Messages are OpenClaw commands",
    "Decision Messages are Hermes instructions",
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
    print(f"\nXX v0.7.3-R readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print("\nv0.7.3-R Approval Decision Layer Full Closeout readiness: ALL PASS")
    sys.exit(0)
