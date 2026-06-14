"""v0.5 — 最小可用的本地持久化 Queue（SQLite）。

設計原則（v0.5 第一步）：
- 只用標準函式庫 sqlite3，不引入 Redis 或其他外部依賴。
- 單一檔案資料庫，FastAPI（寫入 enqueue）與 worker（claim/更新）兩個程序共用。
- 用 WAL + busy_timeout + `BEGIN IMMEDIATE` 交易，確保單一 worker 下 claim 不會重複領取。

任務狀態：queued / running / completed / failed / cancelled。
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# --- 狀態常數 ---------------------------------------------------------------
QUEUED = "queued"
RUNNING = "running"
COMPLETED = "completed"
FAILED = "failed"
CANCELLED = "cancelled"

VALID_STATUSES = {QUEUED, RUNNING, COMPLETED, FAILED, CANCELLED}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


_SCHEMA = """
CREATE TABLE IF NOT EXISTS queue (
    task_id        TEXT PRIMARY KEY,
    created_at     TEXT NOT NULL,
    updated_at     TEXT NOT NULL,
    status         TEXT NOT NULL,
    title          TEXT,
    task_text      TEXT,
    safety_level   INTEGER,
    attempts       INTEGER NOT NULL DEFAULT 0,
    max_attempts   INTEGER NOT NULL DEFAULT 3,
    error          TEXT,
    result_ref     TEXT,
    correlation_id TEXT,
    payload        TEXT
);
CREATE INDEX IF NOT EXISTS idx_queue_status ON queue(status, created_at);
"""


class QueueStore:
    """SQLite-backed durable task queue。每個操作開新連線，避免跨執行緒共用。"""

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = str(db_path)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    # --- 連線 ---------------------------------------------------------------
    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=30, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout=30000;")
        return conn

    def _init_db(self) -> None:
        conn = self._connect()
        try:
            conn.executescript(_SCHEMA)
            conn.commit()
        finally:
            conn.close()

    # --- 寫入 ---------------------------------------------------------------
    def enqueue(
        self,
        *,
        task_id: str,
        title: str,
        task_text: str,
        safety_level: int,
        payload: dict[str, Any],
        correlation_id: str | None = None,
        max_attempts: int = 3,
    ) -> dict[str, Any] | None:
        """新增一筆 queued 任務。重複 task_id 會被忽略（INSERT OR IGNORE）。"""
        now = _utc_now_iso()
        conn = self._connect()
        try:
            conn.execute(
                """INSERT OR IGNORE INTO queue
                   (task_id, created_at, updated_at, status, title, task_text,
                    safety_level, attempts, max_attempts, error, result_ref,
                    correlation_id, payload)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    task_id, now, now, QUEUED, title, task_text,
                    safety_level, 0, max_attempts, None, None,
                    correlation_id, json.dumps(payload, ensure_ascii=False),
                ),
            )
            conn.commit()
        finally:
            conn.close()
        return self.get(task_id)

    def claim_next(self) -> dict[str, Any] | None:
        """原子地領取最舊的 queued 任務：改成 running、attempts+1，回傳該筆。

        沒有可領的任務時回傳 None。使用 BEGIN IMMEDIATE 確保多次呼叫
        （或多 worker）不會重複領取同一筆。
        """
        now = _utc_now_iso()
        conn = self._connect()
        try:
            conn.isolation_level = None  # 手動管理交易
            cur = conn.cursor()
            cur.execute("BEGIN IMMEDIATE;")
            try:
                row = cur.execute(
                    "SELECT task_id FROM queue WHERE status=? ORDER BY created_at ASC LIMIT 1",
                    (QUEUED,),
                ).fetchone()
                if row is None:
                    cur.execute("COMMIT;")
                    return None
                task_id = row["task_id"]
                cur.execute(
                    "UPDATE queue SET status=?, attempts=attempts+1, updated_at=? WHERE task_id=?",
                    (RUNNING, now, task_id),
                )
                cur.execute("COMMIT;")
            except Exception:
                cur.execute("ROLLBACK;")
                raise
        finally:
            conn.close()
        return self.get(task_id)

    def _update(self, task_id: str, **fields: Any) -> dict[str, Any] | None:
        fields["updated_at"] = _utc_now_iso()
        cols = ", ".join(f"{k}=?" for k in fields)
        vals = list(fields.values()) + [task_id]
        conn = self._connect()
        try:
            conn.execute(f"UPDATE queue SET {cols} WHERE task_id=?", vals)
            conn.commit()
        finally:
            conn.close()
        return self.get(task_id)

    def mark_completed(self, task_id: str, result_ref: str | None = None) -> dict[str, Any] | None:
        return self._update(task_id, status=COMPLETED, result_ref=result_ref, error=None)

    def mark_failed(self, task_id: str, error: str | None = None) -> dict[str, Any] | None:
        return self._update(task_id, status=FAILED, error=error)

    def requeue(self, task_id: str, error: str | None = None) -> dict[str, Any] | None:
        """執行失敗但還沒到 max_attempts：改回 queued 等待下一輪。"""
        return self._update(task_id, status=QUEUED, error=error)

    def mark_cancelled(self, task_id: str) -> dict[str, Any] | None:
        return self._update(task_id, status=CANCELLED)

    def cancel_if_queued(self, task_id: str) -> bool:
        """只在任務仍是 queued 時取消；回傳是否真的取消了。"""
        conn = self._connect()
        try:
            cur = conn.execute(
                "UPDATE queue SET status=?, updated_at=? WHERE task_id=? AND status=?",
                (CANCELLED, _utc_now_iso(), task_id, QUEUED),
            )
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()

    def reset_stale_running(self) -> int:
        """worker 啟動時把卡在 running 的任務（上次 worker crash）改回 queued。

        回傳被重設的筆數。單一 worker 架構下這是安全的崩潰復原。
        """
        conn = self._connect()
        try:
            cur = conn.execute(
                "UPDATE queue SET status=?, updated_at=? WHERE status=?",
                (QUEUED, _utc_now_iso(), RUNNING),
            )
            conn.commit()
            return cur.rowcount
        finally:
            conn.close()

    # --- 讀取 ---------------------------------------------------------------
    def get(self, task_id: str) -> dict[str, Any] | None:
        conn = self._connect()
        try:
            row = conn.execute("SELECT * FROM queue WHERE task_id=?", (task_id,)).fetchone()
        finally:
            conn.close()
        return dict(row) if row else None

    def list(self, status: Optional[str] = None, limit: int = 100) -> list[dict[str, Any]]:
        conn = self._connect()
        try:
            if status:
                rows = conn.execute(
                    "SELECT * FROM queue WHERE status=? ORDER BY created_at DESC LIMIT ?",
                    (status, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM queue ORDER BY created_at DESC LIMIT ?",
                    (limit,),
                ).fetchall()
        finally:
            conn.close()
        return [dict(r) for r in rows]

    def counts(self) -> dict[str, int]:
        conn = self._connect()
        try:
            rows = conn.execute(
                "SELECT status, COUNT(*) AS n FROM queue GROUP BY status"
            ).fetchall()
        finally:
            conn.close()
        return {r["status"]: r["n"] for r in rows}
