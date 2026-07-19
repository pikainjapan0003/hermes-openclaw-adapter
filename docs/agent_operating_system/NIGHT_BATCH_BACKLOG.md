# 夜跑批次 Backlog（常備存貨，批單從這裡取材）

> 治理：05 §6.13。凡標【夜跑可做】＝零寫入、零執行、docs/測試/純函式，可直接排批。
> 凡標【Owner 閘】＝依 05 正本需 Owner 逐字授權或在場，**永不排進夜跑**；夜跑只能做其「設計/審查/準備」半邊。
> 本檔由 Fable 5 維護；批單消耗一項就劃掉並註 NB 編號。執行者不得自行從本檔取材加包。

## A. v1.0 收尾（主線）

| 項 | 性質 | 狀態 |
|---|---|---|
| Phase 7 audit writer 實作＋強模型審＋Owner 檢視 audit 檔簽核 | 【Owner 閘】逐字授權句：`允許寫入 data/audit_dev.jsonl（local dev append-only）` | 設計已備（07），等授權句 |
| 07 設計 fresh-context 對抗審查 | 【夜跑可做】 | NB-6 包1 |
| Phase 9 preflight 閘門機械化測試 | 【夜跑可做】 | NB-6 包2 |
| Phase 9 N=1 真實調用 | 【Owner 閘】在場＋單次 token | 等 Phase 7 完成後擇日 |

## B. v1.1／v1.2 準備（畢業考後的路，先把圖畫好）

| 項 | 性質 |
|---|---|
| v1.1 設計稿：repo 內測試檔一次真實寫入的全鏈路（packet/token/audit/rollback 怎麼串，git revert 演練腳本） | 【夜跑可做】docs only，PLANNING ONLY 標記 |
| v1.2 設計稿：首次真實代碼任務的驗收框架（多審查員、測試綠才收工） | 【夜跑可做】docs only |
| O1 提案稿：「計劃級授權」格式（Owner 批計劃後 AUTO 級自動並行的授權長相）——產 2–3 案給 Owner 選 | 【夜跑可做】提案；裁決屬 Owner |
| O2 提案稿：角色化 worker（工程師/測試員/安審…）角色定義、prompt 存放與維護權 | 【夜跑可做】提案；裁決屬 Owner |
| 角色 worker 的 role prompt 初稿（工程師/測試員/安全審查員各一） | 【夜跑可做】docs only，掛 O2 裁決後生效 |

## C. 接線與擴張（遠期）

| 項 | 性質 |
|---|---|
| Blackboard `data/` 目錄佈局設計＋唯讀 reader（讀 fixtures 演練，不建 data/） | 【夜跑可做】reader 純讀；建 data/ 正式區屬 Owner 閘 |
| Hermes runtime 接線設計稿（advisory→Blackboard 留言的格式與頻率，不實作） | 【夜跑可做】docs only |
| Phase 10 connector scope packet 設計研究＋OWASP Agentic Top 10 全文閱讀對照（99 檔第 8 項掛帳） | 【夜跑可做】docs only；接入屬 Owner 閘（§6.11 T1） |
| Replit 單向同步實作 | 【Owner 閘】遠端接線未授權 |

## D. 品質與長期健檢（Phase 11，永不枯竭）

| 項 | 性質 |
|---|---|
| legacy 顯示層覆蓋擴充（full_loop_preview_adapter、result_feedback_preview 等） | 【夜跑可做】NB-6 包3 起，分多批 |
| 信任事故自動掃描：repo 內「越權模式」靜態掃描器（新 POST/writer/token 變更即紅）做成常備測試 | 【夜跑可做】 |
| Phase 0 三源檢查腳本化（local/GitHub hash 對照，read-only） | 【夜跑可做】 |
| 制度檔季度健檢（40 F4 精簡門檻、規則衝突掃描、90 教訓回歸） | 【夜跑可做】週期性重複排批 |
| mock_e2e 舊件與新 contract 的一致性遷移評估 | 【夜跑可做】評估報告先行 |

## 已消耗

- NB-1～NB-5：Phase 3/4/5/6/8 規劃、hash-chain、rollback builder、coverage/mypy/fuzz/全鏈 rehearsal（詳 05 §5 與各批 commit）。
