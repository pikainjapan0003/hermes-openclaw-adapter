# Hermes × OpenClaw Adapter — Approve Route Wiring Plan (v0.7.1-F2)

> **Status: PLAN-ONLY.** This version adds documentation and a static readiness
> script only. It does **not** wire the approval security gate into any route.
>
> Explicit boundary declarations for this version:
>
> - v0.7.1-F2 is plan-only.
> - No app/main.py modification.
> - No queue_store.py modification.
> - No worker.py modification.
> - No result_sink.py modification.
> - No approval_security_gate_v0_7.py modification.
> - No security_gates_v0_7.py modification.
> - No queue_intake_bridge_v0_7.py modification.
> - No approve route wiring.
> - No Dashboard approve wiring.
> - No new route.
> - No new POST handler.
> - No DB schema change.
> - No Worker start.
> - No OpenClaw execution.
> - No Hermes webhook.
> - No Google Sheets write.
> - No Queue status mutation.
> - No audit ledger persistence.

---

## 1. Purpose

This document plans **how** the pure approval security gate helper introduced in
v0.7.1-F (`app/approval_security_gate_v0_7.py`,
`evaluate_approval_to_queued(...)`) could *eventually* be wired into the
adapter's approve flow, so that a `waiting_review → queued` transition can be
gated by tool-level security checks.

It is deliberately **plan-only**. No wiring is performed in this version. The
goal is to:

1. Capture the current approve flow (API + Dashboard + QueueStore) accurately.
2. Name the env flags and the disabled/enabled contracts a future wiring must obey.
3. Record the metadata / requested_tools gap risk and the production readiness
   audit that must precede enabling the gate.
4. Split the future implementation into two staged versions: F2-A (API-only) and
   F2-B (Dashboard), with explicit test matrices.

This plan does not change runtime behavior. The gate remains a pure helper that
is **not** called by any route.

---

## 2. Relationship To v0.7.1-F

v0.7.1-F delivered the pure decision helper:

- `evaluate_approval_to_queued(task_row, *, approval_security_gates_enabled=False,
  global_kill_switch=False, layer_kill_switch=False) -> dict`
- The helper does not import `app.main` / `app.queue_store` / `app.worker` /
  `app.result_sink`, does not write the DB, and does not mutate task state.
- With the gate disabled it returns `allow` /
  `reason=approval_security_gates_disabled`, preserving the existing approve flow.
- With the gate enabled it is fail-closed (local_only / mock /
  executable_by_worker≠true / missing requested_tools / missing allowed_tools /
  denylist hit / disallowed tool / invalid tool name / kill switch → reject).

v0.7.1-F2 is the **planning layer above F**. It does not modify the F helper. It
describes how a future route would *call* that helper and what guarantees the
call site must keep.

---

## 3. Why This Version Is Plan-only

A pre-implementation inventory (the F2 "Approve Route Wiring Risk Review")
concluded that production `waiting_review` tasks may not carry
`metadata.requested_tools` / `allowed_tools`. Because the F helper is
fail-closed when those fields are missing, enabling the gate inside a live
approve route *before* a production readiness audit could block a batch of
otherwise-legitimate `waiting_review` tasks.

The Owner ruling for v0.7.1-F2 is therefore: **plan-only — do not wire the API
approve route, do not wire the Dashboard approve route, do not modify
`app/main.py`.** This document records the safe wiring design without performing
it.

---

## 4. Current API Approve Flow

Source: `app/main.py` (read-only reference; not modified by this version).

- `POST /tasks/{task_id}/approve` → `approve_task(...)`.
- Steps today:
  1. `require_token(x_adapter_token)` — adapter token auth.
  2. `_require_waiting_review(task_id)` — 404 if missing, 409 if not
     `waiting_review` (also 404 in `background` execution mode).
  3. `get_queue().approve(task_id)` — atomic conditional UPDATE
     `waiting_review → queued`; returns `None` on race (409).
  4. `append_task_status(task_id, "queued", via="approve")` — status ledger.
  5. `_add_system_comment(...)` — system comment.
  6. Returns `{"status": "approved", "task_id": ..., "task": updated}`.

There is **no** security-gate call in this flow today. The gate is not wired.

---

## 5. Current Dashboard Approve Flow

Source: `app/main.py` (read-only reference; not modified by this version).

- `POST /dashboard/tasks/{task_id}/approve` → `dashboard_approve(...)`.
- Steps today:
  1. `_task_exists(task_id)` — 404 if missing.
  2. `get_queue().approve(task_id)` — atomic `waiting_review → queued`; on `None`
     redirects back with an error query param (PRG pattern, 303).
  3. `append_task_status(task_id, "queued", via="dashboard-approve")`.
  4. `_add_system_comment(...)`.
  5. `RedirectResponse(target, 303)` (Post/Redirect/Get).

There is **no** security-gate call in this flow today. The gate is not wired.

---

## 6. Current QueueStore Approve Semantics

Source: `app/queue_store.py` (read-only reference; not modified by this version).

- `QueueStore.approve(task_id)`:
  - Atomic `UPDATE queue SET status='queued', updated_at=? WHERE task_id=? AND
    status='waiting_review'`.
  - Does not increment attempts, does not change `task_text`, does not run the worker.
  - Returns the updated row, or `None` when the row was not in `waiting_review`
    (covers concurrent approve/reject races).
- `QueueStore.reject(task_id, reason=None)`:
  - Atomic `waiting_review → rejected` (terminal), records `reason` into `error`.
  - Returns `None` when not in `waiting_review`.

**QueueStore remains the source of truth for task state.** Any future wiring must
keep the gate *in front of* `QueueStore.approve`, never bypassing or duplicating
the state machine.

---

## 7. Current Risk: Metadata / Requested Tools Gap

This is the central risk that makes F2 plan-only.

- production `waiting_review` tasks may not have `metadata.requested_tools` /
  `allowed_tools`.
- The F helper's enabled mode is fail-closed: when `requested_tools` /
  `allowed_tools` are missing it returns `reject`.
- Therefore F2-A route wiring must not be enabled before a production readiness
  audit confirms the shape of existing `waiting_review` tasks.

Concretely, the requested-tools source is fixed (per the v0.7.1-E ruling) to
`payload.metadata.requested_tools`, and `allowed_tools` / `denied_tools` are read
from the task payload. Legacy tasks created before that contract existed will not
have these keys, so enabling the gate naively would `reject` them at approve time
even though they are legitimate.

Mitigations recorded for the future (not implemented here):

- Keep `APPROVAL_SECURITY_GATES_ENABLED` defaulting to false until the audit and
  a backfill/contract decision are complete.
- Stage wiring so the gate is observable (audit-only / shadow) before it is
  allowed to block, if a shadow mode is added later.

---

## 8. Proposed Env Flags

The following flags are *proposed for a future wiring version* (F2-A / F2-B).
They are **not** introduced into `app/main.py` in this plan-only version.

- `APPROVAL_SECURITY_GATES_ENABLED` — master switch for the approve-to-queued
  gate. **APPROVAL_SECURITY_GATES_ENABLED must default to false.**
- `APPROVAL_KILL_SWITCH` — layer kill switch for the approve gate.
  **APPROVAL_KILL_SWITCH must default to false.**
- (Reuse, not new) `GLOBAL_KILL_SWITCH` — the existing global kill switch is
  mapped to the helper's `global_kill_switch` argument.

Mapping into the helper call (future):

```text
evaluate_approval_to_queued(
    task_row,
    approval_security_gates_enabled = APPROVAL_SECURITY_GATES_ENABLED,
    global_kill_switch              = GLOBAL_KILL_SWITCH,
    layer_kill_switch              = APPROVAL_KILL_SWITCH,
)
```

---

## 9. APPROVAL_SECURITY_GATES_ENABLED Behavior

- **APPROVAL_SECURITY_GATES_ENABLED must default to false.**
- When false: the gate returns allow / `approval_security_gates_disabled`.
  **Gate disabled must preserve current approve behavior** — the route behaves
  exactly as documented in sections 4–6.
- When true: **Gate enabled must fail closed** — the helper rejects local_only /
  mock / `executable_by_worker≠true` / missing requested_tools / missing
  allowed_tools / denylist hit / disallowed tool / invalid tool name / non-review
  status, before any `QueueStore.approve` call.

---

## 10. APPROVAL_KILL_SWITCH Behavior

- **APPROVAL_KILL_SWITCH must default to false.**
- When the approve-gate layer kill switch is active, the helper returns reject
  with `priority=layer_kill_switch` and the route must treat it as a gate
  rejection (see section 15). The global kill switch takes precedence over the
  layer kill switch in the helper's priority order.

---

## 11. API Approve Wiring Proposal

Future, staged as **F2-A** (see section 19). Only a sketch is recorded here; no
code is written in this version.

- Only `app/main.py` would be modified; `POST /tasks/{task_id}/approve` only.
- After `_require_waiting_review(task_id)` returns the queue row, build a
  `task_row` and call `evaluate_approval_to_queued(...)` with the env-mapped flags.
- If the decision is allow → proceed with the existing
  `get_queue().approve(task_id)` flow unchanged.
- If the decision is reject → return `409 Conflict` and **do not** call
  `QueueStore.approve`. The task stays `waiting_review`.
- No change to `queue_store.py`, `worker.py`, `result_sink.py`, or the helper.

---

## 12. Dashboard Approve Wiring Proposal

Future, staged as **F2-B** (see section 20). Only a sketch is recorded here; no
code is written in this version.

- The Dashboard approve route should be wired only after API wiring is proven.
- On gate reject, use a PRG redirect (303) back to the task detail page with an
  `error` reason query param.
- On gate reject, the Dashboard must keep the task `waiting_review` and **must
  not** call `QueueStore.approve`.
- No new route is required; the existing `POST
  /dashboard/tasks/{task_id}/approve` handler would gain the gate call.

---

## 13. Gate Disabled Compatibility Contract

- **Gate disabled must preserve current approve behavior.**
- With `APPROVAL_SECURITY_GATES_ENABLED=false`, both API and Dashboard approve
  routes behave byte-for-byte as in sections 4–5: same status codes, same
  redirects, same ledger / comment side effects.
- The gate call, when added, must short-circuit to allow without inspecting
  payload/metadata when disabled, so legacy tasks are unaffected.

---

## 14. Gate Enabled Fail-closed Contract

- **Gate enabled must fail closed.**
- With `APPROVAL_SECURITY_GATES_ENABLED=true`, a task missing
  `requested_tools` / `allowed_tools`, or marked local_only / mock /
  `executable_by_worker≠true`, or hitting denylist / disallowed tool / invalid
  tool name / kill switch, is rejected by the gate before any state change.
- Fail-closed means: when in doubt, reject. Absence of required metadata is a
  reject, not a pass.

---

## 15. Reject Semantics

When the gate rejects an approve attempt:

- **Gate reject must not call QueueStore.approve.**
- **Gate reject must not create queued tasks.**
- **Gate reject must keep task in waiting_review / pending_approval.**
- **Gate reject must not automatically transition task to rejected.** A gate
  reject is *not* an Owner reject; the task stays in review for human decision.
- API: respond `409 Conflict` with a machine-readable reason.
- Dashboard: PRG 303 redirect back to the detail page with an `error` reason.

---

## 16. Audit / Ledger / Comment Boundary

- The helper already produces an observation-only `audit_event`
  (`build_approval_audit_event`).
- In this plan-only version: **No audit ledger persistence.** The audit event is
  not stored anywhere.
- A future wiring version may log the audit event, but a gate reject must not
  write a `queued` status-ledger entry and must not create a queued task. Comment
  writes (if any) must not imply a state transition that did not occur.

---

## 17. Task Row / Payload Requirements Before Enabling

Before `APPROVAL_SECURITY_GATES_ENABLED=true` can be safe, an approvable task
must carry:

- A `payload` that parses to a dict.
- `payload.metadata` as a dict.
- `payload.metadata.requested_tools` as a non-empty list of valid tool names.
- `payload.allowed_tools` as a non-empty list of valid tool names.
- `payload.metadata.executable_by_worker == true`.
- `payload.metadata.local_only` not true and `payload.metadata.mock` not true.

Tasks not meeting these will be fail-closed rejected by the gate when enabled.

---

## 18. Required Production Readiness Audit Before Enabling

Before enabling F2-A, a production readiness audit must answer (read-only; this
plan does not query any production DB):

- How many waiting_review tasks exist?
- How many have payload?
- How many have payload.metadata?
- How many have metadata.requested_tools?
- How many have allowed_tools?
- How many have executable_by_worker=true?
- How many are local_only/mock/executable_by_worker=false?

Only after this audit and an explicit Owner ruling may F2-A enable the gate in a
controlled manner.

---

## 19. Test Matrix For Future F2-A API-only Wiring

F2-A scope (future): only modify `app/main.py`; only wire `POST
/tasks/{id}/approve`; do not wire Dashboard approve yet; do not modify
`queue_store.py` / `worker.py` / `result_sink.py` / the helper.

| # | Case | Flag | Expectation |
|---|------|------|-------------|
| 1 | Normal approve, gate disabled | OFF | 200 approved; status `queued` (unchanged behavior) |
| 2 | Approve fully-formed task, gate enabled | ON | 200 approved; status `queued` |
| 3 | Approve task missing requested_tools, gate enabled | ON | 409; stays `waiting_review`; no `QueueStore.approve` |
| 4 | Approve task missing allowed_tools, gate enabled | ON | 409; stays `waiting_review` |
| 5 | Approve local_only/mock task, gate enabled | ON | 409; stays `waiting_review` |
| 6 | Approve executable_by_worker=false, gate enabled | ON | 409; stays `waiting_review` |
| 7 | Denylist hit, gate enabled | ON | 409; stays `waiting_review` |
| 8 | APPROVAL_KILL_SWITCH active | ON+kill | 409; stays `waiting_review` |
| 9 | GLOBAL_KILL_SWITCH active | ON+kill | 409; stays `waiting_review` |
| 10 | Non-existent task | any | 404 |
| 11 | Not in waiting_review | any | 409 |

In all reject cases: gate enabled reject returns `409 Conflict`, reject keeps the
task `waiting_review`, reject does not call `QueueStore.approve`, and reject does
not write a `queued` ledger entry.

---

## 20. Test Matrix For Future F2-B Dashboard Wiring

F2-B scope (future): wire the Dashboard approve route only after API wiring is
proven; reject uses a PRG redirect with an error reason; reject keeps the task
`waiting_review`; the Dashboard must not call `QueueStore.approve` when the gate
rejects; no new route is required.

| # | Case | Flag | Expectation |
|---|------|------|-------------|
| 1 | Dashboard approve, gate disabled | OFF | 303 redirect to detail; status `queued` (unchanged) |
| 2 | Dashboard approve fully-formed, gate enabled | ON | 303 redirect; status `queued` |
| 3 | Dashboard approve missing requested_tools, gate enabled | ON | 303 redirect with `error`; stays `waiting_review` |
| 4 | Dashboard approve local_only/mock, gate enabled | ON | 303 redirect with `error`; stays `waiting_review` |
| 5 | Dashboard approve executable_by_worker=false, gate enabled | ON | 303 redirect with `error`; stays `waiting_review` |
| 6 | Kill switch active | ON+kill | 303 redirect with `error`; stays `waiting_review` |

---

## 21. Queue Source-of-truth Boundary

- **QueueStore remains the source of truth for task state.**
- The gate is a pre-check in front of `QueueStore.approve`; it never invents,
  caches, or mirrors task state.
- No DB schema change is introduced now or required by the future wiring.

---

## 22. Worker / OpenClaw Boundary

- This plan does not start a worker and does not call OpenClaw.
- Approve only moves a task to `queued`; the worker independently claims `queued`
  tasks (`claim_next` only takes `queued`). The gate does not change that.
- No OpenClaw execution. No Worker start.

---

## 23. Google Sheets Boundary

- No Google Sheets write. `GOOGLE_SHEETS_ENABLED` is not flipped to true.
- The approve gate has no relationship to any Google Sheets writer/runner and
  must never trigger one.

---

## 24. Security / Secrets Rules

- Do not read or display refresh tokens, client secrets, private keys, or full
  spreadsheet IDs.
- Sensitive checks use regex / format matching only.
- This plan does not read `.env`, credentials, tokens, or any secrets file.
- The readiness script for this version is static: no network, no DB, no secrets.

---

## 25. Future Implementation Criteria

The gate may only be wired (F2-A, then F2-B) when **all** of the following hold:

1. The production readiness audit in section 18 is complete.
2. Approvable tasks meet the requirements in section 17 (or a backfill plan exists).
3. Owner explicitly approves moving from plan-only to wiring.
4. `APPROVAL_SECURITY_GATES_ENABLED` and `APPROVAL_KILL_SWITCH` both still default
   to false; enabling is an explicit, reversible operational action.
5. Wiring keeps QueueStore as the source of truth and never bypasses the state
   machine.

---

## 26. Explicit Non-goals

This version explicitly does **not**:

- v0.7.1-F2 is plan-only.
- No app/main.py modification.
- No queue_store.py modification.
- No worker.py modification.
- No result_sink.py modification.
- No approval_security_gate_v0_7.py modification.
- No security_gates_v0_7.py modification.
- No queue_intake_bridge_v0_7.py modification.
- No approve route wiring.
- No Dashboard approve wiring.
- No new route.
- No new POST handler.
- No DB schema change.
- No Worker start.
- No OpenClaw execution.
- No Hermes webhook.
- No Google Sheets write.
- No Queue status mutation.
- No audit ledger persistence.

---

## 27. Final Recommendation

Adopt this plan as the agreed design for a future, staged wiring of the approval
security gate. Do **not** wire any route in this version. Proceed to F2-A
(API-only) only after the production readiness audit (section 18) and an explicit
Owner ruling, keeping `APPROVAL_SECURITY_GATES_ENABLED` and `APPROVAL_KILL_SWITCH`
defaulting to false, and keeping QueueStore as the source of truth for task
state. F2-B (Dashboard) follows only after F2-A is proven.
