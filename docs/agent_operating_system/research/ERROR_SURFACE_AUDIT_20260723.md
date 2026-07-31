# Structured Error Surface Audit — 2026-07-23

Status: completed review; findings remain advisory and do not authorize product changes.

Scope: `approval_packet_builder.py`, `evidence_bundle_builder.py`,
`rollback_preview_builder.py`, `remote_readonly_projection.py`,
`blackboard_validators.py`, and `hash_chain.py`.

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
