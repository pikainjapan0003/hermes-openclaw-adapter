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

### 【Owner 閘】（五組選案維持未裁決）

| 選案 | 目前狀態 | 未裁決前行為 |
|---|---|---|
| RED — schema error redaction | **空白**；一頁表已校正為 A=validator、B=exposure、C=double-layer（建議 C） | E-01/E-02 xfail 維持；不得 export raw validator error |
| AUD — v1.1 audit record | **空白**；A/B/C 提案與 B 建議仍只是設計 | 不改 schema、不實作 writer |
| RB — rollback Git binding | **空白**；A/B/C 提案與 B 建議仍只是設計 | 不改 schema、不執行或猜測 Git rollback |
| PB — Hermes `produced_by` | **空白**；A/B/C 提案與 A 建議仍只是設計 | schema 維持非空字串；future adapter 另行 fail closed |
| ROOT — `parent_task_id: null` projection | **空白**；一頁表已校正為「尚無正式標號方案」，suggested direction 不是選項 | root projection 維持 HOLD，不填 placeholder；ROOT 不可回選案字母 |

`OWNER_DECISION_ONE_PAGER_20260726.md` 已於 NIGHT-BATCH-16 包1校正，現在可
安全閱讀與回覆其中四組已有正式來源選項的選案：RED／AUD／RB／PB。ROOT
仍是第五組空白 Owner gate，但在正式比較稿完成前只能維持空白。任何回覆都
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
| RED／AUD／RB／PB／ROOT 五組既有選案 | **全部空白**；校正後一頁表可安全回覆四組正式選案，ROOT 無正式選項 | 不改 schema、validator、writer、projection 或 runtime；ROOT 保持 HOLD |
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
