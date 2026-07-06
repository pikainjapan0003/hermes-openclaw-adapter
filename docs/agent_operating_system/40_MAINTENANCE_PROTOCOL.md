# 40 維護協議（Maintenance Protocol）

- 讀者：未來維護本資料夾（docs/agent_operating_system/）的任何模型。
- 原則：制度檔是活的，但安全正本的核心不是。改之前先分級。

---

## F1. 可以自行修改（改動落於工作區並在回報中註明；commit 需 Owner 指示。視情況記入 90）

F1 的「自行修改」指工作區檔案編輯，屬 01 §4 第 5 條的任務授權範圍。git commit / push 永遠需要 Owner 指示，不隨 F1 附帶。

```text
typo、格式、失效連結修復
新增踩坑案例到 90_LESSONS_LEARNED.md
補充已實跑驗證過的命令（標註驗證日期與環境）
新增/改進 30 的 task template
為既有規則補充正例/反例
補充已驗證的資料來源（附查證方式）
記錄已確認的環境差異（例：某環境無 subagent）
更新 05 第 5 節狀態追蹤表（僅狀態行）
10 的 C0 環境快照更新（附驗證證據）
```

## F2. 動之前必須先問 Owner（未問而改 = 事故，記 90 並回滾）

```text
修改 01_SAFETY_BOUNDARIES.md 第 1、2、3 節的任何內容
放寬任何 read-only / dry-run / mock boundary
加入 Dashboard controls（任何 POST/form/button/action URL）
允許 connector（任何級別提升）
允許 Worker dispatch
允許 OpenClaw real call
允許 Blackboard / queue / audit write（新路徑或範圍擴大）
允許任何 external side effects
刪除任何安全規則、HOLD 條件、驗收條件
修改 05 計劃表的 Phase 結構或安全邊界欄
修改 CLAUDE.md 的 phase lock / instruction boundary 規則
```

判斷不了屬於 F1 還是 F2？→ 按 F2 處理（fail closed）。

## F3. 踩坑回寫格式（寫入 90_LESSONS_LEARNED.md）

每次踩坑修復後 5 分鐘內回寫，格式固定：

```text
## L-<流水號> <一句話標題>
- 日期：YYYY-MM-DD
- 任務：<當時在做什麼>
- 症狀：<錯誤訊息/行為，逐字貼關鍵行>
- 根因：<真正原因，不是表象>
- 缺的規則：<當時哪條規則存在就能避免>
- 新增/修改的規則：<改了哪個檔哪一節；若只記錄不改規則，寫「僅記錄」>
- 驗收：<如何確認修復有效>
```

## F4. 精簡門檻（防制度自體膨脹，這正是 00 診斷的 D-01 病）

```text
90_LESSONS_LEARNED.md 超過 300 行 → 建 summary 節於檔首，保留最近 20 案例全文，更早案例壓成一行索引。
05 計劃表超過 500 行 → 檔首摘要索引必須存在且與內文同步（目前已有第 0 節）。
任何單一制度檔超過 500 行 → 建摘要與索引，或拆檔。
拆檔/精簡屬 F1，但刪除規則屬 F2——精簡時規則只能移位與壓縮表述，不能消失。
```

精簡的驗收：精簡前後由 fresh-context subagent 對照「規則清單」一致（條數與語意），落檔於 90。

## F5. 修改流程（F1 類也一樣走）

```text
1. 讀目標檔全文（不要只讀要改的段落）。
2. 改。
3. 自查：是否誤觸 F2 清單？
4. commit：**僅在 Owner 指示 commit 時執行**；message 格式 `docs(aos): <改了什麼> [F1]`（或 `[F2 approved: <Owner 授權引用>]`）。未獲指示 → 留在工作區並回報待 commit。
5. 若是規則變更：90 記一筆。
```
