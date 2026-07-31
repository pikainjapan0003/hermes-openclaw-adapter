# Structured Error Surface Audit — 2026-07-23

Status: completed review; findings remain advisory and do not authorize product changes.

Scope: `approval_packet_builder.py`, `evidence_bundle_builder.py`,
`rollback_preview_builder.py`, `remote_readonly_projection.py`,
`blackboard_validators.py`, and `hash_chain.py`.

## Resolution metadata

| Finding | Status | Resolution |
|---|---|---|
| E-01 | Design prepared; unresolved | NIGHT-BATCH-12 package 1 (`2fdd423`) prepared Options A/B/C and a recommendation. The Owner decision remains blank. `app/blackboard_validators.py` is unchanged. |
| E-02 | Design prepared; unresolved | NIGHT-BATCH-13 package 2 (`9da4f78`) added the remote-projection-specific exposure/masking contract to the same Options A/B/C decision. The Owner decision remains blank. `app/remote_readonly_projection.py` is unchanged. |

The ten-schema xfail baseline records the present E-01 behavior; it is not a
fix. No validator, route, projection, remote surface, or runtime wiring has
been changed or authorized.

## Method

The review enumerated every explicit `raise`, structured `errors` construction,
and exception-to-message conversion in the six modules. It checked whether a
failure can echo caller-controlled raw payloads, absolute paths, environment
values, or secrets. Runtime tests use synthetic markers only and perform no IO.

## Results

| Module | Surface | Result |
|---|---|---|
| approval packet builder | `ApprovalPacketBuildError` | Pass. Messages name fields or closed expected values; they do not interpolate caller values. |
| evidence bundle builder | `EvidenceBundleError` / `SensitiveEvidenceError` | Pass. Sensitive-input errors expose an allowlisted structural location, never the rejected value. |
| rollback preview builder | `RollbackPreviewBuildError` | Pass. Messages name contract fields and expected states, never caller values. |
| remote projection builder | `RemoteReadonlyProjectionError` | Pass for normal builder validation. Messages use field names and closed enum/hash requirements. The final leak guard formats its own path/message records, not raw values. |
| Blackboard validator | structured `errors[].message` | **P2 finding E-01.** `jsonschema.ValidationError.message` can include the invalid instance value or unexpected property name. Selection errors are payload-free, but schema-validation errors are not guaranteed payload-free. Do not expose them to an untrusted remote display without a later redaction contract. |
| hash-chain canonicalizer | `HashChainError` | Pass for payload/path/env leakage. Messages expose only JSON structural locations and Python type names. |
| remote projection validator | structured `errors[].message` | **P2 finding E-02.** Like E-01, raw `jsonschema` messages can quote rejected instance values. The projection-specific leak errors are redacted, but generic schema errors need a later sanitization decision before remote exposure. |

## Mechanical checks

`tests/test_error_surface_no_leak.py` feeds each of the four builders a malformed
input containing both `FAKE-SECRET-20260723` and
`C:\Users\Owner\private\payload.txt`; every raised builder message must omit
both markers. It also checks payload-free selection/canonicalization failures
for the validator and hash-chain modules.

The two P2 findings are not fixed in this review-and-test package because the
package did not authorize product-code changes. Current contract modules remain
offline and are not wired to a remote surface, so this is a future exposure
risk rather than an active secret transmission.
