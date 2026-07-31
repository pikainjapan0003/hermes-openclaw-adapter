# Blackboard Board Reader Capacity Trend — 2026-07-26

Status: **MEASUREMENT ONLY**. No CI threshold, storage change, concurrency
mechanism, or write path is authorized.

## Method

The unchanged `tests/test_board_reader_capacity.py` probe created 50 legal
temporary boards with ten Blackboard message types each, then retained the
results of 50 `read_blackboard_board` calls. All 500 files existed only under
pytest `tmp_path`.

Environment: WSL Python 3.12.3, pytest 9.1.1, existing isolated venv
`/tmp/hermes-nb12-venv`, repository mounted at `/mnt/c`.

Command:

```text
python -m pytest -p no:cacheprovider -q -s tests/test_board_reader_capacity.py
```

## Current output

```text
board_reader_capacity boards=50 messages=500 runtime_seconds=9.868599 peak_bytes=2814492
.
1 passed in 11.99s
```

## Trend

| Measure | 2026-07-24 baseline | 2026-07-26 run | Change |
|---|---:|---:|---:|
| Legal boards | 50 | 50 | 0 |
| Validated messages | 500 | 500 | 0 |
| Reader-only runtime | 8.383018 s | 9.868599 s | +1.485581 s (+17.72%) |
| `tracemalloc` peak | 2,822,743 bytes | 2,814,492 bytes | -8,251 bytes (-0.29%) |
| Pytest wall time | 10.41 s | 11.99 s | +1.58 s (+15.18%) |

One mounted-filesystem run is too noisy to establish a performance regression.
The near-flat measured peak and unchanged valid outcome provide no evidence of
a capacity boundary. Runtime remains an observation only.

## Governance boundary

The sole storage re-review trigger remains
`05_VERIFIED_LONG_TERM_PLAN.md` §6.11 T3: frequent conflicts from concurrent
multi-worker writes. This read-only 50-board probe does not trigger T3, create a
CI performance gate, justify a media upgrade, or authorize multi-worker
behavior. It also does not establish that future larger boards are safe.
