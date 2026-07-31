# Test Suite Layer Profile — 2026-07-23

Status: updated by NIGHT-BATCH-13 package 11.

An explicit layer marker on a test file takes precedence; otherwise the
collection hook assigns a layer from the source filename. This changes neither
test bodies nor assertions. A collection-time assignment map and
`tests/test_test_layer_markers.py` now mechanically require every collected
test to belong to exactly one of `contract`, `governance`, `legacy`, or `fuzz`.

| Layer | Selection command | Collected outcomes | Runtime |
|---|---|---:|---:|
| contract | `python -m pytest -m contract -q` | 333 (`323 passed, 10 xfailed`) | 55.08 s |
| governance | `python -m pytest -m governance -q` | 52 | 28.20 s |
| legacy | `python -m pytest -m legacy -q` | 269 | 21.22 s |
| fuzz | `python -m pytest -m fuzz -q` | 271 | 28.54 s |

The layer names are organizational only. They do not relax the default
warning-as-error setting, safety guards, or full-suite acceptance requirement.
The four counts sum exactly to the 925-test collection at this package
boundary. The full-suite measurement was `915 passed, 10 xfailed in 99.47s`;
the ten expected failures are the named schema-error redaction baseline, not a
layering exemption.
