"""v0.7.4-D read-only test: derive_audit_trail_display_view.

Pure in-memory tests of the audit-trail display helper. Uses only synthetic dicts —
no real queue, no POST, no TestClient, no network, no secrets. Verifies the helper
is read-only (does not mutate input), counts Decision Messages from
payload.metadata.approval_decision_events, keeps Result / Advice Message counts at 0
(future-only), and pins the fixed safety flags to False / read_only True.
"""
import copy
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from app.audit_trail_display_v0_7 import derive_audit_trail_display_view  # noqa: E402

PASS = []
FAIL = []


def check(label, cond):
    (PASS if cond else FAIL).append(label)
    print(f"  {'ok' if cond else 'XX'} : {label}")


# ---------------------------------------------------------------------------
# [1] empty / missing payload 安全
# ---------------------------------------------------------------------------
print("[1] empty / missing payload 安全")
v_empty = derive_audit_trail_display_view({})
check("empty task 不 crash 並回 dict", isinstance(v_empty, dict))
check("empty task decision_message_count = 0", v_empty["decision_message_count"] == 0)
check("empty task task_message_present = False", v_empty["task_message_present"] is False)

v_none_payload = derive_audit_trail_display_view({"task_id": "t1", "payload": None})
check("payload=None 不 crash", isinstance(v_none_payload, dict))
check("payload=None decision count = 0", v_none_payload["decision_message_count"] == 0)

v_str_payload = derive_audit_trail_display_view({"task_id": "t1", "payload": "not-json"})
check("payload 非 JSON 字串 不 crash", v_str_payload["decision_message_count"] == 0)

# ---------------------------------------------------------------------------
# [2] Task Message present
# ---------------------------------------------------------------------------
print("[2] Task Message present")
task = {"task_id": "t1", "status": "queued", "payload": {"metadata": {}}}
v = derive_audit_trail_display_view(task)
check("有 task → task_message_present = True", v["task_message_present"] is True)
check("message_family_counts.task_message = 1", v["message_family_counts"]["task_message"] == 1)

# ---------------------------------------------------------------------------
# [3] Decision Messages 計數
# ---------------------------------------------------------------------------
print("[3] Decision Messages 計數")
task_dec = {
    "task_id": "t2",
    "status": "waiting_review",
    "payload": {
        "metadata": {
            "approval_decision_events": [
                {"decision_id": "d1", "decision_type": "approve"},
                {"decision_id": "d2", "decision_type": "reject"},
            ]
        }
    },
}
v_dec = derive_audit_trail_display_view(task_dec)
check("Decision count = 2", v_dec["decision_message_count"] == 2)
check("message_family_counts.decision_message = 2", v_dec["message_family_counts"]["decision_message"] == 2)
check("有 decision → lifecycle_state = owner_decided", v_dec["lifecycle_state"] == "owner_decided")

# JSON 字串 payload 也要能算
task_json = {
    "task_id": "t3",
    "payload": '{"metadata": {"approval_decision_events": [{"decision_id": "d1"}]}}',
}
v_json = derive_audit_trail_display_view(task_json)
check("JSON 字串 payload decision count = 1", v_json["decision_message_count"] == 1)

# ---------------------------------------------------------------------------
# [4] Result / Advice = 0（future-only）
# ---------------------------------------------------------------------------
print("[4] Result / Advice future-only")
check("Result count = 0", v_dec["result_message_count"] == 0)
check("Advice count = 0", v_dec["advice_message_count"] == 0)
check("message_family_counts.result_message = 0", v_dec["message_family_counts"]["result_message"] == 0)
check("message_family_counts.advice_message = 0", v_dec["message_family_counts"]["advice_message"] == 0)
check(
    "Result future-only marker",
    v_dec["result_message_future_note"] == "Result Message display is future-only in v0.7.4-D.",
)
check(
    "Advice future-only marker",
    v_dec["advice_message_future_note"] == "Advice Message display is future-only in v0.7.4-D.",
)
result_timeline = [t for t in v_dec["timeline_items"] if t["kind"] == "result_message"]
advice_timeline = [t for t in v_dec["timeline_items"] if t["kind"] == "advice_message"]
check("timeline 有 result_message future_only", bool(result_timeline) and result_timeline[0]["future_only"] is True)
check("timeline 有 advice_message future_only", bool(advice_timeline) and advice_timeline[0]["future_only"] is True)

# ---------------------------------------------------------------------------
# [5] 固定安全旗標 / read_only
# ---------------------------------------------------------------------------
print("[5] 固定安全旗標 / read_only")
FIXED_FALSE = [
    "execution_permission",
    "dispatch_allowed",
    "worker_dispatch_enabled",
    "openclaw_call_enabled",
    "hermes_call_enabled",
    "google_sheets_write_enabled",
]
for flag in FIXED_FALSE:
    check(f"{flag} 恆為 False", v_dec[flag] is False)
check("read_only 恆為 True", v_dec["read_only"] is True)

# ---------------------------------------------------------------------------
# [6] 不 mutate 輸入
# ---------------------------------------------------------------------------
print("[6] 不 mutate 輸入")
original = {
    "task_id": "t4",
    "status": "waiting_review",
    "payload": {"metadata": {"approval_decision_events": [{"decision_id": "d1"}]}},
}
snapshot = copy.deepcopy(original)
_ = derive_audit_trail_display_view(original)
check("呼叫後輸入 task 未被 mutate", original == snapshot)

# ---------------------------------------------------------------------------
# [7] malformed approval_decision_events 安全
# ---------------------------------------------------------------------------
print("[7] malformed approval_decision_events 安全")
malformed_cases = [
    {"payload": {"metadata": {"approval_decision_events": "not-a-list"}}},
    {"payload": {"metadata": {"approval_decision_events": None}}},
    {"payload": {"metadata": {"approval_decision_events": 123}}},
    {"payload": {"metadata": "not-a-dict"}},
    {"payload": []},
]
malformed_ok = True
for case in malformed_cases:
    try:
        vc = derive_audit_trail_display_view(case)
        if vc["decision_message_count"] != 0 or vc["read_only"] is not True:
            malformed_ok = False
    except Exception:  # noqa: BLE001
        malformed_ok = False
check("malformed approval_decision_events 全部安全處理（count 0）", malformed_ok)

# ---------------------------------------------------------------------------
# 結果
# ---------------------------------------------------------------------------
total = len(PASS) + len(FAIL)
print(f"\n合計：{len(PASS)}/{total} 通過")
if FAIL:
    print(f"\nXX v0.7.4-D readonly test 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print("\nv0.7.4-D Audit Trail Display read-only test: ALL PASS")
    sys.exit(0)
