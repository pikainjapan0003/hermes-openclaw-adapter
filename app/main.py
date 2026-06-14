from __future__ import annotations

import asyncio
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel, Field

APP_NAME = "Hermes OpenClaw Adapter"
DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
TASK_LOG_PATH = DATA_DIR / "tasks.jsonl"

# --- OpenClaw CLI 模式設定 ----------------------------------------------------
# 真實 OpenClaw 沒有可直接 POST 的 REST/Webhook 任務 API，它是 WebSocket Gateway。
# 最簡單的真實任務入口是 CLI：
#     openclaw agent --message "<任務>" --json
# 所以 Adapter 改成用 asyncio.create_subprocess_exec 呼叫 OpenClaw CLI（不用 shell=True）。
OPENCLAW_TRANSPORT = os.getenv("OPENCLAW_TRANSPORT", "cli").strip().lower()
OPENCLAW_CLI_BIN = os.getenv("OPENCLAW_CLI_BIN", "openclaw").strip()
OPENCLAW_CLI_TIMEOUT_SECONDS = float(os.getenv("OPENCLAW_CLI_TIMEOUT_SECONDS", "600"))
# 要跑哪個 agent（對應 `openclaw status` 顯示的 default agent，通常是 main）。
# openclaw agent 需要一個 target session，否則會回 "No target session selected"，
# 所以這裡預設 main。設成空字串才會不傳 --agent。
OPENCLAW_AGENT_ID = os.getenv("OPENCLAW_AGENT_ID", "main").strip()
# 每個 Hermes 任務用獨立 session（避免不同任務互相污染上下文）。
# 最終 session-key = agent:<agent_id>:<prefix>-<task_id>。
OPENCLAW_SESSION_KEY_PREFIX = os.getenv("OPENCLAW_SESSION_KEY_PREFIX", "hermes").strip()

HERMES_ADAPTER_TOKEN = os.getenv("HERMES_ADAPTER_TOKEN", "").strip()

app = FastAPI(
    title=APP_NAME,
    version="0.2.0",
    description="讓 Hermes 把任務送到 Adapter，再透過 OpenClaw CLI 派給真實 OpenClaw。",
)


class TaskEnvelope(BaseModel):
    """Hermes 傳給 Adapter 的任務格式。"""

    task_id: str | None = Field(default=None, description="任務 ID；不填會自動產生")
    title: str = Field(..., description="任務標題，例如：整理商品資料")
    goal: str = Field(..., description="任務目標，例如：找出商品價格與來源")
    task_text: str = Field(..., description="給 OpenClaw 的完整任務指令（instruction）")
    priority: Literal["low", "normal", "high"] = "normal"
    source: str = "hermes"
    metadata: dict[str, Any] = Field(default_factory=dict)


class DispatchResponse(BaseModel):
    """Adapter 回給 Hermes 的結果。

    成功時帶 openclaw_response；失敗時帶 error / stderr / exit_code。
    """

    ok: bool
    adapter_status: Literal["sent", "failed", "dry_run"]
    transport: str
    task_id: str
    message: str | None = None
    # 成功欄位
    openclaw_response: Any | None = None
    # 失敗欄位
    error: str | None = None
    stderr: str | None = None
    exit_code: int | None = None
    # 除錯用：實際組給 OpenClaw 的 message 與指令
    openclaw_message: str | None = None
    openclaw_command: list[str] | None = None


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def require_token(x_adapter_token: str | None) -> None:
    """簡單保護 Adapter：有設定 HERMES_ADAPTER_TOKEN 時，請求必須帶 X-Adapter-Token。"""
    if not HERMES_ADAPTER_TOKEN:
        return
    if x_adapter_token != HERMES_ADAPTER_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid or missing X-Adapter-Token")


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def append_task_log(record: dict[str, Any]) -> None:
    ensure_data_dir()
    with TASK_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def read_task_logs() -> list[dict[str, Any]]:
    if not TASK_LOG_PATH.exists():
        return []
    rows: list[dict[str, Any]] = []
    with TASK_LOG_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def build_openclaw_message(task: TaskEnvelope, task_id: str) -> str:
    """
    Adapter 的核心：把 Hermes 任務翻譯成一段清楚的文字，餵給 OpenClaw agent。

    優先使用 Hermes 傳進來的：instruction(task_text)、goal、title、metadata。
    之後若要接 WebSocket RPC 或其他模式，只要改這個 function 的輸出即可。
    """
    lines: list[str] = []
    lines.append(f"# Hermes 任務 {task_id}")
    if task.title:
        lines.append(f"標題：{task.title}")
    if task.goal:
        lines.append(f"目標：{task.goal}")
    lines.append(f"優先級：{task.priority}")
    lines.append("")
    lines.append("## 指令")
    lines.append(task.task_text.strip())

    if task.metadata:
        lines.append("")
        lines.append("## 附加資訊 (metadata)")
        lines.append(json.dumps(task.metadata, ensure_ascii=False, indent=2))

    return "\n".join(lines)


def build_openclaw_command(
    message: str, timeout_seconds: float, task_id: str
) -> list[str]:
    """組出要執行的 OpenClaw CLI 指令（list 形式，給 create_subprocess_exec 用，不經過 shell）。"""
    cmd = [
        OPENCLAW_CLI_BIN,
        "agent",
        "--message",
        message,
        "--json",
        "--timeout",
        str(int(timeout_seconds)),
    ]
    # openclaw agent 需要一個 target session。優先用 --agent + 每任務獨立的 --session-key。
    if OPENCLAW_AGENT_ID:
        cmd.extend(["--agent", OPENCLAW_AGENT_ID])
        if OPENCLAW_SESSION_KEY_PREFIX:
            cmd.extend(["--session-key", f"{OPENCLAW_SESSION_KEY_PREFIX}-{task_id}"])
    return cmd


async def run_openclaw_cli(
    message: str, timeout_seconds: float, task_id: str
) -> dict[str, Any]:
    """
    用 asyncio.create_subprocess_exec 呼叫 OpenClaw CLI（不用 shell=True）。

    回傳 dict：
      成功 -> {"ok": True, "openclaw_response": <parsed/raw>, "command": [...], "stderr": "..."}
      失敗 -> {"ok": False, "error": "...", "stderr": "...", "exit_code": <int|None>, "command": [...]}
    """
    cmd = build_openclaw_command(message, timeout_seconds, task_id)

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
    except FileNotFoundError:
        return {
            "ok": False,
            "error": f"找不到 OpenClaw CLI 執行檔：{OPENCLAW_CLI_BIN}。請確認 Adapter 跑在能存取 openclaw 的環境（WSL）。",
            "stderr": "",
            "exit_code": None,
            "command": cmd,
        }

    # 比 CLI 自身的 --timeout 再多給一點緩衝，避免 process 卡住時 Adapter 永遠等下去。
    hard_timeout = timeout_seconds + 30
    try:
        stdout_b, stderr_b = await asyncio.wait_for(
            proc.communicate(), timeout=hard_timeout
        )
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        return {
            "ok": False,
            "error": f"OpenClaw CLI 超過 {hard_timeout:.0f} 秒未回應，已強制結束。",
            "stderr": "",
            "exit_code": None,
            "command": cmd,
        }

    stdout = stdout_b.decode("utf-8", "replace").strip()
    stderr = stderr_b.decode("utf-8", "replace").strip()

    if proc.returncode != 0:
        return {
            "ok": False,
            "error": f"OpenClaw CLI 以非零代碼結束 (exit_code={proc.returncode})。",
            "stderr": stderr,
            "exit_code": proc.returncode,
            "command": cmd,
        }

    # 嘗試把 --json 輸出解析成 JSON；解析不了就回原始文字。
    parsed: Any
    try:
        parsed = json.loads(stdout)
    except json.JSONDecodeError:
        parsed = {"raw_text": stdout}

    return {
        "ok": True,
        "openclaw_response": parsed,
        "stderr": stderr,
        "exit_code": proc.returncode,
        "command": cmd,
    }


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "ok": True,
        "app": APP_NAME,
        "transport": OPENCLAW_TRANSPORT,
        "openclaw_cli_bin": OPENCLAW_CLI_BIN,
        "openclaw_cli_timeout_seconds": OPENCLAW_CLI_TIMEOUT_SECONDS,
        "token_required": bool(HERMES_ADAPTER_TOKEN),
    }


@app.post("/tasks/dispatch", response_model=DispatchResponse)
async def dispatch_task(
    task: TaskEnvelope,
    request: Request,
    x_adapter_token: str | None = Header(default=None),
) -> DispatchResponse:
    """
    Hermes 呼叫這個 API，Adapter 會用 OpenClaw CLI 把任務派給真實 OpenClaw。
    """
    require_token(x_adapter_token)

    task_id = task.task_id or f"task-{uuid.uuid4().hex[:12]}"
    message = build_openclaw_message(task, task_id)

    base_log = {
        "task_id": task_id,
        "received_at": utc_now_iso(),
        "transport": OPENCLAW_TRANSPORT,
        "client_host": request.client.host if request.client else None,
        "hermes_task": task.model_dump(),
        "openclaw_message": message,
    }

    # dry_run：不真的呼叫 OpenClaw，只組 message（方便沒裝 OpenClaw 時測流程）。
    if OPENCLAW_TRANSPORT != "cli":
        append_task_log({**base_log, "adapter_status": "dry_run"})
        return DispatchResponse(
            ok=True,
            adapter_status="dry_run",
            transport=OPENCLAW_TRANSPORT,
            task_id=task_id,
            message=(
                f"OPENCLAW_TRANSPORT={OPENCLAW_TRANSPORT}（非 cli），"
                "只組出 OpenClaw message，沒有真的呼叫 CLI。"
            ),
            openclaw_message=message,
        )

    result = await run_openclaw_cli(message, OPENCLAW_CLI_TIMEOUT_SECONDS, task_id)

    if result["ok"]:
        append_task_log(
            {
                **base_log,
                "adapter_status": "sent",
                "openclaw_command": result["command"],
                "openclaw_response": result["openclaw_response"],
                "stderr": result.get("stderr", ""),
            }
        )
        return DispatchResponse(
            ok=True,
            adapter_status="sent",
            transport="cli",
            task_id=task_id,
            message="任務已透過 OpenClaw CLI 送出。",
            openclaw_response=result["openclaw_response"],
            openclaw_message=message,
            openclaw_command=result["command"],
        )

    append_task_log(
        {
            **base_log,
            "adapter_status": "failed",
            "openclaw_command": result.get("command"),
            "error": result.get("error"),
            "stderr": result.get("stderr", ""),
            "exit_code": result.get("exit_code"),
        }
    )
    return DispatchResponse(
        ok=False,
        adapter_status="failed",
        transport="cli",
        task_id=task_id,
        message="任務透過 OpenClaw CLI 送出失敗，請檢查下方 error / stderr。",
        error=result.get("error"),
        stderr=result.get("stderr", ""),
        exit_code=result.get("exit_code"),
        openclaw_message=message,
        openclaw_command=result.get("command"),
    )


@app.get("/tasks/{task_id}")
def get_task(task_id: str, x_adapter_token: str | None = Header(default=None)) -> dict[str, Any]:
    require_token(x_adapter_token)
    rows = [row for row in read_task_logs() if row.get("task_id") == task_id]
    if not rows:
        raise HTTPException(status_code=404, detail="Task not found")
    return rows[-1]


@app.get("/tasks")
def list_tasks(x_adapter_token: str | None = Header(default=None)) -> dict[str, Any]:
    require_token(x_adapter_token)
    rows = read_task_logs()
    return {"count": len(rows), "items": rows[-50:]}
