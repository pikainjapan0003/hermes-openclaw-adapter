"""v0.7.1-B — Local-only Queue Intake Bridge（受控、fail-closed、不可執行落地）。

讓 mock Adapter 產生的 v0.7 TaskEnvelope，在嚴格受控條件下，寫入一個**獨立的
local-only intake DB**，且**一律以 waiting_review 落地**——worker 結構上不會 claim
（QueueStore.claim_next 只取 status='queued'）。

安全原則（全部 fail-closed）：
  1. QUEUE_INTAKE_ENABLED 預設 false → 預設不寫任何 DB。
  2. INTAKE_KILL_SWITCH 優先：true 時拒絕所有 intake。
  3. INTAKE_ALLOWED_TASK_TYPES 預設空集合 → 未允許的 task_type 一律拒絕。
  4. 只寫獨立 intake DB；預設路徑不得等於 production QUEUE_DB_PATH（相等則拒絕）。
  5. 寫入 QueueStore 時 initial_status 一律 waiting_review，**絕不寫 queued**。
  6. payload metadata 標示 local_only / mock source / executable_by_worker=false。

本模組明確不做：
  - 不 import app.worker、不 import app.main。
  - 不呼叫 run_openclaw_cli、不接真 OpenClaw / 真 Hermes / webhook。
  - 不呼叫 Google Sheets / google client、不寫 production data/queue.db。
  - 不讀取 / 不顯示任何 secret（只讀本模組定義的非敏感 flag）。

公開 API：
  class QueueIntakeBridgeError(Exception)
  intake_task_envelope_local_only(task_envelope, *, db_path=None) -> dict
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional

from app.contracts_v0_7 import validate_task_envelope
from app.queue_store import WAITING_REVIEW, QueueStore
# v0.7.1-E：local-only tool-level security gate（純函式）。只在 INTAKE_SECURITY_GATES_ENABLED=true
# 時啟用；reject 一律不寫 DB。build_audit_event 為 observation-only，本版不落地寫 audit 檔。
from app.security_gates_v0_7 import build_audit_event, evaluate_security_gates

# 預設 local-only intake DB（與 production queue.db 分離）。
DEFAULT_INTAKE_DB_PATH = "data/intake_local_v0_7_1_b.db"
# production queue DB（僅用於「拒絕誤寫」比對；不寫入）。
DEFAULT_PRODUCTION_DB_PATH = "data/queue.db"

INTAKE_SOURCE = "mock-adapter-local"


class QueueIntakeBridgeError(Exception):
    """intake bridge 使用錯誤（例如傳入非 dict envelope）時 raise。"""


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _allowed_task_types() -> set[str]:
    """讀 INTAKE_ALLOWED_TASK_TYPES（逗號分隔）。預設空集合 → 全部拒絕。"""
    raw = os.getenv("INTAKE_ALLOWED_TASK_TYPES", "")
    return {part.strip() for part in raw.split(",") if part.strip()}


def _resolve_intake_db_path(db_path: Optional[str]) -> str:
    if db_path:
        return db_path
    return os.getenv("INTAKE_QUEUE_DB_PATH", DEFAULT_INTAKE_DB_PATH)


def _is_production_db(intake_db_path: str) -> bool:
    """intake DB 路徑是否撞到 production queue DB（撞到就拒絕，保護真 queue）。"""
    prod = os.getenv("QUEUE_DB_PATH", DEFAULT_PRODUCTION_DB_PATH)
    try:
        return Path(intake_db_path).resolve() == Path(prod).resolve()
    except OSError:  # pragma: no cover - 防禦性
        return str(intake_db_path) == str(prod)


def _result(
    *,
    accepted: bool,
    written: bool,
    reason: str,
    task_id: Optional[str],
    db_path: Optional[str],
    initial_status: Optional[str],
    security_gate: Optional[Dict[str, Any]] = None,
    audit_event: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "accepted": accepted,
        "written": written,
        "reason": reason,
        "task_id": task_id,
        "db_path": db_path,  # 本機路徑，非 secret
        "initial_status": initial_status,
        "executable_by_worker": False,
    }
    if security_gate is not None:
        out["security_gate"] = security_gate
    if audit_event is not None:
        # observation-only：附在回傳供觀測，本版不寫 audit 檔、不改 queue 狀態。
        out["audit_event"] = audit_event
    return out


def _extract_requested_tools(task_envelope: Dict[str, Any]) -> Any:
    """requested tools 來源固定為 metadata.requested_tools（Owner v0.7.1-E 裁定）。

    回傳原始值（可能為 None / 非 list）；由 evaluate_security_gates 做型別 / 空值判斷與 fail-closed。
    """
    metadata = task_envelope.get("metadata")
    if not isinstance(metadata, dict):
        return None
    return metadata.get("requested_tools")


def intake_task_envelope_local_only(
    task_envelope: Dict[str, Any], *, db_path: Optional[str] = None
) -> Dict[str, Any]:
    """受控地把 v0.7 TaskEnvelope 寫入 local-only intake DB（一律 waiting_review）。

    預設 disabled（QUEUE_INTAKE_ENABLED!=true）→ 不寫 DB。
    kill switch 優先；未 allowlist 的 task_type 一律拒絕；只寫獨立 intake DB；
    絕不寫 queued、絕不啟動 worker、絕不呼叫 OpenClaw / Google Sheets。
    """
    if not isinstance(task_envelope, dict):
        raise QueueIntakeBridgeError("task_envelope 必須為 dict")

    task_id = task_envelope.get("task_id")

    # 1) global kill switch 最優先（fail-closed）。
    if _env_bool("GLOBAL_KILL_SWITCH", False):
        return _result(accepted=False, written=False, reason="global_kill_switch_active",
                       task_id=task_id, db_path=None, initial_status=None)

    # 2) layer kill switch（fail-closed）。
    if _env_bool("INTAKE_KILL_SWITCH", False):
        return _result(accepted=False, written=False, reason="kill_switch_active",
                       task_id=task_id, db_path=None, initial_status=None)

    # 3) 預設 disabled（fail-closed）。
    if not _env_bool("QUEUE_INTAKE_ENABLED", False):
        return _result(accepted=False, written=False, reason="intake_disabled",
                       task_id=task_id, db_path=None, initial_status=None)

    # 4) 格式驗證（v0.7.0-B validator）。
    validate_task_envelope(task_envelope)
    task_id = task_envelope["task_id"]
    task_type = task_envelope.get("task_type")

    # 5) task_type allowlist（預設空集合 → 拒絕）。
    allowed = _allowed_task_types()
    if not task_type or task_type not in allowed:
        return _result(accepted=False, written=False, reason="task_type_not_allowlisted",
                       task_id=task_id, db_path=None, initial_status=None)

    # 6) tool-level security gate（僅在 INTAKE_SECURITY_GATES_ENABLED=true 時啟用；reject 不寫 DB）。
    #    requested tools 固定來源 = metadata.requested_tools；缺失/空/非 list[str] → fail-closed reject。
    if _env_bool("INTAKE_SECURITY_GATES_ENABLED", False):
        gate = evaluate_security_gates(
            requested_tools=_extract_requested_tools(task_envelope),
            allowed_tools=task_envelope.get("allowed_tools"),
            denied_tools=task_envelope.get("denied_tools"),
            # kill switch 已在步驟 1/2 處理；此處只做 tool denylist/allowlist 層。
            global_kill_switch=False,
            layer_kill_switch=False,
        )
        if not gate["allowed"]:
            audit = build_audit_event(
                action="intake.security_gate",
                task_id=task_id,
                decision="reject",
                reason=gate["reason"],
                source_mode="local-only",
                intake_mode="local-only",
                metadata=task_envelope.get("metadata"),
            )
            return _result(accepted=False, written=False, reason="security_gate_rejected",
                           task_id=task_id, db_path=None, initial_status=None,
                           security_gate=gate, audit_event=audit)

    # 7) 解析 intake DB 路徑，並拒絕撞到 production queue DB。
    intake_db_path = _resolve_intake_db_path(db_path)
    if _is_production_db(intake_db_path):
        return _result(accepted=False, written=False, reason="refuse_production_db",
                       task_id=task_id, db_path=None, initial_status=None)

    # 8) 準備 payload：標示 local_only / mock source / 不可執行；status 強制非 queued。
    payload = dict(task_envelope)
    metadata = dict(payload.get("metadata") or {})
    metadata.update({
        "local_only": True,
        "mock": True,
        "intake_source": INTAKE_SOURCE,
        "executable_by_worker": False,
    })
    payload["metadata"] = metadata
    # 即使是 payload 內的 status，也不得為 queued；標為 pending_approval（schema 合法、非可執行）。
    payload["status"] = "pending_approval"
    payload["approval_status"] = "pending"
    validate_task_envelope(payload)

    # 9) 寫入獨立 intake DB，initial_status 一律 waiting_review（worker 不會 claim）。
    store = QueueStore(intake_db_path)
    title = (task_envelope.get("intent") or task_envelope.get("goal") or "local-intake")
    task_text = (task_envelope.get("input_summary") or task_envelope.get("goal") or "")
    safety_level = task_envelope.get("risk_level", 0)
    store.enqueue(
        task_id=task_id,
        title=str(title),
        task_text=str(task_text),
        safety_level=int(safety_level) if isinstance(safety_level, int) else 0,
        payload=payload,
        correlation_id=task_envelope.get("idempotency_key"),
        max_attempts=int(task_envelope.get("max_retries", 1) or 1),
        initial_status=WAITING_REVIEW,
    )

    return _result(accepted=True, written=True, reason="written_waiting_review",
                   task_id=task_id, db_path=intake_db_path, initial_status=WAITING_REVIEW)
