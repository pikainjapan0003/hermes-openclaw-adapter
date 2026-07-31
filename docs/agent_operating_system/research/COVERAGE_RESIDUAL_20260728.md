# Managed Coverage Residual Closeout — 2026-07-28

Status: **MEASUREMENT-ONLY CLOSEOUT — NO PRODUCT CHANGE**

This report classifies the final managed `app/` branch-coverage residuals. It
does not authorize product-code deletion, refactoring, persistence, execution,
dispatch, runtime wiring, or a change to the three-file coverage exclusion.

## Scope and command

Managed modules are every `app/**/*.py` file except `app/main.py`,
`app/worker.py`, and `app/google_sheets_oauth_writer.py`. The first two remain
separately governed surfaces; the third is an existing real-write capability
that nightly batches must not touch.

The baseline measurement used:

```text
COVERAGE_FILE=<system-temp>/nb16-pkg5-before.coverage \
python -m pytest -p no:cacheprovider --cov=app --cov-branch \
  --cov-report=json:<system-temp>/nb16-pkg5-before.json -q
```

Result: `1214 passed, 10 xfailed`. After excluding exactly the three files
above, the measurement contained 2,591 statements and 1,060 branches. One
statement and two branch arcs were missing:

| Module and location | Residual | Mechanical classification | Disposition |
|---|---|---|---|
| `app/full_loop_preview_adapter.py:267-271` | False arc `268→271` | Unreachable redundant inner guard. Entering line 268 requires `found_step_ids` to differ from the required prefix while no required id is missing. If the ids are reordered, duplicated, or have extras, they necessarily differ from the exact full required list, so line 268 is true. If they equal the full list, the outer condition at line 267 is false and line 268 is never entered. Existing tests already cover the true violation path. | Retain as defence in depth; do not rewrite validation logic for coverage. |
| `app/rollback_preview_builder.py:119-124` | Statement 124 and true arc `123→124` | Unreachable redundant equality guard. Line 119 first requires both mappings to equal the same immutable `_SAFE_N1_FLAGS` mapping. After that check passes, `audit_flags != result_flags` cannot be true. Existing tests cover rejection when either source profile differs. | Retain as defence in depth; do not delete the explicit cross-source check for coverage. |

## Mechanical conclusion

Both residuals are classified and closed. Neither represents an untested
reachable behavior, and neither should be removed merely to produce a rounded
100% report. No additional test can reach either arc without bypassing or
changing the product logic, which this package forbids.

Coverage percentage is not an authorization signal. Test green, validation
success, or a closed residual never permits a write, dispatch, runtime call, or
next-phase start.
