# v1.1 AUD/RB Option Impact Analysis

Status: **PLANNING ONLY, NOT AUTHORIZED — AUD/RB DECISIONS BLANK**

Sources: `11_V1_1_FIRST_REAL_WRITE_DESIGN.md` §§5.1–5.2 and the corrected
Owner one-pager. This analysis estimates change surfaces after a future Owner
selection. It does not change a schema, write a file, run Git, or choose an
option.

## Scale convention

| Range | Meaning |
|---|---|
| S | roughly 1–2 implementation/review packages; localized contract or documentation work |
| M | roughly 3–4 packages; new/changed contract plus fixtures, validators, rehearsal, documentation, review |
| L | roughly 5+ packages; coupled contracts, compatibility/migration, multiple review gates |

Ranges assume the design choice has already been made. Phase 7/9/v1.1 write
authorization remains separate.

## AUD — v1.1 structured audit evidence

AUD decision: **________**

### AUD-A — extend existing `audit_event`

| Surface | Expected impact |
|---|---|
| Schema | Version or conditionally extend `docs/schemas/blackboard/audit_event.schema.json` with write digest, preconditions, immutable commit reference, and test result. Because the schema is closed, every new field changes accepted instances. |
| Fixtures | Update/add valid and negative audit fixtures; preserve a v1.0 compatibility fixture or explicitly version it. |
| Validator/index | Existing `audit_event` registration remains, but version selection/compatibility behavior must be explicit. |
| Tests | Inventory, common fields, mutation/fuzz, chain, board-reader, renderer, golden vectors, and v1.1 write-record semantics all need review. |
| Documentation | 05/07/11, schema INDEX, board layout, readiness, rollback crosswalk, and onboarding language. |
| Migration | Highest risk of making old audit evidence fail a newly strict contract or letting optional fields weaken v1.1 evidence. |

Work estimate: **M–L**. Irreversibility: **medium-high** once mixed-version audit
records exist. Rolling back the schema cannot erase already emitted record
shapes; a version strategy is mandatory.

### AUD-B — new closed `v1_1_write_record` (source recommendation)

| Surface | Expected impact |
|---|---|
| Schema | Add one new closed schema; do not alter existing `audit_event`. Define common fields, digest/precondition/commit/test fields, and explicit links to task/result/audit evidence. |
| Fixtures | At least one valid plus missing-common, extra-safety, bad-link, bad-digest, and invalid-state cases. |
| Validator/index | Add a new registration and update exact inventory counts/guards. Board-layout inclusion must be separately decided; no automatic board write. |
| Tests | Schema/fixture tests, builder or data-constructor tests, independent hash/golden vectors, cross-record rehearsal, mutation/fuzz, renderer/index/path guards. |
| Documentation | 05/07/11, INDEX, readiness, future writer package, and rollback linking. |
| Migration | Existing v1.0 audit events stay stable; new consumers must explicitly understand the new message type. |

Work estimate: **M–L**. Irreversibility: **medium**; additive contract is easier
to retire/version, but registered records become a compatibility obligation.

### AUD-C — structured grammar inside `event_notes`

| Surface | Expected impact |
|---|---|
| Schema | Potentially none, but the lack of typed fields is the core tradeoff. A strict grammar/version prefix must be designed outside JSON Schema or added as a pattern. |
| Fixtures | Notes covering escaping, Unicode, delimiter injection, missing keys, duplicate keys, size, and version mismatch. |
| Validator/index | Existing validator may accept malformed “structured” notes unless a separate parser/gate is created. |
| Tests | Parser round-trip, canonicalization, ambiguity/no-leak, mutation/fuzz, and proof that free prose is not misread as structured evidence. |
| Documentation | 07/11 must clearly distinguish schema-valid event from grammar-valid v1.1 evidence. |
| Migration | Easy to emit, hard to evolve safely; old prose and new grammar share one field. |

Work estimate: **S–M** initially, potentially **L** after compatibility hardening.
Irreversibility: **high semantic debt**; ambiguous strings can persist even if a
later typed schema is chosen.

## RB — rollback Git binding

RB decision: **________**

### RB-A — version existing `rollback_event`

| Surface | Expected impact |
|---|---|
| Schema | Add/version immutable `write_commit`, parent, target hash, and revert outcome/state fields while preserving preview-only v1.0 semantics. |
| Fixtures | Separate preview-only and real-write-era vectors; negatives for guessed/mutable/mismatched commit ancestry and impossible outcome states. |
| Validator/index | Existing registration needs version/conditional rules; current preview builder must not accidentally produce a real binding. |
| Tests | Schema/mutation, builder fail-closed, audit/write link, golden vectors, and explicit no-Git execution tests. |
| Documentation | 07/11/14/readiness/INDEX and rollback recovery procedure. |
| Migration | High risk that one message type is mistaken as both preview text and authorization-capable rollback evidence. |

Work estimate: **M–L**. Irreversibility: **medium-high** due mixed semantics under
one message type.

### RB-B — new `v1_1_rollback_record` (source recommendation)

| Surface | Expected impact |
|---|---|
| Schema | Add a distinct closed evidence record with immutable links to the selected AUD contract; record intent/outcome, never a Git command. |
| Fixtures | Valid planned/completed/failed states and negatives for ancestry, target, outcome, AUD link, duplicate/reuse, and token-like fields. |
| Validator/index | New registration and exact inventory updates; board/storage location separately decided. |
| Tests | Schema/builder/data constructor, cross-record rehearsal, independent hashes, mutation/fuzz, and AST/runtime proof that validation never invokes Git. |
| Documentation | 07/11/14, schema INDEX, recovery runbook, readiness, and future human Git procedure. |
| Migration | Existing rollback previews remain stable; consumers opt into a clearly different record. |

Work estimate: **M–L**. Irreversibility: **medium** as an additive, versionable
contract.

### RB-C — embed rollback binding in selected write record

| Surface | Expected impact |
|---|---|
| Schema | Coupled to AUD. Add rollback target and outcome lifecycle inside the chosen write-record shape. AUD-C would require a nested string grammar and is especially ambiguous. |
| Fixtures | Joint AUD/RB state matrix; cases where write succeeds before rollback is requested, rollback fails, or no rollback is applicable. |
| Validator/index | One record changes state or needs append-only successor semantics; mutation of an earlier record is forbidden. |
| Tests | Joint lifecycle, immutability, ordering, hash-chain, partial failure, and no-Git execution proofs. |
| Documentation | One authoritative joint AUD/RB state machine plus recovery and append-only rules. |
| Migration | Tight coupling makes later separation expensive and can enlarge every write record even when rollback is never needed. |

Work estimate: **L**, after AUD is selected. Irreversibility: **high coupling**.

## Cross-option compatibility

| AUD \ RB | RB-A | RB-B | RB-C |
|---|---|---|---|
| AUD-A | Possible; two versioned existing records create the largest compatibility matrix. | Possible; additive rollback record can link to versioned audit. | Possible but strongly couples extended audit lifecycle to rollback. |
| AUD-B | Possible; new write record links to a versioned existing rollback event. | Cleanest separation of evidence types, but adds two registered contracts. | Possible; makes the write record responsible for rollback lifecycle. |
| AUD-C | Weak typed link; requires grammar/parser bridge. | New rollback record would reference an opaque grammar identity. | Highest ambiguity and parsing debt; requires a joint grammar before implementation. |

“Possible” is not a recommendation or authorization. The selected pair still
needs a joint field-by-field contract and lifecycle review.

## Non-negotiable boundaries after any choice

1. A record stores evidence; it never executes Git or a write.
2. Commit IDs cannot be guessed from HEAD, time, prose, or model output.
3. Append-only history records outcomes in later entries; it does not rewrite an
   earlier attempt.
4. Existing v1.0 preview semantics remain distinguishable and fail closed.
5. Schema implementation, Phase 7 writer work, v1.1 real write, and rollback
   execution each require their own exact later authority.
