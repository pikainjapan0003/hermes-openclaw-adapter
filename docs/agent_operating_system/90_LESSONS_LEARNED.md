# 90 踩坑紀錄（Lessons Learned）

- 回寫格式見 40_MAINTENANCE_PROTOCOL.md F3。超過 300 行時按 F4 精簡。
- 新案例往下追加，流水號遞增。

---

## L-001 wsl.exe 會吃掉 $ 變數
- 日期：2026-06（回填），2026-07-07 由 Fable 5 收錄
- 任務：從 Windows 端 Bash/PowerShell 工具經 wsl.exe 跑 Linux 命令
- 症狀：`echo EXIT=$?`、`$VAR`、`$(...)` 在 wsl.exe 邊界被 Windows 端展開或吞掉，輸出為空或錯值
- 根因：變數在 Windows shell 層先被解析，到不了 WSL bash
- 缺的規則：wsl.exe 命令內禁用 `$`
- 新增/修改的規則：00_QUICK_DIAGNOSIS.md D-16——成敗判定用 `cmd && echo PASS || echo FAIL`
- 驗收：本 session 全程以該模式實跑無誤

## L-002 PowerShell 5.1 的 ConvertFrom-Json 對含跳脫序列的大 JSON 會炸
- 日期：2026-07-07
- 任務：解析 Google Drive search_files 落檔結果（71KB，含 `\\#` 等 markdown 跳脫）
- 症狀：`ConvertFrom-Json : Unrecognized escape sequence`
- 根因：Windows PowerShell 5.1 的 JSON 解析器不完全支援；且中文內容在 console 顯示為亂碼（編碼層問題，檔案本身正常）
- 缺的規則：大 JSON / 含非 ASCII 的解析不要用 PS 5.1
- 新增/修改的規則：僅記錄——改用 `python -c "import json; ..."` 指定 `encoding='utf-8'`，一次成功
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
- 新增/修改的規則：已補記於 05 §1 與 §2.1/2.2；Phase 6 唯讀硬化測試屆時必須把 reviews 頁的既有審核 POST 列入白名單並驗證其僅寫 decision event、不觸發 dispatch
- 驗收：Owner 截圖存證；Phase 6 實作時以測試確認 approve 不產生 dispatch

## L-007 二次補強整包只寫入 Drive 鏡像、未進 repo（三次漂移同根因）
- 日期：2026-07-18（Fable 5 健檢發現；漂移發生於 2026-07-08）
- 任務：v1.0 定義凍結前制度健檢（全檔 diff 鏡像 vs repo）
- 症狀：repo 缺 10 C8、05 §6（165 行）、01 §6、20 R-13、README 定位段、99 交接更新——全部只存在於 Desktop\Hermes_OpenClaw_Drive_Upload 鏡像；「GitHub 為王」名存實亡（較新內容在鏡像）
- 根因：2026-07-08 二次補強 session 直接編輯鏡像資料夾，未改 repo 正本；且無任何規則定義正本/鏡像關係與同步方向
- 缺的規則：「正本只在 repo、鏡像單向覆蓋、鏡像禁直改」當時不存在
- 新增/修改的規則：40 F6 鏡像管理（Owner 拍板 2026-07-18）；缺件已全數回填 repo（10 C8 與 05 §6 於本日稍早 commit，01 §6/20 R-13/README/99 隨本筆）
- 驗收：全 11 檔鏡像 vs repo diff 歸零＋fresh-context read-back
