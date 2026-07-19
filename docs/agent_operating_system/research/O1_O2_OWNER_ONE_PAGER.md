# O1／O2 Owner 決策一頁摘要

Status: **DECISION BRIEF ONLY — DECISION FIELDS BLANK**

本摘要只壓縮既有兩份提案，不改提案、不建立 contract、gate、role registry、
prompt、worker、dispatch 或 runtime。細節與風險仍以
`O1_PLAN_LEVEL_AUTH_PROPOSAL.md`、`O2_ROLE_WORKER_PROPOSAL.md` 為準。

未裁決前：O1 的 AUTO 任務仍依 01 §2/§4 在 active Owner instruction 找逐字
授權（fail closed）；O2 的 role id、prompt 與多 worker stage 全部未生效。

## O1：計劃級授權格式

要裁決的問題：Owner 批准一份計劃後，未來如何讓該計劃中精確列出的 AUTO、
唯讀、無害任務不用逐 task 重貼相同句子，同時不把「批准 goal」誤讀成任意權限。

| 案 | 做法 | 主要風險 | 建議 |
|---|---|---|---|
| A：總授權＋不可變附錄 | Owner 逐字句綁 `plan_id`、manifest SHA-256、expiry、task/attempt 上限；manifest 逐項列 exact task/action/read target/role。 | 附件可變或 hash 規格不清會 TOCTOU；弱模型可能把總授權擴成 goal 級權限。 | **首選**；首版限單 session、最多 3 tasks、每 task 1 attempt、AUTO read-only。 |
| B：結構化簽核 contract | 新增封閉 `plan_authorization` contract；active Owner quote 與 schema-valid contract 必須同時存在。 | 容易把 `decision=approve` 或 schema-valid 接成 dispatch；實作面比 A 大。 | A 穩定後，若確有 dashboard/audit 正規化需求再評估。 |
| C：限額 capability token | 短效 token 綁 manifest hash、roles、配額與 expiry；每次 task consume 配額。 | token 洩漏/重放、原子 consume、時鐘、recovery、ledger 與 Phase 9 token 混淆。 | 現階段不選；只有多 worker 配額競爭已被證明後重審。 |

### O1 預設建議

選 A，但裁決只定方向，不授權實作。正式落地前仍需獨立拍板 canonical manifest
hash；禁止 wildcard、衍生 task、跨 session 繼承、任何 write/connector/runtime/
dispatch，以及用 O1 包住 Phase 7、Phase 9、v1.1/v1.2 硬閘。contract 與 runtime
gate 必須分包、分審。

### O1 裁決欄（Owner 填，現在留白）

- 選案：________
- 是否接受建議首版邊界（單 session／3 tasks／每 task 1 attempt／AUTO read-only）：________
- 備註或退回理由：________

## O2：角色化 Worker 體制

要裁決的問題：工程師、測試員、安全審查員的角色語意與 prompt 放哪裡、由誰
維護，以及單 worker 如何在未來安全升到多個 read-only workers。

| 案 | 做法 | 主要風險 | 建議 |
|---|---|---|---|
| A：制度 registry＋逐角色 prompt | Markdown registry 定 role id/version/scope；工程師、測試員、安審 prompt 分檔；read-only test 鎖路徑/hash/禁令。 | registry 與 prompt 可能漂移；角色容易被誤讀為 capability。 | **首選**；人可讀、Git diff 小，首版只做到 Stage 1 順序模擬。 |
| B：單一文件內嵌 prompts | registry 與三份 prompt 放同一 Markdown 正本。 | 改一角色會碰整份高敏感文件；runtime 可能把說明文字誤當 prompt。 | 僅在 Owner 更重視單檔一致性且接受大 diff 時選。 |
| C：machine-readable registry | 封閉 schema/JSON registry 為正本，Markdown 只顯示，prompt hash 由 gate 驗證。 | 首版複雜；會引入 parser/validator/runtime integration 等未授權機制。 | 多 worker runtime 真正出現後再評估，不宜現在先做。 |

### O2 預設建議

選 A；Owner 是唯一啟用/放寬者，Fable 5/commander 只做 steward、不能自批。
現行 Blackboard `role` 永遠只是作者 provenance，不是身份驗證、assignment 或
permission。首版只做 Stage 1「單 worker、分 context 順序模擬三角色」；Stage 2
read-only multi-worker 仍須 O1、assignment contract、claim/revoke/cancel 測試與另案
Owner 授權，Stage 3 寫入不由 O2 解鎖。

### O2 裁決欄（Owner 填，現在留白）

- 選案：________
- 首版停在 Stage 1（單 worker 順序模擬）：________
- registry steward：________
- 三個 role prompt 初稿（採用／修改／退回）：________
- 備註或退回理由：________

## Owner 最短回覆格式

若接受兩份提案各自的預設建議，只需回：

```text
O1 選 A、O2 選 A；接受兩案預設建議邊界。這是方向裁決，不是實作授權。
```

若選別案，只替換字母並在同一句補邊界，例如：

```text
O1 選 B、O2 選 A；O2 首版停在 Stage 1。這是方向裁決，不是實作授權。
```

任何回覆若未明列實作範圍，均不得被解讀為建立 schema、token、registry、prompt
檔、assignment、queue、worker、dispatch 或 runtime 的授權。
