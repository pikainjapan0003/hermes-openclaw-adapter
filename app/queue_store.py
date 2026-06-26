"""v0.5 — 最小可用的本地持久化 Queue（SQLite）。

設計原則（v0.5 第一步）：
- 只用標準函式庫 sqlite3，不引入 Redis 或其他外部依賴。
- 單一檔案資料庫，FastAPI（寫入 enqueue）與 worker（claim/更新）兩個程序共用。
- 用 WAL + busy_timeout + `BEGIN IMMEDIATE` 交易，確保單一 worker 下 claim 不會重複領取。

任務狀態：queued / running / completed / failed / cancelled
          / waiting_review / rejected（v0.5.4 Approval Flow 新增）。
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
# v0.5.4 Approval Flow：
#   waiting_review = 需人工確認，worker 絕不 claim（claim_next 只取 queued）。
#   rejected       = 被拒絕的終止狀態，worker 絕不 claim。
WAITING_REVIEW = "waiting_review"
REJECTED = "rejected"
# v0.5.5 Limited Control Actions：
#   archived = 收納（終止）狀態，只收納不刪資料，worker 絕不 claim。
ARCHIVED = "archived"

# 全部合法狀態。
VALID_STATUSES = {
    QUEUED, RUNNING, COMPLETED, FAILED, CANCELLED, WAITING_REVIEW, REJECTED, ARCHIVED,
}

# 觀測/統計時保證有 key 的狀態順序。
ALL_STATUSES = (
    QUEUED, RUNNING, COMPLETED, FAILED, CANCELLED, WAITING_REVIEW, REJECTED, ARCHIVED,
)

# enqueue 時允許的初始狀態（只能是這兩種；其餘狀態必須走狀態機方法轉換）。
VALID_INITIAL_STATUSES = {QUEUED, WAITING_REVIEW}

# v0.5.5 控制動作允許的「來源狀態」白名單。
CANCEL_CONTROL_FROM = (QUEUED, WAITING_REVIEW)
RETRY_FROM = (FAILED,)
ARCHIVE_FROM = (COMPLETED, FAILED, CANCELLED, REJECTED)


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
        initial_status: str = QUEUED,
    ) -> dict[str, Any] | None:
        """新增一筆任務。重複 task_id 會被忽略（INSERT OR IGNORE）。

        initial_status 只能是 queued（一般任務）或 waiting_review（需人工確認，
        v0.5.4）。預設 queued，向後相容。waiting_review 任務不會被 worker claim。
        """
        if initial_status not in VALID_INITIAL_STATUSES:
            raise ValueError(
                f"initial_status 只能是 {sorted(VALID_INITIAL_STATUSES)}，收到 {initial_status!r}"
            )
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
                    task_id, now, now, initial_status, title, task_text,
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

    # --- v0.5.4 Approval Flow 狀態機（只在 waiting_review 時生效）---------------
    def approve(self, task_id: str) -> dict[str, Any] | None:
        """批准：只有 waiting_review 可轉成 queued。

        不增加 attempts、不改 task_text、不直接執行 worker（worker 之後自然 claim
        queued）。非 waiting_review（含已 approve/已 reject）回 None。
        """
        conn = self._connect()
        try:
            cur = conn.execute(
                "UPDATE queue SET status=?, updated_at=? WHERE task_id=? AND status=?",
                (QUEUED, _utc_now_iso(), task_id, WAITING_REVIEW),
            )
            conn.commit()
            ok = cur.rowcount > 0
        finally:
            conn.close()
        return self.get(task_id) if ok else None

    def reject(self, task_id: str, reason: str | None = None) -> dict[str, Any] | None:
        """拒絕：只有 waiting_review 可轉成 rejected（終止狀態）。

        可記錄 reason 到 error 欄位。rejected 任務不會被 worker claim。
        非 waiting_review 回 None。
        """
        conn = self._connect()
        try:
            cur = conn.execute(
                "UPDATE queue SET status=?, error=?, updated_at=? WHERE task_id=? AND status=?",
                (REJECTED, reason, _utc_now_iso(), task_id, WAITING_REVIEW),
            )
            conn.commit()
            ok = cur.rowcount > 0
        finally:
            conn.close()
        return self.get(task_id) if ok else None

    # --- v0.5.5 Limited Control Actions（安全控制：cancel / retry / archive）------
    # 全部用「條件式 UPDATE（WHERE status IN 白名單）」做原子狀態轉換：
    # 狀態不允許時 rowcount=0 → 回 None（API 層轉 409）。絕不啟動 worker、不呼叫
    # OpenClaw CLI、不碰 running 任務、不刪除資料。
    def _transition(
        self,
        task_id: str,
        *,
        new_status: str,
        allowed_from: tuple[str, ...],
        set_error: bool = False,
        error_value: str | None = None,
    ) -> dict[str, Any] | None:
        placeholders = ",".join("?" for _ in allowed_from)
        if set_error:
            sql = (
                f"UPDATE queue SET status=?, error=?, updated_at=? "
                f"WHERE task_id=? AND status IN ({placeholders})"
            )
            params = [new_status, error_value, _utc_now_iso(), task_id, *allowed_from]
        else:
            sql = (
                f"UPDATE queue SET status=?, updated_at=? "
                f"WHERE task_id=? AND status IN ({placeholders})"
            )
            params = [new_status, _utc_now_iso(), task_id, *allowed_from]
        conn = self._connect()
        try:
            cur = conn.execute(sql, params)
            conn.commit()
            ok = cur.rowcount > 0
        finally:
            conn.close()
        return self.get(task_id) if ok else None

    def cancel_control(self, task_id: str, reason: str | None = None) -> dict[str, Any] | None:
        """嚴格取消：只允許 queued / waiting_review -> cancelled。

        不取消 running（不做 kill worker）。reason 記到 error 欄位。
        非允許狀態回 None（API 轉 409）。
        """
        return self._transition(
            task_id,
            new_status=CANCELLED,
            allowed_from=CANCEL_CONTROL_FROM,
            set_error=True,
            error_value=reason,
        )

    def retry_failed(self, task_id: str, reason: str | None = None) -> dict[str, Any] | None:
        """重試：只允許 failed -> queued。不直接啟動 worker（worker 之後自然 claim）。

        保守處理：**不歸零 attempts**（避免無限重試）；清空 error 讓任務重新開始
        （retry 原因改記到 system blackboard comment 與 tasks.jsonl ledger）。
        由於 worker claim 後一定會把該筆執行一次，manual retry 等同「再跑一次」；
        若該次再失敗且 attempts 已達 max_attempts，worker 不會再自動 requeue。
        """
        return self._transition(
            task_id,
            new_status=QUEUED,
            allowed_from=RETRY_FROM,
            set_error=True,
            error_value=None,  # 清空 error
        )

    def archive(self, task_id: str, reason: str | None = None) -> dict[str, Any] | None:
        """封存：只允許 completed / failed / cancelled / rejected -> archived。

        只收納、不刪資料；保留原本的 error（不覆寫，避免遺失失敗原因）。
        非允許狀態回 None（API 轉 409）。
        """
        return self._transition(
            task_id,
            new_status=ARCHIVED,
            allowed_from=ARCHIVE_FROM,
            set_error=False,
        )

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

    # --- v0.5.1 觀測用唯讀方法（只 SELECT，不改任何狀態）-----------------------
    def counts_by_status(self) -> dict[str, int]:
        """像 counts()，但保證全部合法狀態都有 key（沒有的補 0）。唯讀。"""
        base = {s: 0 for s in ALL_STATUSES}
        base.update(self.counts())
        return base

    def total(self) -> int:
        """queue 內任務總數。唯讀。"""
        conn = self._connect()
        try:
            row = conn.execute("SELECT COUNT(*) AS n FROM queue").fetchone()
        finally:
            conn.close()
        return int(row["n"]) if row else 0

    def list_page(
        self, status: Optional[str] = None, limit: int = 20, offset: int = 0
    ) -> tuple[list[dict[str, Any]], int]:
        """分頁列出任務（created_at DESC）。回傳 (items, total)，

        total 為符合 status 篩選的總數（與分頁無關）。唯讀。
        """
        conn = self._connect()
        try:
            if status:
                total = conn.execute(
                    "SELECT COUNT(*) AS n FROM queue WHERE status=?", (status,)
                ).fetchone()["n"]
                rows = conn.execute(
                    "SELECT * FROM queue WHERE status=? ORDER BY created_at DESC LIMIT ? OFFSET ?",
                    (status, limit, offset),
                ).fetchall()
            else:
                total = conn.execute("SELECT COUNT(*) AS n FROM queue").fetchone()["n"]
                rows = conn.execute(
                    "SELECT * FROM queue ORDER BY created_at DESC LIMIT ? OFFSET ?",
                    (limit, offset),
                ).fetchall()
        finally:
            conn.close()
        return [dict(r) for r in rows], int(total)

    def recent_failed(self, limit: int = 10) -> list[dict[str, Any]]:
        """最近進入 failed 的任務（updated_at DESC）。唯讀。"""
        conn = self._connect()
        try:
            rows = conn.execute(
                "SELECT * FROM queue WHERE status=? ORDER BY updated_at DESC LIMIT ?",
                (FAILED, limit),
            ).fetchall()
        finally:
            conn.close()
        return [dict(r) for r in rows]
