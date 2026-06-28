"""v0.7.2-UI-E-R readiness check: Owner Review Panel closeout + demo validation.

Verifies the UI-E closeout document exists and records the frozen current state
of the Owner Review Panel line (UI-E-A / UI-E-B / UI-E-B-R), the validated master
commit, the Replit Preview demo validation, the demo task record, and the safe
posture — without asserting any unsafe "enabled / connected" state or any secret.

This script only reads the closeout document. It does NOT read .env,
credentials, tokens, or secrets, touches no app/ logic, and makes no network
call.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
PASS = []
FAIL = []

DOC_PATH = ROOT / "docs" / "HERMES_OPENCLAW_OWNER_REVIEW_PANEL_CLOSEOUT_DEMO_VALIDATION_V0_7_2_UI_E_R.md"


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
ok("UI-E-R closeout doc 存在") if DOC_PATH.exists() else xx("UI-E-R closeout doc 存在")
if not DOC_PATH.exists():
    print("\nXX closeout doc 不存在，無法繼續")
    sys.exit(1)

doc = DOC_PATH.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# [2] 必須包含的 closeout / 驗收聲明
# ---------------------------------------------------------------------------
print("[2] 必須包含的 closeout / 驗收聲明")
REQUIRED = [
    "v0.7.2-UI-E-R",
    "5b6c3737ff816ed2c2190c72ac3751277162e42c",
    "Owner Review Panel layout plan completed",
    "Owner Review Panel layout implementation completed",
    "Replit regression and demo fixture alignment completed",
    "Replit Preview demo validation passed",
    "demo-ui-e-b-review-001",
    "waiting_review",
    "safety_level = 3",
    "requires_confirmation = true",
    "demo_only = true",
    "local_only = true",
    "Owner 待處理 validated",
    "Owner 審核佇列 validated",
    "Owner 審核面板 validated",
    "Task detail Owner Review Panel validated",
    "No approval wiring changes",
    "No QueueStore runtime behavior changes",
    "No Worker execution",
    "No OpenClaw call",
    "No Hermes call",
    "No Google Sheets write",
    "No secrets read",
    "No webhook",
    "No external side effects",
    "No cleanup was performed",
]
for token in REQUIRED:
    ok(f"doc 含「{token}」") if token in doc else xx(f"doc 含「{token}」")

# ---------------------------------------------------------------------------
# [3] 必須包含的章節
# ---------------------------------------------------------------------------
print("[3] 必須包含的章節")
REQUIRED_SECTIONS = [
    "1. Purpose",
    "2. Current master commit",
    "3. UI-E scope",
    "4. UI-E-A result",
    "5. UI-E-B result",
    "6. UI-E-B-R result",
    "7. Replit Preview demo validation summary",
    "8. Pages validated",
    "9. Demo task record",
    "10. Safety boundaries",
    "11. Explicit non-goals",
    "12. Current external connection status",
    "13. Demo task persistence note",
    "14. Cleanup note",
    "15. Remaining follow-ups",
    "16. Acceptance criteria",
    "17. Closeout decision",
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
    print(f"\nXX v0.7.2-UI-E-R readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print("\nv0.7.2-UI-E-R Owner Review Panel closeout demo validation readiness: ALL PASS")
    sys.exit(0)
