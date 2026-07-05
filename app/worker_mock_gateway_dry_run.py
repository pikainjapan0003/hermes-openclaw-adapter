"""v0.8.5-C — Worker → Mock Gateway Dry-run（純函式、local-only、mock-only、dry-run-only）。

從一份 v0.8.5-A Command Envelope dict，經由本地 v0.8.5-B mock gateway helper 推導出
一份 synthetic local-only Worker dry-run result。本模組不啟動真實 Worker、不執行
Worker loop、不派工、不呼叫真實 OpenClaw、不讀寫 queue、不寫 audit trail、不新增任何
Dashboard control。

Worker to mock gateway dry-run is not Worker execution.
Worker to mock gateway dry-run is not Worker dispatch.
Mock gateway call is not real OpenClaw call.
Mock gateway response is not actual execution result.
Dry-run result is not audit trail persistence.
Command envelope validation is not execution permission.
External side effects remain forbidden by default.

純 helper 邊界：
  - 不寫入任何檔案、不 mutate 輸入 envelope。
  - 不 import OpenClaw SDK、不 import app.main、不 import network client、不讀 secrets。
  - 不啟動 Worker、不啟動 Worker loop、不呼叫 real OpenClaw、不呼叫 Hermes、不寫 Google Sheets。
  - 不執行 subprocess、不執行 shell command、不做 network call。
  - 不觸碰 real queue DB、不觸碰 production/shared DB、不觸碰 Remote Blackboard API runtime。
  - 僅用標準庫（typing / importlib / pathlib）；本地載入同目錄下的
    ``mock_openclaw_gateway.py``，不透過套件層級 import，維持模組獨立可載入。

公開 API：
  run_worker_to_mock_gateway_dry_run(command_envelope: dict) -> dict
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any, Dict, Mapping

SOURCE = "synthetic_local_only"

_GATEWAY_MODULE_PATH = Path(__file__).resolve().parent / "mock_openclaw_gateway.py"

# Safety flags this dry-run bridge itself enforces before ever calling the local mock
# gateway. Fields absent from the envelope are treated as their safe default (False),
# mirroring the v0.8.5-B mock gateway helper's own validation.
REQUIRED_TRUE_FLAGS = ("mock_only", "dry_run")
REQUIRED_FALSE_FLAGS = (
    "external_side_effects_allowed",
    "dispatch_allowed",
    "worker_allowed",
    "openclaw_allowed",
)

FIXED_SAFE_RESULT_FIELDS = {
    "source": SOURCE,
    "worker_dry_run": True,
    "worker_loop_started": False,
    "worker_dispatched": False,
    "real_openclaw_called": False,
    "external_side_effects_performed": False,
    "queue_written": False,
    "audit_trail_written": False,
    "dashboard_control_added": False,
}


def _load_mock_gateway_module():
    spec = importlib.util.spec_from_file_location("mock_openclaw_gateway_v0_8_5_b", _GATEWAY_MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _unsafe_flag_violations(envelope: Mapping[str, Any]) -> list[str]:
    violations: list[str] = []
    for flag in REQUIRED_TRUE_FLAGS:
        if envelope.get(flag) is not True:
            violations.append(f"{flag} must be true")
    for flag in REQUIRED_FALSE_FLAGS:
        if envelope.get(flag, False) is not False:
            violations.append(f"{flag} must be false")
    return violations


def _rejected_result(reason: str, details: list[str]) -> Dict[str, Any]:
    result: Dict[str, Any] = dict(FIXED_SAFE_RESULT_FIELDS)
    result["mock_gateway_called"] = False
    result["accepted"] = False
    result["rejection_reason"] = reason
    result["rejection_details"] = list(details)
    result["gateway_response"] = None
    return result


def run_worker_to_mock_gateway_dry_run(command_envelope: Mapping[str, Any]) -> Dict[str, Any]:
    """從一份 command envelope 推導 synthetic local-only Worker dry-run result（純函式）。

    不 mutate 輸入、不寫入任何檔案、不連外、不派工、不啟動 Worker、不呼叫 real
    OpenClaw。此函式先自行確認安全旗標（mock_only / dry_run /
    external_side_effects_allowed / dispatch_allowed / worker_allowed /
    openclaw_allowed）；若不符合，直接回傳一個標記 accepted=False、
    mock_gateway_called=False 的 dry-run rejection result，完全不呼叫本地 mock
    gateway。若符合，才呼叫本地 v0.8.5-B ``build_mock_openclaw_response``，並把
    gateway 的 accepted / rejection 資訊原樣反映在回傳的 dry-run result 內。

    回傳 result 的固定安全欄位（source / worker_dry_run / worker_loop_started /
    worker_dispatched / real_openclaw_called / external_side_effects_performed /
    queue_written / audit_trail_written / dashboard_control_added）恆為固定安全值，
    無論 accepted 與否皆不變。
    """
    if not isinstance(command_envelope, Mapping):
        return _rejected_result(
            "command_envelope must be a mapping",
            ["command_envelope is not a dict/mapping"],
        )

    violations = _unsafe_flag_violations(command_envelope)
    if violations:
        return _rejected_result("unsafe command envelope flags", violations)

    gateway_module = _load_mock_gateway_module()
    gateway_response = gateway_module.build_mock_openclaw_response(command_envelope)

    result: Dict[str, Any] = dict(FIXED_SAFE_RESULT_FIELDS)
    result["mock_gateway_called"] = True
    result["accepted"] = bool(gateway_response.get("accepted"))
    result["rejection_reason"] = gateway_response.get("rejection_reason")
    result["rejection_details"] = gateway_response.get("rejection_details", [])
    result["gateway_response"] = gateway_response
    return result
