# 夜跑批次 Backlog（常備存貨，批單從這裡取材）

> 治理：05 §6.13。凡標【夜跑可做】＝零寫入、零執行、docs/測試/純函式，可直接排批。
> 凡標【Owner 閘】＝依 05 正本需 Owner 逐字授權或在場，**永不排進夜跑**；夜跑只能做其「設計/審查/準備」半邊。
> 本檔由 Fable 5 維護；批單消耗一項就劃掉並註 NB 編號。執行者不得自行從本檔取材加包。

## A. v1.0 收尾（主線）

| 項 | 性質 | 狀態 |
|---|---|---|
| Phase 7 audit writer 實作＋強模型審＋Owner 檢視 audit 檔簽核 | 【Owner 閘】逐字授權句：`允許寫入 data/audit_dev.jsonl（local dev append-only）` | 設計已備（07），等授權句 |
| Phase 9 N=1 真實調用 | 【Owner 閘】在場＋單次 token | 等 Phase 7 完成後擇日 |

## B. v1.1／v1.2 準備（畢業考後的路，先把圖畫好）

| 項 | 性質 |
|---|---|
| O1 計劃級授權方案裁決 | 【Owner 閘】提案與一頁摘要已備；等 Owner 選案 |
| O2 角色化 worker 方案裁決 | 【Owner 閘】提案、role prompt 草稿與一頁摘要已備；等 Owner 選案 |

## C. 接線與擴張（遠期）

| 項 | 性質 |
|---|---|
| Replit 單向同步實作 | 【Owner 閘】遠端接線未授權 |

## D. 品質與長期健檢（Phase 11，永不枯竭）

| 項 | 性質 |
|---|---|
| 制度檔季度健檢（40 F4 精簡門檻、規則衝突掃描、90 教訓回歸） | 【夜跑可做】週期性重複排批 |
| mock_e2e 舊件與新 contract 的一致性遷移評估 | 【已完成】NB-7 評估；NB-8 包3 依 Fable 5 裁決落為「保留並凍結」，Owner 可翻案 |

## E. 審查發現待修（來自批審 findings，優先消化）

| 項 | 來源 | 性質 |
|---|---|---|
| （目前無 NB-6 遺留 finding）07 設計修正與 production-endpoint guard 均已由 NB-7 完成 | NB-7 | 【已完成】 |

## 已消耗

- NB-1～NB-5：Phase 3/4/5/6/8 規劃、hash-chain、rollback builder、coverage/mypy/fuzz/全鏈 rehearsal（詳 05 §5 與各批 commit）。
- NB-6：A2（07 對抗審查）、A3（preflight 閘門）、B1（v1.1 設計）、B4=O1 提案、B5=O2 提案（含三 role prompt 草稿）、D1 第一輪（legacy 覆蓋 74/72→99/100）、D2（信任掃描器）。
- NB-7：mock_e2e 舊件與新 contract 的一致性遷移評估完成；建議 Option A「保留並凍結」。
- NB-8 包3：Fable 5 於 2026-07-20 裁決採 Option A，落檔於 05 §6.14；Owner 保留翻案權。
- NB-7：v1.2 設計、Blackboard layout/reader、Hermes wiring 設計、Phase 10 研究、Phase 0 唯讀檢查器、07 finding 與 production-endpoint guard 修正。
- NB-8：legacy coverage 收官、信任／drift guard、唯讀板面檢視、mock_e2e 凍結、builder fuzz、O1/O2 一頁摘要與治理健檢第二輪。

## NIGHT-BATCH-11 補貨（2026-07-23）

以下條目只整理本批已發現或仍待裁決的工作，不構成任何實作授權。

### 【夜跑可做】

| 條目 | 來源 | 邊界 |
|---|---|---|
| README volatile baseline 清理 | onboarding O-01 | docs only；移除過期 commit/test 數，不改 phase 裁決 |
| CLAUDE onboarding 導航前置 | onboarding O-02/O-03 | docs only；只加最短權威入口與硬閘摘要，不放寬 §6.13 |
| 05 §5 排序可讀性提案 | onboarding O-04/O-05 | review/design only；不得改狀態事實 |
| jsonschema error redaction 設計 | error audit E-01/E-02 | 先做格式設計與相容性盤點；remote/runtime 接線仍禁止 |
| pyproject/requirements authority 提案 | dependency audit | docs/review only；不得在未授權包改依賴 |
| transitive dependency lock 方案比較 | dependency audit | docs only；比較 lock file／constraints／同步 pyproject |
| cross-reference orphan 清冊複核 | package 8 advisory | docs review；單次出現不等於錯誤，不得機械刪除 |
| `main.py` GET coverage 後續輪替 | package 4 | 只加 GET/display 測試；POST、worker、claim 仍禁止 |
| test layer profile 定期重跑 | package 9 | 測量與報告；四 marker 不代表安全等級放寬 |

### 【Owner 閘】

| 待裁決組 | Owner 需要選擇 | 未裁決前狀態 |
|---|---|---|
| v1.1 audit record | 11 設計稿的三案：擴充 `audit_event`／新增 `v1_1_write_record`／結構化 `event_notes` | 不改 schema、不實作 writer |
| rollback Git binding | 11 設計稿的三案：`write_commit`／`parent`／`target_hash` 與 outcome 的 contract | 不改 schema、不執行 Git rollback |
| `produced_by` policy | 13 設計稿的 enum／pattern／policy-only 三案 | 維持 provenance-only，不視為授權 |
| root `parent_task_id: null` projection | 決定 root 顯示映射或拒絕規則 | 不自行填 placeholder，不直呼 projection builder |
| Phase 7 audit writer | Owner 逐字授權句仍為必要前置 | 禁止建立 writer、`data/` 正式目錄或持久化寫入 |
| Phase 9 N=1 | Owner 同步在場＋另行 token/gate 設計與授權 | preflight 必須維持 BLOCKED |

### 本批已消耗，不再重開

- 05 已從 482 行精簡至 440 行，規則對照表已落檔；後續不得以精簡名義刪除裁決。
- `main.py` GET-only coverage 已達 65%，worker 結構契約已鎖；這不代表 POST 或 worker 執行獲准。
- approval packet/evidence bundle 各六組 golden vectors 已建立。
- schema stdout renderer、Phase 9 blocked preflight、error surface audit、dependency audit、onboarding review 均已完成。
