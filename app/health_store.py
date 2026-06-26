"""v0.5.6 — System Health / Worker Heartbeat 儲存層（SQLite）。

設計原則：
- 與 QueueStore 完全獨立的「心跳」儲存，只負責 worker_heartbeats 這張表。
- 可以共用同一個 data/queue.db 檔案，但**絕不**讀寫 queue 那張表、
  不改任何 queue 任務狀態、不觸發 worker、不呼叫 OpenClaw CLI。
- 只用標準函式庫 sqlite3。
- 純觀測：心跳只記錄、不反向控制 worker。

worker status：starting / idle / running / stopping / error（raw_status）。
online/stale/unknown 由 last_seen_at 與現在時間推導（見 derive_status）。
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# worker 心跳超過這個秒數沒更新就算 stale。
WORKER_HEARTBEAT_STALE_SECONDS = 30

# 預設 worker id（單一 worker 架構）。
DEFAULT_WORKER_ID = "default"

# raw_status 白名單（僅供參考/驗證，非強制）。
VALID_WORKER_STATUSES = {"starting", "idle", "running", "stopping", "error"}

# 推導出來的線上狀態。
ONLINE = "online"
STALE = "stale"
UNKNOWN = "unknown"

_COLUMNS = (
    "worker_id",
    "status",
    "pid",
    "hostname",
    "started_at",
    "last_seen_at",
    "current_task_id",
    "current_task_started_at",
    "last_claimed_at",
    "last_completed_at",
    "last_error_at",
    "last_error_message",
    "metadata_json",
)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS worker_heartbeats (
    worker_id               TEXT PRIMARY KEY,
    status                  TEXT NOT NULL,
    pid                     INTEGER,
    hostname                TEXT,
    started_at              TEXT,
    last_seen_at            TEXT,
    current_task_id         TEXT,
    current_task_started_at TEXT,
    last_claimed_at         TEXT,
    last_completed_at       TEXT,
    last_error_at           TEXT,
    last_error_message      TEXT,
    metadata_json           TEXT
);
"""


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value)
    except (ValueError, TypeError):
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def derive_status(
    last_seen_at: str | None,
    stale_seconds: int = WORKER_HEARTBEAT_STALE_SECONDS,
    now: datetime | None = None,
) -> str:
    """由 last_seen_at 推導 online / stale / unknown（唯讀，不執行任何東西）。"""
    dt = _parse_iso(last_seen_at)
    if dt is None:
        return UNKNOWN
    now = now or datetime.now(timezone.utc)
    age = (now - dt).total_seconds()
    return ONLINE if age <= stale_seconds else STALE


class HealthStore:
    """SQLite-backed worker heartbeat 儲存。每個操作開新連線。"""

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = str(db_path)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

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

    @staticmethod
    def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
        d = dict(row)
        md: dict[str, Any] = {}
        raw = d.get("metadata_json")
        if raw:
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, dict):
                    md = parsed
            except (json.JSONDecodeError, TypeError):
                md = {}
        d["metadata"] = md
        return d

    def record(self, worker_id: str = DEFAULT_WORKER_ID, **fields: Any) -> dict[str, Any]:
        """寫入/更新一筆心跳（UPSERT）。未提供的欄位沿用既有值；last_seen_at 預設更新為現在。

        只寫 worker_heartbeats，不碰 queue。任何欄位都不會觸發 worker 或 OpenClaw。
        """
        now = _utc_now_iso()
        existing = self.get(worker_id) or {}

        if "metadata" in fields and "metadata_json" not in fields:
            md = fields.pop("metadata")
            fields["metadata_json"] = json.dumps(md, ensure_ascii=False) if md else None

        merged: dict[str, Any] = {c: existing.get(c) for c in _COLUMNS}
        merged.update({k: v for k, v in fields.items() if k in _COLUMNS})
        merged["worker_id"] = worker_id
        merged["last_seen_at"] = fields.get("last_seen_at", now)
        if not merged.get("status"):
            merged["status"] = "idle"

        placeholders = ",".join("?" for _ in _COLUMNS)
        cols = ",".join(_COLUMNS)
        conn = self._connect()
        try:
            conn.execute(
                f"INSERT OR REPLACE INTO worker_heartbeats ({cols}) VALUES ({placeholders})",
                [merged.get(c) for c in _COLUMNS],
            )
            conn.commit()
        finally:
            conn.close()
        return self.get(worker_id)  # type: ignore[return-value]

    def get(self, worker_id: str = DEFAULT_WORKER_ID) -> dict[str, Any] | None:
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT * FROM worker_heartbeats WHERE worker_id=?", (worker_id,)
            ).fetchone()
        finally:
            conn.close()
        return self._row_to_dict(row) if row else None

    def snapshot(
        self,
        worker_id: str = DEFAULT_WORKER_ID,
        stale_seconds: int = WORKER_HEARTBEAT_STALE_SECONDS,
    ) -> dict[str, Any]:
        """組出對外的 worker 觀測樣貌（含推導的 online/stale/unknown）。唯讀。"""
        row = self.get(worker_id)
        if row is None:
            return {
                "worker_id": worker_id,
                "status": UNKNOWN,
                "raw_status": None,
                "pid": None,
                "hostname": None,
                "started_at": None,
                "last_seen_at": None,
                "current_task_id": None,
                "current_task_started_at": None,
                "last_claimed_at": None,
                "last_completed_at": None,
                "last_error_at": None,
                "last_error_message": None,
            }
        return {
            "worker_id": row.get("worker_id"),
            "status": derive_status(row.get("last_seen_at"), stale_seconds),
            "raw_status": row.get("status"),
            "pid": row.get("pid"),
            "hostname": row.get("hostname"),
            "started_at": row.get("started_at"),
            "last_seen_at": row.get("last_seen_at"),
            "current_task_id": row.get("current_task_id"),
            "current_task_started_at": row.get("current_task_started_at"),
            "last_claimed_at": row.get("last_claimed_at"),
            "last_completed_at": row.get("last_completed_at"),
            "last_error_at": row.get("last_error_at"),
            "last_error_message": row.get("last_error_message"),
        }
