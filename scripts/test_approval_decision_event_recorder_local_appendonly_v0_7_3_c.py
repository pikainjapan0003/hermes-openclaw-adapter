#!/usr/bin/env python3
"""v0.7.3-C — Local Approval Event Recorder 測試（純函式 append-only + 本地 route append）。

純函式涵蓋：build event / append-only / immutability / 固定安全值 / import 邊界。
本地 route 涵蓋：透過 FastAPI TestClient 以 temp SQLite 驗證既有 decision route 會 append
event、status transition 不變、無 worker thread、無 results.jsonl。

禁止對 Replit Preview 或真實 queue 送 POST；只在 temp DATA_DIR / temp QUEUE_DB_PATH 內測試。

執行： python scripts/test_approval_decision_event_recorder_local_appendonly_v0_7_3_c.py
"""

from __future__ import annotations

import copy
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# 先 import 純 helper，確認不會拉進 app.main / app.queue_store / app.worker。
from app.approval_decision_event_recorder_v0_7 import (  # noqa: E402
    append_approval_decision_event_to_payload,
    build_approval_decision_event,
)

_IMPORT_SAFE = (
    "app.main" not in sys.modules
    and "app.queue_store" not in sys.modules
    and "app.worker" not in sys.modules
)

PASSED = 0
FAILURES: list[str] = []


def _check(cond: bool, label: str) -> None:
    global PASSED
    if cond:
        PASSED += 1
        print(f"  ok: {label}")
    else:
        print(f"  ❌ FAIL: {label}")
        FAILURES.append(label)


def _pure_tests() -> None:
    print("[1] empty payload metadata append → 產生 approval_decision_events list")
    task = {"task_id": "t-1", "payload": {"metadata": {}}, "safety_level": 3}
    ev = build_approval_decision_event(
        task, decision_type="approve", previous_status="waiting_review", next_status="queued"
    )
    new_payload = append_approval_decision_event_to_payload(task["payload"], ev)
    events = new_payload["metadata"]["approval_decision_events"]
    _check(isinstance(events, list) and len(events) == 1, "empty → 1 event appended")

    print("[2] existing events 保留，新 event append 到尾端")
    payload2 = {"metadata": {"approval_decision_events": [{"decision_id": "old-1"}], "keep": "me"}}
    ev2 = build_approval_decision_event(
        {"task_id": "t-2", "payload": payload2}, decision_type="reject",
        previous_status="waiting_review", next_status="rejected",
    )
    out2 = append_approval_decision_event_to_payload(payload2, ev2)
    evs2 = out2["metadata"]["approval_decision_events"]
    _check(len(evs2) == 2, "existing + new → 2 events")
    _check(evs2[0]["decision_id"] == "old-1", "舊 event 保留在前")
    _check(evs2[1]["decision_type"] == "reject", "新 event append 到尾端")

    print("[3] copy-on-write：不 mutate 輸入 payload / metadata")
    snapshot = copy.deepcopy(payload2)
    append_approval_decision_event_to_payload(payload2, ev2)
    _check(payload2 == snapshot, "append 不 mutate 輸入 payload")

    print("[4] unrelated metadata 保留")
    _check(out2["metadata"].get("keep") == "me", "unrelated metadata（keep）保留")

    print("[5/6] execution_permission_at_decision / dispatch_allowed_at_decision 恆 False")
    _check(ev["execution_permission_at_decision"] is False, "execution_permission_at_decision False")
    _check(ev["dispatch_allowed_at_decision"] is False, "dispatch_allowed_at_decision False")
    # 即使 metadata 來源宣稱 True 也不影響（build 固定 False）。
    _check(evs2[1]["execution_permission_at_decision"] is False, "appended event execution False")
    _check(evs2[1]["dispatch_allowed_at_decision"] is False, "appended event dispatch False")

    print("[7] decision_id 存在且非空")
    _check(isinstance(ev["decision_id"], str) and len(ev["decision_id"]) > 0, "decision_id 非空")

    print("[8] decided_at 像 UTC timestamp")
    _check(isinstance(ev["decided_at"], str) and "T" in ev["decided_at"] and ev["decided_at"].endswith("Z"),
           "decided_at 為 UTC ISO（…Z）")

    print("[9] safety_snapshot / annotation_snapshot / audit_record 是 dict")
    _check(isinstance(ev["safety_snapshot"], dict), "safety_snapshot 是 dict")
    _check(isinstance(ev["annotation_snapshot"], dict), "annotation_snapshot 是 dict")
    _check(isinstance(ev["audit_record"], dict), "audit_record 是 dict")
    _check("token" not in str(ev["audit_record"]).lower() and "secret" not in str(ev["audit_record"]).lower(),
           "audit_record 不含 token / secret 字樣")

    print("[10] helper 不 import app.main / QueueStore / worker")
    _check(_IMPORT_SAFE, "import recorder 不會拉進 app.main / app.queue_store / app.worker")

    print("[10b] JSON 字串 payload / None 也能 append（不 crash）")
    import json as _json  # noqa: PLC0415
    out_js = append_approval_decision_event_to_payload(
        _json.dumps({"metadata": {"x": 1}}), ev
    )
    _check(out_js["metadata"]["x"] == 1 and len(out_js["metadata"]["approval_decision_events"]) == 1,
           "JSON 字串 payload → 解析並 append")
    out_none = append_approval_decision_event_to_payload(None, ev)
    _check(len(out_none["metadata"]["approval_decision_events"]) == 1, "None payload → append（不 crash）")


def _route_tests() -> None:
    print("[11-14] 本地 TestClient（temp SQLite）：既有 decision route append event、不改 transition")
    tmp = tempfile.mkdtemp(prefix="fc3_recorder_test_")
    os.environ["EXECUTION_MODE"] = "queue"
    os.environ["DATA_DIR"] = tmp
    os.environ["QUEUE_DB_PATH"] = str(Path(tmp) / "queue.db")
    os.environ["HERMES_ADAPTER_TOKEN"] = ""
    os.environ["CALLBACK_ENABLED"] = "false"
    os.environ["OPENCLAW_CLI_BIN"] = "/nonexistent/openclaw-should-never-be-called"
    dash_token = "f-3-c-recorder-test-token"
    os.environ["DASHBOARD_AUTH_ENABLED"] = "true"
    os.environ["DASHBOARD_TOKEN"] = dash_token

    from fastapi.testclient import TestClient  # noqa: PLC0415
    from app import main  # noqa: PLC0415

    q = main.get_queue()
    q.enqueue(
        task_id="fc3-approve-task",
        title="DEMO approve recorder",
        task_text="local append-only recorder test",
        safety_level=3,
        payload={"metadata": {"requires_confirmation": True}},
        initial_status="waiting_review",
    )

    client = TestClient(main.app)
    client.headers.update({"X-Dashboard-Token": dash_token})

    # POST approve（本地 temp queue；不是 Replit / 真實 queue）。
    r = client.post("/dashboard/tasks/fc3-approve-task/approve", follow_redirects=False)
    _check(r.status_code in (302, 303), "approve POST → redirect（PRG）")

    task_after = q.get("fc3-approve-task")
    _check(task_after["status"] == "queued", "approve status transition 結果不變（waiting_review → queued）")

    view = main.derive_approval_decision_event_view(task_after)
    _check(view["has_events"] is True and view["event_count"] == 1, "route append 出 1 筆 decision event")
    ev = view["events"][0]
    _check(ev["decision_type"] == "approve", "event decision_type=approve")
    _check(ev["previous_status"] == "waiting_review" and ev["next_status"] == "queued", "event 狀態轉換正確")
    _check(ev["execution_permission_at_decision"] is False, "route event execution_permission False")
    _check(ev["dispatch_allowed_at_decision"] is False, "route event dispatch_allowed False")

    # 第二筆 decision（cancel queued task）→ append-only 第二筆。
    r2 = client.post("/dashboard/tasks/fc3-approve-task/cancel", follow_redirects=False)
    _check(r2.status_code in (302, 303), "cancel POST → redirect")
    task_after2 = q.get("fc3-approve-task")
    _check(task_after2["status"] == "cancelled", "cancel status transition 結果不變（queued → cancelled）")
    view2 = main.derive_approval_decision_event_view(task_after2)
    _check(view2["event_count"] == 2, "append-only：第二筆 event 累積（共 2 筆）")
    _check(view2["events"][0]["decision_type"] == "approve", "舊 approve event 保留")
    _check(view2["events"][1]["decision_type"] == "cancel", "新 cancel event append 到尾端")

    print("[13/14] 不產生 results.jsonl / 沒有 worker thread")
    import threading  # noqa: PLC0415
    _check(not [t for t in threading.enumerate() if "worker" in t.name.lower()], "沒有 worker 執行緒")
    _check(not (Path(tmp) / "results.jsonl").exists(), "沒有 results.jsonl（未執行 OpenClaw）")


def main_test() -> int:
    _pure_tests()
    _route_tests()
    if FAILURES:
        print(f"\n❌ v0.7.3-C recorder 測試失敗 {len(FAILURES)} 項：")
        for f in FAILURES:
            print(f"   - {f}")
        return 1
    print(f"\n✅ test_approval_decision_event_recorder_local_appendonly_v0_7_3_c 全數通過（{PASSED} 項，local append-only）。")
    return 0


if __name__ == "__main__":
    sys.exit(main_test())
