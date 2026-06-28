"""v0.7.2-F-A readiness check: Queue Task Annotation / Approval Readiness plan.

Plan-only verification. Checks that the annotation / approval-readiness plan
exists and is complete (annotation fields, the approval_readiness enum, the
decision/execution separation statements, safety boundaries, non-goals), and
that it asserts no unsafe "enabled / connected" state and contains no secret.

This script only reads the plan document. It does NOT read .env, credentials,
tokens, or secrets, touches no app/ logic, and makes no network call.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
PASS = []
FAIL = []

DOC_PATH = ROOT / "docs" / "HERMES_OPENCLAW_QUEUE_TASK_ANNOTATION_APPROVAL_READINESS_PLAN_V0_7_2_F_A.md"


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
ok("F-A plan doc 存在") if DOC_PATH.exists() else xx("F-A plan doc 存在")
if not DOC_PATH.exists():
    print("\nXX plan doc 不存在，無法繼續")
    sys.exit(1)

doc = DOC_PATH.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# [2] 必須包含的字串（標題 + annotation fields + readiness 狀態 + 安全聲明）
# ---------------------------------------------------------------------------
print("[2] 必須包含的字串")
REQUIRED = [
    "v0.7.2-F-A",
    "Queue Task Annotation",
    "Approval Readiness",
    # annotation fields
    "task_origin",
    "requested_by",
    "request_channel",
    "owner_reason",
    "approval_readiness",
    "approval_blockers",
    "risk_summary",
    "side_effect_summary",
    "next_step_if_approved",
    "execution_mode",
    "external_touchpoints",
    "dry_run_available",
    "mock_available",
    "rollback_note",
    "human_readable_summary",
    # readiness states
    "not_ready",
    "owner_review_required",
    "ready_for_owner_decision",
    "blocked_by_policy",
    "prohibited",
    # decision/execution separation
    "Approval readiness is not execution permission",
    "Owner approval does not automatically imply Worker execution",
    # safety boundaries
    "No QueueStore runtime behavior changes",
    "No approval wiring changes",
    "No Worker execution",
    "No OpenClaw call",
    "No Hermes call",
    "No Google Sheets write",
    "No external side effects",
    "No schema migration",
    "No demo task cleanup",
]
for token in REQUIRED:
    ok(f"doc 含「{token}」") if token in doc else xx(f"doc 含「{token}」")

# ---------------------------------------------------------------------------
# [3] 必須包含的章節
# ---------------------------------------------------------------------------
print("[3] 必須包含的章節")
REQUIRED_SECTIONS = [
    "1. Purpose",
    "2. Current baseline",
    "3. Why this is still v0.7.2",
    "4. Queue task annotation goal",
    "5. Owner problem",
    "6. Proposed annotation fields",
    "7. Proposed approval readiness model",
    "8. Proposed risk explanation model",
    "9. Proposed source / origin model",
    "10. Proposed next-step explanation model",
    "11. Proposed dry-run / mock / real boundary model",
    "12. Dashboard / Owner Review Panel display impact",
    "13. QueueStore compatibility plan",
    "14. Backward compatibility",
    "15. Data migration stance",
    "16. Safety boundaries",
    "17. Non-goals",
    "18. Implementation phases",
    "19. Readiness criteria",
    "20. Risks",
    "21. Acceptance criteria",
]
for section in REQUIRED_SECTIONS:
    ok(f"doc 含章節「{section}」") if section in doc else xx(f"doc 含章節「{section}」")

# ---------------------------------------------------------------------------
# [4] 禁止包含的不安全狀態 / 機密聲明
# ---------------------------------------------------------------------------
print("[4] 禁止包含的不安全狀態 / 機密聲明")
FORBIDDEN_SUBSTR = [
    "GOOGLE_SHEETS_ENABLED=true",
    "Worker enabled",
    "OpenClaw connected",
    "Hermes connected",
    "Google Sheets live write enabled",
]
for token in FORBIDDEN_SUBSTR:
    ok(f"doc 無「{token}」") if token not in doc else xx(f"doc 不得含「{token}」")

FORBIDDEN_PATTERNS = [
    (r"spreadsheets/d/[A-Za-z0-9_-]{20,}", "real spreadsheet URL"),
    (r'"?refresh_token"?\s*[:=]\s*"[^"]+"', "refresh token value"),
    (r'"?client_secret"?\s*[:=]\s*"[^"]+"', "client secret value"),
    (r'-----BEGIN[ A-Z]*PRIVATE KEY-----', "private key value"),
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
    print(f"\nXX v0.7.2-F-A readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print("\nv0.7.2-F-A Queue Task Annotation / Approval Readiness plan readiness: ALL PASS")
    sys.exit(0)
