from __future__ import annotations

import asyncio
import hashlib
import hmac
import importlib.util
import json
import os
import re
import sys
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import httpx
from fastapi import BackgroundTasks, FastAPI, Form, Header, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
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
# v0.7.1-C3：唯讀顯示推導（純函式）。只在 dashboard 觀測 helper 套用，產生 read-only badges；
# 不改 Queue 狀態、不啟動 worker、不呼叫 OpenClaw / Result Sink / Google Sheets。
from app.dashboard_intake_view_v0_7 import derive_intake_status_view
# v0.7.2-F-C：唯讀 annotation 推導（純函式）。只在渲染 review surfaces 時附加顯示用 annotation；
# 不改 Queue 狀態、不接 approval wiring、不啟動 worker、不呼叫 OpenClaw / Hermes / Google Sheets。
from app.queue_task_annotation_v0_7 import derive_queue_task_annotation
# v0.7.3-B：唯讀 Owner 決策紀錄檢視（純函式）。只讀 payload.metadata.approval_decision_events 顯示；
# 不記錄事件、不接 approval wiring、不啟動 worker、不呼叫 OpenClaw / Hermes / Google Sheets。
from app.approval_decision_events_v0_7 import derive_approval_decision_event_view
# v0.7.4-D：唯讀 Audit Trail Display 推導（純函式）。只在 GET display path 附加顯示用 audit trail；
# 不寫 queue、不 dispatch、不 enforce guard、不啟動 worker、不呼叫 OpenClaw / Hermes / Google Sheets。
from app.audit_trail_display_v0_7 import derive_audit_trail_display_view
# v0.7.3-C：local / append-only Owner decision event recorder（純本地 audit metadata）。
# 只在既有 Owner decision routes append local event；不 dispatch Worker、不接外部、不改 status transition。
from app.approval_decision_event_recorder_v0_7 import build_approval_decision_event
# v0.8.5-C：唯讀 Worker → Mock Gateway Dry-run（純函式，local-only / mock-only / dry-run-only）。
# 只在 GET /dashboard/system 附加顯示用 synthetic local-only mock result；不寫 queue、不 dispatch、
# 不啟動 worker、不啟動 worker loop、不呼叫 real OpenClaw / Hermes / Google Sheets、不讀 secrets。
from app.worker_mock_gateway_dry_run import run_worker_to_mock_gateway_dry_run

# v0.8.2-A：唯讀 Local Mock Dashboard Preview（來自 v0.8.1-V read-only preview adapter，純函式）。只在既有
# GET /dashboard/system observe surface 附加顯示用 synthetic local-only read-only preview model；
# 不寫 queue、不 dispatch、不啟動 worker、不呼叫 OpenClaw / Hermes / Google Sheets、不讀 secrets、不 POST。
_V0_8_2_A_ADAPTER_PATH = (
    Path(__file__).resolve().parent.parent / "scripts" / "local_mock_fixture_dashboard_preview_adapter_v0_8_1.py"
)


def _load_v0_8_2_a_build_dashboard_preview_model():
    """Dynamically load build_dashboard_preview_model() from the v0.8.1-V read-only adapter module.

    Mirrors the v0.8.1-W runtime check's loading pattern: temporarily add scripts/ to sys.path so the
    adapter's own bare sibling import of the v0.8.1-P loader resolves, load the adapter by file path
    via importlib, then remove scripts/ from sys.path again. Never modifies the loader or adapter file.
    """
    scripts_dir = str(_V0_8_2_A_ADAPTER_PATH.parent)
    inserted = False
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
        inserted = True
    try:
        spec = importlib.util.spec_from_file_location(
            "local_mock_fixture_dashboard_preview_adapter_v0_8_1", _V0_8_2_A_ADAPTER_PATH
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.build_dashboard_preview_model
    finally:
        if inserted and scripts_dir in sys.path:
            sys.path.remove(scripts_dir)


build_dashboard_preview_model = _load_v0_8_2_a_build_dashboard_preview_model()

# v0.8.3-D：唯讀 Worker Dry-run Preview（來自 v0.8.3-B standalone synthetic local-only builder，純函式）。只在既有
# GET /dashboard/system observe surface 附加顯示用 synthetic local-only read-only worker dry-run preview model；
# 不寫 queue、不 dispatch、不啟動 worker、不呼叫 OpenClaw / Hermes / Google Sheets、不讀 secrets、不 POST。
_V0_8_3_D_BUILDER_PATH = (
    Path(__file__).resolve().parent.parent / "scripts" / "worker_dry_run_preview_boundary_v0_8_3_b.py"
)


def _load_v0_8_3_d_build_worker_dry_run_preview_model():
    """Dynamically load build_worker_dry_run_preview_model() from the v0.8.3-B standalone builder.

    Mirrors the v0.8.2-A loader's file-path importlib pattern. The v0.8.3-B builder has no sibling-
    module imports of its own (stdlib json/pathlib only), so no sys.path manipulation is needed. Never
    modifies the builder file.
    """
    spec = importlib.util.spec_from_file_location(
        "worker_dry_run_preview_boundary_v0_8_3_b", _V0_8_3_D_BUILDER_PATH
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_worker_dry_run_preview_model


build_worker_dry_run_preview_model = _load_v0_8_3_d_build_worker_dry_run_preview_model()

# v0.8.4-D：唯讀 Worker Dry-run Result / Audit Trail（來自 v0.8.4-B standalone synthetic local-only builder，純函式）。
# 只在既有 GET /dashboard/system observe surface 附加顯示用 synthetic local-only read-only result/audit-trail model；
# 不寫 queue、不 dispatch、不啟動 worker、不呼叫 OpenClaw / Hermes / Google Sheets、不讀 secrets、不 POST。
_V0_8_4_D_BUILDER_PATH = (
    Path(__file__).resolve().parent.parent / "scripts" / "worker_dry_run_result_audit_trail_boundary_v0_8_4_b.py"
)


def _load_v0_8_4_d_build_worker_dry_run_result_audit_trail_model():
    """Dynamically load build_worker_dry_run_result_audit_trail_model() from the v0.8.4-B standalone builder.

    Mirrors the v0.8.3-D loader's file-path importlib pattern. The v0.8.4-B builder has no sibling-
    module imports of its own (stdlib json/pathlib only), so no sys.path manipulation is needed. Never
    modifies the builder file.
    """
    spec = importlib.util.spec_from_file_location(
        "worker_dry_run_result_audit_trail_boundary_v0_8_4_b", _V0_8_4_D_BUILDER_PATH
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_worker_dry_run_result_audit_trail_model


build_worker_dry_run_result_audit_trail_model = _load_v0_8_4_d_build_worker_dry_run_result_audit_trail_model()

# v0.8.5-D：唯讀 Dashboard Mock Result View（來自 v0.8.5-C run_worker_to_mock_gateway_dry_run，純函式）。
# 只在既有 GET /dashboard/system observe surface 附加顯示用 synthetic local-only read-only mock result
# preview；不寫 queue、不寫 audit trail、不啟動 worker、不啟動 worker loop、不派工、不呼叫 real
# OpenClaw / Hermes / Google Sheets、不讀 secrets、不 POST。envelope 為固定 deterministic synthetic
# 常數，非使用者輸入。
_V0_8_5_D_SYNTHETIC_COMMAND_ENVELOPE = {
    "command_id": "cmd-dashboard-preview-0001",
    "task_id": "task-dashboard-preview-0001",
    "tool_target": "example.tool",
    "requested_action": "describe a hypothetical action, never executed",
    "risk_level": "low",
    "approval_snapshot": {"owner_review_required": True},
    "execution_mode": "mock_only",
    "dry_run": True,
    "mock_only": True,
    "external_touchpoints": [],
    "rollback_plan": "no rollback needed; nothing is executed",
    "external_side_effects_allowed": False,
}


def build_dashboard_mock_result_view_model() -> dict[str, Any]:
    """從固定 synthetic command envelope 推導 Dashboard mock result 唯讀 preview（純函式）。

    呼叫 v0.8.5-C ``run_worker_to_mock_gateway_dry_run()``，並附加 ``preview_only`` 顯示旗標。
    不 mutate 任何狀態、不寫入任何檔案、不連外、不派工。
    """
    dry_run_result = run_worker_to_mock_gateway_dry_run(_V0_8_5_D_SYNTHETIC_COMMAND_ENVELOPE)
    gateway_response = dry_run_result.get("gateway_response") or {}
    return {
        "source": dry_run_result.get("source"),
        "mock_gateway": gateway_response.get("mock_gateway"),
        "worker_dry_run": dry_run_result.get("worker_dry_run"),
        "worker_loop_started": dry_run_result.get("worker_loop_started"),
        "worker_dispatched": dry_run_result.get("worker_dispatched"),
        "real_openclaw_called": dry_run_result.get("real_openclaw_called"),
        "external_side_effects_performed": dry_run_result.get("external_side_effects_performed"),
        "queue_written": dry_run_result.get("queue_written"),
        "audit_trail_written": dry_run_result.get("audit_trail_written"),
        "dashboard_control_added": dry_run_result.get("dashboard_control_added"),
        "preview_only": True,
        "accepted": dry_run_result.get("accepted"),
        "command_id": gateway_response.get("command_id"),
        "tool_target": gateway_response.get("tool_target"),
        "mock_response_summary": gateway_response.get("mock_response_summary"),
    }


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
        # v0.7.1-C3：唯讀顯示推導（read-only badges），不改任何狀態。
        "intake_status": derive_intake_status_view(item),
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
        # v0.7.1-C3：唯讀顯示推導（read-only badges），不改任何狀態。
        "intake_status": derive_intake_status_view(item),
        # v0.7.2-F-C：唯讀 annotation（顯示用），execution_permission/dispatch_allowed 恆為 False。
        "annotation": derive_queue_task_annotation(item),
        # v0.7.3-B：唯讀 Owner 決策紀錄檢視（顯示用），不記錄事件、不 dispatch。
        "decision_events": derive_approval_decision_event_view(item),
        # v0.7.4-D：唯讀 Audit Trail Display（顯示用），不改 lifecycle、不 enforce guard、不 dispatch。
        "audit_trail": derive_audit_trail_display_view(item),
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
            # v0.7.2-F-C：唯讀 annotation（顯示用），execution_permission/dispatch_allowed 恆為 False。
            "annotation": derive_queue_task_annotation(item),
            # v0.7.3-B：唯讀 Owner 決策紀錄檢視（顯示用），不記錄事件、不 dispatch。
            "decision_events": derive_approval_decision_event_view(item),
            # v0.7.4-D：唯讀 Audit Trail Display（顯示用），不改 lifecycle、不 enforce guard、不 dispatch。
            "audit_trail": derive_audit_trail_display_view(item),
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


def _record_owner_decision(
    task_id: str,
    decision_type: str,
    previous_status: str | None,
    next_status: str | None,
    reason: str | None,
) -> None:
    """v0.7.3-C：append 一筆 Owner approval decision event 到 task payload metadata。

    local / append-only audit record。**不** dispatch Worker、**不**呼叫 OpenClaw /
    Hermes / Google Sheets、**不**改 status transition。execution_permission /
    dispatch_allowed 恆為 False。記錄失敗只吞掉，絕不反過來影響審核或做 external fallback。
    """
    try:
        task = get_queue().get(task_id)
        if task is None:
            return
        event = build_approval_decision_event(
            task,
            decision_type=decision_type,
            previous_status=previous_status,
            next_status=next_status,
            decided_by="owner",
            decision_reason=reason or "",
            via=f"dashboard-{decision_type}",
        )
        get_queue().append_approval_decision_event(task_id, event)
    except Exception:  # noqa: BLE001 - audit 記錄絕不可反過來影響審核狀態機
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


# --- v0.5.7 Dashboard polish：純唯讀的 template helper（不寫任何資料）---------
def short_task_id(task_id: Any, head: int = 10, tail: int = 4) -> str:
    """顯示用的短 task_id（中間省略）。完整值請放在 title 屬性。"""
    s = "" if task_id is None else str(task_id)
    if len(s) <= head + tail + 1:
        return s
    return f"{s[:head]}…{s[-tail:]}"


def truncate(text: Any, max_len: int = 80) -> str:
    """過長文字截斷加省略號。唯讀。"""
    s = "" if text is None else str(text)
    s = s.replace("\n", " ").strip()
    return s if len(s) <= max_len else s[: max_len - 1].rstrip() + "…"


def status_class(status: Any) -> str:
    """回傳 status badge 的 CSS class（badge badge-<status>）。"""
    s = (str(status) if status else "unknown").strip() or "unknown"
    return f"badge badge-{s}"


def format_empty(value: Any, fallback: str = "—") -> str:
    """空值顯示為 muted fallback。唯讀。"""
    if value is None:
        return fallback
    s = str(value).strip()
    return s if s else fallback


def yesno(value: Any) -> str:
    return "yes" if value else "no"


templates.env.globals.update(
    short_task_id=short_task_id,
    truncate=truncate,
    status_class=status_class,
    format_empty=format_empty,
    yesno=yesno,
)

# 首頁 / 任務列表用的狀態篩選連結（順序固定，方便閱讀）。
DASHBOARD_STATUS_FILTERS = (
    ("", "All"),
    ("queued", "Queued"),
    ("running", "Running"),
    ("waiting_review", "Waiting Review"),
    ("failed", "Failed"),
    ("completed", "Completed"),
    ("cancelled", "Cancelled"),
    ("rejected", "Rejected"),
    ("archived", "Archived"),
)


# =============================================================================
# v0.6.4 — Dashboard Auth Gate（Replit 公開前的最小認證關卡）
#
# 原則：只在 DASHBOARD_AUTH_ENABLED=true 時生效；本機開發預設 false → 完全不影響舊行為。
# 開啟後，所有 /dashboard/*（頁面 + 控制表單）都要通過 token gate，未通過 GET→login、
# POST→401。**只加閘門，不改任務狀態機 / worker / OpenClaw 邏輯。**
# 接受的憑證來源：登入後的 httpOnly cookie、或 X-Dashboard-Token header、或 ?dashboard_token=。
# token 來源 DASHBOARD_TOKEN（不寫死、不記 log、不放 docs 真值）。
# =============================================================================
DASHBOARD_AUTH_ENABLED = _env_bool("DASHBOARD_AUTH_ENABLED", False)
DASHBOARD_TOKEN = os.getenv("DASHBOARD_TOKEN", "").strip()
DASHBOARD_COOKIE = "dashboard_auth"
# 登入 / 登出本身永遠豁免（否則無法登入）。
_DASHBOARD_AUTH_EXEMPT = {"/dashboard/login", "/dashboard/logout"}

# 給模板判斷是否顯示 logout 連結（純顯示，不影響保護邏輯）。
templates.env.globals["dashboard_auth_enabled"] = DASHBOARD_AUTH_ENABLED


def _dashboard_authed(request: Request) -> bool:
    """是否通過 Dashboard 認證。auth 關閉時恆 True；開啟但未設 token 時 fail-closed。"""
    if not DASHBOARD_AUTH_ENABLED:
        return True
    if not DASHBOARD_TOKEN:
        # 開了 auth 卻沒設 token → 保守一律擋（避免「以為有保護其實沒設」）。
        return False
    supplied = (
        request.cookies.get(DASHBOARD_COOKIE)
        or request.headers.get("X-Dashboard-Token")
        or request.query_params.get("dashboard_token")
    )
    return bool(supplied) and hmac.compare_digest(str(supplied), DASHBOARD_TOKEN)


@app.middleware("http")
async def _dashboard_auth_middleware(request: Request, call_next):
    """集中保護 /dashboard/*。不碰其他路由（JSON API 仍用各自的 X-Adapter-Token）。"""
    path = request.url.path
    if (
        DASHBOARD_AUTH_ENABLED
        and path.startswith("/dashboard")
        and path not in _DASHBOARD_AUTH_EXEMPT
    ):
        if not _dashboard_authed(request):
            if request.method == "GET":
                return RedirectResponse(url="/dashboard/login", status_code=303)
            return JSONResponse(
                {"detail": "Dashboard auth required"}, status_code=401
            )
    return await call_next(request)


@app.get("/dashboard/login", response_class=HTMLResponse)
def dashboard_login_form(request: Request, error: str | None = None) -> HTMLResponse:
    """登入頁。auth 關閉時直接回 dashboard（不需登入）。"""
    if not DASHBOARD_AUTH_ENABLED:
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "title": DASHBOARD_TITLE, "error": error},
    )


@app.post("/dashboard/login")
def dashboard_login(dashboard_token: str = Form("")) -> RedirectResponse:
    """驗證 DASHBOARD_TOKEN → 設 httpOnly cookie。token 不記 log。"""
    if not DASHBOARD_AUTH_ENABLED:
        return RedirectResponse(url="/dashboard", status_code=303)
    if DASHBOARD_TOKEN and hmac.compare_digest(dashboard_token.strip(), DASHBOARD_TOKEN):
        resp = RedirectResponse(url="/dashboard", status_code=303)
        resp.set_cookie(
            DASHBOARD_COOKIE, DASHBOARD_TOKEN,
            httponly=True, samesite="lax", max_age=60 * 60 * 12,
        )
        return resp
    return RedirectResponse(url="/dashboard/login?error=1", status_code=303)


@app.get("/dashboard/logout")
def dashboard_logout() -> RedirectResponse:
    resp = RedirectResponse(url="/dashboard/login", status_code=303)
    resp.delete_cookie(DASHBOARD_COOKIE)
    return resp


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_home(request: Request) -> HTMLResponse:
    """Dashboard 首頁 / 控制台總覽（唯讀）。"""
    counts, total = _obs_counts_total()
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
            "worker": _worker_snapshot(),  # 真實心跳推導的 online/stale/unknown
            "openclaw": _openclaw_cli_status(),  # 只檢查路徑、不執行
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
            "status_filters": DASHBOARD_STATUS_FILTERS,
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
    # v0.7.3-C：local append-only audit；不 dispatch、不改 status transition。
    _record_owner_decision(task_id, "approve", "waiting_review", "queued", None)
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
    # v0.7.3-C：local append-only audit；不 dispatch、不改 status transition。
    _record_owner_decision(task_id, "reject", "waiting_review", "rejected", reason_clean)
    return RedirectResponse(url=target, status_code=303)


# --- v0.5.5 Dashboard 控制表單（cancel / retry / archive，PRG）-------------------
def _dashboard_control(task_id: str, action: str, method, reason: str | None) -> RedirectResponse:
    """共用 Dashboard 控制表單處理：成功 redirect 回詳情頁；狀態不允許帶 error redirect。"""
    from urllib.parse import quote

    target = f"/dashboard/tasks/{task_id}"
    if not _task_exists(task_id):
        raise HTTPException(status_code=404, detail="Task not found in queue")
    previous_status = (get_queue().get(task_id) or {}).get("status")
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
    # v0.7.3-C：local append-only audit；不 dispatch、不改 status transition。
    _record_owner_decision(task_id, action, previous_status, new_status, reason)
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


@app.get("/")
def root() -> RedirectResponse:
    return RedirectResponse(url="/dashboard", status_code=303)


@app.get("/dashboard/system", response_class=HTMLResponse)
def dashboard_system(request: Request) -> HTMLResponse:
    """Dashboard 系統健康頁。"""
    counts, _total = _obs_counts_total()
    db_exists = (
        False if EXECUTION_MODE == "background" else Path(QUEUE_DB_PATH).exists()
    )
    # v0.8.2-A：唯讀 local mock preview model（來自 v0.8.1-V read-only adapter）。不寫 queue、不 dispatch。
    local_mock_preview_model = build_dashboard_preview_model()
    # v0.8.3-D：唯讀 worker dry-run preview model（來自 v0.8.3-B standalone synthetic local-only builder）。
    # 不寫 queue、不 dispatch、不啟動 worker、不呼叫 OpenClaw / Hermes / Google Sheets。
    worker_dry_run_preview = build_worker_dry_run_preview_model()
    # v0.8.4-D：唯讀 worker dry-run result / audit trail model（來自 v0.8.4-B standalone synthetic local-only builder）。
    # 不寫 queue、不 dispatch、不啟動 worker、不呼叫 OpenClaw / Hermes / Google Sheets。
    worker_dry_run_result_audit_trail = build_worker_dry_run_result_audit_trail_model()
    # v0.8.5-D：唯讀 Dashboard mock result view（來自 v0.8.5-C run_worker_to_mock_gateway_dry_run）。
    # 不寫 queue、不寫 audit trail、不啟動 worker、不啟動 worker loop、不派工、不呼叫 OpenClaw / Hermes / Google Sheets。
    dashboard_mock_result_view = build_dashboard_mock_result_view_model()
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
            "local_mock_preview_model": local_mock_preview_model,
            "worker_dry_run_preview": worker_dry_run_preview,
            "worker_dry_run_result_audit_trail": worker_dry_run_result_audit_trail,
            "dashboard_mock_result_view": dashboard_mock_result_view,
        },
    )
