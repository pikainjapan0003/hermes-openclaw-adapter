# Hermes x OpenClaw — Approval-to-Queued Security Gate (Pure Helper) v0.7.1-F

> 把「`waiting_review / pending_approval → queued` 之前應檢查的安全規則」做成**獨立純函式 helper**。
> 本版**只回決策**：不接 approve route、不改 `app/main.py`、不改 `app/queue_store.py`、不改 production 狀態機。

## 1. Purpose

目前 approve（API 與 Dashboard）只走 `QueueStore.approve`（waiting_review→queued），
**完全沒有** tool allowlist / kill switch / local-only / executable_by_worker 檢查。
v0.7.1-F 先把「approve 到 queued 之前該擋什麼」做成**可測試的純函式 helper**，
未來再決定是否接進 approve route（需逐層批准）。

## 2. Relationship To v0.7.1-E

- v0.7.1-E：把 `evaluate_security_gates` 接進 **intake bridge**（寫入前的 tool gate）。
- v0.7.1-F（本版）：把同一套 security gate + local-only/mock/executable 檢查，包成
  **approval-to-queued 的純函式 helper**（`evaluate_approval_to_queued`），但**不接 route**。

## 3. Why This Version Is Pure Helper Only

- approve route 與 `QueueStore.approve` 碰的是 **production 狀態機**（waiting_review→queued），屬最高風險。
- 先把判斷邏輯做對、可測、fail-closed，未來接 route 時只是「呼叫已驗證純函式」，改動小、可審查、可逐層批准。
- 本版零接線風險：只新增 helper + 測試 + readiness + 文件。

## 4. What Was Implemented

`app/approval_security_gate_v0_7.py`（純函式）：

```text
evaluate_approval_to_queued(task_row, *, approval_security_gates_enabled=False,
                            global_kill_switch=False, layer_kill_switch=False) -> dict
extract_payload / extract_metadata / extract_requested_tools / build_approval_audit_event
APPROVAL_SECURITY_GATES_ENABLED（文件化常數，預設 False；本版用函式參數控制，不接 env）
```

- reuse `app.security_gates_v0_7.evaluate_security_gates` / `build_audit_event`。
- 回傳 decision dict：`allowed / decision / reason / priority`（+ 視情況 `security_gate` / `audit_event`）。

## 5. What Was Not Implemented

```text
No app/main.py modification.
No queue_store.py modification.
No worker.py modification.
No result_sink.py modification.
No security_gates_v0_7.py modification.
No queue_intake_bridge_v0_7.py modification.
No DB write.
No Queue status mutation.
No approve route wiring.
No Dashboard approve wiring.
No new route.
No new POST handler.
No Worker start.
No OpenClaw execution.
No Hermes webhook.
No Google Sheets write.
```

- audit event 產生但**不落地**。

## 6. APPROVAL_SECURITY_GATES_ENABLED Behavior

- 本版用**函式參數** `approval_security_gates_enabled`（預設 `False`）控制，**不接 env、不接 main route**。
- `False`：回 `allowed=True` / `reason="approval_security_gates_disabled"`，不強制 tool gate，
  **不破壞 production 既有 approve flow**（未來接 route 時預設安全）。
- `True`：啟用 fail-closed 檢查。

## 7. Approval-to-Queued Risk

- `QueueStore.approve` 是純狀態機，不看 payload / metadata / tool。
- 目前 local-only intake 任務寫在獨立 intake DB，approve route 讀 production queue，**今天看不到**。
- 但若未來任何流程把 local_only / mock / executable_by_worker=false 任務帶進 production queue 成 waiting_review，
  現有 approve 會**毫無檢查**地轉成 queued → 變 worker 可執行。本 helper 就是為了在這個邊界擋下。

## 8. Input Task Row Model

helper 接受 QueueStore row-like dict：

```python
{
    "task_id": "...", "status": "waiting_review", "correlation_id": "...",
    "payload": {
        "allowed_tools": ["filesystem.read"],
        "denied_tools": [],
        "metadata": {"requested_tools": ["filesystem.read"],
                     "local_only": False, "mock": False, "executable_by_worker": True}
    }
}
```

`payload` 亦可為 JSON 字串。payload 缺失 / 非 dict / JSON 壞 → enabled 時 fail-closed reject。

## 9. Payload / Metadata Extraction

- `extract_payload`：dict 直接用；JSON 字串解析；其他 → None。
- `extract_metadata`：payload.metadata（dict）否則 `{}`。
- `extract_requested_tools`：固定取 `payload.metadata.requested_tools`（沿用 v0.7.1-E 來源裁定）。

## 10. Security Gate Priority

enabled 時的判斷順序（任一拒絕即停、fail-closed）：

```text
1. global kill switch
2. layer kill switch
3. status 必須是 waiting_review / pending_approval
4. payload 可解析
5. local_only=true → reject
6. mock=true → reject
7. executable_by_worker 必須明確 true（false / 缺失 → reject）
8. tool gate（evaluate_security_gates：denylist > allowlist，空 allowed/requested fail-closed）
```

## 11. Local-only / Mock / Executable Boundary

```text
local_only=true → reject (local_only_not_approvable)
mock=true → reject (mock_not_approvable)
executable_by_worker != true（含缺失）→ reject (executable_by_worker_not_true)
```

保守策略：**executable_by_worker 缺失即 reject**（fail-closed）。

## 12. Tool Allowlist / Denylist Rules

```text
requested_tools 缺失 / 空 / 非 list[str] → reject
allowed_tools 缺失 / 空 → reject (fail-closed)
denied_tools 命中 → reject (denylist 優先)
requested tool 不在 allowed_tools → reject
invalid tool name → reject
全部 requested 都在 allowed 且未 denied → 通過此層
```

## 13. Kill Switch Rules

```text
global kill switch active → reject（最優先）
layer kill switch active → reject
kill switch 優先於所有 allowlist
```

## 14. Reject Semantics

```text
Gate rejection does not automatically transition task to rejected.
Gate rejection blocks approve-to-queued and keeps task in current review state.
```

- helper 只回 `allowed=False / decision="reject" / reason=...`，**不改任何狀態**。
- 未來接線時：reject 應阻擋 approve-to-queued，任務**保持原本 review 狀態**（不自動轉 rejected）。

## 15. Audit Event Boundary

```text
Audit event is observation-only and not persisted in this version.
```

- `build_approval_audit_event` 產生 `action="approval.security_gate"`、`observation_only=true` 的事件，
  metadata 經 redact；**不寫檔、不寫 DB、不改狀態**。

## 16. Queue Source-of-truth Boundary

```text
Queue SQLite remains the source of truth for task state.
```

- helper 不改 Queue 狀態、不寫 DB；只回決策。

## 17. Worker / OpenClaw Boundary

- 不啟動 Worker、不 import worker、不呼叫 `run_openclaw_cli`、不呼叫 OpenClaw。

## 18. Google Sheets Boundary

- 維持 `GOOGLE_SHEETS_ENABLED=false`；不 import / 不呼叫任何 Google client。**No Google Sheets write.**

## 19. Test Coverage

`scripts/test_approval_security_gate_v0_7_1_f.py`（純函式）涵蓋：

```text
- disabled → allow；非 review 狀態 → reject；payload 缺/壞/非 dict → reject
- local_only / mock / executable_by_worker=false / 缺失 → reject
- requested_tools 缺/空/非 list、allowed_tools 缺/空、denied 命中、不在 allowlist、invalid name → reject
- global / layer kill switch → reject；全部 OK → allow；JSON 字串 payload → allow
- task_row 不被 mutate；audit_event observation_only=true
- helper 未 import main/worker/queue_store/result_sink；無 approve/reject/enqueue/claim_next/openclaw/google 呼叫
```

## 20. Readiness Checks

`scripts/check_hermes_openclaw_approval_to_queued_security_gate_v0_7_1_f_readiness.py`（純靜態）至少檢查：

```text
- doc / module / test / readiness 存在；doc 含必要章節與安全聲明
- module 含 evaluate_approval_to_queued、APPROVAL_SECURITY_GATES_ENABLED、使用 evaluate_security_gates
- module 不 import main/queue_store/worker/result_sink、不呼叫 approve/reject/enqueue/claim_next/openclaw/google、不寫 DB
- module 強制 local_only / mock / executable_by_worker=false reject
- main/queue_store/worker/result_sink/security_gates/queue_intake_bridge 未被修改接入
- 無新增 route / POST；GOOGLE_SHEETS_ENABLED 無 true；無完整 spreadsheet URL/ID/token/private key
```

## 21. Future Route Wiring Criteria

把 helper 接進 approve route / `QueueStore.approve` 前（需 Owner 逐層批准）：

```text
[ ] Owner 批准修改 app/main.py approve route（或 QueueStore 前置檢查）
[ ] APPROVAL_SECURITY_GATES_ENABLED 改由受控設定提供，預設 false、fail-closed
[ ] reject 阻擋 approve-to-queued，保持 waiting_review（不自動轉 rejected）
[ ] kill switch 立即生效；可回退、可稽核
[ ] audit 落地（獨立 git-ignored 檔，observation-only，不進 production queue.db）
[ ] 完整回歸：既有 approve happy path 在 gate disabled 時不變
```

## 22. Explicit Non-goals

- 不接 `app/main.py` / `queue_store.py` / `worker.py`；不改 `result_sink.py` / `security_gates_v0_7.py` / `queue_intake_bridge_v0_7.py`。
- 不新增 route / POST / DB table；不啟動 Worker；不接真 Hermes / OpenClaw；不寫 Google Sheets。
- 不落地 audit；不自動把任務轉 rejected；不讀 / 不顯示 secret。不進 v0.7.1-F2 / v0.7.2。

## 23. Final Recommendation

approval-to-queued 的安全判斷已成為可測試純函式，預設關閉、開啟即 fail-closed，且
local_only / mock / executable_by_worker=false 一律擋下。建議下一步（需 Owner 批准）才評估
接進 approve route（v0.7.1-F2），並先在 gate disabled 下確保現有 approve flow 不變。

本版到此收住——**不 commit（除非 Owner 批准）、不 push、不 tag、不進 v0.7.1-F2 / v0.7.2。**
