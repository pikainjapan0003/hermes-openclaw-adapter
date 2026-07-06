# 10 模型調度守則（Model Orchestration）

- 讀者：擔任主對話的任何模型（以下稱 commander）。
- 一句話：commander 是指揮官不是勞工；派工要帶三件套；驗收不自驗；錯兩次就升級。

---

## C0. 本環境已驗證的模型與工具（2026-07-07，Claude Code / VSCode extension 環境）

以下為 Fable 5 session 實測驗證：

- 可用 subagent 類型：`general-purpose`（全工具）、`Explore`（唯讀搜索）、`Plan`（架構規劃）、`claude`、`claude-code-guide`、`openclaw-model-fix`（本機自訂）、`statusline-setup`。
- Agent tool 可指定 model：`sonnet` / `opus` / `haiku` / `fable`。
- 當時模型 ID：`claude-fable-5`（僅開放至 2026-07-07）、`claude-opus-4-8`、`claude-sonnet-5`、`claude-haiku-4-5-20251001`。
- subagent 可用 MCP Google Drive 工具與 Web 工具（本 session 實測成功）。
- effort / thinking 參數：**無法確認 effort 設定**——subagent 的 reasoning effort 由 agent 定義檔控制，本 session 無法逐一驗證。不要對外宣稱某 subagent 用了某 effort。

**每個新環境（尤其 API 直連、CLIProxyAPI、OpenClaw gateway）必須重新驗證上表**，方法：列出實際可用工具與模型，寫進回報；過期資訊不得沿用。若無法查到可用模型，採用此原則：

```text
Model availability could not be verified in this environment.
Use the strongest available model for architecture, safety, and final review.
Use cheaper model only after task shape is fully specified.
```

## C1. 指揮官不下場

- 觸發條件：任務需要開超過 5 個檔案、讀超過 500 行、掃整個目錄、批次修改超過 3 個檔案、跑長測試、查多個網頁。
- 操作：派 subagent（讀取用 Explore，綜合任務用 general-purpose），commander 只保留：目標判斷、任務拆解、驗收、風險決策、給 Owner 的摘要。
- 驗收條件：commander 的 context 中不出現大段原始檔案內容，只出現結構化回報。
- 例外（非 HOLD）：無 subagent 可用（API 直連環境）→ 分段處理 + 隨讀隨記摘要到 scratch 檔，並在回報註明「無 subagent，主模型直接執行」。
- HOLD 條件：無。
- 正例：「掃 app/ 找所有可能的寫入路徑」→ Explore subagent → 回報 8 個 `檔案:行號`。
- 反例：commander 逐檔讀完 app/ 全部 28 個檔案後 context 剩 20%，還沒開始正事。

## C2. 派工三件套

每次委派必須包含，缺一不派：

1. **目標與動機**：做什麼、為什麼（讓 subagent 能對邊界情況做正確取捨）。
2. **驗收條件**：完成的客觀判準（測試綠、欄位存在、hash 一致…）。
3. **回報格式**：明確要求 C4 的格式。

- 正例：「目標：驗證 9 個 schema 覆蓋 fixture 全欄位（動機：Phase 3 驗收）。驗收：每個 fixture 欄位都能對應到 schema 屬性，列出無法對應者。回報：C4 格式，缺漏以 `檔案:行號` 列出。」
- 反例：「幫我看一下 schema 寫得怎麼樣。」

## C3. 顯式指定 model

- 讀取/枚舉/格式轉換 → `haiku`（錯一次立刻升 `sonnet`）。
- 實作/測試/文件起草 → `sonnet`。
- 架構取捨、安全審查、最終 review → 可用的最強模型（2026-07 為 `opus`；驗證當下清單見 C0）。
- 規則：**任務形狀未完全指定前，不用便宜模型**。便宜模型的正確用法是「強模型解出模式後的批次套用」。

## C4. 回報合約

subagent 回報必須是以下結構，禁止長篇散文：

```text
[結論] 一到三句
[風險] 條列，可為「無」
[位置] 檔案:行號 清單
[已驗證] 我實際執行/讀取過而確認的事
[未驗證] 我推測或沒查到的事
[建議下一步] 一條
```

長產物（超過 50 行的文件、diff、報告）必須落檔，回報只給路徑。commander 收到不合格式的回報，退回要求重報，不要自己代為整理。

## C5. 升降級路徑

```text
haiku 級錯一次 → 直接升 sonnet 級。
sonnet 級同一子任務連錯兩次 → 帶完整失敗軌跡（原 prompt、兩次錯誤輸出、期望輸出）升最強模型。
最強模型解出模式後 → 把「已解出的模式 + 逐步指示」降回便宜模型批次套用。
同一件事最多重試兩輪。第三次不重試：換路線，或帶著兩次失敗紀錄問 Owner。
```

- 正例：Sonnet 兩次把 schema `required` 欄位寫錯 → 升 Opus 附兩次 diff → Opus 定稿一個 schema 作為模式 → 剩餘 8 個 schema 由 Sonnet 照模式產出。
- 反例：Haiku 連續五次修同一個 import error；或用 Opus 逐字改 200 個檔案的版權頭。

## C6. 驗證不自驗

產出者與驗收者的 context 必須分離。

- 檔案驗收（fresh-context subagent，給清單不給推理過程）：read-back 檔案存在、路徑正確、必要章節存在、關鍵欄位存在、引用的其他檔案真的存在。
- 程式驗收：pytest / compile / lint / smoke test / 實跑 route。「測試綠」才算數，「我看邏輯沒問題」不算數。
- 高風險判斷（安全邊界、寫入路徑、執行閘）：adversarial review——明確指示審查者「找出會被誤讀成越權的句子、找出從 display 走到 execution 的 code path、找出缺 HOLD 條件的規則」。
- 無法開 subagent 時：可做 self-review 但回報必須寫明 `自驗，非獨立驗收`，且高風險項目自驗不能作為 Owner 簽核依據。

## C7. 與既有 loop 的關係

本守則不取代 CLAUDE.md 的 Loop Format Contract。phase lock、Owner instruction boundary、硬停止規則優先於本檔。本檔管的是「一個 phase 內部」怎麼調度模型；CLAUDE.md 管的是 phase 之間怎麼流轉。
