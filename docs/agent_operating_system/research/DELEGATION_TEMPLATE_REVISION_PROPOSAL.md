# Delegation Template Revision Proposal

Status: **PLANNING ONLY, NOT AUTHORIZED — `30_DELEGATION_PROMPTS.md` UNCHANGED**

Source review: `DELEGATION_PROMPT_REVIEW_20260728.md`. The text below is a
candidate replacement set for later review. It is not active routing, does not
dispatch an agent, and does not widen §6.13 or any Owner gate.

## Proposed common overlays

Every future template would retain the current common constraint footer and add
the following two blocks when applicable.

### Routing overlay — proposed full text

```text
[建造層路由]
任務類型：<主幹／量產／純 coding／重大設計／關鍵決策>
指定格位：<Sol+high／Luna+high／Luna+max／Sol+xhigh／Sol+max>
選擇理由：<一行；必須對得上 10_MODEL_ORCHESTRATION.md C8>
失敗軌跡：<無，或先前模型/格位、錯誤、已試方法>
升級規則：只依 C8；不得因趕時間跳級或把升級當授權。
```

### Night-batch overlay — proposed full text

```text
[夜跑包邊界；只在 Owner 已派 §6.13 批單時附]
批次／包：<NIGHT-BATCH-N／pkgN，逐字抄批單>
branch／base：<branch>／<immutable base hash>
本包允許檔案：<exact paths>
本包禁止事項：<逐字抄批單與全批紅線>
commit：本包測試與 git diff --check 綠後，僅一個
  night-batch-N-pkgN-<short-name> commit。
HOLD/skipped：卡住照實標記、零替代工作；只有原批單允許時才繼續下一包。
merge/push：執行者禁止；Fable 5 批審依 05 §6.13 處理。
不得自行從 backlog 加包、換包、合包或拆出未授權產品工作。
```

## T-01 repo scan — suggested replacement

```text
背景：<一句話，為什麼要找>
目標：在 <精確目錄範圍> 找出 <對象與 pattern>
branch/package boundary：<目前 branch/base；若屬夜跑，附 overlay>
不做：不修改檔案；不延伸到未列目錄；不把無命中宣稱為不存在
允許讀取：<目錄清單>
方法：列出使用的搜尋 pattern、大小寫/副檔名/ignore 規則與排除路徑
驗收：每個結果附 file:line 與一行說明；回報實際覆蓋目錄與排除項
HOLD：檔案量或工具限制使窮盡性不足 → 回報實際覆蓋率與缺口，不猜
```

Revision reason: preserves read-only scope while making exclusions and package
boundaries auditable.

## T-02 implementation — suggested replacement

```text
背景：<Phase + 動機 + 05 對應節>
目標：實作 <exact artifacts and behavior>
建造層路由：<attach routing overlay>
若為夜跑：<attach night-batch overlay verbatim>
規格：<fields/interfaces/examples/const and fail-closed constraints>
允許修改：<exact whitelist>
禁止：<protected files, routes, persistence, runtime, execution, adjacent refactor>
驗收：<exact pytest/mypy/lint commands> 全綠；至少 <N> 個反例；
  git diff --check 無輸出；列新增/修改檔與逐檔 diff 摘要
HOLD：規格與現有 contract/fixture/治理正本衝突 → 停本包，列證據，
  不自行取捨、不拿其他工作代替
回報：狀態、commit（若獲批單要求）、原始測試輸出、風險、未解問題
```

Revision reason: adds C8 routing, immutable package discipline, exact redlines,
and evidence required by the current nightly workflow.

## T-03 refactor — suggested replacement

```text
背景：<診斷 D-xx／lesson／量測證據>
目標：<refactored shape>
建造層路由：<attach routing overlay>
不變式：<public behavior, safety gates, errors, schemas, tests>
允許修改：<exact whitelist>
禁止：新功能、公開介面/安全 gate 變更、順手修 discovered behavior bug
基線：修改前執行 <commands> 並保存原文
驗收：修改後同命令全綠；git diff --check；review 證明行為零變
HOLD：必須改行為才能完成，或基線原本紅 → 停並分開回報
```

Revision reason: explicitly separates refactor from bug-fix authority.

## T-04 research/web — suggested replacement

```text
背景：<問題>
目標：回答 <exact questions>
允許能力：<工作單明列的 approved read-only web/search connector>
來源：技術問題優先官方文件/原始研究；每項附 URL、標題、查證日期
禁止：用訓練記憶回答可變版本/日期/存在性；未授權登入、提交或下載到 repo
驗收：每個結論可追到來源；推論明標 inference；UNVERIFIED 單獨成節
HOLD：能力不存在或關鍵來源不可得 → 列已試方法，不自行換未授權 fallback
```

Revision reason: routes by approved capability instead of stale product tool
names.

## T-06 fresh read-back — suggested replacement

```text
背景：驗收 <artifact list>；reviewer 不得沿用作者推理或未落檔主張
目標：逐一核對存在、標題、必要章節、引用路徑、HOLD/正反例/邊界
方法：從檔案與正本重建 checklist；每項 PASS/FAIL + file:line
限制：本模板只驗存在性與完整性，不簽核語意正確性或高風險安全性
驗收：所有 FAIL 一次列全；無 finding 也列實查範圍
HOLD：任一必要項缺失 → artifact 未通過 read-back
```

Revision reason: makes reviewer independence and the non-semantic limit
explicit.

## T-07 high-risk adversarial review — suggested replacement

```text
背景：<artifact> 涉及 <安全邊界/寫入/執行閘/Owner 簽核>
硬閘：依 20 R-13，至少兩個不同模型、互不共享作者推理的 fresh-context
  review。單一結果必須標「不足以作高風險簽核依據」。
reviewer identity/model：<model A or B；每份 prompt 分開發>
目標：找規則衝突、錯誤路徑/模型名、弱模型誤讀、計劃→授權、
  display→permission、mock→real、缺 HOLD/驗收、無來源宣稱
不做：不改檔、不補實作、不提風格偏好、不看另一 reviewer 結論後迎合
驗收：每個 finding = severity + file:line + 觸發/誤讀場景；無 finding 也列角度
彙整：兩份報告都落檔；分歧逐條交 Owner/Fable 5，不得沉默仲裁
HOLD：只有一個模型可用 → 高風險簽核 HOLD
```

Revision reason: closes TREV-02 by embedding the R-13 two-model rule.

## T-08 connected document reading — suggested replacement

```text
背景／目標：<why, exact file/folder/resource, questions>
指定 connector：<work order names the approved read-only connector>
禁止：修改/分享/刪除、下載到 repo、用別的帳號或工具繞過權限
驗收：主張附文件名、stable id/location、最短必要引文；標讀取範圍
HOLD-A：connector/capability unavailable → 原樣回報，不 silent fallback
HOLD-B：connector available but permission denied → 列無法讀的資源，不繞過
```

Revision reason: distinguishes capability absence from document authorization.

## T-09 Dashboard/Replit smoke — suggested replacement

```text
背景：驗證唯讀部署表面；不驗證未提供的 deployed revision
目標：對 <exact URLs> 記 HTTP 狀態、read-only 標示、控制項、洩漏跡象
方法：使用工作單指定的唯讀 HTTP/browser capability；不提交表單
三源語義：
  - HTTP 200–399 = Replit reachable only
  - deployed_hash = UNKNOWN unless an authorized source actually provides it
  - local==GitHub 不代表 Replit revision aligned
禁止：token/login probe、POST、表單提交、把 reachable 報為 deployed hash verified
驗收：reachability/local-GitHub/deployed-revision 三欄分開；無授權畫面=UNVERIFIED
HOLD：疑似洩漏只報類型與位置，不複述 secret/payload
```

Revision reason: adopts the current three-source UNKNOWN semantics.

## T-10 GitHub review — suggested replacement

```text
背景／目標：<Phase 0 consistency or external repo review>
指定能力：<approved GitHub connector or read-only CLI named by work order>
方法：唯讀取得 exact ref/hash/PR/issue facts；記查證時間
禁止：push、PR/issue/fork、權限變更、authentication workaround
三源限制：local/origin equality is a two-source claim; do not infer deployed hash
驗收：hash exact；一致/不一致/UNREACHABLE 分開；connector permission failure=HOLD
```

Revision reason: capability-based routing plus exact two-/three-source claims.

## T-12 plan validation — suggested replacement

```text
背景：05 plan periodic verification under Phase 11
目標：逐 Phase 核對 05 §5 current status、inputs, references, git evidence,
  Owner gates, and already-issued §6.13 package boundaries
方法：run D-12 read-only checks; Replit HTTP reachability stays separate from revision
禁止：用 remembered HEAD/current test count；修改 plan；把 night backlog 當 assignment
驗收：每項 PASS/FAIL/UNKNOWN + evidence；Owner-gated phases remain explicit
HOLD：01 conflict, unknown phase mapping, source drift, or three-source mismatch
```

Revision reason: adds the present §6.13 and Replit semantics without changing
the plan.

## Templates not proposed for replacement

- T-05 general review remains usable; severity/resolution metadata could be a
  later minor edit.
- T-11 open-source evaluation remains usable; primary-source wording could be a
  later minor edit.

## Decision and boundary

Proposal disposition: **________**

Until a later package explicitly authorizes edits, every block above remains
inactive proposal text. `30_DELEGATION_PROMPTS.md` is still the current file and
remains subordinate to CLAUDE.md, 01, 05 §6.13, 10 C8, and 20 R-13.
