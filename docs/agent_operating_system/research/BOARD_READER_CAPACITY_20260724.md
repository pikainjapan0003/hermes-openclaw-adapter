# Blackboard Board Reader Capacity Probe — 2026-07-24

Status: informational test report; no performance gate and no upgrade
authorization.

## Scope

The current contract is N=1 and allows at most one message for each of the ten
Blackboard message types in a board directory. The probe therefore created 50
legal boards × 10 messages rather than weakening the duplicate-message-type
guard to place 500 entries in one invalid board.

All files existed only under pytest `tmp_path`. The measured interval starts
after fixture creation and covers 50 calls to
`read_blackboard_board`, retaining all returned results so peak memory includes
the complete 500-message result set.

## Observed result

Environment: WSL, Python 3.12.3, repository on `/mnt/c`, isolated NB-12 virtual
environment.

```text
board_reader_capacity boards=50 messages=500 runtime_seconds=8.383018 peak_bytes=2822743
1 passed in 10.41s
```

- Reader-only wall time: 8.383018 seconds.
- `tracemalloc` peak: 2,822,743 bytes (about 2.69 MiB).
- Validated messages: 500/500.
- Validated boards: 50/50.

These are observations from one run, not a benchmark, SLO, regression
threshold, or capacity claim. Filesystem mount overhead and retained Python
objects materially affect the numbers.

## Expected multi-worker bottlenecks

1. Directory enumeration and per-file `read_text` are serial; latency grows
   with file count and filesystem characteristics.
2. Every entry is decoded and validated independently, so JSON decoding and
   JSON Schema validation repeat for each message.
3. The reader retains validated message dictionaries in the returned result;
   callers retaining many board results increase memory roughly with payload
   volume.
4. The N=1 uniqueness checks are in-process snapshots. They do not provide a
   transaction, lock, or consistent read if multiple writers mutate a board.
5. Filename ordering is deterministic but does not solve simultaneous-writer
   conflicts, partial replacement, or cross-file atomicity.

## Governance boundary

The authoritative re-review trigger is
`05_VERIFIED_LONG_TERM_PLAN.md` §6.11 T3: frequent conflicts from concurrent
multi-worker writes require the Owner to revisit Q13 and decide whether to move
to SQLite. This probe does not claim T3 has occurred, does not recommend an
upgrade, and does not authorize multi-worker behavior or any write path.

