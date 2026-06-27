"""v0.7.1-C — Dashboard Intake Status View Model 單元測試（純函式，不寫 DB）。

執行： python scripts/test_dashboard_intake_view_v0_7_1_c.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.dashboard_intake_view_v0_7 import derive_intake_status_view  # noqa: E402

# 測試 #12：import view module 不得拉進 app.main / app.worker。
_IMPORT_SAFE = "app.main" not in sys.modules and "app.worker" not in sys.modules

PASSED = 0


def _ok(msg: str) -> None:
    global PASSED
    PASSED += 1
    print(f"  ok: {msg}")


def _assert(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(f"FAIL: {msg}")
    _ok(msg)


def task(*, status=None, safety_level=None, metadata=None, payload_extra=None,
         payload_as_str=False, **top):
    payload = {"metadata": metadata or {}}
    if payload_extra:
        payload.update(payload_extra)
    row = {"task_id": "t-1", "status": status, "safety_level": safety_level,
           "payload": json.dumps(payload) if payload_as_str else payload}
    row.update(top)
    return row


def main() -> int:
    _assert(_IMPORT_SAFE, "import view module 不會拉進 app.main / app.worker")

    print("[1] metadata.mock=true → source_mode mock")
    v = derive_intake_status_view(task(metadata={"mock": True}))
    _assert(v["source_mode"] == "mock", "mock=true → source_mode mock")

    print("[2] intake_source=mock-adapter-local → source_mode local-only")
    v = derive_intake_status_view(task(metadata={"intake_source": "mock-adapter-local"}))
    _assert(v["source_mode"] == "local-only", "intake_source local → source_mode local-only")

    print("[3] metadata.local_only=true → intake_mode local-only")
    v = derive_intake_status_view(task(metadata={"local_only": True}))
    _assert(v["intake_mode"] == "local-only", "local_only=true → intake_mode local-only")

    print("[4] metadata.executable_by_worker=false → executable_by_worker false")
    v = derive_intake_status_view(task(status="waiting_review", metadata={"executable_by_worker": False}))
    _assert(v["executable_by_worker"] == "false", "explicit executable_by_worker=false → false")

    print("[5] status=waiting_review → executable_by_worker false")
    v = derive_intake_status_view(task(status="waiting_review", metadata={}))
    _assert(v["executable_by_worker"] == "false", "waiting_review → false")

    print("[6] status=queued → true，但 local_only/explicit-false 時不為 true")
    v = derive_intake_status_view(task(status="queued", metadata={}))
    _assert(v["executable_by_worker"] == "true", "queued + 無標記 → true")
    v = derive_intake_status_view(task(status="queued", metadata={"local_only": True}))
    _assert(v["executable_by_worker"] == "false", "queued + local_only=true → 不為 true（false）")
    v = derive_intake_status_view(task(status="queued", metadata={"executable_by_worker": False}))
    _assert(v["executable_by_worker"] == "false", "queued + executable_by_worker=false → false")

    print("[7] local-only 任務永遠不能被推成 executable=true")
    # 連矛盾標記（local_only=true 但 executable_by_worker=true）也必須保守為 false。
    v = derive_intake_status_view(
        task(status="queued", metadata={"local_only": True, "executable_by_worker": True})
    )
    _assert(v["executable_by_worker"] == "false", "local_only + 矛盾 executable=true → 保守 false")
    v = derive_intake_status_view(
        task(status="queued", metadata={"intake_source": "mock-adapter-local"})
    )
    _assert(v["executable_by_worker"] == "false", "local-only source + queued → 仍 false")

    print("[8] unknown metadata → 保守 unknown")
    v = derive_intake_status_view(task(status="some_other_status", metadata={}))
    _assert(v["source_mode"] == "unknown", "空 metadata → source_mode unknown")
    _assert(v["intake_mode"] == "unknown", "空 metadata → intake_mode unknown")
    _assert(v["executable_by_worker"] == "unknown", "未知 status → executable unknown")
    _assert(v["approval_status"] == "unknown", "未知 → approval unknown")

    print("[9] risk_level / safety_level 推導")
    v = derive_intake_status_view(task(metadata={"risk_level": 3}, safety_level=1))
    _assert(v["risk_level"] == 3, "risk_level 優先取 metadata.risk_level")
    v = derive_intake_status_view(task(payload_extra={"risk_level": 2}, safety_level=4))
    _assert(v["risk_level"] == 2, "無 metadata.risk_level → 取 payload.risk_level")
    v = derive_intake_status_view(task(safety_level=4))
    _assert(v["risk_level"] == 4, "都沒有 → 退回 safety_level")
    _assert(v["safety_level"] == 4, "safety_level 原樣帶出")

    print("[10] approval_status 推導")
    v = derive_intake_status_view(task(status="waiting_review", metadata={}))
    _assert(v["approval_status"] == "pending", "waiting_review → approval pending")
    v = derive_intake_status_view(task(status="queued", safety_level=1, metadata={}))
    _assert(v["approval_status"] == "not_required", "queued + safety<=2 → not_required")
    v = derive_intake_status_view(task(status="queued", metadata={"approval_status": "approved"}))
    _assert(v["approval_status"] == "approved", "explicit metadata.approval_status 優先")

    print("[11] view-model 不寫 DB（純函式，輸入不被就地修改）")
    t = task(status="queued", metadata={"mock": True})
    import copy  # noqa: PLC0415
    snapshot = copy.deepcopy(t)
    derive_intake_status_view(t)
    _assert(t == snapshot, "derive_intake_status_view 不修改輸入 task")

    print("[12] payload 為 JSON 字串時也能解析")
    v = derive_intake_status_view(
        task(status="waiting_review", metadata={"mock": True, "local_only": True}, payload_as_str=True)
    )
    _assert(v["source_mode"] in ("mock", "local-only"), "JSON 字串 payload 可解析 metadata")
    _assert(v["executable_by_worker"] == "false", "JSON 字串 payload：local_only → false")

    print(f"\n✅ test_dashboard_intake_view_v0_7_1_c 全數通過（{PASSED} 項，純函式，未寫 DB）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
