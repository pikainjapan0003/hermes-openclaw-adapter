# v1.1 First Real Repository Write — Full-Chain Design

Status: **PLANNING ONLY, NOT AUTHORIZED**

前置＝v1.0 簽核完成＋新 Owner instruction；本文件非授權。本文不授權建立、
修改或刪除任何測試檔，不授權發 token、寫 audit、commit、revert、execution、
dispatch 或 runtime 接線。現行 Phase 4 `single_use_execution_token` 必須維持
`null`；真正 v1.1 packet/token 需由日後獨立設計、實作與 Owner 審查包建立。

## 1. 正本與目標

本設計依據：

- `02_V1_0_DEFINITION.md`：真實寫入屬 v1.1，前置為 v1.0 簽核完成與新
  packet/token；
- `05_VERIFIED_LONG_TERM_PLAN.md` §6.8：v1.1 只做 repo 內測試檔一次真實
  寫入，標準 rollback 為 Git；
- `07_AUDIT_WRITE_DESIGN.md`：audit event 使用 canonical JSON、SHA-256 與
  `prev_entry_hash` chain；
- `09_N1_PREFLIGHT_RUNBOOK.md`：證據凍結、Owner checkpoint、單次 token、
  no retry、執行後回到 deny-all。

v1.1 的唯一主動作是：在乾淨、已確認的 repository worktree 內，以一次性
授權建立一個 Owner 指定且 packet 綁定的測試探針檔。建議的候選 target 為
`tests/v1_1_write_probe.txt`；該路徑只是設計候選，不是現在可建立的路徑。
實作前 Owner instruction 必須逐字指定最終 target 與精確內容。

本設計聚焦 N=1，不設計通用檔案寫入器、不接受 caller 任意路徑、不支援第二個
檔案、glob、目錄、symlink、rename、覆寫既有檔、retry 或背景工作。

## 2. 一次寫入的精確邊界

### 2.1 主動作

| 項目 | v1.1 N=1 約束 |
|---|---|
| Target | packet 內一個 repo-relative、Owner 指定、位於 `tests/` 的精確路徑 |
| Precondition | target 不存在；worktree 除本次已審查內容外乾淨；target parent 已存在且不是 symlink |
| Content | packet 內精確 UTF-8 bytes；無 BOM；固定 LF；不得含 secret、token、env、真實 payload |
| Primary mutation | 建立 target 一次；禁止 reopen、append、rewrite、rename 或第二 target |
| Verification | 重讀後 byte hash、長度與 packet 完全一致；`git diff -- target` 只含預期新增內容 |
| Retry | 禁止；失敗或狀態不明即消耗 token、回 deny-all、進 incident/rollback 判定 |
| Scope expansion | 禁止把成功解讀成可寫其他測試檔或可執行真實代碼任務 |

### 2.2 必須明列的基礎設施副作用

「一次真實寫入」是指一個 target 主動作，不表示全鏈沒有其他已審批的持久化。
packet 的 `expected_side_effects` 必須逐項列出：

1. Phase 7 audit file 的 pre-attempt、result、rollback/closeout append；
2. target 測試檔的一次建立；
3. 將該 target 建立記錄成一個專用 Git commit；
4. rollback rehearsal 若啟動，`git revert` 產生一個 revert commit 並移除 target；
5. 除上述項目外不得有 queue、Blackboard、connector、remote、production、
   package install、network 或其他檔案副作用。

若 Owner 不批准 Git commit 或 audit append，整個 v1.1 rehearsal 必須 HOLD，
不得把未 commit 的檔案刪除冒充已完成標準 rollback。

## 3. 新 approval packet 設計

### 3.1 不修改 Phase 4 正本

Phase 4 `approval_packet.schema.json` 的 token 欄位保持 `const null`。v1.1 必須
建立獨立、版本化的新 write-rehearsal packet contract；不得原地放寬舊 schema，
也不得讓既有 dashboard approval 直接成為執行許可。新 contract 的名稱、檔名與
正式 schema 仍需獨立 Owner 裁決。

### 3.2 Packet 必要資料

新 packet 至少綁定下列資料；任何欄位缺失或交叉不一致皆 fail closed：

| 類別 | 必要內容 |
|---|---|
| Identity | packet id、schema version、task id、Owner decision id、created/expiry timestamps |
| Exact action | action type 固定為 create-one-test-probe；不得接受通用 command/string script |
| Exact target | repo identity、base commit、repo-relative target、resolved-path proof、target-absent proof |
| Exact bytes | UTF-8 content、byte length、content SHA-256、newline policy |
| Evidence | dry-run id、result id、evidence bundle id/hash、reviewed diff preview |
| Risk | risk level、完整 expected side effects、forbidden side effects、timeout、no-retry rule |
| Audit | expected audit pre/result/rollback event ids、當下 verified tail hash |
| Rollback | write commit 預期、revert strategy、post-revert target state、test command |
| Decision | Owner approve/edit/reject/respond；只有專用 gate 可判讀，資料本身不執行 |
| Token binding | token id/digest metadata、packet digest、action digest、expires/consumed 狀態；不含 raw token |

Packet 必須在 evidence bundle 凍結後生成。Owner 若 edit 任一 target、內容、hash、
timeout、side effect 或 rollback 欄位，舊 packet 與 token 全部失效，須重做 dry-run
與新 packet；不得就地修補後沿用 approval。

## 4. Single-use token 生命週期

### 4.1 發放

1. v1.0 已正式簽核，Phase 7 writer/chain 已另案完成並通過實檔審查；
2. 最終 evidence 與新 packet 已凍結且完整驗證；
3. Owner 同步在場，逐欄確認 target、bytes、side effects、timeout、rollback；
4. Owner 以該 session 的新 instruction 發出一個高熵、單次 token；
5. gate 只在記憶體持有 raw token，建立不可逆 digest，綁定 packet digest、action
   digest、base commit、target 與 expiry；
6. packet、fixture、log、audit 與 error message 永不存 raw token。

### 4.2 消耗與失敗

- gate 在主動作前原子性地把 token 標成 consumed；consume 失敗即不寫 target；
- missing、expired、consumed、wrong packet、wrong action、wrong base commit、wrong
  target 或 wrong content 任一情況皆拒絕；
- write 回傳 timeout 或狀態不明也視為已消耗，先查證 target 現況，不得 retry；
- 不論結果，gate 立即回到 deny-all；第二次嘗試必須新 evidence、packet、Owner
  instruction 與 token；
- audit 只記 token id、digest 前綴或不可逆引用、issued/consumed outcome，不記 raw
  token。

Token gate 是未來獨立實作包。本文件不得被 parser、runtime 或 worker 當成 gate。

## 5. Audit hash-chain 串接

Phase 7 必須先完成，且實際 audit file 已由 Owner 檢視。v1.1 不另創 hash 規則：

1. 每筆 audit event 先通過既有 closed schema；
2. canonical bytes 依 07 §4：Unicode NFC、key 排序、UTF-8、compact JSON、禁 float、
   禁 duplicate key，實體 LF 不進 hash；
3. event hash 涵蓋完整 event，包括 `prev_entry_hash`；
4. 新事件的 `prev_entry_hash` 必須等於已完整驗證的目前 tail hash；只有真正 genesis
   可用 null；
5. append 前驗完整既有 chain，append 後再驗完整 chain；任一步失敗即停止；
6. 禁止以 audit 成功觸發 queue、dispatch、execution 或下一步 permission。

建議事件序列：

| 順序 | Event | 必要 outcome |
|---:|---|---|
| 1 | v1_1_write_authorized | 記 packet/action/evidence digest、Owner decision、token metadata；不記 raw token |
| 2 | v1_1_write_attempt | token 已 consume、base/target precondition 成立 |
| 3 | v1_1_write_result | target bytes/hash、Git diff、tests、write commit 或失敗/ambiguous 狀態 |
| 4 | v1_1_rollback_attempt | 僅在預先審批的 rehearsal/incident 路徑啟動，記 write commit 與 revert target |
| 5 | v1_1_rollback_result | revert commit、target absent、tests、chain 驗證結果 |
| 6 | v1_1_owner_closeout | Owner 接受/拒絕；永不構成 v1.2 授權 |

若 audit append 自己失敗，主動作不得開始；主動作後的 audit 失敗則立即凍結，保留
worktree 證據並交 Owner，不得以「補寫 audit」名義自動繼續。

## 6. Rehearsal 全鏈順序

### 6.1 寫入前

1. 固定 repo、branch、base commit 與 clean-worktree 證據；
2. 確認 target 不存在、resolved path 在 repo/tests 內、parent 非 symlink；
3. 產生 exact-byte diff preview，不接觸 target；
4. 建 evidence bundle，列出 §2.2 全部 side effects，重算 bundle hash；
5. 建新 packet，完成強模型與 Owner review；
6. 發 token；重新比對所有 frozen digest；
7. 驗 Phase 7 chain，append pre-attempt audit；
8. consume token，再次確認 base、clean state、target absent；
9. 任一差異即 STOP，不能改內容、不能換 target、不能 retry。

### 6.2 寫入、驗證與 commit

1. 以 exclusive-create 語義建立 target，一次寫入 exact bytes；
2. flush/close 成功後重讀，核對 byte length、content hash、LF 與無 BOM；
3. `git diff -- target` 必須只顯示 packet 預覽的新增內容；
4. 執行 packet 指定的最小測試與完整 tests；
5. 若驗證全過，只 stage 該 target 並建立專用 write commit；
6. 記錄 commit hash與 post-write audit；回 deny-all；
7. 若任一步失敗或模糊，禁止補寫/重試，進 §7 rollback/incident gate。

下列只是一個未授權的未來驗證命令示例；實際 branch、target 與測試需由 packet
逐字綁定。

PLANNING ONLY, NOT AUTHORIZED

```text
git status --short --branch
git diff -- tests/v1_1_write_probe.txt
python -m pytest
```

## 7. Rollback＝git revert 演練

### 7.1 啟動條件

rollback 不是自由命令入口，只能處理 packet 記錄的那個 write commit。首次 v1.1
驗收建議把 rollback rehearsal 當成同一個 Owner-supervised session 的強制步驟；
若 Owner 不在場、write commit 不唯一、worktree 不乾淨、HEAD 已漂移或 chain 不完整，
即 HOLD，不得猜測 commit 或手動刪檔。

### 7.2 演練步驟

1. freeze write commit、其唯一 parent、target path、pre/post hashes；
2. 驗 write commit 只新增 packet 指定 target，沒有其他 file/hunk；
3. 產 rollback preview，明列預期為 target absent、產生一個 revert commit；
4. Owner 再確認 exact write commit；
5. append rollback-attempt audit；
6. 執行一次 non-interactive `git revert`，禁止 `reset --hard`、force、checkout 掩蓋；
7. 驗新 HEAD 是 revert commit、target 不存在、其他 tracked files 未變；
8. 跑相同最小測試與完整 tests；
9. append rollback-result audit，再驗完整 chain；
10. Owner closeout。rollback 失敗即凍結，不得自動重試或改用其他命令。

下列命令只說明未來 rehearsal 的形狀；`<WRITE_COMMIT_FROM_PACKET>` 必須來自已
審批 packet，不能由模型自行選擇。

PLANNING ONLY, NOT AUTHORIZED

```text
git show --stat --oneline <WRITE_COMMIT_FROM_PACKET>
git revert --no-edit <WRITE_COMMIT_FROM_PACKET>
git status --short --branch
python -m pytest
```

## 8. Fail-closed 規則

以下任一情況立即 STOP/HOLD：

- v1.0 未簽核、Phase 7 未完成、Owner 不在場或缺新 instruction；
- target 非 packet 精確路徑、已存在、出 repo/tests、parent 為 symlink；
- base commit、worktree、bytes、hash、bundle、packet、timeout 或 side effects 漂移；
- token 缺失、過期、重放、未綁定或已消耗；
- audit chain 斷裂、tail 改變、append/verify 失敗；
- 寫入結果 ambiguous、出現第二檔、額外 Git diff、測試紅；
- write commit 含額外 file/hunk，或 rollback commit target 不唯一；
- 有 queue、dispatch、worker、OpenClaw/Hermes、connector、remote、production 或
  automatic retry 路徑；
- 任何人把 approval、audit success、test green 或 closeout 當成 v1.2 permission。

## 9. 驗收與簽核清單

### 9.1 Contract / evidence

- [ ] v1.0 已有正式 Owner closeout；Phase 7 writer/chain 已正式完成。
- [ ] 新 write packet schema 與 token gate 經獨立 package、反向測試與 fresh-context
      審查；Phase 4 null-token schema 未放寬。
- [ ] evidence bundle 綁定 exact repo/base/target/bytes/hash/diff/side effects/rollback。
- [ ] packet 與 evidence 所有 id/hash 交叉一致，raw token 不在任何持久化資料。

### 9.2 Write

- [ ] Owner 新 instruction 與 fresh token 只覆蓋一次 target create。
- [ ] token consume-before-write；replay、wrong-target、wrong-content、expired 測試全拒絕。
- [ ] target bytes/hash 與 packet 完全一致，沒有第二檔或額外 diff。
- [ ] 最小測試與完整 tests 全綠；write commit 只含一個 target。
- [ ] pre/result audit entries 接續正確，完整 chain 驗證通過。

### 9.3 Rollback / closeout

- [ ] rollback preview 在 revert 前產生，且只指向 write commit。
- [ ] `git revert` 產生可追溯 revert commit；target 消失、其他檔不變。
- [ ] rollback 後最小測試與完整 tests 全綠；audit chain 再次驗證通過。
- [ ] token 重放失敗，gate 已回 deny-all，無 retry/dispatch/runtime 殘留。
- [ ] Owner 檢視 packet、audit、write/revert commits、測試原文並簽核或拒絕 v1.1。
- [ ] Closeout 明寫：v1.1 成功不授權 v1.2、其他檔案寫入或常態 execution。

## 10. 未解設計項（實作前 Owner 裁決）

1. 新 packet contract 的正式檔名、schema version 與欄位正本；
2. token digest/記憶體 registry 的正式介面、expiry 與 consume 原子性；
3. 最終 exact target 與 exact bytes；
4. write/revert commit author identity 與 commit message；
5. 首次 v1.1 是否強制在同一 session 完成 rollback rehearsal；
6. Phase 7 對 v1.1 audit event 是否需新 schema（若需即先 HOLD，另開設計包）；
7. Windows/WSL 支援平台上的 exclusive-create、symlink 與 path canonicalization 規格。

在上述項目、v1.0 closeout 與新 Owner instruction 完成前，本設計永遠停在 planning，
不可轉為實作或執行。
