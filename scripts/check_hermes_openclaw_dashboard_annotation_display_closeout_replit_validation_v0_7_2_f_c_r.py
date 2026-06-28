"""v0.7.2-F-C-R readiness check: Dashboard Annotation Display Closeout +
Replit Preview Validation record.

Closeout / validation-record verification. Checks that the F-C-R closeout
document exists and contains the required markers (current master, the validated
review surfaces, the validated annotation fields, the execution_permission /
dispatch_allowed unauthorized display, the decision/execution separation
reminders, the safety boundaries and non-goals), and that this segment only adds
the closeout document and this readiness script (static scope check).

This script only reads the closeout document and lists the segment's own
artifacts. It does NOT read .env, credentials, tokens, or secrets, makes no
network call, imports no app logic (no app.main, no QueueStore), starts no
Worker, and calls no OpenClaw / Hermes / Google Sheets.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
PASS = []
FAIL = []

DOC_PATH = (
    ROOT
    / "docs"
    / "HERMES_OPENCLAW_DASHBOARD_ANNOTATION_DISPLAY_CLOSEOUT_REPLIT_VALIDATION_V0_7_2_F_C_R.md"
)
SELF_PATH = Path(__file__).resolve()


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
ok("F-C-R closeout doc 存在") if DOC_PATH.exists() else xx("F-C-R closeout doc 存在")
if not DOC_PATH.exists():
    print("\nXX closeout doc 不存在，無法繼續")
    sys.exit(1)

doc = DOC_PATH.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# [2] 必須包含的關鍵文字
# ---------------------------------------------------------------------------
print("[2] 必須包含的關鍵文字")
REQUIRED = [
    "v0.7.2-F-C-R",
    "Dashboard Annotation Display Closeout",
    "Replit Preview Validation",
    "463f09d69dd9da26224a5b02a653c7dce20e2208",
    "feat: display queue task annotations",
    "/dashboard/reviews",
    "/dashboard/tasks/demo-ui-e-b-review-001",
    # annotation fields（中文標籤）
    "審核準備狀態",
    "任務摘要",
    "需要 Owner 的原因",
    "風險摘要",
    "外部影響",
    "核准後下一步",
    "執行模式",
    "可否 dry-run",
    "可否 mock",
    "外部接觸點",
    "Rollback 說明",
    # execution permission / dispatch display
    "執行權限：未授權",
    "派工允許：未允許",
    "execution_permission = False",
    "dispatch_allowed = False",
    # decision/execution separation reminders
    "審核準備狀態不是執行權限",
    "Owner 核准不等於 Worker 執行",
    "Decision 與 dispatch 仍然分離",
    # safety boundaries
    "No QueueStore runtime behavior changes",
    "No approval wiring changes",
    "No Worker execution",
    "No OpenClaw call",
    "No Hermes call",
    "No Google Sheets write",
    "No external side effects",
    "No --apply",
    "No demo task cleanup",
    "No approve/reject/cancel/retry/archive clicks",
]
for token in REQUIRED:
    ok(f"doc 含「{token}」") if token in doc else xx(f"doc 含「{token}」")

# ---------------------------------------------------------------------------
# [3] 必須包含的章節（1–21）
# ---------------------------------------------------------------------------
print("[3] 必須包含的章節")
REQUIRED_SECTIONS = [
    "1. Purpose",
    "2. Current master",
    "3. Scope",
    "4. Relationship to F-A / F-B / F-C",
    "5. What F-C delivered",
    "6. Replit pull result",
    "7. Server restart reason",
    "8. HTTP smoke validation",
    "9. /dashboard/reviews visual validation",
    "10. /dashboard/tasks/demo-ui-e-b-review-001 visual validation",
    "11. Annotation fields validated",
    "12. Execution permission display",
    "13. Dispatch allowed display",
    "14. Safety reminders validated",
    "15. Legacy / fallback behavior",
    "16. Replit overlay note",
    "17. Safety boundaries",
    "18. Non-goals",
    "19. Acceptance criteria",
    "20. Current state",
    "21. Next recommended step",
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

# ---------------------------------------------------------------------------
# [5] scope：本任務只允許新增 closeout doc 與本 readiness script
#     （靜態檢查：docs 下只有此 F_C_R doc、scripts 下只有此 f_c_r readiness）。
# ---------------------------------------------------------------------------
print("[5] scope 只允許新增 closeout doc 與 readiness script")
fcr_docs = sorted(p.name for p in (ROOT / "docs").glob("*") if "F_C_R" in p.name)
ok("docs 下僅有 1 個 F_C_R 文件") if fcr_docs == [DOC_PATH.name] else xx(
    f"docs 下 F_C_R 文件應只有 closeout doc，實際：{fcr_docs}"
)
fcr_scripts = sorted(p.name for p in (ROOT / "scripts").glob("*f_c_r*"))
ok("scripts 下僅有 1 個 f_c_r script") if fcr_scripts == [SELF_PATH.name] else xx(
    f"scripts 下 f_c_r script 應只有此 readiness，實際：{fcr_scripts}"
)

# ---------------------------------------------------------------------------
# 結果
# ---------------------------------------------------------------------------
total = len(PASS) + len(FAIL)
print(f"\n合計：{len(PASS)}/{total} 通過")
if FAIL:
    print(f"\nXX v0.7.2-F-C-R readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print("\nv0.7.2-F-C-R Dashboard Annotation Display Closeout + Replit Preview Validation readiness: ALL PASS")
    sys.exit(0)
