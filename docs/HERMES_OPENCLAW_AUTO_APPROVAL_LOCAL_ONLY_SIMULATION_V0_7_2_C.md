# Hermes × OpenClaw — Auto-Approval Local-only Simulation (v0.7.2-C)

> 安全摘要（boundary statements）：
> - v0.7.2-C is local-only simulation.
> - v0.7.2-C does not read real Queue DB.
> - v0.7.2-C does not read production task data.
> - v0.7.2-C does not write QueueStore.
> - v0.7.2-C does not modify Queue status.
> - v0.7.2-C does not wire routes.
> - v0.7.2-C does not wire intake bridge.
> - v0.7.2-C does not wire approve route.
> - v0.7.2-C does not start Worker.
> - v0.7.2-C does not call OpenClaw.
> - v0.7.2-C does not call Hermes.
> - v0.7.2-C does not write Google Sheets.
> - v0.7.2-C does not read or display secrets.
> - v0.7.2-C does not use network.
> - v0.7.2-C does not use subprocess.
> - Simulation does not mean execution.
> - Decision preview does not mean queued.
> - can_execute is always false.
> - queue_transition_allowed is always false.
> - observation_only is always true.

## 1. Purpose

v0.7.2-C 新增一個「假工單模擬器」（local-only simulation CLI），用內建 sample tasks
呼叫 v0.7.2-B 的純函式 `evaluate_auto_approval(...)`，把 policy decision **預覽**列印出來，
方便人工檢視「在 safe autopilot 設定下，哪些任務會被自動通過、哪些需 Owner、哪些被禁止」。

本版只新增 4 個檔案：

- `docs/HERMES_OPENCLAW_AUTO_APPROVAL_LOCAL_ONLY_SIMULATION_V0_7_2_C.md`
- `scripts/simulate_auto_approval_policy_v0_7_2_c.py`
- `scripts/test_auto_approval_local_only_simulation_v0_7_2_c.py`
- `scripts/check_hermes_openclaw_auto_approval_local_only_simulation_v0_7_2_c.py`

不修改任何既有檔案，不更新 current-state aggregator（如需收編，另開 C2）。

## 2. Relationship To v0.7.2-B

v0.7.2-B 提供純函式 helper `app/auto_approval_policy_v0_7.py:evaluate_auto_approval`。
v0.7.2-C 是 **additive** 的展示層：只 import 並呼叫該 helper，不改動它、不取代它。
C 建立在 B 之上，因此 **不應** 讓 v0.7.2-B readiness 變 stale。

## 3. Relationship To v0.7.2-B2

v0.7.2-B2 把 v0.7.2-A 標為 expected-stale，並把 B helper / B test 列為 current green gate。
v0.7.2-C 不修改 B2 的 doc / readiness，也不修改 current-state aggregator，因此 **不應**
讓 v0.7.2-B2 readiness 變 stale。

## 4. Why Local-only Simulation

先 mock、再 real；先觀察、再接線。auto-approval 的 policy 決策已在 B 做成純函式，
但人類需要一個「看得到、可重跑、零副作用」的方式來檢視政策在各種任務形狀下的行為。
local-only simulation 正好滿足：完全離線、不碰真 Queue、不寫任何狀態，只印 decision preview。

## 5. Simulation Is Not Execution

Simulation does not mean execution. Decision preview does not mean queued.
模擬器顯示的 `auto_approved` 只是 policy 層預覽；helper 仍恆回傳
`can_execute=false / queue_transition_allowed=false / observation_only=true`，
沒有任何任務會因為被模擬而進入 Queue 或被 Worker 執行。

## 6. CLI Interface

```bash
python scripts/simulate_auto_approval_policy_v0_7_2_c.py
python scripts/simulate_auto_approval_policy_v0_7_2_c.py --sample all
python scripts/simulate_auto_approval_policy_v0_7_2_c.py --sample level0
python scripts/simulate_auto_approval_policy_v0_7_2_c.py --sample level1
python scripts/simulate_auto_approval_policy_v0_7_2_c.py --sample level2
python scripts/simulate_auto_approval_policy_v0_7_2_c.py --sample level3
python scripts/simulate_auto_approval_policy_v0_7_2_c.py --sample edge
python scripts/simulate_auto_approval_policy_v0_7_2_c.py --json
python scripts/simulate_auto_approval_policy_v0_7_2_c.py --profile default-off
```

預設：`--sample all`、human-readable、`--profile safe`（safe_autopilot simulation profile）。

## 7. Safe Autopilot Simulation Profile

模擬展示需要一個「安全設定檔」才能顯示 Level 0 / Level 1 的 auto_approved：

```python
auto_approval_mode="safe"
safe_autopilot_enabled=True
low_risk_auto_approval_enabled=True
auto_approval_policy="safe"
global_kill_switch=False
auto_approval_kill_switch=False
```

這只是模擬用 profile，**不是 dangerous mode**：即使在此 profile 下，helper 仍恆回傳
`can_execute=false / queue_transition_allowed=false / observation_only=true`。本模擬器不接 env、
不改 production flags、不啟用任何 skip-permissions 類行為。

## 8. Default-off Profile Behavior

`--profile default-off` 將所有 flags 設為關閉（`auto_approval_mode="off"` 等）。
此時每一個 sample 都會 fallback 到 `needs_owner_approval`（reason `auto_approval_mode_off`，
在 forbidden-op / protected-file 檢查之前就短路）。這證明：**未開啟 safe autopilot 時，
沒有任何任務會被自動通過。**

## 9. Sample Task Catalog

所有 sample tasks 皆內建於 simulation script，不讀外部檔案、不讀 Queue DB、不讀 production data。
分為 `level0 / level1 / level2 / level3 / edge` 五群，可用 `--sample <group>` 篩選。

## 10. Level 0 Samples

唯讀 / report / test / compile / readiness_check（safe_autopilot profile 下 → `auto_approved`，
matched_level 0）：

- level0_read_only_query, level0_report, level0_test, level0_compile, level0_readiness_check

## 11. Level 1 Samples

local-only docs / plan / pure helper（safe profile 下 → `auto_approved`，matched_level 1）：

- level1_docs_only, level1_plan_only, level1_pure_helper_local

## 12. Level 2 Samples

protected file 命中或非 safe task_type（→ `needs_owner_approval`，matched_level 2）：

- level2_protected_main, level2_queue_store（protected_file_touched）
- level2_commit_operation, level2_state_machine_change, level2_approve_route
  （task_type_not_in_safe_allowlist）

## 13. Level 3 Samples

forbidden operations（→ `prohibited`，matched_level 3）：

- level3_git_push, level3_git_tag, level3_read_secrets, level3_display_secrets,
  level3_production_db, level3_worker_start, level3_openclaw_call, level3_hermes_call,
  level3_google_sheets_live_write, level3_webhook

## 14. Edge Case Samples

fail-closed / kill switch / 不合法輸入：

- unknown_task_type, missing_safety_level, invalid_safety_level, requires_confirmation_true,
  empty_requested_tools, empty_allowed_tools, unknown_requested_tool（→ needs_owner_approval）
- denied_tool_hit（→ prohibited）
- kill_switch_global, kill_switch_auto_approval（→ rejected）
- task_row_not_dict, payload_missing_or_invalid, invalid_requested_operations,
  invalid_touched_files, unsupported_auto_approval_mode, safety_level_too_high,
  client_protected_file（→ needs_owner_approval / fail-closed）

## 15. JSON Output Schema

`--json` 輸出為 valid JSON：

```json
{
  "version": "v0.7.2-C",
  "mode": "simulation",
  "profile": "safe_autopilot",
  "observation_only": true,
  "samples": [
    {
      "sample_name": "level0_read_only_query",
      "policy_decision": "auto_approved",
      "matched_level": 0,
      "reason": "auto_approved_low_risk",
      "can_auto_approve": true,
      "can_execute": false,
      "queue_transition_allowed": false,
      "observation_only": true
    }
  ],
  "summary": {
    "auto_approved": 0,
    "needs_owner_approval": 0,
    "rejected": 0,
    "prohibited": 0,
    "total": 0
  }
}
```

每筆 sample 必含：`sample_name / policy_decision / matched_level / reason / can_auto_approve /
can_execute / queue_transition_allowed / observation_only`，且 `can_execute=false /
queue_transition_allowed=false / observation_only=true` 恆定。

## 16. Summary Counts

輸出含 summary：`auto_approved / needs_owner_approval / rejected / prohibited / total`，
數值由逐筆 decision 統計而得（與測試交叉驗證一致）。

## 17. can_execute Boundary

can_execute is always false. 模擬器不執行任何任務，也不可能執行。

## 18. queue_transition_allowed Boundary

queue_transition_allowed is always false. 模擬器不改任何 Queue 狀態轉換。

## 19. observation_only Boundary

observation_only is always true. 所有輸出皆為觀察用 decision preview。

## 20. QueueStore Boundary

v0.7.2-C does not write QueueStore. v0.7.2-C does not modify Queue status.
模擬器不 import QueueStore、不呼叫 approve / reject / claim_next、不讀真 Queue DB、
不讀 production task data。

## 21. Route Boundary

v0.7.2-C does not wire routes. v0.7.2-C does not wire intake bridge.
v0.7.2-C does not wire approve route. 模擬器不定義任何 route / webhook / POST handler。

## 22. Worker / OpenClaw Boundary

v0.7.2-C does not start Worker. v0.7.2-C does not call OpenClaw.
模擬器不啟動 Worker、不呼叫 OpenClaw CLI、不開子行程。

## 23. Hermes Boundary

v0.7.2-C does not call Hermes. 模擬器不建立任何 Hermes webhook、不呼叫 Hermes。

## 24. Google Sheets Boundary

v0.7.2-C does not write Google Sheets. 模擬器不 import 任何 Google / gspread / oauth client，
不改 `GOOGLE_SHEETS_ENABLED`。

## 25. Secrets Boundary

v0.7.2-C does not read or display secrets. 模擬器不讀、不顯示任何 secret；sample tasks 為合成資料，
不含任何真實憑證、token 或完整 spreadsheet id。

## 26. No Network / No Subprocess Boundary

v0.7.2-C does not use network. v0.7.2-C does not use subprocess.
模擬器只用 stdlib（argparse / copy / json / sys / pathlib / typing）與 `evaluate_auto_approval`，
不連外、不開子行程。

## 27. Tests

`scripts/test_auto_approval_local_only_simulation_v0_7_2_c.py` 直接 import 模組（不開子行程），
驗證所有 sample 的 decision / matched_level / reason、固定安全旗標、summary、--json、
default-off 行為、不 mutate task_row，以及 import 邊界。

## 28. Readiness

`scripts/check_hermes_openclaw_auto_approval_local_only_simulation_v0_7_2_c.py` 為靜態 readiness：
檢查 4 檔存在、simulation import 邊界與無接線痕跡、sample 覆蓋 Level 0–3 + edge、test 覆蓋、
doc 章節與聲明、B / B2 / current-state 仍 green、git-diff allowlist 只含本版 4 檔、無真 secret、
無 route wiring、無 network/subprocess、無 dangerous skip-permissions 模式。

## 29. Current-State Aggregator Future Update

本版不更新 current-state aggregator。未來如要把 C readiness + C test 收為 current green gate，
應另開 v0.7.2-C2（additive；不得讓 B / B2 stale）。

## 30. Future v0.7.2-D

v0.7.2-D（Intake Annotation）將在 intake 階段為任務「標註」policy 決策，仍 observation-only、
不改狀態、不接 approve route。C 為 D 的前置展示層。

## 31. Explicit Non-goals

不接 route / intake bridge / approve route、不改 QueueStore、不讀真 Queue DB、不啟 Worker、
不呼叫 OpenClaw / Hermes、不寫 Google Sheets、不讀/顯示 secrets、不連網、不開子行程、
不 tag、不 commit（除非 Owner 另行批准）。

## 32. Final Recommendation

建議 Owner 檢視本版 4 檔與檢查結果。C 是純展示層、零副作用、完全 additive，不影響 B / B2 /
current-state。確認後再決定是否 commit，以及是否進入 v0.7.2-C2（aggregator 收編）或 v0.7.2-D。
