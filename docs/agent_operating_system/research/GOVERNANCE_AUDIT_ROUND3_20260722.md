# Governance Audit Round 3 — Designs 11–14 and Research (2026-07-22)

Status: **REVIEW ONLY — FINDINGS NOT FIXED**

## Resolution metadata

| Finding | 狀態 | 對應 |
|---|---|---|
| R3-01 duplicate-key 文件 | 已修 | `eaf20ad` |
| R3-02 v1.2 rollback 前置 | 已修（HOLD 明文化） | `eaf20ad` |
| R3-03 歷史報告狀態 | 已修 | NIGHT-BATCH-11 package 2 resolution metadata |
| R3-04 writer 措辭 | 已修 | NIGHT-BATCH-11 package 2；仍未授權 writer |

修正只處理文件漂移，不解除任何 Owner gate。

This fresh-context pass reviewed:

- `11_V1_1_FIRST_REAL_WRITE_DESIGN.md` through
  `14_V1_2_FIRST_CODE_TASK_DESIGN.md`;
- every file under `docs/agent_operating_system/research/`;
- the implemented `app/hash_chain.py`, `app/rollback_preview_builder.py`,
  `app/blackboard_board_reader.py`, `app/remote_readonly_projection.py`, and
  `scripts/check_mirror_drift_readonly.py`;
- the closed audit, rollback, task, annotation, and remote-projection schemas.

The review looked for cross-document contradictions, implementation drift, outdated
claims, authorization-like wording, and fields asserted without a real contract. It
made no correction, schema change, runtime connection, writer, or execution path.

## 1. Summary

| ID | Severity | Finding | Evidence |
|---|---|---|---|
| R3-01 | P2 | The board-layout decoder specification still says plain `json.loads` and does not require duplicate-key rejection, while the reader now enforces `object_pairs_hook`. A future reimplementation following the design literally can recreate the ambiguity that the product just fixed. | `12_BLACKBOARD_DATA_LAYOUT.md:91-101`; `app/blackboard_board_reader.py:33-41,146-155`; `app/hash_chain.py:46-52` |
| R3-02 | P2 | The v1.2 design requires a descriptive rollback preview that names the exact code commit, but the only implemented rollback preview cannot carry a commit, parent, or target hash. The new v1.1 options explicitly leave that contract undecided, yet v1.2 does not cross-reference the HOLD. | `14_V1_2_FIRST_CODE_TASK_DESIGN.md:133-148`; `11_V1_1_FIRST_REAL_WRITE_DESIGN.md:176-207`; `app/rollback_preview_builder.py:152-174`; `rollback_event.schema.json:160-216` |
| R3-03 | P3 | The dated 2026-07-21 design-review report contains present-tense open findings that are now partly superseded: duplicate-key rejection is implemented and the Hermes-to-projection mapping is documented. Without a resolution banner, a weak reader can reopen completed work or believe the current implementation still uses ordinary decoding. | `research/DESIGN_REVIEW_11_TO_14_20260721.md:71-86,102-114,141-149`; `app/blackboard_board_reader.py:33-41,146-155`; `13_HERMES_WIRING_DESIGN.md:172-199` |
| R3-04 | P3 | One option table describes “reusing the Phase 7 writer” even though no audit writer exists or is authorized. The file-level PLANNING banner and later implementation warning reduce risk, but the option-cell wording can still be quoted out of context as evidence of an existing component. | `11_V1_1_FIRST_REAL_WRITE_DESIGN.md:142-170`; `07_AUDIT_WRITE_DESIGN.md:201-206`; `05_VERIFIED_LONG_TERM_PLAN.md:200-214` |

No P0 or P1 finding was found. The four design files retain explicit
`PLANNING ONLY, NOT AUTHORIZED` boundaries, and none of the reviewed implementations
contains an audit writer, rollback executor, remote transport, dispatch path, or token
unlock.

## 2. Detailed findings

### R3-01 — P2 — duplicate-key rejection is implementation-only drift

The layout's read sequence says only “decodes UTF-8 JSON with `json.loads`”
(`12_BLACKBOARD_DATA_LAYOUT.md:91-101`). That phrase was accurate before the safety
fix, but is now incomplete: the reader passes an `object_pairs_hook` that raises on a
repeated key (`app/blackboard_board_reader.py:33-41,146-155`). The hash helper also
states that this reader now performs that boundary check (`app/hash_chain.py:46-52`).

Impact: a weak implementation agent rebuilding the reader from document 12 can use
ordinary last-key-wins decoding and still claim design compliance. Because canonical
hashing cannot recover duplicate-key evidence after decoding, downstream schema and
hash checks cannot repair this mistake.

Disposition for Owner: update document 12 in a separate docs package to require
duplicate-key rejection before schema selection and to state that error output must
not echo either key or value. Do not weaken the implemented hook.

### R3-02 — P2 — v1.2 rollback wording outruns the undecided contract

Document 14 requires the rollback preview to name the accepted code commit and then
uses that preview in an exact-commit Git-revert design
(`14_V1_2_FIRST_CODE_TASK_DESIGN.md:133-148`). The implemented builder is intentionally
for the harmless N=1 no-side-effect case: it emits `rollback_required: false`,
`rollback_path: null`, and has no commit binding
(`app/rollback_preview_builder.py:152-174`). The closed schema has no write commit,
parent, target hash, or revert outcome fields.

Document 11 now compares three future contract options and leaves the Owner decision
blank (`11_V1_1_FIRST_REAL_WRITE_DESIGN.md:176-207`). Document 14 does not cite that
unresolved gate, so its imperative sequence can be mistaken for an implementable
specification.

Disposition for Owner: after deciding document 11 §5.2, make document 14 reference the
selected versioned contract. Until then, v1.2 rollback remains HOLD and the current
preview builder must not be repurposed or fed a commit through free text.

### R3-03 — P3 — historical research lacks resolution metadata

The 2026-07-21 report correctly captured its then-current state, but F-03 still says
the live reader uses `json.loads` without `object_pairs_hook`
(`research/DESIGN_REVIEW_11_TO_14_20260721.md:71-86`). That is no longer true. F-05
says the Hermes design has no aggregate mapping (`:102-114`); document 13 now provides
the mapping and explicitly proves that task plus annotation alone are insufficient
(`13_HERMES_WIRING_DESIGN.md:172-199`).

The underlying governance questions are not all closed: `produced_by` remains
policy-only pending Owner choice, and remote wiring remains unauthorized. The problem
is only that the historical report does not distinguish “fixed implementation fact”
from “still-open Owner decision.”

Disposition for Owner: preserve the dated report, but later add a non-destructive
resolution table that points F-03 to the duplicate-key fix and F-05 to document 13
§7.1. Do not rewrite the original finding text or treat the mapping as runtime
authorization.

### R3-04 — P3 — “reuse writer” wording can be detached from its planning boundary

Document 11 option A lists “reuse the Phase 7 writer” as a benefit
(`11_V1_1_FIRST_REAL_WRITE_DESIGN.md:163`). There is a Phase 7 writer *design*, but no
writer implementation or write authorization. The same section correctly says the
options are unauthorized and later requires separate schema and writer packages, so
this is not an active write path.

Impact: a weak reader quoting only the table cell may infer that a writer already
exists and that option A merely wires into it.

Disposition for Owner: in a future docs-only cleanup, change the noun to “future
Phase 7 writer design” and retain the existing Owner gate. No implementation follows
from this wording fix.

## 3. Cross-implementation checks that passed

| Check | Result |
|---|---|
| 11 canonical JSON vs `hash_chain` | Aligned on object root, NFC, sorted keys, compact UTF-8, no physical trailing LF, and complete-entry hashing. |
| 11 current rollback limitation vs builder/schema | Newly documented options correctly state that the present preview cannot bind a real Git target. |
| 12 board inventory vs validator | Ten Blackboard message types remain exact; no evidence bundle is put on the board. |
| 13 task/annotation fields vs schemas | Named fields exist; provenance remains explicitly non-authoritative. |
| 13 projection table vs builder | Correctly identifies exact aggregate fields, non-null parent-id limitation, missing readiness/decision sources, and mandatory evidence hash. |
| Mirror governance vs tool | `SAME`, missing-mirror `BEHIND`, mirror-only `AHEAD`, and indeterminate-content `DIFFERS` match the L-007 fail-closed intent. |
| Authorization language | No reviewed design converts a preview, valid schema, hash, Owner-decision data verb, or test result into standing execution/write authority. |

## 4. Fresh-context handoff

Before implementing anything based on designs 11–14:

1. resolve R3-01 in documentation without altering the duplicate-key guard;
2. obtain an explicit Owner decision for the v1.1 audit and rollback contract options;
3. keep v1.2 rollback HOLD until its exact record schema exists;
4. treat dated research as evidence of historical review, not current-state authority;
5. re-run the authorization-language and cross-field existence checks against the
   exact implementation diff.

This report is not an instruction to implement any finding.
