"""v0.7.2-UI-C readiness check: Jarvis Owner Control Room visual design plan.

Plan-only verification. This script checks that the UI-C visual design plan
exists and is complete, and that neither the plan nor this script carries any
external side effect or secret. It does NOT read .env, credentials, tokens, or
secrets, does NOT touch app/templates/static, and performs no network calls.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
PASS = []
FAIL = []

DOC_PATH = ROOT / "docs" / "HERMES_OPENCLAW_DASHBOARD_JARVIS_OWNER_CONTROL_ROOM_VISUAL_PLAN_V0_7_2_UI_C.md"
SELF_PATH = ROOT / "scripts" / "check_hermes_openclaw_dashboard_jarvis_owner_control_room_visual_plan_v0_7_2_ui_c.py"


def ok(label):
    PASS.append(label)
    print(f"  ok : {label}")


def xx(label):
    FAIL.append(label)
    print(f"  XX : {label}")


# ---------------------------------------------------------------------------
# [1] doc / readiness 自身存在
# ---------------------------------------------------------------------------
print("[1] UI-C doc / readiness 存在")
ok("UI-C plan doc 存在") if DOC_PATH.exists() else xx("UI-C plan doc 存在")
ok("UI-C readiness 自身存在") if SELF_PATH.exists() else xx("UI-C readiness 自身存在")

if not DOC_PATH.exists():
    print("\nXX plan doc 不存在，無法繼續檢查")
    sys.exit(1)

doc_text = DOC_PATH.read_text(encoding="utf-8")
doc_lower = doc_text.lower()

# ---------------------------------------------------------------------------
# [2] 必須包含的 UI-C 設計語彙
# ---------------------------------------------------------------------------
print("[2] doc 必須包含的設計語彙")
REQUIRED_TOKENS = [
    "v0.7.2-UI-C",
    "Jarvis",
    "Owner Control Room",
    "Hermes x OpenClaw",
    "Read-only",
    "Safe",
    "Worker: OFF",
    "OpenClaw: Not Connected",
    "Hermes: Not Connected",
    "Google Sheets: Disabled",
    "Kill Switch",
    "glass",
    "HUD",
    "neon",
    "radar",
    "status cards",
    "Replit Preview acceptance criteria",
    "Non-goals",
    "Allowed files",
    "no external side effects",
]
for token in REQUIRED_TOKENS:
    present = token.lower() in doc_lower
    ok(f"doc 含「{token}」") if present else xx(f"doc 含「{token}」")

# ---------------------------------------------------------------------------
# [3] 必須包含的章節
# ---------------------------------------------------------------------------
print("[3] doc 必須包含的章節")
REQUIRED_SECTIONS = [
    "1. Purpose",
    "2. Current dashboard UI inventory",
    "3. Design reference extracted from research report",
    "4. Jarvis Owner Control Room concept",
    "5. Visual language",
    "6. Layout proposal",
    "7. Color system",
    "8. Typography and icon direction",
    "9. Dashboard overview page design",
    "10. Login page design",
    "11. Status cards design",
    "12. Queue / Review / System panels",
    "13. Safety boundary indicators",
    "14. Replit Preview acceptance criteria",
    "15. Non-goals",
    "16. Allowed files for later implementation",
    "17. Risks",
    "18. Acceptance criteria",
]
for section in REQUIRED_SECTIONS:
    ok(f"doc 含章節「{section}」") if section in doc_text else xx(f"doc 含章節「{section}」")

# ---------------------------------------------------------------------------
# [4] 禁止內容：不得引入真實功能串接 / 外部依賴
#     （Non-goals 提及名稱是允許的；這裡只攔真正的實作/依賴標記）
# ---------------------------------------------------------------------------
print("[4] 禁止：真實串接 / 外部依賴 markers 不得出現")
FORBIDDEN_PATTERNS = [
    (r"GOOGLE_SHEETS_ENABLED\s*=\s*true", "GOOGLE_SHEETS_ENABLED=true"),
    (r"docs\.google\.com/spreadsheets/d/[\w-]+", "real spreadsheet URL"),
    (r"new\s+WebSocket\s*\(", "new WebSocket() implementation"),
    (r"wss?://", "live WebSocket endpoint"),
    (r"api\.(anthropic|openai)\.com", "external LLM API endpoint"),
    (r"three\.(module|min)\.js", "Three.js dependency file"),
    (r"import\s+\*\s+as\s+THREE", "Three.js import"),
    (r"https?://[\w.-]*(cdn|unpkg|jsdelivr)", "external CDN dependency"),
]
for pat, label in FORBIDDEN_PATTERNS:
    found = bool(re.search(pat, doc_text, re.IGNORECASE))
    ok(f"doc 無「{label}」") if not found else xx(f"doc 不得含「{label}」")

# ---------------------------------------------------------------------------
# [5] 禁止內容：secrets 樣式不得出現（doc + 自身）
# ---------------------------------------------------------------------------
print("[5] 機密樣式非混入確認（doc + readiness 自身）")
SECRET_PATTERNS = [
    (r'"refresh_token"\s*:\s*"[^"]+"', "refresh token value"),
    (r'"client_secret"\s*:\s*"[^"]+"', "client secret value"),
    (r'-----BEGIN[ A-Z]*PRIVATE KEY-----', "private key value"),
    (r'1[0-9A-Za-z_-]{40,}', "long spreadsheet id"),
]
self_text = SELF_PATH.read_text(encoding="utf-8") if SELF_PATH.exists() else ""
for name, content in [("plan doc", doc_text), ("readiness self", self_text)]:
    for pat, label in SECRET_PATTERNS:
        found = bool(re.search(pat, content))
        full = f"{name} 無「{label}」"
        ok(full) if not found else xx(f"{name} 不得含「{label}」")

# ---------------------------------------------------------------------------
# [6] 無外部副作用：本 script 不得 import 網路 / 子程序 / 認證模組
# ---------------------------------------------------------------------------
print("[6] readiness 自身無外部副作用 import")
FORBIDDEN_IMPORTS = ["requests", "urllib", "httpx", "socket", "subprocess",
                     "gspread", "google", "openclaw", "websocket"]
for mod in FORBIDDEN_IMPORTS:
    bad = bool(re.search(rf'^\s*import\s+{mod}\b', self_text, re.MULTILINE)) or \
        bool(re.search(rf'^\s*from\s+{mod}\b', self_text, re.MULTILINE))
    ok(f"readiness 不 import {mod}") if not bad else xx(f"readiness 不得 import {mod}")

# ---------------------------------------------------------------------------
# 結果
# ---------------------------------------------------------------------------
total = len(PASS) + len(FAIL)
print(f"\n合計：{len(PASS)}/{total} 通過")
if FAIL:
    print(f"\nXX v0.7.2-UI-C readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print("\nv0.7.2-UI-C Jarvis visual plan readiness: ALL PASS")
    sys.exit(0)
