# Managed coverage residual — final disposition

Date: 2026-08-04

Status: measurement/explanation only. No product code was changed for coverage.

## Residual

The accepted NIGHT-BATCH-20 managed-scope measurement has zero missing statements and one partial branch. The sole arc is the false branch from `app/full_loop_preview_adapter.py:268` to `:271` inside `_validate_timeline`.

## Reachability proof

Let `R` be the complete ordered tuple `REQUIRED_TIMELINE_STEP_IDS` and `F` be `found_step_ids`.

The outer condition at line 267 enters the inner condition only when both:

1. `F != prefix(R, len(F))`; and
2. `missing_required_steps` is empty, meaning every member of `R` occurs in `F`.

The inner false arc would additionally require `F == R`. But if `F == R`, then `F == prefix(R, len(F))`, contradicting outer condition 1. Therefore execution cannot enter line 268 and then take its false branch to line 271. Reordering, duplication, or extra identifiers can enter the inner check, but each necessarily makes `F != R` and takes the already-covered true branch that records the deterministic-order violation.

## Decision

Retain the nested check as defence in depth. It is redundant under the present outer predicate but harmless if surrounding validation is later refactored. Deleting or algebraically weakening it solely to report 100% branch coverage would reduce defensive clarity without exercising new behavior.

The managed closeout therefore remains: all statements covered, one proven-unreachable partial branch retained, rounded report 99%. Any future change that makes this arc reachable must add a behavior test rather than silently delete the check.
