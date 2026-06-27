"""v0.7.1-C3 — Web Dashboard read-only status badges 單元測試。

純 helper / dict 測試：不啟動 server、不寫 DB、不啟動 worker。
驗證 app.main 的 dashboard 觀測 helper 會帶出 v0.7.1-C view-model（intake_status）。

執行： python scripts/test_web_dashboard_status_badges_v0_7_1_c3.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# 測試 #7：app.main 可 import（不啟動 server）。
from app.main import _obs_task_detail, _obs_task_summary  # noqa: E402

# import app.main 不應啟動 worker。
_NO_WORKER = "app.worker" not in sys.modules

PASSED = 0


def _ok(msg: str) -> None:
    global PASSED
    PASSED += 1
    print(f"  ok: {msg}")


def _assert(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(f"FAIL: {msg}")
    _ok(msg)


def row(*, task_id="t-1", status=None, safety_level=None, metadata=None):
    return {
        "task_id": task_id,
        "status": status,
        "title": "demo",
        "task_text": "demo text",
        "safety_level": safety_level,
        "attempts": 0,
        "max_attempts": 3,
        "error": None,
        "created_at": "2026-06-27T00:00:00Z",
        "updated_at": "2026-06-27T00:00:00Z",
        "payload": json.dumps({"metadata": metadata or {}}),
    }


_VIEW_KEYS = {"source_mode", "intake_mode", "executable_by_worker",
              "approval_status", "risk_level", "safety_level", "display_badges"}


def main() -> int:
    _assert(_NO_WORKER, "import app.main 不會啟動 / 拉進 app.worker")

    print("[1] _obs_task_summary 含 intake_status view 欄位")
    s = _obs_task_summary(row(status="queued", metadata={"mock": True}))
    _assert("intake_status" in s, "_obs_task_summary 含 intake_status")
    _assert(_VIEW_KEYS <= set(s["intake_status"].keys()), "_obs_task_summary.intake_status 含 view 欄位")

    print("[2] _obs_task_detail 含 intake_status view 欄位")
    d = _obs_task_detail(row(task_id="t-detail", status="waiting_review", metadata={"local_only": True}))
    _assert("intake_status" in d, "_obs_task_detail 含 intake_status")
    _assert(_VIEW_KEYS <= set(d["intake_status"].keys()), "_obs_task_detail.intake_status 含 view 欄位")

    print("[3] local-only task → executable_by_worker=false")
    v = _obs_task_summary(row(status="queued", metadata={"local_only": True, "intake_source": "mock-adapter-local"}))["intake_status"]
    _assert(v["executable_by_worker"] == "false", "local-only → executable_by_worker false")
    _assert(v["intake_mode"] == "local-only", "local-only → intake_mode local-only")

    print("[4] mock task → source_mode=mock")
    v = _obs_task_summary(row(status="waiting_review", metadata={"mock": True}))["intake_status"]
    _assert(v["source_mode"] == "mock", "mock → source_mode mock")

    print("[5] queued production-like task → executable_by_worker=true")
    v = _obs_task_summary(row(status="queued", metadata={}))["intake_status"]
    _assert(v["executable_by_worker"] == "true", "queued + 無 local 標記 → executable_by_worker true")

    print("[6] unknown metadata → 保守 unknown")
    v = _obs_task_summary(row(status="running", metadata={}))["intake_status"]
    _assert(v["source_mode"] == "unknown", "空 metadata → source_mode unknown")
    _assert(v["executable_by_worker"] == "unknown", "running + 無標記 → executable_by_worker unknown")

    print("[7] display_badges 為 list（template 迭代用）")
    _assert(isinstance(v["display_badges"], list), "display_badges 為 list")

    print(f"\n✅ test_web_dashboard_status_badges_v0_7_1_c3 全數通過（{PASSED} 項，未啟動 server / worker / 未寫 DB）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
