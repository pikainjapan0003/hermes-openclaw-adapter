# 30 派工 Prompt 模板（Delegation Prompts）

- 讀者：擔任 commander 的模型。用法：複製模板、填 `<>` 佔位、整段作為 subagent prompt。
- 所有模板共用的固定尾段（每次都要附上，防 subagent 越權與空話回報）：

```text
[共用約束]
你是 subagent，只做本 prompt 指定的事。
禁止：寫入/修改本 prompt 允許範圍外的任何檔案；任何網路發送（除非本 prompt 明示允許 WebSearch/WebFetch）；宣稱未執行過的驗證。
安全規則見 docs/agent_operating_system/01_SAFETY_BOUNDARIES.md：不確定授權 → 不做並回報。
回報格式（強制）：
[結論] 1–3 句
[風險] 條列或「無」
[位置] 檔案:行號
[已驗證] 實際執行/讀取確認過的事
[未驗證] 推測或查不到的事
[建議下一步] 一條
超過 50 行的產物落檔到 <指定路徑>，回報只給路徑。
```

---

## T-01 搜尋 / repo scan（用 Explore 型 subagent）

```text
背景：<一句話，為什麼要找>
目標：在 <目錄範圍> 找出 <明確對象，例：所有寫入 data/ 的 code path>
不做：不修改任何檔案；不評價代碼品質（除非另有要求）
允許讀取：<目錄清單>
驗收：每個結果附 檔案:行號 與一行說明；宣告搜尋覆蓋了哪些目錄與 pattern
HOLD：範圍內檔案超過 <N> 個無法窮盡 → 回報實際覆蓋率，不要假裝窮盡
```

## T-02 實作

```text
背景：<Phase 編號 + 一句話動機，引用 05 計劃表對應節>
目標：實作 <明確產物，含檔案路徑>
規格：<欄位/行為/介面，越具體越好；有樣本就給樣本>
不做：不改 <明列不可碰檔案，尤其 mock/real 對側檔>；不「順便」重構鄰近代碼；不新增 route/endpoint
允許修改：<白名單路徑>
驗收：<測試命令> 全綠；含至少 <N> 個反例測試；lint 過
HOLD：規格與既有代碼衝突 → 停，回報衝突點，不自行取捨
```

## T-03 重構

```text
背景：<為什麼重構，引用診斷編號 D-xx 或 lessons 條目>
目標：<重構後的形狀，例：抽出共用 validator>
不變式（重構的定義）：外部行為完全不變——<列出必須保持的行為/測試>
不做：不加新功能；不改公開介面（除非明列）；不動安全 gate 邏輯
允許修改：<白名單>
驗收：重構前後 <測試命令> 皆綠；diff 中無行為變更（審查者確認）
HOLD：發現必須改行為才能重構 → 停，回報
```

## T-04 研究（含 web research）

```text
背景：<要解的問題>
目標：回答 <明確問題清單>
方法：WebSearch/WebFetch 允許；每個結論附來源 URL 與查證日期
不做：不憑訓練記憶回答存在性/版本/日期問題；查不到就寫「無法驗證」
驗收：每條結論有來源；UNVERIFIED 單獨成節
HOLD：關鍵問題全部查不到 → 回報查過什麼，不要編
```

## T-05 審查（一般 code/doc review）

```text
背景：<產物是什麼、將用於什麼>
目標：找出 <正確性問題/與規格的偏差>，不談風格偏好
允許讀取：<產物 + 相關規格文件>
不做：不修檔（只回報）；不重寫作者的方案
驗收：每個 finding 附 檔案:行號 + 一句缺陷描述 + 觸發場景；無 finding 也要明說「查了哪些角度」
HOLD：規格本身矛盾 → 列為 finding 而非自行選邊
```

## T-06 read-back 驗收（fresh-context）

```text
背景：驗收剛產出的檔案（你沒有參與產出，保持懷疑）
目標：對 <檔案清單> 逐一確認：
  1. 檔案存在於宣稱路徑
  2. 標題與宣稱一致
  3. 必要章節存在：<章節清單>
  4. 檔內引用的其他路徑真實存在（實際檢查）
  5. <特定必要內容，例：HOLD 條件、正反例>
不做：不評內容好壞，只驗存在性與完整性
驗收：輸出核對表，每項 PASS/FAIL + 證據（行號或引文）
HOLD：任一 FAIL → 全部列出，不要只報第一個
```

## T-07 fresh-context adversarial review（高風險產出必用）

```text
背景：<產物> 涉及安全邊界，假設作者有盲點，你的工作是攻擊它
目標：在 <檔案清單> 中找出：
  1. 互相打架的規則（引用兩處行號）
  2. 錯誤路徑/工具名/模型名
  3. 弱模型會誤讀的模糊句（指出會誤讀成什麼）
  4. 會導致越權執行的句子（display→permission、mock→real、計劃→授權）
  5. 缺 HOLD 條件的規則、缺驗收條件的階段
  6. 無來源支撐的外部宣稱
不做：不改檔；不提「錦上添花」建議（只報缺陷）
驗收：每個 finding = 檔案:行號 + 誤讀場景（誰在什麼情況會做錯什麼）
HOLD：無特定條件（本任務純唯讀）
```

## T-08 Drive / 文件閱讀

```text
背景：<為什麼讀>
目標：讀 <Drive 資料夾/文件 ID 或路徑>，回答 <問題清單>
方法：用 MCP Google Drive 工具；工具不可用立即回報「MCP Drive tools unavailable」，不要繞道
不做：不改任何 Drive 內容；不下載到 repo 內
驗收：關鍵主張附文件名 + 引文；讀不完的文件標明讀到哪
HOLD：權限不足 → 列出無法讀的檔名
```

## T-09 Dashboard / Replit smoke test

```text
背景：驗證部署面狀態（Phase 0 / Phase 6）
目標：對 https://hermes-openclaw-adapter.replit.app 及 /dashboard/system：
  1. 可載入？HTTP 狀態？
  2. 頁面自我標示 read-only？
  3. 有無 form/button/action URL/POST 跡象（登入表單為已知白名單）
  4. 有無 secrets/payload 洩漏
方法：WebFetch 唯讀。禁止提交任何表單、禁止帶 token 嘗試登入（除非 Owner instruction 逐字給了 token 與授權）
驗收：四項各有 觀察到的證據；「登入後畫面」若無授權一律記 UNVERIFIED
HOLD：發現疑似洩漏 → 立即回報，不要在回報中複述 secret 內容
```

## T-10 GitHub repo review

```text
背景：<Phase 0 一致性 / 或評估某外部 repo>
目標：<本 repo：比對 HEAD、結構、issues/PR｜外部 repo：見 T-11>
方法：gh CLI 或 WebFetch，唯讀
不做：不 push、不開 issue/PR、不 fork
驗收：hash 逐字引用；比對結果明確寫「一致/不一致 + 差異」
HOLD：需要認證才能讀 → 回報，不嘗試繞過
```

## T-11 開源項目參考評估

```text
背景：為 <某 Phase> 找可借鑑設計
目標：對 <repo/主題>：驗證仍活躍（最近 release/commit 日期）、stars/forks、README 是否清楚、是否符合本系統（單 Owner、檔案式 Blackboard、弱模型維護）
必答三欄：可借鑑什麼（設計層）／不可照抄什麼（含授權條款風險）／棄用訊號（deprecated 聲明？）
不做：不引入依賴、不 clone 進本 repo
驗收：每項數據註明「於 <日期> 在 <頁面> 看到」；查不到的欄位寫 UNVERIFIED
HOLD：無特定條件（本任務純唯讀）
```

## T-12 計劃表驗證

```text
背景：05_VERIFIED_LONG_TERM_PLAN.md 需要定期重驗（Phase 11 節律）
目標：逐 Phase 檢查：
  1. 「目前系統狀態」節與實際 repo/HEAD 還一致嗎（實跑 Phase 0 命令比對）
  2. 每個 Phase 的輸入依賴是否已因現實變化而失效
  3. 2.3 參考清單是否有已 deprecated 項目（抽查 WebFetch）
  4. 狀態追蹤表（第 5 節）與 git log 是否對得上
不做：不改計劃結構；發現過期只回報，修訂走 40 的權限分級
驗收：逐項 PASS/FAIL + 證據
HOLD：發現計劃與 01 安全正本衝突 → 最高優先回報
```

---

## 使用備註

- 「研究」與「web research」共用 T-04；「審查」細分為 T-05（一般）/T-06（read-back）/T-07（adversarial），按 20_JUDGMENT_RUBRICS.md R-09 選擇。
- 沒有一個模板完全符合時：選最近的模板改造，但**三件套（目標/驗收/回報格式）與共用約束不可省**。
- 模板本身的增修屬 40 F1（可自行改），但改動後要在 90 記一筆原因。
