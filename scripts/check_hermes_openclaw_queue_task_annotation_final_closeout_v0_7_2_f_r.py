"""v0.7.2-F-R readiness check: Queue Task Annotation Final Closeout.

Closeout / current-state verification. Checks that the final closeout document
for the v0.7.2-F queue-task-annotation line (F-A → F-B → F-C → F-C-R) exists and
contains the required markers and sections 1–21, and that it asserts no unsafe
"enabled / connected / execution-granting" claim and contains no secret.

This script only reads the closeout document. It does NOT read .env, credentials,
tokens, or secrets, makes no network call, imports no app logic (no app.main, no
QueueStore), starts no Worker, and calls no OpenClaw / Hermes / Google Sheets.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
PASS = []
FAIL = []

DOC_PATH = (
    ROOT / "docs" / "HERMES_OPENCLAW_QUEUE_TASK_ANNOTATION_FINAL_CLOSEOUT_V0_7_2_F_R.md"
)


def ok(label):
    PASS.append(label)
    print(f"  ok : {label}")


def xx(label):
    FAIL.append(label)
    print(f"  XX : {label}")


# ---------------------------------------------------------------------------
# [1] final closeout 文件存在
# ---------------------------------------------------------------------------
print("[1] final closeout 文件存在")
ok("F-R final closeout doc 存在") if DOC_PATH.exists() else xx("F-R final closeout doc 存在")
if not DOC_PATH.exists():
    print("\nXX final closeout doc 不存在，無法繼續")
    sys.exit(1)

doc = DOC_PATH.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# [2] 必須包含的關鍵文字
# ---------------------------------------------------------------------------
print("[2] 必須包含的關鍵文字")
REQUIRED = [
    "v0.7.2-F-R",
    "Queue Task Annotation Final Closeout",
    "v0.7.2-F-A",
    "v0.7.2-F-B",
    "v0.7.2-F-C",
    "v0.7.2-F-C-R",
    "3104f74b7b54bf0143a8d449258bb23bbf2f9058",
    "docs: close out dashboard annotation display validation",
    "463f09d69dd9da26224a5b02a653c7dce20e2208",
    "feat: display queue task annotations",
    "Read-only Annotation Deriver",
    "Display Annotation in Owner Review Panel",
    "Dashboard Annotation Display Closeout",
    "Replit Preview Validation",
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
    # decision/execution separation statements
    "Approval readiness is not execution permission",
    "Owner approval does not automatically imply Worker execution",
    "Decision and execution dispatch remain separate",
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
    "4. Relationship to F-A / F-B / F-C / F-C-R",
    "5. F-A summary",
    "6. F-B summary",
    "7. F-C summary",
    "8. F-C-R summary",
    "9. What the annotation line now provides",
    "10. What remains read-only",
    "11. Execution permission boundary",
    "12. Dispatch allowed boundary",
    "13. Approval readiness boundary",
    "14. Dashboard / Owner Review Panel state",
    "15. Replit Preview validation state",
    "16. Current system state",
    "17. Safety boundaries",
    "18. Non-goals",
    "19. Acceptance criteria",
    "20. Next recommended step",
    "21. Final closeout statement",
]
for section in REQUIRED_SECTIONS:
    ok(f"doc 含章節「{section}」") if section in doc else xx(f"doc 含章節「{section}」")

# ---------------------------------------------------------------------------
# [4] 必須包含核心結論句
# ---------------------------------------------------------------------------
print("[4] 必須包含核心結論句")
for token in (
    "Queue task annotation line is complete.",
    "execution_permission = False.",
    "dispatch_allowed = False.",
):
    ok(f"doc 含核心結論「{token}」") if token in doc else xx(f"doc 含核心結論「{token}」")

# ---------------------------------------------------------------------------
# [5] 禁止包含的不安全狀態 / 機密 / 授予執行權的聲明
# ---------------------------------------------------------------------------
print("[5] 禁止包含的不安全聲明 / 機密")
FORBIDDEN_SUBSTR = [
    "GOOGLE_SHEETS_ENABLED=true",
    "Worker enabled",
    "OpenClaw connected",
    "Hermes connected",
    "Google Sheets live write enabled",
    "execution_permission = True",
    "dispatch_allowed = True",
    "Owner approval triggers Worker execution",
    "approval readiness grants execution permission",
]
for token in FORBIDDEN_SUBSTR:
    ok(f"doc 無「{token}」") if token not in doc else xx(f"doc 不得含「{token}」")

FORBIDDEN_PATTERNS = [
    (r"spreadsheets/d/[A-Za-z0-9_-]{20,}", "real spreadsheet URL"),
    (r'"?refresh_token"?\s*[:=]\s*"[^"]+"', "refresh token value"),
    (r'"?client_secret"?\s*[:=]\s*"[^"]+"', "client secret value"),
    (r"-----BEGIN[ A-Z]*PRIVATE KEY-----", "private key value"),
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
    print(f"\nXX v0.7.2-F-R readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print("\nv0.7.2-F-R Queue Task Annotation Final Closeout readiness: ALL PASS")
    sys.exit(0)
