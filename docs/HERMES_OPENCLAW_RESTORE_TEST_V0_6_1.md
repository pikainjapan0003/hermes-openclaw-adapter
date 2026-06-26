# Hermes x OpenClaw Restore / Clone Test v0.6.1

## 1. 測試目標

確認 v0.6.0B 的 GitHub 遠端備份可以重新 `clone` 並重建基本環境、跑通離線測試，
證明遠端備份「真的能還原」。本版**只做還原測試**，不新增功能、不改核心程式。

## 2. 測試環境

- 日期：2026-06-26
- 系統：WSL Ubuntu（user `lnovo`）
- Python：`Python 3.12.3`
- 原專案位置：`~/projects/hermes-openclaw-adapter`（master tip `adf56b8`）
- 測試 clone 位置（與原專案分開）：`~/projects/hermes-openclaw-adapter-restore-test`
- 來源 remote：`git@github.com:pikainjapan0003/hermes-openclaw-adapter.git`（SSH）

## 3. GitHub Clone 結果

- `git clone`（SSH）：✅ 成功
- clone 後 master tip：`adf56b8 docs: add v0.6.0B codex handoff report`（= 預期值，與原專案一致）
- `git status -sb`：`## master...origin/master`（乾淨、無多餘變更）
- v0.5.x tags：✅ 全部 **10 個**都在（`v0.5.0-local-queue-worker` … `v0.5.9-backup-push-plan`）
- 外來 `HEAD` 檔：**不在 clone 內**（證明它從未被 commit，只是原工作目錄的本機雜檔）

## 4. 敏感檔案檢查

clone 內 `git ls-files` 篩 `.env` / `data/` / `queue.db` / `tasks.jsonl` / `results.jsonl`：
**零命中（全部未被 tracked）**。

- `.env`：clone 內**不存在**（被 `.gitignore` 排除，本來就不該進備份）→ 符合預期
- `.env.example`：存在（純 placeholder 範本，無真實 secret）
- `data/` / `queue.db` / `*.jsonl`：未被追蹤，clone 內無此類執行期資料

## 5. Python 環境重建

- `python3 -m venv .venv`：✅ 成功
- `pip install --upgrade pip`：✅ 成功
- `pip install -r requirements.txt`：✅ 成功（版本與 pin 一致）
  - fastapi 0.115.6、uvicorn 0.32.1、httpx 0.28.1、pydantic 2.10.4、
    python-dotenv 1.0.1、jinja2 3.1.4、python-multipart 0.0.32

## 6. 測試結果

全部在 **clone 副本**上、用重建的 `.venv` 執行（離線、不需真實 token / OpenClaw）：

| 測試 | 結果 |
|---|---|
| scripts/test_queue_store.py | ✅ PASS |
| scripts/test_queue_observability.py | ✅ PASS |
| scripts/test_dashboard_readonly.py | ✅ PASS |
| scripts/test_blackboard_comments.py | ✅ PASS |
| scripts/test_approval_flow.py | ✅ PASS |
| scripts/test_limited_control_actions.py | ✅ PASS |
| scripts/test_system_health.py | ✅ PASS |
| scripts/test_dashboard_polish.py | ✅ PASS |
| scripts/test_docs_operator_guide.py | ✅ PASS |
| scripts/test_backup_push_plan.py | ✅ PASS |
| `from app.main import app` | ✅ import OK |
| scripts/smoke_test_queue.sh（用內建假 OpenClaw） | ✅ PASS（task completed，result_text 含 PONG） |

> smoke test 的 health 回報 `version: 0.5.6`（APP_VERSION 自 v0.5.6 後未再 bump，
> 因 v0.5.7–v0.5.9 為 UI/文件性質）— 屬已知、非還原問題。

## 7. 尚未測項目（因缺環境 / 屬刻意不測）

以下需要真實外部環境，本版**刻意未跑**（還原測試不碰真實服務）：

- **真實 OpenClaw 端到端**：需在 WSL 有可執行的 `openclaw` CLI + OpenClaw Gateway 在線
  （smoke 只用內建假 CLI 驗證流程，未呼叫真實 OpenClaw）。
- **真實 `.env`**：clone 內無 `.env`（正確）。要實際對外運作需自備 `.env`，至少設定
  `HERMES_ADAPTER_TOKEN`、`OPENCLAW_CLI_BIN`（指向真實 openclaw）等；本版未建立任何真 token。
- **Hermes / MCP / Discord 串接**：需 Hermes Agent + Gateway + 已註冊的 MCP server，未測。
- **callback HTTP 模式**：預設 `ledger_only`，未測 `http`（需 `HERMES_CALLBACK_URL` / `SECRET`）。

## 8. 結論

✅ **Restore / Clone Test 通過**：v0.6.0B 的 GitHub 遠端備份可成功 clone、重建 `.venv`、
安裝相依套件，並通過全部 10 個離線測試 + FastAPI import + smoke（PONG）。備份內容乾淨
（無 `.env` / `data/` / `queue.db` / `*.jsonl` / 外來 `HEAD`），證明遠端備份可用且可還原。

**下一步建議**：
- v0.6.1 可封版（`v0.6.1-restore-clone-test`）。
- 之後：v0.6.2 Google Drive / Sheets 結果落地評估、v0.6.3 Replit / VPS 部署評估。
- 暫不做：Redis、多 Worker、DLQ、公開 Dashboard、自動下單 / 付款 / 發訊息。
