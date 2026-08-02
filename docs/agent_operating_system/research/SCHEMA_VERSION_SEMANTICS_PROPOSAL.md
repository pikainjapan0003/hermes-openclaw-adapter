# `schema_version` semantics proposal

Status: proposal only; no option is authorized.

Date: 2026-08-04

Owner decision: ______

## Verified current state

The ten Blackboard schemas accept any non-empty string for `schema_version`. For example, `docs/schemas/blackboard/approval_packet.schema.json:33-36` uses `type: string` plus `minLength: 1`. Selection in `app/blackboard_validators.py` is by `message_type`, not by a version compatibility table. Consequently a whitespace-only value such as `" "` is structurally valid today. The evidence-bundle contract is different: `docs/schemas/evidence_bundle.json:22` fixes its version to `"1.0"`.

This mismatch is descriptive evidence, not permission to change either contract.

## Option A — format pattern in every Blackboard schema

Add a shared pattern such as `^[0-9]+\.[0-9]+$` to each Blackboard `schema_version` property.

- Benefit: rejects whitespace and malformed spelling mechanically while allowing future numeric versions.
- Risk: a syntactically valid but unsupported value such as `99.99` still passes; callers may mistake format validity for compatibility.
- Weak-model misread: “matches the pattern” may be treated as “supported.” The error surface must distinguish malformed from unsupported.
- Existing-test impact: the 30 positive Blackboard fixtures remain valid; mutation tests that currently demonstrate permissiveness change; all schema inventory and renderer-fidelity tests must be rerun.
- Migration cost: edit 10 schemas, add malformed-format fixtures/tests, document compatibility outside schema.

## Option B — explicit enum allowlist in every Blackboard schema

Use an enum containing only versions accepted by the current implementation, initially `["1.0"]`.

- Benefit: strongest fail-closed behavior; structural validity and supported-version membership agree.
- Risk: adding a compatible release requires a coordinated ten-schema update. Divergent enums between message types could split a chain.
- Weak-model misread: an enum member may still be treated as proof that mixed-version chains are safe; chain-level policy remains necessary.
- Existing-test impact: current positive fixtures remain valid; permissiveness demonstrations change; new unknown-version and mixed-chain tests become normative.
- Migration cost: edit 10 schemas together, add a mechanical cross-schema enum-equality guard, document upgrade ordering.

## Option C — validator compatibility table

Keep schema syntax broad but make `validate_blackboard_message` select a schema through an explicit `(message_type, schema_version)` compatibility map and return a structured unsupported-version error before schema validation.

- Benefit: version support is centralized; it can express per-message migration windows and reject unknown versions without duplicating enums.
- Risk: standalone JSON Schema validation would remain more permissive than the application validator. Two validators could make conflicting claims.
- Weak-model misread: direct `jsonschema` success could be mistaken for complete contract acceptance.
- Existing-test impact: all existing fixtures remain valid, but validator selection/error tests and every caller that bypasses the validator require audit.
- Migration cost: validator code, structured selection errors, compatibility-table tests, and documentation distinguishing syntax from support.

## Comparison

| Criterion | A: pattern | B: enum | C: validator table |
|---|---|---|---|
| Rejects `" "` | Yes | Yes | Yes through validator only |
| Rejects unknown numeric version | No | Yes | Yes through validator only |
| Standalone schema is authoritative | Partly | Yes | No |
| Multi-version migration flexibility | Medium | Low | High |
| Weak-model ambiguity | Medium | Low | High |
| Estimated implementation surface | 10 schemas + tests | 10 schemas + guard + tests | validator + caller audit + tests |

## Suggested option (not a decision)

Option B is the narrowest v1.0 fail-closed contract: one supported version, one mechanically identical enum across all ten Blackboard schemas, and no difference between standalone schema validation and the application validator. If the Owner anticipates overlapping migrations soon, Option C is more flexible but needs a separate rule forbidding callers from treating raw JSON Schema success as acceptance.

## Owner decision gate

Reply format: `SCHEMA_VERSION choose A`, `SCHEMA_VERSION choose B`, or `SCHEMA_VERSION choose C`, with any allowed migration window stated explicitly. Until then, current behavior remains unchanged and no package may claim that version compatibility is enforced.
