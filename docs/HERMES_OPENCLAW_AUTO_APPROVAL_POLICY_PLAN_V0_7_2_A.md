# Hermes × OpenClaw Adapter — Auto-Approval Policy / Safe Autopilot Plan (v0.7.2-A)

> **Status: PLAN-ONLY.** This version adds a policy document and a static
> readiness check. It implements no auto-approval code, wires nothing, and
> creates no tag.
>
> Boundary declarations for this version:
>
> - v0.7.2-A is plan-only.
> - v0.7.2-A does not implement auto-approval code.
> - v0.7.2-A does not add app/auto_approval_policy_v0_7.py.
> - v0.7.2-A does not modify app/main.py.
> - v0.7.2-A does not modify queue_store.py.
> - v0.7.2-A does not modify worker.py.
> - v0.7.2-A does not modify result_sink.py.
> - v0.7.2-A does not modify approval_security_gate_v0_7.py.
> - v0.7.2-A does not modify security_gates_v0_7.py.
> - v0.7.2-A does not modify queue_intake_bridge_v0_7.py.
> - v0.7.2-A does not modify dashboard_intake_view_v0_7.py.
> - v0.7.2-A does not modify templates or static.
> - v0.7.2-A does not wire intake bridge.
> - v0.7.2-A does not wire approve route.
> - v0.7.2-A does not modify QueueStore state semantics.
> - v0.7.2-A does not start Worker.
> - v0.7.2-A does not call OpenClaw.
> - v0.7.2-A does not call Hermes.
> - v0.7.2-A does not write Google Sheets.
> - v0.7.2-A does not create a v0.7 tag.

---

## 1. Purpose

This document plans a **safe, low-risk auto-approval policy** (Safe Autopilot)
for the adapter: a future capability that lets clearly low-risk tasks proceed
without per-task Owner clicks, **only when every safety gate passes**, while all
medium/high-risk operations still require Owner approval and the most dangerous
operations remain prohibited. This version freezes the policy design only; it
implements nothing.

---

## 2. Relationship To v0.7.1-H

v0.7.1-H (closeout) recorded the Safe Autopilot / Auto-Approval direction as a
future, plan-only, default-off option (section 29: "v0.7.2-A: Auto-Approval
Policy Plan / Safe Autopilot Mode"). v0.7.2-A is the dedicated policy plan that
expands that direction into a concrete, reviewable specification — still
plan-only and still implementing nothing.

---

## 3. Why This Version Is Plan-only

Auto-approval touches the most sensitive decision in the system: whether a task
may proceed without an explicit Owner click. Getting the policy, the risk
layering, the allowlists, and the fail-closed semantics right **on paper and
under Owner review** must precede any code. Therefore v0.7.2-A is plan-only:
policy doc + static readiness only, no helper, no wiring.

---

## 4. Auto-Approval Is Not Skip-Permissions

This is the central safety ruling of this version:

- Auto-approval does not mean auto-execute everything.
- No dangerous skip-permissions mode is approved.
- No --dangerously-skip-permissions equivalent is approved.
- AUTO_APPROVAL_MODE must only support off | safe.
- dangerous, unrestricted, skip_permissions, and bypass modes are not allowed.
- Safe autopilot must be default-off.
- Low-risk tasks may be auto-approved only when all safety gates pass.
- High-risk tasks must still require Owner approval.
- Push / tag / secrets / production DB / Worker start / OpenClaw / Hermes /
  Google Sheets live write must never be auto-approved.

---

## 5. Design Principles

- Control before automation; fail-closed by default.
- Reuse the existing, proven gates rather than inventing new ones.
- Default-off everywhere; enabling is an explicit, reversible operation.
- Kill switch overrides everything; denylist overrides allowlist.
- Every decision is auditable; in this plan and the first helper, decisions are
  observation-only.
- QueueStore remains the source of truth for task state.

---

## 6. Existing Reusable Gates

These already exist and are intended for reuse by a future helper (not modified
here):

- `app/security_gates_v0_7.py`: `evaluate_kill_switch`, `evaluate_tool_allowlist`,
  `evaluate_security_gates` (kill switch > denylist > allowlist; empty
  allowed/requested → fail-closed), `build_audit_event` (accepts `risk_level`),
  `redact_audit_metadata`.
- `app/approval_security_gate_v0_7.py`: `evaluate_approval_to_queued`,
  `extract_payload` / `extract_metadata` / `extract_requested_tools`,
  `build_approval_audit_event`, `REVIEW_STATUSES`.
- `app/main.py` v0.5.4 risk skeleton: `parse_safety_level`, `needs_human_review`,
  constants `MAX_AUTO_SAFETY_LEVEL` (1) and `REVIEW_SAFETY_LEVEL` (3).
- `app/dashboard_intake_view_v0_7.py`: read-only derivation of `risk_level`,
  `approval_status`, `source_mode`, `executable_by_worker`.

---

## 7. Existing Reusable Metadata

- `safety_level` (integer risk; `MAX_AUTO_SAFETY_LEVEL=1`, `REVIEW_SAFETY_LEVEL=3`)
- `requires_confirmation` (boolean force-review)
- `task_type`
- `requested_tools` (source fixed at `payload.metadata.requested_tools`)
- `allowed_tools` / `denied_tools` (in payload)
- `executable_by_worker`, `local_only`, `mock`

---

## 8. Existing Reusable Flags

- `GLOBAL_KILL_SWITCH`
- `QUEUE_INTAKE_ENABLED`
- `INTAKE_SECURITY_GATES_ENABLED`
- `APPROVAL_SECURITY_GATES_ENABLED`
- `APPROVAL_KILL_SWITCH`

All default-off, following a consistent pattern that the new flags will mirror.

---

## 9. Proposed Env Flags

Proposed for a future helper (not implemented here):

```text
AUTO_APPROVAL_MODE=off | safe
SAFE_AUTOPILOT_ENABLED=false
LOW_RISK_AUTO_APPROVAL_ENABLED=false
AUTO_APPROVAL_POLICY=safe
AUTO_APPROVAL_KILL_SWITCH=false
```

Rules:

- all flags default off
- AUTO_APPROVAL_MODE only supports off | safe
- unknown mode must fail closed / fallback to Owner approval

---

## 10. AUTO_APPROVAL_MODE Behavior

- `off` (default): no auto-approval; every task follows the existing
  Owner-approval path.
- `safe`: low-risk tasks may be auto-approved only when all safety gates pass;
  everything else falls back to Owner approval or is rejected/prohibited.
- Any other value (dangerous / unrestricted / skip_permissions / bypass / unknown)
  must fail closed / fallback to Owner approval and must never enable execution.

---

## 11. SAFE_AUTOPILOT_ENABLED Behavior

- Default false. When false, no auto-approval decision is ever applied.
- When true (future), it only permits the `safe` policy under all gates; it never
  implies execution and never overrides the kill switch.

---

## 12. LOW_RISK_AUTO_APPROVAL_ENABLED Behavior

- Default false. Gates the Level 0 / Level 1 auto-allow behavior specifically.
- When false, even low-risk tasks require Owner approval. When true (future),
  low-risk tasks may be auto-approved only if every higher-priority gate passes.

---

## 13. Level 0 Policy

Level 0:

- auto-allowed read-only / report / test / compile operations
- no file writes
- no external side effects

## 14. Level 1 Policy

Level 1:

- auto-allowed but audited local-only docs / mock / pure helper work
- must be local-only
- must not touch protected files
- must not create queued tasks
- must not execute Worker

## 15. Level 2 Policy

Level 2 (Owner approval required):

- protected files
- app/main.py
- queue_store.py
- worker.py
- approval route
- commits
- state machine changes

## 16. Level 3 Policy

Level 3 (prohibited or strong approval required):

- push
- tag
- secrets
- production DB
- Worker start
- OpenClaw
- Hermes live client
- Google Sheets live write
- webhooks

---

## 17. Safe task_type Allowlist

```text
docs_only
plan_only
readiness_check
test
compile
report
read_only_query
pure_helper_local
```

- unknown task_type -> Owner approval

## 18. Safe requested_tools Allowlist

```text
read_file
list_files
grep
search
compile
run_tests
```

- unknown requested_tool -> Owner approval or reject
- empty requested_tools -> fail closed
- empty allowed_tools -> fail closed
- denylist overrides allowlist

---

## 19. Protected Files Policy

The following are protected; any task that would touch them is at least Level 2
(Owner approval required) and can never be auto-approved:

```text
app/main.py
app/queue_store.py
app/worker.py
app/result_sink.py
app/approval_security_gate_v0_7.py
app/security_gates_v0_7.py
app/queue_intake_bridge_v0_7.py
app/dashboard_intake_view_v0_7.py
templates/*
static/*
scripts/start_worker.sh
any Google Sheets live runner
any OpenClaw client
any Hermes client
```

## 20. Forbidden Operations Policy

The following operations must never be auto-approved (Level 3; prohibited or
strong Owner approval):

```text
read secrets
display secrets
write production DB
start Worker
call OpenClaw
call Hermes live client
create webhook
push
tag
delete files
set GOOGLE_SHEETS_ENABLED=true
Google Sheets live write
```

---

## 21. Kill Switch Priority

The kill switch always wins. `GLOBAL_KILL_SWITCH` is highest, then
`AUTO_APPROVAL_KILL_SWITCH` (layer). When either is active, no task is
auto-approved.

Full evaluation priority order (fail-closed at any failing step):

```text
1. GLOBAL_KILL_SWITCH
2. AUTO_APPROVAL_KILL_SWITCH
3. forbidden operations
4. protected files
5. denied_tools / denylist
6. task_type allowlist
7. requested_tools allowlist
8. risk level gate
9. requires_confirmation gate
10. local_only / mock / executable_by_worker boundary
11. audit event generation
12. fallback to Owner approval
```

## 22. Denylist / Allowlist Priority

Denylist overrides allowlist. A denied tool / forbidden operation / protected
file is rejected even if it would otherwise match a safe allowlist entry.

## 23. Risk Level Policy

Only `safety_level <= MAX_AUTO_SAFETY_LEVEL` (1) is eligible for auto-approval.
`safety_level >= REVIEW_SAFETY_LEVEL` (3) always requires Owner approval. Missing
or unparseable `safety_level` is treated conservatively (fail-closed → Owner
approval), never as low-risk.

## 24. requires_confirmation Policy

`requires_confirmation == true` forces Owner approval regardless of any other
signal; it can never be auto-approved.

## 25. executable_by_worker / local_only / mock Policy

- `local_only == true` and `mock == true` are intake/observation states and must
  not be auto-approved into execution.
- `executable_by_worker` must be explicitly `true` before a task could ever be
  considered for queued execution; absent/false is fail-closed.
- Auto-approval in v0.7.2 never sets `executable_by_worker` and never queues.

---

## 26. Audit Event Model

Proposed (reusing `build_audit_event` + `redact_audit_metadata`):

```text
decision:
  auto_approved
  needs_owner_approval
  rejected
  prohibited

fields:
  event_id
  created_at
  action="auto_approval.policy_decision"
  observation_only=true
  task_id
  task_type
  safety_level
  requested_tools
  allowed_tools
  denied_tools
  matched_level
  reason
  decision
  actor_id redacted/masked
  metadata redacted
```

- v0.7.2-A does not persist audit events.
- v0.7.2-B should also remain observation-only first.

---

## 27. Observation-only Boundary

All auto-approval decisions in this plan (and the first helper) are
observation-only: a returned decision dict, not a state change. Nothing is
written to any DB.

## 28. QueueStore Boundary

- auto-approved does not mean queued.
- auto-approved does not write QueueStore in v0.7.2-A.
- QueueStore remains the source of truth for task state.

## 29. Approval Route Boundary

- auto-approved does not bypass approval_security_gate.
- auto-approved does not bypass security_gates.
- The approve route is not wired to any auto-approval logic in v0.7.2-A.

## 30. Worker / OpenClaw Boundary

- auto-approved does not mean Worker execution.
- auto-approved does not call OpenClaw.
- No Worker is started.

## 31. Hermes Boundary

- auto-approved does not call Hermes.
- No Hermes client or webhook is added.

## 32. Google Sheets Boundary

- auto-approved does not write production DB.
- Google Sheets live write must never be auto-approved; `GOOGLE_SHEETS_ENABLED`
  is not set to true.

## 33. Secrets Boundary

No refresh token / client secret / private key / full spreadsheet ID is read or
displayed. Sensitive checks use regex / format matching only. This version does
not read `.env`, credentials, tokens, or any secrets file.

---

## 34. Future v0.7.2-B Pure Helper Criteria

v0.7.2-B:

- pure helper only
- app/auto_approval_policy_v0_7.py
- evaluate_auto_approval(...)
- no route wiring
- no QueueStore write
- observation-only

## 35. Future v0.7.2-C Local-only Simulation Criteria

v0.7.2-C:

- local-only simulation CLI
- no Queue status change
- no Worker

## 36. Future v0.7.2-D Intake Annotation Criteria

v0.7.2-D:

- optional local-only intake annotation
- still waiting_review
- still executable_by_worker=false
- no queued
- no Worker

## 37. Relationship To Future F2-A

Future F2-A:

- approve route wiring is separate
- requires production readiness audit
- requires explicit Owner approval

Auto-approval may only ever influence a real `approve → queued` transition
through the separate F2-A path, after its preconditions are met. v0.7.2 does not
touch that path.

---

## 38. Explicit Non-goals

- v0.7.2-A is plan-only.
- v0.7.2-A does not implement auto-approval code.
- v0.7.2-A does not add app/auto_approval_policy_v0_7.py.
- v0.7.2-A does not modify app/main.py.
- v0.7.2-A does not modify queue_store.py.
- v0.7.2-A does not modify worker.py.
- v0.7.2-A does not modify result_sink.py.
- v0.7.2-A does not modify approval_security_gate_v0_7.py.
- v0.7.2-A does not modify security_gates_v0_7.py.
- v0.7.2-A does not modify queue_intake_bridge_v0_7.py.
- v0.7.2-A does not modify dashboard_intake_view_v0_7.py.
- v0.7.2-A does not modify templates or static.
- v0.7.2-A does not wire intake bridge.
- v0.7.2-A does not wire approve route.
- v0.7.2-A does not modify QueueStore state semantics.
- v0.7.2-A does not start Worker.
- v0.7.2-A does not call OpenClaw.
- v0.7.2-A does not call Hermes.
- v0.7.2-A does not write Google Sheets.
- v0.7.2-A does not create a v0.7 tag.

---

## 39. Final Recommendation

Adopt this policy as the agreed Safe Autopilot / Auto-Approval design. Keep all
flags default-off, `AUTO_APPROVAL_MODE` limited to `off | safe`, and every
unknown/dangerous mode fail-closed. Proceed to v0.7.2-B (pure helper,
observation-only) only after Owner approval, reusing `security_gates_v0_7.py` and
`approval_security_gate_v0_7.py` without modifying them. Auto-approval must never
mean auto-execute; push / tag / secrets / production DB / Worker start / OpenClaw
/ Hermes / Google Sheets live write must never be auto-approved; and QueueStore
remains the source of truth. Do not create a v0.7 tag.
