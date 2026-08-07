# Phase 9 實作交付物清單（2026-08-07 建立）

## 0. 這份檔為什麼存在

`05_VERIFIED_LONG_TERM_PLAN.md` 的 Phase 9 節描述「執行日會發生什麼」與「事後要交出什麼報告」，
但從未列出「要先做出哪些程式，那一天才跑得起來」。NIGHT-BATCH-25 到 30 共六批實作，
因此是在沒有對照清單的情況下逐批推導出來的——做完一塊，再想下一塊。

2026-08-07 盤點時發現 `PresenceChannel` 至今沒有具體實作，而 `Phase9Gate` 在 `app/` 內
零建構點：稽核與審查一直把「零建構點」當成**安全證據**（它確實是），但沒有人反過來問
「那執行日由誰來建構它」。答案是目前沒有人。同一個事實有兩面，先前只看了有利的那一面。

本檔補上那一欄。**它是盤點與缺口清單，不是授權**——列在「未完成」不代表可以逕行實作，
仍受 `05` §6.13 第 3 條硬閘與各項 Owner 裁決約束。

## 1. 已完成（截至 master `4dc5df6`）

`app/` 內 8 個模組、`tests/` 內 9 個檔、232 個 Phase 9 測試全綠。
首個模組落地 2026-08-04，最新 2026-08-07。

| 交付物 | 具體實作 | 首次落地 |
|---|---|---|
| 單次 token 結構與驗證 | `app/phase9_token.py` | `130364b`（2026-08-04） |
| 在場六判準計算 | `app/phase9_presence.py` | `e3a587f`（2026-08-04） |
| 中止情境與回報碼 | `app/phase9_abort.py` | `145949c`（2026-08-04） |
| 執行閘門與十三步 trace | `app/phase9_gate.py` | `d21a619`（2026-08-04） |
| 作廢帳本（擋人層 `B-A`） | `app/phase9_burn_ledger.py` → `FileBurnLedger` | `8817360`（2026-08-05） |
| 作廢證據事件（證據層 `B-C`） | `app/phase9_burn_evidence.py` | `d19cfa4`（2026-08-06） |
| 稽核鏈寫入者 | `app/phase9_audit_chain_writer.py` → `LocalAuditChainWriter` | `79eb6a1`（2026-08-07） |
| 真實執行器與版本探針 | `app/phase9_openclaw_executor.py`＋`app/phase9_gate.py` | `cb283d2`（2026-08-07） |
| 稽核授權驗證器 | `app/phase9_gate.py` 的 `AuditAuthorizationVerifier` | NIGHT-BATCH-29 |
| 檔案系統快照器 | `app/phase9_gate.py` 的 `DirectorySnapshotter` | NIGHT-BATCH-25 |
| 六步閉環演練（全假件） | `tests/test_phase9_n1_rehearsal.py`＋`research/PHASE9_N1_REHEARSAL_DRYRUN_20260807.md` | `bbfc013`（2026-08-07） |

## 2. 未完成——執行日跑不起來的原因

`app/phase9_gate.py` 定義 8 個注入式 Protocol，其中 3 個至今沒有任何具體實作：

| 缺口 | Protocol | 為什麼那天需要它 |
|---|---|---|
| Owner 互動管道 | `PresenceChannel` | 執行日顯示挑戰、收 Owner 回應的那條路。§6.18 選 `OOB-C`＝Owner 於**不同本機使用者**的專用終端輸入，不得用模型所在終端或聊天室 |
| 預檢驗證器 | `BooleanGateVerifier` | 十三步的 preflight 重驗；目前只有測試替身 |
| gate/token 協調鎖 | `GateTokenAuditCoordinationLock` | 跨元件互斥；目前只有測試替身 |
| token 產生與發放 | （無 Protocol） | §6.18 選 `T-B`＝另外授權的產生器隨機產生一次，Owner 看見後親自經 `OOB-C` 回送 |
| **執行日進入點** | （無） | `Phase9Gate` 目前只在 `tests/` 內被建構，`app/` 零建構點。**沒有任何腳本能在執行日把它跑起來** |

## 3. 環境前置（與程式無關，Owner 自行準備）

`OOB-C` 要求一個屬於**不同本機使用者**的專用終端。`PHASE9_OWNER_BRIEF.md` 明文：
若專用不同身分終端無法準備，設計**不得**偷偷改用聊天室或模型終端，應停止並另提離機裝置方案。

`app/phase9_gate.py` 的 `EXPECTED_OPENCLAW_VERSION` 為釘死常數。執行日探測到不符即中止；
而實作期間禁止執行任何 openclaw 子命令（`05` §6.20 第 2 條），故版本相符與否只能在執行日當場得知。
提早中止屬煞車正常運作，非失敗。

## 4. 維護規則

新增或完成任何一項時同步更新本檔，並在 `05` §5 狀態表的 Phase 9 列反映實況。
**本檔只記錄實作盤點，不得用來主張任何授權或解鎖**；授權一律以 `05` 第 6 節的 Owner 裁決為準。
