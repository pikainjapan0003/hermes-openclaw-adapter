from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import os
import re
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import httpx
from fastapi import BackgroundTasks, FastAPI, Header, HTTPException, Request
from pydantic import BaseModel, Field

from app.queue_store import QueueStore

APP_NAME = "Hermes OpenClaw Adapter"
APP_VERSION = "0.5.0"

# --- Paths -------------------------------------------------------------------
DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
TASKS_PATH = DATA_DIR / "tasks.jsonl"
RESULTS_PATH = DATA_DIR / "results.jsonl"
CALLBACKS_PATH = DATA_DIR / "callbacks.jsonl"
CALLBACK_ERRORS_PATH = DATA_DIR / "callback_errors.jsonl"

# --- OpenClaw CLI config -----------------------------------------------------
# 真實 OpenClaw 沒有可直接 POST 的 REST/Webhook 任務 API，它是 WebSocket Gateway。
# 最簡單的真實任務入口是 CLI：openclaw agent --message "<任務>" --json
OPENCLAW_CLI_BIN = os.getenv("OPENCLAW_CLI_BIN", "openclaw").strip()
OPENCLAW_AGENT_ID = os.getenv("OPENCLAW_AGENT_ID", "main").strip()
OPENCLAW_SESSION_KEY_PREFIX = os.getenv("OPENCLAW_SESSION_KEY_PREFIX", "hermes").strip()
# v0.4: default 180s (fallback to the older var name if present).
OPENCLAW_TIMEOUT_SECONDS = float(
    os.getenv("OPENCLAW_TIMEOUT_SECONDS", os.getenv("OPENCLAW_CLI_TIMEOUT_SECONDS", "180"))
)

HERMES_ADAPTER_TOKEN = os.getenv("HERMES_ADAPTER_TOKEN", "").strip()


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


# --- Callback config ---------------------------------------------------------
CALLBACK_ENABLED = _env_bool("CALLBACK_ENABLED", True)
HERMES_CALLBACK_MODE = os.getenv("HERMES_CALLBACK_MODE", "ledger_only").strip().lower()
HERMES_CALLBACK_URL = os.getenv(
    "HERMES_CALLBACK_URL", "http://127.0.0.1:8644/webhooks/openclaw-result"
).strip()
HERMES_CALLBACK_SECRET = os.getenv("HERMES_CALLBACK_SECRET", "").strip()
CALLBACK_MAX_RETRIES = int(os.getenv("CALLBACK_MAX_RETRIES", "3"))
CALLBACK_TIMEOUT_SECONDS = float(os.getenv("CALLBACK_TIMEOUT_SECONDS", "20"))

# v0.4 第一版只允許 Level 0 / 1 自動執行。
MAX_AUTO_SAFETY_LEVEL = 1

# --- v0.5 Queue Worker config ------------------------------------------------
# EXECUTION_MODE:
#   queue      = 寫入本地 SQLite queue，由 `python -m app.worker` 執行（v0.5 預設）
#   background = v0.4 舊行為，直接用 FastAPI BackgroundTasks 執行（不需 worker）
EXECUTION_MODE = os.getenv("EXECUTION_MODE", "queue").strip().lower()
QUEUE_DB_PATH = os.getenv("QUEUE_DB_PATH", str(DATA_DIR / "queue.db"))
QUEUE_MAX_ATTEMPTS = int(os.getenv("QUEUE_MAX_ATTEMPTS", "3"))

# 懶初始化 queue store（background 模式完全用不到，不會建立 db）。
_queue_store: QueueStore | None = None


def get_queue() -> QueueStore:
    global _queue_store
    if _queue_store is None:
        ensure_data_dir()
        _queue_store = QueueStore(QUEUE_DB_PATH)
    return _queue_store

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="Hermes → MCP → Adapter →（背景執行 OpenClaw CLI）→ callback Hermes。",
)


# =============================================================================
# Models
# =============================================================================
class TaskEnvelope(BaseModel):
    """Hermes 傳給 Adapter 的任務格式（與舊版相容）。"""

    task_id: str | None = Field(default=None, description="任務 ID；不填會自動產生")
    title: str = Field(..., description="任務標題")
    goal: str = Field(..., description="任務目標")
    task_text: str = Field(..., description="給 OpenClaw 的完整任務指令（必填）")
    priority: Literal["low", "normal", "high"] = "normal"
    source: str = "hermes"
    metadata: dict[str, Any] = Field(default_factory=dict)


class OpenClawCliError(Exception):
    def __init__(self, code: str, message: str, retryable: bool) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.retryable = retryable


# =============================================================================
# Small helpers
# =============================================================================
def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


_write_lock = threading.Lock()


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def append_jsonl(path: Path, record: dict[str, Any]) -> None:
    ensure_data_dir()
    line = json.dumps(record, ensure_ascii=False)
    with _write_lock:
        with path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def append_task_status(task_id: str, status: str, **extra: Any) -> None:
    record = {"task_id": task_id, "status": status, "ts": utc_now_iso(), **extra}
    append_jsonl(TASKS_PATH, record)


def latest_task(task_id: str) -> dict[str, Any] | None:
    match = [r for r in read_jsonl(TASKS_PATH) if r.get("task_id") == task_id]
    return match[-1] if match else None


def find_result(task_id: str) -> dict[str, Any] | None:
    match = [r for r in read_jsonl(RESULTS_PATH) if r.get("task_id") == task_id]
    return match[-1] if match else None


def require_token(x_adapter_token: str | None) -> None:
    if not HERMES_ADAPTER_TOKEN:
        return
    if x_adapter_token != HERMES_ADAPTER_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid or missing X-Adapter-Token")


def parse_safety_level(metadata: dict[str, Any]) -> tuple[int, bool]:
    """Return (level, assumed). assumed=True only when safety_level is absent.

    Accepts "Level 0", "level_0", "0", 0, etc. If present but unparseable,
    returns a high level (99) so it is treated as high-risk and refused.
    """
    raw = metadata.get("safety_level")
    if raw is None or (isinstance(raw, str) and raw.strip() == ""):
        return 0, True
    m = re.search(r"(\d+)", str(raw))
    if not m:
        return 99, False
    return int(m.group(1)), False


def extract_result_text(stdout: str) -> str:
    """Pull the final assistant text out of `openclaw agent --json` output."""
    try:
        data = json.loads(stdout)
    except json.JSONDecodeError:
        return stdout.strip()
    if isinstance(data, dict):
        payloads = data.get("payloads")
        if isinstance(payloads, list) and payloads and isinstance(payloads[0], dict):
            text = payloads[0].get("text")
            if text:
                return str(text)
        meta = data.get("meta") if isinstance(data.get("meta"), dict) else {}
        agent_meta = meta.get("agentMeta") if isinstance(meta.get("agentMeta"), dict) else {}
        text = agent_meta.get("finalAssistantVisibleText")
        if text:
            return str(text)
    return stdout.strip()


def build_openclaw_message(task: TaskEnvelope, task_id: str) -> str:
    lines: list[str] = [f"# Hermes 任務 {task_id}"]
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


def build_openclaw_command(message: str, timeout_seconds: float, task_id: str) -> list[str]:
    cmd = [
        OPENCLAW_CLI_BIN,
        "agent",
        "--message",
        message,
        "--json",
        "--timeout",
        str(int(timeout_seconds)),
    ]
    if OPENCLAW_AGENT_ID:
        cmd.extend(["--agent", OPENCLAW_AGENT_ID])
        if OPENCLAW_SESSION_KEY_PREFIX:
            cmd.extend(["--session-key", f"{OPENCLAW_SESSION_KEY_PREFIX}-{task_id}"])
    return cmd


# =============================================================================
# OpenClaw CLI execution (no shell=True, never crashes the Adapter)
# =============================================================================
async def run_openclaw_cli(message: str, timeout_seconds: float, task_id: str) -> str:
    """Run `openclaw agent ... --json` and return stdout. Raise OpenClawCliError on failure."""
    cmd = build_openclaw_command(message, timeout_seconds, task_id)
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
    except FileNotFoundError:
        raise OpenClawCliError(
            "OPENCLAW_CLI_NOT_FOUND",
            f"找不到 OpenClaw CLI 執行檔：{OPENCLAW_CLI_BIN}。請確認 Adapter 跑在能存取 openclaw 的環境（WSL）。",
            retryable=False,
        )

    hard_timeout = timeout_seconds + 30
    try:
        stdout_b, stderr_b = await asyncio.wait_for(proc.communicate(), timeout=hard_timeout)
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        raise OpenClawCliError(
            "OPENCLAW_TIMEOUT",
            f"OpenClaw CLI 超過 {hard_timeout:.0f} 秒未回應，已強制結束。",
            retryable=True,
        )

    stdout = stdout_b.decode("utf-8", "replace").strip()
    stderr = stderr_b.decode("utf-8", "replace").strip()

    if proc.returncode != 0:
        raise OpenClawCliError(
            "OPENCLAW_CLI_ERROR",
            stderr or f"OpenClaw CLI 以非零代碼結束 (exit_code={proc.returncode})。",
            retryable=True,
        )
    return stdout


def build_task_result(
    *,
    task_id: str,
    correlation_id: str,
    status: str,
    title: str,
    goal: str,
    result_text: str,
    error: dict[str, Any] | None,
) -> dict[str, Any]:
    summary = "OpenClaw 已完成任務。" if status == "completed" else "OpenClaw 執行失敗。"
    return {
        "schema_version": "v1",
        "task_id": task_id,
        "correlation_id": correlation_id,
        "status": status,
        "finished_at": int(time.time()),
        "title": title,
        "goal": goal,
        "summary": summary,
        "result_text": result_text,
        "error": error,
    }


# =============================================================================
# Background runner
# =============================================================================
async def run_openclaw_and_callback(
    task_dict: dict[str, Any], task_id: str, correlation_id: str
) -> None:
    """Run the task in the background; never raises (logs a failed result instead)."""
    try:
        envelope = TaskEnvelope(**task_dict)
        append_task_status(task_id, "running", correlation_id=correlation_id)
        message = build_openclaw_message(envelope, task_id)

        try:
            stdout = await run_openclaw_cli(message, OPENCLAW_TIMEOUT_SECONDS, task_id)
            result_text = extract_result_text(stdout)
            result = build_task_result(
                task_id=task_id,
                correlation_id=correlation_id,
                status="completed",
                title=envelope.title,
                goal=envelope.goal,
                result_text=result_text,
                error=None,
            )
        except OpenClawCliError as exc:
            result = build_task_result(
                task_id=task_id,
                correlation_id=correlation_id,
                status="failed",
                title=envelope.title,
                goal=envelope.goal,
                result_text="",
                error={"code": exc.code, "message": exc.message, "retryable": exc.retryable},
            )

        append_jsonl(RESULTS_PATH, result)
        append_task_status(task_id, result["status"], correlation_id=correlation_id)

        if CALLBACK_ENABLED:
            await send_callback_to_hermes(result)

    except Exception as exc:  # noqa: BLE001 - background must never crash the server
        result = build_task_result(
            task_id=task_id,
            correlation_id=correlation_id,
            status="failed",
            title=str(task_dict.get("title", "")),
            goal=str(task_dict.get("goal", "")),
            result_text="",
            error={
                "code": "ADAPTER_INTERNAL_ERROR",
                "message": f"{type(exc).__name__}: {exc}",
                "retryable": False,
            },
        )
        append_jsonl(RESULTS_PATH, result)
        append_task_status(task_id, "failed", correlation_id=correlation_id)
        if CALLBACK_ENABLED:
            try:
                await send_callback_to_hermes(result)
            except Exception:  # noqa: BLE001
                pass


# =============================================================================
# Callback sender
# =============================================================================
async def send_callback_to_hermes(result: dict[str, Any]) -> None:
    """ledger_only: no HTTP (results.jsonl is the ledger). http: POST with HMAC + retries."""
    if HERMES_CALLBACK_MODE != "http":
        # ledger_only (default): the result already lives in results.jsonl.
        return

    body_bytes = json.dumps(result, ensure_ascii=False).encode("utf-8")
    signature = hmac.new(
        HERMES_CALLBACK_SECRET.encode("utf-8"), body_bytes, hashlib.sha256
    ).hexdigest()
    headers = {
        "Content-Type": "application/json",
        "X-Hermes-OpenClaw-Signature": f"sha256={signature}",
    }

    last_error = ""
    for attempt in range(1, CALLBACK_MAX_RETRIES + 1):
        try:
            async with httpx.AsyncClient(timeout=CALLBACK_TIMEOUT_SECONDS) as client:
                resp = await client.post(HERMES_CALLBACK_URL, content=body_bytes, headers=headers)
            if 200 <= resp.status_code < 300:
                append_jsonl(
                    CALLBACKS_PATH,
                    {
                        "task_id": result.get("task_id"),
                        "correlation_id": result.get("correlation_id"),
                        "ts": utc_now_iso(),
                        "url": HERMES_CALLBACK_URL,
                        "status_code": resp.status_code,
                        "attempt": attempt,
                    },
                )
                return
            last_error = f"HTTP {resp.status_code}: {resp.text[:500]}"
        except Exception as exc:  # noqa: BLE001
            last_error = f"{type(exc).__name__}: {exc}"

        if attempt < CALLBACK_MAX_RETRIES:
            await asyncio.sleep(min(2 ** attempt, 10))

    append_jsonl(
        CALLBACK_ERRORS_PATH,
        {
            "task_id": result.get("task_id"),
            "correlation_id": result.get("correlation_id"),
            "ts": utc_now_iso(),
            "url": HERMES_CALLBACK_URL,
            "attempts": CALLBACK_MAX_RETRIES,
            "error": last_error,
        },
    )


# =============================================================================
# Endpoints
# =============================================================================
@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "ok": True,
        "app": APP_NAME,
        "version": APP_VERSION,
        "mode": "queue-worker" if EXECUTION_MODE != "background" else "async-background+callback",
        "execution_mode": EXECUTION_MODE,
        "queue_db_path": QUEUE_DB_PATH if EXECUTION_MODE != "background" else None,
        "openclaw_cli_bin": OPENCLAW_CLI_BIN,
        "openclaw_timeout_seconds": OPENCLAW_TIMEOUT_SECONDS,
        "callback_enabled": CALLBACK_ENABLED,
        "callback_mode": HERMES_CALLBACK_MODE,
        "token_required": bool(HERMES_ADAPTER_TOKEN),
    }


@app.post("/tasks/dispatch")
async def dispatch_task(
    task: TaskEnvelope,
    request: Request,
    background_tasks: BackgroundTasks,
    x_adapter_token: str | None = Header(default=None),
) -> dict[str, Any]:
    """非同步派工：立刻回 accepted，OpenClaw 在背景執行，完成後寫 results + callback。"""
    require_token(x_adapter_token)

    task_id = task.task_id or f"task-{uuid.uuid4().hex[:12]}"
    correlation_id = str(task.metadata.get("correlation_id") or f"corr-{uuid.uuid4().hex[:12]}")
    level, assumed = parse_safety_level(task.metadata)

    common = {
        "correlation_id": correlation_id,
        "title": task.title,
        "goal": task.goal,
        "priority": task.priority,
        "safety_level": level,
        "assumed_safety_level": assumed,
        "metadata": task.metadata,
    }

    # --- Safety gate: only Level 0 / 1 auto-run in v0.4 ---
    if level > MAX_AUTO_SAFETY_LEVEL:
        if level >= 3:
            reason = "High risk task requires human confirmation before OpenClaw execution."
        elif level == 2:
            reason = "Level 2 tasks are not auto-run in v0.4 (only Level 0/1). Needs human review."
        else:
            reason = "Unrecognized safety_level; refusing to auto-run. Please set safety_level to 0 or 1."
        append_task_status(task_id, "rejected", reason=reason, **common)
        return {"status": "rejected", "task_id": task_id, "reason": reason}

    # --- Accept: 寫 ledger（tasks.jsonl）→ 排程執行 ---
    append_task_status(
        task_id,
        "queued",
        client_host=request.client.host if request.client else None,
        hermes_task=task.model_dump(),
        execution_mode=EXECUTION_MODE,
        **common,
    )

    if EXECUTION_MODE == "background":
        # v0.4 舊路徑：FastAPI BackgroundTasks 直接執行（不需要 worker）。
        background_tasks.add_task(
            run_openclaw_and_callback, task.model_dump(), task_id, correlation_id
        )
    else:
        # v0.5 路徑：寫入持久化 queue，由 app.worker 取出執行。
        get_queue().enqueue(
            task_id=task_id,
            title=task.title,
            task_text=task.task_text,
            safety_level=level,
            payload=task.model_dump(),
            correlation_id=correlation_id,
            max_attempts=QUEUE_MAX_ATTEMPTS,
        )

    return {
        "status": "accepted",
        "task_id": task_id,
        "correlation_id": correlation_id,
        "assumed_safety_level": assumed,
        "execution_mode": EXECUTION_MODE,
        "message": "任務已送出，OpenClaw 會在背景執行，完成後寫入 results.jsonl。",
    }


def _queue_state(task_id: str) -> dict[str, Any] | None:
    """v0.5：附帶 queue 內部狀態（background 模式下為 None，向後相容）。"""
    if EXECUTION_MODE == "background":
        return None
    try:
        return get_queue().get(task_id)
    except Exception:  # noqa: BLE001 - 查詢端點不該因 queue 故障而 500
        return None


@app.get("/tasks/{task_id}/result")
def get_task_result(task_id: str, x_adapter_token: str | None = Header(default=None)) -> dict[str, Any]:
    require_token(x_adapter_token)
    task = latest_task(task_id)
    result = find_result(task_id)
    queue_item = _queue_state(task_id)
    if task is None and result is None and queue_item is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if result is not None:
        return {"task_id": task_id, "task": task, "result": result, "queue": queue_item}
    status = (queue_item or {}).get("status") or (task.get("status") if task else "unknown")
    return {"task_id": task_id, "status": status, "result": None, "queue": queue_item}


@app.get("/tasks/{task_id}")
def get_task(task_id: str, x_adapter_token: str | None = Header(default=None)) -> dict[str, Any]:
    require_token(x_adapter_token)
    task = latest_task(task_id)
    queue_item = _queue_state(task_id)
    if task is None and queue_item is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return {
        "task_id": task_id,
        "task": task,
        "result": find_result(task_id),
        "queue": queue_item,
    }


@app.post("/tasks/{task_id}/cancel")
def cancel_task(task_id: str, x_adapter_token: str | None = Header(default=None)) -> dict[str, Any]:
    """只能取消仍在 queued 的任務（running/completed/failed 無法取消）。"""
    require_token(x_adapter_token)
    if EXECUTION_MODE == "background":
        raise HTTPException(status_code=400, detail="Cancel only supported in queue execution mode.")
    item = get_queue().get(task_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Task not found in queue")
    if get_queue().cancel_if_queued(task_id):
        append_task_status(task_id, "cancelled")
        return {"task_id": task_id, "status": "cancelled"}
    return {
        "task_id": task_id,
        "status": item["status"],
        "message": "Only queued tasks can be cancelled.",
    }


@app.get("/queue")
def queue_overview(x_adapter_token: str | None = Header(default=None)) -> dict[str, Any]:
    require_token(x_adapter_token)
    if EXECUTION_MODE == "background":
        return {"execution_mode": EXECUTION_MODE, "counts": {}, "items": []}
    q = get_queue()
    return {"execution_mode": EXECUTION_MODE, "counts": q.counts(), "items": q.list(limit=50)}


@app.get("/tasks")
def list_tasks(x_adapter_token: str | None = Header(default=None)) -> dict[str, Any]:
    require_token(x_adapter_token)
    rows = read_jsonl(TASKS_PATH)
    return {"count": len(rows), "items": rows[-50:]}
