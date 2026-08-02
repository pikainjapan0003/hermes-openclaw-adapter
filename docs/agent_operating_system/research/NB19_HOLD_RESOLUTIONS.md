# NIGHT-BATCH-19 HOLD Resolutions

Date: 2026-08-02

Authority recorded: Fable 5 independent batch review

Scope: resolution record only; this file is not Phase 7, Phase 9, runtime,
schema, persistence, or execution authorization.

## Package 6 — C

> C——風險可接受，但需正式化契約（我的規格錯）

> 根目錄是呼叫端指定的信任錨點，不是攻擊面：呼叫端說「讀這個板」，reader
> 就讀該路徑解析後的內容——沒有「逃出被指定的板」。真正的攻擊面是板內的
> symlink（攻擊者只要能寫入板目錄就能改指向），而 reader 已正確拒絕。
> 正確不變式應一次寫死：解析 root 一次，之後每個 entry 的 realpath 必須留在
> 解析後的 root 之下。

Recorded disposition: the root symlink is accepted as caller-selected
indirection. An entry symlink remains rejected. The realpath invariant is
formalized at the point of use in `40_MAINTENANCE_PROTOCOL.md` F7.

## Package 9 — A

> A——契約就是「只驗 HTTP 可達性」，HOLD 的前提不成立（我的規格錯）

> `read_replit_status` 從未讀取 response body。因此「截斷 JSON／超大回應」
> 對它在語義上不存在——它不解析內容，也不因大 body 佔記憶體。
> `deployed_hash=null`、`deployed_hash_status="UNKNOWN"`、
> `deployed_hash_verified=false`。

Recorded disposition: HTTP 200 with a malformed or truncated body may still be
`REACHABLE`, because the body is outside this probe's contract. Reachability is
not content validation, a deployed revision, or synchronization evidence.

## Package 11 — A

> A——HOLD 成立，且是真實缺陷。

> 缺陷不在假設性的 `$ref`，而在現行就在用的 `oneOf`：31 個真實欄位被渲染成
> `unspecified`。下一包應修產品 renderer（純函式、唯讀腳本、風險低），而非
> 縮小主張——因為這些是 v1.0 契約的可空欄位，文件必須誠實呈現
> 「string 或 null」。

Recorded disposition: fix the stdout-only renderer and add exhaustive type
fidelity tests. Do not change schema files or persist generated documentation.

## Closure boundary

These resolutions close the three NIGHT-BATCH-19 HOLD questions only. They do
not fill any Owner choice field and do not unlock the Phase 7 writer, Phase 9,
AUD, RB, PB, RED, ROOT, or research-governance gates.
