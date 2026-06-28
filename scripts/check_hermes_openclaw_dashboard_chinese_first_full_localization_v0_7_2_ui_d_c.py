"""v0.7.2-UI-D-C readiness check: Chinese-first full dashboard localization.

Verifies every dashboard page (tasks / task_detail / reviews / system, plus the
already-localized base / dashboard / login + css) presents Owner-facing
Traditional Chinese as the primary text, while keeping the necessary English as
small assistive sublabels and preserving status machine values.

This script only reads the dashboard UI files (templates + css). It does NOT
read .env, credentials, tokens, or secrets, touches no app/ logic, and makes no
network call.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
PASS = []
FAIL = []

TPL = ROOT / "templates"
# 本輪重點頁（存在性檢查）
FOCUS_FILES = {
    "templates/tasks.html": TPL / "tasks.html",
    "templates/task_detail.html": TPL / "task_detail.html",
    "templates/reviews.html": TPL / "reviews.html",
    "templates/system.html": TPL / "system.html",
    "static/dashboard.css": ROOT / "static" / "dashboard.css",
}
# 中文優先 / 英文輔助字串可分散於整個 dashboard，故對全部 UI 檔做語料判斷。
ALL_UI = [
    TPL / "base.html", TPL / "dashboard.html", TPL / "login.html",
    TPL / "tasks.html", TPL / "task_detail.html", TPL / "reviews.html",
    TPL / "system.html", ROOT / "static" / "dashboard.css",
]


def ok(label):
    PASS.append(label)
    print(f"  ok : {label}")


def xx(label):
    FAIL.append(label)
    print(f"  XX : {label}")


# ---------------------------------------------------------------------------
# [1] 重點檔案存在
# ---------------------------------------------------------------------------
print("[1] 重點 UI 檔案存在")
for rel, path in FOCUS_FILES.items():
    ok(f"{rel} 存在") if path.exists() else xx(f"{rel} 存在")

missing = [str(p) for p in ALL_UI if not p.exists()]
if missing:
    print(f"\nXX 缺少 UI 檔案，無法繼續：{missing}")
    sys.exit(1)

corpus = "\n".join(p.read_text(encoding="utf-8") for p in ALL_UI)
corpus_lower = corpus.lower()

# ---------------------------------------------------------------------------
# [2] 必須包含的中文優先字串
# ---------------------------------------------------------------------------
print("[2] 必須包含的中文優先字串")
REQUIRED_ZH = [
    "任務", "任務詳情", "審核", "待審核項目", "系統健康", "工單統計", "快速連結",
    "全部", "排隊中", "執行中", "等待審核", "失敗", "已完成", "已取消", "已拒絕", "已封存",
    "狀態", "顯示筆數", "起始位置", "篩選", "總數", "任務 ID", "標題", "工單入口", "唯讀",
    "嘗試次數", "建立時間", "更新時間", "錯誤",
    "轉接器", "執行器心跳", "OpenClaw 指令工具", "執行器狀態", "原始狀態", "主機名稱",
    "啟動時間", "最後看見時間", "CLI 路徑", "已檢查，未執行",
    "英文輔助",
]
for token in REQUIRED_ZH:
    ok(f"含中文「{token}」") if token in corpus else xx(f"含中文「{token}」")

# ---------------------------------------------------------------------------
# [3] 必須保留的英文輔助 / 狀態機值
# ---------------------------------------------------------------------------
print("[3] 必須保留的英文輔助 / 狀態機值")
REQUIRED_EN = [
    "Tasks", "Reviews", "System Health", "task id", "status",
    "queued", "running", "waiting_review", "failed", "completed",
    "cancelled", "rejected", "archived", "Worker Heartbeat", "OpenClaw CLI",
]
for token in REQUIRED_EN:
    ok(f"保留英文「{token}」") if token in corpus else xx(f"保留英文「{token}」")

# ---------------------------------------------------------------------------
# [4] 禁止包含（外部依賴 / 功能串接 / 機密）
# ---------------------------------------------------------------------------
print("[4] 禁止包含的外部依賴 / 串接 markers")
FORBIDDEN_SUBSTR = [
    "cdn", "three.js", "websocket", "speechrecognition", "openai",
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
# [6] 行為邊界：templates 不得引入 <script> / 外部資源
# ---------------------------------------------------------------------------
print("[6] templates 行為邊界")
html_corpus = "\n".join(
    p.read_text(encoding="utf-8") for p in ALL_UI if p.suffix == ".html"
)
ok("templates 無 <script>") if "<script" not in html_corpus.lower() else xx("templates 不得含 <script>")
ext_link = re.search(r'(href|src)\s*=\s*"https?://', html_corpus, re.IGNORECASE)
ok("templates 無外部 http(s) link/src") if not ext_link else xx("templates 不得含外部 http(s) link/src")

# ---------------------------------------------------------------------------
# 結果
# ---------------------------------------------------------------------------
total = len(PASS) + len(FAIL)
print(f"\n合計：{len(PASS)}/{total} 通過")
if FAIL:
    print(f"\nXX v0.7.2-UI-D-C readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print("\nv0.7.2-UI-D-C Chinese-first full localization readiness: ALL PASS")
    sys.exit(0)
