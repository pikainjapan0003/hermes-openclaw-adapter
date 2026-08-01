# v1.1 / `produced_by` Impact Analysis v2

**PLANNING ONLY, NOT AUTHORIZED.** This document consolidates the current
impact surfaces for the unresolved v1.1 audit/rollback choices and the
`produced_by` policy choice. It does not select an option, edit a schema,
create a writer, issue a token, execute Git, or wire a runtime.

## Current baseline

The v1.0 Blackboard schemas are closed and stable. `audit_event` and
`rollback_event` currently describe preview/in-memory evidence; the existing
builders are pure functions. The approval packet still requires
`single_use_execution_token: null`. The Phase 7 writer and Phase 9 execution
gate are absent by design. `produced_by` is currently a non-empty string and is
provenance, not authentication, approval, or execution authority.

The four pending Owner decisions are independent until a future contract
package explicitly couples them:

| Decision | Options already documented | Current status |
|---|---|---|
| AUD | A extend `audit_event`; B new closed `v1_1_write_record`; C structured `event_notes` grammar | Owner choice blank |
| RB | A version `rollback_event`; B new `v1_1_rollback_record`; C embed in the selected write record | Owner choice blank |
| PB | A exact enum; B namespace plus reviewed registry; C policy-only string | Owner choice blank |
| ROOT/projection | Root `parent_task_id: null` and projection source rules | Owner rule required before implementation |

## Cross-surface impact matrix

| Surface | AUD choice changes | RB choice changes | PB choice changes | Must remain true |
|---|---|---|---|---|
| Closed schemas | Required fields, versioning, inventory, and compatibility | Commit/parent/target/outcome representation and preview separation | Affected producer scope, enum/pattern or no schema change | No schema is edited by this analysis |
| Fixtures | Valid, missing-common, bad-digest, bad-precondition, and version cases | Preview, planned, succeeded, failed, and ancestry cases | Unknown, confusable, and source-disagreement cases | No real token, path, secret, or runtime data |
| Builders/readers | New constructor or explicit caller preconditions | Preview builder must remain unable to claim a real Git binding | Trusted adapter must supply policy value; model text is not trusted | Pure/read-only until separately authorised |
| Hash chain | Canonical fields and append-only event type | Immutable references to the selected write/audit record | Provenance is never a hash-chain authorization | Earlier records are not rewritten |
| Projection/display | New fields need an explicit allowlist and redaction review | Git identifiers require a separate display decision | Display value is provenance only | No remote transport or new route |
| Tests/reviews | Inventory, mutation, vectors, cross-record and migration tests | Lifecycle, ancestry, tamper and no-Git tests | Exact scope, registry/policy disagreement and confusable tests | Fresh adversarial review before implementation |
| Governance | 05/07/11/14, INDEX, readiness and backlog updates | Same plus recovery procedure | 13, INDEX, onboarding and adapter policy | Each decision needs a separate Owner record |

## Compatibility and sequencing

1. Decide AUD and RB together enough to define immutable cross-record links;
   do not implement one while silently assuming the other.
2. Decide the affected `produced_by` message types before changing any enum or
   pattern. Applying a Hermes producer allowlist to worker or Owner records
   without an inventory would reject valid provenance.
3. Decide the root/projection rule before an adapter emits a root record to a
   remote read-only projection. A `null` parent must not be filled with a
   guessed value.
4. After each choice, produce a field-by-field contract, fixtures, negative
   tests, golden vectors, migration note, and fresh-context review as a
   separate package. Only then can an Owner-authorised implementation package
   be considered.

## Misread and rollback risks

- A schema-valid producer string is not an authenticated identity.
- A commit hash in a preview is not proof that a write or revert occurred.
- A valid audit/rollback record is evidence, not a command or dispatch signal.
- Additive message types are generally easier to migrate than changing a
  v1.0 closed type, but they increase inventory and consumer obligations.
- A free-text grammar has the smallest immediate schema surface and the
  greatest long-term ambiguity; it must never be treated as typed evidence
  without a separately reviewed parser.

## Decision record (blank by design)

| Decision | Owner selection | Date | Follow-up contract package |
|---|---|---|---|
| AUD | ____________________ | __________ | ____________________ |
| RB | ____________________ | __________ | ____________________ |
| PB | ____________________ | __________ | ____________________ |
| ROOT/projection | ____________________ | __________ | ____________________ |

Until all applicable rows are filled by the Owner and converted into an exact
implementation brief, the safe disposition is **HOLD**. This analysis never
overrides the Phase 7 and Phase 9 hard gates.
