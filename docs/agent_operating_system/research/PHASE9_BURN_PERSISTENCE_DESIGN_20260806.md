# Phase 9 作廢紀錄持久化設計（2026-08-06）

Status: **Phase 9 稽核寫入授權已於 2026-08-06 取得（§6）。實作授權與執行授權
仍未給予。**

本文記錄 2026-08-06 Owner 就「token 作廢紀錄要寫到哪裡」所做的決定、據此產生
的設計，以及當日取得的稽核寫入授權。本文**不授權**呼叫 OpenClaw，也不解除
任何其他閘門。

---

## 0. 為什麼會有這份文件：一個未被發現的偏差

2026-08-04 Owner 於 `05` §6.18 拍板的 burn/persistence 選案是 **`B-C`**
（把作廢事件寫進 Phase 7 的雜湊鏈）。

但 NIGHT-BATCH-26～28 實際做出來的 `app/phase9_burn_ledger.py`（`FileBurnLedger`）
是一個**獨立檔案**，路徑由呼叫端注入、模組本身不選 `data/`。就
`PHASE9_TOKEN_DESIGN.md` §5 的分類而言，那是 **`B-A`（Separate token marker
file）**，不是 `B-C`。

`app/phase9_*.py` 四個檔案**沒有任何一行 append 稽核事件**——`hash_chain`
只被當作 `canonical_json` 序列化工具使用（`phase9_gate.py:26`、
`phase9_burn_ledger.py:21`、`phase9_token.py:20`）。

**責任歸屬**：NIGHT-BATCH-26 派工單由派工者撰寫，未對照 §6.18 的選案即直接
寫「burn ledger」。三批四份雙審均未攔下，因為各批紅線只檢查「不得寫入
`data/`」，方向恰與此偏差一致。此為派工方缺陷，非實作方缺陷。

---

## 1. Owner 決定（2026-08-06）

| # | 問題 | Owner 決定 |
|---|---|---|
| 1 | 作廢紀錄放哪 | **兩層都要**：`FileBurnLedger` 負責擋住重複執行；稽核鏈另記一筆作為防篡改證據 |
| 2 | 在哪個環境執行 | **把稽核鏈從 Windows 工作副本搬到 WSL 正牌 repo，之後在 WSL 執行** |
| 3 | 稽核鏈那一筆要不要動 schema | **不動**。用既有欄位表達，不新增欄位、不改 `docs/schemas/` |
| 4 | 授權涵蓋幾個目標 | **一份授權涵蓋兩個目標**（原提問為「幾句授權句」，該提問本身係誤加儀式，見 §6.3） |
| 5 | 授權效期 | **長期有效，直到 Owner 收回**（非逐場給予）。理由：真正的執行閘是「Owner 在場＋當日臨場授權」，記帳本身不呼叫任何東西 |

Owner 同時陳述其最終目的（逐字）：

```text
本身要讓你們AI好維護就好，我最終目的只要看到監控板(replit)、Hermes與
openclaw 結果都能看得到這樣就好了
```

此陳述**不是授權**；Replit 接線仍為獨立的未授權 Owner 閘。

---

## 2. 兩層各自的職責

| 層 | 檔案 | 職責 | 現況 |
|---|---|---|---|
| 擋人層 | `data/phase9_burn.jsonl` | 跨行程單發保證。`contains()` 命中即拒絕 | 程式已完成（NB-26～28），四份雙審通過；**路徑未定案、未授權寫入** |
| 證據層 | `data/audit_dev.jsonl` | 防篡改證據。鏈斷即可偵測 | 檔案存在於 Windows 工作副本；**Phase 9 用途未授權** |

**擋人的是擋人層。** 證據層不參與單發判定，因此不需要重新驗證 NB-26～28 已
證明的跨行程互斥性質。

### 2.1 為什麼證據層有價值

`FileBurnLedger` 對 `FileNotFoundError` 回傳 `[]`
（`app/phase9_burn_ledger.py:245`，Owner 閘，未修改）。因此檔案若被**意外**
刪除，`contains()` 回 False，同一 token 可再燒一次。`05` §6.16 已接受「有意
刪改」為殘餘風險，但「意外重放」在防護範圍內。

稽核鏈的每一筆以 `prev_entry_hash` 與前一筆綁定
（`docs/schemas/blackboard/audit_event.schema.json:116`）。缺筆會造成鏈斷，
**可被偵測**，而非被誤讀為「未發生」。

---

## 3. 執行順序與失敗語意

burn 邊界內，於呼叫 executor **之前**：

```text
1. 擋人層 append → fsync → 實體重讀驗證      （已實作，NB-26～28）
2. 證據層 append → 鏈驗證                     （待實作）
3. 才呼叫 executor
```

**任一步失敗一律不呼叫。**

| 失敗點 | 處置 |
|---|---|
| 步驟 1 失敗 | 依既有 burn 邊界分類（`BURN_NOT_ATTEMPTED`／`BURN_WRITE_FAILED`／`BURN_DURABLE_UNVERIFIED`，見 `PHASE9_ABORT_PLAYBOOK.md` §4.4b）。executor＝0 |
| 步驟 2 失敗 | **擋人層已寫入，token 視同已消耗，當日不得重試**。executor＝0。回報碼須與 §4.4b 的「已落盤」語意一致 |

理由：擋人層先落地，才不會出現「已呼叫但無紀錄」。證據層在呼叫前落地，鏈上
才證明得了「當時確實準備呼叫」。寧可浪費一次嘗試，不可多呼叫一次。

---

## 4. 證據層那一筆的內容（不動 schema）

`audit_event.schema.json` 設有 `additionalProperties: false`（:7），因此
**不得新增欄位**。`event_type`（第 179 行起）與 `event_notes`（第 184 行起）
為自由字串，故新增事件種類**不需要改 schema**。

設計約束（沿用 `PHASE9_TOKEN_DESIGN.md` §5 的既有要求）：

- **不得**放入原始 token。
- **不得**以自由文字編碼結構化 burn 欄位（`event_notes` 只放非機密的人類可讀
  說明）。
- 識別碼一律使用既有的識別碼欄位（`audit_id`／`event_id`／`task_id`／
  `related_result_id`），且只放非機密摘要值。
- `preview_only` 必須為 `false`，`audit_status` 必須為 `persisted`——這兩者
  只有在寫入授權存在時才成立。
- 16 個 `safety_flags` 必須誠實反映當次狀態，特別是
  `openclaw_call_allowed` 與 `external_side_effects_occurred`。

**已知限制（明文記載，不得淡化）**：不動 schema 的代價是這一筆**沒有專用的
token-digest／binding 欄位**。它能證明「某場演練的作廢事件在某時發生過」，
不能提供與擋人層逐欄比對的結構化證據。若日後需要，須另案取得 Owner 對
schema 變更的授權（`PHASE9_TOKEN_DESIGN.md` §5 明列此前提）。

---

## 5. 環境搬移

| 步驟 | 動作 | 中止條件 |
|---|---|---|
| 1 | 在 Windows 工作副本驗證 `data/audit_dev.jsonl` 的雜湊鏈完整 | 鏈不完整 → 停止並回報 Owner |
| 2 | 記錄搬移前 SHA-256（現值 `eef4d7db…c85efc2`） | — |
| 3 | 複製到 WSL 正牌 repo `data/` | 目標已存在 → 停止，不得覆蓋 |
| 4 | 搬移後重驗鏈，並比對 SHA-256 | 任一不符 → 停止並回報 Owner |
| 5 | 保留來源檔，**不刪除** | — |

`data/` 已被 `.gitignore` 排除（`.gitignore:13`），兩個檔案都不會進 git。
Owner 只需保護這一個資料夾。

**兩個路徑目前皆不存在於正牌 repo**，這是預期狀態：`data/audit_dev.jsonl`
仍在 Windows 工作副本待搬移，`data/phase9_burn.jsonl` 尚未建立。
`data/audit_dev.jsonl` 已列於 `tests/test_docs_drift_guard.py` 的
`INTENTIONALLY_ABSENT_PATH_REFERENCES`；`data/phase9_burn.jsonl` 尚未列入。
該 guard 目前只掃 `docs/agent_operating_system/*.md`（非遞迴），不含本檔所在的
`research/`；若日後擴大掃描範圍，需先登記此路徑，否則 guard 會紅。

---

## 6. Phase 9 稽核寫入授權（2026-08-06 已取得）

**狀態：已取得。** 範圍如下，逐字：

> 允許 Phase 9 gate 在呼叫 OpenClaw 之前，把「這張一次性許可證已作廢」的紀錄
> 寫入下列兩個檔案，且僅限這兩個：
> 1. `data/phase9_burn.jsonl`（專用作廢檔）
> 2. `data/audit_dev.jsonl`（稽核帳本，只新增一筆作廢事件，不改格式）
>
> 長期有效，直到 Owner 收回。

**取得方式**：範圍由 Fable 5 逐條陳述（含上列「不解鎖」清單），Owner 於
2026-08-06 對話中明示同意。**未產生、也不需要 Owner 自行撰寫的逐字授權句**
（理由見 §6.3）。Owner 原話：

```text
計畫內根本不需要授權語，我同意就同意
```

**收回方式**：Owner 以任何明確措辭表示收回即生效。收回後
`Phase9AuditAuthorizationRecord` 立即作廢，gate 回到 fail-closed 拒絕啟動。
收回不需要理由，也不需要特定格式。

### 6.1 這份授權不解鎖的事（逐條）

- 不解鎖對 OpenClaw 的任何呼叫（需 Owner 在場的執行授權，`05` §6.18）。
- 不解鎖由系統決定執行時機。
- 不解鎖稽核鏈的其他用途或其他寫入者。
- 不解鎖 `docs/schemas/` 變更。
- 不解鎖 Replit 或任何遠端接線。
- **不得**沿用或擴張 `05` §6.15 的 Phase 7 授權；反之亦然。

### 6.2 授權紀錄的機械表達

`Phase9AuditAuthorizationRecord`（`app/phase9_gate.py:312`）僅有
`record_id`／`rehearsal_id`／`scope`／`owner_instruction_digest`／
`authorized_at`／`valid_until`，不保留授權原文。

`PHASE9_AUDIT_SCOPE` 現值為 `phase9-pre-call-burn-and-post-attempt`
（`app/phase9_gate.py:39`）；gate 於 scope 不符時拒絕（:665）。

因授權為長期有效（Owner 2026-08-06 選案「乙」），每場演練由系統產生一張紀錄
引用同一份授權：`rehearsal_id` 為當場值，`valid_until` 不得超過該場 Owner
在場時段。**長期有效的是授權本身，不是任何一張紀錄。**

### 6.3 為什麼這裡不需要 Owner 自行撰寫授權句

**這是一項更正。** 本文初版（commit `688ccd7`）曾要求 Owner 自行產生一句
逐字授權句，並據此退回 Owner 的第一次表述。該要求**於計畫內不存在**，係
Fable 5 誤加：

- `05` §6.13 第 3 條列舉的凍結硬閘為：**Phase 7 首次寫入需逐字授權句；
  Phase 9 需 Owner 在場＋單次 token；v1.1/v1.2 解鎖需新的 Owner instruction。**
  Phase 9 這一條寫的是「在場＋單次 token」，**不含**授權句。
- Owner 已於 2026-07-19 與 2026-08-02 兩度裁決免逐次蓋章
  （§6.13 第 2、2b 條）。
- `01` §5 第 (c) 款要求 audit 這類 runtime 寫入必須**明示授權**、不隨其他任務
  附帶——此為「必須明示」，**不是**「必須由 Owner 撰寫特定句式」。Owner 對
  逐條陳述範圍的明示同意即已滿足。

**規則區分**：要授權 ≠ 要儀式。`05` §6.18 中「授權句由 Owner 當天臨場自己想」
的裁決，其適用對象是**執行日的在場證明**（`owner_verbatim_authorization_verified`），
不適用於本項寫入授權。混用兩者即為誤加儀式。

---

## 7. 待修正的既有紀錄（不得默默進行）

| # | 位置 | 需要的修正 |
|---|---|---|
| 1 | `05` §6.18 | 選案由 `B-C` 改為「`B-A` 擋人 ＋ `B-C` 證據」的疊層。須記明原決定、變更理由、日期與決定者。**`05` 目前恰為 500 行（`40` F4 上限），需先壓縮才能加入** |
| 2 | `PHASE9_TOKEN_DESIGN.md` §8 | Burn/persistence 欄同上更新 |
| 3 | NIGHT-BATCH-26 派工單紅線「不得指向 `data/`」 | 撤銷並記明理由。經查無任何機械測試強制此限制，`app/phase9_burn_ledger.py:3` 的 docstring 僅宣告「模組本身不選 `data/`」，該敘述在呼叫端注入 `data/` 路徑時仍然成立，但措辭應澄清 |

---

## 8. 本文構成與不構成的東西

**構成**：§6 是 Phase 9 稽核寫入授權的權威紀錄（2026-08-06 取得，長期有效）。

**不構成**：實作授權與執行授權。呼叫 OpenClaw 仍需 Owner 在場＋單次 token
（`05` §6.13 第 3 條）。gate 在找不到有效授權紀錄時**維持 fail-closed 拒絕啟動**
（`app/phase9_gate.py:745`、:764）——本授權使該紀錄得以被建立，不使 gate 略過
任何其他檢查。
