# Google Drive / Sheets 連結記錄（收尾）

> 給新手小白看的白話版。這份只記錄「目前 Google Drive / Sheets 已經連到哪、之後可以怎麼用」，**不是**已經串進 Adapter 的功能。

---

## 1. 目前狀態

- ✅ **已建立 Google service account（服務帳號）** —— 用來讓程式（未來的 OpenClaw / Adapter）存取 Google Drive / Sheets。
  - service account 帳號：`cc-663@my-openclaw-491003.iam.gserviceaccount.com`
  - Google Cloud 專案：`my-openclaw-491003`
- ✅ **已下載 service account 的 JSON 金鑰**（檔名類似 `my-openclaw-491003-xxxxxxxx.json`），目前放在本機（C 槽下載）。
- ✅ **已準備一個共用的 Google Drive 資料夾**（之後放結果 / 表格用）：
  - 連結：`https://drive.google.com/drive/u/1/folders/1XLz66pJY_I7bmOH2cADeCMegY5aBoc0h`
- ⏳ **尚未串進 Adapter** —— 目前任務結果仍是寫進 `data/results.jsonl`，還沒有自動寫進 Google Sheet。這是之後的工，不在本次範圍。

---

## 2. ⚠️ 安全注意事項（最重要）

- 🔑 **那個 JSON 金鑰等於一把鑰匙** —— 任何人拿到就能存取這個專案連到的 Drive / Sheets。
- 🚫 **絕對不要把 JSON 金鑰 commit 進 git**（不管 private 還是 public repo）。
- 🚫 **不要把 JSON 內容貼到聊天、截圖、或任何公開地方**。
- ✅ service account email 與資料夾連結本身**不是機密**（是識別碼），記在文件裡 OK。
- 🧷 建議把金鑰放在 repo 外（或加進 `.gitignore`，例如 `*.json` 金鑰、`credentials/`、`secrets/`）。
- ♻️ 如果金鑰不小心外流，到 Google Cloud Console 把這把 key **撤銷並重發（rotate）**。

> 要分享資料夾給 service account 使用時：在該 Drive 資料夾按「共用」，把上面那個 `cc-663@...gserviceaccount.com` 加為**編輯者**即可。

---

## 3. 之後可以怎麼用（方向，先不做）

- 讓 OpenClaw / Adapter 完成任務後，除了寫 `data/results.jsonl`，**另外把結果寫進指定的 Google Sheet**（用 service account 認證）。
- 把商品資料整理、訂單整理等工作流的輸出，直接落地成 Google 試算表，方便人工檢視。
- 這會需要：改程式 + 安裝 Google API 套件 + 用 JSON 金鑰認證 —— 屬於未來版本的工作，**本次不實作**。

---

## 4. 結論

- ✅ Google Drive / Sheets 的**憑證與資料夾已準備好**（service account + 金鑰 + 共用資料夾）。
- ⏳ **尚未**接進 Adapter，目前不影響現有 v0.4 流程。
- 🔒 金鑰務必保管好、**不要進 git**。
- ➡️ 真正的 Sheets 串接列為**後續工作**（可在 v0.5 之後或獨立小版本處理）。

> 本文件僅為 Google Drive / Sheets 連結現況的收尾記錄。
