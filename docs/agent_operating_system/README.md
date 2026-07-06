# Agent Operating System — 入口索引

任何 session 開工前先讀本檔（30 秒），再按需要跳轉。這裡是 Hermes × OpenClaw 的「弱模型作業系統」：把判斷力外化成規則，讓 Sonnet/Haiku 級模型也能安全維運本系統。

## 現在系統在哪

- 全系統處於 **read-only / mock / dry-run rehearsal** 狀態（v1.0-RC-R closeout，`HEAD 7a93127e` 時點）。唯一既存例外：`/dashboard/reviews` 有 Owner 核准/拒絕入口（decision ≠ dispatch，見 90 L-006）。
- 沒有任何 real write / dispatch / call 被授權。授權規則見 01。
- 下一步：`05_VERIFIED_LONG_TERM_PLAN.md` Phase 2（v1.0 Definition Freeze，需 Owner）。目前狀態見 05 第 5 節狀態追蹤表。

## 檔案地圖（按用途查）

| 你要做的事 | 讀這份 |
|---|---|
| 開工定位、避開已知坑 | 本檔 + `90_LESSONS_LEARNED.md` |
| 判斷「能不能做這個動作」 | `01_SAFETY_BOUNDARIES.md`（正本，最高優先） |
| 知道下一步/某 Phase 怎麼做 | `05_VERIFIED_LONG_TERM_PLAN.md`（第 0 節 30 秒索引） |
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
