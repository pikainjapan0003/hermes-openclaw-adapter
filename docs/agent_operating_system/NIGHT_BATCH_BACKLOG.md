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
| pyproject/requirements authority 提案 | dependency audit | docs/review only；不得在未授權包改依賴 |
| transitive dependency lock 方案比較 | dependency audit | docs only；比較 lock file／constraints／同步 pyproject |
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

## NIGHT-BATCH-12 補貨（2026-07-24）

### 【夜跑可做】

| 條目 | 來源 | 邊界 |
|---|---|---|
| fixture inventory 定期複核 | NB-12 包12 | review only；目前 50 檔、零 byte-identical duplicate、零確認 orphan，不得機械刪除 |
| board reader capacity 趨勢重跑 | NB-12 包7 | measurement only；無 CI 門檻，T3 未觸發前不得據此升級介質 |

### 【Owner 閘】

| 待裁決組 | Owner 需要選擇 | 未裁決前狀態 |
|---|---|---|
| Blackboard schema error redaction | `SCHEMA_ERROR_REDACTION_CONTRACT_DESIGN.md` 的 A／B／C（建議 C） | 十 schema leak-marker 基線維持 xfail；validator 不改、錯誤不得接不可信 exposure |
| v1.1 audit record | 11 設計稿三案 | 不改 schema、不實作 writer |
| rollback Git binding | 11 設計稿三案 | 不改 schema、不執行 Git rollback |
| `produced_by` policy | 13 設計稿三案 | 維持 policy-only provenance |
| root `parent_task_id: null` projection | 決定 root 顯示映射或拒絕規則 | 不填 placeholder、不直呼 projection builder |
| Phase 7 audit writer | Owner 逐字授權句 | writer、正式 `data/` 與持久化仍禁止 |
| Phase 9 N=1 | Owner 同步在場＋token/gate 另行裁決 | preflight 維持 BLOCKED |

### 本批已消耗，不再重開

- README volatile baseline、CLAUDE onboarding 前置、05 §5 can/cannot/next
  入口與排序誤讀警告已由包3完成；cross-reference orphan 已由包4降為零。
- Blackboard schema-error 遮罩三案設計與十 schema xfail 基線已由包1/2
  完成；這不是 Owner 裁決，也不是 validator 修正。
- legacy contract 兩模組覆蓋已由 95%/97% 提升至 100%/100%（包6）。
- 500-message reader 容量量測、十 schema renderer 演習、Round 4、
  compaction crosswalk guard、三源 JSON 模式、fixture inventory 均已完成。
- 包5為 HOLD、無 commit、無殘留變更；不得把它列為 coverage 75% 完成。

## NIGHT-BATCH-13 補貨（2026-07-25）

以下為本批後的目前存貨。歷史報告保留原 finding，不代表 finding 仍未處置。

### 【夜跑可做】

| 條目 | 來源 | 邊界 |
|---|---|---|
| fixture conventions 與 inventory 定期交叉複核 | NB-13 包9／Round 5 | review/test only；新增 fixture 仍須另有授權 |
| test layer profile 定期重跑 | NB-13 包11 | measurement only；marker 是組織層，不是安全等級 |
| Phase 11 research 目錄趨勢 | NB-13 包14 | measurement/proposal only；未拍板門檻前不得自動歸檔 |

### Owner 四組選案中心

Owner 可一次回覆四組，例如：
`redaction=C；v1.1 audit=B；rollback=B；produced_by=A`。
字母仍以各提案原檔方案為準；本表不替 Owner 預選。

| 待裁決組 | 可選方案 | 未裁決前狀態 |
|---|---|---|
| Redaction contract | A validator 端／B exposure 端／C 雙層（文件建議 C） | 十 schema xfail 維持；Blackboard 與 projection validator 均不改 |
| v1.1 audit record | A 擴充 `audit_event`／B 新增 `v1_1_write_record`／C 結構化 `event_notes` | 不改 schema、不實作 writer |
| Rollback Git binding | 11 設計稿 A／B／C 三案 | 不改 schema、不執行 Git rollback |
| `produced_by` policy | A enum／B pattern／C policy-only | 維持現行 policy-only provenance |

### 其他專屬硬閘

| 項目 | 未解條件 |
|---|---|
| root `parent_task_id: null` projection | Owner 決定 root 顯示映射或拒絕規則；不得填 placeholder |
| Phase 7 audit writer | 仍需 Owner 逐字授權句；夜跑不得實作 |
| Phase 9 N=1 | 仍需 Phase 7 完成、Owner 同步在場及另行 gate/token 裁決 |

### 本批已消耗，不再重開

- `main.py` 修正版純-helper 包達 69%（原 65%，目標 68%）；禁用的
  command/dispatch/callback helper 與所有 POST 均未觸及。
- E-02 remote projection redaction 專節、05/crosswalk 數字校正、
  onboarding/error-surface resolution metadata 已完成（包2–4）。
- 十 schema xfail 精確 inventory guard、三個 legacy 模組 100% coverage、
  reader concurrency、三源 stdout schema 已完成（包5–8）。
- fixture conventions、Round 5、exactly-one test-layer meta guard、v1.0
  readiness evidence index已完成（包9–12）。
- Round 5 R5-01 的雙 marker finding 已由包11修正並由完整 collection
  機械守護；不得重開為未解 finding。

## NIGHT-BATCH-14 補貨（2026-07-26）

以下 finding 只進存貨，不因列在本檔而取得修正或實作授權。

### 【夜跑可做】

本表八項已由 NIGHT-BATCH-15 包1–6消耗；移入下方已消耗紀錄，
不再列為目前存貨。

### 【Owner 閘】（位置確認，未移入夜跑）

| 項目 | 未裁決前狀態 |
|---|---|
| 四組選案：redaction／v1.1 audit／rollback binding／`produced_by` | `OWNER_DECISION_ONE_PAGER_20260726.md` 裁決欄全空；不得實作任何選案 |
| root `parent_task_id: null` projection | 等 Owner 決定；不得填 placeholder 或直接呼叫現行 builder |
| Phase 7 audit writer | 等逐字授權句；禁止 writer、正式 `data/` 與持久化 |
| Phase 9 N=1 | 等 Phase 7 完成、Owner 同步在場及另行 token/gate 裁決 |
| Replit 單向同步 | remote/runtime 接線未授權；不得把三源 HTTP 可達當 deployed hash 已驗證 |

### 本批已消耗，不再重開

- Round 5 R5-02/R5-03/R5-04 已分別由包2 `e5af141`、包3
  `45e0df3`、包4 `2529883` 校正或補 metadata/checklist；歷史 finding
  保留，不得把它們列回未處置。
- auto policy、remote projection、queue store、queue intake bridge、
  blackboard store 覆蓋已由包5/6補強；rollback preview 唯一剩餘分支為
  exact-profile 前置後邏輯不可達的縱深防禦，不得為 coverage 刪除。
- 包7依硬條款 HOLD、無 commit、無產品修改；不能宣稱 `main.py` 已達 72%。
- dependency authority/lock 方案、test-layer profile、board-reader capacity、
  fixture inventory、季度治理、Round 6、Owner 一頁摘要與 three-source
  Replit unknown schema 演習已完成；提案與 findings 不等於 Owner 裁決。

## NIGHT-BATCH-15 補貨（2026-07-27）

以下條目來自本批的實測與 fresh-context review。列入 backlog 不授權產品、
schema、依賴、runtime、持久化或 Owner-gated 變更。

### 【夜跑可做】

| 條目 | 來源 | 邊界 |
|---|---|---|
| README 移除過期 `HEAD 7a93127e`，並保留 05 §5 為唯一狀態權威 | Onboarding O2-01 | docs only；不得以新 hash 取代舊 hash |
| 05 Phase 3 備註移除「jsonschema/pytest 未入 requirements」過期掛帳 | Onboarding O2-02 | docs only；不改依賴檔或 Phase 完成裁決 |
| README §6.13「批審通過即合」補同句封閉範圍 | Onboarding O2-03 | docs only；只 cross-reference CLAUDE/05，不能擴張常設授權 |
| RED 一頁表 A/B 標籤對回 redaction source design | Round 7 R7-01 | docs only；只修摘要一致性，Owner choice 保持空白 |
| ROOT 提案來源補齊：將 R 方案寫成正式 planning-only 比較稿，或把一頁表降為新提案 | Round 7 R7-02 | docs only；不得把 R 當 Owner 已選，不改 projection schema/builder |
| Quarterly 與 Round 6 加 later-resolution metadata | Round 7 R7-03/R7-04 | docs only；歷史 finding 原文不重寫 |
| 2026-07-26 layer profile 補 package checkpoint 註記 | Round 7 R7-05 | docs only；不把量測數變成 CI 門檻 |
| legacy enum／mock E2E／preview-loader error exposure 修正方案 | Error audit ES2-01/02/03 | 先做 docs/test 設計；產品錯誤格式需另包明文授權，E-01/E-02 xfail 不動 |
| test-layer profile 與 board-reader stress 趨勢重跑 | NB-15 包8/17 | measurement only；不設效能門檻、不以 marker 跳過最終全測 |
| dependency declaration baseline 定期複核 | NB-15 包11 | tests/report only；Owner 未裁決 authority 前不得改三份依賴宣告 |

上述十項足以供下一批取材，夜跑存貨未枯竭。執行者仍不得自行從本表加包。

### 【Owner 閘】（五組選案維持未裁決）

| 選案 | 目前狀態 | 未裁決前行為 |
|---|---|---|
| RED — schema error redaction | **空白**；R7-01 指出一頁表 A/B 對調，先修文件再請 Owner 選 | E-01/E-02 xfail 維持；不得 export raw validator error |
| AUD — v1.1 audit record | **空白**；A/B/C 提案與 B 建議仍只是設計 | 不改 schema、不實作 writer |
| RB — rollback Git binding | **空白**；A/B/C 提案與 B 建議仍只是設計 | 不改 schema、不執行或猜測 Git rollback |
| PB — Hermes `produced_by` | **空白**；A/B/C 提案與 A 建議仍只是設計 | schema 維持非空字串；future adapter 另行 fail closed |
| ROOT — `parent_task_id: null` projection | **空白**；R7-02 指出 R 建議缺完整來源提案 | root projection 維持 HOLD，不填 placeholder |

Phase 7 audit writer、Phase 9 Owner-present N=1、v1.1/v1.2 instruction 與
Replit/runtime 接線仍是各自獨立硬閘，不因上表或夜跑常設流程解鎖。

### 本批已消耗，不再重開

- 包1–3：three-source schema 已入 INDEX/path guard；fixture conventions 已與
  實際機械範圍對齊；三源事實/UNKNOWN/verdict/exit-code 語義文件已完成。
- 包4：季度 GQ-01～GQ-05 已修正；後續只補 resolution metadata，不重做修正。
- 包5–6：`main.py` GET/helper 安全面達 71%；納管 coverage 缺口已逐條分類，
  defensive/unreachable 分支保留。
- 包7–9：六 contract mutation 240 案、大板面 2,000 檔量測、1,000 筆 hash
  長鏈驗證均完成。
- 包10–13：error surface Round 2、dependency sync baseline、15-schema renderer
  全量演習、Phase 9 all-of preflight 反向測試完成。
- 包14–18：v1.0 readiness 二版、onboarding/治理 review、test-layer 新檔 guard、
  1,206-outcome profile、golden vector 獨立 hash 驗證完成。
