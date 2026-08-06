# Phase 9 N=1 六步閉環：全假演習紀錄

日期：2026-08-07
狀態：**全假件演習；不是 OpenClaw 執行授權，也沒有執行 OpenClaw。**

## Owner 先看這三句

1. 這次把 Phase 9 的六個步驟用合成資料走完，確認每一步能留下可檢查的證據。
2. 「執行」步驟用的是受控假件；真實 OpenClaw 呼叫數是 **0**。
3. 真正執行那天仍要 Owner 在場，重新確認版本、動作、目標與一次性授權；本報告不能代替那次授權。

## 六步演習結果

| 步驟 | 這次做了什麼 | 暫存證據 | 結果 |
|---|---|---|---|
| 1. Evidence bundle | 用既有 builder 產生 N=1 dry-run 證據並重算 hash | `01_evidence_bundle.json` | 通過 |
| 2. Approval packet | 用既有 builder 產生 Owner 審閱資料；舊 schema 的 token 仍為 null | `02_approval_packet.json` | 通過 |
| 3. One-shot attempt | gate 完成全部檢查後只呼叫受控假 executor 一次 | `03_one_shot_execution.json` | 假呼叫 1、真呼叫 0 |
| 4. Audit chain | burn ledger 與 audit event 都寫入 pytest 暫存目錄，並讀回驗鏈 | `04_audit_chain.json` | durable、verified |
| 5. Post verification | 比對前後檔案快照、確認無變動、gate 回到全禁狀態 | `05_post_verification.json` | 通過 |
| 6. Rollback preview | 產生「無副作用，因此無需 rollback」的描述性資料 | `06_rollback_preview.json` | 通過 |

以上六個 JSON 只存在於 pytest 的臨時目錄，測試結束後不會留在 repo。repo 的
`data/audit_dev.jsonl` 沒有被本演習寫入，`data/phase9_burn.jsonl` 也沒有建立。

## 一次性證明

同一個 token 交給第二個全新 gate 再跑時，durable burn ledger 回覆
`TOKEN_ALREADY_BURNED`；第二次沒有再呼叫假 executor。這證明本次演習中的
一次性限制不是只靠記憶體狀態。

## 真正執行日 Owner 要做什麼

1. 親自確認當日唯一動作與唯一目標。
2. 看 gate 顯示的 packet/action digest，確認與凍結資料一致。
3. 在同一場次親自提供逐字授權並保持在線。
4. 看到任何版本漂移、預檢失敗、未知檔案變更或逾時，立即停止；不自動重試。
5. 執行後檢視 audit、前後快照與 rollback 說明，再決定是否簽核 Phase 9。

第一個真實 version probe 與第一個真實 OpenClaw call 都只能在那個 Owner 在場、
另有明確執行授權的 session 發生。本次程式施工與全假演習均未做這兩件事。
