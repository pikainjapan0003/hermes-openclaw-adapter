# Error Surface Audit — Round 7

Date: 2026-08-04

Status: review plus test-only evidence. No renderer, inventory, schema, runtime, route, or remote-output behavior is changed or authorized.

## Scope

This round reviews the renderer's `oneOf`/`anyOf`/`allOf` paths and the closed artifact inventory's exceptional output. The renderer is an intentional local stdout tool; field names, declared descriptions, const/enum values, constraints, and relative source names are public by contract. The artifact inventory is pytest-only and is not an application error surface.

## Findings

| ID | Severity | Result | Evidence |
|---|---|---|---|
| ESR7-01 | — | Pass | Composite renderer branches expose derived type labels (`string | null`, `string & number`) but omit hidden `$comment`, `examples`, and `default` payloads. Malformed non-object roots raise a fixed reason plus path, not raw JSON content. |
| ESR7-02 | P2 | Open/local-only | Artifact inventory errors can include the filesystem path supplied to `Path.read_bytes()`. More importantly, pytest assertion rewriting of the bare-CR check includes the failing bytes expression, so raw artifact bytes can appear in a failed-test report. This helper must remain local and must not be wired to a dashboard, remote report, or untrusted exposure. |
| ESR7-03 | P3 | Corrected specification drift | `docs/schemas/remote_readonly_projection.schema.json:124` already uses root-level `allOf` as an `if`/`then` conditional rule. The renderer's current type-composition label is only a display convention and does not render that root conditional; package 4 is the explicitly scoped stdout-only change for presenting it. Package 3 records this fact and does not alter renderer logic. |

## Reverse-test evidence

`tests/test_error_surface_round7.py` proves hidden composite metadata and malformed renderer payloads are not echoed. It also detects—without adding an xfail—the inventory's absolute-path and bare-CR raw-bytes exposures. The tests name both known exposures explicitly so a future refactor cannot silently broaden them or falsely claim the inventory failure surface is payload-free.

The established 14 expected xfails are unchanged. This audit neither removes nor adds a redaction xfail and does not claim that intended local labels are secret-safe.
