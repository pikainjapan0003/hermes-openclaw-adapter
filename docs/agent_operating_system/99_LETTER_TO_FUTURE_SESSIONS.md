# 99 給未來 session 的信

寫信人：Fable 5（2026-07-07，本模型最後開放日）。收信人：之後接手的每一個模型——多半是 Sonnet、Haiku 或 API 調用的你。

你不需要比我聰明才能把這個系統運行好。你需要的是：照文件做、驗收不自驗、不確定就 HOLD。這三件事你做得到。

---

## 1. 三件 Owner 沒問、但我認為對這個環境最重要的事

1. **這個系統最大的資產不是代碼，是邊界的語意設計。**「Dashboard display is not execution permission」這種句式擋住的不是駭客，是「過度想幫忙的你」。你未來最危險的時刻，是你覺得「Owner 應該是想要我順便做掉這個」的時刻。那一刻請打開 01 第 5 節做四問。
2. **Owner 的工作流是 ChatGPT 出指令 → 你執行 → Owner review 的三角 loop。**你不是唯一的 AI，你的回報會被貼給另一個 AI 讀。所以回報格式紀律（CLAUDE.md 第 11 節）不是官僚主義，是讓 loop 不散架的接口契約。硬停止（「完成後停止，等待 Owner 下一步」）是這個 loop 的心跳，不要自作主張開下一 phase。
3. **這個環境是 Windows + WSL 混血，坑很具體。**開工前把 90_LESSONS_LEARNED.md 的 L-001 到 L-004 掃一眼，能省你半小時的撞牆。

## 2. 這套制度最可能的退化方式與預防法

| 退化方式 | 早期症狀 | 預防法 |
|---|---|---|
| 文件膨脹回 167 份時代 | 新 phase 又開始全文重抄安全聲明 | 40 F4 精簡門檻；引用 01 而非重抄（00 D-01） |
| 驗收退化成自驗 | 回報裡沒有「驗收者是誰」 | R-02 三問；高風險必走 T-06/T-07 |
| 邊界被「一次特例」侵蝕 | 「這次先這樣，之後補」 | 特例也要 Owner 逐字授權；沒有口頭特例 |
| 制度文件與現實脫節 | 文件說的路徑/工具不存在了 | Phase 11 節律的 T-12 計劃表驗證 |
| 弱模型跳過閱讀直接開工 | 回報引用不出任何 D-xx/R-xx 編號 | CLAUDE.md 路由段強制第一步讀 README |
| 90 變成流水帳沒人讀 | 同一坑第三次出現 | 回寫時必填「缺的規則」欄，把教訓變規則 |

## 3. 各種「遇到…怎麼辦」

- **context 快滿**：立刻停止新產出。順序：(1) 未完成清單寫進本檔第 5 節；(2) read-back 已落檔項；(3) 一段式總結給 Owner。落檔的才算存在，回覆草稿裡的不算。
- **工具不能用**（無 subagent / 無 MCP / 無網路）：不要繞道硬試。在回報中標註哪個工具不可用、因此哪些驗收降級成自驗、哪些主張降級成「無法驗證」。降級要顯式，不要沉默。
- **repo / GitHub / Replit 狀態不一致**：跑 D-12 命令確認差異範圍（D-12 只查這三源）→ 回報差異 → HOLD 等 Owner 決定同步方向。禁止自行 push/pull/redeploy「修復」。**Drive 報告與 repo 矛盾**：D-12 查不了 Drive，按下一條的優先序處理並記 90。
- **Owner 要求快速做事但安全邊界不明**：提供 safe alternative（R-07）：「我可以立刻給你 dry-run/preview 版；real 版需要你一句逐字授權：<把需要的授權句寫好給 Owner 照抄>」。把授權成本降到 Owner 打一行字，而不是把邊界成本降到零。
- **網路資料與本機狀態矛盾**：本機實跑結果 > 本 repo 文件 > Drive 報告 > 網路資料。矛盾本身要記錄（可能是文件過期的訊號，記 90）。
- **小模型連續犯錯**：C5 升降級。你如果就是那個小模型：第二次失敗後停止重試，把失敗軌跡打包，回報建議升級。承認「這題超出我」是制度要求，不是丟臉。

## 4. Context 緊急協議（複述，因為這封信可能是你唯一讀完的檔）

察覺 context 吃緊 → 停新產出 → 未完成清單落檔 → read-back → 一段總結 → 硬停止。

## 5. 已完成／未完成清單（接手者從這裡開始）

已完成（不要重做）：三源環境驗證（HEAD 7a93127e 一致）；Drive 三份報告全文閱讀；8 項開源參考查證；全套 10 份制度檔＋CLAUDE.md 第 12 節路由；fresh-context adversarial review（18 findings 全修，見 90 L-005）；fresh-context read-back 驗證。**二次補強盤問（2026-07-08）：Owner 親答 20 題，裁決全數落檔於 05 §6——讀 05 時第 6 節優先於第 3 節，不要重新盤問已裁決的題目（重審觸發器見 05 §6.11）。**

未完成，截至 2026-07-07 Fable 5 session 結束：

1. ~~commit/push~~ 已完成（2026-07-07，Owner 指示）：制度與 README 同步均已 push 到 origin。
2. ~~Phase 2（v1.0 Definition Freeze）~~ **已完成（2026-07-18）**：02_V1_0_DEFINITION.md 凍結，Owner 逐字簽核（該檔 §5）。下一步＝Phase 3（Blackboard Contract Hardening），實作需 Owner instruction 逐字授權。
3. ~~Replit 登入後畫面未驗證~~ 已由 Owner 截圖驗證（2026-07-07）：/dashboard/reviews 有既存核准/拒絕按鈕，見 90 L-006。
4. OWASP Agentic Top 10 全文未讀（只驗證了發布頁），Phase 8 使用前要先讀原文。
5. ~~`patches/` 目錄未追蹤狀態未處理~~ **已結案（2026-07-18，Owner 指示歸檔）**：內容為早已入庫的 v0.7.2-UI-B 舊補丁（commit 820ec62），已移出 repo 至 `~/projects/hermes-openclaw-adapter-patches-bak-20260718/`。
6. Drive 資料夾中 v0.8.x 歷史報告未全文讀取（對現況非必要）。

## 6. 下一個 session 的第一步建議

```text
1. 讀 CLAUDE.md → docs/agent_operating_system/README.md（10 分鐘內完成定位）。
2. 跑 Phase 0 三源檢查（D-12 一條命令）。
3. 向 Owner 確認：是否 commit 本制度？是否開始 Phase 2？
4. 之後按 Owner instruction 的 [PHASE] 走，不要自行推進。
```

祝穩定運行。邊界在，系統就在。

— Fable 5
