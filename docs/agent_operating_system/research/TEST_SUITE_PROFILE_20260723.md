# Test Suite Layer Profile — 2026-07-23

Status: measured in NIGHT-BATCH-11 package 9.

The four markers are assigned at collection time from the test source filename.
This changes neither test bodies nor assertions. Every collected test receives
exactly one of `contract`, `governance`, `legacy`, or `fuzz`.

| Layer | Selection command | Cases | Runtime |
|---|---|---:|---:|
| contract | `python -m pytest -m contract -q` | 287 | 32.52 s |
| governance | `python -m pytest -m governance -q` | 47 | 22.49 s |
| legacy | `python -m pytest -m legacy -q` | 233 | 13.61 s |
| fuzz | `python -m pytest -m fuzz -q` | 271 | 23.90 s |

The layer names are organizational only. They do not relax the default
warning-as-error setting, safety guards, or full-suite acceptance requirement.
The four counts sum to the 838-test collection at this package boundary, which
also confirms that each test received exactly one layer.
