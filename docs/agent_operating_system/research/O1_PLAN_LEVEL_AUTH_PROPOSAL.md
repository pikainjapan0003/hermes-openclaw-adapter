# O1 提案稿：計劃級授權格式

Status: **PROPOSAL ONLY — OWNER NOT DECIDED**

本文件只提出資料與治理選項，不修改 `01_SAFETY_BOUNDARIES.md`，不建立授權
gate，不允許 dispatch/runtime，不讓 approval event 變成 execution permission。

**未裁決前 AUTO 級照 01 §2/§4 逐字授權（fail closed）。**

## 1. O1 要解的問題

05 §6.11 O1 的問題是：Owner 批准 Hermes 切分的一份計劃後，未來系統如何讓
計劃內明列的 `AUTO`、唯讀、無害子任務在精確邊界內並行，而不要求 Owner 對每一個
子任務重貼相同授權句。

O1 不處理：

- `OWNER_APPROVAL` 寫入或副作用任務；
- `OWNER_MANUAL` 花錢、不可逆或結構性不可派發任務；
- runtime/worker/queue/dispatch 的實作或解鎖；
- 跨計劃、跨資源、跨角色的常態白名單；
- Phase 7、Phase 9、v1.1/v1.2 的專屬 Owner 硬閘；
- 以 dashboard、Hermes 建議、decision event、測試綠或過往 instruction 代替
  Owner instruction。

計劃級授權若將跨 session 生效，與 01 §4.2「跨 session 不繼承」有直接衝突；
因此任何方案落地前都必須由 Owner 明示是否修改 01 §4，不能靠本提案推定例外。

## 2. 三案共同的不可放寬條件

不論選哪案，正式格式都應具備：

1. **Owner sole approver**：唯一權威仍是 active Owner instruction 的逐字內容；
2. **Manifest immutability**：授權綁定 `plan_id` 與整份 manifest SHA-256，任何
   byte/field 變化使授權失效；
3. **Exact allowlist**：每個 task 明列 task id、action、resource、role、
   `execution_class=AUTO`、allowed reads、forbidden writes、timeout 與最大次數；
4. **Deny by default**：不在 allowlist、分類不確定、資源或參數不一致即 HOLD；
5. **No derived tasks**：模型不得從 goal、parent task、相鄰 task 或「完成所需」推導
   新的 AUTO 權限；新增/拆分後的新 id 必須重新授權；
6. **No side-effect promotion**：任何 write、send、call、queue、audit、connector、
   external side effect 都不能被 AUTO manifest 包含；
7. **Bounded lifetime**：明列 session/expiry、最大 task count、最大總次數與 revoke；
8. **Role binding**：只允許 manifest 指定的角色；role prompt 本身不是權限來源；
9. **Auditability without secrets**：記錄 plan/manifest hash、Owner quote、task outcome，
   不記 secret/token；
10. **No implicit dispatch**：計劃級授權只是未來 gate 的一項輸入；在 runtime/dispatch
    另案授權前，不得因資料驗證通過而啟動 worker；
11. **Nested hard gates win**：Phase 7、Phase 9、v1.1/v1.2 或 01 F2 類型的更嚴格
    授權永遠優先，不能被 O1 包住；
12. **Revocation is immediate**：Owner revoke、manifest 漂移、expiry、事故或 trust
    scan 失敗後，尚未開始的 task 全部失效；進行中只允許安全停止。

## 3. 共通 manifest 最小欄位

正式 schema 尚未裁決；以下只是三案比較時共用的資料需求。

| 欄位 | 用途 | Fail-closed 規則 |
|---|---|---|
| `plan_id` | 計劃唯一 id | 缺失、重用或格式不符即拒絕 |
| `manifest_version` | 格式版本 | gate 不認識的版本即拒絕，不做寬鬆轉換 |
| `manifest_hash` | canonical manifest SHA-256 | 重算不符即全計劃失效 |
| `owner_instruction_quote` | 可逐字引用的 Owner 授權 | 空白、轉述、前 session 引用即拒絕 |
| `issued_at` / `expires_at` | 時間邊界 | 過期、時鐘不可信即拒絕 |
| `session_scope` | 是否只限本 session | 未明列即採本 session、不可繼承 |
| `max_tasks` / `max_total_attempts` | 計劃配額 | 超過即拒絕；失敗 attempt 也計數 |
| `allowed_roles` | 可接 task 的角色 | role 不符即拒絕 |
| `tasks[]` | exact task allowlist | 每項必為 AUTO 且完整綁定 action/resource |
| `forbidden_capabilities[]` | 顯式 deny list | 至少含所有 write/dispatch/runtime/connector 類別 |
| `revoked_at` / `revocation_reason` | Owner 撤銷 | 非 null 即全計劃拒絕 |

每個 `tasks[]` 項目還應固定 `task_id`、`parent_task_id`、`action_type`、精確
read target、參數 hash、role、timeout、max attempts、expected output shape、資料敏感
級別與 `execution_class=AUTO`。不得含 command string、script、通用 URL pattern、
filesystem glob 或「及完成所需的其他動作」等開放語句。

## 4. 方案 A：一句話總授權＋不可變白名單附錄

### 格式

Owner instruction 內放一條固定語法的總授權句，逐字引用 `plan_id`、manifest hash、
expiry 與最大 task 數；同一 instruction 附上或指向 byte-frozen allowlist manifest。

規劃示例，不是授權：

> [OWNER-INSTRUCTION-START] 批准計劃級授權 plan_id=P-EXAMPLE，僅限
> manifest_sha256=EXAMPLE 所列 AUTO 唯讀任務，max_tasks=3，expires_at=EXAMPLE；
> 不含任何寫入、副作用、OWNER_APPROVAL、OWNER_MANUAL 或新拆分任務。
> [OWNER-INSTRUCTION-END]

Gate 必須同時驗 quote 與 manifest hash；只看到其中一個一律不生效。Owner edit
manifest 後必須提供新 hash 與新 instruction，不能沿用舊總授權。

### 優點

- 最接近 01 §2/§4 現行「逐字句子＋精確範圍」，fresh-context 容易核對；
- 人可讀、Git diff 可審、弱模型只需 exact-match，不必判斷自然語言好壞；
- 可一次涵蓋數個 N 小、同一計劃內的 read-only tasks；
- 撤銷可用 plan id/hash 精確指向，不需要管理多個能力 token。

### 風險

- instruction 與附件若分離、附件可變或 hash canonicalization 不明，會發生 TOCTOU；
- 一句總授權容易被模型誤讀成 goal 級無限權限；
- plan 拆分後新增 task id 容易被錯當「同一計劃自然包含」；
- 若允許跨 session，必須正式修改 01 §4，否則與正本衝突。

### 弱模型誤讀面與防護

| 誤讀 | 必要防護 |
|---|---|
| 「Owner 批計劃＝批准所有完成 goal 所需動作」 | gate 只認 manifest 中 exact task id；衍生 task 永遠拒絕 |
| 「同一 parent_task_id 都算已授權」 | parent 只作引用，不作授權繼承 |
| 「AUTO 天生不用授權」 | manifest 無有效 Owner quote/hash 即 HOLD |
| 「失敗可以重試直到成功」 | attempt 也扣配額；max attempts 預設 1 |
| 「總授權也包含 dispatch」 | manifest validation 與 worker start 分離；沒有另案 runtime gate 就不啟動 |

## 5. 方案 B：逐計劃結構化簽核欄

### 格式

建立 `plan_authorization` contract；Owner instruction 逐字批准一個 authorization id，
而 contract 內使用結構化欄位記錄 manifest hash、scope、expiry、task allowlist 與
Owner decision。Dashboard 只顯示；正式 gate 必須同時持有 active instruction quote
與 schema-valid contract。

### 優點

- schema 可機械驗證 `additionalProperties: false`、AUTO-only、配額與 expiry；
- UI 可清楚呈現範圍，Owner 容易逐欄檢查；
- 適合未來 audit 與多 worker 引用相同 authorization id；
- 欄位版本化比純自然語言更容易遷移。

### 風險

- 最容易重演「decision event is not dispatch」混淆：資料列 `approved` 不能自己觸發；
- schema-valid 不代表 Owner 真正看過或 active instruction 存在；
- dashboard button 或資料庫欄位可能被錯接成 dispatch hook；
- 需要新 schema、validator、builder、顯示與 negative tests，實作面明顯較大。

### 弱模型誤讀面與防護

| 誤讀 | 必要防護 |
|---|---|
| 「`decision=approve` 就可執行」 | active Owner quote 與 manifest hash 是獨立必備條件；contract 只是資料 |
| 「schema 過了就代表安全」 | classification、exact target 與 read-only deny list 必須另驗 |
| 「舊 authorization 可套新 manifest version」 | authorization id、schema version、manifest hash 三者全綁定 |
| 「dashboard 顯示的 approved 是 runtime permission」 | 顯示層永遠 GET-only；AST 測試禁止 approve→dispatch |

## 6. 方案 C：限額 capability token 配額制

### 格式

Owner 對 plan 發一個短效、不可轉移的 capability token。token 綁 manifest hash、
allowed roles、max tasks/attempts、expiry；每個 task consume 一份配額。raw token 只存
記憶體，持久化資料只記不可逆 digest 與 consume ledger。

### 優點

- 可機械化 expiry、replay、配額與撤銷；
- 高並行時可用原子 consume 控制總量；
- scope digest 可精確綁定 plan/task/resource；
- 若未來跨 process，能力生命週期比文字簽核更容易觀測。

### 風險

- 對目前成熟度過度複雜；token store、原子 consume、時鐘、recovery 都是新攻擊面；
- token 容易被弱模型當成「有 token 就都可做」，忽略 action/resource/classification；
- 洩漏、重放、partial consume 與跨 worker race 需要大量負向測試；
- 名稱可能與 Phase 9/v1.1 single-use execution token 混淆；
- 任何持久化 ledger 都會觸發新的寫入與 Owner 授權，不能夜跑偷做。

### 弱模型誤讀面與防護

| 誤讀 | 必要防護 |
|---|---|
| 「token 存在＝全部 AUTO 可做」 | 每次仍驗 manifest/task/action/resource/role 全綁定 |
| 「剩餘配額可拿來跑新 task」 | quota 只屬 allowlisted task ids，不能轉移 |
| 「失敗不算使用」 | consume-before-start，任何 attempt 都扣配額 |
| 「Phase 9 token 可當 O1 token」 | 不同 contract、prefix、issuer、audience 與 gate；跨類型必拒 |

## 7. 比較

| 維度 | A 總授權＋附錄 | B 結構化簽核 | C token 配額 |
|---|---|---|---|
| 與現行 01 相容度 | 高；仍以逐字 Owner quote 為根 | 中；必須避免資料列取代 quote | 低；需新能力基礎設施 |
| 弱模型判斷負擔 | 低：exact quote/hash/task match | 中：多一層 contract/quote 關係 | 高：token、scope、ledger、race |
| 人工可審性 | 高 | 高 | 中 |
| 並行控制 | 以 task/attempt 上限約束 | 以 schema/gate 約束 | 原子配額最好，但實作最重 |
| 洩漏/重放面 | 低 | 低至中 | 高 |
| 最小可行實作 | 最小 | 中 | 最大 |
| 建議時機 | 首次 O1 落地 | A 穩定後若需 dashboard/audit | 多 worker 高並行且需求被證明後 |

## 8. 建議案

建議 Owner 選 **方案 A：一句話總授權＋不可變白名單附錄**，並加上以下硬限制：

1. 首版只限單 session、`AUTO`、read-only、最多 3 tasks、每 task 1 attempt；
2. Owner quote 必須逐字包含 plan id、manifest hash、expiry、max tasks；
3. manifest canonicalization 與 hash 規格需先獨立拍板；
4. 每項 task 必須列 exact read resource，不接受 wildcard、自然語言延伸或子任務繼承；
5. 任何 write、副作用、connector、runtime/dispatch、Phase 7/9、v1.1/v1.2 都明示排除；
6. 第一版不跨 session，因此不需先放寬 01 §4.2；若未來需要跨 session，再由 Owner
   正式修改 01；
7. 先完成 contract 與 fail-closed tests，再另案決定是否實作 runtime gate；兩者不能
   同包，更不能把 contract valid 直接接上 worker。

方案 B 可作第二階段的顯示/audit 正規化，但仍不能取代 active Owner quote。方案 C
暫不建議；只有多 worker 並行已真實出現配額競爭，且 §6.11 T3 重審完成後才值得考慮。

## 9. Owner 裁決欄（目前空白）

Owner 尚未選 A/B/C，也尚未批准本提案任何句型、欄位或 gate。正式裁決至少需回答：

1. 選 A、B、C 或退回；
2. 是否只限單 session；
3. 首版 max tasks、attempts、expiry；
4. manifest hash canonicalization 正本；
5. 是否以及何時修改 01 §4；
6. 哪些角色與 read-only resource 類型可進首版 allowlist。

未取得裁決前，現況不變：每個 AUTO task 都必須依 01 §2/§4 在 active Owner
instruction 中找得到逐字授權；找不到、語意模糊或 scope 不符即 HOLD。
