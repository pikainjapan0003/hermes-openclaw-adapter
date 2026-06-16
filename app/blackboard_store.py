"""v0.5.3 — Blackboard / task comments 留言儲存層（SQLite）。

設計原則：
- 與 QueueStore 完全獨立的「留言」儲存，只負責 task_comments 這張表。
- 可以共用同一個 data/queue.db 檔案，但**絕不**讀寫 queue 那張表、
  不改任何 queue 任務狀態、不觸發 worker、不呼叫 OpenClaw CLI。
- 只用標準函式庫 sqlite3，不引入 Redis 或其他外部依賴。
- task 是否存在（避免孤兒留言）由呼叫端用 QueueStore 判斷，這層不依賴 queue 表。

author_type 白名單：user / hermes / openclaw / system。
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# --- author_type 白名單 ------------------------------------------------------
AUTHOR_USER = "user"
AUTHOR_HERMES = "hermes"
AUTHOR_OPENCLAW = "openclaw"
AUTHOR_SYSTEM = "system"

VALID_AUTHOR_TYPES = {AUTHOR_USER, AUTHOR_HERMES, AUTHOR_OPENCLAW, AUTHOR_SYSTEM}

# 保守的輸入長度上限（v0.5.3 先不做嚴格身份驗證，但限制輸入大小）。
MAX_CONTENT_LEN = 8000
MAX_AUTHOR_NAME_LEN = 200


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


_SCHEMA = """
CREATE TABLE IF NOT EXISTS task_comments (
    comment_id    TEXT PRIMARY KEY,
    task_id       TEXT NOT NULL,
    author_type   TEXT NOT NULL,
    author_name   TEXT,
    content       TEXT NOT NULL,
    created_at    TEXT NOT NULL,
    metadata_json TEXT
);
CREATE INDEX IF NOT EXISTS idx_comments_task ON task_comments(task_id, created_at);
"""


class CommentValidationError(ValueError):
    """留言輸入不合法（空 content / 非法 author_type 等）。由 API 層轉成 400。"""


class BlackboardStore:
    """SQLite-backed task comments 留言板。每個操作開新連線，避免跨執行緒共用。"""

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

    # --- 序列化 helper ------------------------------------------------------
    @staticmethod
    def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
        md: dict[str, Any] = {}
        raw = row["metadata_json"]
        if raw:
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, dict):
                    md = parsed
            except (json.JSONDecodeError, TypeError):
                md = {}
        return {
            "comment_id": row["comment_id"],
            "task_id": row["task_id"],
            "author_type": row["author_type"],
            "author_name": row["author_name"],
            "content": row["content"],
            "created_at": row["created_at"],
            "metadata": md,
        }

    # --- 寫入 ---------------------------------------------------------------
    def add_comment(
        self,
        *,
        task_id: str,
        author_type: str,
        content: str,
        author_name: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """新增一則留言。只寫 task_comments，不碰 queue。

        輸入不合法時丟 CommentValidationError（由 API 轉 400）。
        呼叫端應先確認 task_id 存在，避免孤兒留言。
        """
        author_type = (author_type or "").strip()
        if author_type not in VALID_AUTHOR_TYPES:
            raise CommentValidationError(
                f"author_type 必須是 {sorted(VALID_AUTHOR_TYPES)} 之一"
            )

        if content is None or content.strip() == "":
            raise CommentValidationError("content 不可為空")
        content = content.strip()
        if len(content) > MAX_CONTENT_LEN:
            raise CommentValidationError(f"content 過長（上限 {MAX_CONTENT_LEN} 字）")

        if author_name is not None:
            author_name = author_name.strip() or None
            if author_name and len(author_name) > MAX_AUTHOR_NAME_LEN:
                raise CommentValidationError(
                    f"author_name 過長（上限 {MAX_AUTHOR_NAME_LEN} 字）"
                )

        if metadata is None:
            metadata = {}
        if not isinstance(metadata, dict):
            raise CommentValidationError("metadata 必須是物件")

        comment_id = "cmt-" + uuid.uuid4().hex[:12]
        now = _utc_now_iso()
        conn = self._connect()
        try:
            conn.execute(
                """INSERT INTO task_comments
                   (comment_id, task_id, author_type, author_name,
                    content, created_at, metadata_json)
                   VALUES (?,?,?,?,?,?,?)""",
                (
                    comment_id, task_id, author_type, author_name,
                    content, now, json.dumps(metadata, ensure_ascii=False),
                ),
            )
            conn.commit()
        finally:
            conn.close()
        return self.get(comment_id)  # type: ignore[return-value]

    # --- 讀取 ---------------------------------------------------------------
    def get(self, comment_id: str) -> dict[str, Any] | None:
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT * FROM task_comments WHERE comment_id=?", (comment_id,)
            ).fetchone()
        finally:
            conn.close()
        return self._row_to_dict(row) if row else None

    def list_for_task(self, task_id: str) -> list[dict[str, Any]]:
        """取某 task 的全部留言（created_at 由舊到新）。唯讀。"""
        conn = self._connect()
        try:
            rows = conn.execute(
                "SELECT * FROM task_comments WHERE task_id=? ORDER BY created_at ASC, comment_id ASC",
                (task_id,),
            ).fetchall()
        finally:
            conn.close()
        return [self._row_to_dict(r) for r in rows]

    def count_for_task(self, task_id: str) -> int:
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT COUNT(*) AS n FROM task_comments WHERE task_id=?", (task_id,)
            ).fetchone()
        finally:
            conn.close()
        return int(row["n"]) if row else 0
