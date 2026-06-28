# Hermes × OpenClaw Adapter — Auto-Approval Expected-Stale Readiness Update (v0.7.2-B2)

> **Status: REGRESSION / POLICY UPDATE ONLY.** This version updates the
> current-state aggregator to record v0.7.2-A as expected-stale and to add the
> v0.7.2-B helper readiness + test as new green gates. It adds no feature, wires
> nothing, and creates no tag.

---

## 1. Purpose

After v0.7.2-B landed the auto-approval pure helper, the v0.7.2-A plan-only
readiness turned red (it asserted the helper must not exist). v0.7.2-B2 records
this as an expected-stale historical snapshot and brings the v0.7.2-B green gates
into the current-state aggregator, so the single regression entry point reflects
current health correctly.

## 2. Context

- v0.7.2-A readiness is expected-stale after v0.7.2-B.
- The only stale reason is app/auto_approval_policy_v0_7.py now exists.
- This mirrors the v0.7.1 A/C/C2/D dynamic, already governed by the v0.7.1-G
  stale-readiness policy.

## 3. Why v0.7.2-A Readiness Became Stale

v0.7.2-A was plan-only and asserted "app/auto_approval_policy_v0_7.py does not
exist". v0.7.2-B intentionally created that helper. The negative assertion
therefore flips red by design; it is a version-timing artifact, not a defect.

## 4. Expected-Stale Classification

The current-state aggregator's `EXPECTED_STALE_READINESS` now includes:

```text
"v0.7.2-A": "superseded by v0.7.2-B auto_approval_policy_v0_7.py pure helper"
```

The aggregator never runs v0.7.2-A as a hard gate; it only prints the allowlist.

## 5. Relationship To v0.7.2-A

v0.7.2-A readiness remains a historical snapshot and must not be rewritten. It is
preserved unchanged as the version-time record of the plan-only boundary.

## 6. Relationship To v0.7.2-B

v0.7.2-B helper readiness and test are now current green gates. They are executed
by the aggregator (subprocess, EXIT=0) and represent the landed helper's health.

## 7. Current-State Aggregator Update

`scripts/check_hermes_openclaw_v0_7_1_current_state.py` is updated to:

- add `v0.7.2-A` to `EXPECTED_STALE_READINESS`;
- add the v0.7.2-B helper readiness and test to the green gates;
- add `app/auto_approval_policy_v0_7.py` to required modules;
- assert positive current-state truths and the unwired boundary for the helper.

## 8. New Green Gates

```text
scripts/check_hermes_openclaw_auto_approval_policy_helper_v0_7_2_b.py
scripts/test_auto_approval_policy_v0_7_2_b.py
```

## 9. Positive Current-State Assertions

The aggregator now asserts:

```text
app/auto_approval_policy_v0_7.py exists
helper exports evaluate_auto_approval
helper contains can_execute false behavior
helper contains queue_transition_allowed false behavior
helper contains observation_only true behavior
helper does not import app.main / queue_store / worker / result_sink
helper does not contain route/webhook/QueueStore/run_openclaw_cli/google/gspread/sqlite3/requests/subprocess
app/main.py does not import auto_approval_policy_v0_7
queue_store.py does not import auto_approval_policy_v0_7
worker.py does not import auto_approval_policy_v0_7
result_sink.py does not import auto_approval_policy_v0_7
```

## 10. Historical Snapshot Policy

current-state aggregator is the source of truth for current health. Plan-only
readiness scripts (A/C/C2/D and now v0.7.2-A) are preserved as version-time audit
snapshots and are not required to be green.

## 11. Why Not Modify v0.7.2-A Readiness

B2 does not modify A readiness. Rewriting a plan-only snapshot would destroy its
audit value and violate the established stale-readiness policy. It stays red
by-design and is explicitly allowlisted instead.

## 12. Why Not Modify v0.7.2-B Readiness

B2 does not modify B readiness. The v0.7.2-B helper readiness is already correct
and green; B2 only references it as a green gate, it does not change it.

## 13. Safety Boundary

B2 does not add features. B2 does not modify auto_approval_policy_v0_7.py. It only
updates the aggregator and adds this doc + a B2 readiness check.

## 14. No Route Wiring

B2 does not wire routes. No new route, POST handler, or webhook is added.

## 15. No QueueStore Mutation

B2 does not wire QueueStore. No queued task is created and no state machine is
changed.

## 16. No Worker Execution

B2 does not start Worker. The helper remains observation-only with can_execute
always false.

## 17. No OpenClaw / Hermes Calls

B2 does not call OpenClaw. B2 does not call Hermes. No live client is added.

## 18. No Google Sheets Live Write

B2 does not write Google Sheets. B2 does not set `GOOGLE_SHEETS_ENABLED` true.

## 19. No Secrets Access

B2 does not read secrets. Sensitive checks use regex / format matching only; no
`.env`, credentials, or token file is read.

## 20. No v0.7 Tag

B2 does not create tag. No v0.7 tag exists.

## 21. Future Maintenance Rule

When a future plan-only version is later implemented, update the aggregator's
positive assertions and add the now-superseded plan-only readiness to
`EXPECTED_STALE_READINESS`; never rewrite the historical plan-only readiness, and
never require it to be green in current-state regression.

## 22. Final Recommendation

Adopt the updated aggregator as the single current-state regression gate covering
v0.7.1 through v0.7.2-B, with v0.7.2-A classified expected-stale. Keep the
v0.7.2-A readiness unchanged as a historical snapshot. Do not create a v0.7 tag.
