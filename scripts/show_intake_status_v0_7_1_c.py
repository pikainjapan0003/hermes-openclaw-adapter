#!/usr/bin/env python3
"""v0.7.1-C — 唯讀 intake status report CLI。

從指定的 SQLite Queue DB 讀取任務，套用 v0.7.1-C view-model，印出安全摘要。

唯讀保證：
  - 只用 QueueStore 的 SELECT 方法（list_page / counts_by_status）。
  - 不寫入、不 enqueue、不 claim_next、不 approve/reject。
  - 不呼叫 worker / OpenClaw / Google Sheets、不讀 secrets。
  - 只輸出 console summary，不建立任何檔案。

用法：
  python scripts/show_intake_status_v0_7_1_c.py [--db-path PATH] [--limit N] [--status S]

預設 --db-path 取 INTAKE_QUEUE_DB_PATH（再退回 data/intake_local_v0_7_1_b.db）。
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.dashboard_intake_view_v0_7 import derive_intake_status_view  # noqa: E402
from app.queue_store import QueueStore  # noqa: E402

DEFAULT_INTAKE_DB_PATH = "data/intake_local_v0_7_1_b.db"


def _resolve_db_path(arg_db_path: str | None) -> str:
    if arg_db_path:
        return arg_db_path
    return os.getenv("INTAKE_QUEUE_DB_PATH", DEFAULT_INTAKE_DB_PATH)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only intake status report (v0.7.1-C).")
    parser.add_argument("--db-path", default=None, help="SQLite queue DB path（唯讀）。")
    parser.add_argument("--limit", type=int, default=20, help="最多顯示幾筆（預設 20）。")
    parser.add_argument("--status", default=None, help="只看某個 status（可選）。")
    args = parser.parse_args(argv)

    db_path = _resolve_db_path(args.db_path)
    print(f"[intake-status] db-path = {db_path}（唯讀）")

    if not Path(db_path).exists():
        print("[intake-status] DB 檔不存在；沒有任何 intake 任務可顯示。")
        return 0

    # 只用唯讀 SELECT 方法。
    store = QueueStore(db_path)
    counts = store.counts_by_status()
    print(f"[intake-status] counts = {counts}")

    limit = max(1, min(args.limit, 200))
    rows, total = store.list_page(status=args.status, limit=limit, offset=0)
    print(f"[intake-status] 顯示 {len(rows)} / {total} 筆"
          + (f"（status={args.status}）" if args.status else "") + "：")

    for row in rows:
        view = derive_intake_status_view(row)
        badges = ",".join(view["display_badges"]) or "-"
        print(
            f"  - {view['task_id']} | status={view['status']}"
            f" | source={view['source_mode']} | intake={view['intake_mode']}"
            f" | executable_by_worker={view['executable_by_worker']}"
            f" | approval={view['approval_status']} | risk={view['risk_level']}"
            f" | badges=[{badges}]"
        )

    print("[intake-status] 完成（唯讀，未寫入、未改狀態、未啟動 worker）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
