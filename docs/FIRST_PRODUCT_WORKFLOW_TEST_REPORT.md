# 第一個正式工作流測試報告：商品資料整理（Level 0）

> 測試日期：2026-06-14
> 結論：**成功 ✅**。Hermes 依 OpenClaw Executor skill 判斷為 Level 0，自動呼叫 MCP 工具
> `dispatch_to_openclaw`，由 OpenClaw 產出 Markdown 表格，全程無 curl、無直接 Adapter、無直接 CLI、無副作用。

---

## 1. 測試目標

驗證新建立的 Hermes skill「**openclaw-executor**」能讓 Hermes：
- 把「商品資料整理」這類**純文字整理（Level 0）**任務，
- **自動**透過 MCP 工具 `dispatch_to_openclaw` 交給 OpenClaw 執行，
- 並把結果整理回報，且**不做任何高風險或外部操作**。

## 2. 測試任務

- **任務名稱**：商品資料整理工作流測試
- **安全等級**：Level 0（純文字整理）
- **要求欄位**：商品名稱 / 品牌 / 商品特色 / 適合對象 / 注意事項 / 代購提醒
- **安全邊界**：不要查網路、不要操作檔案、不要登入網站、不要下單、不要發送訊息
- **商品資料**：
  1. ISHIYA 白色戀人，北海道經典伴手禮，適合送禮，包裝精緻，賞味期限約 120 天。
  2. ISHIYA 美冬 巧克力千層條，與白色戀人同家出產，有千層派口感，常態款有多種口味，賞味期限約 150 天。
  3. 六花亭 酒糖，北海道甜點伴手禮，含酒精，不適合兒童與孕婦，購買前需提醒客人。

## 3. Hermes skill 是否生效 → ✅ 是

- `hermes skills list` 顯示：`openclaw-executor | automation | local | local | enabled`。
- skill 影響了 Hermes 的行為：Hermes 組出的 Task Envelope `metadata` 完全符合 skill 的標準格式：
  ```json
  {
    "source": "hermes",
    "workflow": "product-data-markdown-table",
    "safety_level": "level_0",
    "requires_confirmation": false,
    "expected_output": "Markdown 表格，欄位：商品名稱 / 品牌 / 商品特色 / 適合對象 / 注意事項 / 代購提醒；另附簡短備註"
  }
  ```
  → Hermes 自己把這件事**標記成 `safety_level: level_0` 且 `requires_confirmation: false`**，正是 skill 教它的判斷。

## 4. Hermes 是否呼叫 MCP tool → ✅ 是

- Hermes 自述：「已交給 OpenClaw 執行並取得結果」。
- MCP server log（`~/.hermes/logs/mcp-stderr.log`）有 **`CallToolRequest`**。
- 全程**沒有** curl、**沒有**直接呼叫 Adapter、**沒有**直接呼叫 openclaw CLI。

## 5. Adapter / OpenClaw 是否成功 → ✅ 是

- Adapter HTTP log：`POST /tasks/dispatch HTTP/1.1 200 OK`。
- `adapter_status: sent`。
- `data/tasks.jsonl` 行數 8 → 9（新增一筆）。

## 6. 最終表格（OpenClaw 回傳）

| 商品名稱 | 品牌 | 商品特色 | 適合對象 | 注意事項 | 代購提醒 |
| --- | --- | --- | --- | --- | --- |
| 白色戀人 | ISHIYA | 北海道經典伴手禮，包裝精緻 | 適合送禮 | 賞味期限約 120 天 | — |
| 美冬 巧克力千層條 | ISHIYA | 與白色戀人同家出產，有千層派口感，常態款有多種口味 | — | 賞味期限約 150 天 | — |
| 酒糖 | 六花亭 | 北海道甜點伴手禮，含酒精 | — | 含酒精，不適合兒童與孕婦 | 購買前需提醒客人 |

備註（OpenClaw + Hermes）：
- 「—」表示原始資料未提供該欄位，未自行推測補充。
- 酒糖含酒精，代購前需特別提醒客人不適合兒童與孕婦。
- 整理過程未查網路、未操作檔案、未登入、未下單、未發送訊息（符合 Level 0）。

## 7. task_id

```
task-0199478f7be1
```
（先前里程碑：PONG = task-f1ac05baf045；三點摘要 = task-2000b69a1a97）

## 8. data/tasks.jsonl 驗證

- 最新一筆 `task_id = task-0199478f7be1`、`adapter_status = sent`、`title = 北海道伴手禮商品資料整理`。
- `metadata` 帶 `safety_level=level_0`、`requires_confirmation=false`、`expected_output=...`。
- 與 Hermes 回報的 task_id 一致 → 真實鏈路。

## 9. 是否符合 Level 0 安全規則 → ✅ 完全符合

| 檢查 | 結果 |
|---|---|
| 沒有 curl / 沒有直接 Adapter / 沒有直接 CLI | ✅ 全程經 Hermes → MCP |
| 沒有改檔案 | ✅ |
| 沒有登入 / 付款 / 下單 / 發送訊息 | ✅ |
| 沒有查網路 / 外部操作 | ✅ |
| Hermes 標記 safety_level=level_0、requires_confirmation=false | ✅ |

## 10. 結論

`Hermes（OpenClaw Executor skill）→ MCP（dispatch_to_openclaw）→ Adapter → OpenClaw CLI → 真實 OpenClaw → 回傳 Hermes`
完整跑通，並產出正確的 Markdown 表格。

→ **商品資料整理工作流可作為「第一個正式工作流」**。
它是 Level 0、零副作用、好驗證，適合作為之後「代購訂單整理」「Beyblade 採購分析」的基礎技能線起點。
