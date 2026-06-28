"""v0.7.2-F-B readiness check: Queue Task Annotation Deriver (read-only helper).

Verifies that the pure / read-only annotation deriver and its unit test exist and
declare the required API, annotation fields, approval_readiness enum, the
decision/execution separation statements, and the safety boundaries — and that
the helper / test source contains no unsafe "enabled / connected" claim, no
secret, and no external-call / side-effect marker.

This script only reads the F-B helper and test source files. It does NOT read
.env, credentials, tokens, or secrets, makes no network call, imports no app
logic, and writes nothing.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
PASS = []
FAIL = []

HELPER_PATH = ROOT / "app" / "queue_task_annotation_v0_7.py"
TEST_PATH = ROOT / "scripts" / "test_queue_task_annotation_readonly_v0_7_2_f_b.py"


def ok(label):
    PASS.append(label)
    print(f"  ok : {label}")


def xx(label):
    FAIL.append(label)
    print(f"  XX : {label}")


# ---------------------------------------------------------------------------
# [1] 檔案存在
# ---------------------------------------------------------------------------
print("[1] F-B 檔案存在")
ok("app/queue_task_annotation_v0_7.py 存在") if HELPER_PATH.exists() else xx("app/queue_task_annotation_v0_7.py 存在")
ok("scripts/test_queue_task_annotation_readonly_v0_7_2_f_b.py 存在") if TEST_PATH.exists() else xx(
    "scripts/test_queue_task_annotation_readonly_v0_7_2_f_b.py 存在"
)
if not HELPER_PATH.exists() or not TEST_PATH.exists():
    print("\nXX F-B 必要檔案缺失，無法繼續")
    sys.exit(1)

helper_src = HELPER_PATH.read_text(encoding="utf-8")
test_src = TEST_PATH.read_text(encoding="utf-8")
combined = helper_src + "\n" + test_src

# ---------------------------------------------------------------------------
# [2] 必須存在的 API / 欄位 / enum / 安全聲明（掃 helper + test）
# ---------------------------------------------------------------------------
print("[2] 必須存在的 API / 欄位 / enum / 安全聲明")
REQUIRED = [
    # public API
    "derive_queue_task_annotation",
    "normalize_approval_readiness",
    # annotation fields
    "task_origin",
    "requested_by",
    "request_channel",
    "owner_reason",
    "approval_readiness",
    "approval_blockers",
    "risk_summary",
    "side_effect_summary",
    "next_step_if_approved",
    "execution_mode",
    "external_touchpoints",
    "dry_run_available",
    "mock_available",
    "rollback_note",
    "human_readable_summary",
    "execution_permission",
    "dispatch_allowed",
    # approval_readiness enum
    "not_ready",
    "owner_review_required",
    "ready_for_owner_decision",
    "blocked_by_policy",
    "prohibited",
    # decision/execution separation
    "Approval readiness is not execution permission",
    "Owner approval does not automatically imply Worker execution",
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
    ok(f"helper/test 含「{token}」") if token in combined else xx(f"helper/test 含「{token}」")

# ---------------------------------------------------------------------------
# [3] execution_permission / dispatch_allowed 必須恆 False（helper 內明確）
# ---------------------------------------------------------------------------
print("[3] execution_permission / dispatch_allowed 恆 False")
ok("helper 設定 execution_permission False") if re.search(
    r'"execution_permission"\s*:\s*False', helper_src
) else xx("helper 設定 execution_permission False")
ok("helper 設定 dispatch_allowed False") if re.search(
    r'"dispatch_allowed"\s*:\s*False', helper_src
) else xx("helper 設定 dispatch_allowed False")

# ---------------------------------------------------------------------------
# [4] 禁止包含的不安全狀態 / 機密 / 外部呼叫 markers（只掃 helper + test）
# ---------------------------------------------------------------------------
print("[4] 禁止包含的不安全狀態 / 機密 / 外部呼叫 markers（helper + test）")
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
]
for token in FORBIDDEN_SUBSTR:
    if token in combined:
        xx(f"helper/test 不得含「{token}」")
    else:
        ok(f"helper/test 無「{token}」")

FORBIDDEN_PATTERNS = [
    (r"https?://", "external URL"),
    (r"spreadsheets/d/[A-Za-z0-9_-]{20,}", "real spreadsheet URL"),
    (r'"?refresh_token"?\s*[:=]\s*"[^"]+"', "refresh token value"),
    (r'"?client_secret"?\s*[:=]\s*"[^"]+"', "client secret value"),
    (r"-----BEGIN[ A-Z]*PRIVATE KEY-----", "private key value"),
]
for pat, label in FORBIDDEN_PATTERNS:
    found = bool(re.search(pat, combined, re.IGNORECASE))
    ok(f"helper/test 無「{label}」") if not found else xx(f"helper/test 不得含「{label}」")

# ---------------------------------------------------------------------------
# [5] import 邊界：helper 不得「實際 import」app.main / QueueStore / worker
#     （只比對 import 陳述句，docstring 內提及邊界的文字不算違規）。
# ---------------------------------------------------------------------------
print("[5] helper import 邊界（pure / read-only）")
FORBIDDEN_IMPORTS = [
    "app.main",
    "app.queue_store",
    "app.worker",
    "app.result_sink",
]
for token in FORBIDDEN_IMPORTS:
    mod = re.escape(token)
    found = bool(
        re.search(rf"^\s*import\s+{mod}\b", helper_src, re.MULTILINE)
        or re.search(rf"^\s*from\s+{mod}\b", helper_src, re.MULTILINE)
    )
    if found:
        xx(f"helper 不得 import「{token}」")
    else:
        ok(f"helper 不 import「{token}」")

# ---------------------------------------------------------------------------
# 結果
# ---------------------------------------------------------------------------
total = len(PASS) + len(FAIL)
print(f"\n合計：{len(PASS)}/{total} 通過")
if FAIL:
    print(f"\nXX v0.7.2-F-B readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print("\nv0.7.2-F-B Queue Task Annotation Deriver readiness: ALL PASS")
    sys.exit(0)
