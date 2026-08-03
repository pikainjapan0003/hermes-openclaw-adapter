# Phase 9 Token Schema Proposal

Status: **PLANNING ONLY. NOT AUTHORIZED. NO SCHEMA IS CHANGED BY THIS DOCUMENT.**

Date: 2026-08-03
Decision scope: how a future Phase 9 gate receives a live one-use token while
preserving the Phase 4 guarantee that an accepted v1 approval packet cannot
carry execution authority.

Authorization ladder: an Owner schema selection chooses an option only; a later
exact instruction must separately authorize schema/code implementation; after
that work passes independent review, another exact Owner-present instruction
must authorize the one execution. No layer implies the next.

## Threat model

Source: `05_VERIFIED_LONG_TERM_PLAN.md` §6.16, commit `e34ca1c`.

> 在範圍內（設計必須擋住）：模型過度熱心、誤解授權、自作主張、把顯示當授權、意外重放、崩潰後誤續跑。
>
> 明確不在範圍內：一個刻意規避的對抗性模型。
>
> 已知並接受的殘餘風險（不得再被當成待修缺陷）：模型可經 `wsl.exe -u root` 取得 root；gate 程式碼與 `.venv` 對模型可寫；burn ledger 與 frozen artifact 可被有意刪改；`~/.openclaw/` config 可被有意竄改。

Accordingly, this document relies on **procedural constraint plus best-effort
technical isolation, effective against a non-adversarial model**. It makes no
claim that a deliberately evasive model is mechanically excluded.

## 1. Accepted baseline

The current `approval_packet.schema.json` is a Phase 4, data-only contract:

- `single_use_execution_token` is required but structurally fixed to JSON null
  (`docs/schemas/blackboard/approval_packet.schema.json:191-194`);
- its description says real token design belongs to Phase 9;
- `decision` is inert offline data, never dispatch permission
  (`approval_packet.schema.json:196-199`);
- `additionalProperties` is false;
- current fixtures and `approval_packet_builder.py` always produce null; and
- reverse tests reject a non-null token and prove a packet cannot reach
  execution (`tests/test_approval_packet.py:42,65-75,182-186`).

The current accepted run has 2305 non-skipped test outcomes (2320 collected
items including 15 environment/platform skips). A repository search finds
direct token assumptions across 15 schema, fixture, builder, and test files.
Those counts describe the review baseline; they are not permission to edit any
of those files in this docs-only batch.

## 2. Safety requirements for every acceptable option

1. An old v1 approval packet must always reject a string/object token at schema
   validation, before gate logic.
2. A Phase 4 builder must remain unable to create a live-token artifact.
3. The raw token is transient secret material. Persisted evidence records only
   a non-reversible digest/reference and binding metadata.
4. The live-token contract must have an explicit version discriminator; unknown
   or downgraded versions fail closed.
5. Validation alone never executes. A separate Owner-authorized gate must also
   check frozen packet/evidence/action bindings, Owner presence, expiry, durable
   burn, and deny-all posture.
6. Fixtures use clearly synthetic non-secret examples and cannot be accepted by
   the real ceremony/gate.
7. No option may reinterpret an existing `decision: approve` as permission.
8. The live-token presentation reaches a gate running as an OS principal
   different from the model, or through a wholly off-host channel; same-principal
   ingress/egress is structurally unacceptable regardless of schema validity.
9. The Owner independently observes the canonical packet/action digests through
   the approved non-model egress or trusted frozen-artifact reader before the
   transient presentation can validate at the gate boundary.

## 3. Option A — dedicated Phase 9 authorization contract

Keep `approval_packet.schema.json` unchanged. Add a separate, future Phase 9
contract for a **transient execution-authorization presentation**. It references
the immutable v1 approval packet by id/hash and carries the live token only at
the in-memory gate boundary. Persisted/audit form replaces the raw value with a
digest and burn reference.

Proposed contract responsibilities:

- exact Phase 9 contract version and rehearsal id;
- approval packet id/hash and evidence bundle hash;
- action hash, exact target digest, timeout, and attempt number `1`;
- issued/expiry timestamps and Owner-session confirmation reference;
- transient `single_use_execution_token` with minimum entropy/length rules;
- explicit `persistence_forbidden: true`; and
- no worker, queue, connector, follow-up, or general allowlist fields.

### How v1 remains impossible to tokenize

The v1 approval schema is byte-for-byte unchanged and still requires token null.
The gate takes two separately validated inputs: v1 approval packet plus Phase 9
authorization presentation. Supplying a token inside the approval packet fails
before gate comparison. The Phase 9 contract cannot repair or wrap an invalid
approval packet.

### Test impact

- Existing Phase 4 builder, fixtures, dashboard, reverse tests, schema inventory,
  and non-null rejection tests remain semantically unchanged.
- New tests cover the separate schema, transient/persisted redaction boundary,
  exact binding, expiry, replay, version rejection, and synthetic-fixture ban.
- If registered as a Blackboard message, inventory counts and common-field
  contract tests expand; the recommended placement is a non-Blackboard Phase 9
  transient contract, like a specialized gate input, so it cannot appear as a
  normal board message.
- Trust-violation scanning needs one narrow allowlist for the future dedicated
  module and must keep rejecting token material everywhere else.

### Risk

Two-object validation is slightly more work, and developers may try to persist
the transient object. A hard no-persistence test and typed separation between
transient presentation and redacted audit record are required.

**Assessment: recommended.** It preserves the strongest structural Phase 4
guarantee and makes Phase 9 authority visibly separate.

## 4. Option B — versioned approval-packet branches

Change the approval-packet schema into explicit version branches:

- v1 branch: exact `schema_version` v1 value and token `type:null,const:null`;
- v2 branch: exact v2 discriminator plus the Phase 9 token/binding fields;
- no generic non-empty version string; and
- exactly one branch must validate, with closed properties in each branch.

The Phase 4 builder would remain v1-only. A future separately named Phase 9
builder would be the only component allowed to create v2.

### How v1 remains impossible to tokenize

The branch discriminator must be a schema `const`, not application convention.
The v1 branch retains token null, and a token string cannot cause automatic
upgrade to v2. The gate rejects v1 for execution even when its decision is
approve. Version conversion requires a fresh artifact and Owner ceremony; an
existing packet cannot be mutated in place.

### Test impact

- All current v1 fixtures and builder outputs require regression validation
  against the v1 branch.
- `tests/test_approval_packet.py`, preflight checks, trust scans, mutation/fuzz
  tests, golden vectors, contract rendering, inventory, and dashboard display
  need new v1/v2-specific assertions.
- Tests that directly inspect `properties.single_use_execution_token.const`
  must be redesigned to resolve the selected branch, increasing complexity.
- Phase 4 reverse tests must explicitly prove v1 non-null rejection and prove an
  approved v1 packet still cannot invoke the gate.
- Conditional-schema mutation coverage must attack missing, duplicated, unknown,
  downgraded, and cross-branch version/token combinations.

### Risk

Execution-adjacent data enters the same message type used for offline approval.
A weak model can mistake “v2 approval packet” for executable permission, and
schema composition mistakes can accidentally allow both/no branches. The test
and review surface is substantially larger than Option A.

**Assessment: viable but not preferred.** Choose only if one message type is an
important Owner requirement.

## 5. Option C — directly relax the current field

Change the existing token property from null-only to null-or-string while
leaving the current loose `schema_version` and message type in place.

### Effect on the Phase 4 guarantee

This option destroys the structural guarantee: a historical v1-shaped packet
could validate with a token. An application gate might later reject it, but the
weak-model safety property “format alone rejects a live token” would be gone.
There is no schema-level method under this option to prove that old v1 packets
can never carry tokens; adding such a discriminator converts it into Option B.

### Test impact

- Current non-null rejection, token-null builder, preflight, trust scan, fixture,
  mutation, and golden assertions fail or must be weakened.
- Phase 4’s “packet cannot reach execution” negative assurance becomes dependent
  on runtime code that does not yet exist.
- Every consumer of `approval_packet` must distinguish inert and live-token data
  without a reliable version branch.
- The broad accepted suite may remain superficially green only by deleting or
  loosening precisely the safeguards Phase 4 established.

### Risk

Highest weak-model ambiguity, downgrade ambiguity, accidental secret
persistence, and retroactive contract change. It makes schema-valid data look
more authoritative while providing no execution-gate safety by itself.

**Assessment: reject.** It cannot satisfy the v1-old-packet requirement.

## 6. Comparison

| Criterion | A: dedicated contract | B: version branches | C: direct relax |
|---|---|---|---|
| v1 packet structurally token-free | Strongest; unchanged schema | Strong if branch is exact and closed | **No** |
| Phase 4 reverse guarantee | Unchanged | Preserved with substantial new tests | Weakened/broken |
| Raw token separation | Clear transient boundary | Mixed into approval message family | Poor |
| Existing-suite disruption | Lowest | High | High and safety-negative |
| Weak-model readability | Two clearly named artifacts | Version distinction must be understood | Ambiguous |
| Recommended | **Yes** | Conditional alternative | **No** |

## 7. Required implementation-package proof, regardless of choice

Before any real token is accepted, an independently reviewed package must prove:

- every historical/fixture v1 packet with a non-null token fails schema
  validation;
- unknown and downgraded versions fail;
- raw token never persists or appears in errors;
- packet validation does not call a gate or executor;
- the same token presented twice produces at most one fake-executor start;
- process restart and concurrent presentation preserve replay denial;
- `approve` without a separately valid Phase 9 authorization remains inert; and
- no worker, queue, route, or follow-up path is introduced for N=1.

## 8. Owner decision record

Schema option (`A`, `B`, or `C`): ____________________

If B, exact v2 discriminator: ____________________

Transient token retention/display limit: ____________________

Owner notes / required changes: ____________________________________________

Decision date and explicit implementation authorization: ____________________

Until the Owner fills this record and issues a separate implementation brief,
the accepted schema remains unchanged and the live token remains impossible.
