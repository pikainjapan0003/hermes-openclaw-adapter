# Hermes × OpenClaw — Auto-Approval Local-only Simulation Current-State Update (v0.7.2-C2)

> 安全摘要（boundary statements）：
> - v0.7.2-C2 updates current-state only.
> - v0.7.2-C2 does not add features.
> - v0.7.2-C2 does not modify the simulation script.
> - v0.7.2-C2 does not modify the C readiness script.
> - v0.7.2-C2 does not modify the C test.
> - v0.7.2-C is additive and does not supersede v0.7.2-B.
> - v0.7.2-C is additive and does not supersede v0.7.2-B2.
> - v0.7.2-C test is a current-state green gate.
> - v0.7.2-C readiness remains a standalone readiness check and required artifact.
> - current-state aggregator does not subprocess-call C readiness, to avoid circular dependency.
> - current-state aggregator validates C simulation through C test plus inline positive assertions.
> - current-state aggregator is the source of truth for current health.
> - v0.7.2-C2 does not wire routes.
> - v0.7.2-C2 does not wire QueueStore.
> - v0.7.2-C2 does not start Worker.
> - v0.7.2-C2 does not call OpenClaw.
> - v0.7.2-C2 does not call Hermes.
> - v0.7.2-C2 does not write Google Sheets.
> - v0.7.2-C2 does not read secrets.
> - v0.7.2-C2 does not use network.
> - v0.7.2-C2 does not use subprocess.
> - v0.7.2-C2 does not create tag.

## 1. Purpose

v0.7.2-C2 只做一件事：把 v0.7.2-C 的 local-only simulation **收編進 current-state aggregator**。
為避免循環依賴（C readiness 會回呼 current-state），aggregator **只把 C test 當 subprocess green gate**，
並加入 simulation 正向斷言與邊界檢查（[4c] inline）；C readiness 改列為 required artifact 與
standalone readiness。本版不新增任何功能、不接線、不改 simulation 行為。

## 2. Context

v0.7.2-C 已 commit（`26bd7b9`），新增 4 個 local-only simulation 檔（doc / simulate / test / readiness）。
v0.7.2-C 當時刻意**不**更新 current-state aggregator，留待本 C2 收編（與 v0.7.2-B → B2 的分工一致）。

## 3. Relationship To v0.7.2-C

v0.7.2-C2 是 v0.7.2-C 的「current-state 收編層」。它只修改
`scripts/check_hermes_openclaw_v0_7_1_current_state.py`，並新增 C2 doc 與 C2 readiness。
v0.7.2-C2 does not modify the simulation script. v0.7.2-C2 does not modify the C readiness script.
v0.7.2-C2 does not modify the C test.

## 4. Why Current-State Aggregator Needs C

current-state aggregator is the source of truth for current health。C 落地後，aggregator 應：
- 以 subprocess 重跑 **C test** 作為 hard green gate（**不**重跑 C readiness，避免循環依賴）；
- 確認 C artifacts 存在（含 C readiness）；
- 加入 simulation 正向斷言（profile / sample 覆蓋 / 固定安全旗標）與邊界（未被 main/queue_store/
  worker/result_sink 接入）。
otherwise aggregator 無法反映「C 已成為 current master 健康的一部分」。
current-state aggregator validates C simulation through C test plus inline positive assertions.

## 5. C Is Additive

v0.7.2-C is additive and does not supersede v0.7.2-B. v0.7.2-C is additive and does not supersede
v0.7.2-B2. C 建立在 B helper 之上（只呼叫 `evaluate_auto_approval`），不取代任何既有版本，
故不進 expected-stale。

## 6. C Does Not Supersede B

C 只是 B helper 的展示層。B helper readiness 與 B test 仍是 current green gate，未被 C 取代或 stale。

## 7. C Does Not Supersede B2

B2 的 expected-stale policy 與 doc 不被本版修改。B2 readiness 仍 green。C2 不改 B2 任何檔。

## 8. New Green Gates

aggregator GREEN_READINESS 新增 **一個** hard gate（subprocess returncode==0）：

- `scripts/test_auto_approval_local_only_simulation_v0_7_2_c.py`（C test）

v0.7.2-C test is a current-state green gate.
v0.7.2-C readiness remains a standalone readiness check and required artifact.
current-state aggregator does not subprocess-call C readiness, to avoid circular dependency.

原因：C readiness（`check_hermes_openclaw_auto_approval_local_only_simulation_v0_7_2_c.py`）本身會以
subprocess 回呼 current-state aggregator 驗證 current health；若 aggregator 又把 C readiness 當
subprocess gate，兩者互呼會形成循環依賴。故 aggregator 不重跑 C readiness，改以 C test gate +
[4c] inline 正向斷言驗證 simulation 健康；C readiness 仍可單獨執行（standalone）且列為 required artifact。

## 9. Required C Artifacts

aggregator 新增 C artifacts 存在性檢查：

- `docs/HERMES_OPENCLAW_AUTO_APPROVAL_LOCAL_ONLY_SIMULATION_V0_7_2_C.md`
- `scripts/simulate_auto_approval_policy_v0_7_2_c.py`
- `scripts/test_auto_approval_local_only_simulation_v0_7_2_c.py`
- `scripts/check_hermes_openclaw_auto_approval_local_only_simulation_v0_7_2_c.py`

## 10. Positive Current-State Assertions

aggregator 新增 simulation 正向斷言：simulation imports evaluate_auto_approval、supports --sample、
supports --json、has safe profile、has default-off profile、includes Level 0 / Level 1 / Level 2 /
Level 3 / edge samples，且實跑 `--json` 驗證每筆 returns can_execute false /
queue_transition_allowed false / observation_only true，決策涵蓋 auto_approved /
needs_owner_approval / prohibited / rejected。

## 11. Simulation Boundary

aggregator 斷言 simulation 不 import app.main / queue_store / worker / result_sink / sqlite3 /
requests / subprocess / google / gspread / oauth，且無 QueueStore / approve / reject / claim_next /
run_openclaw_cli / route / webhook 痕跡。

## 12. QueueStore Boundary

v0.7.2-C2 does not wire QueueStore. aggregator 斷言 simulation 未被 main/queue_store/worker/
result_sink 接入，且不寫 QueueStore、不改 Queue 狀態、不讀真 Queue DB。

## 13. Route Boundary

v0.7.2-C2 does not wire routes. C2 不接任何 route / intake bridge / approve route；simulation 亦無
route / webhook 定義。

## 14. Worker / OpenClaw Boundary

v0.7.2-C2 does not start Worker. v0.7.2-C2 does not call OpenClaw. C2 不啟動 Worker、不呼叫
OpenClaw CLI。

## 15. Hermes Boundary

v0.7.2-C2 does not call Hermes. C2 不呼叫 Hermes、不建立 webhook。

## 16. Google Sheets Boundary

v0.7.2-C2 does not write Google Sheets. C2 不寫 Google Sheets、不改 `GOOGLE_SHEETS_ENABLED`。

## 17. Secrets Boundary

v0.7.2-C2 does not read secrets. C2 不讀、不顯示任何 secret；aggregator / doc / readiness 不含真實
憑證、token 或完整 spreadsheet id。

## 18. Network / Subprocess Boundary

v0.7.2-C2 does not use network. v0.7.2-C2 does not use subprocess.
此 boundary 指 **simulation / 產品層**：simulation 不連網、不開子行程。verification tooling
（readiness 與 current-state aggregator）只為靜態驗證而以 subprocess 重跑 sub-check 與 git diff，
此為既有慣例（B2 / current-state 皆然），不引入任何產品副作用、不連外。

## 19. No Expected-Stale Change

本版**不**改動 EXPECTED_STALE_READINESS。A / B / B2 的 expected-stale policy 保留原樣。
v0.7.2-C 不加入 expected-stale（C 是 additive，非 superseded）。

## 20. No v0.7 Tag

v0.7.2-C2 does not create tag. 本版不建立任何 v0.7 tag、不 push。

## 21. Future v0.7.2-D

收編 C 後，下一步路線為 v0.7.2-D（Intake Annotation；在 intake 階段標註 policy 決策，仍
observation-only、不改狀態、不接 approve route）。本版不進 D。

## 22. Final Recommendation

v0.7.2-C2 updates current-state only. v0.7.2-C2 does not add features. 建議 Owner 檢視
aggregator 更新 + C2 doc + C2 readiness。確認後再決定是否 commit。

本版已**移除 current-state ⇄ C readiness 的循環依賴**：aggregator 不再 subprocess 重跑 C readiness、
亦不再需要任何 re-entrancy guard。剩餘唯一的「未 commit 中間態」紅燈來自既有的 **B-helper
readiness** git-diff allowlist——它偵測到本版（已授權的）aggregator 改動而暫時轉紅，連帶
current-state / H readiness 轉紅；此為 v0.7.2-B2 當初相同的中間態效應，**commit 後 working tree
clean 即恢復全綠**，與循環依賴無關。
