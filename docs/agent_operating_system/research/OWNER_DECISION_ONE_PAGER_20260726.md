# Owner Decision One-Pager — 2026-07-26

Status: **PLANNING ONLY, NOT AUTHORIZED — ALL DECISIONS BLANK**

This page compresses existing proposals; it does not select an option, change a
schema, unlock implementation, or replace the source designs.

| Decision | Problem | Existing options / recommended option | If selected | Default when not selected | Owner decision |
|---|---|---|---|---|---|
| **RED** — schema-error redaction | Validator errors can contain raw instance values, schema fragments, paths, or display identifiers at E-01/E-02 exposure boundaries. | A: redact only at each caller; B: change validator output globally; **C (recommended): keep rich internal errors and require one fail-closed export redactor plus static/tests guards**. | A later separately authorized package may implement the chosen boundary and the complete leak-marker checklist; selection alone creates no route or exposure. | Current validator remains unchanged; known raw-error cases remain `xfail`; no validator error may be exported or remotely displayed. | **________** |
| **AUD** — v1.1 structured audit evidence | Closed `audit_event` cannot mechanically express write digest, preconditions, commit, and test result. | A: version/extend `audit_event`; **B (recommended): add closed `v1_1_write_record`**; C: encode key/value data inside `event_notes`. | The chosen contract must first receive an independent schema/fixture/validator design package; no writer or write authority follows from the choice. | HOLD; `event_notes` must not be claimed as structured v1.1 write evidence. | **________** |
| **RB** — rollback Git binding | Preview-only `rollback_event` cannot bind an immutable write commit/parent/target hash or record revert outcome. | A: version/extend `rollback_event`; **B (recommended): add closed `v1_1_rollback_record`**; C: embed rollback state in the candidate write record. | The chosen record and cross-record invariants must be designed before any rehearsal; the record remains evidence, never a Git command. | HOLD; no commit may be guessed from HEAD, recency, text, or model output. | **________** |
| **PB** — Hermes `produced_by` | The canonical Hermes identities are policy strings, while current Blackboard schemas accept any non-empty producer. | **A (recommended): exact enum only in Hermes-produced `task_draft`/`annotation` schemas**; B: namespace pattern plus registry; C: keep schema unchanged and enforce only in trusted adapter. | A later schema package must inventory every producer and state that provenance is not authentication, approval, or execution permission. | Schemas stay unchanged; any future adapter must separately fail closed against the exact three-value allowlist. | **________** |
| **ROOT** — root `parent_task_id` projection | Blackboard permits `parent_task_id: null` for a root, but projection v1 requires a patterned `parent_task_display_id` string. | **R (recommended): version the projection contract so a verified root maps explicitly to JSON `null`; never hash a placeholder or invent a parent.** | A later contract-only package may define the version, builder invariant, fixtures, and tests; this choice does not authorize aggregation or remote transport. | HOLD the projection for root tasks; do not call the current builder with a placeholder. | **________** |

Sources: `SCHEMA_ERROR_REDACTION_CONTRACT_DESIGN.md` §§5–8;
`11_V1_1_FIRST_REAL_WRITE_DESIGN.md` §§5.1–5.2; and
`13_HERMES_WIRING_DESIGN.md` §§4.1, 7.

Owner one-line reply example:

`RED=C; AUD=B; RB=B; PB=A; ROOT=R`

Any omitted or blank item keeps its stated fail-closed default. A selection is a
design decision only; Phase 7, Phase 9, v1.1 writes, schema implementation,
runtime, remote wiring, execution, and dispatch still require their own gates.
