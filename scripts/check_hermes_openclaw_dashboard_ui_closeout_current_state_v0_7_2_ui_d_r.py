"""v0.7.2-UI-D-R readiness check: Dashboard UI closeout / current-state.

Verifies the UI-D closeout document exists and records the frozen current state
of the Dashboard UI line (UI-D-A / UI-D-B / UI-D-C), the validated master commit,
the safe posture, and the explicit non-goals — without asserting any unsafe
"enabled / connected" state.

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

DOC_PATH = ROOT / "docs" / "HERMES_OPENCLAW_DASHBOARD_UI_CLOSEOUT_CURRENT_STATE_V0_7_2_UI_D_R.md"


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
ok("UI-D-R closeout doc 存在") if DOC_PATH.exists() else xx("UI-D-R closeout doc 存在")
if not DOC_PATH.exists():
    print("\nXX closeout doc 不存在，無法繼續")
    sys.exit(1)

doc = DOC_PATH.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# [2] 必須包含的 closeout / current-state 聲明
# ---------------------------------------------------------------------------
print("[2] 必須包含的 closeout / current-state 聲明")
REQUIRED = [
    "v0.7.2-UI-D-R",
    "299797017c20f82511086ecaf0cdf3e88c50672d",
    "Jarvis visual shell completed",
    "Traditional Chinese owner-friendly shell completed",
    "Chinese-first full dashboard localization completed",
    "Replit Preview visual validation passed",
    "read-only",
    "Worker is OFF",
    "OpenClaw is Not Connected",
    "Hermes is Not Connected",
    "Google Sheets is Disabled",
    "No Worker execution",
    "No OpenClaw call",
    "No Hermes call",
    "No Google Sheets write",
    "No secrets read",
    "No webhook",
    "No external side effects",
    "Traditional Chinese is the primary Owner-facing UI language",
    "English is retained only as small auxiliary labels",
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
    "3. UI-D scope",
    "4. UI-D-A result",
    "5. UI-D-B result",
    "6. UI-D-C result",
    "7. Replit Preview validation summary",
    "8. Current dashboard pages covered",
    "9. Safety boundaries",
    "10. Explicit non-goals",
    "11. Current external connection status",
    "12. Known local overlays",
    "13. Remaining UI follow-ups",
    "14. Acceptance criteria",
    "15. Closeout decision",
]
for section in REQUIRED_SECTIONS:
    ok(f"doc 含章節「{section}」") if section in doc else xx(f"doc 含章節「{section}」")

# ---------------------------------------------------------------------------
# [4] 禁止包含的「已啟用 / 已連線 / 機密」聲明
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
    print(f"\nXX v0.7.2-UI-D-R readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print("\nv0.7.2-UI-D-R Dashboard UI closeout current-state readiness: ALL PASS")
    sys.exit(0)
