# 05 經驗證的長期計劃表（Verified Long-term Plan）

- 撰寫：Fable 5 replanning session（2026-07-07），依據 v1.0-RC-R closeout 第 14 節的 Fable 5 handoff 授權
- 讀者：未來每一個 session 的模型 + Owner
- 用法：Owner instruction 引用「Phase N」即可，不必重貼背景（見 00_QUICK_DIAGNOSIS.md D-03）。模型收到指令後讀對應 Phase 章節再開工。
- 命名對照：Owner instruction 的 `[PHASE]`（v1.0-A 等版本序，屬 CLAUDE.md 體系）與本表 Phase 0–11 是**兩套命名**。instruction 應寫明對應（例：`[PHASE] v1.0-A（計劃表 Phase 3）`）；未寫明 → 問 Owner，不得自行推斷。
- 鐵律：**本計劃表不是授權。** 每個 Phase 的實作仍需 Owner instruction 逐字授權（01_SAFETY_BOUNDARIES.md 第 4 節）。計劃表寫「允許實作」意思是「屆時可以向 Owner 提案實作」，不是「現在就能做」。

---

## 0. 摘要索引（30 秒版）

| Phase | 名稱 | 一句話 | 可提案實作※ | 外部副作用 | 建議模型 |
|---|---|---|---|---|---|
| 0 | Current State Verification | 每 session 開工前三源對齊 | 否（檢查） | 無 | Haiku 級可 |
| 1 | Weak-model Operating System | 本制度上線與磨合 | docs only | 無 | Sonnet 級 |
| 2 | v1.0 Definition Freeze | Owner 凍結 v1.0 定義 | docs only | 無 | Sonnet+Owner |
| 3 | Blackboard Contract Hardening | 9 種 schema + validator + 測試 | 是（local） | 無 | Sonnet 級 |
| 4 | Owner Approval Packet | 審批包 schema + 產生器 | 是（local） | 無 | Sonnet 級 |
| 5 | Dry-run Evidence Bundle | 標準化 dry-run 證據包 | 是（local） | 無 | Sonnet 級 |
| 6 | Dashboard Read-only Hardening | 唯讀防呆自動化驗證 | 是（display） | 無 | Sonnet 級 |
| 7 | Local Audit / Rollback Preview | 首次授權寫入：local dev 檔 | 是（local write） | 無 | Sonnet 級，強模型審 |
| 8 | Remote Read-only Planning | 遠端/共享後端唯讀規劃 | docs only | 無 | 強模型 |
| 9 | Limited Controlled Execution | 首次真實執行（N=1、可逆、白名單） | 是（受控） | **有，單發** | 強模型+Owner 在場 |
| 10 | Connector Read-only Expansion | scope packet 制 connector L1 | 是（受控讀） | 讀外部 | Sonnet 級，強模型審 |
| 11 | Long-term Loop Engineering | 常態運行節律與制度自我維護 | 持續 | 依授權 | 混合 |

※「可提案實作」欄**不是授權**（見上方鐵律）：值為「是」只代表該 Phase 屆時可以向 Owner 提案實作。

順序原則：0–1 隨時做；2 是 3–7 的前提；3→4→5 有依賴鏈；6 可與 4、5 並行；**7 依賴 Phase 5 的 evidence bundle，必須在 5 之後**；8 規劃可提早；9 必須在 3+4+5+7 全部完成後；10 在 9 之後（先證明執行紀律，再開外部讀取）；11 貫穿全程。

---

## 1. 目前系統狀態（2026-07-07 驗證）

- 系統 = Hermes（advisory only）× Blackboard（概念存在，schema 未定）× Worker（dry-run only）× OpenClaw（mock gateway only）× Dashboard（GET-only display）× Owner（唯一 approver）。
- v1.0-RC-R closeout 已完成並 push：`HEAD 7a93127e6ee5de4941700d48078cd35836944086`，本機 == GitHub live（本 session 以 `git ls-remote` 驗證）。
- 全系統處於 read-only / mock / dry-run / synthetic rehearsal 狀態。無任何 real write、real dispatch、real call 曾發生（v1.0-RC-R 第 9 節逐條確認）。
- 工作區狀態：制度全套與 README 同步已於 2026-07-07 依 Owner 指示 commit 並 push（`8648f00`、`47bbc4e`，本機==origin）；`patches/` 未追蹤（既知狀態）。
- Replit `https://hermes-openclaw-adapter.replit.app/dashboard/system` 可載入，標示唯讀，登入牆前無任何執行控制（WebFetch 驗證）。登入後畫面已由 Owner 截圖確認（2026-07-07）：總覽/任務/系統頁為唯讀顯示；**`/dashboard/reviews` 含既存的 Owner 核准/拒絕按鈕**（v0.7.x 建立，decision ≠ dispatch，`dispatch_allowed=False`，詳見 90 L-006）。dashboard 版本 0.5.6、Worker OFF、OpenClaw/Hermes 未接線、Google Sheets 已停用。
- 已知主要缺口（Drive v1.0 報告 + 本 session 檢查）：Blackboard 9 種 schema 未定、approval packet 未定、audit/rollback 真實 write path 不存在、connector scope packet 未成熟、v1.0 定義未凍結。注意：`app/google_sheets_oauth_writer.py` 是**既存的真實寫入能力模組**（env flag 防護、預設關閉、檔名無 real_ 標記），動它前先讀 00 D-09 第 (4) 條。

## 2. 資料來源

### 2.1 已驗證（本 session 實際讀取/執行）

- 本機 repo：`/home/lnovo/projects/hermes-openclaw-adapter`，git log/status/ls-remote 實跑。
- Drive 文件（subagent 全文讀取）：《開發總結報告 v1.0》（Doc ID `19UcxFjiKnwNTPzLaiMjv2oC7Ym7U1tbE8qnGoEUCB_Q`）、《v0.9.5–v0.9.6》（`1qh_hS8Dxfp3wbhMq5mRbyp81c5SyhXeS7mHcMZAERa4`）、《deep-research-report (3).md》（`1vzkiz3TmItnF538OW0f6G7am3Gwf1mmu`）。
- 本機文件：CLAUDE.md、docs/HERMES_FULL_BLACKBOARD_LOOP_REHEARSAL_CLOSEOUT_V1_0_RC_R.md 全文。
- GitHub：repo 公開、master、195 commits、0 issues/PR（WebFetch）。
- Replit：/dashboard/system 登入牆前畫面（WebFetch）。
- 開源/文獻參考：8 項，見 2.3，全部經本 session WebSearch/WebFetch 逐一驗證。

### 2.2 無法驗證（明確標註，禁止當事實引用）

- Replit 登入後的 dashboard 內容（無 token 可用）。
- Drive 資料夾內 PDF/docx 版教學報告（依標題判定與 deep-research-report 同內容，未開啟確認）。
- v1.0-RC 各子階段在 Drive 報告中的 commit hash（報告未列；本機 closeout 文件有列，以本機為準）。
- CrewAI / AG2 的 human-in-the-loop 細節（未第一手查證）。
- OWASP Agentic Top 10 的完整十項內容（只驗證了發布頁，未讀全文 PDF）。

### 2.3 開源與文獻參考（已驗證，含可借鑑/不可照抄）

| # | 參考 | 狀態（查證時） | 可借鑑 | 不可照抄 |
|---|---|---|---|---|
| 1 | [Flock](https://github.com/whiteducksoftware/flock) blackboard 框架 | 活躍，0.5.600（2026-06），~112★ | Blackboard 訊息 = typed schema artifact（Pydantic contract）；circuit breaker 防迴圈 | 它是 Dapr 分散式 runtime，過重；只借 contract 思想 |
| 2 | [Terrarium](https://arxiv.org/abs/2510.14312)（arXiv 2025-10） | 學術 testbed | Blackboard 是天然安全咽喉點：驗證、審計、審批都放在 board 層 | 它是攻擊模擬研究，不是 production 協定 |
| 3 | [LangGraph HITL 官方文件](https://docs.langchain.com/oss/python/langchain/human-in-the-loop) | 活躍官方文件 | 審批四動詞 approve / edit / reject / respond；凍結狀態可跨時間恢復 | 不引入 LangGraph runtime；在 Blackboard 檔案上實作同語意 |
| 4 | [HumanLayer](https://github.com/humanlayer/humanlayer) ~11.1k★ | **SDK 已 deprecated**，公司轉向 | 審批放在 tool-calling 層、per-function、可異步離線批 | 不要依賴其 SDK 或 hosted API，僅設計參考 |
| 5 | [microsoft/agent-governance-toolkit](https://github.com/microsoft/agent-governance-toolkit) ~4.7k★，v4.1.0（2026-06） | 活躍 | YAML policy：allow / deny / require_approval 三裁決，deny 在工具呼叫前結構性攔截 | 企業級身分/沙箱體系對單 Owner 檔案系統過重 |
| 6 | [OWASP Agentic Top 10 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/)（2025-12 發布） | 已發布 | 每次新開能力前的 pre-flight 風險清單 | 全文未讀（見 2.2），使用前先讀原文 |
| 7 | [Anthropic safe agents framework](https://www.anthropic.com/news/our-framework-for-developing-safe-and-trustworthy-agents)（2025-08） | 官方原則文 | 升級階梯：read-only 預設 → 逐動作審批 → 對已證明可靠的例行動作發持久授權；不可跳級 | 原則非實作；「持久授權」是很後期的事 |
| 8 | [mcp-firewall](https://github.com/ressl/mcp-firewall) ~10★ | 極早期 | hash-chain 防篡改審計日誌（每筆記錄含前筆 hash） | 太不成熟且 AGPL；只借日誌設計不用代碼 |

註：OpenAI Swarm 已查證為 deprecated（educational only），不列入參考。

---

## 3. 各階段詳細計劃

每階段格式固定：為什麼現在／目標／輸入／輸出／邊界／驗收／最易出錯／HOLD／模型與流程／進入下一階段條件。

欄位對照（弱模型逐項核對用）：Why now＝為什麼現在｜Goal＝目標｜Inputs＝輸入｜Outputs＝輸出｜Allowed actions＝安全邊界內明示允許的動作｜Forbidden actions＝安全邊界的禁止部分＋01 全部禁令（永遠疊加）｜Required model level／Subagent use／Fresh-context review＝模型與流程（review 要求另見 3.1 表）｜Validation method＝驗收條件所列方法｜PASS criteria＝驗收條件全數成立｜HOLD criteria＝HOLD 條件｜Most likely failure modes＝最易出錯｜Recovery path＝3.1 表｜Next phase entry condition＝進入下一階段條件。

### 3.1 各 Phase 的 Recovery Path 與 Fresh-context Review 要求

| Phase | Fresh-context review | Recovery path（驗收失敗或做錯時怎麼退回安全狀態） |
|---|---|---|
| 0 | NO | 純讀取，無狀態可壞；發現漂移 → 回報 Owner，不自行同步 |
| 1 | YES（制度檔修訂時） | docs 全在 git 管理下：未 commit 用 `git checkout -- <file>` 還原（Owner 同意後）；已 commit 用 `git revert` |
| 2 | YES | 純 docs：還原上一版；撤銷「已凍結」宣告須 Owner 明示 |
| 3 | YES（schema 初稿） | schema／validator／tests 均為新增檔：刪除新增檔即回基線；禁止為過測試而改既有 fixture |
| 4 | YES（adversarial 必做） | builder 為純函式新檔：刪檔回退；發現 packet→執行通路 → 立即移除該通路並記 90 |
| 5 | YES | 新增檔刪除即回退；被污染的 fixture 用 git 還原 |
| 6 | NO（以反向測試代替：注入 button 應紅） | 測試檔可整檔移除；誤改 route/template → git 還原 |
| 7 | YES（另加強模型審寫入代碼） | 停止呼叫 writer 即無新副作用 → 經 Owner 同意刪除 `data/audit_dev.jsonl` → 刪新增檔回基線 |
| 8 | YES | 純 docs，同 Phase 2 |
| 9 | YES＋Owner 在場 | 執行前：廢棄 token 即中止。執行後：執行 approval packet 內的 rollback path（該欄必填正因於此）；rollback 也失敗 → 凍結一切執行、人工處理、記 90 |
| 10 | YES（gate 代碼） | 撤銷 scope packet（刪 packet 檔）→ gate 自動回 L0；讀取無副作用，無資料需回滾 |
| 11 | NO（健檢本身即 review） | 健檢誤刪規則 → 依 40 F4 的精簡驗收紀錄用 git 還原 |

### Phase 0：Current State Verification（每 session 例行）

- 為什麼現在：一切決策的地基。三源（local/GitHub/Replit）漂移時做的所有工作都可能作廢（D-12）。做完代表：本 session 的事實基礎成立。沒做會卡住：後續每一步。
- 目標：確認 local HEAD == origin master == 預期狀態，Replit 可載入且仍為唯讀。
- 輸入：無（任何 session 可直接執行）。
- 輸出：回報中一段三源狀態（三個 hash/狀態 + 一致與否）。不產生檔案，除非發現漂移（則記入 90_LESSONS_LEARNED.md）。
- 安全邊界：純讀取。禁止為「修復不一致」而擅自 push/pull/reset/redeploy。
- 驗收條件：回報含 local HEAD hash、ls-remote hash、Replit HTTP 可達性三項，且為實跑結果（引用命令輸出）。
- 最易出錯：假設 origin 與本機一致而不實查；用舊 session 記憶的 hash 充數。
- HOLD 條件：三源任兩者不一致 → 回報差異，等 Owner 決定同步方向。
- 模型與流程：Haiku 級即可；無需 subagent；命令直接抄 00_QUICK_DIAGNOSIS.md D-12。
- 進入下一階段：一致即通過。本 phase 永遠重複，無「完成」。

### Phase 1：Weak-model Operating System（本制度上線）

- 為什麼現在：Fable 5 只有這一次；制度不落地，之後每個弱模型 session 都在裸奔。做完代表：任何 Sonnet 級 session 能按文件自舉。沒做會卡住：所有後續 phase 的執行品質。
- 目標：docs/agent_operating_system/ 全套文件存在、互相引用正確、CLAUDE.md 有路由指向。
- 輸入：本 session 產出（00、01、05、10、20、30、40、90、99、README）。
- 輸出：上述檔案 + 後續每個 session 對文件的磨合修訂（走 40 的規則）。
- 安全邊界：docs only。修改 01 的第 1–3 節需 Owner。
- 驗收條件：fresh-context read-back 通過（每檔存在、必要章節齊、引用路徑正確）；一個新 session 只讀 CLAUDE.md + README 就能答出「現在系統在哪個狀態、下一步是什麼、什麼不能做」。
- 最易出錯：文件之間規則打架（例如 CLAUDE.md phase lock vs 計劃表引用式指令）——衝突時 CLAUDE.md 與 01 優先。
- HOLD 條件：發現文件互相矛盾且無法判定優先序 → 問 Owner。
- 模型與流程：維護用 Sonnet 級；修訂安全相關內容需 fresh-context review。
- 進入下一階段：Owner 以 Owner Review 通過形式（CLAUDE.md 第 2 節格式）接受本制度，並記錄於下一輪 instruction。「一頁總結」指 Fable 5 session 最終回報中的 ONE-PAGE OWNER SUMMARY。

### Phase 2：v1.0 Definition Freeze

- 為什麼現在：v1.0-RC 已 closeout，但「v1.0 到底是什麼」沒有凍結定義，任何實作都會範圍蔓延。做完代表：v1.0 有一份不可再默默膨脹的定義文件。沒做會卡住：Phase 3–7 的驗收都沒有基準。
- 目標：產出 `docs/agent_operating_system/02_V1_0_DEFINITION.md`，採 Drive v1.0 報告建議：**v1.0 = Owner-supervised Blackboard Loop MVP Baseline**。明確列入/列出：包含（本機 Blackboard read-write with schema、approval packet 流程、dry-run evidence、audit 檔 local write、rollback preview）；不包含（real Worker dispatch、real OpenClaw call、connector read/write、production DB、remote API、Dashboard controls）。
- 輸入：Drive v1.0 報告第 8 節建議、本計劃表、Owner 決定。
- 輸出：定義文件 + Owner 簽核紀錄（文件內一行：`Owner approved on <date>, instruction quote: ...`）。
- 安全邊界：docs only。定義本身不解除任何禁令。
- 驗收條件：定義文件對每個「包含」項都有對應驗收方式；每個「不包含」項都寫明推遲到哪個 phase；fresh-context read-back。
- 最易出錯：把「包含 Blackboard write」誤讀為「現在就可以寫」——定義≠授權。
- HOLD 條件：Owner 未逐字簽核前，任何人不得宣稱 v1.0 定義已凍結。
- 模型與流程：Sonnet 級起草，Owner 逐條裁決（這是品味/取捨題，流程補不了，見誠實條款）。
- 進入下一階段：Owner 簽核。

### Phase 3：Blackboard Contract Hardening

- 為什麼現在：Blackboard 是整個系統的安全咽喉點（參考 #2 Terrarium）；schema 不定，後面 approval packet、evidence bundle 都無地基。做完代表：所有 board 訊息可被機器驗證，弱模型可以「拒絕格式錯誤」而不必「判斷內容好壞」（參考 #1 Flock）。沒做會卡住：Phase 4、5、7、9。
- 目標：定義並實作 9 種 schema（task draft / annotation / approval readiness / owner decision / worker dry-run / openclaw command envelope / result message / audit event / rollback event）+ validator + pytest 測試。
- 輸入：Phase 2 定義、docs/schemas/ 既有內容、fixtures/local_mock_data/ 既有 fixture 反推欄位。
- 輸出：`docs/schemas/` 下 9 份 JSON Schema、`app/blackboard_validators.py`、`tests/test_blackboard_schemas.py`（tests/ 目錄現不存在，屆時新建）、一份 schema 索引文件。每種 schema 必含欄位：`schema_version`、`safety_flags`（沿用 v1.0-RC 16 面旗）、`prev_entry_hash`（為 Phase 7 hash-chain 預留，參考 #8）。
- 安全邊界：只新增 schema/validator/測試檔；不改 mock 元件行為；不建立任何 write path；validator 只在記憶體驗證 fixture。
- 驗收條件：pytest 全綠（含每 schema 至少 1 正例 fixture + 2 反例 fixture）；fresh-context review 檢查 schema 是否涵蓋 v1.0-RC-D fixture 的全部欄位。
- 最易出錯：schema 寫完但和既有 fixture 對不上（拿理想欄位而非實際欄位）；validator 順手接上 runtime。
- HOLD 條件：發現既有 fixture 欄位互相矛盾（需 Owner 裁決哪個是對的）。
- 模型與流程：Sonnet 級實作；schema 設計初稿建議一次強模型 review；驗收 = 測試 + fresh-context read-back（不允許純自驗）。
- 進入下一階段：9 schema 測試全綠 + Owner review 通過。

### Phase 4：Owner Approval Packet

- 為什麼現在：這是「Owner-supervised」的核心機制，v1.0 報告已列出必要欄位。做完代表：任何未來執行請求都有標準審批格式，Owner 可以在異步、離線狀態下裁決（參考 #3、#4）。沒做會卡住：Phase 7、9。
- 目標：定義 approval packet schema + 產生器（從 dry-run 結果生成 packet 的純函式）+ 顯示（納入既有 GET-only dashboard）。
- 輸入：Phase 3 schema；v1.0 報告欄位清單：action summary、risk level、exact target、expected side effects、rollback path、timeout、dry-run evidence、audit trail preview、approval timestamp、single-use execution token。
- 輸出：`docs/schemas/approval_packet.json`、`app/approval_packet_builder.py`（純函式，無 IO 副作用）、dashboard 顯示區塊、測試。
- 決策動詞採參考 #3 的四動詞：`approve / edit / reject / respond`。Owner 的裁決在本 phase 只以檔案形式模擬（synthetic fixture），不建真實裁決入口。
- 安全邊界：packet 是資料格式，不是執行機制。本 phase 禁止實作「讀取 packet 並執行」的任何代碼。dashboard 仍 GET-only。single-use execution token 欄位在本 phase 永遠為 `null`（真 token 機制屬 Phase 9）。
- 驗收條件：測試全綠；fresh-context adversarial review 專項檢查「是否有任何 code path 能從 packet 走到執行」——必須為零。
- 最易出錯：builder 順手加上「approved 就觸發下一步」的方便邏輯——這正是 Result Message is not next dispatch permission 要防的。
- HOLD 條件：任何人（包括 Hermes 建議）要求在本 phase 加執行 hook → HOLD。
- 模型與流程：Sonnet 級；adversarial review 必須 fresh-context。
- 進入下一階段：Owner review 通過。

### Phase 5：Dry-run Evidence Bundle

- 為什麼現在：Phase 9 的真實執行必須「先有完整證據再有審批」；證據格式現在不定，屆時審批包就是空殼。做完代表：每次 dry-run 自動產出可審計的證據包。沒做會卡住：Phase 9。
- 目標：標準化 dry-run 輸出為 evidence bundle：輸入 task、command envelope、mock 結果、預期副作用清單、diff preview（若適用）、bundle hash。
- 輸入：Phase 3 schema、既有 worker_mock_gateway_dry_run.py 輸出。
- 輸出：`docs/schemas/evidence_bundle.json`、`app/evidence_bundle_builder.py`、fixture、測試。
- 安全邊界：bundle 產生只讀 fixture 與 dry-run 記憶體結果；寫入僅限 `fixtures/local_mock_data/`，且此寫入屬本 phase 任務授權範圍（01 §4 第 5 條），仍須在回報中逐檔列出。
- 驗收條件：一次完整 rehearsal flow 能產出通過 schema 驗證的 bundle；hash 可重算一致。
- 最易出錯：bundle 裡塞入真實環境資訊（路徑、token、env）造成洩漏——bundle 欄位須白名單制。
- HOLD 條件：發現 dry-run 輸出含 secrets → 停，先修 dry-run。
- 模型與流程：Sonnet 級；驗收含一次 fresh-context read-back。
- 進入下一階段：與 Phase 4 均完成，Owner review 通過。

### Phase 6：Dashboard Read-only Safety Hardening（可與 4/5 並行）

- 為什麼現在：dashboard 是 Owner 的眼睛，也是「display ≠ permission」誤讀的高發區。做完代表：唯讀性由自動化測試保證，不再只靠人記得。沒做會卡住：Phase 8 的遠端唯讀規劃沒有可信基線。
- 目標：(0) **先盤點現有 route 與控制項，建立白名單**（已知：登入表單、`/dashboard/reviews` 既存 Owner 核准/拒絕控制〔90 L-006〕、tasks 頁篩選表單）；(1) 白名單**以外**的 `/dashboard/*` route 自動化驗證為 GET-only、無 form/button/action URL（HTML 層 assert）；(2) 所有 preview 區塊帶標準安全標籤（沿用 v0.9.6-C 十標籤）；(3) 檢查不洩漏 secrets/payload；(4) 對 reviews 的既存核准 POST 加**行為測試**：approve 只寫 decision event，不觸發任何 dispatch（`dispatch_allowed` 保持 False）。
- 輸入：既有 templates/、app/main.py route 表。
- 輸出：`tests/test_dashboard_readonly.py`（對每個 route：GET 200、POST 405/404、HTML 無 `<form`、無 `<button`（登入表單除外，白名單標註）、標籤存在）。
- 安全邊界：只加測試與標籤；不改 route 行為；不動登入機制。
- 驗收條件：pytest 全綠；故意注入一個 `<button>` 到 template 測試會紅（驗證測試真的在防守）。
- 最易出錯：測試寫成「只測現有 route」，未來新增 route 逃過檢查——route 清單須動態枚舉 app 的 route 表。
- HOLD 條件：發現**白名單以外**的未知 POST route → 停，回報 Owner；發現 approve 路徑可達任何 dispatch/execution 代碼 → 最高優先回報。
- 模型與流程：Sonnet 級；反向測試（注入 button 應紅）為必做驗收。
- 進入下一階段：測試全綠且反向測試證明有效。

### Phase 7：Local Audit / Rollback Preview（首次授權寫入）

- 為什麼現在：這是整個計劃第一次解除「No audit trail write」——刻意選最低風險的寫入（本機 dev 檔、append-only、可整檔刪除重來）作為寫入紀律的練習場。做完代表：系統第一次有真實持久化的行為紀錄，且 hash-chain 防篡改（參考 #8）。沒做會卡住：Phase 9（沒有審計就不許執行）。
- 目標：audit event 寫入 `data/audit_dev.jsonl`（append-only、每筆含 prev hash）+ rollback preview（對每筆可執行動作，預生成「如何撤銷」的描述性 preview，不實作撤銷執行）。
- 輸入：Phase 3 audit/rollback schema、Phase 5 bundle。
- 輸出：`app/audit_writer_local.py`、`app/rollback_preview_builder.py`、測試（含 hash-chain 斷鏈偵測測試）。
- 安全邊界：**需 Owner instruction 逐字授權**：`允許寫入 data/audit_dev.jsonl（local dev append-only）`。僅此一檔。不寫 queue、不寫 Blackboard 正式區、不碰 production。rollback preview 是文字產物，不是執行機制。
- 驗收條件：寫入後 hash chain 驗證通過；篡改中間一筆後驗證必須失敗；fresh-context review 確認無其他寫入路徑被夾帶。
- 最易出錯：「順便」把 queue write 也接上（就差一行）；audit 檔路徑寫成共享位置。
- HOLD 條件：Owner instruction 沒有逐字寫出允許的檔案路徑 → HOLD。
- 模型與流程：Sonnet 級實作 + 強模型（可用的最強）review 寫入代碼；fresh-context adversarial review 必做。
- 進入下一階段：Owner 檢視實際 audit 檔內容後簽核。

### Phase 8：Remote Blackboard / Shared Backend Read-only Planning（docs only）

- 為什麼現在：可提早並行，因為純規劃。Replit 上的 dashboard 已是遠端唯讀顯示的雛形。做完代表：遠端/共享後端的唯讀方案有文件與風險評估。沒做會卡住：多裝置/多 agent 觀測。
- 目標：規劃（不實作）遠端 Blackboard 唯讀方案：資料同步方向（單向 local→remote）、認證、不暴露 payload 的顯示層、與 Replit 現有部署的關係。
- 輸入：Phase 6 基線、Replit 現況（登入後畫面屆時需 Owner 提供或授權查看）。
- 輸出：一份 plan 文件 + OWASP Agentic Top 10 對照檢查表（使用前先讀原文，見 2.2）。
- 安全邊界：docs only。禁止建立任何 remote API、webhook、callback receiver。
- 驗收條件：plan 對每個組件都寫明「讀什麼、絕不寫什麼、認證怎麼做、洩漏面在哪」。
- 最易出錯：規劃文件裡的示例代碼被未來 session 誤當已授權實作——文件內每段代碼前加 `PLANNING ONLY, NOT AUTHORIZED`。
- HOLD 條件：規劃過程發現需要暴露新 endpoint 才可行 → 記為 open question 交 Owner，不自行放寬。
- 模型與流程：強模型起草（架構取捨題）；Sonnet 級可做資料收集。
- 進入下一階段：Owner 決定是否排入實作（可長期停在規劃）。

### Phase 9：Limited Controlled Execution Rehearsal（首次真實執行）

- 為什麼現在：只有在 3（schema）、4（審批包）、5（證據包）、7（審計）全部就位後，才有資格談真實執行。做完代表：系統完成第一次「證據 → 審批 → 單發執行 → 審計 → 驗證 → （必要時）回滾」的完整閉環，N=1。沒做會卡住：一切真正的 automation。
- 目標：選一個**白名單動作**完成單次真實執行。白名單動作標準（全部滿足）：(a) 可逆或冪等；(b) 影響範圍單一資源；(c) 失敗後果可完整描述；(d) 有 rollback 命令且已在 dry-run 驗證過。建議首選：對 Owner 自有測試資源的一次寫入（例如寫一行到 Owner 指定的測試 Google Sheet——需屆時另行 connector 授權——或更保守：一次 `openclaw agent` 的無害查詢型調用）。實際動作由 Owner 屆時指定，本計劃不預授權任何動作。
- 輸入：Phase 3/4/5/7 全部產出。
- 輸出：一份 execution rehearsal 報告：完整 evidence bundle、approval packet（含 Owner 真實裁決與 single-use token）、執行輸出、audit chain、事後驗證、rollback 演練結果。
- 安全邊界：**Owner 必須在場**（同步 session，非異步）。single-use execution token 由 Owner instruction 提供、用後即廢。一次授權一發，執行完自動回到全禁狀態。第二發需要全新 packet + token。No retry without new token——執行失敗不得自動重試。
- 驗收條件：閉環六步各有落檔證據；audit chain 驗證通過；token 重放測試失敗（token 真的單次）。
- 最易出錯：執行失敗後模型「幫忙」重試（違反單發原則）；把 rehearsal 成功解讀為常態執行授權（Closeout is not next-phase start）。
- HOLD 條件：evidence bundle 與實際執行參數有任何不一致 → 廢棄 token，重走流程。
- 模型與流程：可用的最強模型主導；Owner 同步在場逐步確認；全程不委派有副作用的步驟給 subagent。
- 進入下一階段：Owner 對 N=1 結果簽核，並明文決定是否擴大白名單（每次擴大都是新的 Owner 決定）。

### Phase 10：Connector Read-only Expansion

- 為什麼現在：外部資料讀取價值高（如嗶咔報價流程），但必須在執行紀律證明後才開。做完代表：connector 有 scope packet 制度，L1（metadata read）安全開放。沒做會卡住：所有需要外部資料的實際業務。
- 目標：定義 connector scope packet schema（connector 名、級別 L0 documentation / L1 metadata read / L2 content read / L3 write、資源清單、有效期、發放紀錄）；實作 L1 讀取路徑 + 審計；L2/L3 保持禁止。
- 輸入：v0.9.5 系列文件（L0 已完成）、Phase 7 audit、Phase 9 紀律。
- 輸出：scope packet schema、`app/connector_scope_gate.py`（無 packet 一律裁決 L0）、L1 實作、測試。
- 安全邊界：每次 connector 調用前 gate 檢查 packet；packet 過期即失效；L2/L3 請求一律 HOLD。已知環境事實：service account 可讀分享檔但不能寫個人 My Drive（無配額），寫入需 OAuth——L3 規劃時必須考慮。
- 驗收條件：無 packet 調用被 gate 攔截的測試；過期 packet 被拒的測試；audit 記錄每次調用。
- 最易出錯：L1 實作「順便」讀了內容（metadata 與 content 的界線要在代碼層 assert，不是靠自律）。
- HOLD 條件：packet 內級別與指令要求不符 → HOLD。
- 模型與流程：Sonnet 級實作，強模型審 gate 代碼。
- 進入下一階段：Owner 按資源逐項發放 packet（常態運行，無終點）。

### Phase 11：Long-term Loop Engineering（貫穿全程）

- 為什麼現在：制度不維護就退化（見 99 信第 2 節）。做完代表：系統有節律地自我檢查與精簡。
- 目標與節律：
  - 每 session：Phase 0 三源檢查；踩坑即回寫 90。
  - 每 10 個 session 或每月（先到者）：跑一次「制度健檢」——90 是否超 300 行需精簡（40 F4）、文件互引是否斷鏈、01 是否被繞過的案例。
  - 每次 phase closeout：更新本計劃表的 Phase 狀態行（只改狀態不改結構）。
  - 每季：重新驗證 2.3 參考的活性（deprecated 的移除）；重讀 Anthropic/OWASP 是否有新版。
- 輸出：健檢報告 append 到 90；計劃表狀態更新。
- 安全邊界：健檢是讀取與 docs 修訂，走 40 的權限分級。
- 驗收條件：健檢報告含具體行數/斷鏈清單，非「大致良好」。
- HOLD 條件：健檢發現 01 曾被繞過 → 立即報 Owner，凍結相關能力直到根因寫入 90。
- 模型與流程：Sonnet 級例行；發現制度性問題升強模型。

---

## 4. 誠實條款（harness 的極限）

拆解、驗證、多樣本評審可以補**執行**品質；但以下不能靠流程補足：

- 模糊題與品味判斷（例：v1.0 該包含什麼——Phase 2 必須 Owner 裁決）。
- 產品方向與商業取捨（例：connector 該優先接哪個服務）。
- 「這樣做值不值得」類問題。

遇到這類問題，弱模型必須：(1) 升級模型；(2) 找外部第二意見；(3) 或明說做不到/不確定。禁止用流暢的散文掩蓋沒有判斷依據的事實。

---

## 5. 狀態追蹤（每次 phase closeout 後更新本節）

| Phase | 狀態 | 最後更新 | 備註 |
|---|---|---|---|
| 0 | 常態運行 | 2026-07-07 | 本 session 已跑一輪，三源一致 |
| 1 | 本 session 建立 | 2026-07-07 | 待 Owner 接受 + 首個弱模型 session 磨合 |
| 2–11 | 未開始 | — | Phase 2 為下一個建議動作 |
