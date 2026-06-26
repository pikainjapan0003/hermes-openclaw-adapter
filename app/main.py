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
from fastapi import BackgroundTasks, FastAPI, Form, Header, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from app.blackboard_store import (
    VALID_AUTHOR_TYPES,
    BlackboardStore,
    CommentValidationError,
)
from app.health_store import (
    DEFAULT_WORKER_ID,
    WORKER_HEARTBEAT_STALE_SECONDS,
    HealthStore,
)
from app.queue_store import (
    ARCHIVED,
    QUEUED,
    REJECTED,
    VALID_STATUSES,
    WAITING_REVIEW,
    QueueStore,
)

APP_NAME = "Hermes OpenClaw Adapter"
APP_VERSION = "0.5.6"

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


# v0.5.3：Blackboard / task comments 獨立儲存層（共用 db 檔，但只動 task_comments 表）。
_blackboard_store: BlackboardStore | None = None


def get_blackboard() -> BlackboardStore:
    global _blackboard_store
    if _blackboard_store is None:
        ensure_data_dir()
        _blackboard_store = BlackboardStore(QUEUE_DB_PATH)
    return _blackboard_store


# v0.5.6：System Health / Worker Heartbeat 獨立儲存層（共用 db 檔，只動 worker_heartbeats 表）。
WORKER_ID = os.getenv("WORKER_ID", DEFAULT_WORKER_ID).strip() or DEFAULT_WORKER_ID
_health_store: HealthStore | None = None


def get_health() -> HealthStore:
    global _health_store
    if _health_store is None:
        ensure_data_dir()
        _health_store = HealthStore(QUEUE_DB_PATH)
    return _health_store


def _task_exists(task_id: str) -> bool:
    """任務是否存在於 queue（用於避免孤兒留言）。background 模式無 queue → False。唯讀。"""
    if EXECUTION_MODE == "background":
        return False
    try:
        return get_queue().get(task_id) is not None
    except Exception:  # noqa: BLE001 - 查詢失敗時保守當作不存在
        return False

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


# v0.5.4 Approval Flow：safety_level >= 此值（或 requires_confirmation=true）→ waiting_review。
REVIEW_SAFETY_LEVEL = 3


def _coerce_bool(raw: Any) -> bool:
    """寬鬆地把 metadata 值轉成 bool；無法判定一律 False（向後相容）。"""
    if isinstance(raw, bool):
        return raw
    if isinstance(raw, (int, float)):
        return raw != 0
    if isinstance(raw, str):
        return raw.strip().lower() in ("1", "true", "yes", "on")
    return False


def needs_human_review(metadata: dict[str, Any]) -> tuple[bool, bool]:
    """v0.5.4：判斷任務是否要進 waiting_review。回傳 (needs_review, requires_confirmation)。

    規則：
    - requires_confirmation == true → 需審核。
    - safety_level 為「可解析的整數」且 >= 3 → 需審核。
    向後相容（皆 → 不需審核 → 照舊 queued）：
    - 沒有 metadata、requires_confirmation 缺失。
    - safety_level 缺失或無法解析為數字（不會被誤判成高風險）。
    """
    requires_confirmation = _coerce_bool(metadata.get("requires_confirmation"))

    high_level = False
    raw = metadata.get("safety_level")
    if raw is not None and not (isinstance(raw, str) and raw.strip() == ""):
        m = re.search(r"(\d+)", str(raw))
        if m and int(m.group(1)) >= REVIEW_SAFETY_LEVEL:
            high_level = True

    return (requires_confirmation or high_level), requires_confirmation


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

    needs_review, requires_confirmation = needs_human_review(task.metadata)

    common = {
        "correlation_id": correlation_id,
        "title": task.title,
        "goal": task.goal,
        "priority": task.priority,
        "safety_level": level,
        "assumed_safety_level": assumed,
        "requires_confirmation": requires_confirmation,
        "metadata": task.metadata,
    }

    # --- v0.5.4 Approval gate：safety_level >= 3 或 requires_confirmation → waiting_review ---
    if needs_review:
        if EXECUTION_MODE == "background":
            # 背景模式沒有持久化 queue 可暫存待審任務 → 維持「高風險不自動跑」的保守行為。
            reason = (
                "需人工確認的任務無法在 background 執行模式排隊待審（沒有持久化 queue）。"
                "請改用 queue 執行模式，任務會進 waiting_review 等待 approve。"
            )
            append_task_status(task_id, "rejected", reason=reason, **common)
            return {"status": "rejected", "task_id": task_id, "reason": reason}

        append_task_status(
            task_id,
            "waiting_review",
            client_host=request.client.host if request.client else None,
            hermes_task=task.model_dump(),
            execution_mode=EXECUTION_MODE,
            **common,
        )
        get_queue().enqueue(
            task_id=task_id,
            title=task.title,
            task_text=task.task_text,
            safety_level=level,
            payload=task.model_dump(),
            correlation_id=correlation_id,
            max_attempts=QUEUE_MAX_ATTEMPTS,
            initial_status=WAITING_REVIEW,
        )
        return {
            "status": "waiting_review",
            "task_id": task_id,
            "correlation_id": correlation_id,
            "safety_level": level,
            "requires_confirmation": requires_confirmation,
            "execution_mode": EXECUTION_MODE,
            "message": "任務需人工確認，已進入 waiting_review。approve 後才會被 worker 執行。",
        }

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
            initial_status=QUEUED,
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


class ControlBody(BaseModel):
    """v0.5.5 cancel / retry / archive 的 request body（reason 選填）。"""

    reason: str | None = Field(default=None, description="動作原因（選填）")


@app.post("/tasks/{task_id}/cancel")
def cancel_task(
    task_id: str,
    body: ControlBody | None = None,
    x_adapter_token: str | None = Header(default=None),
) -> dict[str, Any]:
    """v0.5.5：取消 queued / waiting_review 任務 -> cancelled。

    不取消 running（不做 kill worker）。狀態不允許回 409、不存在回 404。
    （沿用既有 QueueStore.cancel_if_queued 方法保留不動，這裡改用更嚴格的
     cancel_control，額外支援 waiting_review 並對非法狀態回 409。）
    """
    require_token(x_adapter_token)
    reason = body.reason if body else None
    return _run_control(
        task_id, action="cancel",
        method=lambda q: q.cancel_control(task_id, reason=reason),
        reason=reason,
    )


@app.post("/tasks/{task_id}/retry")
def retry_task(
    task_id: str,
    body: ControlBody | None = None,
    x_adapter_token: str | None = Header(default=None),
) -> dict[str, Any]:
    """v0.5.5：重試 failed 任務 -> queued。不直接啟動 worker。狀態不允許回 409。"""
    require_token(x_adapter_token)
    reason = body.reason if body else None
    return _run_control(
        task_id, action="retry",
        method=lambda q: q.retry_failed(task_id, reason=reason),
        reason=reason,
    )


@app.post("/tasks/{task_id}/archive")
def archive_task(
    task_id: str,
    body: ControlBody | None = None,
    x_adapter_token: str | None = Header(default=None),
) -> dict[str, Any]:
    """v0.5.5：封存 completed/failed/cancelled/rejected 任務 -> archived（只收納不刪資料）。"""
    require_token(x_adapter_token)
    reason = body.reason if body else None
    return _run_control(
        task_id, action="archive",
        method=lambda q: q.archive(task_id, reason=reason),
        reason=reason,
    )


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


# =============================================================================
# v0.5.1 Queue Observability — 唯讀觀測 API
#
# 原則：所有 /queue/* 觀測端點只讀 queue（SELECT）與既有 ledger（tasks/results.jsonl），
# 絕不修改 queue 狀態、不觸發 worker claim/retry/cancel、不呼叫 OpenClaw CLI。
# background 執行模式下沒有持久化 queue，回傳空集合 / 404 而非報錯。
# =============================================================================
OBSERVABILITY_MODE = "queue-observability"

# 觀測端點對外公開的狀態白名單（沿用 queue_store 的合法狀態）。
# v0.5.4：加入 waiting_review / rejected。
_OBS_COUNT_KEYS = (
    "queued", "running", "completed", "failed", "cancelled",
    "waiting_review", "rejected", "archived",
)


def _parse_payload_metadata(payload_json: str | None) -> dict[str, Any]:
    """從 queue row 的 payload(JSON 字串) 取出 metadata。失敗回 {}。唯讀。"""
    if not payload_json:
        return {}
    try:
        payload = json.loads(payload_json)
    except (json.JSONDecodeError, TypeError):
        return {}
    md = payload.get("metadata") if isinstance(payload, dict) else None
    return md if isinstance(md, dict) else {}


def _obs_worker_status(counts: dict[str, int]) -> dict[str, Any]:
    """無 worker 心跳機制；用是否有 running 任務做保守推斷（唯讀，不代表確定在線）。"""
    status = "online" if counts.get("running", 0) > 0 else "unknown"
    return {"status": status, "last_seen": None}


def _obs_task_summary(item: dict[str, Any]) -> dict[str, Any]:
    """列表用的精簡任務樣貌。"""
    return {
        "task_id": item.get("task_id"),
        "status": item.get("status"),
        "title": item.get("title"),
        "created_at": item.get("created_at"),
        "updated_at": item.get("updated_at"),
        "attempts": item.get("attempts"),
        "max_attempts": item.get("max_attempts"),
        "error_message": item.get("error"),
    }


def _obs_task_detail(item: dict[str, Any]) -> dict[str, Any]:
    """單筆任務詳情。started_at 取自 tasks.jsonl 首筆 running；finished_at / result_text 取自 results.jsonl。"""
    task_id = item["task_id"]
    result = find_result(task_id)
    started_at = None
    for r in read_jsonl(TASKS_PATH):
        if r.get("task_id") == task_id and r.get("status") == "running":
            started_at = r.get("ts")
            break
    return {
        "task_id": task_id,
        "status": item.get("status"),
        "title": item.get("title"),
        "task_text": item.get("task_text"),
        "created_at": item.get("created_at"),
        "updated_at": item.get("updated_at"),
        "started_at": started_at,
        "finished_at": (result or {}).get("finished_at"),
        "attempts": item.get("attempts"),
        "max_attempts": item.get("max_attempts"),
        "result_text": (result or {}).get("result_text"),
        "error_message": item.get("error"),
        "metadata": _parse_payload_metadata(item.get("payload")),
    }


def _obs_counts_total() -> tuple[dict[str, int], int]:
    """共用唯讀 helper：取 queue 各狀態計數與總數（background 模式回全 0）。"""
    if EXECUTION_MODE == "background":
        return {k: 0 for k in _OBS_COUNT_KEYS}, 0
    q = get_queue()
    return q.counts_by_status(), q.total()


@app.get("/queue/overview")
def queue_obs_overview(x_adapter_token: str | None = Header(default=None)) -> dict[str, Any]:
    require_token(x_adapter_token)
    counts, total = _obs_counts_total()
    return {
        "version": APP_VERSION,
        "mode": OBSERVABILITY_MODE,
        "counts": counts,
        "total": total,
        "worker": _obs_worker_status(counts),
        "generated_at": utc_now_iso(),
    }


@app.get("/queue/tasks")
def queue_obs_tasks(
    status: str | None = None,
    limit: int = 20,
    offset: int = 0,
    x_adapter_token: str | None = Header(default=None),
) -> dict[str, Any]:
    require_token(x_adapter_token)
    limit = max(1, min(limit, 200))
    offset = max(0, offset)
    if status is not None and status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    if EXECUTION_MODE == "background":
        return {"items": [], "limit": limit, "offset": offset, "total": 0}
    items, total = get_queue().list_page(status=status, limit=limit, offset=offset)
    return {
        "items": [_obs_task_summary(i) for i in items],
        "limit": limit,
        "offset": offset,
        "total": total,
    }


@app.get("/queue/recent-errors")
def queue_obs_recent_errors(
    limit: int = 10,
    x_adapter_token: str | None = Header(default=None),
) -> dict[str, Any]:
    require_token(x_adapter_token)
    limit = max(1, min(limit, 200))
    if EXECUTION_MODE == "background":
        return {"items": []}
    items = get_queue().recent_failed(limit=limit)
    return {
        "items": [
            {
                "task_id": i.get("task_id"),
                "title": i.get("title"),
                "error_message": i.get("error"),
                "updated_at": i.get("updated_at"),
            }
            for i in items
        ]
    }


@app.get("/queue/health")
def queue_obs_health(x_adapter_token: str | None = Header(default=None)) -> dict[str, Any]:
    require_token(x_adapter_token)
    if EXECUTION_MODE == "background":
        return {
            "ok": True,
            "queue_db_exists": False,
            "queue_db_path": None,
            "counts": {},
            "execution_mode": EXECUTION_MODE,
        }
    db_exists = Path(QUEUE_DB_PATH).exists()
    counts: dict[str, int] = {}
    ok = True
    try:
        counts = get_queue().counts_by_status()
    except Exception:  # noqa: BLE001 - 觀測端點不該因 queue 故障而 500
        ok = False
    return {
        "ok": ok,
        "queue_db_exists": db_exists,
        "queue_db_path": QUEUE_DB_PATH,
        "counts": counts,
        "execution_mode": EXECUTION_MODE,
    }


@app.get("/queue/tasks/{task_id}")
def queue_obs_task_detail(
    task_id: str, x_adapter_token: str | None = Header(default=None)
) -> dict[str, Any]:
    require_token(x_adapter_token)
    if EXECUTION_MODE == "background":
        raise HTTPException(status_code=404, detail="Queue not available in background mode")
    item = get_queue().get(task_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Task not found in queue")
    return _obs_task_detail(item)


# =============================================================================
# v0.5.3 — Blackboard / task comments（留言板）
#
# 原則：留言只寫入 task_comments 表（BlackboardStore），絕不改 queue 任務狀態、
# 不觸發 worker、不呼叫 OpenClaw CLI、不碰 Hermes / Discord。
# 任務不存在時回 404，不建立孤兒留言。
# =============================================================================
class CommentCreate(BaseModel):
    """新增留言的 request body。"""

    author_type: Literal["user", "hermes", "openclaw", "system"] = "user"
    author_name: str | None = Field(default=None, description="留言者名稱（選填）")
    content: str = Field(..., min_length=1, description="留言內容（必填、不可為空）")
    metadata: dict[str, Any] = Field(default_factory=dict)


@app.get("/tasks/{task_id}/comments")
def get_task_comments(
    task_id: str, x_adapter_token: str | None = Header(default=None)
) -> dict[str, Any]:
    """取得指定 task 的留言串（唯讀）。任務不存在回 404。"""
    require_token(x_adapter_token)
    if not _task_exists(task_id):
        raise HTTPException(status_code=404, detail="Task not found in queue")
    items = get_blackboard().list_for_task(task_id)
    return {"task_id": task_id, "items": items}


@app.post("/tasks/{task_id}/comments", status_code=201)
def add_task_comment(
    task_id: str,
    body: CommentCreate,
    x_adapter_token: str | None = Header(default=None),
) -> dict[str, Any]:
    """新增指定 task 的留言。只寫 task_comments，不改 queue 狀態、不觸發 worker。"""
    require_token(x_adapter_token)
    if not _task_exists(task_id):
        raise HTTPException(status_code=404, detail="Task not found in queue")
    try:
        comment = get_blackboard().add_comment(
            task_id=task_id,
            author_type=body.author_type,
            author_name=body.author_name,
            content=body.content,
            metadata=body.metadata,
        )
    except CommentValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return comment


# =============================================================================
# v0.5.4 — Approval Flow（人工審核狀態機）
#
# 原則：approve / reject 只透過 QueueStore 狀態機處理（waiting_review -> queued / rejected），
# 不直接啟動 worker、不呼叫 OpenClaw CLI、不碰 Hermes / Discord。
# worker 之後自然 claim queued 任務（claim_next 只取 queued，永不取 waiting_review/rejected）。
# =============================================================================
class RejectBody(BaseModel):
    """reject 的 request body（reason 選填）。"""

    reason: str | None = Field(default=None, description="拒絕原因（選填）")


# v0.5.5 控制動作成功時的 system 留言模板。
_CONTROL_COMMENT = {
    "cancel": "Task cancelled by owner.",
    "retry": "Task retry requested by owner.",
    "archive": "Task archived by owner.",
}


def _run_control(
    task_id: str,
    *,
    action: str,
    method: "Any",
    reason: str | None,
) -> dict[str, Any]:
    """共用控制流程：404（不存在）/ 409（狀態不允許）；成功寫 ledger + system 留言。

    所有狀態轉換都委派給 QueueStore 狀態機（method）；本函式不啟動 worker、
    不呼叫 OpenClaw CLI。
    """
    if EXECUTION_MODE == "background":
        raise HTTPException(status_code=404, detail="Queue not available in background mode")
    if get_queue().get(task_id) is None:
        raise HTTPException(status_code=404, detail="Task not found in queue")
    updated = method(get_queue())
    if updated is None:
        current = (get_queue().get(task_id) or {}).get("status")
        raise HTTPException(
            status_code=409,
            detail=f"Action '{action}' not allowed from status '{current}'",
        )
    new_status = updated.get("status")
    append_task_status(task_id, new_status, via=action, reason=reason)
    base = _CONTROL_COMMENT.get(action, f"Task {action} by owner.")
    _add_system_comment(
        task_id, f"{base} Reason: {reason}" if reason else base
    )
    return {"status": new_status, "action": action, "task_id": task_id, "task": updated}


def _review_summary(item: dict[str, Any]) -> dict[str, Any]:
    """pending review 列表用：在精簡樣貌上補 safety_level / requires_confirmation / 摘要。"""
    md = _parse_payload_metadata(item.get("payload"))
    text = item.get("task_text") or ""
    summary = _obs_task_summary(item)
    summary.update(
        {
            "safety_level": item.get("safety_level"),
            "requires_confirmation": _coerce_bool(md.get("requires_confirmation")),
            "task_text_snippet": text[:200],
        }
    )
    return summary


def _add_system_comment(task_id: str, content: str) -> None:
    """approve/reject 時寫一則 system 留言（純記錄）。失敗不影響狀態機。"""
    try:
        get_blackboard().add_comment(
            task_id=task_id,
            author_type="system",
            author_name="approval-flow",
            content=content,
            metadata={"via": "approval-flow"},
        )
    except Exception:  # noqa: BLE001 - 留言只是附帶記錄，絕不可反過來影響審核
        pass


@app.get("/reviews/pending")
def reviews_pending(
    limit: int = 20,
    offset: int = 0,
    x_adapter_token: str | None = Header(default=None),
) -> dict[str, Any]:
    """列出所有 waiting_review 任務（唯讀）。"""
    require_token(x_adapter_token)
    limit = max(1, min(limit, 200))
    offset = max(0, offset)
    if EXECUTION_MODE == "background":
        return {"items": [], "limit": limit, "offset": offset, "total": 0}
    items, total = get_queue().list_page(
        status=WAITING_REVIEW, limit=limit, offset=offset
    )
    return {
        "items": [_review_summary(i) for i in items],
        "limit": limit,
        "offset": offset,
        "total": total,
    }


def _require_waiting_review(task_id: str) -> dict[str, Any]:
    """共用前置檢查：任務不存在 -> 404；存在但非 waiting_review -> 409。回傳該 queue row。"""
    if EXECUTION_MODE == "background":
        raise HTTPException(status_code=404, detail="Queue not available in background mode")
    item = get_queue().get(task_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Task not found in queue")
    if item.get("status") != WAITING_REVIEW:
        raise HTTPException(
            status_code=409,
            detail=f"Task is not waiting_review (current status: {item.get('status')})",
        )
    return item


@app.post("/tasks/{task_id}/approve")
def approve_task(
    task_id: str, x_adapter_token: str | None = Header(default=None)
) -> dict[str, Any]:
    """批准 waiting_review 任務 -> queued。不直接啟動 worker。"""
    require_token(x_adapter_token)
    _require_waiting_review(task_id)
    updated = get_queue().approve(task_id)
    if updated is None:
        # 競態：剛剛狀態被改掉（例如併發 approve/reject）。
        raise HTTPException(status_code=409, detail="Task is no longer waiting_review")
    append_task_status(task_id, "queued", via="approve")
    _add_system_comment(
        task_id,
        "Task approved; status changed from waiting_review to queued.",
    )
    return {"status": "approved", "task_id": task_id, "task": updated}


@app.post("/tasks/{task_id}/reject")
def reject_task(
    task_id: str,
    body: RejectBody | None = None,
    x_adapter_token: str | None = Header(default=None),
) -> dict[str, Any]:
    """拒絕 waiting_review 任務 -> rejected（終止狀態）。不直接啟動 worker。"""
    require_token(x_adapter_token)
    _require_waiting_review(task_id)
    reason = body.reason if body else None
    updated = get_queue().reject(task_id, reason=reason)
    if updated is None:
        raise HTTPException(status_code=409, detail="Task is no longer waiting_review")
    append_task_status(task_id, "rejected", via="reject", reason=reason)
    _add_system_comment(
        task_id,
        f"Task rejected. Reason: {reason}" if reason else "Task rejected.",
    )
    return {"status": "rejected", "task_id": task_id, "task": updated}


# =============================================================================
# v0.5.2 — Read-only Dashboard（本機唯讀 UI）
#
# 原則：Dashboard 只「讀」資料，重用上面 v0.5.1 的 observability 唯讀 helper
# （_obs_counts_total / _obs_task_summary / _obs_task_detail / _obs_worker_status），
# 不另寫一套查 DB 邏輯、不改任何 queue 狀態、不呼叫 OpenClaw CLI、不碰 Discord/Hermes。
# 純 server-side render（FastAPI + Jinja2），無前後端分離、無登入。
# =============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

# templates / static 目錄一定存在（隨原始碼一起 commit），缺了直接讓它噴出來。
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

DASHBOARD_TITLE = "Hermes x OpenClaw Queue Control Board"


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_home(request: Request) -> HTMLResponse:
    """Dashboard 首頁 / Overview（唯讀）。"""
    counts, total = _obs_counts_total()
    worker = _obs_worker_status(counts)
    queue_db_exists = (
        False if EXECUTION_MODE == "background" else Path(QUEUE_DB_PATH).exists()
    )
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "title": DASHBOARD_TITLE,
            "version": APP_VERSION,
            "execution_mode": EXECUTION_MODE,
            "counts": counts,
            "total": total,
            "queue_db_exists": queue_db_exists,
            "worker": worker,
            "generated_at": utc_now_iso(),
        },
    )


@app.get("/dashboard/tasks", response_class=HTMLResponse)
def dashboard_tasks(
    request: Request,
    status: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> HTMLResponse:
    """任務列表（唯讀）。重用 observability 的分頁與精簡樣貌 helper。"""
    limit = max(1, min(limit, 200))
    offset = max(0, offset)
    invalid_status = status is not None and status not in VALID_STATUSES
    if EXECUTION_MODE == "background" or invalid_status:
        items: list[dict[str, Any]] = []
        total = 0
    else:
        rows, total = get_queue().list_page(status=status, limit=limit, offset=offset)
        items = [_obs_task_summary(i) for i in rows]
    return templates.TemplateResponse(
        "tasks.html",
        {
            "request": request,
            "title": DASHBOARD_TITLE,
            "items": items,
            "total": total,
            "status": status,
            "limit": limit,
            "offset": offset,
            "invalid_status": invalid_status,
            "valid_statuses": sorted(VALID_STATUSES),
            "has_prev": offset > 0,
            "has_next": offset + limit < total,
            "prev_offset": max(0, offset - limit),
            "next_offset": offset + limit,
        },
    )


@app.get("/dashboard/tasks/{task_id}", response_class=HTMLResponse)
def dashboard_task_detail(
    request: Request, task_id: str, error: str | None = None
) -> HTMLResponse:
    """任務詳情（唯讀）+ Blackboard 留言串。找不到回 404。"""
    if EXECUTION_MODE == "background":
        raise HTTPException(status_code=404, detail="Queue not available in background mode")
    item = get_queue().get(task_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Task not found in queue")
    detail = _obs_task_detail(item)
    comments = get_blackboard().list_for_task(task_id)
    return templates.TemplateResponse(
        "task_detail.html",
        {
            "request": request,
            "title": DASHBOARD_TITLE,
            "task": detail,
            "comments": comments,
            "author_types": sorted(VALID_AUTHOR_TYPES),
            "comment_error": error,
        },
    )


@app.post("/dashboard/tasks/{task_id}/comments")
def dashboard_add_comment(
    task_id: str,
    author_type: str = Form("user"),
    author_name: str = Form("owner"),
    content: str = Form(...),
) -> RedirectResponse:
    """Dashboard 留言表單處理。只寫 task_comments，寫完 redirect 回詳情頁（PRG）。

    不改 queue 狀態、不觸發 worker、不呼叫 OpenClaw CLI。
    """
    target = f"/dashboard/tasks/{task_id}"
    if not _task_exists(task_id):
        raise HTTPException(status_code=404, detail="Task not found in queue")
    try:
        get_blackboard().add_comment(
            task_id=task_id,
            author_type=author_type,
            author_name=author_name,
            content=content,
            metadata={"via": "dashboard"},
        )
    except CommentValidationError as exc:
        # PRG：帶錯誤訊息 redirect 回詳情頁（不丟 500）。
        from urllib.parse import quote

        return RedirectResponse(
            url=f"{target}?error={quote(str(exc))}", status_code=303
        )
    return RedirectResponse(url=target, status_code=303)


@app.get("/dashboard/reviews", response_class=HTMLResponse)
def dashboard_reviews(
    request: Request, limit: int = 50, offset: int = 0
) -> HTMLResponse:
    """Pending Reviews 頁面：列出 waiting_review 任務，提供 Approve / Reject。"""
    limit = max(1, min(limit, 200))
    offset = max(0, offset)
    if EXECUTION_MODE == "background":
        items: list[dict[str, Any]] = []
        total = 0
    else:
        rows, total = get_queue().list_page(
            status=WAITING_REVIEW, limit=limit, offset=offset
        )
        items = [_review_summary(i) for i in rows]
    return templates.TemplateResponse(
        "reviews.html",
        {
            "request": request,
            "title": DASHBOARD_TITLE,
            "items": items,
            "total": total,
            "limit": limit,
            "offset": offset,
        },
    )


@app.post("/dashboard/tasks/{task_id}/approve")
def dashboard_approve(task_id: str) -> RedirectResponse:
    """Dashboard approve 表單：waiting_review -> queued，PRG redirect 回詳情頁。

    只走 QueueStore 狀態機，不直接啟動 worker、不呼叫 OpenClaw CLI。
    """
    from urllib.parse import quote

    target = f"/dashboard/tasks/{task_id}"
    if not _task_exists(task_id):
        raise HTTPException(status_code=404, detail="Task not found in queue")
    updated = get_queue().approve(task_id)
    if updated is None:
        return RedirectResponse(
            url=f"{target}?error={quote('只有 waiting_review 任務可以 approve')}",
            status_code=303,
        )
    append_task_status(task_id, "queued", via="dashboard-approve")
    _add_system_comment(
        task_id, "Task approved via dashboard; status changed from waiting_review to queued."
    )
    return RedirectResponse(url=target, status_code=303)


@app.post("/dashboard/tasks/{task_id}/reject")
def dashboard_reject(
    task_id: str, reason: str = Form("")
) -> RedirectResponse:
    """Dashboard reject 表單：waiting_review -> rejected，PRG redirect 回詳情頁。"""
    from urllib.parse import quote

    target = f"/dashboard/tasks/{task_id}"
    if not _task_exists(task_id):
        raise HTTPException(status_code=404, detail="Task not found in queue")
    reason_clean = reason.strip() or None
    updated = get_queue().reject(task_id, reason=reason_clean)
    if updated is None:
        return RedirectResponse(
            url=f"{target}?error={quote('只有 waiting_review 任務可以 reject')}",
            status_code=303,
        )
    append_task_status(task_id, "rejected", via="dashboard-reject", reason=reason_clean)
    _add_system_comment(
        task_id,
        f"Task rejected via dashboard. Reason: {reason_clean}"
        if reason_clean
        else "Task rejected via dashboard.",
    )
    return RedirectResponse(url=target, status_code=303)


# --- v0.5.5 Dashboard 控制表單（cancel / retry / archive，PRG）-------------------
def _dashboard_control(task_id: str, action: str, method, reason: str | None) -> RedirectResponse:
    """共用 Dashboard 控制表單處理：成功 redirect 回詳情頁；狀態不允許帶 error redirect。"""
    from urllib.parse import quote

    target = f"/dashboard/tasks/{task_id}"
    if not _task_exists(task_id):
        raise HTTPException(status_code=404, detail="Task not found in queue")
    updated = method(get_queue())
    if updated is None:
        current = (get_queue().get(task_id) or {}).get("status")
        return RedirectResponse(
            url=f"{target}?error={quote(f'{action} 不允許（目前狀態 {current}）')}",
            status_code=303,
        )
    new_status = updated.get("status")
    append_task_status(task_id, new_status, via=f"dashboard-{action}", reason=reason)
    base = _CONTROL_COMMENT.get(action, f"Task {action} by owner.")
    _add_system_comment(
        task_id, f"{base} (via dashboard) Reason: {reason}" if reason else f"{base} (via dashboard)"
    )
    return RedirectResponse(url=target, status_code=303)


@app.post("/dashboard/tasks/{task_id}/cancel")
def dashboard_cancel(task_id: str, reason: str = Form("")) -> RedirectResponse:
    """Dashboard cancel 表單：queued / waiting_review -> cancelled。"""
    reason_clean = reason.strip() or None
    return _dashboard_control(
        task_id, "cancel",
        lambda q: q.cancel_control(task_id, reason=reason_clean),
        reason_clean,
    )


@app.post("/dashboard/tasks/{task_id}/retry")
def dashboard_retry(task_id: str, reason: str = Form("")) -> RedirectResponse:
    """Dashboard retry 表單：failed -> queued（不直接啟動 worker）。"""
    reason_clean = reason.strip() or None
    return _dashboard_control(
        task_id, "retry",
        lambda q: q.retry_failed(task_id, reason=reason_clean),
        reason_clean,
    )


@app.post("/dashboard/tasks/{task_id}/archive")
def dashboard_archive(task_id: str, reason: str = Form("")) -> RedirectResponse:
    """Dashboard archive 表單：completed/failed/cancelled/rejected -> archived。"""
    reason_clean = reason.strip() or None
    return _dashboard_control(
        task_id, "archive",
        lambda q: q.archive(task_id, reason=reason_clean),
        reason_clean,
    )


# =============================================================================
# v0.5.6 — System Health / Worker Heartbeat（純觀測）
#
# 原則：只「讀」queue counts + worker_heartbeats，並對 OpenClaw CLI「只檢查路徑、
# 絕不執行」。不改 queue 狀態機、不觸發 worker、不呼叫 OpenClaw CLI。
# =============================================================================
def _openclaw_cli_status() -> dict[str, Any]:
    """只檢查 OpenClaw CLI 路徑是否存在 / 可執行——**絕不執行它**（不跑 --version）。"""
    import shutil  # noqa: PLC0415

    raw = OPENCLAW_CLI_BIN
    resolved: str | None
    exists: bool
    if os.sep in raw or (os.altsep and os.altsep in raw):
        # 看起來是路徑：直接檢查檔案是否存在且可執行。
        resolved = raw
        exists = os.path.isfile(raw) and os.access(raw, os.X_OK)
    else:
        # 看起來是 PATH 上的指令名：用 which 解析（不執行）。
        found = shutil.which(raw)
        resolved = found
        exists = found is not None
    return {
        "cli_bin": raw,
        "cli_path": resolved,
        "cli_path_exists": exists,
        "cli_checked_without_execution": True,
    }


def _worker_snapshot() -> dict[str, Any]:
    """讀 worker heartbeat（background 模式無 queue db 也安全）。唯讀。"""
    try:
        return get_health().snapshot(WORKER_ID, WORKER_HEARTBEAT_STALE_SECONDS)
    except Exception:  # noqa: BLE001 - 觀測端點不該因 health store 故障而 500
        return {"worker_id": WORKER_ID, "status": "unknown", "raw_status": None,
                "last_seen_at": None, "current_task_id": None}


@app.get("/system/health")
def system_health(x_adapter_token: str | None = Header(default=None)) -> dict[str, Any]:
    """整體系統健康（adapter / queue / worker / openclaw cli path）。唯讀、不執行 CLI。"""
    require_token(x_adapter_token)
    counts, _total = _obs_counts_total()
    db_exists = (
        False if EXECUTION_MODE == "background" else Path(QUEUE_DB_PATH).exists()
    )
    worker = _worker_snapshot()
    return {
        "ok": True,
        "version": APP_VERSION,
        "adapter": {"status": "online"},
        "queue": {"db_exists": db_exists, "counts": counts},
        "worker": {
            "status": worker.get("status"),
            "raw_status": worker.get("raw_status"),
            "last_seen_at": worker.get("last_seen_at"),
            "current_task_id": worker.get("current_task_id"),
        },
        "openclaw": _openclaw_cli_status(),
        "generated_at": utc_now_iso(),
    }


@app.get("/system/worker")
def system_worker(x_adapter_token: str | None = Header(default=None)) -> dict[str, Any]:
    """worker heartbeat 詳情（含推導的 online/stale/unknown）。唯讀。"""
    require_token(x_adapter_token)
    return _worker_snapshot()


@app.get("/dashboard/system", response_class=HTMLResponse)
def dashboard_system(request: Request) -> HTMLResponse:
    """Dashboard 系統健康頁。"""
    counts, _total = _obs_counts_total()
    db_exists = (
        False if EXECUTION_MODE == "background" else Path(QUEUE_DB_PATH).exists()
    )
    return templates.TemplateResponse(
        "system.html",
        {
            "request": request,
            "title": DASHBOARD_TITLE,
            "version": APP_VERSION,
            "adapter_status": "online",
            "db_exists": db_exists,
            "counts": counts,
            "worker": _worker_snapshot(),
            "openclaw": _openclaw_cli_status(),
            "generated_at": utc_now_iso(),
        },
    )
