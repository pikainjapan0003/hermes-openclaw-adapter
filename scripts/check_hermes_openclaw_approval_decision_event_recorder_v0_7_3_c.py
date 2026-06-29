"""v0.7.3-C readiness check: Local Approval Event Recorder.

Verifies the local append-only Owner approval decision event recorder: the doc,
the pure recorder helper, and the test script exist; app/main.py wires the
recorder into the existing Owner decision routes; the QueueStore narrow append
method exists; the required safety / append-only / fixed-False markers and the
decision/execution separation statements are present; the existing decision
route paths are preserved — and that the recorder surfaces (helper + doc + test +
queue_store) contain no unsafe "enabled / connected / execution-granting /
dispatch / external" claim and no secret.

This script only reads the F-3-C recorder surfaces and wiring. It does NOT read
.env, credentials, tokens, or secrets, makes no network call, imports no app
logic (no app.main, no QueueStore), starts no Worker, and calls no OpenClaw /
Hermes / Google Sheets.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
PASS = []
FAIL = []

HELPER_PATH = ROOT / "app" / "approval_decision_event_recorder_v0_7.py"
DOC_PATH = ROOT / "docs" / "HERMES_OPENCLAW_APPROVAL_DECISION_EVENT_RECORDER_V0_7_3_C.md"
MAIN_PATH = ROOT / "app" / "main.py"
QUEUE_PATH = ROOT / "app" / "queue_store.py"
TEST_PATH = ROOT / "scripts" / "test_approval_decision_event_recorder_local_appendonly_v0_7_3_c.py"


def ok(label):
    PASS.append(label)
    print(f"  ok : {label}")


def xx(label):
    FAIL.append(label)
    print(f"  XX : {label}")


# ---------------------------------------------------------------------------
# [1] 必要檔案存在
# ---------------------------------------------------------------------------
print("[1] v0.7.3-C 必要檔案存在")
required_files = {
    "app/approval_decision_event_recorder_v0_7.py": HELPER_PATH,
    "docs/HERMES_OPENCLAW_APPROVAL_DECISION_EVENT_RECORDER_V0_7_3_C.md": DOC_PATH,
    "app/main.py": MAIN_PATH,
    "app/queue_store.py": QUEUE_PATH,
    "scripts/test_approval_decision_event_recorder_local_appendonly_v0_7_3_c.py": TEST_PATH,
}
missing = False
for label, path in required_files.items():
    if path.exists():
        ok(f"{label} 存在")
    else:
        xx(f"{label} 存在")
        missing = True
if missing:
    print("\nXX v0.7.3-C 必要檔案缺失，無法繼續")
    sys.exit(1)

helper_src = HELPER_PATH.read_text(encoding="utf-8")
doc_src = DOC_PATH.read_text(encoding="utf-8")
main_src = MAIN_PATH.read_text(encoding="utf-8")
queue_src = QUEUE_PATH.read_text(encoding="utf-8")
test_src = TEST_PATH.read_text(encoding="utf-8")

positive = "\n".join([doc_src, helper_src, main_src, queue_src, test_src])
# 禁止字掃描：不掃 main.py（既有 worker/callback 程式碼）。
recorder_surfaces = "\n".join([helper_src, doc_src, queue_src, test_src])

# ---------------------------------------------------------------------------
# [2] 必須包含的 markers
# ---------------------------------------------------------------------------
print("[2] 必須包含的 markers")
REQUIRED = [
    "v0.7.3-C",
    "Local Approval Event Recorder",
    "append-only",
    "local metadata",
    "payload.metadata.approval_decision_events",
    "approve is not execute",
    "Owner decision event is not Worker dispatch",
    "Owner approval does not automatically imply Worker execution",
    "Decision and execution dispatch remain separate",
    "Approval readiness is not execution permission",
    "execution_permission_at_decision = False",
    "dispatch_allowed_at_decision = False",
    "No Worker execution",
    "No OpenClaw call",
    "No Hermes call",
    "No Google Sheets write",
    "No external side effects",
    "No --apply",
    "No demo task cleanup",
    "No seed demo task",
    "No secrets read",
    "No webhook",
]
for token in REQUIRED:
    ok(f"含「{token}」") if token in positive else xx(f"含「{token}」")

# ---------------------------------------------------------------------------
# [3] recorder helper API + 固定 False
# ---------------------------------------------------------------------------
print("[3] recorder helper API + 固定 False")
ok("helper 提供 build_approval_decision_event") if re.search(
    r"def\s+build_approval_decision_event\s*\(", helper_src
) else xx("helper 提供 build_approval_decision_event")
ok("helper 提供 append_approval_decision_event_to_payload") if re.search(
    r"def\s+append_approval_decision_event_to_payload\s*\(", helper_src
) else xx("helper 提供 append_approval_decision_event_to_payload")
ok("helper 設定 execution_permission_at_decision False") if re.search(
    r'"execution_permission_at_decision"\s*:\s*False', helper_src
) else xx("helper 設定 execution_permission_at_decision False")
ok("helper 設定 dispatch_allowed_at_decision False") if re.search(
    r'"dispatch_allowed_at_decision"\s*:\s*False', helper_src
) else xx("helper 設定 dispatch_allowed_at_decision False")
# helper import 邊界（只比對 import 陳述句）。
for token in ("app.main", "app.queue_store", "app.worker"):
    mod = re.escape(token)
    found = bool(
        re.search(rf"^\s*import\s+{mod}\b", helper_src, re.MULTILINE)
        or re.search(rf"^\s*from\s+{mod}\b", helper_src, re.MULTILINE)
    )
    xx(f"helper 不得 import「{token}」") if found else ok(f"helper 不 import「{token}」")

# ---------------------------------------------------------------------------
# [4] app/main.py local recorder wiring
# ---------------------------------------------------------------------------
print("[4] app/main.py local recorder wiring")
ok("main.py import build_approval_decision_event") if re.search(
    r"from app\.approval_decision_event_recorder_v0_7 import build_approval_decision_event", main_src
) else xx("main.py import build_approval_decision_event")
ok("main.py 定義 _record_owner_decision") if re.search(
    r"def\s+_record_owner_decision\s*\(", main_src
) else xx("main.py 定義 _record_owner_decision")
ok("main.py 呼叫 _record_owner_decision") if main_src.count("_record_owner_decision(") >= 4 else xx(
    "main.py 在多個 decision route 呼叫 _record_owner_decision"
)

# ---------------------------------------------------------------------------
# [5] QueueStore narrow append method
# ---------------------------------------------------------------------------
print("[5] QueueStore narrow append method")
ok("queue_store 新增 append_approval_decision_event") if re.search(
    r"def\s+append_approval_decision_event\s*\(", queue_src
) else xx("queue_store 新增 append_approval_decision_event")

# ---------------------------------------------------------------------------
# [6] route paths 仍保留（POST decision routes）
# ---------------------------------------------------------------------------
print("[6] route paths 仍保留")
for route in (
    '"/dashboard/tasks/{task_id}/approve"',
    '"/dashboard/tasks/{task_id}/reject"',
    '"/dashboard/tasks/{task_id}/cancel"',
    '"/dashboard/tasks/{task_id}/retry"',
    '"/dashboard/tasks/{task_id}/archive"',
):
    ok(f"main.py 保留 route {route}") if route in main_src else xx(f"main.py 保留 route {route}")

# ---------------------------------------------------------------------------
# [7] 禁止包含的不安全聲明 / 機密（recorder surfaces，不掃 main.py）
# ---------------------------------------------------------------------------
print("[7] 禁止包含的不安全聲明 / 機密")
FORBIDDEN_SUBSTR = [
    "GOOGLE_SHEETS_ENABLED=true",
    "Worker enabled",
    "OpenClaw connected",
    "Hermes connected",
    "Google Sheets live write enabled",
    "execution_permission_at_decision = True",
    "dispatch_allowed_at_decision = True",
    "execution_permission = True",
    "dispatch_allowed = True",
    "Owner approval triggers Worker execution",
    "approve triggers dispatch",
    "approve calls OpenClaw",
    "approve calls Hermes",
    "approve writes Google Sheets",
    "decision event dispatches Worker",
    "POST to Replit Preview",
    "clicked approve",
    "clicked reject",
    "clicked cancel",
    "clicked retry",
    "clicked archive",
    "demo task cleaned up",
    "seeded demo task",
]
for token in FORBIDDEN_SUBSTR:
    xx(f"recorder surfaces 不得含「{token}」") if token in recorder_surfaces else ok(f"recorder surfaces 無「{token}」")

FORBIDDEN_PATTERNS = [
    (r"spreadsheets/d/[A-Za-z0-9_-]{20,}", "real spreadsheet URL"),
    (r'"?refresh_token"?\s*[:=]\s*"[^"]+"', "refresh token value"),
    (r'"?client_secret"?\s*[:=]\s*"[^"]+"', "client secret value"),
    (r"-----BEGIN[ A-Z]*PRIVATE KEY-----", "private key value"),
]
for pat, label in FORBIDDEN_PATTERNS:
    found = bool(re.search(pat, recorder_surfaces, re.IGNORECASE))
    ok(f"recorder surfaces 無「{label}」") if not found else xx(f"recorder surfaces 不得含「{label}」")

# ---------------------------------------------------------------------------
# [8] recorder helper 不新增外部呼叫 / webhook
# ---------------------------------------------------------------------------
print("[8] recorder helper 不新增外部呼叫 / webhook")
for token in ("requests.", "httpx.", "urllib.request", "socket.", "webhook", "subprocess", "Popen"):
    xx(f"helper 不得含「{token}」") if token in helper_src else ok(f"helper 無「{token}」")

# ---------------------------------------------------------------------------
# 結果
# ---------------------------------------------------------------------------
total = len(PASS) + len(FAIL)
print(f"\n合計：{len(PASS)}/{total} 通過")
if FAIL:
    print(f"\nXX v0.7.3-C readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print("\nv0.7.3-C Local Approval Event Recorder readiness: ALL PASS")
    sys.exit(0)
