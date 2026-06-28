# Hermes × OpenClaw Adapter — Auto-Approval Policy Pure Helper (v0.7.2-B)

> **Status: PURE-HELPER ONLY.** This version adds a pure decision helper, its
> tests, a doc, and a static readiness check. It wires nothing and changes no
> existing file.
>
> Boundary declarations:
>
> - v0.7.2-B is pure-helper only.
> - v0.7.2-B is observation-only.
> - v0.7.2-B does not wire routes.
> - v0.7.2-B does not wire intake bridge.
> - v0.7.2-B does not wire approve route.
> - v0.7.2-B does not write QueueStore.
> - v0.7.2-B does not create queued tasks.
> - v0.7.2-B does not start Worker.
> - v0.7.2-B does not call OpenClaw.
> - v0.7.2-B does not call Hermes.
> - v0.7.2-B does not write Google Sheets.
> - v0.7.2-B does not read or display secrets.
> - auto_approved does not mean queued.
> - auto_approved does not mean execution.
> - can_execute is always false.
> - queue_transition_allowed is always false.
> - observation_only is always true.
> - No dangerous skip-permissions mode is approved.
> - No --dangerously-skip-permissions equivalent is approved.

---

## 1. Purpose

Implement the Safe Autopilot / Auto-Approval policy designed in v0.7.2-A as a
**pure function**: given a task row and flags, return a policy decision about
whether the task is clearly low-risk enough to be auto-approved — without ever
executing, queueing, or mutating anything.

## 2. Relationship To v0.7.2-A

v0.7.2-A froze the policy (Level 0–3, allowlists, protected files, forbidden
ops, priority order, audit model, default-off flags). v0.7.2-B implements that
policy as `evaluate_auto_approval(...)`, observation-only, reusing the existing
security-gate pure functions.

## 3. Why Pure Helper First

Following the proven D2 / F pattern: land the decision logic as a tested pure
function with no side effects before any wiring. This keeps the most sensitive
decision auditable and reversible, and lets C/D/F2-A consume it later without
re-deriving the policy.

## 4. Helper API

```python
def evaluate_auto_approval(
    task_row: dict,
    *,
    auto_approval_mode: str = "off",
    safe_autopilot_enabled: bool = False,
    low_risk_auto_approval_enabled: bool = False,
    auto_approval_policy: str = "safe",
    global_kill_switch: bool = False,
    auto_approval_kill_switch: bool = False,
) -> dict
```

## 5. Return Schema

The returned dict contains:

```text
policy_decision
reason
matched_level
can_auto_approve
can_execute
queue_transition_allowed
requires_owner_approval
prohibited
observation_only
task_type
safety_level
requires_confirmation
requested_tools
allowed_tools
denied_tools
audit_event
```

## 6. Decision Enum

`policy_decision` is one of:

```text
auto_approved
needs_owner_approval
rejected
prohibited
```

## 7. can_auto_approve vs can_execute

`can_auto_approve` only states that the **policy layer** would allow automatic
approval. It never implies execution. `can_execute` is a separate field and is
always false. auto_approved does not mean execution.

## 8. queue_transition_allowed Boundary

`queue_transition_allowed` is always false. auto_approved does not mean queued.
A real `approve → queued` transition belongs to QueueStore via the separate
future F2-A path, not to this helper.

## 9. observation_only Boundary

`observation_only` is always true. Every decision (including the audit event) is
data only; nothing is persisted.

## 10. Reused Pure Functions

- `app.security_gates_v0_7.evaluate_security_gates` — tool denylist/allowlist gate.
- `app.security_gates_v0_7.build_audit_event` — observation-only audit event
  (masks actor, redacts metadata, sets observation_only=true).
- `app.approval_security_gate_v0_7.extract_payload` / `extract_metadata` — pure
  payload/metadata extraction (dict or JSON string).

## 11. Import Boundary

The helper imports only `app.security_gates_v0_7` and
`app.approval_security_gate_v0_7` (pure functions). It does not import app.main,
queue_store, worker, result_sink, sqlite3, requests, subprocess, google,
gspread, or oauth. There is no circular import: approval_security_gate imports
only stdlib + security_gates.

## 12. Level 0 Behavior

Level 0 (read-only / report / test / compile): no file writes, no external side
effects. Eligible for auto_approved (matched_level 0) when all gates pass.

## 13. Level 1 Behavior

Level 1 (docs_only / plan_only / pure_helper_local): local-only, audited. Must
not touch protected files, must not create queued tasks, must not execute Worker.
Eligible for auto_approved (matched_level 1) when all gates pass; can_execute
stays false.

## 14. Level 2 Behavior

Level 2 (protected files, commit, state machine change, approval route,
app/main.py, queue_store.py, worker.py): always needs_owner_approval. Protected
files override a safe task_type.

## 15. Level 3 Behavior

Level 3 (push, tag, secrets, production DB, Worker start, OpenClaw, Hermes live
client, Google Sheets live write, webhook): prohibited. Denied dangerous tools
also map to prohibited.

## 16. Safe task_type Allowlist

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

unknown task_type → needs_owner_approval.

## 17. Safe requested_tools Allowlist

```text
read_file
list_files
grep
search
compile
run_tests
```

unknown requested_tool → needs_owner_approval; empty requested_tools → fail
closed; empty allowed_tools → fail closed; denylist overrides allowlist.

## 18. Protected Files

Built-in protected list includes app/main.py, queue_store.py, worker.py,
result_sink.py, approval_security_gate_v0_7.py, security_gates_v0_7.py,
queue_intake_bridge_v0_7.py, dashboard_intake_view_v0_7.py, templates/*,
static/*, scripts/start_worker.sh, plus the live-client patterns
`*google_sheets*` / `*openclaw*` / `*hermes*` applied **only** to paths under
app/ or scripts/ (so docs titles containing HERMES_OPENCLAW are not misclassified
as clients).

## 19. Forbidden Operations

```text
read_secrets
display_secrets
write_production_db
start_worker
call_openclaw
call_hermes
create_webhook
git_push
git_tag
delete_file
enable_google_sheets_live_write
google_sheets_live_write
```

A `requested_operations` hit → prohibited.

## 20. Priority Order

```text
1. GLOBAL_KILL_SWITCH
2. AUTO_APPROVAL_KILL_SWITCH
3. invalid / unsupported mode
4. safe autopilot flags off
5. forbidden operations
6. protected files
7. denied_tools / denylist
8. task_type allowlist
9. requested_tools allowlist
10. risk level gate
11. requires_confirmation gate
12. local_only / mock / executable_by_worker boundary (observation-only)
13. audit event generation
14. fallback to Owner approval
```

Kill switch overrides everything; denylist overrides allowlist; unknown / empty /
unsafe is always fail-closed.

## 21. Kill Switch Behavior

`global_kill_switch=True` → rejected; `auto_approval_kill_switch=True` →
rejected. Kill switch is evaluated first and overrides forbidden ops, protected
files, and everything else.

## 22. Denylist Overrides Allowlist

A requested tool present in `denied_tools` → prohibited, even if it is also in
the safe allowlist or the task's own allowed_tools.

## 23. Risk Level Behavior

Only `safety_level <= MAX_AUTO_SAFETY_LEVEL` (1) is eligible. Missing or
unparseable safety_level → needs_owner_approval (never treated as low-risk);
safety_level > 1 → needs_owner_approval.

## 24. requires_confirmation Behavior

`requires_confirmation == true` → needs_owner_approval, regardless of other
signals.

## 25. touched_files / requested_operations Schema

Both are optional `list[str]` metadata fields. When present but not a list of
strings → needs_owner_approval (invalid). When absent, the corresponding gate is
skipped (a task with no declared touched_files / operations is still subject to
all other gates). Unknown / unsafe declared values fail closed.

## 26. Audit Event Model

Each decision carries an `audit_event` built via `build_audit_event` with
`action="auto_approval.policy_decision"`, `observation_only=true`, masked actor,
redacted metadata, and the decision/reason/risk_level. It is returned only and
never persisted.

## 27. QueueStore Boundary

The helper does not write QueueStore and does not create queued tasks.
queue_transition_allowed is always false. QueueStore remains the source of truth.

## 28. Approval Route Boundary

The helper does not wire the approve route and does not bypass
approval_security_gate. auto_approved does not bypass security_gates.

## 29. Worker / OpenClaw Boundary

The helper does not start Worker and does not call OpenClaw. can_execute is
always false.

## 30. Hermes Boundary

The helper does not call Hermes and adds no Hermes client or webhook.

## 31. Google Sheets Boundary

The helper does not write Google Sheets and does not set
`GOOGLE_SHEETS_ENABLED` true.

## 32. Secrets Boundary

The helper does not read or display secrets. Metadata in the audit event is
redacted via `redact_audit_metadata`. No `.env`, credentials, or token files are
read.

## 33. Tests

`scripts/test_auto_approval_policy_v0_7_2_b.py` covers Level 0–3, kill switch,
mode/flags off, denylist-overrides-allowlist, protected files override safe
task_type, forbidden operations, requires_confirmation, safety_level missing /
invalid / > 1, empty requested_tools, empty allowed_tools, unknown requested
tool, input-not-mutated, and the fixed safety fields (can_execute=false,
queue_transition_allowed=false, observation_only=true) for every decision.

## 34. Readiness

`scripts/check_hermes_openclaw_auto_approval_policy_helper_v0_7_2_b.py` statically
verifies the helper's purity, import boundary, fixed-false execution fields,
decision enum, doc headings/declarations, test coverage anchors, that no existing
app file was modified, and that no real secret patterns are present.

## 35. Explicit Non-goals

- v0.7.2-B is pure-helper only.
- v0.7.2-B is observation-only.
- v0.7.2-B does not wire routes.
- v0.7.2-B does not wire intake bridge.
- v0.7.2-B does not wire approve route.
- v0.7.2-B does not write QueueStore.
- v0.7.2-B does not create queued tasks.
- v0.7.2-B does not start Worker.
- v0.7.2-B does not call OpenClaw.
- v0.7.2-B does not call Hermes.
- v0.7.2-B does not write Google Sheets.
- v0.7.2-B does not read or display secrets.

## 36. Future v0.7.2-C

Local-only simulation CLI that prints `evaluate_auto_approval` decisions for
sample/local tasks; no Queue status change, no Worker.

## 37. Future v0.7.2-D

Optional local-only intake annotation that records the policy decision into the
local-only intake metadata; tasks stay waiting_review, executable_by_worker=false,
not queued, no Worker.

## 38. Relationship To Future F2-A

Approve route wiring (F2-A) is a separate path requiring a production readiness
audit and explicit Owner approval. This helper never wires it; auto_approved may
only ever influence a real approve→queued transition through that separate path.

## 39. Final Recommendation

Adopt `evaluate_auto_approval` as the canonical Safe Autopilot policy decision
function, kept observation-only with can_execute / queue_transition_allowed
always false. Keep all flags default-off and `auto_approval_mode` limited to
off | safe. Proceed to v0.7.2-C (local-only simulation) only after Owner
approval. auto_approved never means queued or execution, and QueueStore remains
the source of truth.
