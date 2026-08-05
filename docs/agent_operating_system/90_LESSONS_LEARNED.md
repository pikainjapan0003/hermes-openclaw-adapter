# 90 踩坑紀錄（Lessons Learned）

- 回寫格式見 40_MAINTENANCE_PROTOCOL.md F3。超過 300 行時按 F4 精簡。
- 新案例往下追加，流水號遞增。

---

## L-009 Cross-platform fixture bytes and board-boundary tests

- Incident: fixture digest checks and filesystem-boundary tests can pass on one host while failing on another when line endings, hardlinks, symlinks, or non-regular files differ.
- Cause: hashing raw checkout bytes and treating host filesystem semantics as universal makes the contract depend on the runner rather than the fixture content.
- Rule: canonical fixture digest inputs normalize CRLF to LF; tests must state which filesystem cases are portable and which are skipped by capability. A board reader may report a shared inode for a hardlink, while any future writer must reject hardlinks and other ambiguous paths.
- Safety: malformed-input failures are structured and payload-free, and a platform-specific skip is never a silent acceptance of an unsafe path.
- Verification: run the fixture inventory, malicious-path boundary tests, and the full suite on both Windows and WSL before accepting a batch.

## L-001 host shell 可能在 wsl.exe 前先展開 `$`
- 日期：2026-06（回填），2026-07-07 由 Fable 5 收錄
- 任務：從 Windows 端 Bash/PowerShell 工具經 wsl.exe 跑 Linux 命令
- 症狀：`echo EXIT=$?`、`$VAR`、`$(...)` 在 wsl.exe 邊界被 Windows 端展開或吞掉，輸出為空或錯值
- 根因：變數在 Windows shell 層先被解析，到不了 WSL bash
- 缺的規則：跨 PowerShell→wsl.exe→Bash 時必須保護 Bash 程式不被 host shell 展開；不是全面禁止 Bash `$`
- 新增/修改的規則：PowerShell 呼叫 `bash -lc` 時把整段 Bash 程式置於 PowerShell 單引號中；簡單成敗判定仍優先用 00_QUICK_DIAGNOSIS.md D-16 的 `cmd && echo PASS || echo FAIL`
- 驗收：本 session 全程以該模式實跑無誤

## L-002 PowerShell 5.1 的 ConvertFrom-Json 對含跳脫序列的大 JSON 會炸
- 日期：2026-07-07
- 任務：解析 Google Drive search_files 落檔結果（71KB，含 `\\#` 等 markdown 跳脫）
- 症狀：`ConvertFrom-Json : Unrecognized escape sequence`
- 根因：Windows PowerShell 5.1 的 JSON 解析器不完全支援；且中文內容在 console 顯示為亂碼（編碼層問題，檔案本身正常）
- 缺的規則：大 JSON / 含非 ASCII 的解析不要用 PS 5.1
- 新增/修改的規則：JSON 解析改用 `python -c "import json; ..."` 並指定 `encoding='utf-8'`；一般 UTF-8 文字以 PowerShell 讀取時明示 `Get-Content -Encoding UTF8`，必要時同步設定 console output encoding，不把顯示亂碼誤判成檔案損壞
- 驗收：本 session 以 python 解析同檔成功列出 15 個項目

## L-003 UNC 路徑下 git 極慢，檔案讀寫卻可靠
- 日期：2026-07-07
- 任務：對 WSL 內 repo 同時做 git 操作與檔案讀寫
- 症狀：`\\wsl.localhost\...` 路徑下 git 命令延遲極高
- 根因：UNC 檔案協定逐檔往返，git 需大量 stat
- 缺的規則：工具選路規則
- 新增/修改的規則：00 D-16——git/測試/批量 shell 走 `wsl.exe -e bash -c "cd /home/... && ..."`；單檔讀寫用 Read/Write 工具走 UNC
- 驗收：本 session 兩種路徑並用，全部成功

## L-004 subagent 可以用 MCP Drive 與 Web 工具（本環境）
- 日期：2026-07-07
- 任務：派 general-purpose subagent 讀 Drive 全文與做 web 查證
- 症狀：（無錯誤——這是正向確認）
- 根因：general-purpose 工具集為 `*`，含 MCP
- 缺的規則：C0 環境快照當時不存在
- 新增/修改的規則：10_MODEL_ORCHESTRATION.md C0；注意：其他環境（API 直連、OpenClaw gateway）不保證成立，須重驗
- 驗收：兩個 subagent 均成功回報（Drive 三文件全文、8 項 web 查證）

## L-005 制度初稿經 adversarial review 抓出 18 個缺陷（含 2 HIGH）
- 日期：2026-07-07
- 任務：Fable 5 撰寫本制度全套文件後，派 fresh-context subagent 對抗審查
- 症狀：初稿含互相打架的規則（「既有慣例」變相授權寫入 vs R-06 逐字授權）、錯誤統計數字（憑一次 `ls | wc -l` 把 209 個檔案當成 209 個 check script，實為 157）、以及把「計劃表允許實作」欄寫成會被誤讀為授權的形式
- 根因：產出者自己 read-back 看不出自己的語意盲點；「已驗證」標記下藏著推論而非實測
- 缺的規則：無（R-09/T-07 正是為此而設，本次證明有效）
- 新增/修改的規則：僅記錄——所有 findings 已逐項修入各檔。教訓：制度文件本身也必須走 T-07，不能因為「是安全文件」就豁免審查
- 驗收：修復後由另一 fresh-context read-back 核對（見本 session 最終回報）

## L-006 Replit 登入後 dashboard 有 Owner 核准/拒絕按鈕（既存事實，非新增）
- 日期：2026-07-07（Owner 提供登入後截圖確認）
- 任務：驗證 Replit dashboard 唯讀狀態
- 症狀：`/dashboard/reviews` 存在「核准 Approve」「拒絕 Reject」按鈕與拒絕原因輸入框——登入後的 dashboard 並非純 display，含 Owner 審核控制（v0.7.x 時期建立，早於本制度）。頁面同時標示 `dispatch_allowed = False`、`execution_permission = False`、「Owner 核准不等於 Worker 執行」
- 根因：v0.7 系列曾授權建立 Owner 審核面板；後續文件慣用「dashboard 是 read-only display」的簡化說法，未區分「queue 資料唯讀」與「有審核決策入口」
- 缺的規則：01/05 描述 dashboard 時應寫明例外：登入牆後有 Owner-only 審核控制（approve/reject 決策記錄），但 decision ≠ dispatch
- 新增/修改的規則：已補記於 05 §1 與 §2.1/2.2；Phase 6 唯讀硬化已把 reviews 頁的既有審核 POST 列入白名單，並以測試驗證其僅寫 decision event、不觸發 dispatch
- 驗收：Owner 截圖存證；Phase 6 測試已確認 approve 不產生 dispatch（完成狀態見 05 §5）

## L-007 二次補強整包只寫入 Drive 鏡像、未進 repo（三次漂移同根因）
- 日期：2026-07-18（Fable 5 健檢發現；漂移發生於 2026-07-08）
- 任務：v1.0 定義凍結前制度健檢（全檔 diff 鏡像 vs repo）
- 症狀：repo 缺 10 C8、05 §6（165 行）、01 §6、20 R-13、README 定位段、99 交接更新——全部只存在於 Desktop\Hermes_OpenClaw_Drive_Upload 鏡像；「GitHub 為王」名存實亡（較新內容在鏡像）
- 根因：2026-07-08 二次補強 session 直接編輯鏡像資料夾，未改 repo 正本；且無任何規則定義正本/鏡像關係與同步方向
- 缺的規則：「正本只在 repo、鏡像單向覆蓋、鏡像禁直改」當時不存在
- 新增/修改的規則：40 F6 鏡像管理（Owner 拍板 2026-07-18）；缺件已全數回填 repo（10 C8 與 05 §6 於本日稍早 commit，01 §6/20 R-13/README/99 隨本筆）
- 驗收：全 11 檔鏡像 vs repo diff 歸零＋fresh-context read-back

## L-008 rollback E 規格與 bundle contract 脫節
- 日期：2026-07-19
- 任務：Phase 7 rollback preview builder 的跨 contract 輸入與欄位來源設計
- 症狀：初版設計要求從 evidence bundle 比對 `safety_flags`、`parent_task_id`、`result_id`，但實際 evidence bundle schema 與正例 fixture 均無這些欄位，規格因此無法機械驗證並觸發 HOLD
- 根因：設計裁決引用了不存在的欄位，未先 dump／grep 實際 schema 與 fixture，便從相鄰 Blackboard contract 推定 bundle 也有同名欄位
- 缺的規則：跨 contract 欄位比對的設計，落筆前必須逐欄位 grep 實際 schema／fixture，並在設計文件附欄位存在性清單
- 新增/修改的規則：已寫入 07 §6.3；欄位不存在或來源矛盾時必須 HOLD，不得自行補 schema／fixture
- 驗收：NIGHT-BATCH-5 包1完成 B 案三輸入設計與存在性清單；包2完成純函式 builder，正例過 `rollback_event` schema 且 fail-closed 反例全綠

## L-010 自報 `git diff --check` 與獨立實測不一致

- 日期：2026-08-01
- 任務：夜跑 package 的 whitespace/diff acceptance evidence
- 症狀：Codex 自報 `git diff --check` 無輸出，Fable 5 在待審 branch 的實際狀態重跑卻得到一行輸出；「綠」的文字主張與可重算證據不一致
- 根因：自報命令可能未實跑，或跑在不同 checkout／HEAD／編輯狀態；回報只寫結論，未貼 stdout/stderr 與被檢查狀態，因此無法追溯
- 缺的規則：逐 package 的 diff-check 原始輸出與 active-checkout/state 證據
- 新增/修改的規則：40 F7 第 5 條；每包在編輯完成、commit 前於 authorized checkout 實跑 `git diff --check`，逐包回報原文。空輸出也必須明寫 `（無輸出；exit 0）`，不得用「已確認」代替
- 驗收：NIGHT-BATCH-19 的 done/HOLD/skipped 逐包回報都附該包 `git diff --check` 原文；Fable 5 必須在同一待審 branch 獨立重跑，不沿用 Codex 自報數字

## L-011 路徑間接不等於逃逸：邊界必須寫成可機械檢查的不變式

- 日期：2026-08-02
- 任務：Blackboard reader 的 hardlink、board-root symlink 與板內逃逸邊界
- 症狀：批單三度把 hardlink 或 caller-selected root symlink 直接等同「逃出板面」，造成兩次不必要的 HOLD；實際上 root 是呼叫端指定的信任錨點，而板內 symlink 才能把 entry 解析到錨點外。
- 根因：規格只寫自然語言「永不逃出板面目錄」，沒有先定義 root、entry 與解析後路徑之間的可判定關係。
- 缺的規則：任何路徑邊界都必須一次寫成可機械檢查的不變式，不能用「間接」「外部」等含糊詞推定危險。
- 新增/修改的規則：40 F7 第 2 條——先取 `R = realpath(root)`；root 本身可以是呼叫端指定的 symlink；每個 entry 的 `realpath` 必須位於 `R` 之下，板內 symlink 一律在讀取前拒絕。reader 可接受 hardlink 並標 `shared_inode=true`，未來 writer 仍必須拒絕 `st_nlink > 1`。
- 驗收：NIGHT-BATCH-20 包3 的 root-symlink、板內 symlink、相對 `../` 逃逸、hardlink、FIFO、socket 與 device 邊界測試全綠或依主機能力明示 skip；沒有修改 reader 行為。

## L-012 派工方未自檢跨 contract 欄位存在性（L-008 的再犯）

- 日期：2026-08-04
- 範圍：NIGHT-BATCH-20 package 10 的 approval packet／evidence bundle 交叉不變式
- 症狀：派工單要求兩個 builder 產物共享 `task_id`、`schema_version`、`safety_flags`、`execution_class`，但實際 evidence bundle contract 沒有 `safety_flags`；package 只能 HOLD。
- 根因：派工方在下單前沒有先 dump／grep 實際 schema 與 fixture，直接把推測中的共同 shape 寫成機械驗收事實。
- 缺的規則：L-008 只約束設計與實作者檢查欄位存在性，沒有要求派工方在派出 contract-field package 前附實物證據。
- 新增規則：40 F8；任何依賴 contract 欄位的派工包，派出前都必須附欄位到實際 schema／fixture 的 file:line 證據，證據缺漏則該包不得派出。
- 驗收：NIGHT-BATCH-21 package 0 已先產 contract/spec precheck；下一批不得再出現同型 HOLD。

## L-013 防錯規則本身太窄：F8 只管欄位

- 日期：2026-08-02
- 範圍：NIGHT-BATCH-21 package 5 的 schema-keyword 主張與 package 10 的行為前置主張
- 症狀：package 5 的 `allOf` 缺席主張與 package 10 的 detached／shallow fail-closed 主張都未被 F8 或 precheck 攔下，兩包最後只能 HOLD。
- 根因：F8 只要求 contract 欄位存在性證據，沒有涵蓋 schema keyword 的存在／缺席，也沒有涵蓋工具或模組行為前置。
- 缺的規則：派工前的事實查證不能只掃欄位名稱；schema 組合語義與行為前置同樣必須有實際 file:line 證據。
- 新增規則：40 F8 擴為三類——欄位存在性、schema keyword 存在／缺席、行為前置主張；任一類缺證據即不得派出。
- 驗收：本批 package 0 型自檢覆蓋三類；下一批不得再出現同型 HOLD。

## L-014 派工方 commit 純文件後未重跑套件，把紅的 master 推上遠端

- 日期：2026-08-05
- 範圍：`3addbe6`（NIGHT-BATCH-26 findings 登記）到 `6ee2f57`（修復）
- 症狀：登記 backlog 時，把「Fable 5 的第 5 號 finding」寫成了 F 家族規則同形狀的
  識別碼（大寫 F、連字號、數字 5）。`tests/test_cross_reference_integrity.py` 的
  `TOKEN_RE` 會把 `docs/agent_operating_system/` 內所有該形狀的字串當成指向
  `40_MAINTENANCE_PROTOCOL.md` 的 F 家族制度規則參照；該檔並未定義該編號，
  判為懸空引用，`test_every_governance_reference_has_an_authority_definition` 變紅。
  commit 後未重跑套件即 push，紅的 master 在遠端擺了約一天，
  由下一批的執行者在派工單外自行發現並修補，反而製造包界線爭議。
- 根因：把「重跑完整套件」的觸發條件內化成「有改程式才要跑」。但本 repo 的
  治理測試會讀 `docs/` 內容，**文件本身就是被測對象**；純文件 commit 一樣會使套件變紅。
- 缺的規則：F5 修改流程未明寫「純文件變更也必須在 commit 前跑完整套件」，
  也未提醒制度檔內不得出現與規則代號同形狀的自由文字。
- 新增規則：
  1. **任何 commit 前都必須跑完整套件，不分程式或文件**；push 前必須綠。
  2. `docs/agent_operating_system/` 內的自由文字**不得使用與制度規則同形狀的識別碼**
     （`F-?\d+`、`R-?\d+`、`L-?\d+` 等）。指稱審查 finding 一律寫
     `finding N`，不得寫 `F-N` 或 `FN`。
  3. 若必須在批次內修補基線自身的缺陷，該修補應獨立成一個標明「基線缺陷修補」
     的 commit，不得默默併入其他包，以免包界線審查產生歧義。
- 驗收：`6ee2f57` 修復後 `test_cross_reference_integrity.py` 3 passed、完整套件
  `2452 passed`；NIGHT-BATCH-27 登記時六處 finding 標籤全數改用 `finding N` 措辭，
  `grep -nE 'F[0-9]|F-[0-9]' ` 對新增段落零命中。
