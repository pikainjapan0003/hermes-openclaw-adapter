# Owner Decision One-Pager — 2026-07-26

Status: **PLANNING ONLY, NOT AUTHORIZED — ALL DECISIONS BLANK**

Resolution metadata: **corrected in
`night-batch-16-pkg1-owner-one-pager`** (this package's immutable Git commit;
see repository history). This correction resolves Round 7 findings R7-01 and
R7-02 without making any Owner decision.

This page compresses existing proposals; it does not select an option, change a
schema, unlock implementation, or replace the source designs.

| Decision | Problem | Existing options / recommended option | If selected | Default when not selected | Owner decision |
|---|---|---|---|---|---|
| **RED** — schema-error redaction | Validator errors can contain raw instance values, schema fragments, paths, or display identifiers at E-01/E-02 exposure boundaries. | A: redact inside each validator; B: keep validator output and redact only at exposure points; **C (recommended): double-layer contract**. Source: `SCHEMA_ERROR_REDACTION_CONTRACT_DESIGN.md:142,151,162-183`. | A later separately authorized package may implement the chosen boundary and the complete leak-marker checklist; selection alone creates no route or exposure. | Current validator remains unchanged; known raw-error cases remain `xfail`; no validator error may be exported or remotely displayed. | **________** |
| **AUD** — v1.1 structured audit evidence | Closed `audit_event` cannot mechanically express write digest, preconditions, commit, and test result. | A: 擴充 `audit_event`; **B (recommended): 新增 `v1_1_write_record`**; C: 塞入 `event_notes` 結構化字串. Source: `11_V1_1_FIRST_REAL_WRITE_DESIGN.md:161-174`. | The chosen contract must first receive an independent schema/fixture/validator design package; no writer or write authority follows from the choice. | HOLD; `event_notes` must not be claimed as structured v1.1 write evidence. | **________** |
| **RB** — rollback Git binding | Preview-only `rollback_event` cannot bind an immutable write commit/parent/target hash or record revert outcome. | A: 升版 `rollback_event`; **B (recommended): 新增 `v1_1_rollback_record`**; C: 內嵌在候選 `v1_1_write_record`. Source: `11_V1_1_FIRST_REAL_WRITE_DESIGN.md:194-207`. | The chosen record and cross-record invariants must be designed before any rehearsal; the record remains evidence, never a Git command. | HOLD; no commit may be guessed from HEAD, recency, text, or model output. | **________** |
| **PB** — Hermes `produced_by` | The canonical Hermes identities are policy strings, while current Blackboard schemas accept any non-empty producer. | **A (recommended): 精確 enum**; B: namespace pattern; C: 保留非空字串. Source: `13_HERMES_WIRING_DESIGN.md:78-99`. | A later schema package must inventory every producer and state that provenance is not authentication, approval, or execution permission. | Schemas stay unchanged; any future adapter must separately fail closed against the exact three-value allowlist. | **________** |
| **ROOT** — root `parent_task_id` projection | Blackboard permits `parent_task_id: null` for a root, but projection v1 requires a patterned `parent_task_display_id` string. | **No formal source options exist yet.** Source: `13_HERMES_WIRING_DESIGN.md:181,196-199` only identifies the incompatibility and requires a future display-rule decision. Suggested direction (not an option label): version the projection contract so a verified root can map explicitly to JSON `null`; never hash a placeholder or invent a parent. | A future design package must first define and compare formally labelled options. Only after that may Owner select one; this row authorizes no contract change, aggregation, or remote transport. | HOLD the projection for root tasks; do not call the current builder with a placeholder. | **________** |

Sources: `SCHEMA_ERROR_REDACTION_CONTRACT_DESIGN.md` §§5–8;
`11_V1_1_FIRST_REAL_WRITE_DESIGN.md` §§5.1–5.2; and
`13_HERMES_WIRING_DESIGN.md` §§4.1, 7.

Owner one-line reply example for the four decisions that currently have formal
source options:

`RED=C; AUD=B; RB=B; PB=A`

`ROOT` must remain blank until a source design defines formal labelled options.

Any omitted or blank item keeps its stated fail-closed default. A selection is a
design decision only; Phase 7, Phase 9, v1.1 writes, schema implementation,
runtime, remote wiring, execution, and dispatch still require their own gates.
