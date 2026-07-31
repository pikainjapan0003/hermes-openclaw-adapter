# Error Surface Audit, Round 2 — 2026-07-27

Status: review and regression tests complete; findings are advisory and do not
authorize product changes.

## Scope and boundary

This round extends the earlier six-module contract audit to every remaining
pure/helper-style module under `app/`. It excludes `app/main.py`, `app/worker.py`,
and `app/google_sheets_oauth_writer.py` as directed. Stateful storage and file
boundary modules (`blackboard_board_reader`, `blackboard_store`,
`blackboard_validators`, `health_store`, `queue_intake_bridge_v0_7`,
`queue_store`, and `result_sink`) were inventoried but are not represented as
pure functions in the conclusions below.

The reviewed pure/helper modules were:

- approval decision recorder/view, approval security gate, audit display, and
  auto-approval policy;
- approval packet, evidence bundle, hash chain, remote projection, and rollback
  builders already covered by Round 1;
- legacy contract validator, dashboard intake view, demo cleanup preview, and
  full-loop preview;
- Hermes readback, strategy suggestion, mock generator, mock adapter, mock E2E,
  and mock OpenClaw gateway;
- queue annotation, security gates, and worker mock-gateway dry-run helpers;
- result feedback preview.

The review inspected explicit raises, caught-exception interpolation, rejection
records, and validation-result construction. It searched for paths where
caller-controlled values, fixture paths, environment values, or secret-like
strings could enter an error or rejection surface.

## Regression evidence

`tests/test_noncontract_error_surface_no_leak.py` supplies
`FAKE-SECRET-20260727` and `C:\Users\Owner\private\payload.txt` to rejected
inputs for:

- the frozen v0.7 contract type guard;
- the mock adapter metadata guard;
- the dashboard intake type guard;
- the mock OpenClaw rejection record;
- the Hermes strategy rejection record;
- the Hermes result-readback rejection record.

All six cases prove that those selected rejection paths omit both markers.
Together with `tests/test_error_surface_no_leak.py`, the focused run completed:

```text
11 passed in 6.30s
```

The E-01/E-02 xfail baselines were not edited, widened, removed, or converted to
passes.

## Findings

### ES2-01 — P2 — legacy enum validation echoes the rejected value

`app/contracts_v0_7.py` builds some enum errors with the actual invalid value.
A hostile `status` such as `FAKE-SECRET-20260727` therefore appears in
`ContractValidationError`. The new passing regression deliberately targets the
separate type-error path; it must not be interpreted as proving every legacy
validator branch payload-free.

The module is a frozen local compatibility contract, so this is not an active
remote leak. Any future display or transport of its raw error text must first
add a redaction decision and regression coverage.

### ES2-02 — P3 — frozen mock E2E errors interpolate identifiers and status

`app/mock_e2e_v0_7.py` interpolates the requested `task_id` when a record is not
found and interpolates an unexpected initial status. Those are caller-derived
values. The helper is frozen, synthetic, and in-memory, which limits current
exposure, but a future UI must not forward these exception strings as trusted
redacted messages.

### ES2-03 — P3 — preview loaders stringify local fixture-read exceptions

`app/full_loop_preview_adapter.py` and `app/result_feedback_preview.py` include
the caught exception in a rejected view when a fixed repository fixture cannot
be loaded. An OS error can contain the local fixture path. The path is not
caller-selected and neither helper is remotely wired, so the present risk is
local diagnostic disclosure rather than secret exfiltration.

## Known Round 1 findings retained

- E-01: raw `jsonschema` messages in the Blackboard validator can quote an
  invalid instance or unexpected property.
- E-02: the remote projection validator has the same generic-schema-message
  risk despite its separate projection leak guard.

Both remain P2, offline, and unresolved. Their existing xfail baseline remains
the source of truth; this package does not claim or implement a fix.

## No-action conclusion

No product code was changed. The passing marker tests establish only the named
branches. ES2-01 through ES2-03 and E-01/E-02 must remain visible to future
reviewers and must not be rephrased as resolved merely because the current
system has no runtime or remote error exposure.
