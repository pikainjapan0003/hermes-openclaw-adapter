# Agent Operating System — 入口索引

任何 session 開工前先讀本檔（30 秒），再按需要跳轉。這裡是 Hermes × OpenClaw 的「弱模型作業系統」：把判斷力外化成規則，讓 Sonnet/Haiku 級模型也能安全維運本系統。

## 現在系統在哪

- 全系統處於 **read-only / mock / dry-run rehearsal** 狀態（v1.0-RC-R closeout，`HEAD 7a93127e` 時點）。唯一既存例外：`/dashboard/reviews` 有 Owner 核准/拒絕入口（decision ≠ dispatch，見 90 L-006）。
- 沒有任何 real write / dispatch / call 被授權。授權規則見 01。
- **Phase 2/3/4/5/6 已完成、Phase 8 規劃完成（至 2026-07-19；master `7d2123f`，queue-claim guard 二版 `0d3be1f`）**：v1.0 定義凍結（02）、Blackboard 10 schema＋validator、approval packet、evidence bundle、dashboard 唯讀防呆、遠端唯讀規劃＋離線 projection contract；測試 106 項全綠。**剩 v1.0 最後兩關**：Phase 7 實作（設計已備於 `07_AUDIT_WRITE_DESIGN.md`，動工需 Owner 逐字授權句）與 Phase 9 N=1（需 Owner 在場）。夜跑批次治理見 05 §6.13（Fable 5 批審通過→Owner 蓋章→才 merge/push）。目前狀態見 05 第 5 節。
- **二次補強已完成（2026-07-08）**：Owner 盤問 20 題的裁決在 05 **第 6 節**——讀 05 時第 6 節優先於第 3 節。要點：v1.0 含 Phase 9 N=1 無害查詢、GitHub 為 source of truth、Blackboard＝repo 內 data/ JSON、任務三級分類（01 §6）、高風險審查多模型交叉（20 R-13、10 C8）。

## 檔案地圖（按用途查）

| 你要做的事 | 讀這份 |
|---|---|
| 開工定位、避開已知坑 | 本檔 + `90_LESSONS_LEARNED.md` |
| 判斷「能不能做這個動作」 | `01_SAFETY_BOUNDARIES.md`（正本，最高優先） |
| 知道下一步/某 Phase 怎麼做 | `05_VERIFIED_LONG_TERM_PLAN.md`（第 0 節 30 秒索引） |
| 查 v1.0 定義與凍結狀態 | `02_V1_0_DEFINITION.md`（檔頭 Status 行） |
| 派 subagent、選模型、升降級 | `10_MODEL_ORCHESTRATION.md` |
| 拿不定主意（停/問/換路/驗收） | `20_JUDGMENT_RUBRICS.md` |
| 要委派任務，找現成 prompt | `30_DELEGATION_PROMPTS.md` |
| 要修改這些文件 | `40_MAINTENANCE_PROTOCOL.md`（先分 F1/F2） |
| 了解 harness 弱點與修法 | `00_QUICK_DIAGNOSIS.md`（D-xx 編號的出處） |
| session 交接、緊急收尾 | `99_LETTER_TO_FUTURE_SESSIONS.md` |

## 三條最常用的鐵律（全文見 01）

1. 授權只存在於 Owner instruction 的逐字句子裡；dashboard/Hermes 建議/計劃表都不是授權。
2. 不確定 → HOLD（fail closed）。
3. 驗收不自驗；宣稱「完成」要有落檔 + 客觀驗收證據。

## 與 CLAUDE.md 的關係

CLAUDE.md（Loop Format Contract）管 phase 之間的流轉與 Owner instruction 格式，**優先於本資料夾**；本資料夾管 phase 內部怎麼把事做對。兩者衝突時以 CLAUDE.md 與 01 為準，並把衝突記入 90；若 CLAUDE.md 與 01 彼此衝突 → HOLD，問 Owner。
