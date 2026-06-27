"""v0.7.1-B — Local-only Queue Intake Bridge 單元測試（tempfile DB，純 mock）。

執行： python scripts/test_queue_intake_bridge_v0_7_1_b.py

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

# 測試 #9：import bridge 後不得把 app.worker / app.main 拉進來。
_IMPORT_SAFE = "app.worker" not in sys.modules and "app.main" not in sys.modules

PASSED = 0
INTAKE_FLAGS = (
    "QUEUE_INTAKE_ENABLED",
    "INTAKE_KILL_SWITCH",
    "INTAKE_ALLOWED_TASK_TYPES",
    "INTAKE_QUEUE_DB_PATH",
)


def _ok(msg: str) -> None:
    global PASSED
    PASSED += 1
    print(f"  ok: {msg}")


def _assert(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(f"FAIL: {msg}")
    _ok(msg)


def _clear_flags() -> None:
    for k in INTAKE_FLAGS:
        os.environ.pop(k, None)


def mock_request(**overrides) -> dict:
    base = {
        "request_id": "mock-intake-001",
        "requested_by": "owner",
        "intent": "summarize",
        "goal": "Summarize a mock document",
        "task_type": "mock.summarize",
        "risk_level": 0,
        "approval_required": False,
        "input_summary": "Mock input only",
        "target_runtime": "mock",
        "target_workspace": "local",
        "priority": "normal",
        "metadata": {"mock": True},
    }
    base.update(overrides)
    return base


def main() -> int:
    _assert(_IMPORT_SAFE, "import bridge 不會拉進 app.worker / app.main")

    envelope = prepare_queue_candidate_from_mock_request(mock_request())
    tmp = Path(tempfile.mkdtemp(prefix="intake_bridge_"))
    db = str(tmp / "intake_local_test.db")

    print("[1] 預設 QUEUE_INTAKE_ENABLED=false → 不寫 DB")
    _clear_flags()
    r = intake_task_envelope_local_only(envelope, db_path=db)
    _assert(r["accepted"] is False and r["written"] is False, "預設 disabled → accepted/written False")
    _assert(r["reason"] == "intake_disabled", "預設 disabled → reason intake_disabled")
    _assert(not Path(db).exists(), "預設 disabled → 未建立任何 DB 檔")

    print("[2] INTAKE_KILL_SWITCH=true → 拒絕（優先於 enabled）")
    _clear_flags()
    os.environ["QUEUE_INTAKE_ENABLED"] = "true"
    os.environ["INTAKE_KILL_SWITCH"] = "true"
    os.environ["INTAKE_ALLOWED_TASK_TYPES"] = "mock.summarize"
    r = intake_task_envelope_local_only(envelope, db_path=db)
    _assert(r["written"] is False and r["reason"] == "kill_switch_active", "kill switch → 拒絕，未寫入")

    print("[3] allowlist 空 → 拒絕")
    _clear_flags()
    os.environ["QUEUE_INTAKE_ENABLED"] = "true"
    os.environ["INTAKE_ALLOWED_TASK_TYPES"] = ""
    r = intake_task_envelope_local_only(envelope, db_path=db)
    _assert(r["written"] is False and r["reason"] == "task_type_not_allowlisted",
            "allowlist 空 → 拒絕，未寫入")
    _assert(not Path(db).exists(), "拒絕情況下仍未建立 DB 檔")

    print("[4] allowlist 含 task_type 且 enabled=true → 寫入 tempfile DB")
    _clear_flags()
    os.environ["QUEUE_INTAKE_ENABLED"] = "true"
    os.environ["INTAKE_ALLOWED_TASK_TYPES"] = "mock.summarize,other.type"
    r = intake_task_envelope_local_only(envelope, db_path=db)
    _assert(r["accepted"] is True and r["written"] is True, "enabled+allowlisted → 寫入成功")
    _assert(Path(db).exists(), "寫入後 tempfile DB 檔存在")
    _assert(r["db_path"] == db, "db_path 為傳入的 tempfile 路徑（非 production）")

    print("[5] 寫入狀態必須是 waiting_review")
    _assert(r["initial_status"] == WAITING_REVIEW, "intake 回傳 initial_status=waiting_review")
    store = QueueStore(db)
    row = store.get(envelope["task_id"])
    _assert(row is not None and row["status"] == WAITING_REVIEW, "DB 內任務 status=waiting_review")

    print("[6] 不得產生 queued 任務")
    counts = store.counts()
    _assert(counts.get(QUEUED, 0) == 0, "DB 內沒有任何 queued 任務")
    _assert(r["executable_by_worker"] is False, "回傳 executable_by_worker=False")

    print("[7] claim_next 不應 claim waiting_review 任務")
    claimed = store.claim_next()
    _assert(claimed is None, "claim_next 對 waiting_review 任務回傳 None（worker 不會執行）")
    # claim_next 後狀態仍為 waiting_review（未被改成 running）
    _assert(store.get(envelope["task_id"])["status"] == WAITING_REVIEW,
            "claim_next 後任務仍是 waiting_review")

    print("[8] metadata / payload 標示 local_only / executable_by_worker=false")
    payload = json.loads(store.get(envelope["task_id"])["payload"])
    md = payload.get("metadata", {})
    _assert(md.get("local_only") is True, "payload.metadata.local_only=true")
    _assert(md.get("executable_by_worker") is False, "payload.metadata.executable_by_worker=false")
    _assert(md.get("intake_source") == "mock-adapter-local", "payload.metadata.intake_source 標示 local")
    _assert(payload.get("status") != "queued", "payload.status 不是 queued")

    print("[9] / [10] import / 外部呼叫安全")
    _ok("已驗證未 import app.worker / app.main（見開頭）")
    bridge_src = (Path(__file__).resolve().parent.parent / "app" / "queue_intake_bridge_v0_7.py").read_text(encoding="utf-8")
    # 檢查實際「呼叫」痕跡，而非 docstring 安全說明中提到的字樣。
    _assert("run_openclaw_cli(" not in bridge_src, "bridge 原始碼未呼叫 run_openclaw_cli()")
    _assert("googleapiclient" not in bridge_src and "import google" not in bridge_src,
            "bridge 原始碼未 import Google client")

    _clear_flags()
    print(f"\n✅ test_queue_intake_bridge_v0_7_1_b 全數通過（{PASSED} 項，tempfile DB，未接任何真系統）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
