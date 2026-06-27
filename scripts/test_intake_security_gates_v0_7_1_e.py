"""v0.7.1-E — Local-only Intake Security Gates wiring 單元測試（tempfile DB，純 mock）。

執行： python scripts/test_intake_security_gates_v0_7_1_e.py

使用 tempfile DB，絕不碰 data/queue.db；不接真系統、不啟動 worker。
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.mock_adapter_v0_7 import prepare_queue_candidate_from_mock_request  # noqa: E402
from app.queue_intake_bridge_v0_7 import intake_task_envelope_local_only  # noqa: E402
from app.queue_store import QUEUED, WAITING_REVIEW, QueueStore  # noqa: E402

# 測試 #17：import bridge 不得拉進 app.main / app.worker。
_IMPORT_SAFE = "app.main" not in sys.modules and "app.worker" not in sys.modules

ENV_FLAGS = (
    "QUEUE_INTAKE_ENABLED", "INTAKE_KILL_SWITCH", "GLOBAL_KILL_SWITCH",
    "INTAKE_SECURITY_GATES_ENABLED", "INTAKE_ALLOWED_TASK_TYPES",
    "INTAKE_QUEUE_DB_PATH", "QUEUE_DB_PATH",
)

PASSED = 0


def _ok(msg: str) -> None:
    global PASSED
    PASSED += 1
    print(f"  ok: {msg}")


def _assert(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(f"FAIL: {msg}")
    _ok(msg)


def _set(**flags) -> None:
    for k in ENV_FLAGS:
        os.environ.pop(k, None)
    for k, v in flags.items():
        os.environ[k] = v


def envelope(*, allowed_tools=None, denied_tools=None, requested_tools="__omit__", task_type="mock.summarize"):
    req = {
        "request_id": "mock-e-001", "requested_by": "owner", "intent": "summarize",
        "goal": "g", "task_type": task_type, "risk_level": 0, "approval_required": False,
        "input_summary": "s", "target_runtime": "mock", "target_workspace": "local",
        "priority": "normal", "metadata": {"mock": True},
    }
    env = prepare_queue_candidate_from_mock_request(req)
    if allowed_tools is not None:
        env["allowed_tools"] = allowed_tools
    if denied_tools is not None:
        env["denied_tools"] = denied_tools
    if requested_tools != "__omit__":
        env["metadata"]["requested_tools"] = requested_tools
    return env


def main() -> int:
    _assert(_IMPORT_SAFE, "import bridge 未拉進 app.main / app.worker")

    tmp = Path(tempfile.mkdtemp(prefix="intake_gate_"))
    db = str(tmp / "intake.db")

    print("[1] gates disabled → 既有 v0.7.1-B happy path 仍寫入 waiting_review")
    _set(QUEUE_INTAKE_ENABLED="true", INTAKE_ALLOWED_TASK_TYPES="mock.summarize")
    r = intake_task_envelope_local_only(envelope(), db_path=db)
    _assert(r["written"] is True and r["initial_status"] == WAITING_REVIEW, "disabled gate → B 行為寫入 waiting_review")

    print("[2] gate enabled + missing metadata.requested_tools → reject 不寫")
    db2 = str(tmp / "g2.db")
    _set(QUEUE_INTAKE_ENABLED="true", INTAKE_ALLOWED_TASK_TYPES="mock.summarize",
         INTAKE_SECURITY_GATES_ENABLED="true")
    r = intake_task_envelope_local_only(envelope(allowed_tools=["read"]), db_path=db2)
    _assert(r["written"] is False and r["reason"] == "security_gate_rejected", "missing requested_tools → reject")
    _assert(not Path(db2).exists(), "reject 未建立 DB 檔")

    print("[3] requested_tools 空 list → reject")
    r = intake_task_envelope_local_only(envelope(allowed_tools=["read"], requested_tools=[]), db_path=db2)
    _assert(r["written"] is False and r["reason"] == "security_gate_rejected", "empty requested_tools → reject")

    print("[4] requested_tools 非 list[str] → reject")
    r = intake_task_envelope_local_only(envelope(allowed_tools=["read"], requested_tools="read"), db_path=db2)
    _assert(r["written"] is False and r["reason"] == "security_gate_rejected", "string requested_tools → reject")

    print("[5] allowed_tools 缺失 → reject")
    r = intake_task_envelope_local_only(envelope(requested_tools=["read"]), db_path=db2)
    _assert(r["written"] is False and r["reason"] == "security_gate_rejected", "missing allowed_tools → reject")

    print("[6] denied_tools 命中 → reject")
    r = intake_task_envelope_local_only(
        envelope(allowed_tools=["read"], denied_tools=["read"], requested_tools=["read"]), db_path=db2)
    _assert(r["written"] is False and r["security_gate"]["priority"] == "denylist", "denied_tools 命中 → reject (denylist)")

    print("[7] requested tool 不在 allowed_tools → reject")
    r = intake_task_envelope_local_only(
        envelope(allowed_tools=["read"], requested_tools=["write"]), db_path=db2)
    _assert(r["written"] is False and r["reason"] == "security_gate_rejected", "tool 不在 allowlist → reject")

    print("[8] invalid tool name → reject")
    r = intake_task_envelope_local_only(
        envelope(allowed_tools=["bad tool!"], requested_tools=["bad tool!"]), db_path=db2)
    _assert(r["written"] is False and r["reason"] == "security_gate_rejected", "invalid tool name → reject")

    print("[9] allowed 且未 denied → 成功寫入 waiting_review")
    db9 = str(tmp / "g9.db")
    r = intake_task_envelope_local_only(
        envelope(allowed_tools=["read", "list"], denied_tools=["delete"], requested_tools=["read"]), db_path=db9)
    _assert(r["written"] is True and r["initial_status"] == WAITING_REVIEW, "gate pass → 寫入 waiting_review")

    print("[10] GLOBAL_KILL_SWITCH=true → reject 不寫")
    dbk = str(tmp / "gk.db")
    _set(QUEUE_INTAKE_ENABLED="true", INTAKE_ALLOWED_TASK_TYPES="mock.summarize",
         INTAKE_SECURITY_GATES_ENABLED="true", GLOBAL_KILL_SWITCH="true")
    r = intake_task_envelope_local_only(
        envelope(allowed_tools=["read"], requested_tools=["read"]), db_path=dbk)
    _assert(r["written"] is False and r["reason"] == "global_kill_switch_active", "global kill switch → reject")
    _assert(not Path(dbk).exists(), "global kill → 未建 DB")

    print("[11] INTAKE_KILL_SWITCH=true → reject 不寫（優先）")
    _set(QUEUE_INTAKE_ENABLED="true", INTAKE_ALLOWED_TASK_TYPES="mock.summarize",
         INTAKE_SECURITY_GATES_ENABLED="true", INTAKE_KILL_SWITCH="true")
    r = intake_task_envelope_local_only(
        envelope(allowed_tools=["read"], requested_tools=["read"]), db_path=dbk)
    _assert(r["written"] is False and r["reason"] == "kill_switch_active", "layer kill switch → reject")

    print("[12] task_type allowlist 仍生效")
    _set(QUEUE_INTAKE_ENABLED="true", INTAKE_ALLOWED_TASK_TYPES="other.type",
         INTAKE_SECURITY_GATES_ENABLED="true")
    r = intake_task_envelope_local_only(
        envelope(allowed_tools=["read"], requested_tools=["read"]), db_path=dbk)
    _assert(r["written"] is False and r["reason"] == "task_type_not_allowlisted", "task_type allowlist 仍擋")

    print("[13] production DB path guard 仍生效")
    prod = str(tmp / "prod_queue.db")
    _set(QUEUE_INTAKE_ENABLED="true", INTAKE_ALLOWED_TASK_TYPES="mock.summarize",
         INTAKE_SECURITY_GATES_ENABLED="true", QUEUE_DB_PATH=prod)
    r = intake_task_envelope_local_only(
        envelope(allowed_tools=["read"], requested_tools=["read"]), db_path=prod)
    _assert(r["written"] is False and r["reason"] == "refuse_production_db", "撞 production DB → reject")
    _assert(not Path(prod).exists(), "production DB 未被建立")

    print("[14]/[15] 成功寫入的 payload / status 不變式")
    store = QueueStore(db9)
    row = store.get(envelope()["task_id"]) if False else None  # task_id 每次不同，改用列出
    rows, _ = store.list_page(limit=10, offset=0)
    _assert(len(rows) == 1 and rows[0]["status"] == WAITING_REVIEW, "成功列 status=waiting_review")
    payload = json.loads(rows[0]["payload"])
    md = payload.get("metadata", {})
    _assert(md.get("local_only") is True and md.get("mock") is True
            and md.get("executable_by_worker") is False, "payload metadata local_only/mock/executable_by_worker=false")
    _assert(payload.get("status") != "queued", "payload status 不是 queued")
    _assert(store.counts().get(QUEUED, 0) == 0, "DB 內無 queued 任務")

    print("[16] claim_next 不 claim waiting_review")
    _assert(store.claim_next() is None, "claim_next 對 waiting_review 回 None")

    print("[17]/[18] bridge import / 呼叫安全")
    _ok("已驗證未 import app.main / app.worker（見開頭）")
    src = (Path(__file__).resolve().parent.parent / "app" / "queue_intake_bridge_v0_7.py").read_text(encoding="utf-8")
    _assert("run_openclaw_cli(" not in src, "bridge 未呼叫 run_openclaw_cli()")
    _assert("googleapiclient" not in src and "import google" not in src, "bridge 未 import Google client")

    _set()
    print(f"\n✅ test_intake_security_gates_v0_7_1_e 全數通過（{PASSED} 項，tempfile DB，未接真系統）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
