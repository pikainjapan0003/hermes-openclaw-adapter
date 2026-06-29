"""v0.7.3-A readiness check: Approval Decision Event Plan.

Plan-only verification. Checks that the Approval Decision Event plan document
exists and contains the required markers, decision types, the "approve only
records / does not dispatch" statements, and sections 1-21, and that it asserts
no unsafe "enabled / connected / execution-granting / approve-triggers" claim and
contains no secret.

This script only reads the plan document. It does NOT read .env, credentials,
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
    ROOT / "docs" / "HERMES_OPENCLAW_APPROVAL_DECISION_EVENT_PLAN_V0_7_3_A.md"
)


def ok(label):
    PASS.append(label)
    print(f"  ok : {label}")


def xx(label):
    FAIL.append(label)
    print(f"  XX : {label}")


# ---------------------------------------------------------------------------
# [1] plan 文件存在
# ---------------------------------------------------------------------------
print("[1] plan 文件存在")
ok("v0.7.3-A plan doc 存在") if DOC_PATH.exists() else xx("v0.7.3-A plan doc 存在")
if not DOC_PATH.exists():
    print("\nXX plan doc 不存在，無法繼續")
    sys.exit(1)

doc = DOC_PATH.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# [2] 必須包含的關鍵文字
# ---------------------------------------------------------------------------
print("[2] 必須包含的關鍵文字")
REQUIRED = [
    "v0.7.3-A",
    "Approval Decision Event Plan",
    "Owner decision event",
    "approval decision event",
    # decision event fields
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
    # separation statements
    "approve is not execute",
    "Owner decision event is not Worker dispatch",
    "Owner approval does not automatically imply Worker execution",
    "Decision and execution dispatch remain separate",
    "Approval readiness is not execution permission",
    "execution_permission = False",
    "dispatch_allowed = False",
    # safety boundaries
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
    ok(f"doc 含「{token}」") if token in doc else xx(f"doc 含「{token}」")

# ---------------------------------------------------------------------------
# [3] 必須包含的 decision types
# ---------------------------------------------------------------------------
print("[3] 必須包含的 decision types")
DECISION_TYPES = [
    "approve",
    "reject",
    "cancel",
    "retry",
    "archive",
    "comment",
    "request_more_info",
]
for token in DECISION_TYPES:
    ok(f"doc 含 decision type「{token}」") if token in doc else xx(f"doc 含 decision type「{token}」")

# ---------------------------------------------------------------------------
# [4] 必須包含「approve only records / does not」聲明
# ---------------------------------------------------------------------------
print("[4] 必須包含 approve-only-records 聲明")
APPROVE_STATEMENTS = [
    "approve only records an Owner decision event.",
    "approve does not dispatch Worker.",
    "approve does not call OpenClaw.",
    "approve does not call Hermes.",
    "approve does not write Google Sheets.",
    "retry does not call external systems.",
    "archive does not delete external state.",
]
for token in APPROVE_STATEMENTS:
    ok(f"doc 含「{token}」") if token in doc else xx(f"doc 含「{token}」")

# ---------------------------------------------------------------------------
# [5] 必須包含的章節（1-21）
# ---------------------------------------------------------------------------
print("[5] 必須包含的章節")
REQUIRED_SECTIONS = [
    "1. Purpose",
    "2. Current master",
    "3. Scope",
    "4. Relationship to v0.7.2-F annotation line",
    "5. Why approval decision events are needed",
    "6. Decision event definition",
    "7. Decision event fields",
    "8. Decision types",
    "9. Decision lifecycle",
    "10. Approval readiness snapshot",
    "11. Execution permission snapshot",
    "12. Dispatch allowed snapshot",
    "13. Safety snapshot",
    "14. Audit trail requirement",
    "15. Dashboard future display",
    "16. Queue metadata future storage",
    "17. Boundaries",
    "18. Non-goals",
    "19. Acceptance criteria",
    "20. Next recommended step",
    "21. Final planning statement",
]
for section in REQUIRED_SECTIONS:
    ok(f"doc 含章節「{section}」") if section in doc else xx(f"doc 含章節「{section}」")

# ---------------------------------------------------------------------------
# [6] current master marker
# ---------------------------------------------------------------------------
print("[6] current master marker")
ok("doc 含 current master 888967c") if "888967cbf2ff644df7c89c20226d0d9a2f5d164c" in doc else xx(
    "doc 含 current master 888967c"
)

# ---------------------------------------------------------------------------
# [7] 禁止包含的不安全聲明 / 機密
# ---------------------------------------------------------------------------
print("[7] 禁止包含的不安全聲明 / 機密")
FORBIDDEN_SUBSTR = [
    "GOOGLE_SHEETS_ENABLED=true",
    "Worker enabled",
    "OpenClaw connected",
    "Hermes connected",
    "Google Sheets live write enabled",
    "execution_permission = True",
    "dispatch_allowed = True",
    "Owner approval triggers Worker execution",
    "approval readiness grants execution permission",
    "approve triggers dispatch",
    "approve calls OpenClaw",
    "approve calls Hermes",
    "approve writes Google Sheets",
]
for token in FORBIDDEN_SUBSTR:
    ok(f"doc 無「{token}」") if token not in doc else xx(f"doc 不得含「{token}」")

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
    print(f"\nXX v0.7.3-A readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print("\nv0.7.3-A Approval Decision Event Plan readiness: ALL PASS")
    sys.exit(0)
