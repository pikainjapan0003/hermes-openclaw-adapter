# 40 維護協議（Maintenance Protocol）

- 讀者：未來維護本資料夾（docs/agent_operating_system/）的任何模型。
- 原則：制度檔是活的，但安全正本的核心不是。改之前先分級。

---

## F7. Blackboard path trust and portable fixture maintenance

For every board-reader or fixture change, maintain the following boundary contract:

1. A reader may accept a valid hardlink as an input and report `shared_inode=true`; a future writer must reject hardlinks (`st_nlink > 1`) before any write is authorized.
2. Resolve the caller-selected board root exactly once as `R = realpath(root)`. The root itself may be a symlink because it is the caller's trust anchor; that indirection is not an escape. Every immediate entry's `realpath` must remain below `R`, while every symlink found inside the board is rejected before reading. Relative `../` escapes, sockets, FIFOs, devices, directories used as files, and malformed or ambiguous names are rejected fail-closed. Tests may skip an unavailable filesystem capability only when the reason is recorded.
3. Mirror comparison state `DIFFERS` means human decision required; never overwrite either copy automatically. `BEHIND` is reserved for a missing mirror file and `AHEAD` for a mirror-only file.
4. Fixture SHA-256 inventory inputs normalize CRLF to LF before hashing so Windows and WSL verify the same contract bytes. Error reports remain structured and payload-free.
5. Every package report must include the raw `git diff --check` result from the active authorized checkout and the exact state it checked. Run it after the package edits and before commit; paste stdout/stderr verbatim. When output is empty, report `（無輸出；exit 0）` rather than silently claiming success. A command run in another checkout, at another HEAD, or before the reported edits is not evidence for that package (90 L-010).

Verification: run the malicious-path, fixture-integrity, mirror-drift, and full-suite tests on each supported host before accepting a maintenance batch.

### Test execution profiles

- Daily fast path: `python -m pytest`. Repository `addopts` excludes tests marked `slow`; this is the default developer feedback loop.
- Explicit fast path: `python -m pytest -m "not slow"`.
- Required full path before batch acceptance: `python -m pytest -o addopts=""`. This overrides the repository default and includes every `slow` test without deleting or disabling it.
- A fast-path pass is not evidence that the full path passed. Reports must name the command actually run and preserve both outcomes when a package requires both.

### Performance claim provenance

- Every timing number in a current performance or Phase-11 health report must
  be accompanied by a report-level environment note covering OS/host, Python,
  test runner, checkout/commit, and relevant isolation or load conditions.
- A historical report that lacks those facts must say `environment unknown` and
  its timing is non-reproducible context, not acceptance evidence. Do not fill
  in missing facts from memory.
- The performance-claim guard mechanically checks that every report containing
  timing output has an environment section and the commands used. A number
  without that provenance is a documentation finding, not a green performance
  claim.

## F8. Contract/spec dispatch precheck

Before dispatching any package whose acceptance criteria depend on a machine
contract or a factual tool/module precondition, the dispatch brief must include
file:line evidence from the actual repository artifact. The dispatcher must
inspect the artifact at the authorized HEAD; inference from another contract,
a builder name, an earlier report, or memory is not evidence. F8 has three
mandatory evidence classes:

1. **Field existence:** every claimed field is mapped to the actual schema or
   fixture line where it exists (90 L-012).
2. **Schema-keyword claims:** every claim that a schema does or does not use a
   keyword or composition (`oneOf`, `anyOf`, `allOf`, `$ref`, `if`/`then`/`else`,
   `not`, or a future equivalent) is mapped to the inspected schema lines that
   establish presence or absence.
3. **Behaviour preconditions:** every claim that a tool or module fail-closes,
   exposes a state, supports a mode, or rejects a condition is mapped to the
   implementation/test lines that establish that behaviour; if it has not been
   verified, the brief must say **待驗證** instead of asserting it as fact.

If any applicable class lacks evidence, the package is not dispatchable and
must remain HOLD until the brief is corrected. A package may not turn an
uncited fact into a test assertion, invented field, schema change, or weakened
acceptance rule.

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
4. commit：**僅在 Owner 指示 commit 時執行**；message 格式 `docs(aos): <改了什麼> [F1]`（或 `[F2 approved: <Owner 授權引用>]`）。未獲指示 → 留在工作區並回報待 commit。例外：夜跑批次產物依 05 §6.13 常設指示（Owner 2026-07-19 拍板）於 Fable 5 批審通過後 merge/push。
5. 若是規則變更：90 記一筆。
```

## F6. 鏡像管理（Drive 上傳資料夾，Owner 拍板 2026-07-18）

```text
正本唯一：repo 的 docs/agent_operating_system/（GitHub 為王，05 §6.5）。
鏡像：Desktop\Hermes_OpenClaw_Drive_Upload（供 Owner 手機/Drive 隨時翻閱）。
修改流程固定：改 repo → commit → 把改動檔整檔單向覆蓋到鏡像。三步缺一不可。
同步時點＝merge 進 master 後；夜跑分支工作期間鏡像可暫時落後。
鏡像禁止直接修改。直改鏡像 = 事故，記 90 並以 repo 為準處理。
發現鏡像內容超前 repo（歷史漂移）→ 事故：回報 Owner，經裁決後回填 repo，不得沉默同步。
Phase 0 開工檢查可抽查 diff（任一檔鏡像 vs repo 應為 0 差異）。
```

背景：2026-07-08 二次補強整包（05 §6、10 C8、01 §6、20 R-13、README、99）當時只寫入鏡像、未進 repo，2026-07-18 健檢才發現並回填——見 90 L-007。
