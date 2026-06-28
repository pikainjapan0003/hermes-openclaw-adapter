"""v0.7.2-F-C readiness check: Display Annotation in Owner Review Panel.

Verifies that the read-only annotation display wiring is present: main.py imports
and attaches derive_queue_task_annotation, the review surfaces (task_detail.html /
reviews.html) render the annotation fields, the decision/execution separation
reminders, and the explicit execution_permission=False / dispatch_allowed=False
("執行權限：未授權" / "派工允許：未允許") markers — and that the display surfaces
(templates + css + test) contain no unsafe "enabled / connected" claim, no secret,
no external-call / side-effect marker, and no banned front-end dependency.

This script only reads the F-C display surfaces and wiring. It does NOT read .env,
credentials, tokens, or secrets, makes no network call, imports no app logic, and
writes nothing.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
PASS = []
FAIL = []

MAIN_PATH = ROOT / "app" / "main.py"
TASK_DETAIL_PATH = ROOT / "templates" / "task_detail.html"
REVIEWS_PATH = ROOT / "templates" / "reviews.html"
CSS_PATH = ROOT / "static" / "dashboard.css"
TEST_PATH = ROOT / "scripts" / "test_dashboard_annotation_display_readonly_v0_7_2_f_c.py"


def ok(label):
    PASS.append(label)
    print(f"  ok : {label}")


def xx(label):
    FAIL.append(label)
    print(f"  XX : {label}")


# ---------------------------------------------------------------------------
# [1] 必要檔案存在
# ---------------------------------------------------------------------------
print("[1] F-C 必要檔案存在")
required_files = {
    "app/main.py": MAIN_PATH,
    "templates/task_detail.html": TASK_DETAIL_PATH,
    "templates/reviews.html": REVIEWS_PATH,
    "static/dashboard.css": CSS_PATH,
    "scripts/test_dashboard_annotation_display_readonly_v0_7_2_f_c.py": TEST_PATH,
}
missing = False
for label, path in required_files.items():
    if path.exists():
        ok(f"{label} 存在")
    else:
        xx(f"{label} 存在")
        missing = True
if missing:
    print("\nXX F-C 必要檔案缺失，無法繼續")
    sys.exit(1)

main_src = MAIN_PATH.read_text(encoding="utf-8")
detail_src = TASK_DETAIL_PATH.read_text(encoding="utf-8")
reviews_src = REVIEWS_PATH.read_text(encoding="utf-8")
css_src = CSS_PATH.read_text(encoding="utf-8")
test_src = TEST_PATH.read_text(encoding="utf-8")

# 正向掃描：wiring（main.py）+ review surfaces（templates）+ test docstring。
positive = "\n".join([main_src, detail_src, reviews_src, test_src])
# 禁止字掃描：只掃顯示面（templates + css + test），不掃 main.py
# （main.py 既有 worker/callback 程式碼合法包含 subprocess/httpx/webhook）。
display_only = "\n".join([detail_src, reviews_src, css_src, test_src])

# ---------------------------------------------------------------------------
# [2] 必須存在的識別字 / annotation 欄位 / 安全聲明
# ---------------------------------------------------------------------------
print("[2] 必須存在的識別字 / annotation 欄位 / 安全聲明")
REQUIRED = [
    "v0.7.2-F-C",
    "Display Annotation in Owner Review Panel",
    "derive_queue_task_annotation",
    # annotation fields
    "human_readable_summary",
    "approval_readiness",
    "owner_reason",
    "risk_summary",
    "side_effect_summary",
    "next_step_if_approved",
    "execution_mode",
    "dry_run_available",
    "mock_available",
    "external_touchpoints",
    "rollback_note",
    "execution_permission",
    "dispatch_allowed",
    # decision/execution separation reminders（中文）
    "審核準備狀態不是執行權限",
    "Owner 核准不等於 Worker 執行",
    "Decision 與 dispatch 仍然分離",
    # explicit unauthorized markers
    "執行權限",
    "派工允許",
    "未授權",
    "未允許",
    # safety boundaries
    "No QueueStore runtime behavior changes",
    "No approval wiring changes",
    "No Worker execution",
    "No OpenClaw call",
    "No Hermes call",
    "No Google Sheets write",
    "No external side effects",
]
for token in REQUIRED:
    ok(f"含「{token}」") if token in positive else xx(f"含「{token}」")

# ---------------------------------------------------------------------------
# [3] main.py 只做 read-only context wiring（附加 annotation，不接 approval wiring）
# ---------------------------------------------------------------------------
print("[3] main.py read-only annotation wiring")
ok("main.py import derive_queue_task_annotation") if re.search(
    r"from app\.queue_task_annotation_v0_7 import derive_queue_task_annotation", main_src
) else xx("main.py import derive_queue_task_annotation")
ok("main.py 在 context 附加 annotation") if re.search(
    r'"annotation"\s*:\s*derive_queue_task_annotation\(', main_src
) else xx("main.py 在 context 附加 annotation")

# ---------------------------------------------------------------------------
# [4] 顯示面（templates）明確標示 execution_permission / dispatch_allowed = False
# ---------------------------------------------------------------------------
print("[4] 顯示面明確標示 未授權 / 未允許")
ok("task_detail 顯示 執行權限：未授權") if "執行權限：未授權" in detail_src else xx("task_detail 顯示 執行權限：未授權")
ok("task_detail 顯示 派工允許：未允許") if "派工允許：未允許" in detail_src else xx("task_detail 顯示 派工允許：未允許")
ok("task_detail 顯示 execution_permission = False") if "execution_permission = False" in detail_src else xx(
    "task_detail 顯示 execution_permission = False"
)
ok("task_detail 顯示 dispatch_allowed = False") if "dispatch_allowed = False" in detail_src else xx(
    "task_detail 顯示 dispatch_allowed = False"
)

# ---------------------------------------------------------------------------
# [5] 禁止包含的不安全狀態 / 機密 / 外部呼叫 / 前端依賴 markers（只掃顯示面）
# ---------------------------------------------------------------------------
print("[5] 禁止包含的不安全 / 機密 / 外部依賴 markers（templates + css + test）")
FORBIDDEN_SUBSTR = [
    "GOOGLE_SHEETS_ENABLED=true",
    "Worker enabled",
    "OpenClaw connected",
    "Hermes connected",
    "Google Sheets live write enabled",
    "subprocess",
    "Popen",
    "requests.",
    "httpx.",
    "uvicorn",
    "webhook",
    "Three.js",
    "WebSocket",
    "SpeechRecognition",
    "openai",
]
for token in FORBIDDEN_SUBSTR:
    if token in display_only:
        xx(f"顯示面不得含「{token}」")
    else:
        ok(f"顯示面無「{token}」")

FORBIDDEN_PATTERNS = [
    (r"spreadsheets/d/[A-Za-z0-9_-]{20,}", "real spreadsheet URL"),
    (r'"?refresh_token"?\s*[:=]\s*"[^"]+"', "refresh token value"),
    (r'"?client_secret"?\s*[:=]\s*"[^"]+"', "client secret value"),
    (r"-----BEGIN[ A-Z]*PRIVATE KEY-----", "private key value"),
]
for pat, label in FORBIDDEN_PATTERNS:
    found = bool(re.search(pat, display_only, re.IGNORECASE))
    ok(f"顯示面無「{label}」") if not found else xx(f"顯示面不得含「{label}」")

# ---------------------------------------------------------------------------
# [6] approval route 行為不得改變（POST approve/reject/cancel/retry/archive 仍在）
# ---------------------------------------------------------------------------
print("[6] approval route 行為未被破壞（仍存在原 POST 路由）")
for route in (
    '"/dashboard/tasks/{task_id}/approve"',
    '"/dashboard/tasks/{task_id}/reject"',
    '"/dashboard/tasks/{task_id}/cancel"',
    '"/dashboard/tasks/{task_id}/retry"',
    '"/dashboard/tasks/{task_id}/archive"',
):
    ok(f"main.py 保留 route {route}") if route in main_src else xx(f"main.py 保留 route {route}")

# ---------------------------------------------------------------------------
# [7] 顯示面不得引入 <script> 或外部 http(s) 資源
# ---------------------------------------------------------------------------
print("[7] 顯示面 templates 無 <script> / 無外部 http(s) 資源")
for label, src in (("task_detail.html", detail_src), ("reviews.html", reviews_src)):
    ok(f"{label} 無 <script>") if "<script" not in src.lower() else xx(f"{label} 無 <script>")
    found_url = bool(re.search(r'(?:src|href)\s*=\s*["\']https?://', src, re.IGNORECASE))
    ok(f"{label} 無外部 http(s) link/src") if not found_url else xx(f"{label} 無外部 http(s) link/src")

# ---------------------------------------------------------------------------
# 結果
# ---------------------------------------------------------------------------
total = len(PASS) + len(FAIL)
print(f"\n合計：{len(PASS)}/{total} 通過")
if FAIL:
    print(f"\nXX v0.7.2-F-C readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print("\nv0.7.2-F-C Display Annotation in Owner Review Panel readiness: ALL PASS")
    sys.exit(0)
