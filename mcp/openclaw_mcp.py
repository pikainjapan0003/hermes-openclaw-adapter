#!/usr/bin/env python3
"""
OpenClaw MCP bridge for Hermes (v0.4 — async dispatch + result polling).

Two MCP tools:
- ``dispatch_to_openclaw``   → POST /tasks/dispatch ; returns the Adapter's
  *accepted* response immediately (the task runs in the Adapter's background).
- ``get_openclaw_task_result`` → GET /tasks/{task_id}/result ; poll for the
  completed/failed result later.

Design rules (intentional):
- This MCP server ONLY makes HTTP calls to the Adapter.
- It NEVER calls the ``openclaw`` CLI directly and NEVER uses a shell.
"""
from __future__ import annotations

import os
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

# --- Config from environment (with safe defaults) ----------------------------
# Base for /tasks/dispatch; the result endpoint is derived from the same host.
ADAPTER_URL = os.getenv("OPENCLAW_ADAPTER_URL", "http://127.0.0.1:8000/tasks/dispatch")
ADAPTER_BASE = ADAPTER_URL.rsplit("/tasks/dispatch", 1)[0] or "http://127.0.0.1:8000"
ADAPTER_TOKEN = os.getenv("OPENCLAW_ADAPTER_TOKEN", "change-me")
# Dispatch now returns fast (accepted), so a short timeout is fine.
DISPATCH_TIMEOUT_SECONDS = float(os.getenv("OPENCLAW_ADAPTER_TIMEOUT_SECONDS", "60"))
RESULT_TIMEOUT_SECONDS = float(os.getenv("OPENCLAW_ADAPTER_RESULT_TIMEOUT_SECONDS", "30"))

mcp = FastMCP("openclaw")

_HEADERS = {"Content-Type": "application/json", "X-Adapter-Token": ADAPTER_TOKEN}


def _safe_json(resp: httpx.Response) -> Any | None:
    try:
        return resp.json()
    except Exception:  # noqa: BLE001
        return None


def _error(message: str, **extra: Any) -> dict[str, Any]:
    return {"ok": False, "error": message, **extra}


@mcp.tool()
def dispatch_to_openclaw(
    title: str,
    goal: str,
    task_text: str,
    priority: str = "low",
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """把任務送到 OpenClaw 執行端（透過本機 Adapter /tasks/dispatch），**立刻**回傳。

    v0.4 是非同步派工：這個工具不會等 OpenClaw 做完，而是馬上回傳
    {"status":"accepted","task_id":...}。任務會在 Adapter 背景執行，
    完成後寫入 results。要拿結果，之後用 get_openclaw_task_result(task_id) 查。

    只在需要實際「執行 / 操作 / 自動化 / CLI / 跨平台 / 固定格式整理」任務時使用。
    高風險動作（改檔 / 刪資料 / 登入 / 下單 / 發送訊息）請先向使用者確認，
    且只送 Level 0 / Level 1 任務（在 metadata.safety_level 標註）。
    不要把密碼、API key、token 放進 task_text 或 metadata。

    回傳：
        accepted → {"status":"accepted","task_id":...,"message":...}
        rejected → {"status":"rejected","task_id":...,"reason":...}（高風險被擋）
    """
    payload = {
        "title": title,
        "goal": goal,
        "task_text": task_text,
        "priority": priority,
        "metadata": metadata if metadata is not None else {"source": "hermes"},
    }
    try:
        resp = httpx.post(ADAPTER_URL, json=payload, headers=_HEADERS, timeout=DISPATCH_TIMEOUT_SECONDS)
    except httpx.ConnectError:
        return _error(
            f"無法連線到 Adapter（{ADAPTER_URL}）。請先啟動 Adapter："
            "uvicorn app.main:app --host 0.0.0.0 --port 8000 --env-file .env"
        )
    except httpx.TimeoutException:
        return _error(f"呼叫 Adapter 超過 {DISPATCH_TIMEOUT_SECONDS:.0f} 秒逾時。")
    except Exception as exc:  # noqa: BLE001
        return _error(f"呼叫 Adapter 發生未預期錯誤：{type(exc).__name__}: {exc}")

    if resp.status_code in (401, 403):
        return _error(
            f"Adapter 拒絕請求（HTTP {resp.status_code}）。請確認 OPENCLAW_ADAPTER_TOKEN 與 "
            "Adapter 的 HERMES_ADAPTER_TOKEN 一致。",
            status_code=resp.status_code,
        )
    if resp.status_code == 422:
        return _error(
            "Adapter 回 422（欄位驗證失敗），最常見原因是缺少必填欄位 task_text。",
            status_code=422,
            detail=_safe_json(resp),
        )
    if resp.status_code != 200:
        return _error(
            f"Adapter 回傳非預期狀態碼（HTTP {resp.status_code}）。",
            status_code=resp.status_code,
            detail=resp.text[:2000],
        )

    parsed = _safe_json(resp)
    if parsed is None:
        return _error("Adapter 回傳非 JSON 內容。", status_code=200, raw=resp.text[:2000])
    return parsed


@mcp.tool()
def get_openclaw_task_result(task_id: str) -> dict[str, Any]:
    """查詢某個 OpenClaw 任務的結果（透過 Adapter GET /tasks/{task_id}/result）。

    用在 dispatch_to_openclaw 之後。回傳：
        - 還在執行：{"task_id":...,"status":"queued"/"running",...,"result":null}
        - 已完成/失敗：{"task_id":...,"task":{...},"result":{...}}（result.status = completed/failed）
        - 找不到：{"ok":false,"error":"...","status_code":404}
    """
    url = f"{ADAPTER_BASE}/tasks/{task_id}/result"
    try:
        resp = httpx.get(url, headers=_HEADERS, timeout=RESULT_TIMEOUT_SECONDS)
    except httpx.ConnectError:
        return _error(f"無法連線到 Adapter（{url}）。請確認 Adapter 已啟動。")
    except httpx.TimeoutException:
        return _error(f"查詢結果超過 {RESULT_TIMEOUT_SECONDS:.0f} 秒逾時。")
    except Exception as exc:  # noqa: BLE001
        return _error(f"查詢結果發生未預期錯誤：{type(exc).__name__}: {exc}")

    if resp.status_code == 404:
        return _error(f"找不到 task_id={task_id}。", status_code=404)
    if resp.status_code in (401, 403):
        return _error(f"Adapter 拒絕查詢（HTTP {resp.status_code}），token 可能不符。", status_code=resp.status_code)
    if resp.status_code != 200:
        return _error(f"Adapter 回傳非預期狀態碼（HTTP {resp.status_code}）。", status_code=resp.status_code, detail=resp.text[:2000])

    parsed = _safe_json(resp)
    if parsed is None:
        return _error("Adapter 回傳非 JSON 內容。", status_code=200, raw=resp.text[:2000])
    return parsed


if __name__ == "__main__":
    mcp.run()  # stdio transport
