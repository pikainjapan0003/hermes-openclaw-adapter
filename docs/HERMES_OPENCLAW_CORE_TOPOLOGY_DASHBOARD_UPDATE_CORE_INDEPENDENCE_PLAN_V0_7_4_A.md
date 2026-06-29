# Hermes × OpenClaw Adapter — Core Topology / Dashboard Update / Core Independence Plan (v0.7.4-A)

> **Status: PLAN / DOCS-ONLY.** This version adds one planning document and one
> static readiness check. It changes no application code, no templates, no static
> assets, no `app/main.py`, no `app/queue_store.py`, no existing docs, no README,
> no tests, and no seed script; it wires no route, migrates no schema, builds no
> database, creates no connector, and creates no tag. It does not touch the Replit
> SQLite database and does not clean up or seed the demo task.
>
> Boundary declarations:
>
> - v0.7.4-A is documentation / planning only.
> - No QueueStore runtime behavior changes.
> - No approval routes changes.
> - No dashboard auth changes.
> - No status transition changes.
> - No Worker execution.
> - No OpenClaw call.
> - No Hermes call.
> - No Google Sheets write.
> - No external side effects.
> - No --apply.
> - No demo task cleanup.
> - No seed demo task.
> - No secrets read.
> - No webhook.
> - No production DB.
> - No remote shared DB.
> - No Remote Blackboard API runtime.
> - No webhook receiver.

---

## 1. Purpose

This is the **Core Topology / Dashboard Update / Core Independence Plan** for the
v0.7.4 line. It is a planning document that formally defines the system topology:
the positioning of GitHub, Windows WSL, and Replit; the Dashboard Update Rule; the
Core Independence Rule; the boundary between the local queue and the Replit queue;
the future direction for a Remote Blackboard API / shared DB; and the core
Hermes ↔ Blackboard ↔ OpenClaw loop. It performs no code change, enables no
runtime behavior, and recommends no release tag.

---

## 2. Current master

```
HEAD = origin/master = 1ea988ef1ed089336f720358e0d24f4164cf572a
docs: close out approval decision layer
```

---

## 3. Scope

In scope (this segment only):

- Add this planning document.
- Add one static readiness script that asserts the document exists, contains the
  required sections (1–20), the current-master marker, the v0.7.3 completion
  markers, the positioning / rule / boundary / future / message-family / loop /
  posture markers, and the next recommended step — and carries no unsafe claim and
  no secret.

Explicitly out of scope: any change to runtime code, templates, static assets,
`app/main.py`, `app/queue_store.py`, existing docs, README, tests, the seed
script, approval routes, dashboard auth, QueueStore, status transitions, the
Worker, or any external system. No production DB, no remote shared DB, no Remote
Blackboard API runtime, no webhook receiver, and no new connector are created.

---

## 4. Relationship to v0.7.3-R

v0.7.4-A builds directly on the v0.7.3-R closeout. The Approval Decision Layer is
already complete and stays unchanged:

```
v0.7.3 Approval Decision Layer is complete.
approval_decision_events are Decision Messages.
Decision Messages are blackboard audit records, not execution commands.
approve is not execute.
Owner decision event is not Worker dispatch.
No Worker / OpenClaw / Hermes / Google Sheets execution was enabled.
```

v0.7.4-A does not modify, re-open, or extend the v0.7.3 recorder, view, routes, or
QueueStore method. It only records the topology and rules around that completed
layer.

---

## 5. Core topology summary

The system is composed of three environments and one logical core loop:

- **GitHub** — clean source of truth for code and docs.
- **Windows WSL** — primary local development environment.
- **Replit** — remote observation station / Preview Dashboard.

The logical core is the **Blackboard loop**: Hermes writes Task / Advice Messages
to the Blackboard, the Worker / OpenClaw reads Task Messages and reports Result
Messages back, and the Owner monitors and decides. The Dashboard is a window onto
this loop, not the loop itself.

---

## 6. GitHub positioning

```
GitHub = clean source of truth for code and docs.
GitHub is not the queue database.
GitHub is not the blackboard database.
GitHub is not a secrets store.
GitHub must not store .env, tokens, credentials, local queue DB, logs, private keys, or production secrets.
```

GitHub carries versioned code and documentation only. Queue data, blackboard
records, and secrets are deliberately kept out of the repository.

---

## 7. Windows WSL positioning

```
Windows WSL = primary local development environment.
Windows WSL is responsible for code edits, tests, commits, pushes, and local development validation.
Windows WSL may have its own local queue and local logs.
Windows WSL local queue does not automatically sync to Replit.
```

Windows WSL is where development happens. Any local queue it holds is local
development state, not a shared production blackboard.

---

## 8. Replit positioning

```
Replit = remote observation station / Preview Dashboard.
Replit is not the production Worker host.
Replit is not the production OpenClaw host.
Replit is not the production Hermes host.
Replit is not the production queue database.
Replit is not the high-risk external execution host.
Replit Dashboard is a remote monitor, not the factory itself.
```

Replit hosts a read-only Preview Dashboard for remote observation. It does not run
the Worker, OpenClaw, or Hermes, and it is not the authoritative queue.

---

## 9. Dashboard Update Rule

```
Dashboard update means git pull plus Dashboard restart.
Dashboard update only updates UI / dashboard code on that environment.
Dashboard update does not sync WSL local queue.
Dashboard update does not update Hermes memory.
Dashboard update does not update OpenClaw execution state.
Dashboard update does not start Worker.
Dashboard update does not call OpenClaw.
Dashboard update does not call Hermes.
Dashboard update does not write Google Sheets.
Dashboard update does not trigger webhook.
Dashboard update does not cause external side effects.
```

Updating a Dashboard refreshes only the UI / dashboard code on that environment.
It is an inert code-refresh, not an execution event.

---

## 10. Core Independence Rule

```
The core blackboard loop should not depend on whether Replit Dashboard is updated.
Dashboard can be stale.
Dashboard can be offline.
Dashboard can be temporarily unavailable.
Core Blackboard / Queue / Worker / Hermes / OpenClaw should eventually live on a core host or shared backend.
Dashboard is an Owner observation and review surface, not the system heart.
```

The core loop must remain correct and live regardless of the Dashboard's state.
The Dashboard is an observation and review surface; the heart of the system is the
core blackboard loop.

---

## 11. Local queue vs Replit queue boundary

```
Current Windows WSL local queue and Replit local queue are separate.
They do not automatically sync.
Replit pull updates code, not queue data.
GitHub push updates code, not queue data.
A shared blackboard requires a future Remote Blackboard API or shared DB.
```

Today there are two independent local queues. Neither code pull nor code push
moves queue data between them; a genuinely shared blackboard is a future build.

---

## 12. Remote Blackboard API / shared DB future path

```
Remote Blackboard API / shared DB is future planning only in v0.7.4-A.
v0.7.4-A does not implement production DB.
v0.7.4-A does not migrate queues.
v0.7.4-A does not enable shared writes.
v0.7.4-A does not create webhooks.
v0.7.4-A does not start Worker.
```

A Remote Blackboard API / shared DB is the eventual path to a single shared
blackboard, but it is described here only as direction. This segment implements
none of it.

---

## 13. Blackboard message family

The Blackboard carries four message kinds:

```
Task Message
Decision Message
Result Message
Advice Message
```

- **Task Message** — work to be done, written toward the Worker.
- **Decision Message** — an Owner decision, recorded as audit metadata.
- **Result Message** — an outcome reported back by the Worker / OpenClaw.
- **Advice Message** — Hermes guidance derived from results.

---

## 14. Approval decision events as Decision Messages

```
approval_decision_events are Decision Messages.
Decision Messages are blackboard audit records.
Decision Messages are not Worker commands.
Decision Messages are not OpenClaw commands.
Decision Messages are not Hermes instructions.
```

The v0.7.3 `approval_decision_events` are exactly the Decision Message family
member. They record that an Owner made a decision; they are audit entries, not
instructions to any executor.

---

## 15. Hermes ↔ Blackboard ↔ OpenClaw loop

```
Hermes writes to Blackboard.
OpenClaw / Worker reads from Blackboard.
OpenClaw / Worker reports Result Messages back to Blackboard.
Hermes reads Result Messages and produces Advice Messages.
Owner monitors, approves, rejects, cancels, archives, and can interrupt the loop.
```

This is the original intent of the system: a blackboard-mediated loop where Hermes
and the Worker communicate only through the Blackboard, and the Owner stays in
control of the loop. v0.7.4-A wires none of this; it only records the topology.

---

## 16. Current safe system posture

```
Dashboard read-only / controlled local route behavior
Worker OFF
OpenClaw Not Connected
Hermes Not Connected
Google Sheets Disabled
No external side effects
No --apply
No demo task cleanup
No seed demo task
No secrets read
No webhook
No tag
```

---

## 17. Deployment boundary decisions

The deployment boundaries follow directly from the positioning above:

- Code and docs flow through GitHub; queue data and secrets do not.
- Development, tests, commits, and pushes happen on Windows WSL.
- Replit serves a remote read-only Preview Dashboard and is not a production
  executor or production queue.
- A Dashboard update is a UI code-refresh (git pull plus restart) with no runtime
  or external side effect.
- The core loop's correctness must not depend on whether a Dashboard was updated.
- A shared blackboard, if and when built, lives behind a future Remote Blackboard
  API / shared DB — not in GitHub and not as an automatic queue sync.

---

## 18. Non-goals

v0.7.4-A explicitly does not:

- Change any runtime code, template, static asset, `app/main.py`, or
  `app/queue_store.py`.
- Change QueueStore runtime behavior, approval routes, dashboard auth, or any
  status transition.
- Modify the seed script, existing docs, or the README.
- Add a route, migrate schema, or build a production DB / remote shared DB.
- Implement a Remote Blackboard API runtime, a webhook receiver, or any connector.
- Start the Worker, call OpenClaw / Hermes, or write Google Sheets.
- Read secrets, create a webhook, or add any external side effect.
- Seed (`--apply`) or clean up the demo task.
- Perform a live local queue write validation.
- Commit, push, or create a release tag.

---

## 19. Acceptance criteria

v0.7.4-A is accepted when:

1. This planning document exists at the documented path and contains sections
   1–20.
2. The readiness script
   `scripts/check_hermes_openclaw_core_topology_dashboard_update_core_independence_plan_v0_7_4_a.py`
   reports PASS.
3. The document records the current master, the v0.7.3 completion markers, the
   GitHub / Windows WSL / Replit positioning, the Dashboard Update Rule, the Core
   Independence Rule, the local-vs-Replit queue boundary, the Remote Blackboard
   future-only direction, the Blackboard message family, the Decision Message
   positioning, the Hermes ↔ Blackboard ↔ OpenClaw loop, and the safe posture.
4. The document states the non-goals and carries no unsafe claim and no secret.
5. The segment adds only this document and the readiness script — no runtime file
   changed.
6. Nothing is committed, pushed, or tagged without Owner approval.

---

## 20. Next recommended step

Recommended next step (requires explicit Owner approval to start):

- **v0.7.4-B — Queue / Blackboard Lifecycle Plan.**

> v0.7.4-B must remain plan-first.
> It should define Queue / Blackboard lifecycle and message family before any runtime enforcement.
> No Worker dispatch.
> No OpenClaw / Hermes / Google Sheets.
> No external side effects.

Execution dispatch wiring, production DB, shared writes, and any Remote Blackboard
API runtime remain explicitly **out** of this feature line.
