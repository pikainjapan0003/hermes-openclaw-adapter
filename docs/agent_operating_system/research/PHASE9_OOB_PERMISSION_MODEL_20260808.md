# Phase 9 OOB 專用群組權限模型（2026-08-08）

## 1. 狀態與範圍

本檔記錄 NIGHT-BATCH-33 對 regular-file OOB reader 的實作決定。它只修復
Owner 回應檔的本機讀取權限死結，不是 Phase 9 執行授權，也不改變
`05_VERIFIED_LONG_TERM_PLAN.md` §6.13 第 3 條的「Owner 在場＋單次 token」硬閘。
真實 OpenClaw 呼叫、真實 token 產生與 `--real` 仍維持禁止。

這項權限規則不存在於任何 Owner 裁決。`05` §6.18 的 OOB-C 只要求 Owner
在不同本機使用者的專用終端輸入；舊的 `mode & 0o077 == 0` 是 NB-31
實作自行加入的判斷。因此本次是實作層修正，不是修改 Owner 的安全語意。

## 2. 舊規則為何無解

舊 reader 同時要求：

1. 回應檔由 `hermes-owner`（uid 1001）擁有；
2. gate（uid 1000）能以 `rb` 開啟；
3. group 與 other 的九個權限位全部為零。

在 Owner 與 gate 是不同 uid 時，第三項會切斷 gate 唯一可用的讀取路徑。
以下四種模式已用真實檔案模式位驗證；「可讀」欄描述 gate 位元層是否有路徑，
「舊規則」是原判斷式的結果：

| 模式 | gate 位元層可讀 | 舊規則接受 | 結果 |
|---|---:|---:|---|
| `0600` | 否 | 是 | reader 判綠，但不同 uid gate 無法 `open("rb")` |
| `0640` | 是（經 group） | 否 | gate 可讀，但 reader 主動拒絕 |
| `0644` | 是（經 other） | 否 | reader 拒絕；且暴露給所有人 |
| `0604` | 是（經 other） | 否 | reader 拒絕；且暴露給所有人 |

所以不存在同時滿足「不同 uid 可讀」與舊權限判斷的模式。

## 3. 新規則

regular-file OOB 回應只接受以下條件的 AND：

1. 檔案 owner uid 等於 execution-day 注入的 expected Owner uid；
2. 檔案 group gid 等於 execution-day 注入的專用 group gid；
3. 系統查得的 group 名稱與注入名稱一致；
4. 該 group 的完整成員 uid 集合嚴格等於 `{gate uid, Owner uid}`；
5. 模式嚴格等於 `0640`：Owner 可讀寫、專用群組唯讀、other 無任何權限；
6. 既有 regular-file、no-symlink、大小、期限、principal 與 payload 驗證全部保留。

群組名稱、gid、gate principal 與 Owner principal 都由建構參數注入，程式沒有
硬編 `phase9-oob`。production resolver 同時納入 primary-group 與 supplementary-
group 成員；多一人、少一人、名稱／gid 漂移或查詢失敗皆 fail-closed。

## 4. 放寬了什麼

唯一放寬是：舊規則禁止所有 group access；新規則允許一個經明確指定、成員集合
精確受限的專用群組具有 read 權限。沒有放寬 other；other 任一 read、write 或
execute 位元仍被拒絕。也沒有允許 gate 寫檔：`0640` 的 group 只有 read。

這仍符合安全目的，因為可讀集合只從「Owner 一人」擴成「Owner＋gate」，而 gate
本來就是必須讀取該回應的驗證主體。任何第三位本機使用者進入群組都會讓完整成員
集合不相等，reader 直接拒絕。

## 5. 新舊結果對照

| 模式 | 舊規則 | 新規則（owner/group/membership 均正確） |
|---|---:|---:|
| `0600` | 接受 | 拒絕：gate 無 group read |
| `0640` | 拒絕 | 接受 |
| `0644` | 拒絕 | 拒絕：other read |
| `0604` | 拒絕 | 拒絕：other read |

此外，`0640` 在 group gid 不符、group 成員不精確或 owner uid 不符時仍拒絕。

## 6. 證據邊界

測試能以真實 ext4 檔案驗證四種 mode、symlink/regular-file 行為及唯讀性；但
測試行程無權把檔案 chown 成另一個 uid。跨 uid 成功路徑因此明確標成模擬，僅
替換 stat identity，不能宣稱端對端完成。真正的 Owner→gate 驗證仍須 Owner
依唯讀自檢工具印出的兩步流程，在 `hermes-owner` 與 gate 兩個視窗各做一步。

## 7. 不變的硬閘

- 本次未建立系統群組、未修改 `/var/hermes-phase9`，也未寫正式 OOB 回應檔。
- 找不到專用群組、成員集合不精確或 gate 讀不到檔案，一律停止。
- 自檢綠燈只證明檔案身分與權限可供 gate 讀取，不是 token 或執行授權。
- `--real`、真實 token、OpenClaw 呼叫與自動重試全部維持鎖定。
