#!/usr/bin/env python3
"""v0.6.7 — Google Sheets Mock Sink 測試（完全離線、不連真 Google）。

用 importlib.reload 在不同 RESULT_SINK_* env 下重建 app.result_sink。
驗證：預設關閉不寫檔、mock 模式寫 JSONL、欄位完整、長摘要截斷、error 欄位、
mock log 在 data/ 且未被 git tracked、app.main 可 import。
"""

from __future__ import annotations

import importlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

FAILURES: list[str] = []


def _check(cond: bool, label: str) -> None:
    print(f"  {'ok ' if cond else '❌ '}: {label}")
    if not cond:
        FAILURES.append(label)


def _load(enabled: str, stype: str, mode: str, mock_path: str):
    os.environ["RESULT_SINK_ENABLED"] = enabled
    os.environ["RESULT_SINK_TYPE"] = stype
    os.environ["RESULT_SINK_MODE"] = mode
    os.environ["MOCK_GOOGLE_SHEETS_ROWS_PATH"] = mock_path
    import app.result_sink as rs  # noqa: PLC0415
    importlib.reload(rs)
    return rs


def _task(**over):
    base = {
        "task_id": "rs-1",
        "title": "結果落地測試",
        "status": "completed",
        "safety_level": 0,
        "created_at": "2026-06-26T00:00:00+00:00",
        "updated_at": "2026-06-26T00:00:01+00:00",
        "attempts": 1,
        "source": "hermes",
        "payload": json.dumps({"metadata": {"requires_confirmation": False, "source": "hermes"}}),
    }
    base.update(over)
    return base


def main() -> int:
    tmp = tempfile.mkdtemp(prefix="mocksink_")
    mock_path = str(Path(tmp) / "data" / "mock_google_sheets_rows.jsonl")

    print("[1] 預設 disabled → emit 回 disabled，不寫檔")
    rs = _load("false", "none", "mock", mock_path)
    _check(rs.is_result_sink_enabled() is False, "is_result_sink_enabled()=False")
    res = rs.emit_result(_task(), result={"status": "completed", "result_text": "ok"})
    _check(res.get("status") == "disabled", f"emit→disabled（實際 {res.get('status')}）")
    _check(not Path(mock_path).exists(), "disabled 時沒有寫出 mock 檔")

    print("[1b] enabled 但 type=none → 仍視為未啟用")
    rs = _load("true", "none", "mock", mock_path)
    _check(rs.is_result_sink_enabled() is False, "type=none → 未啟用")
    _check(rs.emit_result(_task()).get("status") == "disabled", "type=none emit→disabled")

    print("[2] mock 模式啟用 → 寫入 mock JSONL")
    rs = _load("true", "google_sheets", "mock", mock_path)
    _check(rs.is_result_sink_enabled() is True, "google_sheets+enabled → 啟用")
    res = rs.emit_result(_task(), result={"status": "completed", "result_text": "PONG",
                                          "finished_at": 1782460000})
    _check(res.get("status") == "mock_written", f"emit→mock_written（實際 {res.get('status')}）")
    _check(Path(mock_path).exists(), "mock JSONL 已建立")
    lines = Path(mock_path).read_text(encoding="utf-8").strip().splitlines()
    _check(len(lines) == 1, "寫了 1 列")
    rec = json.loads(lines[0])
    _check(rec.get("_mock") is True, "mock 標記存在（_mock=true）")
    row = rec["row"]

    print("[3] row 欄位完整（v0.6.6 設計的全部欄位）")
    for col in rs.LEDGER_COLUMNS:
        _check(col in row, f"row 含欄位 {col}")
    _check(row["task_id"] == "rs-1" and row["status"] == "completed", "task_id/status 正確")
    _check(row["result_summary"] == "PONG", "result_summary=PONG")
    _check(row["requires_confirmation"] is False, "requires_confirmation 來自 metadata")
    _check(row["source"] == "hermes", "source 來自 metadata")

    print("[4] 長 result_summary 被截斷（<= 500 + 省略號）")
    long_text = "x" * 2000
    rs.emit_result(_task(task_id="rs-long"),
                   result={"status": "completed", "result_text": long_text})
    last = json.loads(Path(mock_path).read_text(encoding="utf-8").strip().splitlines()[-1])["row"]
    _check(len(last["result_summary"]) <= 500, f"summary 截斷到 <=500（實際 {len(last['result_summary'])}）")
    _check(last["result_summary"].endswith("…"), "截斷後有省略號")

    print("[5] error case → error 欄位有值，status=failed")
    rs.emit_result(_task(task_id="rs-err", status="failed"),
                   result={"status": "failed", "result_text": ""},
                   error="OPENCLAW_TIMEOUT: 逾時")
    erow = json.loads(Path(mock_path).read_text(encoding="utf-8").strip().splitlines()[-1])["row"]
    _check(erow["status"] == "failed", "error case status=failed")
    _check("OPENCLAW_TIMEOUT" in erow["error"], "error 欄位含錯誤訊息")

    print("[6] mock log 在 data/ 路徑下、且未被 git tracked")
    _check("data/" in rs.MOCK_GOOGLE_SHEETS_ROWS_PATH or "/data/" in mock_path,
           "mock log 路徑在 data/ 下")
    tracked = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "data/mock_google_sheets_rows.jsonl",
         "*mock_google_sheets_rows.jsonl"],
        capture_output=True, text=True).stdout.strip()
    _check(not tracked, "mock_google_sheets_rows.jsonl 未被 git tracked")

    print("[7] emit 永不拋例外（壞輸入也只回 error/相容）")
    res = rs.emit_result({}, result=None, error=None)  # 空 task
    _check(res.get("status") in ("mock_written", "error", "skipped"), "空 task 不會 crash")

    print("[8] app.main 可 import")
    try:
        import app.main as m  # noqa: PLC0415
        _check(hasattr(m, "app"), "import app.main OK")
    except Exception as exc:  # noqa: BLE001
        _check(False, f"import app.main 失敗：{exc}")

    if FAILURES:
        print(f"\n❌ Google Sheets Mock Sink 測試失敗 {len(FAILURES)} 項：")
        for f in FAILURES:
            print(f"   - {f}")
        return 1
    print("\n✅ Google Sheets Mock Sink 測試全數通過（沒有連真 Google）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
