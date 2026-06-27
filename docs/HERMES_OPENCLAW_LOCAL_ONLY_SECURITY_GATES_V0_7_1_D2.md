# Hermes x OpenClaw — Local-only Security Gates v0.7.1-D2

> 把 v0.7.1-D 的 Kill Switch / Audit Log / Per-tool Allowlist 規格，做成**獨立、local-only、純函式可測試模組**。
> **不接 `app/main.py` / `worker.py`、不改 Queue 狀態、不新增 route、不啟動 Worker、不接 Hermes/OpenClaw、不寫 Google Sheets。**

## 1. Purpose

v0.7.1-D 把 kill switch / audit / allowlist 的規格定清楚（plan-only）。
v0.7.1-D2 把這些規格**實作成純函式**，放在獨立模組 `app/security_gates_v0_7.py`，
可被單元測試覆蓋，但**完全不接任何真路徑**（intake / approve / worker / OpenClaw 都不接）。

目的：先讓「判斷邏輯」正確、可測、安全；未來要把 gate 接進真路徑時，只是「呼叫已驗證的純函式」。

## 2. Relationship To v0.7.1-D

- v0.7.1-D：規格 / plan（gate 優先序、kill switch 控制點、audit schema、allowlist 規則）。
- v0.7.1-D2（本版）：依規格實作純函式 `evaluate_kill_switch` / `evaluate_tool_allowlist` /
  `evaluate_security_gates` / `redact_audit_metadata` / `build_audit_event`，加測試與 readiness。
- 真正接線（intake / approve / worker / OpenClaw）留待後續、需逐層批准。

## 3. What Was Implemented

`app/security_gates_v0_7.py`（純函式）：

```text
evaluate_kill_switch(global_kill_switch, layer_kill_switch) -> dict
evaluate_tool_allowlist(requested_tools, allowed_tools, denied_tools) -> dict
evaluate_security_gates(...) -> dict   # 套用完整優先序
redact_audit_metadata(metadata) -> dict
build_audit_event(...) -> dict         # observation-only audit event
```

回傳決策結構：`allowed / decision / reason / priority`（allowlist 另含 `matched_denied_tools` / `missing_allowed_tools`）。

## 4. What v0.7.1-D2 Does Not Do

```text
No app/main.py modification.
No worker.py modification.
No queue_store.py modification.
No result_sink.py modification.
No DB write.
No Queue status mutation.
No new route.
No new POST handler.
No Worker start.
No OpenClaw execution.
No Hermes webhook.
No Google Sheets write.
Audit events are observation-only, not Queue source of truth.
```

- 模組不 import `app.main` / `app.worker` / `app.queue_store` / `app.result_sink`。
- 不寫 DB / sqlite、不連外、不讀 secrets。

## 5. Security Gate Priority

`evaluate_security_gates` 套用優先序（任一拒絕即停）：

```text
1. Global kill switch
2. Layer-specific kill switch
3. Denylist
4. Allowlist
```

（完整跨層順序見 v0.7.1-D 文件：之後還有 risk/approval gate、queue status gate、worker execution gate，本模組先實作前四層的純判斷。）

## 6. Kill Switch Evaluation

`evaluate_kill_switch`：

```text
global_kill_switch is True   → reject（priority=global_kill_switch）
global_kill_switch is None   → reject（fail-closed，unknown 視為 active）
layer_kill_switch is True    → reject（priority=layer_kill_switch）
layer_kill_switch is None    → reject（fail-closed）
兩者皆明確 False              → allow
```

kill switch **優先於** allowlist；無法判定一律視為 active（reject）。

## 7. Per-tool Allowlist Evaluation

`evaluate_tool_allowlist` 規則：

```text
requested_tools 空 / None        → reject
tool name 格式不合法              → reject（^[a-zA-Z0-9_.:-]{1,64}$）
denied_tools 命中                 → reject（denylist 優先）
allowed_tools 空 / None           → reject（fail-closed）
requested tool 不在 allowed_tools → reject
全部 requested 都在 allowed 且未 denied → allow
```

## 8. Denylist Priority

```text
denylist 優先於 allowlist（同時命中 → 拒絕）
kill switch 優先於所有 allowlist
unknown / invalid tool → reject
local-only 不得被推成 executable（沿用 v0.7.1-C view-model 保守原則）
```

## 9. Audit Event Builder

`build_audit_event` 產生 observation-only 事件，欄位：

```text
event_id, created_at, actor_type, actor_id_masked, action, task_id, correlation_id,
from_status, to_status, decision, reason, risk_level, source_mode, intake_mode,
tool_name, metadata_redacted, observation_only=True
```

- `actor_id` 一律 mask/hash（`actor-<sha256[:12]>`），不輸出原始值。
- `metadata` 一律經 `redact_audit_metadata` 遮罩。
- **不改任何 queue 狀態**；event 只是純資料。

## 10. Audit Metadata Redaction

`redact_audit_metadata`：

- 敏感 key（含子字串）一律遮罩為 `***REDACTED***`：
  `refresh_token / client_secret / access_token / private_key / credentials / token /
  spreadsheet_id / google_sheets_url / secret / password`。
- 可疑「值」也遮罩：完整 Google Sheets URL（`spreadsheets/d/<id>`）、token 前綴（`ya29.` / `1//` / `gocspx-`）、private key 區塊、疑似長 id。
- 巢狀 dict / list 遞迴遮罩。

## 11. Observation-only Boundary

- audit event 為 **observation-only**，不寫 DB、不改 queue 狀態、不影響 claim / 執行。
- 本模組所有函式皆純函式：相同輸入 → 相同輸出，無副作用。

## 12. Queue Source-of-truth Boundary

- **Queue SQLite remains the source of truth for task state.**
- security gates 只「准許 / 拒絕 / 記錄」，不定義或改變任務狀態。

## 13. Result Sink Boundary

- **Result Sink is observation-only, not Queue source of truth.**
- 本模組不呼叫 Result Sink、不寫任何 sink。

## 14. Google Sheets Boundary

- 維持 `GOOGLE_SHEETS_ENABLED=false`；不 import / 不呼叫任何 Google client。

## 15. Security / Secrets Rules

- 不讀 / 不顯示任何 secret；audit 一律遮罩（`actor_id_masked` / `metadata_redacted`）。
- 不輸出原始 token / client secret / private key / 完整 spreadsheet ID / 完整 Google Sheets URL。
- 敏感檢查（readiness）一律 regex / 格式比對。

## 16. Test Coverage

`scripts/test_security_gates_v0_7_1_d2.py`（純函式，不寫 DB）涵蓋：

```text
- kill switch：global/layer active → reject；None → fail-closed；both False → allow
- denylist 命中 → reject；allowed_tools 空/None → reject；requested 空/None → reject
- requested 不在 allowed → reject；invalid tool name → reject；allowed 且未 denied → allow
- evaluate_security_gates 優先序（kill switch > denylist > allowlist）
- build_audit_event：event_id / created_at / action / observation_only
- actor_id masked/hashed；metadata 敏感 key 遮罩；完整 URL / ID 不外洩
- 模組未 import main / worker / queue_store / result_sink；純函式無副作用
```

## 17. Readiness Checks

`scripts/check_hermes_openclaw_local_only_security_gates_v0_7_1_d2_readiness.py`（純靜態）：

```text
- doc / module / test / readiness 存在；doc 含必要章節與安全聲明
- module 不 import main / worker / queue_store / result_sink
- module 不呼叫 enqueue / claim_next / approve / reject / run_openclaw_cli / google client
- module 不寫 DB / sqlite
- module 含 evaluate_kill_switch / evaluate_tool_allowlist / redact_audit_metadata / build_audit_event
- module 實作 denylist priority / allowlist fail-closed
- app/main.py / worker.py / queue_store.py / result_sink.py 未被接入
- 無新增 route / webhook / POST handler；GOOGLE_SHEETS_ENABLED 無 true
- 無完整 spreadsheet URL / ID / token / private key（格式比對）
```

## 18. Future Integration Criteria

把這些純函式接進真路徑前（需 Owner 逐層批准）：

```text
[ ] intake 層：queue_intake_bridge 呼叫 evaluate_security_gates（拒絕即不寫）
[ ] approval 層：approve→queued 前再評估一次
[ ] worker 層：claim 後、OpenClaw 執行前最後一道（縱深防禦）
[ ] audit：在各決策點 build_audit_event 並寫獨立 git-ignored 紀錄（observation-only）
[ ] 全程不改 queue source-of-truth、可急停（kill switch 立即生效）、可回退
```

## 19. Explicit Non-goals

- 不接 `app/main.py` / `worker.py`、不改 `queue_store.py` / `result_sink.py`。
- 不新增 route / webhook / POST handler / DB table。
- 不接真 Hermes / 真 OpenClaw、不啟動 Worker、不寫 Queue DB、不改 Queue 狀態、不寫 Google Sheets。
- 不讀 / 不顯示 secret。不進 v0.7.1-E。

## 20. Final Recommendation

純函式 security gates 已實作且測試覆蓋（kill switch / allowlist / denylist / audit / redaction）。
建議下一步（需 Owner 逐層批准）才把它接進 **intake 層**（最早、最安全），
再依序 approval → worker，並在各決策點產生 observation-only audit。

本版到此收住——**不 commit（除非 Owner 批准）、不 push、不 tag、不進 v0.7.1-E。**
