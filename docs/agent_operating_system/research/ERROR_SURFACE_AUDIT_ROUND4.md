# Error Surface Audit, Round 4 — 2026-07-29

Status: **REVIEW AND BASELINE TESTS ONLY — NOTHING FIXED OR AUTHORIZED**

## Scope and method

This round extends the error-surface inventory to test helper functions and
fixture-loading paths. It does not treat pytest output as a product API, but it
does treat copied CI/test reports as a possible disclosure surface.

The audit:

1. parsed every `tests/test_*.py` helper that combines `Path.read_text` and
   `json.loads` and checked that the helper has no direct print/log call;
2. loaded a synthetic marker-bearing fixture successfully and captured
   stdout/stderr;
3. ran an isolated, captured pytest probe for a malformed fixture value and a
   marker-bearing missing filename; and
4. kept the existing E-01/E-02 and ES3 `xfail` inventory unchanged.

The synthetic markers were written only inside pytest `tmp_path`. The parent
test captures the failing child report and does not print it.

## Findings

### ES4-01 — P2 — pytest assertion rewriting can echo malformed fixture values

Many test fixture helpers load JSON and then use a rewritten assertion such as
`assert isinstance(value, dict)`. If a malformed fixture root contains a secret
marker, the failing pytest report includes the represented value. The new
captured subprocess probe demonstrates this current behavior without adding an
`xfail` or exposing the captured child report in an ordinary passing run.

This is a test-report exposure, not a runtime product leak. Secret-bearing or
production-derived fixtures must not be introduced, and raw CI output must not
be promoted to a public artifact before a separate report-redaction policy.

### ES4-02 — P3 — missing-fixture exceptions include the requested path

The fixture helpers normally allow `FileNotFoundError` to reach pytest. A
marker-bearing missing filename therefore appears in the local test report,
along with an environment-dependent fixture path. The captured probe locks this
fact as an explicit baseline. It does not weaken or change any loader.

Repository fixture names are closed and synthetic today, so this is not a
current secret source. Future parameterized loaders must not accept untrusted
filenames, and externally shared reports require path redaction.

### ES4-03 — no direct fixture-helper output call found

The static guard found at least twenty JSON fixture-loader helpers and no
direct `print` or logging call inside them. A successful marker-bearing load
also produced no captured stdout/stderr. This narrows the known surface to
failure-report rendering rather than ordinary fixture loading.

## Baseline and boundary

- E-01/E-02 remain unresolved exactly as previously recorded.
- The ten schema-redaction and four ES3 read-only-tool `xfail` cases are neither
  removed nor widened by this package.
- No fixture, builder, validator, script, route, or product module changed.
- A passing baseline test is evidence of known behavior; it is not permission
  to place real secrets in fixtures or publish raw reports.

Any remediation must be separately scoped. This review does not authorize
custom pytest reporters, global exception rewriting, fixture schema changes,
or output persistence.
