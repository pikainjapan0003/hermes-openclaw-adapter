#!/usr/bin/env python3
"""
OpenClaw MCP bridge for Hermes.

Exposes a single MCP tool, ``dispatch_to_openclaw``, that forwards a task to the
local Adapter (``POST /tasks/dispatch``). The Adapter then runs the task through
the real OpenClaw CLI.

Design rules (intentional):
- This MCP server ONLY makes an HTTP POST to the Adapter.
- It NEVER calls the ``openclaw`` CLI directly.
- It NEVER uses a shell (no ``shell=True``).

Runs as a stdio MCP server (the transport Hermes spawns via
``hermes mcp add --command <python> --args <this file>``).
"""
from __future__ import annotations

import os
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

# --- Config from environment (with safe defaults) ----------------------------
ADAPTER_URL = os.getenv(
    "OPENCLAW_ADAPTER_URL", "http://127.0.0.1:8000/tasks/dispatch"
)
ADAPTER_TOKEN = os.getenv("OPENCLAW_ADAPTER_TOKEN", "change-me")
ADAPTER_TIMEOUT_SECONDS = float(os.getenv("OPENCLAW_ADAPTER_TIMEOUT_SECONDS", "900"))

mcp = FastMCP("openclaw")


def _safe_json(resp: httpx.Response) -> Any | None:
    try:
        return resp.json()
    except Exception:  # noqa: BLE001 - non-JSON body
        return None


def _error(message: str, **extra: Any) -> dict[str, Any]:
    return {
        "ok": False,
        "adapter_status": "failed",
        "transport": "mcp->adapter",
        "error": message,
        **extra,
    }


@mcp.tool()
def dispatch_to_openclaw(
    title: str,
    goal: str,
    task_text: str,
    priority: str = "low",
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """把任務送到 OpenClaw 執行端（透過本機 Adapter /tasks/dispatch）。

    只在需要實際「執行 / 操作 / 自動化 / CLI / 跨平台」任務時使用；
    能直接回答的問題請不要用這個工具。
    高風險動作（改檔 / 刪資料 / 登入 / 操作平台 / 對外發送）請先向使用者確認。
    不要把密碼、API key、token 等敏感資訊放進 task_text 或 metadata。

    參數：
        title:     任務標題（短）
        goal:      這個任務想達成什麼
        task_text: 完整、明確、可驗證的指令（必填）
        priority:  low | normal | high（預設 low）
        metadata:  附加資訊（選填，例如 {"source": "hermes"}）

    回傳：
        Adapter 的 JSON。成功時含 ok=true / adapter_status="sent" / transport /
        task_id / openclaw_response（最終文字在 openclaw_response.payloads[0].text）。
        失敗時含 ok=false / error，視情況另有 stderr / exit_code / status_code。
    """
    payload = {
        "title": title,
        "goal": goal,
        "task_text": task_text,
        "priority": priority,
        "metadata": metadata if metadata is not None else {"source": "hermes"},
    }
    headers = {
        "Content-Type": "application/json",
        "X-Adapter-Token": ADAPTER_TOKEN,
    }

    try:
        resp = httpx.post(
            ADAPTER_URL, json=payload, headers=headers, timeout=ADAPTER_TIMEOUT_SECONDS
        )
    except httpx.ConnectError:
        return _error(
            f"無法連線到 Adapter（{ADAPTER_URL}）。請先啟動 Adapter："
            "cd ~/projects/hermes-openclaw-adapter && source .venv/bin/activate && "
            "uvicorn app.main:app --host 0.0.0.0 --port 8000 --env-file .env"
        )
    except httpx.TimeoutException:
        return _error(
            f"呼叫 Adapter 超過 {ADAPTER_TIMEOUT_SECONDS:.0f} 秒逾時。"
            "任務可能太重，或 OpenClaw 端卡住。"
        )
    except Exception as exc:  # noqa: BLE001 - surface anything unexpected clearly
        return _error(f"呼叫 Adapter 發生未預期錯誤：{type(exc).__name__}: {exc}")

    # Map common HTTP error codes to clear messages.
    if resp.status_code in (401, 403):
        return _error(
            f"Adapter 拒絕請求（HTTP {resp.status_code}）。X-Adapter-Token 可能不正確；"
            "請確認此 MCP 的 OPENCLAW_ADAPTER_TOKEN 與 Adapter 的 HERMES_ADAPTER_TOKEN 一致。",
            status_code=resp.status_code,
        )
    if resp.status_code == 422:
        return _error(
            "Adapter 回 422（欄位驗證失敗）。最常見原因是缺少必填欄位 task_text。",
            status_code=422,
            detail=_safe_json(resp),
        )
    if resp.status_code >= 500:
        return _error(
            f"Adapter 內部錯誤（HTTP {resp.status_code}）。",
            status_code=resp.status_code,
            detail=resp.text[:2000],
        )
    if resp.status_code != 200:
        return _error(
            f"Adapter 回傳非預期狀態碼（HTTP {resp.status_code}）。",
            status_code=resp.status_code,
            detail=resp.text[:2000],
        )

    # HTTP 200: return the Adapter's JSON as-is (ok / adapter_status decide success).
    parsed = _safe_json(resp)
    if parsed is None:
        return _error("Adapter 回傳非 JSON 內容。", status_code=200, raw=resp.text[:2000])
    return parsed


if __name__ == "__main__":
    # stdio transport (default). Hermes connects to this over stdin/stdout.
    mcp.run()
