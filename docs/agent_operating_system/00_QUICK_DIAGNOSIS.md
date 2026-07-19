# 00 快速診斷（Quick Diagnosis）

- 撰寫：Fable 5 replanning session（2026-07-07）
- 讀者：未來較弱模型（Sonnet / Haiku / API 調用模型）與 Owner
- 依據（已驗證）：本機 repo `HEAD=7a93127e`（與 GitHub live HEAD 一致）、`CLAUDE.md` Loop Format Contract、既有 docs 166 份、scripts/ 209 個檔案（其中 157 個 `check_*.py`）、Drive《開發總結報告 v1.0 / v0.9.5–v0.9.6》全文、Replit `/dashboard/system` 實際抓取
- 本檔用途：列出目前 harness（ChatGPT 出指令 → Claude Code 執行 → Owner review 的 loop）最漏 token、最易失焦、最易出錯的問題，每項附具體修法與弱模型可執行的檢查法。後續所有制度檔都引用本檔的問題編號（D-xx）。

---

## 1. 三份排行榜

同一問題可能同時上多榜。細節見第 2 節的問題卡（依 D-xx 編號查找，只寫一次，不重複）。

### 1.1 最漏 token 前十名

| 排名 | 編號 | 問題 |
|---|---|---|
| 1 | D-01 | 每份 phase 文件重複整套安全聲明（166 份 docs × 約 20 條 litany） |
| 2 | D-02 | 每個 phase 一個 check script（157 個），大量重複樣板 |
| 3 | D-03 | Owner instruction 每次重貼完整背景與歷史 |
| 4 | D-06 | 主模型親自掃 repo、讀長文件、逐字比對 |
| 5 | D-04 | docs/ 無索引摘要層，找一份文件要列 167 個檔名 |
| 6 | D-05 | 無 routing：每個新 session 重新解釋系統背景 |
| 7 | D-17 | phase 命名密集（v0.7.2-F-C-R 這類），指令內反覆全名引用 |
| 8 | D-13 | 無 context emergency protocol，快滿時還在產出長文 |
| 9 | D-11 | 無查證規則，模型用長篇「推測」代替一次查證 |
| 10 | D-16 | WSL/Windows 混合環境踩坑重試，同一錯誤反覆燒 token |

### 1.2 最容易失焦前十名

| 排名 | 編號 | 問題 |
|---|---|---|
| 1 | D-17 | phase 名稱又長又像，弱模型抓錯 phase |
| 2 | D-03 | phase 指令過長，主線淹沒在背景裡 |
| 3 | D-05 | 無 routing，session 開頭花大量往返對齊背景 |
| 4 | D-04 | 無摘要層，模型讀錯版本的文件當成現況 |
| 5 | D-13 | context 快滿時沒有收尾優先序，斷在半成品 |
| 6 | D-06 | 主模型下場做工人活，忘記自己的驗收職責 |
| 7 | D-14 | 沒有踩坑回寫，同樣的岔路每個 session 都重走 |
| 8 | D-10 | connector 權限語意模糊，討論發散成猜測 |
| 9 | D-12 | 三源（local/GitHub/Replit）狀態未對齊就開工 |
| 10 | D-15 | 無升降級規則，弱模型卡死在同一題反覆重試 |

### 1.3 最容易出錯前十名

| 排名 | 編號 | 問題 |
|---|---|---|
| 1 | D-07 | 驗收依賴同一模型自驗（check script 由寫文件的同一 session 產生，且多為字串存在檢查） |
| 2 | D-08 | Dashboard display 被誤認為 execution permission |
| 3 | D-09 | mock / dry-run / real 邊界只靠文件記憶，無命名與程式層防呆 |
| 4 | D-11 | 沒查證就憑印象回答（編造 repo、模型名、API 行為） |
| 5 | D-12 | 本機 / GitHub / Replit 狀態不一致時照舊執行 |
| 6 | D-10 | connector 權限模糊，容易「順手」讀了 metadata |
| 7 | D-16 | WSL `$` mangling、PowerShell 5.1 限制等環境陷阱 |
| 8 | D-15 | 小模型連錯不升級，錯誤累積成災 |
| 9 | D-14 | 踩坑不回寫，修過的坑再踩 |
| 10 | D-18 | 長 Owner prompt 尾部截斷，漏掉 EXPECTED-LAST-LINE 之後的關鍵約束 |

---

## 2. 問題卡（每項含修法、檢查法、正例、反例）

### D-01 安全聲明全文重複於每份 phase 文件

- 症狀：166 份既有 docs 幾乎每份都全文重抄「No Blackboard write / No Worker dispatch / ...」約 20 條。每次讀文件都重複消耗 token，且抄寫時容易漏條或改字，造成版本漂移。
- 修法：以 `docs/agent_operating_system/01_SAFETY_BOUNDARIES.md` 為唯一正本（canonical）。新 phase 文件只寫一行：`本 phase 遵守 01_SAFETY_BOUNDARIES.md 全部規則，無新增豁免。` 只有「本 phase 特有」的邊界才展開寫。舊文件不回頭改（歷史紀錄保持原樣）。
- 弱模型檢查法：新增 phase 文件前，grep 該文件是否含 `01_SAFETY_BOUNDARIES.md` 字樣；若同時又全文重抄超過 5 條 litany，判定違規，改為引用。
- 正例：`## 安全邊界\n本 phase 遵守 01_SAFETY_BOUNDARIES.md 全部規則。本 phase 特有限制：fixture 僅允許讀取 fixtures/local_mock_data/。`
- 反例：把 20 條 litany 全文貼進新文件第 9、12、13、18、19 節各一次（v1.0-RC-R closeout 舊格式）。

### D-02 每 phase 一個 check script，大量重複樣板

- 症狀：scripts/ 有 209 個檔案，其中 157 個 `check_*.py`，多數只驗證「文件裡存在某些字串」。維護成本高、真實防護力低（字串在≠行為對）。
- 修法：新 phase 不再產生一次性 check script，改用兩層驗收：(1) 通用 read-back 驗收（見 `10_MODEL_ORCHESTRATION.md` C6）；(2) 涉及程式行為時用真測試（pytest / smoke test / 實跑 route）。既有 157 個 check script 保留不動（歷史證據），但不再作為新 phase 的驗收標準。
- 弱模型檢查法：若你正要寫一個「檢查文件是否包含某段字」的新 script，停下來——改用 read-back 驗收模板。只有「檢查程式行為」的 script 才值得新寫。
- 正例：v1.0-A 驗收 = `pytest tests/test_blackboard_schemas.py`（未來檔案，tests/ 目錄屆時新建）+ fresh-context read-back。
- 反例：`check_v1_0_a_plan.py` 內容是 20 行 `assert "No Worker dispatch" in text`。

### D-03 Owner instruction 每次重貼完整背景

- 症狀：每輪 ChatGPT 指令重複解釋系統架構與歷史，phase 主線被淹沒；長 prompt 也加大 D-18 截斷風險。
- 修法：Owner instruction 只需包含 CLAUDE.md 第 6 節要求的框架（`[PHASE]`、`[EXPECTED-LAST-LINE]`、唯一授權任務）加「本輪特有」的差異資訊。背景一律以一行引用代替：`背景見 docs/agent_operating_system/05_VERIFIED_LONG_TERM_PLAN.md 對應 Phase。`
- 弱模型檢查法：收到指令後，先讀被引用的 Phase 章節，再開工。若指令與計劃表衝突，以指令為準但在回報中標註衝突。
- 正例：`[PHASE] v1.0-A\n背景與驗收見 05_VERIFIED_LONG_TERM_PLAN.md Phase 3。本輪差異：schema 欄位 X 改為 optional。`
- 反例：指令前 60 行重述 v0.5 到 v1.0-RC 全部歷史。

### D-04 docs/ 無索引摘要層

- 症狀：README 21KB、既有 docs 166 份平鋪，弱模型找現況要靠檔名猜，常讀到過期版本文件當成現況。
- 修法：`docs/agent_operating_system/README.md`（本資料夾索引，已建立）作為入口；現況只認 `05_VERIFIED_LONG_TERM_PLAN.md` 第 5 節狀態表。最新正式 closeout 文件仍是 `docs/HERMES_FULL_BLACKBOARD_LOOP_REHEARSAL_CLOSEOUT_V1_0_RC_R.md`，但它只代表過去 closeout，不覆蓋其後已落入 05 第 5 節的 Phase 實況。其餘既有 docs 一律視為歷史紀錄，除非被指名，不要主動讀。
- 弱模型檢查法：開工前只讀三份：CLAUDE.md → agent_operating_system/README.md → 計劃表對應 Phase。讀第四份前先問自己「指令有指名它嗎」。
- 正例：被要求了解現況 → 讀計劃表 Phase 0 的「目前系統狀態」節，5 分鐘完成。
- 反例：把 docs/ 下 167 份全部 glob 出來逐一略讀「以求完整」。

### D-05 無 routing 導致每次重新解釋背景

- 症狀：新 session 開頭平均花大量往返讓模型「進入狀況」。
- 修法：CLAUDE.md 末尾加一段固定路由（本次 session 已加）：任何 session 第一步 = 讀 `docs/agent_operating_system/README.md`。
- 弱模型檢查法：如果你發現自己在沒有讀過 agent_operating_system/README.md 的情況下開始執行任務，停下來先讀它。
- 正例：session 開場三步：CLAUDE.md → README.md（本資料夾）→ 指令指定的 Phase。
- 反例：直接根據 Owner 一句話開始改檔案。

### D-06 主模型親自做大量讀取與掃 repo

- 症狀：commander 模型把 context 花在讀 167 份文件、掃 209 個 script、逐字 diff，導致後段驗收與決策時 context 已殘破。
- 修法：見 `10_MODEL_ORCHESTRATION.md` C1「指揮官不下場」。大量讀取一律派 Explore/general-purpose subagent，只回結構化摘要與 `檔案:行號`。
- 弱模型檢查法：動手前估算——若需要開超過 5 個檔案或讀超過 500 行，就派 subagent；若無 subagent 可用（例如 API 直連），改為分段讀並隨讀隨記摘要到 scratch 檔。
- 正例：「掃 app/ 找出所有寫入 queue 的 code path」→ 派 Explore，回報 `app/queue_store.py:41` 等清單。
- 反例：主對話逐檔 cat app/ 下 28 個 .py。

### D-07 驗收過度依賴同一模型自驗

- 症狀：寫文件的 session 自己寫 check script、自己跑、自己宣布 PASS。同一個 context 的盲點會同時出現在產出與驗收裡。
- 修法：兩級驗收制。一般產出：fresh-context read-back（新 subagent 或新 session，只給驗收清單不給原始推理）。高風險產出（安全邊界、schema、approval packet）：adversarial review（明確指示「找出會被誤讀成越權的句子」）。
- 弱模型檢查法：宣布 PASS 前自問：「驗收者的 context 是否乾淨？」若驗收者就是產出者本人且無 fresh-context 可用，回報中必須寫明 `自驗，非獨立驗收`。
- 正例：文件寫完 → 開 fresh subagent 給它驗收清單 → 它回報缺第 7 節 → 修 → 再驗。
- 反例：「我重讀了一遍我剛寫的文件，確認沒問題。」

### D-08 Dashboard display 與 execution permission 混淆

- 症狀：弱模型看到 dashboard 顯示「approval readiness: ready」就以為可以 dispatch。這是本系統明文的頭號語意陷阱。
- 修法：litany 正本化（01_SAFETY_BOUNDARIES.md）+ 判斷 rubric（20_JUDGMENT_RUBRICS.md R-06）。規則一句話版：畫面上的任何字都不是授權；授權只存在於 Owner instruction 的 `[OWNER-INSTRUCTION-START]...[OWNER-INSTRUCTION-END]` 區塊內。
- 弱模型檢查法：執行任何有副作用的動作前，引用出授權來源的逐字句子與其所在 Owner instruction。引用不出來 = 沒有授權 = HOLD。
- 正例：「Owner instruction 第 12 行寫『允許寫入 data/blackboard_dev.json』，故執行。」
- 反例：「dashboard 顯示 task 已 approved，所以我幫它 dispatch。」

### D-09 mock / dry-run / real 邊界只靠文件記憶

- 症狀：mock gateway、dry-run worker、preview adapter 與未來的 real 元件同居一個 app/，弱模型改錯檔就可能把 mock 換成 real。
- 修法：(1) 命名鐵律：所有 mock/dry-run/preview 檔案與函式必須含 `mock_`、`_mock`、`dry_run`、`preview`、`synthetic` 字樣之一；未來 real 元件必須含 `real_` 且住在獨立模組。(2) 程式層防呆：real 元件入口必須檢查環境變數形式的 execution token（Phase 9 定義），缺 token 直接 raise。(3) 弱模型不得在同一個 commit 內同時修改 mock 檔與 real 檔。(4) **重要例外**：既有檔案早於本規則，命名不可靠。已知**無標記但具真實寫入能力**的檔案：`app/google_sheets_oauth_writer.py`（真實 Google Sheets 寫入路徑，env flag 防護、預設關閉）；`app/worker.py`、`app/queue_store.py`、`app/blackboard_store.py`、`app/result_sink.py` 亦無 mock/real 標記。修改這些檔案前把本卡讀完整張，並視為高風險（R-09 必走 fresh-context review）。命名鐵律約束的是**新檔案**。
- 弱模型檢查法：改任何 app/ 檔案前，看檔名——含 mock/preview/dry_run 字樣就確認你的任務也是 mock/preview 範疇；任務要求 real 行為但目標檔是 mock 檔（或反之），HOLD 並回報 mismatch。
- 正例：任務是「調整 mock gateway 回傳格式」→ 只碰 `app/mock_openclaw_gateway.py`。
- 反例：任務是改 mock，順手把 `worker.py` 裡的 dry-run flag 預設值改成 False。

### D-10 connector 權限過度模糊

- 症狀：「connector preview」「metadata read」「content read」「write」四級語意不同，但指令常只說「試一下 connector」。v0.9.5 只授權了 L0（documentation-only）。
- 修法：任何 connector 動作必須有 explicit scope packet（Phase 10 定義 schema：connector 名、允許動作級別 L0/L1/L2/L3、目標資源清單、有效期）。沒有 scope packet，一律當 L0。
- 弱模型檢查法：指令含 connector 而不含 scope packet → 回覆「connector scope packet missing, defaulting to L0 (documentation-only), HOLD for packet」。
- 正例：收到 scope packet 授權 L1 metadata read on Google Sheet X → 只讀 metadata，不讀內容。
- 反例：「Owner 叫我看看那個 sheet 能不能連」→ 直接讀了整張表內容。

### D-11 沒有 freshness / web verification 規則

- 症狀：模型憑訓練記憶回答「某 repo 有某功能」「某 API 這樣用」，事後發現是編造。弱模型此缺陷更嚴重。
- 修法：三類主張必須先查證再寫：(1) 外部 repo/工具/API 的存在與行為；(2) 模型名稱與參數；(3) 任何日期敏感資訊。查證手段：WebSearch/WebFetch/實跑命令。查不到就寫 `無法驗證`，禁止補白。
- 弱模型檢查法：寫下任何含專有名詞的外部主張前自問：「這句話的來源是本 session 的哪一次工具呼叫？」答不出來就刪掉或標 `無法驗證`。
- 正例：「LangGraph interrupt() 支援 human-in-the-loop（來源：本 session WebFetch 官方文件）」。
- 反例：「AutoGen 上個月剛加了 blackboard 模式」（沒有任何工具呼叫支撐）。

### D-12 沒有 repo / GitHub / Replit 一致性檢查

- 症狀：本機改了沒 push、Replit 跑的是舊版、GitHub 是唯一 remote——三者漂移時，針對錯誤狀態做的決策全部作廢。
- 修法：每個 session 開工前跑三源檢查（一條命令，見下）；結果不一致時先回報差異，等 Owner 決定同步方向，不要擅自 push/pull/redeploy。
- 弱模型檢查法（Windows host 端可直接複製執行；已在 WSL 內則去掉外層 wrapper 只跑引號內命令）：
  ```bash
  wsl.exe -e bash -c "cd /home/lnovo/projects/hermes-openclaw-adapter && git status --short && git log --oneline -1 && git ls-remote origin master"
  ```
  比對本機 HEAD 與 `ls-remote` hash；再開 `https://hermes-openclaw-adapter.replit.app/dashboard/system` 確認 HTTP 可達。此檢查不取得 Replit deployed hash，故只能證明 local/GitHub hash 是否一致及 Replit 是否可達，不得宣稱三個 revision 一致。
- 正例：發現本機 ahead 2 commits → 回報「local ahead of origin by 2, HOLD for push decision」。
- 反例：假設 origin 一定和本機一樣，直接在計劃裡引用本機才有的檔案路徑要 Replit 讀。

### D-13 沒有 context 快滿時的 emergency protocol

- 症狀：session 尾聲 context 將盡，模型還在產出新內容，最後截斷在半成品，下個 session 無從接手。
- 修法：見 `99_LETTER_TO_FUTURE_SESSIONS.md` 第 4 節。優先序鐵律：察覺 context 吃緊時，立刻停止新產出，依序做 (1) 把已完成事項與未完成清單落檔 (2) read-back 已落檔項 (3) 一段式總結。落檔的才算存在。
- 弱模型檢查法：每完成一個交付物立即寫檔（隨做隨寫），任何時刻中斷都只損失當前一項。
- 正例：完成 3/7 份文件時中斷 → 3 份已在磁碟上，信裡有剩餘 4 份的規格。
- 反例：七份文件全部寫在回覆草稿裡打算最後一起落檔。

### D-14 沒有踩坑回寫協議

- 症狀：WSL `$` mangling 這類坑，每個新 session 重新踩一次。
- 修法：`90_LESSONS_LEARNED.md` + `40_MAINTENANCE_PROTOCOL.md` F3 格式。踩坑修復後 5 分鐘內回寫，含觸發條件與繞法。
- 弱模型檢查法：任何錯誤重試成功後，自問「同樣錯誤下個 session 會不會再犯？」會 → 回寫一條。
- 正例：發現 `wsl.exe` 吃掉 `$?` → 回寫「用 `cmd && echo PASS || echo FAIL` 代替」。
- 反例：默默換個寫法繼續，坑留給下一位。

### D-15 沒有模型升降級規則

- 症狀：便宜模型在超出能力的任務上重試到天荒地老；或強模型做批次體力活浪費成本。
- 修法：見 `10_MODEL_ORCHESTRATION.md` C5。一句話版：小模型錯一次就升級；同一子任務連錯兩次帶失敗軌跡升級;最多重試兩輪，第三次換路線或問 Owner。
- 弱模型檢查法：每次重試前數一下這是第幾次。第 3 次 = 禁止重試。
- 正例：Haiku 寫 schema 驗證器失敗一次 → 直接升 Sonnet 帶著失敗 diff 重做。
- 反例：同一個 import error 用五種姿勢重試五次。

### D-16 WSL / Windows 混合環境陷阱

- 症狀：本專案跨 Windows（Claude Code host）與 WSL Ubuntu（repo 所在）。已知坑：(1) Bash-tool→wsl.exe 會吃掉 `$?`/`$VAR`/`$(...)`；(2) PowerShell 5.1 無 `&&`、`ConvertFrom-Json` 對某些 escape 會炸；(3) UNC 路徑 `\\wsl.localhost\...` 下 git 操作極慢，git 一律進 WSL 內跑。
- 修法：固定命令模式：`wsl.exe -e bash -c "cd /home/lnovo/projects/hermes-openclaw-adapter && <cmd>"`，命令內不用 `$` 變數，成敗用 `&& echo PASS || echo FAIL` 表達。檔案讀寫用 Read/Write 工具走 UNC 路徑（可靠），shell 命令走 wsl.exe（快）。
- 弱模型檢查法：wsl.exe 命令含 `$` 字元 → 改寫。PowerShell 中用了 `&&` → 改成 `if ($?)` 或分開呼叫。
- 正例：`wsl.exe -e bash -c "cd /home/... && python -m pytest -q && echo PASS || echo FAIL"`
- 反例：`wsl.exe -e bash -c "echo EXIT=$?"`（$? 會被 Windows 端吃掉）。

### D-17 phase 命名密集導致抓錯 phase

- 症狀：`v0.7.2-F-C-R`、`v1.0-RC-D` 等名稱一字之差意義完全不同，弱模型容易執行到相鄰 phase。CLAUDE.md 已有 phase lock 規則，但缺「怎麼核對」的具體法。
- 修法：執行前把指令中的 `[PHASE]` 逐字複製到回報開頭；比對目標文件檔名中的 phase 字串與 `[PHASE]` 完全一致（大小寫、連字號、字母序）才動手。另注意：`[PHASE]` 用版本序（v1.0-A 等），計劃表用 Phase 0–11，是**兩套命名**；instruction 必須寫明對應（例：`[PHASE] v1.0-A（計劃表 Phase 3）`），未寫明 → 問 Owner，不得自行推斷。檔名比對僅適用於會建立 phase 命名檔案的任務。
- 弱模型檢查法：`[PHASE]` 字串是否為你將建立/修改的檔名的子字串（正規化底線/連字號後）？不是 → 停，回報 `Source phase mismatch; stopped before execution.`
- 正例：`[PHASE] v1.0-A` → 檔名 `..._V1_0_A.md` → 一致 → 執行。
- 反例：`[PHASE] v1.0-RC-E` 卻去改 `..._V1_0_RC_D.md`「因為看起來是同一件事」。

### D-18 長 Owner prompt 尾部截斷

- 症狀：貼上超長指令時尾部丟失，最重要的約束（通常在最後）不見了。CLAUDE.md 第 6 節已要求檢查最後 300–500 字完整。
- 修法：維持 CLAUDE.md 規則，外加：`[EXPECTED-LAST-LINE]` 之後不得再有任何約束性內容（結構性保證，讓截斷必然可偵測）。
- 弱模型檢查法：確認指令實際最後一行 == `[EXPECTED-LAST-LINE]` 宣告的字串。不等 → `Owner instruction format incomplete; stopped before execution.`
- 正例：宣告的 last line 出現且其後無正文 → 通過。
- 反例：宣告的 last line 沒出現，模型「大概懂了」就開工。

---

## 3. 現況中已經做對的事（不要破壞）

1. Phase lock + Owner instruction boundary（CLAUDE.md）— 已阻止過自動延伸任務，保留。
2. 安全 litany 的語意設計（「X is not Y」句式）— 對抗過度服從非常有效，正本化後繼續用。
3. GET-only dashboard、mock gateway、synthetic fixture 的分層 — 邊界物理上存在，不只是文件。
4. 每 phase 有 closeout 文件 — 歷史可追溯。問題只在重複（D-01）與自驗（D-07），不在制度本身。
5. 繁體中文說明 + 英文技術詞的雙語慣例 — 保留。
