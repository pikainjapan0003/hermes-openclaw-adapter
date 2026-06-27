# Hermes x OpenClaw — Mock E2E Closeout + Boundary Review v0.7.0-E

> 這是一個**收尾與邊界審查**版本，不是新功能版本。
> 本版只做：文件、邊界審查、readiness check。**不新增功能、不接真系統、不改既有流程。**

## 1. v0.7.0-E 結論

v0.7.0 的 A–D 已經完成一條**純 mock 的 Hermes ↔ OpenClaw dry-run 主線**：
一個假任務可以從 mock Adapter 進來，經過格式驗證、approval gate、in-memory mock queue、
mock worker、mock callback，最後產生可驗證的 dry-run 結果。

但要講清楚——目前這條線**全部都是 mock**：

- 目前仍**未接真 Hermes**。
- 目前仍**未接真 OpenClaw**。
- 目前仍**未寫真 Queue DB**。
- 目前仍**未啟動真 Worker**。
- 目前仍**未自動寫 Google Sheets**（維持 `GOOGLE_SHEETS_ENABLED=false`；remains false）。

換句話說：彩排已經跑得通，但還沒有對真實世界做任何事。

## 2. A–D 完成內容整理

| 版本 | 做了什麼 | 是否 mock | 是否接真系統 | 風險狀態 |
|------|----------|-----------|--------------|----------|
| v0.7.0-A | 合作藍圖 / Integration Plan / contract readiness（純文件） | N/A（純文件） | 否 | 低：只有文件，無程式副作用 |
| v0.7.0-B | TaskEnvelope + CallbackEvent schema / 純 Python validator / contract tests | 是（純驗證） | 否 | 低：只驗格式，不連任何系統 |
| v0.7.0-C | Mock Adapter + Approval Gate（request → TaskEnvelope → approval 判斷） | 是 | 否 | 低：只產生 queue candidate，不寫 DB |
| v0.7.0-D | Mock E2E Dry-run（in-memory queue + mock worker + mock callback） | 是 | 否 | 低：全程 in-memory，不寫 DB / 不啟動 worker |

## 3. 現在系統能做什麼

目前**可以用 mock 跑完整一圈**：

```text
mock Hermes request
  → mock Adapter
  → TaskEnvelope validation（validate_task_envelope）
  → approval gate
  → InMemoryMockQueue（純記憶體）
  → mock Worker
  → CallbackEvent validation（validate_callback_event）
  → dry-run result
```

這代表契約（schema）、流程（adapter → queue → worker → callback）、
與 approval 判斷邏輯都已經能被驗證，且彼此串得起來。

## 4. 現在系統不能做什麼

明確列出**目前不能做**的事：

- 不能接收真 Hermes webhook。
- 不能呼叫真 OpenClaw。
- 不能寫真 Queue DB。
- 不能啟動真 Worker。
- 不能自動寫 Google Sheets。
- 不能自動操作外部世界（沒有任何真實 side effect）。
- 不能自動批准高風險任務（risk_level 3–4 一律停在 approval gate）。

## 5. Mock / Real 邊界表

| 元件 | 目前邊界 |
|------|----------|
| Hermes | **mock only**（輸入只是手寫 mock dict，無真 Hermes 整合） |
| Adapter | **mock adapter exists**（`app/mock_adapter_v0_7.py`，只產生 queue candidate） |
| Queue | **in-memory mock queue only for v0.7.0-D**（`InMemoryMockQueue`，非真 Queue DB） |
| Worker | **mock worker only**（`mock_worker_process_task`，不做真事、不啟動真 Worker） |
| Callback | **mock callback event only**（符合 schema，由 mock worker 產生） |
| OpenClaw | **no true call**（完全不呼叫真 OpenClaw / 不建 webhook） |
| Google Sheets | **no auto write**（`GOOGLE_SHEETS_ENABLED=false`，writer/runner 仍獨立） |
| Dashboard | **no new integration**（本版未對 dashboard 做任何整合） |
| Result Sink | **observation only, not source of truth**（觀測層，不可破壞 Queue 狀態） |

## 6. Approval Gate 邊界

approval gate 的判斷規則（v0.7.0-C 定義、v0.7.0-D dry-run 驗證）：

```text
risk_level 0–2 且 approval_required=false → queued
risk_level 3–4                            → pending_approval
approval_required=true                    → pending_approval
pending_approval 不會進 worker
```

重點：**高風險（3–4）或被要求批准的任務，一律停在 approval gate，不會進 mock worker**，
更不會產生 completed callback。這是「進 Queue / 進執行前」的安全閘門。

## 7. 下一階段（進 v0.7.1）前的安全條件

在進入 v0.7.1 之前，至少要先由 Owner 決定以下事項：

- 是否允許寫真 Queue DB。
- 是否先做 local-only intake（只在本機落地，不對外）。
- 是否仍禁止真 OpenClaw execution。
- 是否需要 Owner 手動批准所有外部 side effect。
- 是否需要 dashboard 顯示 mock / real 狀態。
- 是否需要 kill switch（緊急全停開關）。
- 是否需要 audit log（操作稽核紀錄）。
- 是否需要 per-tool allowlist（逐工具白名單）。

## 8. 建議下一步：不要直接接真 OpenClaw

建議下一步**不是**直接接真 OpenClaw，而是先做：

```text
v0.7.1-A：Controlled Queue Intake Plan
```

意思是：

- 先**規劃** mock Adapter 何時、在什麼安全條件下能寫入真 Queue DB。
- 仍然**不呼叫真 OpenClaw**。
- 仍然**不啟動自動外部操作**。
- 所有高風險任務仍需 **Owner approval**。

也就是說：先把「進 Queue」這一步在受控、可回退、可稽核的前提下談清楚，再談「真執行」。

## 9. 安全聲明

本版（v0.7.0-E）以及目前整體 v0.7.0 狀態：

```text
No true Hermes integration
No true OpenClaw execution
No true Queue DB write from mock E2E
No true Worker start
No automatic Google Sheets write
No secrets read or displayed
GOOGLE_SHEETS_ENABLED remains false
No v0.7 tag created
```

本版到此收住。**不進 v0.7.1**，等待 Owner 確認主線節奏。
