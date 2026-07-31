# Fresh-eyes Design Review: 11–14 (2026-07-21)

Status: **REVIEW ONLY — FINDINGS RECORDED, NOTHING FIXED OR AUTHORIZED**

## Resolution metadata

| Finding | 狀態 | 對應 |
|---|---|---|
| F-01 audit contract | 待裁決 | `11_V1_1_FIRST_REAL_WRITE_DESIGN.md` §5.1 三案，Owner 欄留白 |
| F-02 rollback binding | 待裁決 | 同檔 §5.2 三案，Owner 欄留白 |
| F-03 duplicate-key decoder | 已修 | `005e9e0` reader hook；`eaf20ad` 文件同步 |
| F-04 `produced_by` | 待裁決 | `13_HERMES_WIRING_DESIGN.md` §4.1 三案 |
| F-05 projection mapping | 已修（設計） | `115d40b` 逐欄映射；runtime 仍未授權 |

原 finding 文字保留為當時快照，不可覆蓋上表 current status。

## 1. Scope and method

Reviewed:

- `11_V1_1_FIRST_REAL_WRITE_DESIGN.md`;
- `12_BLACKBOARD_DATA_LAYOUT.md`;
- `13_HERMES_WIRING_DESIGN.md`;
- `14_V1_2_FIRST_CODE_TASK_DESIGN.md`;
- the implemented `hash_chain`, rollback-preview builder, Blackboard board reader,
  remote read-only projection, and the closed Blackboard schemas they consume.

The review looked for contradictions, authorization-like wording, implementation drift,
and cross-contract fields that do not exist. It did not modify a design, schema, builder,
reader, route, runtime, or persistence path.

## 2. Verdict

No P0 or P1 finding was found. The four documents consistently retain their
`PLANNING ONLY, NOT AUTHORIZED` boundary and do not create an execution or write grant.

Two P2 contract gaps must remain HOLD items before v1.1/v1.2 implementation. Three P3
boundary ambiguities should be resolved in the relevant future design package so a weak
implementer cannot silently select an incompatible contract.

## 3. Findings

### F-01 — P2 — v1.1 audit outcomes do not fit the current closed audit schema

`11_V1_1_FIRST_REAL_WRITE_DESIGN.md:128-137` requires six event kinds that retain
packet/action/evidence digests, token metadata, base/target preconditions, target hashes,
Git diff/test evidence, write/revert commits, and chain-verification results. The current
closed audit contract exposes only identifiers plus free-text `event_type` and
`event_notes` for those facts (`docs/schemas/blackboard/audit_event.schema.json:159-204`).
There are no structured fields for the required digests, preconditions, commit ids, or
test results, and `additionalProperties: false` prevents adding them ad hoc.

The design already recognizes the uncertainty at
`11_V1_1_FIRST_REAL_WRITE_DESIGN.md:253-260`, especially the possible need for a new
schema. That unresolved item is therefore a real implementation gate, not permission to
pack security-relevant evidence into `event_notes` or weaken the closed schema.

Required disposition before implementation: Owner must select a versioned audit
contract (or an explicitly structured referenced evidence contract) and define every
cross-reference. Until then, the Phase 7 writer and v1.1 event set cannot be assumed
schema-compatible.

### F-02 — P2 — the existing rollback preview cannot name a real Git rollback target

Both future designs require a preview bound to one exact commit:

- `11_V1_1_FIRST_REAL_WRITE_DESIGN.md:177-196` requires the write commit, its parent,
  target path/hashes, and expected revert commit outcome;
- `14_V1_2_FIRST_CODE_TASK_DESIGN.md:133-148` requires a descriptive preview naming the
  accepted code commit and post-revert validation.

The current rollback schema contains `source_audit_id`, status, a descriptive
`rollback_path`, and reason, but no write commit, parent commit, revert target, target
hash, or post-revert assertion (`docs/schemas/blackboard/rollback_event.schema.json:160-216`).
The implemented N=1 builder is narrower still: it always emits `NOT_REQUIRED`,
`rollback_required: false`, and `rollback_path: null`
(`app/rollback_preview_builder.py:152-174`).

Required disposition before implementation: define a separately versioned real-write
rollback preview contract/builder. The current preview must not be repurposed by placing
a commit hash in free text or by loosening its preview-only N=1 semantics.

### F-03 — P3 — board JSON decoding does not preserve the duplicate-key safety boundary

The formal canonicalization rule rejects duplicate JSON keys and explains that ordinary
decoding loses the evidence (`07_AUDIT_WRITE_DESIGN.md:99-115`; `app/hash_chain.py:46-53`).
The board layout says entries are decoded with `json.loads`
(`12_BLACKBOARD_DATA_LAYOUT.md:91-101`), and the implementation uses ordinary
`json.loads` without an `object_pairs_hook`
(`app/blackboard_board_reader.py:130-145`). A file with duplicate keys can therefore be
accepted according to only its last value.

This reader is not the authorized audit writer, so the issue is not a current write-path
violation. It is an ambiguity at the reader-to-hash boundary: a future caller could treat
a schema-valid board audit entry as unambiguous hash input when the original bytes were
not. The future persistence design must either hard-reject duplicates at every file
decode boundary or state mechanically that board-reader output can never be the source
of persisted hash-chain entries.

### F-04 — P3 — Hermes provenance values are policy-only, not schema-enforced

`13_HERMES_WIRING_DESIGN.md:55-76` defines three proposed `produced_by` strings and says
unknown or unprovable provider identity causes HOLD. The task and annotation schemas
only require `produced_by` to be non-empty text
(`docs/schemas/blackboard/task_draft.schema.json:134-138` and
`docs/schemas/blackboard/annotation.schema.json:139-143`). Schema validation alone will
therefore accept an arbitrary provider label.

The document correctly assigns provider identity to trusted envelope construction at
`13_HERMES_WIRING_DESIGN.md:78-96`; no current schema change is implied. Before wiring,
tests must prove the adapter-level exact allowlist and HOLD behavior. A weak implementer
must not claim that passing `validate_blackboard_message` proves brain provenance.

### F-05 — P3 — Hermes display output has no explicit mapping to the existing remote projection

The Hermes design ends with an in-memory schema-valid task/annotation preview for Owner
display (`13_HERMES_WIRING_DESIGN.md:168-185`). The existing remote display builder does
not accept either Blackboard message directly: it requires an exact aggregate source
with `phase`, `status`, `approval_readiness`, decision fields, and
`evidence_bundle_hash` (`app/remote_readonly_projection.py:66-87,187-235`).

This is not a present runtime conflict because remote wiring is explicitly unauthorized.
It is an integration ambiguity. A future dashboard/remote package must either define a
separate trusted aggregate mapping or explicitly exclude the remote projection. Passing
a task draft or annotation directly, inventing a placeholder evidence hash, or copying
model text into the aggregate must fail closed.

## 4. Cross-contract field-existence check

| Design claim | Existing contract check | Result |
|---|---|---|
| 13 §6 task-draft field table | All 15 fields exist in `task_draft.schema.json` | aligned |
| 13 §7 annotation field table | All common and annotation-specific fields exist in `annotation.schema.json` | aligned |
| 12 ten board message types | Exact set equals `blackboard_validators.SCHEMA_FILES` | aligned |
| 11 §5 structured v1.1 audit evidence | Digests, preconditions, commit ids, and test results absent from `audit_event.schema.json` | **HOLD — F-01** |
| 11 §7 / 14 §6 exact Git rollback target | Commit/parent/target-hash fields absent; current builder is no-rollback preview only | **HOLD — F-02** |
| 13 display preview → remote projection | Projection requires a separate exact aggregate source not defined in 13 | clarify — F-05 |

## 5. Authorization-language check

- `11_V1_1_FIRST_REAL_WRITE_DESIGN.md:3-8,263-264` states that the document is not
  authorization and that v1.0 closeout plus a new Owner instruction are prerequisites.
- `12_BLACKBOARD_DATA_LAYOUT.md:3-8,107-135` keeps the proposed `data/` tree absent and
  the implemented helper read-only.
- `13_HERMES_WIRING_DESIGN.md:3-7,230-244` makes runtime and Blackboard wiring an Owner
  gate.
- `14_V1_2_FIRST_CODE_TASK_DESIGN.md:3-8,192-206` requires v1.1 signoff plus a new v1.2
  instruction and grants no execution path.

No sentence was found that converts a preview, schema-valid message, Owner decision as
data, role label, or completed earlier phase into standing execution/write authority.

## 6. Fresh-context handoff

Before any implementation package based on 11–14:

1. resolve F-01 and F-02 through explicit versioned contracts;
2. make the F-03 decode/hash boundary mechanical rather than caller folklore;
3. test F-04 provider allowlisting outside the permissive provenance string schema;
4. decide F-05 explicitly instead of fabricating an aggregate projection source;
5. rerun a fresh-context authorization review against the exact implementation diff.
