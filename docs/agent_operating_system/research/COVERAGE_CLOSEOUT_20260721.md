# Coverage Closeout — 2026-07-21

## Scope and method

This report records NIGHT-BATCH-8 package 11.  It measures branch coverage for
all Python modules under `app/`, excluding exactly the three files named by the
package specification:

- `app/main.py`
- `app/worker.py`
- `app/google_sheets_oauth_writer.py`

The BEFORE measurement used the package-10 HOLD worktree at commit `78e7ce2`
with the package-11 tests absent.  The AFTER measurement used the same product
code plus the package-11 tests.  Both runs used Python 3.12.3, `pytest-cov`,
branch coverage, and an external coverage data file under `/tmp`; no coverage
database was written into the repository.

No product module was modified.  The frozen `app/mock_e2e_v0_7.py` was covered
only through behavior-locking tests.  Any SQLite or JSONL write exercised by the
tests was confined to pytest `tmp_path`.

## Raw summaries

BEFORE:

```text
591 passed in 68.55s
TOTAL (specified exclusions applied): 2583 statements, 546 missed,
1056 branches, 130 partial branches, 78% coverage
```

AFTER:

```text
662 passed in 63.17s (0:01:03)
TOTAL (specified exclusions applied): 2583 statements, 27 missed,
1056 branches, 38 partial branches, 98% coverage
```

## Per-module branch coverage

| Module | BEFORE | AFTER | Result |
|---|---:|---:|---|
| `app/__init__.py` | 100% | 100% | pass |
| `app/approval_decision_event_recorder_v0_7.py` | 78% | 100% | pass |
| `app/approval_decision_events_v0_7.py` | 49% | 100% | pass |
| `app/approval_packet_builder.py` | 100% | 100% | pass |
| `app/approval_security_gate_v0_7.py` | 100% | 100% | pass |
| `app/audit_trail_display_v0_7.py` | 69% | 100% | pass |
| `app/auto_approval_policy_v0_7.py` | 98% | 98% | pass |
| `app/blackboard_board_reader.py` | 76% | 97% | pass |
| `app/blackboard_store.py` | 80% | 80% | pass |
| `app/blackboard_validators.py` | 100% | 100% | pass |
| `app/contracts_v0_7.py` | 95% | 95% | pass |
| `app/dashboard_intake_view_v0_7.py` | 64% | 97% | pass |
| `app/demo_task_cleanup_v0_7.py` | 100% | 100% | pass |
| `app/evidence_bundle_builder.py` | 100% | 100% | pass |
| `app/full_loop_preview_adapter.py` | 99% | 99% | pass |
| `app/hash_chain.py` | 100% | 100% | pass |
| `app/health_store.py` | 43% | 99% | pass |
| `app/hermes_result_readback_mock.py` | 100% | 100% | pass |
| `app/hermes_strategy_suggestion_model.py` | 48% | 100% | pass |
| `app/mock_adapter_v0_7.py` | 100% | 100% | pass |
| `app/mock_e2e_v0_7.py` | 0% | 99% | pass; frozen behavior only |
| `app/mock_hermes_generator.py` | 53% | 100% | pass |
| `app/mock_openclaw_gateway.py` | 73% | 100% | pass |
| `app/queue_intake_bridge_v0_7.py` | 0% | 99% | pass |
| `app/queue_store.py` | 70% | 99% | pass |
| `app/queue_task_annotation_v0_7.py` | 69% | 97% | pass |
| `app/remote_readonly_projection.py` | 98% | 98% | pass |
| `app/result_feedback_preview.py` | 100% | 100% | pass |
| `app/result_sink.py` | 0% | 100% | pass; mock sink writes only to `tmp_path` |
| `app/rollback_preview_builder.py` | 98% | 98% | pass |
| `app/security_gates_v0_7.py` | 78% | 100% | pass |
| `app/worker_mock_gateway_dry_run.py` | 74% | 97% | pass |

## Threshold and exclusions

All in-scope modules meet the required branch-coverage threshold of at least
80%.  There are no below-threshold exemptions.

The three files excluded above are specification-level exclusions, not
after-the-fact exemptions.  In particular,
`app/google_sheets_oauth_writer.py` was neither imported for coverage nor
modified, because it is a real-write-capable module forbidden by the batch.

## Residual branches

Remaining uncovered or partial branches are defensive paths in modules already
above threshold.  No production branch was deleted or weakened to increase the
percentage.  The closeout tests assert fail-closed behavior, forced safety
flags, read-only projections, copy-on-write normalization, and frozen mock E2E
behavior; they do not create an execution or dispatch path.
