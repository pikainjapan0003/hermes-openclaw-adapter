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
| legacy enum／mock E2E／preview-loader error exposure 修正方案 | Error audit ES2-01/02/03 | 先做 docs/test 設計；產品錯誤格式需另包明文授權，E-01/E-02 xfail 不動 |
| test-layer profile 與 board-reader stress 趨勢重跑 | NB-15 包8/17 | measurement only；不設效能門檻、不以 marker 跳過最終全測 |
| dependency declaration baseline 定期複核 | NB-15 包11 | tests/report only；Owner 未裁決 authority 前不得改三份依賴宣告 |

執行者仍不得自行從本表加包。

### 【Owner 閘】（四組正式選案＋一個 ROOT direction gate，均未裁決）

| 選案 | 目前狀態 | 未裁決前行為 |
|---|---|---|
| RED — schema error redaction | **空白**；一頁表已校正為 A=validator、B=exposure、C=double-layer（建議 C） | E-01/E-02 xfail 維持；不得 export raw validator error |
| AUD — v1.1 audit record | **空白**；A/B/C 提案與 B 建議仍只是設計 | 不改 schema、不實作 writer |
| RB — rollback Git binding | **空白**；A/B/C 提案與 B 建議仍只是設計 | 不改 schema、不執行或猜測 Git rollback |
| PB — Hermes `produced_by` | **空白**；A/B/C 提案與 A 建議仍只是設計 | schema 維持非空字串；future adapter 另行 fail closed |
| ROOT — `parent_task_id: null` projection | **空白**；一頁表已校正為「尚無正式標號方案」，suggested direction 不是選項 | root projection 維持 HOLD，不填 placeholder；ROOT 不可回選案字母 |

`OWNER_DECISION_ONE_PAGER_20260726.md` 已於 NIGHT-BATCH-16 包1校正，現在可
安全閱讀與回覆四組已有正式來源選項的選案：RED／AUD／RB／PB。ROOT
不是第五個選案，而是一個尚無正式標號方案的空白 direction gate；在正式比較稿
完成前只能維持空白。任何回覆都
只是設計裁決，不是 schema、writer、runtime、execution 或 dispatch 授權。

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
- NIGHT-BATCH-16 包1–3：Owner 一頁表 RED 標籤與 ROOT 身分已校正並由
  consistency guard 鎖定；Quarterly、Round 6 與 2026-07-26 profile 的
  resolution/checkpoint metadata 已補齊。Round 7 歷史原文尚待補 disposition。

## NIGHT-BATCH-16 補貨（2026-07-28）

以下條目吸收本批實測、Round 8、research 治理提案與 delegation template
複核。列入本檔不授權執行者自行開包或擴大修正範圍。

### 【夜跑可做】

| 條目 | 來源 | 邊界 |
|---|---|---|
| Round 7 加 later-resolution metadata，記錄 R7-01～R7-05 已由 NB-16 包1/3處置 | Round 8 R8-02 | 【已完成】NB-17 包2；歷史 finding 原文未重寫，Owner 選案仍空白 |
| README/05 onboarding 三項過期文字校正 | Onboarding O2-01/02/03 | docs only；不得用新 HEAD 取代舊 HEAD；§6.13 封閉範圍不得放寬 |
| 非 contract 唯讀工具 error-surface 遮罩設計 | ES3-01～ES3-04 | 先做 docs/tests；現有四個 xfail 維持，未有明文產品包不得改 script output contract |
| delegation templates 加 current routing/night-batch overlays | TREV-01/03 | docs only；只同步 05 §6.13 與 10 C8，不新增授權或自動派工 |
| T-07 補 R-13 雙模型 fresh-context 硬閘 | TREV-02 | docs only；不得把單模型 review 升格為高風險簽核 |
| T-04/T-08/T-09/T-10 capability 與 Replit UNKNOWN 語義更新 | TREV-04/05 | docs only；不得建立 remote 接線、登入、deploy 或 deployed-hash 推測 |
| board-wide `schema_version` 一致性設計評估 | NB-16 包11 | docs/tests only；現況為逐筆保留版本標記且可混版，不改既有 schema/reader |
| `main.py` GET-only coverage 後續僅在新增安全表面時重估 | NB-16 包4 HOLD／包5 | 【已完成】NB-17 包1改為 raw 69.507% 回歸 floor；POST/control/execution/callback 永不為 coverage 觸及 |
| 唯讀 script coverage 輪替與 renderer union 顯示評估 | NB-16 包10 | tests/docs only；不為 coverage 改工具行為 |
| board-reader symlink 惡意路徑在可建立 symlink 的 WSL 環境重跑 | NB-16 包7 | test-only；Windows 無權限 skip 不算通過該場景，不得建立 repo 正式 board |

### 【Owner 閘】

| 待裁決組 | 目前狀態 | 未裁決前行為 |
|---|---|---|
| RED／AUD／RB／PB 四組正式選案＋ROOT direction gate | **全部空白**；校正後一頁表可安全回覆四組正式選案，ROOT 無正式選項 | 不改 schema、validator、writer、projection 或 runtime；ROOT 保持 HOLD |
| `research/` 目錄治理 | `RESEARCH_DIR_GOVERNANCE.md` A/B/C 三案（建議 B），Owner 欄空白 | 不建 archive、不搬檔、不改名、不壓縮、不刪檔 |
| Phase 7 audit writer | 實作包規格草案已備，但仍只屬 PLANNING ONLY | 仍需 Owner 在實作 turn 給逐字授權句；不得建立 writer/正式 `data/` |
| Phase 9 N=1 | 12-condition truth table 與 preflight 仍 fail closed | 等 Phase 7 完成、Owner 同步在場及另行 token/gate 裁決 |

### 本批已消耗，不再重開

- 包1–3、16：一頁表校正、機械 guard、Round 6/Quarterly/profile metadata 與
  Round 8 review 完成；Round 8 R8-01 已由本 backlog 同步處置。
- 包4 HOLD：安全 GET/display 表面不足以把 `main.py` 提升至 72%，零 edit、
  零 commit；不得以 coverage 名義觸及 POST/control/execution/callback。
- 包5–13：納管 coverage residual 分類、120 案 cross-message mutation、board
  惡意路徑、hash 極端輸入、唯讀 script error/coverage、版本演化、全鏈 v4、
  12-condition truth table 均已完成。Defensive/unreachable 分支不得為數字刪除。
- 包14–15：v1.0 readiness 三版與 Phase 7 implementation package 草案已備；
  引用逐字授權句不等於取得該授權。
- 包17–18：research 目錄治理三案與 T-01～T-12 現況複核已完成；兩者皆為
  planning/review，未實際歸檔、搬檔、刪檔或修改 delegation templates。

## NIGHT-BATCH-17 補貨（2026-07-29）

本節吸收 NIGHT-BATCH-17 的 HOLD、error-surface／governance／core-doc
findings 與效能量測。列入本檔只代表可供未來 Fable 5 派工取材；執行者
不得自行加包。已完成的分析、測試與報告移到本節「已消耗」，不得拿同一
工作再次交差。

### 【夜跑可做】

| 條目 | 來源 | 邊界 |
|---|---|---|

| NIGHT-BATCH-18 refill (2026-08-01) | Packages 1–22 completed in the section below; Round-10 findings remain review-only | 22 package commits plus mechanical corrections; no Owner gate is opened |
| board reader hardlink 目錄邊界修正設計＋產品小修＋回歸測試 | NB-17 包7 HOLD | 先把板內 hardlink 指向板外有效 fixture 的現行接受行為定為 closed rule；不得建立正式 board/data 目錄，不得藉測試讀任意板外 payload |
| test helper／fixture loader pytest report redaction 設計 | ES4-01/ES4-02 | 先做 docs/test contract；現有 14 個 E-01/E-02/ES3 xfail 精確基線不增不減，禁止把 raw CI report 接 remote/dashboard |
| Round 9 later-status 修補 | R9-01/R9-02 | 只加 health checkpoint metadata，並把 backlog 的「五組選案」改成「四組正式選案＋一個 ROOT direction gate」；歷史 finding 原文不改 |
| 00 current-workflow checkpoint | `CORE_DOCS_REVIEW_00_01.md` finding 1 | docs only；保留 2026-07-07 歷史事實，另標 current Codex 五級路由、immutable night package 與 Fable 5 批審流程 |
| 00 Phase 9 token 措辭收斂 | `CORE_DOCS_REVIEW_00_01.md` finding 2 | docs only；只能標明舊 env-token 句未拍板／不得實作，不得替 Owner 設計或解鎖 token |
| 00 active-checkout 可攜命令修訂 | `CORE_DOCS_REVIEW_00_01.md` finding 3 | docs only；先 resolve Owner 指定 checkout，再給 Windows/WSL 分支示例；不得自行同步、push 或猜 authoritative clone |
| 00 capability/model example 更新 | `CORE_DOCS_REVIEW_00_01.md` finding 4 | docs only；以 available approved capability 與 10 C8 五級路由 cross-reference 取代固定 WebSearch/Haiku/Sonnet 名稱 |
| coverage floor 執行分層提案 | `TEST_PERFORMANCE_20260729.md` P1 | tests/settings proposal；floor 仍是必跑 gate，不降 raw 69.507%、不觸及 POST/control/execution/callback |
| dependency AST inventory session-scope 評估 | `TEST_PERFORMANCE_20260729.md` P2 | tests only；同平台 before/after，assertion/baseline 零改動，先證明 collection scope 不造成 stale inventory |
| test layers 平行 CI 可行性審查 | `TEST_PERFORMANCE_20260729.md` P3/P4 | docs/tests only；不得加未宣告 dependency、不得縮 stress/capacity workload、governance/Git/global collection 先排除 |
| delegation template proposal fresh review | `DELEGATION_TEMPLATE_REVISION_PROPOSAL.md` | review only；若後續明文包核准修改 30，必須保持 §6.13/C8/R-13 邊界且不得新增自動派工權 |
| fixture SHA-256 inventory 定期更新規則 | NB-17 包19 | docs/test convention；fixture 新增/修改需同包說明 hash table 變更，不能用自動接受新 digest 掩蓋未審 fixture |

以上存貨足以拆成下一個不少於十包的夜跑批次；不需要也不得挪用下列
Owner gates 充數。

### 【Owner 閘】（全部維持未裁決）

| 待裁決組 | 目前狀態 | 未裁決前行為 |
|---|---|---|
| RED／AUD／RB／PB 四組正式選案 | **全部空白**；一頁表已校正、guard 已建，可安全回覆 | 不改 schema、validator、writer、projection 或 runtime |
| ROOT direction gate | **空白**；尚無正式標號方案，不可回選案字母 | root projection 維持 HOLD，不填 placeholder |
| `research/` 目錄治理 | A/B/C 三案與二版 SOP 已備，Owner 欄空白 | 不建 archive、不搬檔、不刪檔、不壓縮 |
| 01 §2／§4.5 夜跑例外 cross-reference | `CORE_DOCS_REVIEW_00_01.md` finding 5；01 屬 F2 | 未有 Owner 明示 F2 文件包前不動 01；既有 §6.13 例外不擴張 |
| Phase 7 audit writer | 實作包草案與 readiness 路徑已備 | 仍需 Owner 在實作 turn 給逐字授權句；不得建立 writer、正式 `data/` 或持久化 |
| Phase 9 N=1 | 12-condition preflight 仍 fail closed | 等 Phase 7 完成、Owner 同步在場及另行 token/gate 裁決 |

### 本批已消耗，不再重開

- 包1：`main.py` raw coverage 回歸 floor 已建；GET-only 安全面不再追高。
- 包2：Round 7/8 later-disposition metadata 已補。
- 包3–5：Owner choice preflight、research 治理二版 SOP、delegation template
  修訂提案已備；沒有任何 Owner 欄被填、30 檔未改。
- 包6、8、10、11：時間/序 mutation、builder 極端合法值、three-source
  schema 雙向鎖、12 步負向全鏈已完成。
- 包7：HOLD；hardlink 板外讀取缺口已列上方，未以弱測試交差。
- 包9：四支唯讀 script 覆蓋第二輪已完成。
- 包12–14：preflight catalog、AUD/RB/PB impact analysis 已完成；只屬分析。
- 包15–18：error surface Round 4、governance Round 9、00/01 review 與
  Windows 效能量測已完成；findings 已轉上方存貨。
- 包19：50-file fixture SHA-256 closed inventory 已建。

## NIGHT-BATCH-18 backlog refill — 2026-08-01 (Round 8)

This round records the completed NB18 packages and remaining work that may be scheduled without reopening an Owner gate. It is bookkeeping only; it does not authorize implementation, persistence, execution, dispatch, runtime, remote, or schema changes.

### Completed in NIGHT-BATCH-18

Packages 1–22 are consumed; the result/commit index is preserved in `research/NIGHT_BATCH_BACKLOG_COMPACTION_CROSSWALK_20260804.md` (NB-18 table).

### Follow-up candidates after NIGHT-BATCH-18

- Governance Round 10 findings R10-01 through R10-04 remain review findings; repair work requires a separately scoped package.
- Any future package must preserve the no-persistence, no-execution, no-runtime, no-remote, and Owner-gate boundaries stated below.

### Owner-gated items (not night-run authorization)

AUD (v1.1 audit record), RB (rollback-to-Git binding), PB (produced_by policy), and ROOT projection decisions remain blank pending Owner choice. Phase 7 still requires the exact Owner instruction `允許寫入 data/audit_dev.jsonl（local dev append-only）`; Phase 9 still requires Owner presence. This section does not grant either gate.

> **Later-status metadata (2026-08-03; historical text above unchanged):**
> Owner subsequently gave that exact Phase 7 instruction and signed off Phase
> 7 (05 §5/§6.15). This later fact grants neither Phase 9 audit writing nor
> Phase 9 execution; those remain separately gated.

## NIGHT-BATCH-19 backlog refill — 2026-08-02 (Round 9)

This section supersedes only the current-status interpretation of older
backlog rows; it does not rewrite their historical record and grants no new
authority. NIGHT-BATCH-17 and NIGHT-BATCH-18 are already merged in the
NIGHT-BATCH-19 base (`10fd5a2`). The issued package text still called their
merge the upstream blocker, but recording that as current would be false and
would conflict with the authorized checkout. The current upstream v1.0
blockers remain the Phase 7 exact instruction and Phase 9 Owner presence.

### 【夜跑可做】current stock

| Item | Source | Boundary |
|---|---|---|
| 【已裁決】Board-root symlink contract | NB-19 package 6 HOLD → Fable 5 C, 2026-08-02 | Root is the caller-selected trust anchor; reject board-entry symlinks and enforce the F7 realpath invariant |
| 【已裁決】Replit response-body contract | NB-19 package 9 HOLD → Fable 5 A, 2026-08-02 | Reachability-only; response body and deployed revision are not read or claimed |
| 【已裁決】Schema renderer `oneOf` fidelity | NB-19 package 11 HOLD → Fable 5 A, 2026-08-02 | Fix the stdout-only renderer and add exhaustive tests; no generated-file persistence or schema changes |
| Repair NB-18 correction-commit traceability and add F7/L-009 point-of-use links | R11-01/R11-02 | Docs only; preserve historical commit content and all gates |
| Add later-status metadata to the dated 2026-08-01 health snapshot | R11-03 | Docs only; do not rewrite point-in-time measurements |
| Repair 20 R-05/R-11 and nightly cross-references | `CORE_DOCS_REVIEW_20.md` findings 01–06 | Dedicated rubric docs package; preserve authorization precedence and §6.13 limits |
| Review 00 D-03/D-08/D-10/D-13/D-14/D-17 proposals | `CORE_DOCS_REVIEW_00_ROUND2.md` findings 01–04 | Safety-semantics review only; no direct edit until the package explicitly authorizes it |
| Re-run research stdout redaction baseline | ESR5-03 | Tests/report only; existing 14 xfails must not silently grow or disappear |

### 【Owner 閘】all choices remain blank

| Gate | Current state | Until a future Owner decision |
|---|---|---|
| RED schema-error redaction | **Blank** | Existing xfail contract remains; validator/exposure unchanged |
| AUD v1.1 audit record | **Blank** | No schema extension and no writer |
| RB rollback Git binding | **Blank** | No Git rollback execution |
| PB `produced_by` policy | **Blank** | Provenance remains non-authorizing |
| ROOT projection direction | **Blank; no lettered options** | No placeholder and no direct root projection |
| Research-directory governance | **Blank** | No archive directory, move, rename, compression, or deletion |
| Phase 7 audit writer | Exact active instruction still absent | No writer, formal `data/`, or persistent append |
| Phase 9 N=1 | Owner presence and prior Phase 7 closeout absent | Token remains null; preflight stays blocked |

### NIGHT-BATCH-19 consumed through package 22

Packages 1–22 (including HOLD evidence for 6/9/11 and the package-21 correction) are consumed; the exact result/commit index is preserved in `research/NIGHT_BATCH_BACKLOG_COMPACTION_CROSSWALK_20260804.md` (NB-19 table).

Older NIGHT-BATCH-17 stock for hardlinks, active-checkout portability,
coverage-floor layering, test-layer markers, and fixture hash portability is
consumed by NIGHT-BATCH-18/19 and must not be reopened under the old wording.
The Owner choices above intentionally remain blank.

> **Later-status metadata (2026-08-03; historical rows above unchanged):**
> Owner subsequently gave `允許寫入 data/audit_dev.jsonl（local dev
> append-only）` and signed off Phase 7 (05 §5/§6.15). This update does not
> authorize a Phase 9 audit ledger or any execution.

## NIGHT-BATCH-21 backlog refill — 2026-08-04 (Round 11)

NIGHT-BATCH-20 packages 1–22, including HOLD evidence for 8/10, are consumed
on accepted master `7cd2d98`. NIGHT-BATCH-21 packages 0–22 are allocated to the
current batch and therefore are not future stock; their final done/HOLD status
belongs in the batch report. This inventory grants no merge, write, execution,
Phase 7, Phase 9, or Owner-option authority.

### Consumed or resolved in NIGHT-BATCH-21

- Round-12 traceability, F7-reference and dated-health fixes: package 6.
- Schema-version and real cross-builder relationship proposals: packages 1–2;
  their Owner decision fields remain blank.
- Portable metrics timeout, coverage residual, nested evidence mutations,
  realpath fuzz, mirror/error reviews and artifact inventory: packages 3, 7–9,
  11–12 and 18–19.
- L-012, F8, readiness seven and Phase-7 spec v4: packages 14–17.
- Package 5 and package 10 remain HOLD; no replacement work was substituted.

### Next night-run stock

| Item | Source | Boundary |
|---|---|---|
| Broaden dispatch precheck beyond field names to schema keywords and behavior preconditions | R13-01/R13-02 | F8 design/review first; do not reopen HOLD packages with invented evidence |
| Correct renderer composition brief from the actual existing `allOf` contract | NB-21 package 5 HOLD | Fresh schema dump first; proposal/tests only unless separately authorized |
| Design explicit detached-HEAD and shallow-clone reporting semantics | NB-21 package 10 HOLD | Do not fake fail-closed evidence with monkeypatch-only tests |
| Redact artifact-inventory assertion paths/raw bytes | R13-05 / ESR7-02 | Local test-tool surface only; keep the 14-xfail product baseline unchanged |
| Profile aggregate fast-path cost by file | package 19, fast `304.26s` | Performance proposal first; do not hide coverage by bulk marker changes |
| Refresh stale current-document status without rewriting dated reports | R13-04 | Backlog bookkeeping only; preserve historical evidence |
| Review F8 effectiveness against the next dispatch brief | L-012 acceptance | Review/report only; zero same-shape HOLD is the target |
| Re-run governance and error-surface audits after the above dispositions | Round 13 | Findings do not self-authorize fixes |
| Continue Phase-11 health and test-growth measurement | package 22 handoff | Report only; recomputable numbers required |

The bounded stock above is sufficient for another night batch without
inventing persistence or execution work.

### Owner gates remain blank

| Gate | State |
|---|---|
| AUD — v1.1 audit record | **Blank** |
| RB — rollback Git binding | **Blank** |
| PB — `produced_by` policy | **Blank** |
| ROOT — projection direction | **Blank; no placeholder option selected** |
| Research-directory governance | **Blank; no archive/move/delete authority** |
| Phase 7 audit writer | Exact active Owner instruction still absent |
| Phase 9 N=1 | Owner presence and Phase 7 closeout still absent |

> **Later-status metadata (2026-08-03; historical rows above unchanged):**
> The exact Phase 7 instruction was subsequently given and Phase 7 was signed
> off (05 §5/§6.15). Phase 9 audit writing and execution still require their
> own authorization and are not unlocked by this note.

## NIGHT-BATCH-22 backlog refill - 2026-08-05 (Round 12)

This section records the bounded work completed on the NIGHT-BATCH-22 branch
through package 19. It is bookkeeping only. The branch is not an accepted
phase-state change until the normal independent review and merge; this section
does not grant merge, persistence, execution, dispatch, runtime, remote, or
Owner-gate authority.

### Consumed in NIGHT-BATCH-22 (packages 1-19)

- F8 was broadened to require evidence for field existence, schema-keyword
  presence/absence, and behavior or precondition claims. Missing evidence is a
  HOLD; it is never filled with an invented field or behavior.
- L-013 and the corrected renderer brief are recorded. The schema renderer now
  displays conditional `if`/`then`/`else` rules without implying that the
  display is a runtime authorization.
- Three-source tests cover the observable non-git and unreachable-remote
  cases. Detached-HEAD and shallow-clone semantics remain an explicit design
  gap because the current tool/schema do not expose those states.
- Inventory digests, conditional projection mutation tests, second-round
  realpath fuzzing, mirror edge tests, error-surface Round 8, and governance
  Round 14 are recorded as tests/reviews only. No product writer or runtime
  path was added.
- The performance-claim provenance rule now requires an environment, command,
  commit, and isolation note for timing numbers. The current report records
  `2268 passed, 1 skipped, 21 deselected, 14 xfailed` for fast and
  `2289 passed, 1 skipped, 14 xfailed` for complete, with both profiles
  reconciled.
- Legacy coverage rotation and the conditional full-chain rehearsal remain
  test-only. The readiness v8 and Phase 7 package v5 documents preserve the
  exact Owner gate and all planning-only warnings.

### Findings and bounded next stock

| Item | Source | Boundary |
|---|---|---|
| Recheck every future package against F8's three evidence classes | NB-22 package 1 / L-012 | Review/precheck only; a precheck cannot authorize the package or invent missing contract evidence |
| Decide detached-HEAD and shallow-clone reporting fields | NB-22 three-source partial guard | Owner/design proposal only until the tool and schema contract are changed by an authorized package |
| Keep renderer conditional documentation synchronized with schema keywords | NB-22 packages 3-5 | Read-only renderer/tests; no generated-file persistence or schema edits |
| Preserve four-state mirror classification and human-review warning | NB-22 package 11 | Read-only tool/tests; never overwrite either copy automatically |
| Continue the next coverage rotation without deleting defensive branches | NB-22 package 15 | Tests only; keep the three excluded modules and their exclusion rationale |
| Repeat full-chain conditional rehearsal after any contract decision | NB-22 package 16 | In-memory tests only; no writer, queue, dispatch, or runtime |
| Maintain timing provenance and fast/complete arithmetic | NB-22 package 19 | Reports/markers only; no bulk hiding of tests |
| Run the research-governance v5 review and the Phase 11 health report | NB-22 packages 21-22 | Docs/report only; numbers must be recomputable from recorded commands |

### Owner gates remain unchanged

| Gate | State | Boundary |
|---|---|---|
| AUD / v1.1 audit record | **Blank** | No schema extension and no audit writer |
| RB / rollback Git binding | **Blank** | No Git rollback execution |
| PB / `produced_by` policy | **Blank** | Provenance remains non-authorizing |
| ROOT / root projection direction | **Blank; no placeholder option selected** | No direct root projection |
| Research-directory governance | **Blank** | No archive, move, rename, compression, or deletion |
| Phase 7 audit writer | Exact active Owner instruction still absent | No writer, formal `data/`, or persistent append |
| Phase 9 N=1 | Owner presence and Phase 7 closeout still absent | Token remains null; preflight stays blocked |

> **Later-status metadata (2026-08-03; historical rows above unchanged):**
> Owner subsequently supplied the exact Phase 7 instruction and signed off
> Phase 7 (05 §5/§6.15). Phase 9 audit writing and execution remain separate
> Owner gates; this metadata is not authorization.

## NIGHT-BATCH-26 補貨 — 2026-08-05（雙審 findings 登記）

NB-26（真實 `FileBurnLedger` ＋協調鎖必填＋鎖失敗證據收尾）已於 `d1732c0`
合併並 push。雙審結論：Fable 5 = conditional pass、Opus 5 = PASS，**零阻擋
finding**。兩人獨立裁定 `LOCK_EX|LOCK_NB` / `LK_NBLCK` ＋輪詢為**接受**
（同一 OS 互斥語意，且比無界阻塞更 fail-closed）。以下為兩份審查提出、
**本批不修**的存貨；登記於此不構成任何實作、寫入或執行授權。

### 【夜跑可做】

| 條目 | 來源 | 邊界 |
|---|---|---|
| `FileBurnLedger` 共用實例的 check-then-act：`_active_handle` 防重入檢查未受同步保護，同行程第二呼叫者會提前拋 `BurnLedgerError` 而跳過 timeout 輪詢，導致回報 `BURN_WRITE_FAILED` 而非 `TOKEN_ALREADY_BURNED` | Fable 5 Finding 1（150 輪實測：executor 恆為 1、ledger 恆 1 筆，**安全不變式未破**，5/150 輪錯誤碼誤導） | 二擇一並附測試：為該屬性加 `threading.Lock`，或在 docstring/型別層明文禁止跨呼叫者共用實例。**不得**放寬任何 fail-closed 條件 |
| `_find_in_flight_denial` 缺相關性檢查：會冒領例外鏈上任何 `GateDenied`；該分支未呼叫 `_closed_denial()`，gate 可能停在 `BURNING`、`freeze.frozen=False` | Opus 5 P2-1（出貨的 `FileBurnLedger` 未 import `GateDenied`，實務上不可觸發；即便觸發，第二次 `run()` 仍得 `REHEARSAL_FROZEN`、executor 恆 0） | masked 分支補一次 `_closed_denial()`，或限定只認本次 `run()` 產生的 denial；附回歸測試 |
| `test_noop_lock_control_demonstrates_double_execution` 在原生 Windows/NTFS flaky | Fable 5 Finding 2（連跑 4 次 = PASS/FAIL/FAIL/PASS；`line_count==2` 斷言不可移植——無鎖並發 append 在 NTFS 上會**靜默吃掉**一次寫入而非乾淨產生兩筆） | 評估平台特定斷言或重試；**不得**因此弱化保護版測試。此現象反而強化真鎖的必要性，須在測試註解中記明 |
| 對照組改為只覆寫 `exclusive_lock` 的 `FileBurnLedger` 子類 | Opus 5 P3-1（現行 `UnsafeNoOpLedger` 是另寫類別＋額外 barrier，證明「無鎖會雙跑」但未直接證明「正牌那把鎖就是擋住的」；複審自建真對照 10/10 重現，結論成立） | tests only；保留原測試或取代皆可，須維持證明力 |
| 補永久回歸測試：同行程雙 gate 共用 ledger、雙獨立 ledger 實例指同一檔、`_find_in_flight_denial` 邊界（環路／長鏈／payload 不外洩） | Fable 5 J-3 ／ Opus 5 第三節 7–8 | 兩份審查的臨時 probe 均未提交，這些安全性質目前**無任何永久測試**守護 |
| `pyproject.toml [tool.mypy].files` 併入 `app/phase9_*.py` | 兩審皆提（Fable 5 B 節／Opus 5 P3-2） | 現行 `python -m mypy` 的「6 files 全綠」不涵蓋 Phase 9，易被誤讀為已驗證 |
| `_read_physical_records` 持鎖分支的 `OSError` 未轉 `BurnLedgerError` | Opus 5 P3-4 | 仍 fail-closed，僅型別不一致 |
| 讀取失敗（既有 ledger 損毀）被回報成 `BURN_WRITE_FAILED` | Opus 5 P3-3 | 語意誤導；實際是重放屏障損毀。仍 fail-closed、executor＝0 |
| `phase9_burn_ledger.py:50-51` docstring 措辭：宣稱與 `audit_writer_local.py` 同鎖策略，實際後者為阻塞型 | Fable 5 finding 5 | 註解修正；不影響安全 |
| Windows `msvcrt` 分支無 CI 覆蓋 | Opus 5 P3-5 | 兩審的 Windows 證據皆為手動、不具持續性 |
| 本檔 NB-18/19/21/22 節仍載「Phase 7 exact Owner instruction still absent」，與 2026-08-03 Owner 已給授權句的事實不符 | 本次登記時發現 | docs only；只加 later-status metadata，**不得**改寫歷史章節原文 |

### 【Owner 閘】（維持未裁決）

| 閘 | 狀態 |
|---|---|
| **Phase 9 稽核寫入授權**（B-C：作廢紀錄寫入稽核鏈） | **未請求、未取得**。與 2026-08-03 的 Phase 7 授權句是兩回事，**不得沿用**。缺此紀錄時 gate 維持 fail-closed |
| Phase 9 執行授權（N=1 真實調用） | 未取得。需 Owner 在場＋當日臨場逐字授權句（05 §6.18） |
| ledger 檔案**意外刪除**＝讀成「未燒過」，可再燒一次 | 兩審獨立指出（`_read_physical_records` 對 `FileNotFoundError` 回 `[]`）。§6.16 已接受「有意刪改」為殘餘風險，但「意外重放」在防護範圍內，本項落在兩者交界。兩審均建議登記凍結、非本批引入。是否加獨立錨點（inode／建立時間／第二處 digest）**待 Owner 裁決** |

## NIGHT-BATCH-27 補貨 — 2026-08-06（雙審 findings 登記，排 NB-28）

NB-27（八包＋FIX09）已於 `31fbdcc` 合併並 push。兩輪雙審結論：
八包 = Fable 5 pass／Opus 5 conditional pass（一項阻擋：對照組 flaky，已由 FIX09 修復）；
FIX09 = Fable 5 pass／Opus 5 conditional pass，**零阻擋**。
實跑：`2462 passed, 1 skipped, 14 xfailed`；mypy 11 檔＋5 檔全綠；
定向重複跑合計 WSL 100 次＋Windows 80 次，零失敗。
以下為登記存貨，**不構成任何實作、寫入或執行授權**。

### 【夜跑可做】

| 條目 | 來源 | 邊界 |
|---|---|---|
| **對照組的 rendezvous 實測無效，措辭必須更正**：`tests/test_phase9_burn_ledger.py:339` 新加的 `start_barrier.wait()` 對穩定性無貢獻——`ProcessBarrierPresence` 已在 `app/phase9_gate.py:705` 對**同一個 barrier** 會合且離臨界區更近，完全支配該行。實測 fix vs nofix 失手率相同（閒置 1/120 vs 1/120；滿載 37/60 vs 31/60，z≈1.1 不顯著）。**穩定性 100% 來自 k=5 聚合** | Opus 5 FIX09 finding 1（P2） | docs/測試註解 only；該行留著無害，但任何報告或 commit 訊息**不得**把確定性歸因於 rendezvous |
| **k=5 的邊際不足**：CPU 滿載時單輪失手率 0.617，k=5 殘餘偽紅率約 **8.9%/invocation**（閒置與四核負載下分別為 4.0e-11、1.3e-4）。建議改 `k_max≈20 ＋ 撞到雙執行即 break`：閒置下更快（約 1 輪），滿載下降至 6e-5 | Opus 5 FIX09 finding 2（P2） | tests only；不得改為放寬結果集合或標 slow／xfail／flaky |
| 每輪 `assert line_count in {1,2}` 應改條件式：對 `["EXECUTED","TOKEN_ALREADY_BURNED"]` 的輪次唯一正確值是 1，允許 2 會掩蓋「被拒行程卻寫了紀錄」的缺陷 | Opus 5 FIX09 finding 4（P3） | tests only |
| `_process_worker` 的 `start_barrier.wait()` 位於 `try:` 之外，barrier 破損時子行程裸退出、不投遞 queue 訊息，父層只看到 `exitcode!=0`，診斷不如 `UNEXPECTED:BrokenBarrierError` | Opus 5 FIX09 finding 3（P3） | tests only；實測無 hang（11.8s 有界） |
| 對照組使該測試由 ~1.3s 升至 ~4.5–6.5s（5 倍）；early-break 可一併解決 | Opus 5 FIX09 finding 5（P3） | tests only |
| `inspect.getsource` 禁字掃描只掃單一方法，barrier 若藏在類主體屬性或 lambda 預設值可規避（實務上被 `__dict__` callable 斷言擋住） | Opus 5 FIX09 finding 6（P3） | tests only；資訊性 |
| 保護版 20 輪測試共用 `_process_worker`，FIX09 也改變了它的時序；已證明仍能拒絕無鎖 ledger，但**本身未做 ≥50 次重複跑**（有 `@pytest.mark.slow`） | Opus 5 FIX09 未解問題 3 | tests only；補重複跑證據 |
| Windows 原生樣本量僅 10 次 invocation／50 round，足以坐實 NTFS 靜默丟寫註解，**不足以估計 Windows 滿載偽紅率** | Opus 5 FIX09 未解問題 2 | measurement only |

### 【NB-27 八包遺留、本批未修的 P3】（來源：Opus 5 八包審查）

> **NB-28 已消耗四項（2026-08-06）**：burn 邊界中止碼三分
> （`BURN_NOT_ATTEMPTED`／`BURN_WRITE_FAILED`／`BURN_DURABLE_UNVERIFIED`，
> 落盤與否以持鎖狀態下重讀 ledger 判定，判定失敗一律保守）、乾淨退出路徑的
> denial 收斂、`_find_in_flight_denial` 改為雙鏈廣度優先、非有限 timeout 拒絕。
> 下表其餘各項與上表【夜跑可做】各項**均未消耗**，仍為 NB-29 以後的存貨。

### 【NB-28 雙審 findings 登記，排 NB-29】

雙審結論：Fable 5 = conditional pass、Opus 5 = PASS，**零阻擋**。
**利益衝突揭露**：NB-28 的派工規格與程式實作同源（皆為派工者），
故兩審皆被要求加嚴，且兩份 findings 全數列此。

| 條目 | 來源 | 邊界 |
|---|---|---|
| **`commit()` 的 fsync 失敗路徑繞過新分類**：`phase9_burn_ledger.py:285-292` 在 `write()+flush()` **成功後** fsync 失敗時**直接 return `durable=False` 而不拋例外**，因此不經 `_commit_failure_disposition`，落入 gate 既有的 burn_verification 檢查而回報 `BURN_VERIFY_FAILED`——但紀錄**物理上已在檔案內**（第一審以真實 `FileBurnLedger` 實測 `contains()` 回 True）。NB-28 已先以文件修正（§4.4b 明記此碼可能代表 token 已消耗），**程式面未改** | Fable 5 NB-28 P1-1 | 比照 readback 失敗改為拋例外並走 `_commit_failure_disposition`；**不得**放寬任何 fail-closed 條件 |
| **包1 的核心主張無真實 ledger 測試**：NB-28 新增的 6 個 gate 測試**全部注入 `TmpBurnLedger` 假件**，其 `contains()` 走與生產完全不同的路徑（重讀檔案文字、無 handle 重用、無 flush）。第二審自行補跑真實 `FileBurnLedger` 的四個場景（全過）並建議收編為正式測試 | Opus 5 NB-28 補證 | tests only；把真實 ledger 的四場景收為提交測試 |
| **本批新增兩行零測試覆蓋**（coverage 實測）：`_burn_boundary_disposition` 的 `"commit"` 保守分支與 `except GateDenied: raise` 一行 | Opus 5 NB-28 finding 2 | tests only；第二審已 probe 證明後者正確，前者實務上近乎不可達 |
| **`_commit_failure_disposition` 用裸 `except Exception` 包住 `contains()`**，會吞掉 `GateDenied`（`RuntimeError` 子類），原始拒絕碼消失。與相隔約 240 行的 `except GateDenied: raise` 處理相反，屬同檔自相矛盾。安全方向保守（替代碼為不可重試的 `CRASH_AFTER_BURN`），生產 `FileBurnLedger.contains()` 亦只拋 `BurnLedgerError` | Opus 5 NB-28 finding 1 | 統一兩處對 `GateDenied` 的處理 |
| **包1 正確性依賴一條未寫入契約的不變式**：`_read_physical_records` 的**持鎖分支會先 `handle.flush()`**，非持鎖分支不會。第二審實測：改用非持鎖探測時，`contains()` 會在資料仍在緩衝區時回 False——**那就會是真正的反向漏洞**。日後若有人「優化」掉該 flush 或改走非持鎖分支，包1 靜默失效 | Opus 5 NB-28 finding 3 | 在 `contains()`／`_read_physical_records` docstring 明記此不變式；牽涉推遲中的「`contains()` 持鎖對稱性」，**待 Owner 裁決是否落成程式契約** |
| `_burn_boundary_disposition` 的 `"commit"` 分支是否真的可達（第二審無法構造可達案例）：留作 defence-in-depth 或收斂 | Opus 5 NB-28 未解問題 2 | **待 Owner 拍板**；不得逕自刪除 |
| `BurnLedger` Protocol 未約束 `contains()` 可拋哪些例外，決定上列裸 `except` 的風險大小 | Opus 5 NB-28 未解問題 3 | 契約設計 only |
| backlog 的四項消耗只以前言宣告，表內對應列未逐列標記，日後易重複派工 | Opus 5 NB-28 finding 5 | docs only |

| 條目 | 邊界 |
|---|---|
| 乾淨退出路徑的 denial 未收斂（`app/phase9_gate.py:800`，`except GateDenied` 分支）：`__exit__` 乾淨時停在 `CHECKING`／`frozen=False`／`rejection_count=0`。僅 BurnLedger 實作自拋裸 `GateDenied` 才觸發，executor 恆 0 | 修法為導向 `_converge_existing_denial`（冪等）；不得順手擴大 |
| NaN timeout 無界忙轉（`phase9_burn_ledger.py:104-106,146-147`）：`nan <= 0` 為 False 通過驗證，`monotonic() >= nan` 恆 False，sleep 被夾成 0.0。基線既有、非回歸；gate 只傳常數 5.0，實務不可達 | 加 `math.isfinite` 檢查 |
| 開檔／取鎖失敗與 **commit 內部 readback 失敗**仍報 `BURN_WRITE_FAILED`：後者紀錄其實已 fsync 落盤（實測 `physical_records=1`），維運會誤以為沒燒而重試 | 錯誤碼細分；仍須 fail-closed |
| `contains()` 不檢查持鎖，與 `commit()` 不對稱：公開 API 允許無鎖 check-then-act，只靠慣例保護。基線相同 | 對稱化或文件化 |
| `_find_in_flight_denial` 的 `__cause__` 盲點（`app/phase9_gate.py:98`）：`current.__context__ or current.__cause__`，若 `__context__` 是非 denial 的鏈而 denial 只掛 `__cause__` 就會漏找。基線零 diff | 兩條鏈都要走 |
| 同執行緒重入診斷品質下降：改用不可重入 `threading.Lock` 後，重入會耗掉整個 timeout（gate 常數 5.0s）才回報通用的 `lock unavailable`，無法區分「重入」與「競爭」 | 恢復專屬訊息或快速路徑；不得放寬有界失敗 |
| Windows `msvcrt` 分支無持續 CI 覆蓋：兩輪四份審查的 Windows 證據皆為手動、不具持續性 | 提案 only；不得偽稱 CI-covered |

## NIGHT-BATCH-29 補貨 — 2026-08-06（雙審 findings 登記，排 NB-30）

NB-29（四包：稽核鏈遷移／burn evidence builder／gate 接線／Owner grant verifier）
獨立複審：Fable 5 = pass、第二審（fresh-context, Opus）= conditional pass，**零阻擋**。
與 NB-27 相同先例（八包／FIX09 亦為 pass + conditional pass、零阻擋）下 ff-merge。
以下為兩份審查登記、非本批範圍內修的 P2/P3；**不構成任何後續實作或執行授權**。

| 條目 | 來源 | 邊界 |
|---|---|---|
| **`AuditChainReceipt` 欄位驗證對非字串 `entry_hash` 無 `isinstance` 保護**：`app/phase9_gate.py` 的 receipt 驗證區塊在呼叫 `len(audit_chain_receipt.entry_hash)` 前未先確認其為 `str`。若注入的 `AuditChainWriter` 回傳 `entry_hash=None`／整數等畸形值，`TypeError` 會逃逸到外層 `except Exception`，被 `_burn_boundary_disposition("burn_verification", receipt)` 分類為 `BURN_VERIFY_FAILED`／`PRECALL_AUDIT_FAILURE`，而非更精確的 `CRASH_AFTER_BURN`。executor 仍恆為 0、gate 仍收斂 `CLOSED_DENY`、token 仍視為消耗（`burn_ledger.contains()` 仍 True），**非執行或重放安全洞**；但 `PHASE9_ABORT_PLAYBOOK.md` §4.4b 明文禁止「已落盤的燒錄用讀來安全可重試的碼回報」，此為分類精確度缺陷。本批尚無真實 `AuditChainWriter` 實作，故此路徑目前不可達 | 第二審（fresh-context, Opus）Q1 | 加 `or not isinstance(audit_chain_receipt.entry_hash, str)` 到驗證條件；tests only，**不得**放寬任何 fail-closed 條件 |
| **「不 import audit_writer_local」的 AST 守門測試對 `from X import Y` 形式無效**：`tests/test_phase9_burn_evidence.py` 與 `tests/test_phase9_gate.py` 的 `imports` 集合由 `alias.name` 組成，對 `from app.audit_writer_local import append_audit_event` 只會收到 `append_audit_event`，斷言 `"app.audit_writer_local" not in imports` 恆真、不構成有效防線。目前兩檔實際皆為零 import，非本批引入的漏洞，屬既有測試盲點 | 第二審 Q7-3 | 改用 `ast.ImportFrom.module` 比對；tests only |
| **B-C evidence 的 3 個 safety_flags／`event_notes` 可讀性偏樂觀**：`app/phase9_burn_evidence.py` 的 `synthetic_local_only=False`／`mock_only=False`／`dry_run=False` 與 `event_notes`「consumed before any OpenClaw call」在 gate 目前恆要求 `executor.test_double is True`（`app/phase9_gate.py:840`）的前提下，未反映「本次仍是受控假件」的事實；該事件也會是 `data/audit_dev.jsonl` 中第一筆三旗皆 False 的紀錄，日後讀者易誤讀為「真實呼叫已發生」。未發現任何旗或欄位**謊報**已取得執行授權（`openclaw_call_allowed`／`external_side_effects_*` 等仍誠實為 False） | 第二審 Q6 | 待 Owner 或下一批裁決是否讓旗/文字反映 `test_double` 事實；docs/measurement only，**不得**藉此放寬任何一旗 |
| **`AuditChainWriter.append_burn_evidence` 的 Protocol 簽章傳整個 `BurnRecord`**（含 `token_digest`／`binding_hash`）而非已白名單化的投影；純函式 builder 本身不外洩，但介面本身不結構性強制未來 writer 也不外洩 | 第二審 Q7-1 | 待真實 writer 落地時一併設計；本批僅為 Protocol 注入點，設計選擇 only |
| `AuditAuthorizationVerifier` 類別 docstring 稱「wording change therefore fails closed until reviewed」，但實際 runtime 比對的是硬編常數，非即時讀檔；05 文字被改動時只有測試會紅，不是 runtime fail-closed | 第二審 Q4 | 措辭修正 only；不影響安全（`test_recorded_owner_audit_grant_text_and_digest_match_05` 已鎖此不變式） |

**獨立複核（Fable 5，2026-08-06）**：對上列前兩項均已用真實碼路徑再驗證（`entry_hash=None` 確實觸發 `TypeError`→`BURN_VERIFY_FAILED`；`from…import` 形式確實逃過 AST 守門），確認非誇大。V6（暫改 05 §6.19 第 2 項一字、確認 digest guard 變紅、還原後零 diff 且測試轉綠）已獨立重跑通過。

## NIGHT-BATCH-30 補貨 — 2026-08-07（雙審 findings 登記，排 NB-31）

NB-30（四包：真實 `AuditChainWriter`／真實 executor 骨架／補償證明＋解除 blanket deny／六步閉環演練）
雙審結論：主審 Fable 5 = pass、第二審（fresh-context）= pass，**零阻擋**，已 ff-merge 並 push（`bbfc013`）。
findings 僅存在於審查報告、未經登記，由 Opus 5 於合併後補登。以下**不構成任何後續實作或執行授權**。

| 條目 | 來源 | 邊界 |
|---|---|---|
| **演練報告的「真實 OpenClaw 呼叫 0」是硬編字面值，不是量出來的**：`tests/test_phase9_n1_rehearsal.py` 第 171 行把 `real_openclaw_call_count` 直接寫成 `0`，第 222 行對它的斷言因此是同義反覆；`research/PHASE9_N1_REHEARSAL_DRYRUN_20260807.md` 複述同一未實測數字。該值目前為真，靠的是 AST 接線檢查與 `app/` 內零建構點這兩個**獨立**事實，不是這一步量到的。文件讀起來像實測證據，實際不是 | 第二審 | 改以真實 instrumentation（例如 monkeypatch 全域 `subprocess.run` 並斷言呼叫數）取代字面值；tests/docs only，**不得**藉此放寬任何斷言 |
| **執行器與版本探針的 `process_runner=None` 預設會靜默建構真實 runner**：`app/phase9_gate.py` 第 553 行與第 582 行附近，未顯式傳入時會拿到真實 `ForegroundSubprocessRunner()` 而非報錯。目前 `app/` 內零建構點故不可達，但這是「忘記傳參數就取得真實執行能力」的形狀 | 第二審 | 改為必填關鍵字參數；**接線前必須先做**，屬執行日前置硬化 |
| **死碼與失效屬性**：`app/phase9_gate.py` 第 862 行附近的 `except NotImplementedError` 分支自 exec02 起不可能觸發（兩個真實類別都不再拋該例外）；`Executor.test_double` 自 exec03 起 `run()` 內已無任何邏輯讀取，僅供測試辨識 | 主審 | 清理 only；移除前須確認沒有測試依賴該分支 |
| **entry-state check-then-act 的理論競態**（`app/phase9_gate.py` 第 817 行附近）：多執行緒場景下理論上可競態。**非本批 diff 引入**（既存碼），且 `Phase9Gate` 在 `app/` 內零建構點故不可達 | 第二審 | 真正接線時一併處理；本批不構成阻擋 |

**Opus 5 獨立複核（2026-08-07）**：已自行核對 master＝origin＝`bbfc013`、四個 commit 無額外自撰 commit、`10 files changed, 1108 insertions(+), 21 deletions(-)`、`data/audit_dev.jsonl` SHA-256 未變、`data/phase9_burn.jsonl` 不存在、四處紅線檔零 diff、`app/phase9_gate.py` 無 `threading`／`subprocess` import。

## NIGHT-BATCH-32 補貨 — 2026-08-08（雙審 findings 登記，最重一項排 NB-33）

NB-32 共五包（真實 principal／真實 OOB 讀取／token issuer 接線／Owner 自檢工具／
清單修正），前兩包由 ChatGPT 於獨立 Windows clone 施工，後三包由 Codex 於 WSL 正牌
repo 施工。雙審結論：主審 Fable 5 = accepted（自報 R-13 未完成）、
第二審（fresh-context, Opus）= conditional pass，**零阻擋**，已 ff-merge 至 `010e182`。
以下為登記事項；**不構成任何後續實作或執行授權**。

| 條目 | 來源 | 邊界 |
|---|---|---|
| **自檢工具的執行視窗指示與其檢查的性質相反，且照做時根本執行不了**：`scripts/check_phase9_oob_wiring.py` 恆印「請在 hermes-owner 視窗執行此檢查」，僅在 `current_uid() == GATE_UID` 時才補印「這只是樣張」。但該工具要證明的是「gate（uid 1000）讀得到 Owner（uid 1001）寫的檔，且認得出不是自己寫的」——**此性質只有坐在 uid 1000 才驗得到**。照指示在 hermes-owner 視窗讀自己寫的檔，會得到無警語的成功訊息與 return code 0，實際上不證明任何事。Opus 5 另實測：`/home/lnovo` 權限為 `drwxr-x---`，`hermes-owner` 不在該群組，**連進入 repo 目錄執行該腳本都做不到**，故該指示不僅方向相反且無法遵循 | 第二審＋Opus 5 實測 | **排 NB-33，執行日前必須修**：警語應改掛在 uid 1001 側，並明確標示 uid 1000 那次才是決定性的；同時修正「在哪個視窗跑」的敘述。屬 C4 交付物本身的正確性缺陷，非新功能 |
| **自檢工具唯一碰檔案系統的函式零測試覆蓋**：`scripts/check_phase9_oob_wiring.py` 的 `_observe_regular_file` 與 `_principal_name` 在五個模擬測試中一律被注入替身，故 symlink 拒絕、`S_ISREG` 判定、`pwd` 查詢皆無回歸保護。第二審手動補驗行為正確（symlink 拒、root 所有拒、同 uid 拒） | 第二審 | 補真實檔案系統邊界測試；tests only |
| **preflight 與實際 gate 的接受條件不一致**：自檢工具只回 `writer_uid`，不檢查權限位；但 `RegularFilePresenceReader` 要求 `stat.S_IMODE & 0o077 == 0`，亦不檢查 payload 是否為合法 JSON。故工具給綠燈後，執行日 gate 仍可能以「owner presence response is unavailable」中止。方向為 fail-closed，非 fail-open | 第二審 | 讓 preflight 檢查條件與 gate 對齊；與上一條可同批 |
| **`_validated_oob_directory` 用字串比對，可繞過**：`scripts/run_phase9_n1.py` 以 `as_posix()` 字串前綴判定 `/mnt/c`。第二審實測 `//mnt/c/...`（POSIX 保留雙斜線、`as_posix()` 不正規化）、`/mnt/C/...`、`/mnt/d/...`、`/mnt/wsl/...` 皆被接受。預設 automount（uid 1000）下仍 fail-closed，但若 `/etc/wsl.conf` 將 automount uid 設為 1001，會變成 fail-open 的假綠燈 | 第二審 | 改以 `Path.resolve()` 加掛載檔案系統型別判定；非預設設定才觸發 |
| `PHASE9_IMPLEMENTATION_INVENTORY` 稱 `for_formal_runtime` 沒有呼叫者，實際 `tests/test_phase9_token_issuer.py` 有測試呼叫者；同檔他處慣例是標「測試接線」。實質結論（formal 未接線）正確 | 第二審 | 措辭精確化 only |
| `tests/test_phase9_n1_entrypoint.py` 中 T2 的 docstring 稱 real cross-uid isolation 延後至 C4，但 C4 已落地且交付的是工具與模擬測試，**並未**完成真實跨 uid 驗證。該句現在會誤導 | 第二審 | 措辭修正 only |
| `scripts/check_phase9_oob_wiring.py` 的 `GATE_UID` 為硬編 1000，而進入點用的是 runtime `os.getuid()`；兩處對 gate 身分的認定來源不同 | 第二審 | 統一為 runtime 取得 |
| `_observe_regular_file` 的 `lstat` → `open` 之間存在理論 TOCTOU（`writer_uid` 取自 open 前的 lstat 而非 open 後的 fstat）。本機 Owner 自用工具，影響極小 | 主審＋第二審 | 觀察 only |
| research 目錄下的文件不在任何 artifact integrity 清單內（v5 只收 `scripts/` 與 `docs/schemas/`，v6 只收 `agent_operating_system/*.md`），故其內容無防竄改釘死 | 第二審 | 觀察 only；擴大涵蓋範圍屬另案 |

**Opus 5 獨立複核（2026-08-08）**：已自行核對 master 與 origin 於合併前皆為 `797a378`、本輪三筆 commit 與七個檔案範圍相符、`app/` 自 `797a378` 起零 diff、`docs/schemas/` 零 diff、`data/audit_dev.jsonl` SHA-256 未變、`data/phase9_burn.jsonl` 不存在、無 merge commit、未 push。另**更正第二審一項事實錯誤**：該報告稱 `/var/hermes-phase9` 尚不存在，實測該目錄存在且為 `drwxr-xr-x hermes-owner hermes-owner`，uid 1000 可讀取；其餘 findings 均經證據支持。
