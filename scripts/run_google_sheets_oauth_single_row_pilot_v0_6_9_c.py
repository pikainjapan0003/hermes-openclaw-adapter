#!/usr/bin/env python3
"""v0.6.9-C — Google Sheets OAuth single-row live pilot runner（C0：preflight，本版不真寫）。

這支 script 是未來 C1 第一次真寫用；本版（C0）只做 preflight：
- 因 `GOOGLE_SHEETS_ENABLED=false`，writer 會回 skipped/disabled，**不連 Google、不 append**。
- 必須帶 `--i-understand-this-writes-one-row`，否則即使 env 全對也拒絕（雙重 live guard）。
- **永不**印出 refresh token / client secret / 完整 env；spreadsheet id 只 masked 顯示。

使用 app.google_sheets_oauth_writer 的 guard；不接 Queue / Worker / result_sink / app.main。
詳見 docs/HERMES_OPENCLAW_GOOGLE_SHEETS_LIVE_PILOT_V0_6_9_C0.md。
"""

from __future__ import annotations

import argparse
import datetime
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.google_sheets_oauth_writer import (  # noqa: E402
    APPEND_RANGE,
    PILOT_ROW_LEN,
    WORKSHEET_NAME_REQUIRED,
    GoogleSheetsWriterError,
    append_single_pilot_row,
    build_pilot_row,
    load_google_sheets_writer_config,
)

EVENT_TYPE = "oauth_sheets_write_pilot"
PILOT_METADATA_JSON = '{"version":"v0.6.9","phase":"C","mode":"pilot","single_row":true}'


def _mask(value: str) -> str:
    """只顯示前 6 + 後 4，其餘遮罩；過短一律全遮。"""
    v = (value or "").strip()
    if len(v) <= 10:
        return "***"
    return f"{v[:6]}...{v[-4:]}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Google Sheets OAuth single-row live pilot runner (v0.6.9-C). "
                    "C0 為 preflight；本版不真寫。",
    )
    parser.add_argument(
        "--i-understand-this-writes-one-row", action="store_true",
        dest="ack",
        help="雙重 live guard：未帶此旗標一律拒絕（即使 env 全對）。",
    )
    args = parser.parse_args(argv)

    if not args.ack:
        print("❌ 拒絕：必須帶 --i-understand-this-writes-one-row 才能執行 pilot runner。",
              file=sys.stderr)
        return 2

    config = load_google_sheets_writer_config()

    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    row = build_pilot_row(
        timestamp=timestamp,
        event_type=EVENT_TYPE,
        task_id="manual-pilot-001",
        status="ok",
        message="Google Sheets OAuth pilot write succeeded",
        metadata_json=PILOT_METADATA_JSON,
    )

    # 只有帶 ack 時才允許傳 allow_live_write=True；但因 ENABLED=false，writer 會 skipped。
    try:
        result = append_single_pilot_row(
            row, config, transport=None, allow_live_write=True,
        )
    except GoogleSheetsWriterError as exc:
        print(f"❌ pilot runner guard 拒絕：{exc}", file=sys.stderr)
        return 1

    status = result.get("status")
    # 安全摘要（不印 token / client secret / 完整 env / 完整 spreadsheet id）。
    print("=== Google Sheets OAuth single-row pilot — SUMMARY ===")
    print(f"  writer result status : {status}")
    print(f"  worksheet            : {WORKSHEET_NAME_REQUIRED}")
    print(f"  row columns          : {len(row)} (required {PILOT_ROW_LEN})")
    print(f"  append range         : {APPEND_RANGE}")
    print(f"  spreadsheet id (masked): {_mask(config.spreadsheet_id)}")
    print(f"  GOOGLE_SHEETS_ENABLED: {'true' if config.is_enabled else 'false'}")
    print(f"  write_mode           : {config.write_mode}")

    if status == "skipped":
        print("\nℹ️  preflight：GOOGLE_SHEETS_ENABLED 不是 true → skipped（未連 Google、未 append）。")
        print("   第一次真寫請見 C1（Owner 受控下暫時開 ENABLED=true，寫完立即關回 false）。")
        return 0
    if status == "appended":
        print("\n✅ 已 append 一列（這是 C1 真寫路徑；C0 預期不會走到這裡）。")
        return 0
    print(f"\n⚠️  非預期狀態：{status}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
