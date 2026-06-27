# Hermes x OpenClaw — Local-only Intake Security Gates Wiring v0.7.1-E

> 把 v0.7.1-D2 的純函式安全閘（`evaluate_security_gates`）接進 **local-only intake bridge**。
> 只限 `app/queue_intake_bridge_v0_7.py`；**不接 main / worker，不改 queue_store / result_sink / security_gates**。

## 1. Purpose

讓 local-only intake 在既有 task_type allowlist 之上，再加一層 **tool-level security gate**
（kill switch / denylist / allowlist），且**預設關閉**、一旦開啟即 **fail-closed**。
reject 一律不寫 DB；成功寫入仍維持 `waiting_review`、不可執行。

## 2. Relationship To v0.7.1-B / D / D2

- v0.7.1-B：local-only intake bridge（kill switch + task_type allowlist + waiting_review）。
- v0.7.1-D：kill switch / audit / per-tool allowlist 規格（plan）。
- v0.7.1-D2：把規格做成純函式模組 `app/security_gates_v0_7.py`（不接任何真路徑）。
- v0.7.1-E（本版）：把 `evaluate_security_gates` / `build_audit_event` 接進 intake bridge（local-only）。

## 3. What Was Implemented

- 修改 `app/queue_intake_bridge_v0_7.py`：
  - import `evaluate_security_gates` / `build_audit_event`（純函式）。
  - 新增 `GLOBAL_KILL_SWITCH`（最優先）與 `INTAKE_SECURITY_GATES_ENABLED`（tool gate 開關，預設 false）。
  - 在 task_type allowlist 後、production DB guard 前，加入 tool-level security gate。
  - gate reject → 回傳 `reason="security_gate_rejected"` + `security_gate` 決策 + observation-only `audit_event`，**不寫 DB**。

## 4. What Was Not Implemented

```text
No app/main.py modification.
No worker.py modification.
No queue_store.py modification.
No result_sink.py modification.
No security_gates_v0_7.py modification.
No DB schema change.
No new route.
No new POST handler.
No Worker start.
No OpenClaw execution.
No Hermes webhook.
No Google Sheets write.
```

- audit event 產生但**本版不落地**（不寫 audit 檔）。

## 5. Requested Tools Source

- requested tools 來源**固定為** `task_envelope["metadata"]["requested_tools"]`（Owner v0.7.1-E 裁定）。
- 不改 schema、不新增 TaskEnvelope 頂層欄位、不用 task text / prompt 猜工具。
- `allowed_tools` / `denied_tools` 取自 TaskEnvelope 頂層既有欄位。

## 6. Missing Requested Tools Behavior

```text
INTAKE_SECURITY_GATES_ENABLED=false：
  不啟用 tool gate，維持既有 v0.7.1-B 行為（回歸測試不受影響）。

INTAKE_SECURITY_GATES_ENABLED=true：
  metadata.requested_tools 缺失 / 空 / 非 list[str] → fail-closed reject，不寫 DB。
```

## 7. INTAKE_SECURITY_GATES_ENABLED Behavior

- 預設 **false**；`true / 1 / yes / on` → true，其他 / unset → false。
- false 時 tool gate 完全略過（B 行為）；true 時 tool gate 內部一律 fail-closed。

## 8. GLOBAL_KILL_SWITCH Behavior

- 預設 **false**；`true / 1 / yes / on` → true，其他 / unset → false。
- **最高優先**：active 時最先 reject（`global_kill_switch_active`），不寫 DB。

## 9. Security Gate Priority

intake bridge 的實際判斷順序（任一拒絕即停、fail-closed）：

```text
1. GLOBAL_KILL_SWITCH active        → reject:global_kill_switch_active
2. INTAKE_KILL_SWITCH active        → reject:kill_switch_active
3. QUEUE_INTAKE_ENABLED != true     → reject:intake_disabled
4. validate_task_envelope
5. task_type allowlist              → reject:task_type_not_allowlisted
6. (若 INTAKE_SECURITY_GATES_ENABLED) tool gate：denylist > allowlist → reject:security_gate_rejected
7. production DB path guard         → reject:refuse_production_db
8. 建立 local-only payload（status=pending_approval）
9. enqueue(initial_status=WAITING_REVIEW)
```

第 6 步內部由 `evaluate_security_gates` 套用 denylist 優先於 allowlist。

## 10. Local-only Intake Flow

- 只寫 `INTAKE_QUEUE_DB_PATH` 指定的 local-only DB；撞 production `queue.db` → reject。
- 成功寫入：`initial_status=WAITING_REVIEW`、payload `status=pending_approval`、
  metadata `local_only=true / mock=true / executable_by_worker=false`、回傳 `executable_by_worker=false`。

## 11. Reject Semantics

```text
Rejects do not write Queue DB.
```

- 任何 gate reject → `accepted=False`、`written=False`、不 enqueue、不改 Queue 狀態、不寫 audit 檔。
- security gate reject 回傳含 `security_gate`（決策 dict）與 `audit_event`（observation-only）。

## 12. Audit Event Boundary

```text
Audit event is observation-only and not persisted in this version.
```

- `build_audit_event` 產生純資料 event（actor_id 遮罩、metadata redact）；本版**只回傳、不寫檔**。
- audit event 不改 Queue 狀態、不影響 claim / 執行。

## 13. Queue Source-of-truth Boundary

```text
Queue SQLite remains the source of truth for task state.
Successful writes remain waiting_review.
Tasks must not become queued.
executable_by_worker remains false.
```

## 14. Worker / OpenClaw Boundary

- 不啟動 Worker、不 import `app.worker`、不呼叫 `run_openclaw_cli`、不呼叫 OpenClaw。
- `claim_next` 只取 `queued`，故 `waiting_review` 任務 worker 結構上無法執行。

## 15. Google Sheets Boundary

- 維持 `GOOGLE_SHEETS_ENABLED=false`；不 import / 不呼叫任何 Google client。**No Google Sheets write.**

## 16. Security / Secrets Rules

- 不讀 / 不顯示任何 secret；audit event 經 `redact_audit_metadata` 遮罩（不輸出原始 token / client secret / 完整 spreadsheet ID / URL / private key）。
- requested_tools / allowed_tools / denied_tools 為工具名稱清單，非 secret。
- 敏感檢查（readiness）一律 regex / 格式比對。

## 17. Test Coverage

`scripts/test_intake_security_gates_v0_7_1_e.py`（tempfile DB）涵蓋：

```text
- gate disabled → B happy path 寫入 waiting_review
- gate enabled：missing / empty / 非 list[str] requested_tools → reject 不寫
- allowed_tools 缺失/空 → reject；denied 命中 → reject；不在 allowlist → reject；invalid name → reject
- allowed 且未 denied → 寫入 waiting_review
- GLOBAL_KILL_SWITCH / INTAKE_KILL_SWITCH → reject 不寫
- task_type allowlist 仍生效；production DB guard 仍生效
- 成功 payload local_only/mock/executable_by_worker=false、status 不是 queued
- claim_next 不 claim waiting_review；bridge 未 import main/worker、未呼叫 OpenClaw/Google
```

## 18. Readiness Checks

`scripts/check_hermes_openclaw_local_only_intake_security_gates_v0_7_1_e_readiness.py`（純靜態）至少檢查：

```text
- doc / test / readiness 存在；doc 含必要章節與安全聲明
- bridge import evaluate_security_gates、含 INTAKE_SECURITY_GATES_ENABLED、metadata.requested_tools 來源
- bridge reject path written=False；成功 path initial_status=WAITING_REVIEW、executable_by_worker=false
- bridge 不 import main / worker / result_sink、不呼叫 run_openclaw_cli / google、不新增 route / POST
- main/worker/queue_store/result_sink/security_gates 未被修改
- GOOGLE_SHEETS_ENABLED 無 true；無完整 spreadsheet URL / ID / token / private key（格式比對）
```

## 19. Future Integration Criteria

把 gate 接到更後面層（需 Owner 逐層批准）：

```text
[ ] approval 層：approve→queued 前再評估一次（仍不可讓 local-only 變 queued）
[ ] worker 層：claim 後、OpenClaw 執行前最後一道（縱深防禦）
[ ] audit 落地：寫獨立 git-ignored 檔，observation-only，不進 production queue.db
[ ] requested_tools 來源若要擴充（如真 Hermes 帶入），需另行設計與批准
```

## 20. Explicit Non-goals

- 不接 `app/main.py` / `worker.py`；不改 `queue_store.py` / `result_sink.py` / `security_gates_v0_7.py`。
- 不新增 route / POST handler / DB table；不啟動 Worker；不接真 Hermes / OpenClaw；不寫 Google Sheets。
- 不落地 audit log；不讓任務變 `queued`；不讀 / 不顯示 secret。不進 v0.7.1-F。

## 21. Final Recommendation

tool-level security gate 已安全接進 local-only intake：預設關閉、開啟即 fail-closed、reject 不落地、
成功仍 `waiting_review` 不可執行。建議下一步（需 Owner 批准）才評估 audit 落地與 approval/worker 層接線。

本版到此收住——**不 commit（除非 Owner 批准）、不 push、不 tag、不進 v0.7.1-F。**
