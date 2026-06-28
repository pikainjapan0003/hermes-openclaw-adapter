"""v0.7.2-UI-D-A readiness check: Jarvis visual shell implementation.

Verifies the dashboard visual shell (base / login / dashboard templates +
dashboard.css) carries the Jarvis Owner Control Room look and the safe-posture
status indicators, and that it introduces no external dependency or side effect.

This script only reads the four UI files (templates + css). It does NOT read
.env, credentials, tokens, or secrets, touches no app/ logic, and makes no
network call.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
PASS = []
FAIL = []

UI_FILES = {
    "templates/base.html": ROOT / "templates" / "base.html",
    "templates/login.html": ROOT / "templates" / "login.html",
    "templates/dashboard.html": ROOT / "templates" / "dashboard.html",
    "static/dashboard.css": ROOT / "static" / "dashboard.css",
}


def ok(label):
    PASS.append(label)
    print(f"  ok : {label}")


def xx(label):
    FAIL.append(label)
    print(f"  XX : {label}")


# ---------------------------------------------------------------------------
# [1] UI 檔案存在
# ---------------------------------------------------------------------------
print("[1] UI 檔案存在")
for rel, path in UI_FILES.items():
    ok(f"{rel} 存在") if path.exists() else xx(f"{rel} 存在")

missing = [rel for rel, p in UI_FILES.items() if not p.exists()]
if missing:
    print(f"\nXX 缺少 UI 檔案，無法繼續：{missing}")
    sys.exit(1)

# 合併語料（4 個 UI 檔的內容），required/forbidden 皆對合併語料判斷。
corpus = "\n".join(p.read_text(encoding="utf-8") for p in UI_FILES.values())
corpus_lower = corpus.lower()

# ---------------------------------------------------------------------------
# [2] 必須包含（Jarvis 視覺 + 安全狀態語彙；大小寫不敏感）
# ---------------------------------------------------------------------------
print("[2] 必須包含的視覺 / 狀態語彙")
REQUIRED = [
    "Hermes x OpenClaw Owner Control Room",
    "Read-only",
    "Safe",
    "Worker",
    "OFF",
    "OpenClaw",
    "Not Connected",
    "Hermes",
    "Google Sheets",
    "Disabled",
    "Kill Switch",
    "Local-only",
    "Owner Required",
    "jarvis",   # jarvis or Jarvis
    "hud",      # hud or HUD
    "glass",
    "neon",
]
for token in REQUIRED:
    ok(f"含「{token}」") if token.lower() in corpus_lower else xx(f"含「{token}」")

# ---------------------------------------------------------------------------
# [3] 禁止包含（外部依賴 / 功能串接 / 機密）
# ---------------------------------------------------------------------------
print("[3] 禁止包含的外部依賴 / 串接 markers")
FORBIDDEN_SUBSTR = [
    "cdn",
    "three.js",
    "websocket",
    "speechrecognition",
    "openai",
    "GOOGLE_SHEETS_ENABLED=true",
]
for token in FORBIDDEN_SUBSTR:
    ok(f"無「{token}」") if token.lower() not in corpus_lower else xx(f"不得含「{token}」")

print("[4] 禁止包含的機密 / 外部 URL 樣式")
FORBIDDEN_PATTERNS = [
    (r"spreadsheets/d/[A-Za-z0-9_-]{20,}", "real spreadsheet URL"),
    (r'"?refresh_token"?\s*[:=]\s*"[^"]+"', "refresh token value"),
    (r'"?client_secret"?\s*[:=]\s*"[^"]+"', "client secret value"),
    (r'-----BEGIN[ A-Z]*PRIVATE KEY-----', "private key value"),
    (r'https?://[\w.-]*(cdnjs|unpkg|jsdelivr)', "external CDN URL"),
]
for pat, label in FORBIDDEN_PATTERNS:
    found = bool(re.search(pat, corpus, re.IGNORECASE))
    ok(f"無「{label}」") if not found else xx(f"不得含「{label}」")

# ---------------------------------------------------------------------------
# [5] 行為邊界：UI 檔不得引入 <script> 或外部資源連結
# ---------------------------------------------------------------------------
print("[5] UI 檔不得引入 script / 外部資源")
html_corpus = "\n".join(
    UI_FILES[f].read_text(encoding="utf-8")
    for f in ("templates/base.html", "templates/login.html", "templates/dashboard.html")
)
ok("templates 無 <script>") if "<script" not in html_corpus.lower() else xx("templates 不得含 <script>")
# 只允許本地 /static 樣式；不得有 http(s) 外連 link/src
ext_link = re.search(r'(href|src)\s*=\s*"https?://', html_corpus, re.IGNORECASE)
ok("templates 無外部 http(s) link/src") if not ext_link else xx("templates 不得含外部 http(s) link/src")

# ---------------------------------------------------------------------------
# 結果
# ---------------------------------------------------------------------------
total = len(PASS) + len(FAIL)
print(f"\n合計：{len(PASS)}/{total} 通過")
if FAIL:
    print(f"\nXX v0.7.2-UI-D-A readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print("\nv0.7.2-UI-D-A Jarvis visual shell readiness: ALL PASS")
    sys.exit(0)
