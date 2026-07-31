# 05 計劃表精簡：規則存檔與前後對照（2026-07-23）

Status: governance archive and mechanical crosswalk. This file preserves every rule
moved or compressed by NIGHT-BATCH-11 package 3. It does not change authority, grant
permission, or replace the current 05 plan.

## 1. Mechanical result

| Check | Before | After | Result |
|---|---:|---:|---|
| `05_VERIFIED_LONG_TERM_PLAN.md` line count | 482 | ≤440 | required |
| Moved completed-phase rule groups | 11 | 11 indexed below | exact |
| Compressed live rule groups | 18 | 18 mapped below | exact |
| Owner decisions or HOLD rules deleted | 0 | 0 | required |

The current compact wording remains in 05. The blocks below are verbatim historical
text from pre-compaction commit `63384b8`, retained so no completed-phase record or
Owner wording disappears.

## 2. Archived §6.3 original — Phase 2 candidate

```text
v1.0 = Owner-supervised Full-chain Baseline
     = Phase 3–7 全部完成
     + Phase 9 的 N=1：一次無害查詢型 openclaw agent 真實調用成功
```

- 包含：本機 Blackboard 讀寫（schema 驗證）、approval packet 流程、dry-run evidence、audit 檔 local write、rollback preview、**一次真實全鏈路查詢調用（零寫入）**。
- 不包含：任何真實寫入型執行（→ v1.1）、真實代碼任務（→ v1.2）、connector read/write（Phase 10，無限期規劃）、production DB、remote API runtime、Dashboard 新控制項。
- 與第一輪定義（Drive 報告建議版）的差異：**Phase 9 N=1 併入 v1.0**（Owner Q4=C）；理由：「傳話中樞的 v1.0」必須證明真的能傳話。
- 本候選仍需 Phase 2 正式簽核（見 6.9），簽核前不得宣稱 v1.0 定義已凍結。

## 3. Archived §6.9 original — Phase 2 checklist

Phase 2 執行時，向 Owner 逐條取得逐字簽核，全部完成才得產出
`02_V1_0_DEFINITION.md` 並宣告凍結：

```text
[ ] 1. v1.0 候選定義（6.3 全文）逐字接受？（含 Phase 9 併入 v1.0）
[ ] 2. 「包含」六項，各自的驗收方式逐項接受？
[ ] 3. 「不包含」各項的推遲去向（v1.1/v1.2/Phase 10）接受？
[ ] 4. 任務三級分類寫入 01 §6 接受？
[ ] 5. 02 文件內記錄簽核行：Owner approved on <date>, instruction quote: <逐字>
```

- 已預裁決（盤問時 Owner 口頭已答，Phase 2 只需正式化，不必重問）：Q4/Q5/Q8 的內容。若 Owner 在簽核時改主意，以新裁決為準並更新本節 6.0 表。

## 4. Archived §6.12 original — Phase 3 construction rulings

包1（Sol+xhigh 設計稿）觸發 fixture 矛盾 HOLD，Owner 裁決如下：

1. **`safety_flags` 正本＝16 面旗、巢狀 boolean object**：14 個共同鍵（synthetic_local_only／mock_only／dry_run／owner_review_required／external_side_effects_allowed／external_side_effects_occurred／blackboard_write_allowed／queue_write_allowed／audit_trail_write_allowed／worker_dispatch_allowed／openclaw_call_allowed／hermes_runtime_allowed／connector_call_allowed／google_sheets_write_allowed）＋ follow_up_allowed ＋ follow_up_requires_owner_confirmation。
2. RC-D fixture 的 17 鍵版（多 read_only／follow_up_task_creation_allowed／dashboard_controls_allowed）與 view model 的 `"key=value"` 字串陣列版一律降為**舊 fixture／顯示層投影**：不進新 schema、不改舊檔，validator 只驗新 contract。
3. 追認包1設計的兩處泛化：公共欄位加 `message_type`、`created_at`（共 9 個公共欄位）；`role`＝產物作者的功能角色（不限 worker）。
4. 包2 交付方式：Codex 於 GitHub 開工作 branch＋PR（不碰 master），Fable 5 審＋本地實跑測試，Owner 按 merge。

## 5. Rule-by-rule crosswalk

| ID | Before rule | After location | Semantic check |
|---|---|---|---|
| C01 | 終局是簡單傳話中樞，權力在 Owner | 05 §6.1 bullet 1 | exact |
| C02 | 單一 AI 包辦流程又難又耗時 | 05 §6.1 bullet 1 | exact |
| C03 | Hermes 拆分、角色 worker 並行、Owner 看錯誤 | 05 §6.1 bullet 1 | exact |
| C04 | 先自身，Vault／pika 待定 | 05 §6.1 bullet 1 | exact |
| C05 | 每週 5+ 小時、2–3 月、無砍點 | 05 §6.1 bullet 2 | exact |
| C06 | 成功是信任；Phase 11 查信任事故 | 05 §6.1 bullet 2 | exact |
| C07 | 增加傳話複雜度預設否決 | 05 §6.1 bullet 3 | exact |
| C08 | 本機 WSL 是唯一開發工作區 | 05 §6.5 bullet 1 | exact |
| C09 | GitHub master 為王、單向同步、同步仍需授權 | 05 §6.5 bullet 2 | exact |
| C10 | Replit 只拉 GitHub、不可改碼、有時間戳 | 05 §6.5 bullet 3 | exact |
| C11 | Claude Code 是施工介面、非 Hermes | 05 §6.5 bullet 4 | exact |
| C12 | ChatGPT 5.5 由 Owner 搬運、異步顧問 | 05 §6.5 bullet 5 | exact |
| C13 | 手機看／批；Replit 登入牆 | 05 §6.5 bullet 6 | exact |
| C14 | Blackboard 位於 repo `data/` JSON、隨 git | 05 §6.7 bullet 1 | exact |
| C15 | 本機→GitHub→Replit、最後 push、時間戳 | 05 §6.7 bullet 1 | exact |
| C16 | 唯一介質升級條件是多 worker 寫入衝突 | 05 §6.7 bullet 2 | exact |
| C17 | 觸發時重問是否 SQLite | 05 §6.7 bullet 2、§6.11 T3 | exact |
| C18 | 觸發前換介質預設否決 | 05 §6.7 bullet 2 | exact |
| M01 | v1.0＝Phase 3–7＋Phase 9 N=1 | 本檔 §2；02 frozen definition | preserved |
| M02 | v1.0 包含六項與零寫入真實查詢 | 本檔 §2；02 | preserved |
| M03 | v1.1/v1.2/Phase10 等不包含項 | 本檔 §2；02 | preserved |
| M04 | Phase 9 併入 v1.0 的 Q4 理由 | 本檔 §2；05 §6.0 Q4 | preserved |
| M05 | Phase 2 未簽不得稱凍結（歷史） | 本檔 §2；現已由 02 簽核 | preserved |
| M06 | Phase 2 checklist 五項 | 本檔 §3；02 §5 | preserved |
| M07 | Q4/Q5/Q8 預裁決與新裁決優先 | 本檔 §3；05 §6.0 | preserved |
| M08 | 16 面旗 closed object | 本檔 §4；schema INDEX／05 §6.10 | preserved |
| M09 | RC-D 17 鍵與 key=value 是舊投影 | 本檔 §4；schema INDEX | preserved |
| M10 | 9 公共欄與 role 語義 | 本檔 §4；schema INDEX／05 §6.10 | preserved |
| M11 | Phase 3 歷史 branch/PR 交付法 | 本檔 §4（歷史）；night batch 現依 §6.13 | preserved |

## 6. Fail-closed verification

- 05 §6.0 Q1–Q20 remains intact.
- 05 §6.4 risk matrix remains intact.
- 05 §6.8 execution-class and version gates remain intact.
- 05 §6.10 adjustments, §6.11 triggers/open questions, §6.13 night governance,
  §6.14 frozen mock decision, and the indexed §6.12 rulings remain locatable.
- Phase 7 exact authorization gate and Phase 9 Owner-presence/token gate were not edited.

Any missing crosswalk row makes this compaction invalid and requires HOLD rather than
guessing or silently deleting a rule.
