# Owner Decision Preflight

Status: **PLANNING ONLY, NOT AUTHORIZED — ALL DECISIONS BLANK**

Purpose: show the work that would follow each possible RED/AUD/RB/PB/ROOT
direction before the Owner replies. A reply selects a design direction only; it
does not itself authorize schema edits, validator changes, a writer, Git
operations, runtime wiring, execution, dispatch, or remote exposure.

The authoritative option identities remain their source designs and the
corrected `OWNER_DECISION_ONE_PAGER_20260726.md`. Package counts below are
planning ranges, not commitments or authorization.

## RED — schema-error redaction

Current decision: **________**

| If Owner selects | Next separately issued work | Explicitly will not happen from selection alone | Estimated packages |
|---|---|---|---:|
| A — redact inside each validator | Inventory both validator implementations and every structured error field; define one closed redacted-error record; implement validator-side redaction; update E-01/E-02 tests and run fresh-context leak review. | No new route, remote display, raw-error export, schema widening, runtime call, or persistence. | 3–4 |
| B — keep validator output; redact exposure points | Inventory every current/future exposure boundary; define a mandatory boundary wrapper; add fail-closed tests proving raw errors cannot bypass it; separately implement only named exposure sites. | Validators and schemas remain unchanged; no exposure is created merely to exercise the wrapper. | 3–4 |
| C — double layer (document recommendation) | Define separate validator-safe and exposure-safe records; implement validator minimization first; add exposure re-redaction and cross-layer no-leak tests; independent adversarial review. | No claim that either layer alone permits external display; no runtime/remote wiring. | 4–5 |

Fail-closed default while blank: keep all 14 xfail baselines visible; export no
raw validator or script error to an untrusted surface.

## AUD — v1.1 structured audit evidence

Current decision: **________**

| If Owner selects | Next separately issued work | Explicitly will not happen from selection alone | Estimated packages |
|---|---|---|---:|
| A — extend `audit_event` | Produce a versioned schema-change design; enumerate backward-compatibility and fixture migration; implement schema/fixtures/validator tests only after approval; update v1.1 design crosswalk. | No audit writer, file creation, append, real write, token, or execution. | 3–4 |
| B — new `v1_1_write_record` (document recommendation) | Freeze a new closed record contract; design IDs/hash references to existing audit evidence; add schema, fixtures, validator registration, and in-memory rehearsal; adversarial review. | Record acceptance never writes a file or executes a task. Phase 7 remains separately gated. | 4–5 |
| C — structured string in `event_notes` | Define canonical string grammar, escaping, size limits, and parse-failure behavior; test round-trip and ambiguity attacks; document loss of typed validation. | No claim that an opaque string is equivalent to a closed schema until its limits are explicitly accepted. | 2–3 |

Fail-closed default while blank: do not modify any schema and do not represent
v1.1 write evidence as already structured.

## RB — rollback Git binding

Current decision: **________**

| If Owner selects | Next separately issued work | Explicitly will not happen from selection alone | Estimated packages |
|---|---|---|---:|
| A — version `rollback_event` | Design a versioned record containing immutable write commit, parent, target hash, and outcome fields; assess compatibility; implement contract fixtures/tests only after approval. | No `git revert`, subprocess, repository mutation, or guessed commit. | 3–4 |
| B — new `v1_1_rollback_record` (document recommendation) | Freeze a separate closed record linked to the selected AUD record; add schema/fixtures/validator and in-memory link rehearsal; independent review. | The record is evidence only and never invokes Git. | 4–5 |
| C — embed rollback fields in the selected write record | First require a compatible AUD choice; specify nested fields and lifecycle states; test immutable links and partial/failure states. | No implementation before both AUD and RB choices are jointly reconciled. | 3–4 after AUD contract |

Fail-closed default while blank: previews remain descriptive; never infer a Git
target from HEAD, recency, text, or model output.

## PB — Hermes `produced_by`

Current decision: **________**

| If Owner selects | Next separately issued work | Explicitly will not happen from selection alone | Estimated packages |
|---|---|---|---:|
| A — exact enum (document recommendation) | Inventory every existing producer string and fixture; design schema migration/version behavior; update all ten schemas only under a specifically authorized schema package; add compatibility tests. | Provenance does not become authentication, approval, role authority, or execution permission. | 3–4 |
| B — namespace pattern plus registry | Define syntax, registry ownership, unknown-producer behavior, and offline registry fixture; test pattern/registry disagreement fail-closed; then separately authorize schema work. | No network registry, dynamic trust, runtime lookup, or automatic producer enrollment. | 4–5 |
| C — policy-only non-empty string | Document the exact adapter-side allowlist and its ownership; add future-adapter fail-closed tests without changing schemas. | The schema continues to accept other non-empty strings; no claim that schema validation authenticates provenance. | 2–3 |

Fail-closed default while blank: schemas remain non-empty strings; any future
adapter must independently enforce the currently documented exact producer set.

## ROOT — root `parent_task_id: null` projection

Current decision: **________**

There are **no formally labelled source options yet**. The corrected one-pager's
suggested null direction is not an option label and cannot be selected as
`ROOT=R`.

| If Owner gives a direction | Next separately issued work | Explicitly will not happen from direction alone | Estimated packages |
|---|---|---|---:|
| Ask for a formal comparison first | Produce a planning-only design comparing at least: versioned JSON null, explicit root discriminator, or fail-closed omission/rejection; include migration and weak-model misread analysis. | No projection schema/builder change and no placeholder parent. | 1 design package, then 2–4 implementation/review packages after a later selection |
| Say “follow the suggested null direction” | Treat it only as authority to prepare the formal versioned-null design and acceptance checklist; return for confirmation if the resulting contract changes scope. | No immediate schema edit, runtime projection, aggregation, transport, or remote wiring. | 1–2 design packages, then 2–4 later packages |
| Keep ROOT blank/HOLD | No product work; retain explicit rejection of root projection through the current builder. | Never hash, invent, or serialize a fake parent ID. | 0 |

Fail-closed default while blank: root projection remains HOLD.

## Cross-choice ordering constraints

1. RED can be designed independently but cannot create an exposure route.
2. AUD should be selected before implementing RB Option C; any AUD/RB pair must
   receive a joint ID/hash/lifecycle crosswalk.
3. PB schema choices require a complete producer inventory before schema edits.
4. ROOT needs a formal option design before a letter-labelled selection exists.
5. Phase 7 and Phase 9 remain separate Owner hard gates regardless of any choice.
6. Every implementation package must restate its exact whitelist, tests,
   negative scope, and rollback; no row above is itself a work order.

## Owner reply preflight

The corrected one-pager can safely accept formal selections for RED/AUD/RB/PB.
ROOT should be a prose direction or remain blank until formal options exist.

Owner reply: **________**
