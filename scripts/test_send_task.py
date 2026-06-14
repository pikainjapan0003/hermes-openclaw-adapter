from __future__ import annotations

import os
import sys

import httpx

ADAPTER_URL = os.getenv("ADAPTER_URL", "http://127.0.0.1:8000")
ADAPTER_TOKEN = os.getenv("HERMES_ADAPTER_TOKEN", "change-me")

# 安全測試任務：只要 OpenClaw 回覆 PONG，不要做任何有副作用的動作。
payload = {
    "title": "Adapter → OpenClaw CLI 連線測試 (PONG)",
    "goal": "確認 Adapter 能透過 OpenClaw CLI 真實跑一次 agent",
    "task_text": "請只回覆 PONG，不要操作任何檔案、不要執行外部動作。",
    "priority": "normal",
    "metadata": {
        "example": True,
        "safe_test": True,
        "workflow": "hermes-adapter-openclaw-cli",
    },
}

headers = {"Content-Type": "application/json"}
if ADAPTER_TOKEN:
    headers["X-Adapter-Token"] = ADAPTER_TOKEN

# OpenClaw agent 可能要跑數十秒～數百秒，所以 HTTP 端逾時必須比 CLI 逾時更長。
HTTP_TIMEOUT = float(os.getenv("TEST_HTTP_TIMEOUT_SECONDS", "660"))

try:
    response = httpx.post(
        f"{ADAPTER_URL}/tasks/dispatch",
        json=payload,
        headers=headers,
        timeout=HTTP_TIMEOUT,
    )
    print("HTTP", response.status_code)
    print(response.text)
    response.raise_for_status()
except Exception as exc:
    print(f"測試失敗：{exc}", file=sys.stderr)
    sys.exit(1)
