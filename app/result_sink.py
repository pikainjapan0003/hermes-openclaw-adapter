"""v0.6.7 — Google Sheets *Mock* Result Sink（雛形，預設關閉，不連真 Google）。

設計原則：
- **預設關閉**：`RESULT_SINK_ENABLED=false` → `emit_result()` 立刻回 `{"status":"disabled"}`，
  對 Worker / Queue 完全沒有影響。
- **不連真 Google**：本模組**不 import 任何 google client library**、不讀 credentials、零 API call。
- **只在 mock 模式寫本地 JSONL**：`RESULT_SINK_TYPE=google_sheets` + `RESULT_SINK_MODE=mock`
  時，把一列 ledger row append 到 `MOCK_GOOGLE_SHEETS_ROWS_PATH`（預設 data/，已 gitignore）。
- **永不拋例外**：`emit_result()` 內部全 try/except，失敗只回 `{"status":"error"}`，
  **絕不讓任務 sink 失敗影響 queue 狀態 / Worker 流程**。
- 不改 Queue 狀態機、不改 Worker claim、不改 OpenClaw / Hermes。
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# --- 設定（import 時讀一次）-------------------------------------------------
def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


RESULT_SINK_ENABLED = _env_bool("RESULT_SINK_ENABLED", False)
RESULT_SINK_TYPE = os.getenv("RESULT_SINK_TYPE", "none").strip().lower()
RESULT_SINK_MODE = os.getenv("RESULT_SINK_MODE", "mock").strip().lower()
MOCK_GOOGLE_SHEETS_ROWS_PATH = os.getenv(
    "MOCK_GOOGLE_SHEETS_ROWS_PATH", "data/mock_google_sheets_rows.jsonl"
).strip()

# result_summary 截斷上限（長結果不塞整段；長結果未來放 Drive artifact）。
MAX_SUMMARY_LEN = 500

# v0.6.6 設計的 Sheets ledger 欄位順序。
LEDGER_COLUMNS = (
    "task_id", "title", "status", "safety_level", "requires_confirmation",
    "created_at", "updated_at", "completed_at", "attempts", "source",
    "result_summary", "result_uri", "drive_file_id", "error", "metadata_json",
)


def is_result_sink_enabled() -> bool:
    """sink 是否實際啟用（enabled 且 type 不是 none）。"""
    return RESULT_SINK_ENABLED and RESULT_SINK_TYPE not in ("", "none")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _truncate(value: Any, limit: int = MAX_SUMMARY_LEN) -> str:
    s = "" if value is None else str(value)
    s = s.strip()
    return s if len(s) <= limit else s[: limit - 1].rstrip() + "…"


def _coerce_bool(raw: Any) -> bool:
    if isinstance(raw, bool):
        return raw
    if isinstance(raw, (int, float)):
        return raw != 0
    if isinstance(raw, str):
        return raw.strip().lower() in ("1", "true", "yes", "on")
    return False


def _payload_metadata(task: dict[str, Any]) -> dict[str, Any]:
    """從 queue row 的 payload(JSON 字串或 dict) 取 metadata。失敗回 {}。"""
    payload = task.get("payload")
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except (json.JSONDecodeError, TypeError):
            return {}
    if not isinstance(payload, dict):
        return {}
    md = payload.get("metadata")
    return md if isinstance(md, dict) else {}


def build_task_ledger_row(
    task: dict[str, Any],
    result: dict[str, Any] | None = None,
    error: str | None = None,
) -> dict[str, Any]:
    """把 queue row(+TaskResult) 組成一列 Sheets ledger row。缺欄位給空值，不 crash。"""
    task = task or {}
    result = result or {}
    md = _payload_metadata(task)

    status = result.get("status") or task.get("status") or ("failed" if error else None)
    err_val = error or result.get("error") or task.get("error")
    summary_src = result.get("result_text") or result.get("summary")

    row = {
        "task_id": task.get("task_id"),
        "title": task.get("title") or result.get("title"),
        "status": status,
        "safety_level": task.get("safety_level"),
        "requires_confirmation": _coerce_bool(md.get("requires_confirmation")),
        "created_at": task.get("created_at"),
        "updated_at": task.get("updated_at"),
        "completed_at": result.get("finished_at"),
        "attempts": task.get("attempts"),
        "source": md.get("source") or task.get("source"),
        "result_summary": _truncate(summary_src) if summary_src else "",
        "result_uri": None,        # 未來 Drive artifact（Hybrid）才填
        "drive_file_id": None,     # 未來 Drive artifact（Hybrid）才填
        "error": _truncate(err_val, 1000) if err_val else "",
        "metadata_json": json.dumps(md, ensure_ascii=False) if md else "{}",
    }
    # 保證所有欄位都在（缺的補 None）。
    for col in LEDGER_COLUMNS:
        row.setdefault(col, None)
    return row


def _append_mock_row(row: dict[str, Any]) -> dict[str, Any]:
    path = Path(MOCK_GOOGLE_SHEETS_ROWS_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {"_mock": True, "_emitted_at": _utc_now_iso(), "row": row}
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record


def emit_result(
    task: dict[str, Any],
    result: dict[str, Any] | None = None,
    error: str | None = None,
) -> dict[str, Any]:
    """任務 completed / failed 後可選地 emit 一列結果。

    回傳 status：disabled / mock_written / skipped / error。**永不拋例外。**
    """
    try:
        if not is_result_sink_enabled():
            return {"status": "disabled"}
        # 目前只支援 google_sheets 的 mock 模式（不連真 Google）。
        if RESULT_SINK_TYPE == "google_sheets" and RESULT_SINK_MODE == "mock":
            row = build_task_ledger_row(task, result, error)
            self_rec = _append_mock_row(row)
            return {
                "status": "mock_written",
                "path": MOCK_GOOGLE_SHEETS_ROWS_PATH,
                "row": row,
                "emitted_at": self_rec["_emitted_at"],
            }
        # 啟用了但不是 mock（例如 real）→ v0.6.7 不做真寫入。
        return {
            "status": "skipped",
            "reason": f"non-mock not implemented in v0.6.7 (type={RESULT_SINK_TYPE}, mode={RESULT_SINK_MODE})",
        }
    except Exception as exc:  # noqa: BLE001 - sink 失敗絕不可影響任務 / queue
        return {"status": "error", "error": f"{type(exc).__name__}: {exc}"}
