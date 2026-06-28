"""v0.7.2-UI-D-B readiness check: Traditional Chinese dashboard localization.

Verifies the dashboard visual shell (base / login / dashboard templates +
dashboard.css) presents Owner-facing Traditional Chinese text while preserving
the safe-posture meaning, and introduces no external dependency or side effect.

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

corpus = "\n".join(p.read_text(encoding="utf-8") for p in UI_FILES.values())
corpus_lower = corpus.lower()

# ---------------------------------------------------------------------------
# [2] 必須包含的繁中介面字串
# ---------------------------------------------------------------------------
print("[2] 必須包含的繁中介面字串")
REQUIRED_ZH = [
    "Owner 控制室",
    "唯讀監控台",
    "總覽",
    "任務",
    "審核",
    "系統",
    "登出",
    "控制台登入",
    "系統模式",
    "唯讀 / 安全",
    "工單入口",
    "本機限定",
    "審核閘門",
    "需要 Owner 核准",
    "執行器",
    "關閉",
    "未接線",
    "已停用",
    "緊急停止",
    "可見",
    "系統健康",
    "工單統計",
    "快速連結",
]
for token in REQUIRED_ZH:
    ok(f"含繁中「{token}」") if token in corpus else xx(f"含繁中「{token}」")

# ---------------------------------------------------------------------------
# [3] 安全狀態意義仍保留（英文或繁中任一即可）
# ---------------------------------------------------------------------------
print("[3] 安全狀態意義仍保留")
SAFETY_EITHER = [
    (("Read-only", "唯讀"), "Read-only / 唯讀"),
    (("Safe", "安全"), "Safe / 安全"),
    (("Worker", "執行器"), "Worker / 執行器"),
    (("OpenClaw",), "OpenClaw"),
    (("Hermes",), "Hermes"),
    (("Google Sheets",), "Google Sheets"),
    (("Kill Switch", "緊急停止"), "Kill Switch / 緊急停止"),
]
for variants, label in SAFETY_EITHER:
    present = any(v in corpus for v in variants)
    ok(f"保留狀態意義「{label}」") if present else xx(f"保留狀態意義「{label}」")

# ---------------------------------------------------------------------------
# [4] 禁止包含（外部依賴 / 功能串接 / 機密）
# ---------------------------------------------------------------------------
print("[4] 禁止包含的外部依賴 / 串接 markers")
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

print("[5] 禁止包含的機密 / 外部 URL 樣式")
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
# [6] 行為邊界：UI 檔不得引入 <script> 或外部資源；route/form 行為保留
# ---------------------------------------------------------------------------
print("[6] UI 檔行為邊界")
html_corpus = "\n".join(
    UI_FILES[f].read_text(encoding="utf-8")
    for f in ("templates/base.html", "templates/login.html", "templates/dashboard.html")
)
ok("templates 無 <script>") if "<script" not in html_corpus.lower() else xx("templates 不得含 <script>")
ext_link = re.search(r'(href|src)\s*=\s*"https?://', html_corpus, re.IGNORECASE)
ok("templates 無外部 http(s) link/src") if not ext_link else xx("templates 不得含外部 http(s) link/src")
# 登入 form 行為（method/action/input name）必須保留
login_html = UI_FILES["templates/login.html"].read_text(encoding="utf-8")
ok("login form method=post 保留") if 'method="post"' in login_html else xx("login form method=post 保留")
ok("login form action=/dashboard/login 保留") if 'action="/dashboard/login"' in login_html else xx("login form action 保留")
ok("login input name=dashboard_token 保留") if 'name="dashboard_token"' in login_html else xx("login input name 保留")

# ---------------------------------------------------------------------------
# 結果
# ---------------------------------------------------------------------------
total = len(PASS) + len(FAIL)
print(f"\n合計：{len(PASS)}/{total} 通過")
if FAIL:
    print(f"\nXX v0.7.2-UI-D-B readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print("\nv0.7.2-UI-D-B Traditional Chinese localization readiness: ALL PASS")
    sys.exit(0)
