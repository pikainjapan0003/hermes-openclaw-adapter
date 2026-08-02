# Approval-packet / evidence-bundle field contract proposal

Status: proposal only; no option is authorized.

Date: 2026-08-04

Owner decision: ______

## Measured shapes

This proposal starts from the real closed contracts, not names that sound similar.

| Concept | Approval packet | Evidence bundle |
|---|---|---|
| `task_id` | Top-level (`approval_packet.schema.json:121-124`) | `.task.task_id` (`evidence_bundle.json:26-36`) and correlation copies in `.command_envelope` / `.mock_result.gateway_response` |
| `schema_version` | Top-level non-empty string (`approval_packet.schema.json:33-36`) | Top-level const `"1.0"` (`evidence_bundle.json:22`) |
| `execution_class` | Top-level const `AUTO` (`approval_packet.schema.json:95-97`) | `.task.execution_class` const `AUTO` (`evidence_bundle.json:36`) |
| `safety_flags` | Top-level canonical 16-boolean object (`approval_packet.schema.json:47-86`) | Absent from the closed top-level property list and all nested definitions |
| Composition gate | None | None |

The valid fixtures corroborate these positions: `fixtures/blackboard_contract/approval_packet.valid.json:2-29` and `fixtures/local_mock_data/n1_dry_run_evidence_bundle.json:1-61`. Therefore “compare four common top-level fields” is not an implementable current contract.

## Option A — typed accessor/composition layer

Define pure accessors that project semantically comparable values without changing either artifact:

- `task_id`: packet top-level ↔ bundle `.task.task_id`, with bundle-internal correlation checked first;
- `schema_version`: packet top-level ↔ bundle top-level;
- `execution_class`: packet top-level ↔ bundle `.task.execution_class`;
- `safety_flags`: no comparison unless a separately approved policy derives a named safety profile from existing bundle const fields.

The composition gate would accept both complete artifacts, validate each against its own schema, run the accessors, then return a separate comparison result. It must not mutate either input.

- Risk: accessors become a third contract and can drift from both schemas.
- Weak-model misread: a derived safety profile could be mistaken for the canonical 16 flags. It must have a different name and explicit provenance.
- Migration cost: new pure module/schema-or-typed result, per-accessor fixtures, internal bundle-correlation checks, and caller audit.

## Option B — mirror selected fields at evidence-bundle top level

Add top-level `task_id`, `execution_class`, and possibly `safety_flags` to the evidence-bundle schema and builder, keeping nested copies for current consumers.

- Risk: duplicate sources of truth. Every builder path must reject divergence between top-level and nested copies. Adding canonical `safety_flags` also changes the meaning of a Phase 5 artifact that currently expresses safety through narrow const fields.
- Weak-model misread: a mirrored field may be treated as independent authority rather than a redundant copy.
- Migration cost: schema migration, builder changes, golden-vector rewrite, hash changes, fixture updates, downstream hash/projection/rollback tests, version policy.

## Option C — declare no cross-builder consistency guarantee

Keep the contracts independent. Consumers validate each artifact separately and rely only on explicit references already present in the approval packet (`dry_run_evidence`) and evidence-bundle internal correlation.

- Risk: no mechanical proof that a packet and bundle refer to the same task beyond caller-managed correlation. A caller can accidentally pair valid but unrelated artifacts.
- Weak-model misread: “both valid” may be mistaken for “valid as a pair.” Documentation must deny that inference.
- Migration cost: documentation and tests that reject any claim of composition; no product/schema change.

## Comparison

| Criterion | A: accessors | B: mirrors | C: independent |
|---|---|---|---|
| Changes existing schemas/hashes | No | Yes | No |
| Proves task/execution-class agreement | Yes | Yes | No |
| Represents canonical safety flags | Not without separate policy | Could, with major semantic expansion | No |
| Duplicate-value drift risk | Low | High | None inside artifacts |
| New composition surface | Yes, explicit | Yes, embedded | No |

## Suggested option (not a decision)

Option A is the smallest path to a real join contract without rewriting evidence-bundle hashes. The initial accessor contract should compare only the three fields that actually exist semantically on both sides. `safety_flags` must remain out of scope until the Owner separately authorizes a derivation rule or Option B's schema expansion.

## Owner decision gate

Reply format: `CROSS_BUILDER choose A`, `CROSS_BUILDER choose B`, or `CROSS_BUILDER choose C`. If choosing A or B, state separately whether safety-profile derivation is authorized. Until then there is no cross-builder composition gate and no shared four-field shape.
