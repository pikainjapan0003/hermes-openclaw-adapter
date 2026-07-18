# 02 v1.0 Definition（v1.0 定義文件）

> Status: **DRAFT——未凍結**。依 05 Phase 2 HOLD 條款：Owner 未逐字簽核前，任何人不得宣稱 v1.0 定義已凍結。
> 來源：05 §6.3 候選定義（Owner 2026-07-08 盤問裁決 Q4/Q5/Q8）＋05 第 3 節 Phase 2 規格。起草：Fable 5，2026-07-18。
> 效力邊界：**定義 ≠ 授權**。本文件只凍結 v1.0 的範圍，不解除 01 的任何禁令；每個 Phase 的實作仍需 Owner instruction 逐字授權（01 §2/§4）。

## 1. 定義

```text
v1.0 = Owner-supervised Full-chain Baseline
     = Phase 3–7 全部完成
     + Phase 9 的 N=1：一次無害查詢型 openclaw agent 真實調用成功（零寫入）
```

與 Drive 報告第一輪建議版（v1.0 = MVP Baseline，不含真實調用）的差異：**Phase 9 N=1 併入 v1.0**（Owner Q4 裁決）。理由：「傳話中樞的 v1.0」必須證明真的能傳話。

## 2. 包含（每項附驗收方式）

| # | 項目 | 驗收方式 | 對應 Phase |
|---|---|---|---|
| 1 | 本機 Blackboard 讀寫（schema 驗證） | 9 種 schema pytest 全綠（每 schema ≥1 正例＋2 反例 fixture）＋fresh-context review 確認覆蓋 v1.0-RC-D fixture 全欄位；schema 含 `execution_class`/`produced_by`/`parent_task_id`/`role` 欄（05 §6.10） | 3 |
| 2 | Approval packet 流程 | 對 N=1 查詢動作具體設計（不做通用格式）；packet schema＋產生器測試綠；裁決入口＝既存 `/dashboard/reviews`（不新建）；Owner review 通過 | 4 |
| 3 | Dry-run evidence bundle | 聚焦 N=1 動作的標準化證據包；產生器測試全綠，且反向測試（缺件即 FAIL）證明驗證有效 | 5 |
| 4 | Audit 檔 local write | 首次授權寫入僅限 local dev 檔；hash-chain 欄位落地（`prev_entry_hash`）；Owner 檢視實際 audit 檔內容後簽核 | 7 |
| 5 | Rollback preview | 與 audit 同輪驗收；git 為標準回滾路；preview 不執行任何真實 rollback | 7 |
| 6 | 一次真實全鏈路查詢調用（零寫入） | N=1 無害查詢型 `openclaw agent` 調用；前置＝Phase 3/4/5/7 全部完成＋Owner 在場＋單次 token；全鏈路 audit 記錄完整、schema 驗證全過；Owner 對 N=1 結果簽核 | 9 |

## 3. 不包含（每項註明推遲去向）

| 項目 | 推遲到 |
|---|---|
| 任何真實寫入型執行（首發＝repo 內測試檔一次真實寫入） | **v1.1**（05 §6.8 解鎖階梯；需 v1.0 簽核完成＋新 packet/token） |
| 真實代碼任務（Owner 痛點場景首次真演練） | **v1.2**（需 v1.1 簽核完成＋多審查員驗收） |
| 多 worker 並行／角色化 worker | **v1.2 之後**（05 §6.2；O2 開放問題屆時先解） |
| Connector read/write | **Phase 10，無限期停留規劃**（業務接入時重啟，先跑 §6.11 T1/Q16 重審） |
| Production DB | v1.0 之外，未排程（Blackboard＝repo 內 `data/` JSON，Q13；升 SQLite 僅由 §6.11 T3 觸發重問） |
| Remote API runtime | v1.0 之外（Phase 8 為 docs-only 規劃；v1.0 之後第一優先，Q11/Q12） |
| Dashboard 新控制項 | 不在 v1.0（既存 `/dashboard/reviews` 核准入口除外，90 L-006；首次接上真實 dispatch 前觸發 §6.11 T2 重審） |

## 4. 任務三級分類（Q8，正式定義寫入 01 §6）

```text
AUTO           唯讀/無害         Owner 批計劃後可自動並行（計劃級授權格式未定＝O1；定義前照 01 §2/§4 逐字授權，fail closed）
OWNER_APPROVAL 會寫入/有副作用    逐件送 Owner 批
OWNER_MANUAL   高風險（花錢/不可逆）不進派工佇列；Hermes 只在計劃中標記「這件 Owner 親自做」
```

Schema 欄位名：`execution_class`（Phase 3 落地）。

## 5. Owner 簽核紀錄（05 §6.9 checklist）

簽核前本文件維持 DRAFT；五項全簽才得宣告凍結。

```text
[ ] 1. v1.0 候選定義（§1，即 05 §6.3 全文）逐字接受？（含 Phase 9 併入 v1.0）
[ ] 2. 「包含」六項各自的驗收方式（§2）逐項接受？
[ ] 3. 「不包含」各項的推遲去向（§3）接受？
[ ] 4. 任務三級分類寫入 01 §6（§4）接受？
[ ] 5. 簽核行記錄完成？
```

Owner approved on: ＜待簽＞
Instruction quote: ＜待 Owner 逐字簽核文字＞
