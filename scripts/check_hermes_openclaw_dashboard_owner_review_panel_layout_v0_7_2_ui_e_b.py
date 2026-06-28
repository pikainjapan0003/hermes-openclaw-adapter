"""v0.7.2-UI-E-B readiness check: Owner Review Panel layout implementation.

Verifies the Owner Review Panel / Pending Actions UI was implemented across the
dashboard / reviews / task_detail templates + dashboard.css, Chinese-first with
clear safety reminders, and introduces no external dependency or side effect.

This script only reads the four UI files. It does NOT read .env, credentials,
tokens, or secrets, touches no app/ logic, and makes no network call.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
PASS = []
FAIL = []

TPL = ROOT / "templates"
UI_FILES = {
    "templates/dashboard.html": TPL / "dashboard.html",
    "templates/reviews.html": TPL / "reviews.html",
    "templates/task_detail.html": TPL / "task_detail.html",
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
# [2] 必須包含的 Owner Review Panel markers
# ---------------------------------------------------------------------------
print("[2] 必須包含的 Owner Review Panel markers")
REQUIRED = [
    # dashboard overview
    "Owner 待處理",
    "待審核任務",
    "最近錯誤",
    "需要人工確認",
    "下一步建議",
    "查看待審核項目",
    # reviews page
    "Owner 審核佇列",
    "需要你確認的任務",
    "風險等級",
    "請求動作",
    "目前狀態",
    "查看詳情",
    "核准前請確認風險",
    "拒絕會保留任務記錄",
    # task detail
    "Owner 審核面板",
    "這個任務為什麼需要你確認",
    "是否可核准",
    "風險提示",
    "安全邊界",
    "人工審核",
    "安全控制",
    "工單入口",
    # css classes
    ".owner-review-panel",
    ".owner-action-card",
    ".owner-risk-note",
    ".owner-safety-boundary",
]
for token in REQUIRED:
    ok(f"含「{token}」") if token in corpus else xx(f"含「{token}」")

# ---------------------------------------------------------------------------
# [3] 禁止包含（外部依賴 / 機密）
# ---------------------------------------------------------------------------
print("[3] 禁止包含的外部依賴 / 機密 markers")
FORBIDDEN_SUBSTR = [
    "cdn", "three.js", "websocket", "speechrecognition", "openai",
    "GOOGLE_SHEETS_ENABLED=true", "refresh_token", "client_secret", "private_key",
]
for token in FORBIDDEN_SUBSTR:
    ok(f"無「{token}」") if token.lower() not in corpus_lower else xx(f"不得含「{token}」")

print("[4] 禁止包含的外部 URL / spreadsheet 樣式")
FORBIDDEN_PATTERNS = [
    (r"spreadsheets/d/[A-Za-z0-9_-]{20,}", "real spreadsheet URL"),
    (r'https?://[\w.-]*(cdnjs|unpkg|jsdelivr)', "external CDN URL"),
]
for pat, label in FORBIDDEN_PATTERNS:
    found = bool(re.search(pat, corpus, re.IGNORECASE))
    ok(f"無「{label}」") if not found else xx(f"不得含「{label}」")

# ---------------------------------------------------------------------------
# [5] 行為邊界：templates 不得引入 <script> / 外部資源
# ---------------------------------------------------------------------------
print("[5] templates 行為邊界")
html_corpus = "\n".join(
    UI_FILES[f].read_text(encoding="utf-8")
    for f in ("templates/dashboard.html", "templates/reviews.html", "templates/task_detail.html")
)
ok("templates 無 <script>") if "<script" not in html_corpus.lower() else xx("templates 不得含 <script>")
ext_link = re.search(r'(href|src)\s*=\s*"https?://', html_corpus, re.IGNORECASE)
ok("templates 無外部 http(s) link/src") if not ext_link else xx("templates 不得含外部 http(s) link/src")
# approve/reject form 行為保留（route/method/input name 不變）
reviews_html = UI_FILES["templates/reviews.html"].read_text(encoding="utf-8")
ok("reviews approve route 保留") if 'action="/dashboard/tasks/{{ t.task_id }}/approve"' in reviews_html else xx("reviews approve route 保留")
ok("reviews reject route 保留") if 'action="/dashboard/tasks/{{ t.task_id }}/reject"' in reviews_html else xx("reviews reject route 保留")
ok("reviews reject input name=reason 保留") if 'name="reason"' in reviews_html else xx("reviews reject input name 保留")

# ---------------------------------------------------------------------------
# 結果
# ---------------------------------------------------------------------------
total = len(PASS) + len(FAIL)
print(f"\n合計：{len(PASS)}/{total} 通過")
if FAIL:
    print(f"\nXX v0.7.2-UI-E-B readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print("\nv0.7.2-UI-E-B Owner Review Panel layout readiness: ALL PASS")
    sys.exit(0)
