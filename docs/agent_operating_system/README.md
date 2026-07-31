# Agent Operating System — 入口索引

任何 session 開工前先讀本檔（30 秒），再按需要跳轉。這裡是 Hermes × OpenClaw 的「弱模型作業系統」：把判斷力外化成規則，讓 Sonnet/Haiku 級模型也能安全維運本系統。

## 現在系統在哪

- 全系統處於 **read-only / mock / dry-run rehearsal** 狀態（v1.0-RC-R closeout，`HEAD 7a93127e` 時點）。唯一既存例外：`/dashboard/reviews` 有 Owner 核准/拒絕入口（decision ≠ dispatch，見 90 L-006）。
- 沒有任何 real write / dispatch / call 被授權。授權規則見 01。
- **Phase 2/3/4/5/6 已完成、Phase 8 規劃完成**：v1.0 定義凍結（02）、Blackboard 10 schema＋validator、approval packet、evidence bundle、dashboard 唯讀防呆、遠端唯讀規劃＋離線 projection contract均已落地；全套測試綠（數量見 CI／實跑）。**剩 v1.0 最後兩關**：Phase 7 實作（設計已備於 `07_AUDIT_WRITE_DESIGN.md`，動工需 Owner 逐字授權句）與 Phase 9 N=1（需 Owner 在場）。夜跑批次治理見 05 §6.13（批審通過即合，免逐次蓋章）。目前狀態只以 05 第 5 節為準；本入口不寫易過期的 branch、commit 或測試數。
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

## 治理規則快速路由（定義仍以原檔為準）

這裡只提供第二入口，避免有效規則成為只能靠全文搜尋找到的孤兒；不重述、
不取代原規則：

- 模型與回報：10 的 C3（指定模型）、C4（回報合約）、C7（既有 loop
  關係）。
- harness 診斷：00 的 D-02、D-04、D-05、D-06、D-07、D-08、D-10、
  D-11、D-13、D-14、D-15、D-17、D-18。
- 已知環境／制度坑：90 的 L-002、L-003、L-005。
- 拿不定主意時的 rubrics：20 的 R-01、R-03、R-04、R-05、R-08、
  R-10、R-11、R-12。
- 文件修改流程：40 的 F5；夜跑常設例外仍只看 05 §6.13。
- Owner 裁決速查：05 §6.0（Q1–Q20）、§6.5（tool role map）、
  §6.9（Phase 2 checklist）、§6.12（Phase 3 contract 裁決）、
  §6.14（legacy mock 凍結）。

## 三條最常用的鐵律（全文見 01）

1. 授權只存在於 Owner instruction 的逐字句子裡；dashboard/Hermes 建議/計劃表都不是授權。
2. 不確定 → HOLD（fail closed）。
3. 驗收不自驗；宣稱「完成」要有落檔 + 客觀驗收證據。

## 與 CLAUDE.md 的關係

CLAUDE.md（Loop Format Contract）管 phase 之間的流轉與 Owner instruction 格式，**優先於本資料夾**；本資料夾管 phase 內部怎麼把事做對。兩者衝突時以 CLAUDE.md 與 01 為準，並把衝突記入 90；若 CLAUDE.md 與 01 彼此衝突 → HOLD，問 Owner。
