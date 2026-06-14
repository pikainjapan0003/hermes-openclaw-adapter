"""QueueStore 單元 smoke test（不需 OpenClaw / FastAPI）。

執行： python scripts/test_queue_store.py
驗證：enqueue → claim_next（running, attempts+1）→ completed / requeue / failed /
      cancel / reset_stale_running 全部行為正確。
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.queue_store import (  # noqa: E402
    CANCELLED, COMPLETED, FAILED, QUEUED, RUNNING, QueueStore,
)


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(f"FAIL: {msg}")
    print(f"  ok: {msg}")


def main() -> int:
    tmp = tempfile.mkdtemp(prefix="queue_smoke_")
    db = Path(tmp) / "queue.db"
    q = QueueStore(db)

    print("[1] enqueue 兩筆")
    q.enqueue(task_id="t1", title="A", task_text="do A", safety_level=0,
              payload={"title": "A", "goal": "g", "task_text": "do A"}, max_attempts=2)
    q.enqueue(task_id="t2", title="B", task_text="do B", safety_level=1,
              payload={"title": "B", "goal": "g", "task_text": "do B"}, max_attempts=2)
    _check(q.get("t1")["status"] == QUEUED, "t1 為 queued")
    _check(q.counts().get(QUEUED) == 2, "兩筆 queued")

    print("[2] claim_next → 最舊的 t1 變 running、attempts=1")
    c = q.claim_next()
    _check(c["task_id"] == "t1", "先領到 t1（FIFO）")
    _check(c["status"] == RUNNING, "t1 變 running")
    _check(c["attempts"] == 1, "t1 attempts=1")

    print("[3] t1 完成")
    q.mark_completed("t1", result_ref="data/results.jsonl")
    _check(q.get("t1")["status"] == COMPLETED, "t1 completed")
    _check(q.get("t1")["result_ref"] == "data/results.jsonl", "result_ref 已寫入")

    print("[4] t2 失敗一次 → requeue（attempts=1 < max 2）")
    c = q.claim_next()
    _check(c["task_id"] == "t2" and c["attempts"] == 1, "領到 t2，attempts=1")
    q.requeue("t2", error="transient")
    _check(q.get("t2")["status"] == QUEUED, "t2 改回 queued")

    print("[5] t2 再失敗 → 達上限 → failed（attempts=2 == max 2）")
    c = q.claim_next()
    _check(c["attempts"] == 2, "t2 attempts=2")
    q.mark_failed("t2", error="permanent")
    _check(q.get("t2")["status"] == FAILED, "t2 failed")
    _check(q.get("t2")["error"] == "permanent", "error 已記錄")

    print("[6] cancel_if_queued：queued 可取消、非 queued 不可")
    q.enqueue(task_id="t3", title="C", task_text="do C", safety_level=0, payload={})
    _check(q.cancel_if_queued("t3") is True, "queued 的 t3 取消成功")
    _check(q.get("t3")["status"] == CANCELLED, "t3 cancelled")
    _check(q.cancel_if_queued("t1") is False, "completed 的 t1 不能取消")

    print("[7] reset_stale_running：running 任務崩潰復原")
    q.enqueue(task_id="t4", title="D", task_text="do D", safety_level=0, payload={})
    q.claim_next()  # t4 -> running
    _check(q.get("t4")["status"] == RUNNING, "t4 running")
    n = q.reset_stale_running()
    _check(n == 1 and q.get("t4")["status"] == QUEUED, "t4 被改回 queued")

    print("[8] claim_next 沒有任務時回 None")
    while q.claim_next() is not None:
        pass
    _check(q.claim_next() is None, "空 queue 回 None")

    print("\n✅ QueueStore smoke test 全數通過。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
