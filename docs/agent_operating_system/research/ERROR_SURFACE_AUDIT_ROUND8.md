# Error Surface Audit — Round 8 — 2026-08-05

Status: review and test-only evidence. No renderer, schema, application route,
runtime, remote, or persistence behavior is authorized by this report.

## Scope

This round covers the conditional-rule presentation added to the stdout-only
`scripts/render_schema_docs_readonly.py` in NIGHT-BATCH-22 package 4. The
reviewed path is `_conditional_rule_lines`, `_condition_terms`, and `_literal`.
The output is a local documentation view of a schema; it is not validation,
execution, synchronization, or an authorization decision.

## Contract-visible output

The renderer may display relative schema source names, property names, `const`
values, and `enum` values because those are the schema's public contract. For
the current remote projection schema this produces the status/phase conditional
rules. The renderer does not claim to render every JSON Schema keyword or to
recompute a projection's validity.

## Reverse checks

`tests/test_error_surface_round7.py` now supplies a conditional schema whose
`$comment`, `examples`, and `default` contain a secret marker. The test asserts
that the visible conditional rule is present while those hidden metadata values,
filesystem-path markers, and environment-like text are absent. Existing
composite-branch and malformed-root checks remain in place. The established 14
expected xfails are not changed.

## Findings

| ID | Severity | Result | Evidence |
|---|---|---|---|
| ESR8-01 | — | Pass | Conditional output is limited to public field names and literal contract values; hidden metadata is not traversed. |
| ESR8-02 | P3 | Local-only boundary | The renderer accepts a caller-provided relative source label and prints it as documentation context. It remains a stdout-only local tool and is not wired to a remote/dashboard surface. |

No finding authorizes redaction changes, schema changes, runtime wiring, or a
new route. A future renderer feature must add a focused reverse test before it
can claim a broader output-safety boundary.
