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

**二次補強（2026-07-08）**：Owner 盤問 20 題的裁決與各 Phase 修訂記錄於**第 6 節**；第 3 節內容與第 6 節衝突時以第 6 節為準。要點：Phase 9 併入 v1.0（6.3）、Phase 8 升為 v1.0 後第一優先、Phase 10 無限期停留規劃。

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

- 為什麼現在：一切決策的地基。local/GitHub 漂移或 Replit 不可達時，針對錯誤狀態做的所有工作都可能作廢（D-12）。做完代表：本 session 的事實基礎成立。沒做會卡住：後續每一步。
- 目標：確認 local HEAD == origin master == 預期狀態，並確認 Replit HTTP 可達且仍為唯讀；本檢查不驗證 Replit deployed hash。
- 輸入：無（任何 session 可直接執行）。
- 輸出：回報中一段三源狀態（三個 hash/狀態 + 一致與否）。不產生檔案，除非發現漂移（則記入 90_LESSONS_LEARNED.md）。
- 安全邊界：純讀取。禁止為「修復不一致」而擅自 push/pull/reset/redeploy。
- 驗收條件：回報含 local HEAD hash、ls-remote hash、Replit HTTP 可達性三項，且為實跑結果（引用命令輸出）；不得把 HTTP 可達性寫成 Replit revision 已與 GitHub 對齊。
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
- **二次補強**：v1.0 候選定義已由 Owner 預裁決（6.3：Phase 9 N=1 併入 v1.0），本 Phase 工作縮小為按 6.9 checklist 逐條正式簽核 + 產出 02 文件。

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
- **二次補強**：優先級上調——手機開 Replit 是完成態主介面（Q11），本 Phase 是 v1.0 後第一優先；方案預定向 GitHub→Replit 單向拉取、顯示帶資料時間戳（6.5/6.7/6.10）。

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
- **二次補強**：本 Phase 已併入 v1.0 範圍（Q4）；白名單動作已由 Owner 預指定＝無害查詢型 `openclaw agent` 調用、零寫入（Q5，見 6.8 階梯）；屆時仍需逐字授權 + Owner 在場。

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
- **二次補強**：本 Phase **無限期停留規劃**（Q3=C：先服務系統自身）；業務（pika/Vault）要接入時才重啟，且須先跑 6.11 T1 重審。

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
| 2 | **完成** | 2026-07-18 | `02_V1_0_DEFINITION.md` 凍結（Owner 逐字簽核，見該檔 §5；fresh-context read-back 通過） |
| 3 | **完成** | 2026-07-19 | 9 schema＋validator＋pytest 41/41 全綠（Fable 5 於 WSL 乾淨 venv 獨立實跑）；§6.12 裁決全落實（16 面旗封閉、9 公共欄、OWNER_MANUAL 派工路徑結構性拒絕）；Codex Luna+max 施工（commit `f9ae105`）、Fable 5 審查、Owner 核准合併。掛帳：jsonschema/pytest 未入 requirements（白名單禁改依賴檔，另單補） |
| 4 | **完成** | 2026-07-19 | approval packet schema＋純函式 builder＋GET-only 顯示（`d305ff8`）；token const null 三重鎖；雙審查員通過（Fable 5 全項驗收＋Opus fresh-context 對抗審查「packet→execution 零路徑」） |
| 5 | **完成** | 2026-07-19 | evidence bundle schema＋builder＋hash 重算/篡改/洩漏反向測試（`88bf8b2`，NIGHT-BATCH-1） |
| 6 | **完成** | 2026-07-19 | 動態 route 盤點＋七條 POST 白名單＋注入 button 必紅＋approve 行為測試（`9f79657`）；queue-claim guard 二版於 NIGHT-BATCH-3 補強（已知風險：approve→queued 後若外部啟動 worker 可被 claim，execution gate 屬 Phase 9） |
| 8 | **規劃完成** | 2026-07-19 | docs 方案＋OWASP 對照（`3edbc0b`）；離線 projection contract（`51f657f`，超包，Owner 2026-07-19 追認）；遠端接線／remote API 仍未授權 |
| 7 | 設計已備 | 2026-07-19 | `07_AUDIT_WRITE_DESIGN.md`（NIGHT-BATCH-2）；**實作前置＝Owner 逐字授權句「允許寫入 data/audit_dev.jsonl（local dev append-only）」，未給不得動工** |
| 9–11 | 未開始 | — | Phase 9 需 Owner 在場；Phase 7 實作＋Phase 9 為 v1.0 最後兩關 |

---

## 6. 二次補強（Second-pass Refinement，2026-07-08 Owner 盤問整合）

- 來源：2026-07-08 grill-me 盤問，三輪共 20 題（Round 1 核心方向 Q1–Q10、Round 2 執行條件 Q11–Q15、Round 3 風險取捨 Q16–Q20），Owner 全數親答、零 SKIP。
- 效力：本節記錄的是 **Owner 已裁決的方向**，第 3 節各 Phase 內容與本節衝突時以本節為準（本節較新）。但**本節仍不是授權**——第 7 行鐵律照舊，實作仍需 Owner instruction 逐字授權。
- 修改權限：本節記錄 Owner 裁決，屬 40 F2——修改任何一條裁決都必須先問 Owner。

### 6.0 決策紀錄（Q1–Q20 速查）

| Q | 主題 | Owner 裁決 |
|---|---|---|
| 1 | 終局形態 | 傳話中樞（留言板）。權力全在 Owner；Hermes 監工調度、OpenClaw 做事；**刻意保持簡單** |
| 2 | 第一條 loop | 全鏈路：Hermes → Blackboard → OpenClaw → Result → Hermes readback |
| 3 | 第一個服務對象 | 系統自身（自我維護），暫不接 pika / Vault 業務 |
| 4 | v1.0 範圍 | **必須含一次真實全鏈路執行**（Phase 9 N=1 併入 v1.0） |
| 5 | N=1 動作 | 無害查詢型 `openclaw agent` 真實調用，零寫入 |
| 6 | 成功指標 | 信任感：三個月後 Owner 敢把某類真實任務放心交給它 |
| 7 | 砍點 | 無。永遠修到好，接受 bug 長存，賭模型會進步 |
| 8 | 並行授權粒度 | 三級：無害自動跑／寫入逐件批／高風險（花錢等）**不派 AI**，Hermes 在計劃中標記提醒 Owner 親自做 |
| 9 | Owner 可投入時間 | 每天可碰（每週 5+ 小時），同步審批可行 |
| 10 | 時程 | 2–3 個月穩紮穩打（系統還是記憶空白的嬰兒階段） |
| 11 | 主使用介面 | 完成態＝手機開 Replit dashboard（看狀態、批任務）；Claude Code 是施工介面 |
| 12 | 三環境關係 | **GitHub 為王**（source of truth）；流向：本機 → GitHub → Replit |
| 13 | Blackboard 介質 | repo 內 `data/` JSON 檔，隨 git 走（一條管道，歷史免費） |
| 14 | 模型費用配置 | 規劃/審查/檢查 → ChatGPT 5.5；寫代碼 → Sonnet；Opus 幾乎不用 |
| 15 | Hermes 肉身 | adapter 程式 + 三腦：GPT-5.5 → Minimax M3 → Deepseek v4 Pro（用量耗盡右移） |
| 16 | 三腦資料外送 | 不設限（自有專案資料）。重審觸發器見 6.11 |
| 17 | 最怕的錯 | A 越權動作最怕；謊報用**多審查員異模型交叉**壓；失控迴圈可手動 kill |
| 18 | v1.1 首次真實寫入 | repo 內測試檔（git 回滾＝標準 rollback path） |
| 19 | 手機審批門檻 | Replit 現有登入牆即可（Owner 知悉風險）。重審觸發器見 6.11 |
| 20 | 腦降級規則 | 三腦同權，不縮權限、不加降級標記 |

### 6.1 Owner Goal Profile

- **終局**：一個刻意簡單的傳話中樞。Blackboard 是留言板＝多 agent 並行協作的協調介質；使用權力永遠在 Owner。
- **真實痛點**（原話大意）：做專案時，一個 AI agent 從計劃、施作、監工到審查用到底，又難又花時間。
- **願景場景**：Hermes 把計劃切成細小任務 → 丟給多個角色化 OpenClaw（工程師、UI 設計師、PM、測試員、安全審查員…）並行施工 → Owner 只看哪個報錯。
- **服務順序**：系統自身 → （未來另行決定）Vault / pika。
- **節奏**：每週 5+ 小時、v1.0 目標 2–3 個月、無砍點。
- **成功指標**：信任感。反向指標＝信任事故（越權、謊報、假驗收）；Phase 11 健檢必查「本期間有無信任事故」。
- **弱模型設計裁決規則**：任何提案先過一問——「這會不會讓傳話層變複雜？」會 → 預設否決，除非 Owner 明示要。

### 6.2 Loop Engineering Definition

- 「長期穩定運行的 loop」＝ **Hermes 留言 → Blackboard → OpenClaw 執行 → Result 回貼 → Hermes readback** 這條全鏈路。
- 可機械判定的「穩定」定義：連續 3 次完整 rehearsal（屆時為真實 run）**無人工介入**跑完全鏈路，且每次 audit 記錄完整、schema 驗證全過。
- 長期形態：同一條 loop 橫向擴成多 worker 並行（角色化），錯誤狀態上浮給 Owner；並行擴張屬 v1.2 之後，本計劃表內不實作。

### 6.3 v1.0 Definition Candidate（供 Phase 2 正式凍結）

```text
v1.0 = Owner-supervised Full-chain Baseline
     = Phase 3–7 全部完成
     + Phase 9 的 N=1：一次無害查詢型 openclaw agent 真實調用成功
```

- 包含：本機 Blackboard 讀寫（schema 驗證）、approval packet 流程、dry-run evidence、audit 檔 local write、rollback preview、**一次真實全鏈路查詢調用（零寫入）**。
- 不包含：任何真實寫入型執行（→ v1.1）、真實代碼任務（→ v1.2）、connector read/write（Phase 10，無限期規劃）、production DB、remote API runtime、Dashboard 新控制項。
- 與第一輪定義（Drive 報告建議版）的差異：**Phase 9 N=1 併入 v1.0**（Owner Q4=C）；理由：「傳話中樞的 v1.0」必須證明真的能傳話。
- 本候選仍需 Phase 2 正式簽核（見 6.9），簽核前不得宣稱 v1.0 定義已凍結。

### 6.4 Risk Tolerance Matrix

| 風險 | Owner 容忍度 | 防禦配置（弱模型照做） |
|---|---|---|
| 越權動作（未授權的寫/發/叫） | **零容忍，最怕** | 01 禁令牆 + 四問 + adversarial review，防禦資源最厚；發生即最高優先回報 |
| 謊報／假驗收 | 低 | 高風險審查一律 ≥2 個不同模型交叉審（20 R-13）；單一模型自審不得作為通過依據 |
| 弄壞 repo | 中 | GitHub 為王 + git 回滾為標準恢復路；破壞性 git 操作仍需授權 |
| 失控迴圈 | 中（Owner 可用 Claude Code 手動終止） | 嬰兒階段不建自動 circuit breaker；多 worker 並行前重新評估 |
| 亂花錢／不可逆動作 | 結構性排除 | `OWNER_MANUAL` 級任務**不進派工佇列**（見 6.8），Hermes 只在計劃中標記提醒 |
| 資料送三腦廠商 | 不設限（Q16=A，自有資料） | 無需 sensitivity 欄位；重審觸發器見 6.11 |
| 手機審批入口被冒用 | 接受（Q19=A，現有登入牆） | Owner 已知悉；重審觸發器見 6.11 |

### 6.5 Tool Role Map

| 角色 | 定位 | 規則 |
|---|---|---|
| 本機 WSL repo | 開發工作區 | 一切開發在此發生 |
| GitHub master | **source of truth** | 漂移裁決一律以 GitHub master 為準；同步方向固定：本機 → GitHub → Replit。push 仍需 Owner 指示 |
| Replit | 部署/展示層；**完成態的手機主介面** | 從 GitHub 拉取部署；不得直接在 Replit 上改代碼；顯示須帶資料時間戳（新鮮度標示） |
| Claude Code | 施工介面（建造 Hermes 的工人） | 不是 Hermes 本人 |
| ChatGPT 5.5 | 規劃/審查/檢查顧問 | 經 Owner 搬運（export bundle → Drive → GPT），異步 |
| 手機 | 完成態使用介面 | 看狀態、批任務；門檻＝Replit 登入牆（Q19） |

- Phase 0 漂移處理修訂：三源不一致 → 回報差異 + **按「GitHub 為準」提出同步提案**（不再只是空等），實際同步動作仍需 Owner 指示。

### 6.6 Model Use Policy（三層分工）

1. **建造層（Claude Code session）**：寫代碼/測試/文件 → Sonnet；Opus 選配（Owner 極少用）。「升最強模型」的實際含義：先升環境內最強試一次；制度性/架構性問題 → **打包審查包（問題+失敗軌跡+選項）等 Owner 搬給 ChatGPT 5.5**，異步取回裁決。細則見 10 C8。
2. **Hermes 腦（runtime）**：GPT-5.5 → Minimax M3 → Deepseek v4 Pro，用量耗盡右移；**三腦同權**（Q20=A），不加降級規則。Blackboard 訊息記 `produced_by`（純來源記錄，不掛任何規則）。
3. **OpenClaw worker（執行層）**：做事的手；未來角色化多開（工程師/測試員/安審…），v1.2 後才擴。

- 高風險審查硬規則（Q17）：安全邊界/寫入路徑/執行閘/Owner 簽核前產物 → **≥2 個不同模型的審查員交叉審**，絕不指派單一 agent 或單一模型。見 20 R-13。

### 6.7 Blackboard Storage Decision（決策樹已走完）

```text
留言板存哪？→ repo 內 data/ 下 JSON 檔，隨 git 走（Q13=A）
  好處：一條管道（本機→GitHub→Replit）、git 歷史免費、Replit 拉取即更新
  代價：手機看到的 = 最後一次 push（顯示須帶時間戳）
升級條件（唯一）：多 worker 並行寫入頻繁衝突 → 屆時重問 Owner 是否升 SQLite（6.11）
在那之前：任何人提議換介質 → 預設否決（違反 Q1「保持簡單」）
```

### 6.8 First Real Write Gate（真實動作解鎖階梯）

| 版本 | 解鎖動作 | 前置條件 | rollback path |
|---|---|---|---|
| v1.0（Phase 9 N=1） | 無害查詢型 `openclaw agent` 調用，**零寫入** | Phase 3/4/5/7 完成 + Owner 在場 + 單次 token | 無需（無副作用） |
| v1.1 | repo 內測試檔**一次**真實寫入（全鏈路） | v1.0 簽核完成 + 新 packet/token | `git checkout`/`git revert`（標準答案） |
| v1.2 | 首次真實代碼任務（Owner 痛點場景第一次真演練） | v1.1 簽核完成 + 多審查員驗收 | git + 測試綠才算收工 |

- 每級解鎖都是**新的 Owner instruction**，不跨級繼承、不跨 session 繼承（01 §4 不變）。
- 任務三級分類（Q8，schema 欄位 `execution_class`，正式定義見 01 §6）：

```text
AUTO           唯讀/無害      Owner 批計劃後可自動並行（計劃級授權格式未定，見 6.11 OPEN）
OWNER_APPROVAL 會寫入/副作用   逐件送 Owner 批
OWNER_MANUAL   高風險（花錢/不可逆） 不進派工佇列；Hermes 在計劃中標記「這件 Owner 親自做」
```

### 6.9 Phase 2 Owner Decision Checklist（弱模型帶著 Owner 逐條簽）

Phase 2 執行時，向 Owner 逐條取得逐字簽核，全部完成才得產出 `02_V1_0_DEFINITION.md` 並宣告凍結：

```text
[ ] 1. v1.0 候選定義（6.3 全文）逐字接受？（含 Phase 9 併入 v1.0）
[ ] 2. 「包含」六項，各自的驗收方式逐項接受？
[ ] 3. 「不包含」各項的推遲去向（v1.1/v1.2/Phase 10）接受？
[ ] 4. 任務三級分類寫入 01 §6 接受？
[ ] 5. 02 文件內記錄簽核行：Owner approved on <date>, instruction quote: <逐字>
```

- 已預裁決（盤問時 Owner 口頭已答，Phase 2 只需正式化，不必重問）：Q4/Q5/Q8 的內容。若 Owner 在簽核時改主意，以新裁決為準並更新本節 6.0 表。

### 6.10 Phase 3–11 Adjustment Notes（對第 3 節的修訂，衝突時以本節為準）

- **Phase 3**：9 種 schema 新增欄位：`execution_class`（6.8）、`produced_by`（腦/模型來源，純記錄）、`parent_task_id`（任務拆解父子鏈）、`role`（worker 角色身份）。設計原則改為「**夠用就好**」（Q1）：先為單 worker 全鏈路 loop 設計；並行相關欄位只預留、不實作機制。
- **Phase 4**：審批包**對著 N=1 查詢型動作具體設計**，不做通用格式（Q5）；顯示區塊以手機畫面為目標（Q11）；裁決入口＝既存 `/dashboard/reviews` 按鈕（不新建入口）。
- **Phase 5**：證據包同樣聚焦 N=1 動作；通用化推遲到 v1.1。
- **Phase 6**：`/dashboard/reviews` 核准入口正式列入白名單管理；門檻維持 Replit 登入牆（Q19，Owner 已裁決，測試不需要求二次確認）。
- **Phase 7**：不變，仍在 v1.0 範圍內。
- **Phase 8**：**優先級上調**——手機是完成態主介面（Q11），Phase 8 是 v1.0 之後第一優先；方案已預定向：GitHub → Replit 單向拉取（Q12/Q13），顯示帶資料時間戳。
- **Phase 9**：併入 v1.0（Q4）；白名單動作已由 Owner 預指定＝無害查詢型調用（Q5），不再是「屆時指定」；「Owner 必須在場」維持。
- **Phase 10**：**無限期停留規劃**（Q3=C）；業務（pika/Vault）接入時才重啟，屆時先跑 6.11 的 Q16 重審。
- **Phase 11**：健檢新增必查項「本期間有無信任事故（越權/謊報/假驗收）」（Q6/Q17）；**不**新增省時統計、任務完成率等 metrics 機制（Q6 裁決成功指標＝信任感，不需儀表）。
- **Phase 0**：漂移處理按 6.5 修訂（GitHub 為準提案制）。

### 6.11 重審觸發器與 OPEN QUESTIONS

重審觸發器（觸發時弱模型必須停下重問 Owner，引用本節）：

```text
T1 他人個資（如 pika 客戶資料）將進入 Blackboard → 重問 Q16（三腦外送是否分級）
T2 /dashboard/reviews 核准按鈕第一次接上真實 dispatch → 重問 Q19（是否加二次確認）
T3 多 worker 並行寫入頻繁衝突 → 重問 Q13（是否升 SQLite）
T4 Hermes 腦供應商/條款變動 → 重問 Q16、Q20
```

OPEN QUESTIONS（Owner 尚未裁決，遇到即 HOLD）：

```text
O1 「計劃級授權」的正式格式未定義——Owner 批准 Hermes 切分計劃後，AUTO 級任務自動派發
   的授權要長什麼樣（一句話？簽核欄？）。首次多 worker 並行（v1.2 後）前必須定。
   在定義之前：AUTO 級任務照現行 01 §2/§4 逐字授權規則處理（fail closed）。
O2 角色化 worker（工程師/測試員/安審…）的角色定義與 prompt 由誰維護、存哪——v1.2 前定。
```

### 6.13 夜跑批次治理（2026-07-19 Owner 拍板，L0）

1. 夜跑長批單模式啟用：一單多包、包定義不可由執行者替換或自行加包、卡住標 skipped/HOLD 不硬猜、事後 Fable 5 一批審一次。
2. **免逐次蓋章**（Owner 2026-07-19 裁決「以後別蓋章、別有授權回覆」）：Fable 5 批審通過後**直接 merge/push、開下一批**，不再等 Owner 逐次確認。
3. 例外（維持不變，屬凍結計劃內建硬閘，非逐次蓋章）：Phase 7 首次寫入需 Owner 逐字授權句（本檔 Phase 7 節）；Phase 9 需 Owner 在場＋單次 token；v1.1/v1.2 各級解鎖需新的 Owner instruction（§6.8）。
4. Phase 8a 離線 projection contract 超包：Owner 2026-07-19 追認收下；後續批次禁止再自行加包。

### 6.12 Phase 3 施工期裁決（2026-07-18 Owner 親答，L0）

包1（Sol+xhigh 設計稿）觸發 fixture 矛盾 HOLD，Owner 裁決如下：

1. **`safety_flags` 正本＝16 面旗、巢狀 boolean object**：14 個共同鍵（synthetic_local_only／mock_only／dry_run／owner_review_required／external_side_effects_allowed／external_side_effects_occurred／blackboard_write_allowed／queue_write_allowed／audit_trail_write_allowed／worker_dispatch_allowed／openclaw_call_allowed／hermes_runtime_allowed／connector_call_allowed／google_sheets_write_allowed）＋ follow_up_allowed ＋ follow_up_requires_owner_confirmation。
2. RC-D fixture 的 17 鍵版（多 read_only／follow_up_task_creation_allowed／dashboard_controls_allowed）與 view model 的 `"key=value"` 字串陣列版一律降為**舊 fixture／顯示層投影**：不進新 schema、不改舊檔，validator 只驗新 contract。
3. 追認包1 設計的兩處泛化：公共欄位加 `message_type`、`created_at`（共 9 個公共欄位）；`role`＝產物作者的功能角色（不限 worker）。
4. 包2 交付方式：Codex 於 GitHub 開工作 branch＋PR（不碰 master），Fable 5 審＋本地實跑測試，Owner 按 merge。
