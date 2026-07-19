# 99 給未來 session 的信

寫信人：Fable 5（初版 2026-07-07；2026-07-14 起恢復可用，本文於 2026-07-21 同步現況）。收信人：之後接手的每一個模型。

你不需要比我聰明才能把這個系統運行好。你需要的是：照文件做、驗收不自驗、不確定就 HOLD。這三件事你做得到。

---

## 1. 三件 Owner 沒問、但我認為對這個環境最重要的事

1. **這個系統最大的資產不是代碼，是邊界的語意設計。**「Dashboard display is not execution permission」這種句式擋住的不是駭客，是「過度想幫忙的你」。你未來最危險的時刻，是你覺得「Owner 應該是想要我順便做掉這個」的時刻。那一刻請打開 01 第 5 節做四問。
2. **Owner 的工作流是 ChatGPT 出指令 → 你執行 → Owner review 的三角 loop。**你不是唯一的 AI，你的回報會被貼給另一個 AI 讀。所以回報格式紀律（CLAUDE.md 第 11 節）不是官僚主義，是讓 loop 不散架的接口契約。一般 phase 維持硬停止；夜跑批次則依 05 §6.13 常設指示，在既定包界線內逐包推進，Fable 5 批審通過後可 merge/push 並開下一批。兩者都不得自行加工作。
3. **這個環境是 Windows + WSL 混血，坑很具體。**開工前把 90_LESSONS_LEARNED.md 的 L-001 到 L-004 掃一眼，能省你半小時的撞牆。

## 2. 這套制度最可能的退化方式與預防法

| 退化方式 | 早期症狀 | 預防法 |
|---|---|---|
| 文件膨脹回 167 份時代 | 新 phase 又開始全文重抄安全聲明 | 40 F4 精簡門檻；引用 01 而非重抄（00 D-01） |
| 驗收退化成自驗 | 回報裡沒有「驗收者是誰」 | R-02 三問；高風險必走 T-06/T-07 |
| 邊界被「一次特例」侵蝕 | 「這次先這樣，之後補」 | 特例也要 Owner 逐字授權；05 §6.13 夜跑常設指示是已落檔、範圍封閉的例外，不是口頭特例 |
| 制度文件與現實脫節 | 文件說的路徑/工具不存在了 | Phase 11 節律的 T-12 計劃表驗證 |
| 弱模型跳過閱讀直接開工 | 回報引用不出任何 D-xx/R-xx 編號 | CLAUDE.md 路由段強制第一步讀 README |
| 90 變成流水帳沒人讀 | 同一坑第三次出現 | 回寫時必填「缺的規則」欄，把教訓變規則 |

## 3. 各種「遇到…怎麼辦」

- **context 快滿**：立刻停止新產出。順序：(1) 未完成清單寫進本檔第 5 節；(2) read-back 已落檔項；(3) 一段式總結給 Owner。落檔的才算存在，回覆草稿裡的不算。
- **工具不能用**（無 subagent / 無 MCP / 無網路）：不要繞道硬試。在回報中標註哪個工具不可用、因此哪些驗收降級成自驗、哪些主張降級成「無法驗證」。降級要顯式，不要沉默。
- **repo / GitHub / Replit 狀態不一致**：跑 D-12 命令確認差異範圍（D-12 只查 local/GitHub hash 與 Replit HTTP 可達性）→ 以 GitHub 為準提出同步提案；實際同步仍須適用的 Owner 指示。禁止用 push/pull/redeploy 默默「修復」。**Drive 報告與 repo 矛盾**：D-12 查不了 Drive，按下一條的優先序處理並記 90。
- **Owner 要求快速做事但安全邊界不明**：提供 safe alternative（R-07）：「我可以立刻給你 dry-run/preview 版；real 版需要你一句逐字授權：<把需要的授權句寫好給 Owner 照抄>」。把授權成本降到 Owner 打一行字，而不是把邊界成本降到零。
- **網路資料與本機狀態矛盾**：本機實跑結果 > 本 repo 文件 > Drive 報告 > 網路資料。矛盾本身要記錄（可能是文件過期的訊號，記 90）。
- **小模型連續犯錯**：C5 升降級。你如果就是那個小模型：第二次失敗後停止重試，把失敗軌跡打包，回報建議升級。承認「這題超出我」是制度要求，不是丟臉。

## 4. Context 緊急協議（複述，因為這封信可能是你唯一讀完的檔）

察覺 context 吃緊 → 停新產出 → 未完成清單落檔 → read-back → 一段總結 → 硬停止。

## 5. 已完成／未完成清單（接手者從這裡開始）

已完成（不要重做）：Phase 2–6；Phase 7 的設計、hash-chain 與 rollback preview；Phase 8 規劃與離線 projection contract；Blackboard schemas／reader／唯讀檢視工具；夜跑批次治理、preflight／信任掃描／contract fuzz／全鏈 rehearsal／coverage closeout。**Phase 0 是每個 session 都要重跑的 recurring gate，不屬於「完成後不要重做」。**Owner 既有裁決集中在 05 §6；除 §6.11 的重審觸發器成立外，不要重新盤問。

未完成清單同步至 2026-07-21：

1. ~~commit/push~~ 已完成（2026-07-07，Owner 指示）：制度與 README 同步均已 push 到 origin。
2. ~~Phase 2–6~~ **已完成（2026-07-19）**：v1.0 定義凍結、Blackboard contract、Owner approval packet、dry-run evidence bundle、Dashboard 唯讀防呆均已落地；queue-claim guard 二版由 NIGHT-BATCH-3 `0d3be1f` 補強。
3. ~~Replit 登入後畫面未驗證~~ 已由 Owner 截圖驗證（2026-07-07）：/dashboard/reviews 有既存核准/拒絕按鈕，見 90 L-006。
4. ~~Phase 8 規劃與 OWASP 對照~~ **規劃完成（2026-07-19）**：`08_REMOTE_READONLY_PLAN.md`＋離線 projection contract 已完成；遠端 API、webhook、receiver 與 runtime 接線仍未授權。
5. ~~`patches/` 目錄未追蹤狀態未處理~~ **已結案（2026-07-18，Owner 指示歸檔）**：內容為早已入庫的 v0.7.2-UI-B 舊補丁（commit 820ec62），已移出 repo 至 `~/projects/hermes-openclaw-adapter-patches-bak-20260718/`。
6. **Phase 7 部分完成（2026-07-19）**：hash-chain 計算層與三輸入 rollback preview builder 已完成，B 案欄位裁決及存在性清單見 07 §6；剩餘 audit writer 動工前仍需 Owner 逐字授權「允許寫入 data/audit_dev.jsonl（local dev append-only）」。現有記憶體內 hash 計算與 preview 不構成寫入授權。
7. **Phase 9 未開始**：需 Owner 在場、單次 token 與已完成的 Phase 7 audit 基線。
8. Drive 資料夾中 v0.8.x 歷史報告未全文讀取（對現況非必要）。
9. **夜跑體制已啟用**：批單內逐包 commit、禁止自行加包；Fable 5 批審通過後依 05 §6.13 merge/push 並開下一批。此常設指示不取代 Phase 7/9/v1.1/v1.2 硬閘。

## 6. 下一個 session 的第一步建議

```text
1. 讀 CLAUDE.md → docs/agent_operating_system/README.md（10 分鐘內完成定位）。
2. 跑 Phase 0 三源檢查（D-12 一條命令）。
3. 讀 05 §5 確認目前 phase；不要重開已完成的 Phase 2–6。
4. 一般工作按 Owner instruction 的 [PHASE]；夜跑則只按現行批單與 05 §6.13 推進，不得自行從 backlog 加包。
```

祝穩定運行。邊界在，系統就在。

— Fable 5
