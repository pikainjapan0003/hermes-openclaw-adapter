"""v0.7.2-UI-E-A readiness check: Owner Review Panel layout plan.

Plan-only verification. Checks that the Owner Review Panel layout plan exists and
is complete (Chinese-first wording, the three proposed panels, safety boundaries,
non-goals, Replit Preview smoke criteria), and that it asserts no unsafe
"enabled / connected" state and contains no secret.

This script only reads the plan document. It does NOT read .env, credentials,
tokens, or secrets, touches no app/ logic, and makes no network call.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
PASS = []
FAIL = []

DOC_PATH = ROOT / "docs" / "HERMES_OPENCLAW_DASHBOARD_OWNER_REVIEW_PANEL_LAYOUT_PLAN_V0_7_2_UI_E_A.md"


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
ok("UI-E-A plan doc 存在") if DOC_PATH.exists() else xx("UI-E-A plan doc 存在")
if not DOC_PATH.exists():
    print("\nXX plan doc 不存在，無法繼續")
    sys.exit(1)

doc = DOC_PATH.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# [2] 必須包含的字串（中文優先 + 邊界聲明 + 章節關鍵字）
# ---------------------------------------------------------------------------
print("[2] 必須包含的字串")
REQUIRED = [
    "v0.7.2-UI-E-A",
    "Owner Review Panel",
    "待審核項目",
    "Owner 待處理",
    "任務詳情",
    "核准",
    "拒絕",
    "取消",
    "重試",
    "封存",
    "Chinese-first",
    "Read-only",
    "No approval wiring changes",
    "No QueueStore behavior changes",
    "No Worker execution",
    "No OpenClaw call",
    "No Hermes call",
    "No Google Sheets write",
    "No external side effects",
    "Replit Preview smoke criteria",
    "Allowed future implementation files",
    "Non-goals",
    "Acceptance criteria",
]
for token in REQUIRED:
    ok(f"doc 含「{token}」") if token in doc else xx(f"doc 含「{token}」")

# ---------------------------------------------------------------------------
# [3] 必須包含的章節
# ---------------------------------------------------------------------------
print("[3] 必須包含的章節")
REQUIRED_SECTIONS = [
    "1. Purpose",
    "2. Current UI baseline",
    "3. Owner Review Panel goal",
    "4. User problem",
    "5. Proposed dashboard overview changes",
    "6. Proposed reviews page layout",
    "7. Proposed task detail review panel layout",
    "8. Pending actions model",
    "9. Safety boundary labels",
    "10. Chinese-first wording plan",
    "11. Read-only vs action-capable distinction",
    "12. Visual hierarchy",
    "13. Empty states",
    "14. Error states",
    "15. Replit Preview smoke criteria",
    "16. Allowed future implementation files",
    "17. Non-goals",
    "18. Risks",
    "19. Acceptance criteria",
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
    print(f"\nXX v0.7.2-UI-E-A readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print("\nv0.7.2-UI-E-A Owner Review Panel layout plan readiness: ALL PASS")
    sys.exit(0)
