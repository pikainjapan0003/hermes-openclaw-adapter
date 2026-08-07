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

## 1. 已完成（截至 NIGHT-BATCH-31）

首個模組落地 2026-08-04；NIGHT-BATCH-31 已補齊本檔原列五個程式缺口。
本表只表示「零件存在且測試全綠」，不表示真實 token 或執行已獲授權。

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
| Owner 互動管道 | `app/phase9_presence_channel.py` | `952bb61`（NIGHT-BATCH-31 pkg1） |
| 凍結預檢驗證器＋有界協調鎖 | `app/phase9_preflight.py` | `2e491df`（NIGHT-BATCH-31 pkg2） |
| 執行日 N=1 進入點（預設全假 rehearsal；真實模式仍鎖） | `scripts/run_phase9_n1.py` | `6598eba`（NIGHT-BATCH-31 pkg3） |
| runner 必填注入＋演練 process instrumentation | `app/phase9_gate.py`＋既有 rehearsal | `7061a41`（NIGHT-BATCH-31 pkg4） |
| token 產生與 OOB 發放邊界（formal path 仍拒絕） | `app/phase9_token_issuer.py` | `night-batch-31-phase9-gap05-token-issuer`（本 commit） |

## 2. 未完成——只剩 Owner／執行日硬閘，不是程式缺口

本檔原列五個程式缺口皆已補齊。下列事項刻意不能由本批自行完成：

| 尚未解鎖事項 | 現況 | 為什麼不能在本批完成 |
|---|---|---|
| 真實 token 產生與發放 | formal issuer 綁定 deny verifier；固定向量測試可走 | §6.20 明禁本批產生或發放任何真實 token；只可在 Owner 在場的執行日解鎖 |
| 進入點真實模式 | 預設 rehearsal 可走完整十三步；`--real` 在建構 executor 前拒絕 | 尚無當次執行授權，§6.13 第 3 條硬閘不變 |
| OOB-C 執行環境 | 讀取媒介、路徑與主體皆可注入 | Owner 必須在執行日準備不同本機使用者的專用終端並親自在場 |

## 3. 環境前置（與程式無關，Owner 自行準備）

`OOB-C` 要求一個屬於**不同本機使用者**的專用終端。`PHASE9_OWNER_BRIEF.md` 明文：
若專用不同身分終端無法準備，設計**不得**偷偷改用聊天室或模型終端，應停止並另提離機裝置方案。

`app/phase9_gate.py` 的 `EXPECTED_OPENCLAW_VERSION` 為釘死常數。執行日探測到不符即中止；
而實作期間禁止執行任何 openclaw 子命令（`05` §6.20 第 2 條），故版本相符與否只能在執行日當場得知。
提早中止屬煞車正常運作，非失敗。

## 4. 維護規則

新增或完成任何一項時同步更新本檔，並在 `05` §5 狀態表的 Phase 9 列反映實況。
**本檔只記錄實作盤點，不得用來主張任何授權或解鎖**；授權一律以 `05` 第 6 節的 Owner 裁決為準。
