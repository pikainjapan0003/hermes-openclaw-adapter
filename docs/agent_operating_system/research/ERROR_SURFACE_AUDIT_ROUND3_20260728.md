# Error Surface Audit, Round 3 — 2026-07-28

Status: **REVIEW AND BASELINE TESTS ONLY — NOTHING FIXED OR AUTHORIZED**

## Scope

This round extends error/output-surface review to the four read-only tools in
`scripts/`:

- `check_three_source_readonly.py`;
- `check_mirror_drift_readonly.py`;
- `inspect_blackboard_readonly.py`; and
- `render_schema_docs_readonly.py`.

The review injected `FAKE-SECRET-NB16-SCRIPT-SURFACE` into a caught diagnostic,
a relative filename, a board-error filename, and schema-owned display text.
`tests/test_readonly_script_error_surface_no_leak.py` records each current echo
as an exact `xfail` baseline and separately asserts that the echo inventory is
exactly these four tools. A newly clean surface becomes an ordinary pass; a new
tool or changed inventory makes the guard fail rather than silently widening.

## Findings

### ES3-01 — P2 — three-source diagnostics echo raw failure detail

`check_three_source_readonly.py` includes caught Git, HTTP, URL, OS, and timeout
exception text in `SourceState.detail`, then prints it in text and JSON reports.
Those strings may contain a remote URL, local path, command detail, or
environment-dependent error content. The tool is local and read-only, but its
output must not be published remotely until a payload-free diagnostic mapping
exists.

### ES3-02 — P3 — mirror report prints caller-controlled relative paths

`check_mirror_drift_readonly.py` intentionally reports every relative path.
A secret-like marker placed in a filename is therefore printed. This is useful
for local drift diagnosis and does not read file content into the report, but
the path list is not a redacted export surface.

### ES3-03 — P2 — board inspector preserves filenames and identifiers

`inspect_blackboard_readonly.py` removes message payload text but emits board
filenames and selected `*_id` values. A hostile invalid filename or identifier
can therefore reach stdout. The output is local-only today; it is not safe for
a future remote/dashboard boundary without a separate redaction contract.

### ES3-04 — P3 — schema renderer prints schema-owned strings verbatim

`render_schema_docs_readonly.py` emits schema titles, source names, property
names, patterns, enums, consts, and descriptions. These values are useful for
trusted repository documentation, but a caller-selected schema tree can place
a marker in the generated Markdown. The output is not a public sanitization
boundary.

## Boundary and disposition

All four findings are offline/local and no current route imports these tools as
an export API. This limits present impact but does not make their output
redacted. No product or script code changed, and the package does not alter the
existing E-01/E-02 schema-redaction baselines.

Before any output is copied into a dashboard, remote projection, log sink, or
persistent artifact, an Owner-selected redaction design and ordinary passing
marker tests are required. An `xfail` is evidence of an unresolved gap, never
permission to expose the text.
