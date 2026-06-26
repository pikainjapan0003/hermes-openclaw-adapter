"""v0.5 — OpenClaw Queue Worker。

啟動方式：
    python -m app.worker

行為：
- 輪詢本地 SQLite queue（app/queue_store.py）。
- 找到 queued 任務 → claim 成 running（attempts+1）。
- 重用 app.main 既有的 OpenClaw 執行邏輯（run_openclaw_cli 等），CLI 呼叫方式不變。
- 成功：寫 results.jsonl + tasks.jsonl(completed)，queue → completed，（可選）callback。
- 失敗且可重試且 attempts < max_attempts：queue → queued（下一輪重跑）。
- 失敗且達上限（或不可重試）：寫 results.jsonl(failed) + tasks.jsonl(failed)，queue → failed。

不改 token、不改安全等級邏輯、不改 OpenClaw CLI 呼叫方式。
"""

from __future__ import annotations

import asyncio
import json
import os
import signal
import sys

from dotenv import load_dotenv

# 先載入 .env，讓 worker 與 adapter 共用同一份設定（adapter 由 uvicorn --env-file 載入，
# worker 需自己載），且必須在 import app.main 之前，因為 main 在 import 時就讀 env。
load_dotenv()

from app import main as adapter  # noqa: E402
from app.health_store import HealthStore  # noqa: E402
from app.queue_store import QueueStore  # noqa: E402

POLL_INTERVAL = float(os.getenv("WORKER_POLL_INTERVAL_SECONDS", "2"))
RETRY_BACKOFF = float(os.getenv("WORKER_RETRY_BACKOFF_SECONDS", "5"))
QUEUE_DB_PATH = os.getenv("QUEUE_DB_PATH", str(adapter.DATA_DIR / "queue.db"))

_stop = False

# v0.5.6：worker heartbeat（純觀測）。心跳寫入只記錄，不改任務執行邏輯、
# 不改 queue 狀態機、不呼叫 OpenClaw CLI；寫入失敗也絕不讓 worker 崩潰。
_health: HealthStore | None = None


def _heartbeat(**fields) -> None:
    """安全寫入一筆 worker 心跳。任何例外都吞掉（worker 不可因心跳故障崩潰）。"""
    if _health is None:
        return
    try:
        _health.record(adapter.WORKER_ID, **fields)
    except Exception as exc:  # noqa: BLE001 - 心跳純觀測，失敗不可影響任務執行
        _log(f"(heartbeat 寫入失敗，已忽略：{type(exc).__name__})")


def _handle_signal(signum, _frame) -> None:
    global _stop
    _stop = True
    print(f"[worker] 收到 signal {signum}，跑完當前任務後結束…", flush=True)


def _log(msg: str) -> None:
    print(f"[worker] {msg}", flush=True)


async def process_item(queue: QueueStore, item: dict) -> None:
    task_id = item["task_id"]
    correlation_id = item.get("correlation_id") or task_id
    attempts = int(item.get("attempts") or 0)        # claim_next 已 +1
    max_attempts = int(item.get("max_attempts") or 1)

    # 解析 payload → TaskEnvelope
    try:
        payload = json.loads(item["payload"]) if item.get("payload") else {}
        envelope = adapter.TaskEnvelope(**payload)
    except Exception as exc:  # payload 壞掉 → 永久失敗
        error = {"code": "BAD_PAYLOAD", "message": f"{type(exc).__name__}: {exc}", "retryable": False}
        result = adapter.build_task_result(
            task_id=task_id, correlation_id=correlation_id, status="failed",
            title=str((item or {}).get("title", "")), goal="", result_text="", error=error,
        )
        adapter.append_jsonl(adapter.RESULTS_PATH, result)
        adapter.append_task_status(task_id, "failed", correlation_id=correlation_id)
        queue.mark_failed(task_id, error=json.dumps(error, ensure_ascii=False))
        _heartbeat(status="idle", current_task_id=None, current_task_started_at=None,
                   last_error_at=adapter.utc_now_iso(), last_error_message=error["message"])
        _log(f"{task_id} payload 解析失敗，已標記 failed。")
        return

    adapter.append_task_status(task_id, "running", correlation_id=correlation_id, attempt=attempts)
    _log(f"執行 {task_id}（attempt {attempts}/{max_attempts}）：{envelope.title}")

    message = adapter.build_openclaw_message(envelope, task_id)

    try:
        stdout = await adapter.run_openclaw_cli(message, adapter.OPENCLAW_TIMEOUT_SECONDS, task_id)
        result_text = adapter.extract_result_text(stdout)
        result = adapter.build_task_result(
            task_id=task_id, correlation_id=correlation_id, status="completed",
            title=envelope.title, goal=envelope.goal, result_text=result_text, error=None,
        )
        adapter.append_jsonl(adapter.RESULTS_PATH, result)
        adapter.append_task_status(task_id, "completed", correlation_id=correlation_id)
        queue.mark_completed(task_id, result_ref=str(adapter.RESULTS_PATH))
        _heartbeat(status="idle", current_task_id=None, current_task_started_at=None,
                   last_completed_at=adapter.utc_now_iso())
        if adapter.CALLBACK_ENABLED:
            await adapter.send_callback_to_hermes(result)
        _log(f"✅ {task_id} 完成。")
        return

    except adapter.OpenClawCliError as exc:
        can_retry = exc.retryable and attempts < max_attempts
        if can_retry:
            queue.requeue(task_id, error=f"{exc.code}: {exc.message}")
            adapter.append_task_status(
                task_id, "queued", correlation_id=correlation_id,
                retry=True, attempt=attempts, error=exc.code,
            )
            _heartbeat(status="idle", current_task_id=None, current_task_started_at=None,
                       last_error_at=adapter.utc_now_iso(),
                       last_error_message=f"{exc.code}: {exc.message}")
            _log(f"♻️ {task_id} 失敗（{exc.code}），改回 queued 重試。{RETRY_BACKOFF}s 後繼續。")
            await asyncio.sleep(RETRY_BACKOFF)
            return
        # 達上限或不可重試 → failed
        error = {"code": exc.code, "message": exc.message, "retryable": exc.retryable}
        result = adapter.build_task_result(
            task_id=task_id, correlation_id=correlation_id, status="failed",
            title=envelope.title, goal=envelope.goal, result_text="", error=error,
        )
        adapter.append_jsonl(adapter.RESULTS_PATH, result)
        adapter.append_task_status(task_id, "failed", correlation_id=correlation_id)
        queue.mark_failed(task_id, error=json.dumps(error, ensure_ascii=False))
        _heartbeat(status="idle", current_task_id=None, current_task_started_at=None,
                   last_error_at=adapter.utc_now_iso(), last_error_message=exc.message)
        if adapter.CALLBACK_ENABLED:
            try:
                await adapter.send_callback_to_hermes(result)
            except Exception:  # noqa: BLE001
                pass
        _log(f"❌ {task_id} 失敗（{exc.code}，attempts={attempts}/{max_attempts}）。")
        return

    except Exception as exc:  # noqa: BLE001 - worker 永不因單筆任務崩潰
        error = {"code": "WORKER_INTERNAL_ERROR", "message": f"{type(exc).__name__}: {exc}", "retryable": False}
        result = adapter.build_task_result(
            task_id=task_id, correlation_id=correlation_id, status="failed",
            title=envelope.title, goal=envelope.goal, result_text="", error=error,
        )
        adapter.append_jsonl(adapter.RESULTS_PATH, result)
        adapter.append_task_status(task_id, "failed", correlation_id=correlation_id)
        queue.mark_failed(task_id, error=json.dumps(error, ensure_ascii=False))
        _heartbeat(status="idle", current_task_id=None, current_task_started_at=None,
                   last_error_at=adapter.utc_now_iso(), last_error_message=error["message"])
        _log(f"❌ {task_id} worker 內部錯誤：{error['message']}")
        return


async def main_loop() -> None:
    global _health
    import socket  # noqa: PLC0415

    adapter.ensure_data_dir()
    queue = QueueStore(QUEUE_DB_PATH)
    _health = HealthStore(QUEUE_DB_PATH)
    _heartbeat(
        status="starting",
        pid=os.getpid(),
        hostname=socket.gethostname(),
        started_at=adapter.utc_now_iso(),
        current_task_id=None,
        current_task_started_at=None,
        last_error_at=None,
        last_error_message=None,
    )

    reset = queue.reset_stale_running()
    _log(f"啟動。queue db = {QUEUE_DB_PATH}；poll={POLL_INTERVAL}s；openclaw_bin={adapter.OPENCLAW_CLI_BIN}")
    if reset:
        _log(f"崩潰復原：{reset} 筆卡在 running 的任務已改回 queued。")
    _log(f"目前 queue 狀態：{queue.counts()}")
    _heartbeat(status="idle")

    while not _stop:
        item = queue.claim_next()
        if item is None:
            _heartbeat(status="idle")  # 定期 idle 心跳
            await asyncio.sleep(POLL_INTERVAL)
            continue
        now = adapter.utc_now_iso()
        _heartbeat(
            status="running",
            current_task_id=item["task_id"],
            current_task_started_at=now,
            last_claimed_at=now,
        )
        await process_item(queue, item)
        # process_item 內已依結果寫過 completed/error 心跳；這裡確保回到 idle 並清掉 current_task。
        _heartbeat(status="idle", current_task_id=None, current_task_started_at=None)

    _heartbeat(status="stopping")
    _log("已停止。")


def main() -> None:
    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        pass
    sys.exit(0)


if __name__ == "__main__":
    main()
