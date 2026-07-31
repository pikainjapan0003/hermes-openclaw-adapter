# Blackboard Board Reader Stress Measurement — 2026-07-27

Status: measurement only; not a service-level objective, capacity promise, or
authorization for a persistent board.

## Scope

`tests/test_board_reader_stress.py` creates 200 independent synthetic N=1 boards
under pytest's temporary directory. Each board contains one valid fixture for each
of the ten registered Blackboard message types, for 2,000 JSON files total. It then
calls `read_blackboard_board` once per board.

The probe performs no network access and writes only test data under `tmp_path`. It
does not create the proposed formal `data/` layout, start a worker, claim a task,
dispatch work, or exercise any execution path.

## Observed result

Environment: WSL, CPython virtual environment, repository branch
`night-batch-15`.

```text
board_reader_stress boards=200 files=2000 runtime_seconds=26.959988 peak_bytes=10267463
1 passed in 32.00s
```

The measured reader phase completed successfully for every board and validated all
2,000 messages. Python `tracemalloc` reported a peak of 10,267,463 bytes during the
reader phase. Fixture creation time is outside the printed reader runtime but inside
pytest's total duration.

## Interpretation and limits

- This is one local observation, not a stable benchmark.
- Filesystem, CPU, Python, antivirus, and JSON Schema cache behavior can materially
  change the result.
- The test deliberately has no runtime or memory pass/fail threshold. Its assertions
  cover correctness and that measurement occurred.
- Repeated CI timing would be needed before proposing any regression threshold.
- The design remains N=1 and read-only. Running 200 synthetic boards in a test does
  not authorize multi-board runtime orchestration or persistence.

## T3 conclusion

No T3 expansion is justified by this measurement. The probe demonstrates only that
the current read-only implementation can process this finite synthetic sample. It
does not establish multi-worker safety, concurrent access, retention, locking,
remote transport, or a production capacity target.
