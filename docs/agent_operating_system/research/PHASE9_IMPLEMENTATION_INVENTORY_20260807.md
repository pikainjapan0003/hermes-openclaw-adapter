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

## 1. 已完成與接線狀態（截至 NIGHT-BATCH-32）

首個模組落地 2026-08-04。NIGHT-BATCH-32 的 C1 至 C4 分別完成：必填 Owner principal
（`69727a9`，清單雜湊更新 `b626740`）、真實 regular-file OOB reader 接線（`d237194`）、
rehearsal issuer 接線（`7c66d05`），以及 Owner 唯讀自檢工具（`7a2b596`）。

「零件存在」與「已被正式流程接線」是兩件事。下表的接線欄必須同時回答由誰建構、被誰呼叫；
若只有測試使用，或 formal／real 分支仍無呼叫者，便明確標示未接線。

| 交付物 | 具體實作 | 首次落地／本次更新 | 接線檢查（建構者 → 呼叫者） |
|---|---|---|---|
| 單次 token 結構與驗證 | `app/phase9_token.py` | `130364b`（2026-08-04） | `Phase9TokenIssuer` 建構 token；`Phase9Gate` 驗證 presentation。已接線於固定向量 rehearsal，formal 仍鎖。 |
| 在場六判準計算 | `app/phase9_presence.py` | `e3a587f`（2026-08-04） | `Phase9Gate` 直接呼叫。已接線。 |
| 中止情境與回報碼 | `app/phase9_abort.py` | `145949c`（2026-08-04） | gate、issuer 與相關元件建構／拋出中止狀態。已接線。 |
| 執行閘門與十三步 trace | `app/phase9_gate.py` | `d21a619`（2026-08-04） | `scripts/run_phase9_n1.py` 建構並呼叫；`app/main.py` 與 `app/worker.py` 未呼叫。獨立 rehearsal 已接線，應用 runtime 未接線。 |
| 作廢帳本（擋人層 `B-A`） | `app/phase9_burn_ledger.py` → `FileBurnLedger` | `8817360`（2026-08-05） | N=1 進入點建構後注入 `Phase9Gate`，由 gate 呼叫。已接線於 rehearsal workspace。 |
| 作廢證據事件（證據層 `B-C`） | `app/phase9_burn_evidence.py` | `d19cfa4`（2026-08-06） | `Phase9Gate` 在作廢後建立證據事件。已接線。 |
| 稽核鏈寫入者 | `app/phase9_audit_chain_writer.py` → `LocalAuditChainWriter` | `79eb6a1`（2026-08-07） | N=1 進入點建構後注入 `Phase9Gate`，由 gate 呼叫。已接線於 rehearsal workspace。 |
| 真實執行器與版本探針 | `app/phase9_openclaw_executor.py`＋`app/phase9_gate.py` | `cb283d2`（2026-08-07） | rehearsal 只建構受控假 executor 與假 version runner；formal real executor 沒有允許的建構／呼叫路徑。未接線。 |
| 稽核授權驗證器 | `app/phase9_gate.py` 的 `AuditAuthorizationVerifier` | NIGHT-BATCH-29 | N=1 進入點建構後注入 `Phase9Gate`，由 gate 呼叫。已接線於 rehearsal。 |
| 檔案系統快照器 | `app/phase9_gate.py` 的 `DirectorySnapshotter` | NIGHT-BATCH-25 | N=1 進入點建構後注入 `Phase9Gate`，由 gate 呼叫。已接線於隔離 workspace。 |
| 六步閉環演練（全假件） | `tests/test_phase9_n1_rehearsal.py`＋`research/PHASE9_N1_REHEARSAL_DRYRUN_20260807.md` | `bbfc013`（2026-08-07） | 只由測試建構／呼叫；不是執行日入口。測試接線。 |
| Owner 互動管道 | `app/phase9_presence_channel.py` | `952bb61`；`d237194` 接入真實 reader | N=1 進入點依模式建構 `JsonPresenceChannel`；`Phase9Gate` 呼叫。regular-file reader 已接線，真實跨 uid 尚未由 Owner 驗證。 |
| 凍結預檢驗證器＋有界協調鎖 | `app/phase9_preflight.py` | `2e491df`（NIGHT-BATCH-31） | N=1 進入點建構後注入 `Phase9Gate`，由 gate 呼叫。已接線於 rehearsal。 |
| 執行日 N=1 進入點（真實模式仍鎖） | `scripts/run_phase9_n1.py` | `6598eba`；`69727a9`、`d237194`、`7c66d05` 更新 | 由 Owner 手動 CLI 呼叫；未由 `app/main.py` 或 `app/worker.py` 呼叫。獨立入口已接線，正式 real 分支未接線。 |
| runner 必填注入＋演練 process instrumentation | `app/phase9_gate.py`＋既有 rehearsal | `7061a41`（NIGHT-BATCH-31） | N=1 進入點注入受控 runner，gate 呼叫；真實 runner 無建構者。rehearsal 已接線，formal 未接線。 |
| token 產生與 OOB 發放邊界 | `app/phase9_token_issuer.py` | NIGHT-BATCH-31；`7c66d05` 接線 | N=1 進入點以固定向量建構並呼叫 issuer；`for_formal_runtime` 僅由 `tests/test_phase9_token_issuer.py` 建構／呼叫。rehearsal 已接線，formal 只有測試接線、runtime 未接線。 |
| Owner OOB 接線自檢 | `scripts/check_phase9_oob_wiring.py` | `7a2b596`（NIGHT-BATCH-32）；NIGHT-BATCH-33 修正兩步流程 | Owner 先在 `hermes-owner` 終端建立檔案並離開，再由 gate／lnovo 終端手動呼叫；工具唯讀核對 writer uid、專用群組與精確 0640 權限。真實 Owner→gate 執行結果尚未完成。 |

## 2. 經接線核對後仍未完成

下列項目是逐一查過建構者與呼叫者後仍存在的缺口或執行日硬閘；不再以「零件都有」推論
「沒有程式缺口」。

| 尚未完成事項 | 已核對現況 | 真正缺少什麼 |
|---|---|---|
| formal token 產生與一次性 Owner 發放 | `for_formal_runtime` 使用 deny verifier，且只有測試呼叫；固定向量 rehearsal 可走 | 當次 Owner 授權、真實在場驗證器，以及獲准的 formal runtime 建構／呼叫路徑 |
| 進入點真實模式與 real executor | `--real` 在建構 executor 前拒絕；真實 executor 呼叫數保持零 | 當次執行授權，以及通過另案審查的 formal 接線；目前刻意未實作可執行分支 |
| 真實跨 uid OOB 驗證 | regular-file reader 與唯讀自檢工具已存在；測試只做身份模擬 | Owner 必須在 `hermes-owner` 終端建立檔案後離開，再由 gate／lnovo 終端執行唯讀自檢；未做前不得宣稱端對端完成，Owner 在自己終端讀自己檔案不算證據 |
| 正式執行環境版本確認 | 版本常數已釘死；本批從未執行 OpenClaw 子命令 | 只能在獲授權的執行日探測並比對版本 |

## 3. 本次清單失準的教訓

原清單列的是**零件**，沒有列**零件之間的接線**。五個零件全數打勾後，結論便寫成
「沒有程式缺口」，但實際上沒有人接線：進入點仍在讀一個不存在的 `uid:2000`，Owner 回應仍由
程式自己合成，issuer 也沒有被入口呼叫。這與先前只看到 `PresenceChannel` 類別存在、卻沒有追問
誰建構它，是同一個盲點。

後續盤點每一項都必須追問：「誰建構它、誰呼叫它、哪一條真實入口會走到它？」若答案只指向
測試，便只能標成測試接線；若 real／formal 分支沒有呼叫者，必須標示「未接線」，不能用零件存在
替代整合證據。

## 4. 環境前置（Owner 自行準備）

`OOB-C` 要求一個屬於**不同本機使用者**的專用終端。`PHASE9_OWNER_BRIEF.md` 明文：
若專用不同身分終端無法準備，設計**不得**偷偷改用聊天室或模型終端，應停止並另提離機裝置方案。

`app/phase9_gate.py` 的 `EXPECTED_OPENCLAW_VERSION` 為釘死常數。執行日探測到不符即中止；
而實作期間禁止執行任何 openclaw 子命令（`05` §6.20 第 2 條），故版本相符與否只能在執行日當場得知。
提早中止屬煞車正常運作，非失敗。

## 5. 維護規則

新增或完成任何一項時同步更新本檔，並在 `05` §5 狀態表的 Phase 9 列反映實況。
**本檔只記錄實作盤點，不得用來主張任何授權或解鎖**；授權一律以 `05` 第 6 節的 Owner 裁決為準。
