# Hermes × OpenClaw Adapter — v0.7.1 Closeout Boundary Review (v0.7.1-H)

> **Status: CLOSEOUT-ONLY.** This version adds a closeout document and a static
> readiness check. It changes no application code, wires no route, and creates no
> tag.
>
> Boundary declarations for this version:
>
> - v0.7.1-H is closeout-only.
> - v0.7.1-H does not modify app/main.py.
> - v0.7.1-H does not modify queue_store.py.
> - v0.7.1-H does not modify worker.py.
> - v0.7.1-H does not modify result_sink.py.
> - v0.7.1-H does not modify queue_intake_bridge_v0_7.py.
> - v0.7.1-H does not modify security_gates_v0_7.py.
> - v0.7.1-H does not modify approval_security_gate_v0_7.py.
> - v0.7.1-H does not modify dashboard_intake_view_v0_7.py.
> - v0.7.1-H does not modify templates or static files.
> - v0.7.1-H does not wire approve routes.
> - v0.7.1-H does not wire Dashboard approve.
> - v0.7.1-H does not modify QueueStore state semantics.
> - v0.7.1-H does not start Worker.
> - v0.7.1-H does not call OpenClaw.
> - v0.7.1-H does not call Hermes.
> - v0.7.1-H does not write Google Sheets.
> - v0.7.1-H does not create a v0.7 tag.

---

## 1. Purpose

This document closes out the v0.7.1 line (segments A through G). It freezes the
completion status, the safety boundaries, the explicitly-unwired items, and the
preconditions for any future approve-route wiring (F2-A) into a single closeout
record. It performs no code change and recommends no release tag.

Key closeout facts:

- v0.7.1-A through G are complete.
- current master is 0c02c562620b1631cc60f44e8d4e61825bb6a30f.
- current-state aggregator is the regression gate.
- A/C/C2/D stale readiness scripts are historical snapshots and are not required
  to be green.
- F2-A has not started.
- F2-B has not started.
- v0.7.2 has not started.
- No v0.7 tag currently exists.

---

## 2. Current Master State

- HEAD = origin/master = 0c02c562620b1631cc60f44e8d4e61825bb6a30f.
- Working tree clean; no v0.7 tag.
- `compileall app scripts` and `from app.main import app` succeed.
- The current-state aggregator and G readiness pass; B/C3/D2/E/F/F2 readiness and
  their tests pass.

---

## 3. v0.7.1 Scope Summary

v0.7.1 built the controlled intake → review → (planned) approval safety chain in
the adapter, strictly under "control before automation, mock before real, queue
before worker, owner approval before external side effect". It delivered intake
bridging, dashboard read-only visibility, security-gate pure helpers, intake-gate
wiring, an approval-gate pure helper, the approve-route wiring plan, and a
current-state regression aggregator. No external system (OpenClaw / Hermes /
Google Sheets) was newly connected, and the approval gate remains unwired.

---

## 4. v0.7.1-A Status

Plan-only — controlled queue intake plan. Complete. Negative assertions later
intentionally superseded by v0.7.1-B (see stale policy, section 20).

## 5. v0.7.1-B Status

Implemented — `app/queue_intake_bridge_v0_7.py` (local-only intake bridge;
`QUEUE_INTAKE_ENABLED` default false; kill switch; writes only a local-only
intake DB; `initial_status=WAITING_REVIEW`). Complete.

## 6. v0.7.1-C Status

Implemented — `app/dashboard_intake_view_v0_7.py` (read-only intake status
view-model derivation). Complete.

## 7. v0.7.1-C2 Status

Plan-only — web dashboard read-only status badges plan. Complete. Superseded by
v0.7.1-C3 (see stale policy).

## 8. v0.7.1-C3 Status

Implemented — read-only intake/status badges wired into `app/main.py` and
`templates/task_detail.html` (display only; no state mutation). Complete.

## 9. v0.7.1-D Status

Plan-only — kill switch / audit / allowlist plan. Complete. Superseded by
v0.7.1-D2 and v0.7.1-F security gate modules (see stale policy).

## 10. v0.7.1-D2 Status

Implemented — `app/security_gates_v0_7.py` pure functions
(`evaluate_security_gates`, `evaluate_tool_allowlist`, `build_audit_event`,
`redact_audit_metadata`). No DB write, no wiring. Complete.

## 11. v0.7.1-E Status

Implemented — local-only intake security gate wiring into the intake bridge
(`INTAKE_SECURITY_GATES_ENABLED` default false; fail-closed reject does not write
the DB). Complete.

## 12. v0.7.1-F Status

Implemented as a pure helper — `app/approval_security_gate_v0_7.py`
(`evaluate_approval_to_queued`; disabled → allow; enabled → fail-closed). Not
wired into any route, QueueStore, or worker. Complete as helper.

## 13. v0.7.1-F2 Status

Plan-only — approve route wiring plan (API F2-A and Dashboard F2-B staged for the
future). No wiring performed. Complete as plan.

## 14. v0.7.1-G Status

Implemented — current-state regression aggregator
(`scripts/check_hermes_openclaw_v0_7_1_current_state.py`), stale readiness policy
document, and G readiness. Complete.

---

## 15. Implemented Capabilities

- Local-only queue intake bridge
- Dashboard read-only intake/status badges
- Security gates pure helper
- Local-only intake security gate wiring
- Approval-to-queued security gate pure helper
- Approve route wiring plan
- Current-state regression aggregator
- Expected-stale readiness allowlist

---

## 16. Plan-only Items

- v0.7.1-A (controlled queue intake plan)
- v0.7.1-C2 (web dashboard badges plan)
- v0.7.1-D (kill switch / audit / allowlist plan)
- v0.7.1-F2 (approve route wiring plan)

These are documentation only; they performed no wiring and no state change.

---

## 17. Explicitly Unwired Items

- approval_security_gate_v0_7.py is not wired into app/main.py.
- API POST /tasks/{id}/approve is not wired to evaluate_approval_to_queued.
- Dashboard approve is not wired to evaluate_approval_to_queued.
- QueueStore.approve remains unchanged.
- Worker is not changed.
- OpenClaw is not newly connected.
- Hermes is not connected.
- Google Sheets live write is not enabled.
- No v0.7 tag has been created.

---

## 18. Safety Boundary Confirmation

The current-state aggregator asserts (and this closeout confirms) that the
approval gate helper exists but is not wired anywhere, that QueueStore remains
the source of truth for task state, that no external system was newly connected,
that Google Sheets live write is disabled, and that no real secret patterns are
present. The intake bridge and intake gate are local-only and default-off.

---

## 19. Current-State Regression Status

current-state aggregator is the regression gate. On current master it passes,
re-running B/C3/D2/E/F/F2 readiness as hard gates and asserting all current-state
truths and boundaries. It does not require A/C/C2/D to be green.

---

## 20. Stale Readiness Policy

A/C/C2/D stale readiness scripts are historical snapshots and are not required to be green. They are preserved unchanged as version-time audit snapshots; the
current-state aggregator carries the expected-stale allowlist
(v0.7.1-A/C/C2/D) and is the single regression entry point. See v0.7.1-G doc.

---

## 21. Approval Route Boundary

API approve (`POST /tasks/{id}/approve`) still runs the existing flow:
token auth → require waiting_review → `QueueStore.approve` →
status ledger + system comment. It does not import or call
`evaluate_approval_to_queued`. The approval gate is not wired here.

---

## 22. Dashboard Approval Boundary

Dashboard approve (`POST /dashboard/tasks/{id}/approve`) still runs the existing
PRG flow via `QueueStore.approve`. It does not import or call
`evaluate_approval_to_queued`. The approval gate is not wired here.

---

## 23. QueueStore Boundary

`app/queue_store.py` is unchanged. `approve` remains the atomic conditional
`waiting_review → queued`; `reject` remains `waiting_review → rejected`.
QueueStore remains the source of truth for task state. No DB schema change.

---

## 24. Worker / OpenClaw Boundary

`app/worker.py` is unchanged. The worker still claims only `queued` tasks; no new
gate is inserted. OpenClaw is not newly connected; the only `run_openclaw_cli`
usage is the pre-existing background dispatch path in `app/main.py`, untouched by
v0.7.1.

## 25. Hermes Boundary

Hermes is not connected. No Hermes webhook, client, or intake endpoint was added.

## 26. Google Sheets Boundary

Google Sheets live write is not enabled. `GOOGLE_SHEETS_ENABLED` is not set to
true. No Google Sheets writer/runner was wired into any v0.7.1 path.

## 27. Secrets Boundary

No refresh token / client secret / private key / full spreadsheet ID is read or
displayed. Sensitive checks use regex / format matching only. This version does
not read `.env`, credentials, tokens, or any secrets file.

---

## 28. F2-A Preconditions

Before starting F2-A (API-only approve gate wiring), at least the following must
be satisfied:

- production readiness audit for waiting_review tasks:
  - count waiting_review tasks
  - count payload presence
  - count payload.metadata presence
  - count metadata.requested_tools presence
  - count allowed_tools presence
  - count executable_by_worker=true
  - count local_only/mock/executable_by_worker=false
- Owner explicit approval for API-only wiring
- APPROVAL_SECURITY_GATES_ENABLED default false
- APPROVAL_KILL_SWITCH default false
- reject returns 409
- reject keeps waiting_review
- reject does not call QueueStore.approve
- QueueStore remains state source of truth

This closeout version does not query any production DB; it only records the
preconditions.

---

## 29. v0.7.2 Direction Options

- (Preferred) F2-A: API-only approve gate wiring, after the production readiness
  audit and explicit Owner approval, starting with the gate disabled.
- (Next) F2-B: Dashboard approve wiring, only after F2-A is proven.
- (Later) Real-integration scaffolding (still mock-first) for Hermes / OpenClaw /
  Worker, sequenced after the approve-gate wiring is stable.

### v0.7.2-A: Auto-Approval Policy Plan / Safe Autopilot Mode

A future option is a controlled, low-risk auto-approval capability. It is a
**safe** policy, not an unrestricted execution mode.

Hard rulings for this future option:

- This is not a dangerous skip-permissions mode.
- No --dangerously-skip-permissions equivalent is approved.
- The goal is safe low-risk auto-approval, not unrestricted execution.
- Low-risk tasks may be auto-approved only when all safety gates pass.
- High-risk tasks must still require Owner approval.
- v0.7.2-A should start as plan-only.

Proposed env flags (all default-off / safe):

```text
AUTO_APPROVAL_MODE=off | safe
SAFE_AUTOPILOT_ENABLED=false by default
LOW_RISK_AUTO_APPROVAL_ENABLED=false by default
AUTO_APPROVAL_POLICY=safe
```

Proposed risk layering:

- Level 0: auto-allowed read-only / report / test / compile operations
- Level 1: auto-allowed but audited local-only docs / mock / pure helper work
- Level 2: Owner approval required for protected files, app/main.py, queue_store.py, worker.py, approval route, commits
- Level 3: prohibited or strong approval required for push, tag, secrets, production DB, Worker start, OpenClaw, Hermes live client, Google Sheets live write

v0.7.2-A preconditions (before any implementation):

- Define safe task_type allowlist.
- Define safe requested_tools allowlist.
- Define protected files list.
- Define forbidden operations list.
- Define audit requirements.
- Define fallback to Owner approval.
- Define kill switch behavior.
- Define default-off env flags.

---

## 30. Tag Recommendation

- Do not tag in v0.7.1-H.
- Tagging requires separate explicit Owner approval.
- v0.7.1-H should close out by doc + readiness first.

---

## 31. Explicit Non-goals

- v0.7.1-H is closeout-only.
- v0.7.1-H does not modify app/main.py.
- v0.7.1-H does not modify queue_store.py.
- v0.7.1-H does not modify worker.py.
- v0.7.1-H does not modify result_sink.py.
- v0.7.1-H does not modify queue_intake_bridge_v0_7.py.
- v0.7.1-H does not modify security_gates_v0_7.py.
- v0.7.1-H does not modify approval_security_gate_v0_7.py.
- v0.7.1-H does not modify dashboard_intake_view_v0_7.py.
- v0.7.1-H does not modify templates or static files.
- v0.7.1-H does not wire approve routes.
- v0.7.1-H does not wire Dashboard approve.
- v0.7.1-H does not modify QueueStore state semantics.
- v0.7.1-H does not start Worker.
- v0.7.1-H does not call OpenClaw.
- v0.7.1-H does not call Hermes.
- v0.7.1-H does not write Google Sheets.
- v0.7.1-H does not create a v0.7 tag.

---

## 32. Final Closeout Recommendation

v0.7.1 (A through G) is complete, self-consistent, and all current-state
regressions are green. The approval gate helper exists but is intentionally
unwired; QueueStore remains the source of truth; no external system was newly
connected. Close out v0.7.1 with this document plus the H readiness check, keep
the current-state aggregator as the regression entry point, and do **not** create
a v0.7 tag. Proceed to F2-A only after the production readiness audit (section 28)
and explicit Owner approval. Any future Safe Autopilot / Auto-Approval work
(v0.7.2-A: Auto-Approval Policy Plan / Safe Autopilot Mode, section 29) must start
as plan-only, default-off, and is explicitly **not** a dangerous skip-permissions
mode: no --dangerously-skip-permissions equivalent is approved, low-risk tasks may
be auto-approved only when all safety gates pass, and high-risk tasks must still
require Owner approval.
