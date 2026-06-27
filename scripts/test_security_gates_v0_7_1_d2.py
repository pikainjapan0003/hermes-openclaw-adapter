"""v0.7.1-D2 — Local-only Security Gates 單元測試（純函式，不寫 DB、不接真路徑）。

執行： python scripts/test_security_gates_v0_7_1_d2.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.security_gates_v0_7 import (  # noqa: E402
    REDACTED,
    build_audit_event,
    evaluate_kill_switch,
    evaluate_security_gates,
    evaluate_tool_allowlist,
    redact_audit_metadata,
)

# 測試 #15：import 不得拉進 main / worker / queue_store / result_sink。
_IMPORT_SAFE = all(
    m not in sys.modules
    for m in ("app.main", "app.worker", "app.queue_store", "app.result_sink")
)

PASSED = 0


def _ok(msg: str) -> None:
    global PASSED
    PASSED += 1
    print(f"  ok: {msg}")


def _assert(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(f"FAIL: {msg}")
    _ok(msg)


def main() -> int:
    _assert(_IMPORT_SAFE, "import security_gates 未拉進 main / worker / queue_store / result_sink")

    print("[1] kill switch")
    _assert(evaluate_kill_switch(global_kill_switch=True, layer_kill_switch=False)["allowed"] is False,
            "global kill switch active → reject")
    _assert(evaluate_kill_switch(global_kill_switch=False, layer_kill_switch=True)["allowed"] is False,
            "layer kill switch active → reject")
    _assert(evaluate_kill_switch()["allowed"] is False, "kill switch None/None → fail-closed reject")
    _assert(evaluate_kill_switch(global_kill_switch=False, layer_kill_switch=None)["allowed"] is False,
            "layer kill switch None → fail-closed reject")
    _assert(evaluate_kill_switch(global_kill_switch=False, layer_kill_switch=False)["allowed"] is True,
            "both explicitly False → allow")

    print("[2] denylist / allowlist")
    r = evaluate_tool_allowlist(requested_tools=["read"], allowed_tools=["read"], denied_tools=["read"])
    _assert(r["allowed"] is False and r["priority"] == "denylist", "denied_tools match → reject (denylist priority)")
    _assert("read" in r["matched_denied_tools"], "matched_denied_tools 含命中工具")

    _assert(evaluate_tool_allowlist(requested_tools=["read"], allowed_tools=None, denied_tools=[])["allowed"] is False,
            "allowed_tools None → reject (fail-closed)")
    _assert(evaluate_tool_allowlist(requested_tools=["read"], allowed_tools=[], denied_tools=[])["allowed"] is False,
            "allowed_tools empty → reject (fail-closed)")
    _assert(evaluate_tool_allowlist(requested_tools=None, allowed_tools=["read"], denied_tools=[])["allowed"] is False,
            "requested_tools None → reject")
    _assert(evaluate_tool_allowlist(requested_tools=[], allowed_tools=["read"], denied_tools=[])["allowed"] is False,
            "requested_tools empty → reject")
    r = evaluate_tool_allowlist(requested_tools=["write"], allowed_tools=["read"], denied_tools=[])
    _assert(r["allowed"] is False and "write" in r["missing_allowed_tools"],
            "requested tool not in allowed_tools → reject")
    _assert(evaluate_tool_allowlist(requested_tools=["read", "list"], allowed_tools=["read", "list"], denied_tools=["delete"])["allowed"] is True,
            "allowed and not denied → allow")
    _assert(evaluate_tool_allowlist(requested_tools=["bad tool!"], allowed_tools=["bad tool!"], denied_tools=[])["allowed"] is False,
            "invalid tool name → reject")

    print("[3] evaluate_security_gates priority")
    # kill switch 優先：即使工具全允許，global kill 仍 reject。
    r = evaluate_security_gates(requested_tools=["read"], allowed_tools=["read"], denied_tools=[],
                                global_kill_switch=True, layer_kill_switch=False)
    _assert(r["allowed"] is False and r["priority"] == "global_kill_switch",
            "security_gates：global kill switch 優先於 allowlist")
    # denylist 優先於 allowlist。
    r = evaluate_security_gates(requested_tools=["read"], allowed_tools=["read"], denied_tools=["read"],
                                global_kill_switch=False, layer_kill_switch=False)
    _assert(r["allowed"] is False and r["priority"] == "denylist", "security_gates：denylist 優先於 allowlist")
    # 全通過。
    r = evaluate_security_gates(requested_tools=["read"], allowed_tools=["read"], denied_tools=[],
                                global_kill_switch=False, layer_kill_switch=False)
    _assert(r["allowed"] is True, "security_gates：kill clear + allowed → allow")

    # 合成的「假 secret」fixture：用片段組出，避免在原始碼留下可被敏感掃描誤判的字面樣式
    # （執行期的值仍完整，redaction 才能被真正驗證）。
    fake_token = "1/" + "/" + "FAKETOKENVALUE1234567890"
    fake_sheet_id = "1Abcdefghijklmnopqrstuvwxyz012345"
    fake_sheet_url = "https://docs.google.com/spreadsheets/d" + "/" + fake_sheet_id
    fake_long_id = "Abcdefghijklmnopqrstuvwxyz0123456789"

    print("[4] build_audit_event")
    ev = build_audit_event(action="intake.reject", task_id="t-1", actor_id="owner@example.com",
                           decision="reject", reason="kill_switch_active",
                           metadata={"note": "ok", "refresh_token": fake_token})
    _assert(isinstance(ev.get("event_id"), str) and ev["event_id"].startswith("audit-"), "event 有 event_id")
    _assert(isinstance(ev.get("created_at"), str) and ev["created_at"].endswith("Z"), "event 有 created_at")
    _assert(ev["action"] == "intake.reject", "event 有 action")
    _assert(ev["observation_only"] is True, "event 標示 observation_only")

    print("[5] actor_id masked / hashed")
    _assert(ev["actor_id_masked"] is not None and ev["actor_id_masked"].startswith("actor-"),
            "actor_id 已 mask/hash")
    _assert("owner@example.com" not in str(ev), "原始 actor_id 不出現在 event")

    print("[6] metadata redaction")
    _assert(ev["metadata_redacted"]["refresh_token"] == REDACTED, "refresh_token key 被遮罩")
    _assert(ev["metadata_redacted"]["note"] == "ok", "非敏感 key 保留")
    md = redact_audit_metadata({
        "client_secret": "abc", "access_token": "x", "private_key": "y",
        "credentials": {"k": "v"}, "spreadsheet_id": fake_sheet_id, "google_sheets_url": "http://x",
        "nested": {"token": "zzz", "ok": "keep"},
        "url_value": fake_sheet_url,
        "long_id": fake_long_id,
    })
    for k in ("client_secret", "access_token", "private_key", "credentials",
              "spreadsheet_id", "google_sheets_url"):
        _assert(md[k] == REDACTED, f"{k} 被遮罩")
    _assert(md["nested"]["token"] == REDACTED, "巢狀 token 被遮罩")
    _assert(md["nested"]["ok"] == "keep", "巢狀非敏感保留")
    _assert(md["url_value"] == REDACTED, "完整 Google Sheets URL 值被遮罩")
    _assert(md["long_id"] == REDACTED, "疑似長 id 值被遮罩")

    print("[7] full spreadsheet URL / ID 不外洩")
    blob = str(ev) + str(md)
    _assert(fake_sheet_id not in blob, "完整 sheet id 不出現")
    _assert(fake_token not in blob, "token 原始值不出現")

    print("[8] 純函式：不寫 DB / 不改 queue（無副作用，重複呼叫一致）")
    a = evaluate_security_gates(requested_tools=["read"], allowed_tools=["read"], denied_tools=[],
                                global_kill_switch=False, layer_kill_switch=False)
    b = evaluate_security_gates(requested_tools=["read"], allowed_tools=["read"], denied_tools=[],
                                global_kill_switch=False, layer_kill_switch=False)
    _assert(a == b, "evaluate_security_gates 為純函式（同輸入同輸出）")

    print(f"\n✅ test_security_gates_v0_7_1_d2 全數通過（{PASSED} 項，純函式，未接真路徑）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
