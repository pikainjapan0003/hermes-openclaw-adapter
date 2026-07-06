# v0.9.5-A Limited Connector Trial Boundary Plan

## 1. Phase Title

v0.9.5-A Limited Connector Trial Boundary Plan

## 2. Explicit Correction

This phase must not be called Limited External Action Plan.

## 3. Current Baseline

v0.9-R completed, pushed, verified, closed.

Additional accepted docs/check-only baseline commit:

```text
52e96bec19bb78ceceb1996af703c2d12128d2bc
docs: add Replit autoscale migration safety audit
```

## 4. Purpose

Define boundary for future Limited Connector Trial.

## 5. Phase Classification

L0 documentation-only / check-only.

## 6. L0 / L1 / L2 Definitions

- **L0** — Documentation-only / no connector call.
- **L1** — Read-only metadata preview / no content mutation.
- **L2** — Read-only content preview / no content mutation.

## 7. Binding Ruling

- v0.9.5-A is L0 only.
- v0.9.5-A does not authorize L1.
- v0.9.5-A does not authorize L2.
- Any L1 or L2 trial requires separate Owner instruction.
- Any write-capable connector action is out of scope.

## 8. Read-Only First Principle

Every future connector interaction defaults to read-only. Write-capable behavior is never the starting point of a trial.

## 9. Single-Connector Only Principle

Future trial phases (v0.9.5-B onward) must scope to exactly one connector at a time. No multi-connector trial batching.

## 10. Single-Purpose Only Principle

Each connector trial phase covers exactly one narrow purpose (e.g. one metadata field, one preview surface). No bundling of unrelated capabilities into one phase.

## 11. Synthetic-to-Real Boundary Explicit Principle

Synthetic/mock context and fixtures used in v0.9-A through v0.9-R remain clearly separated from any future real connector data. A phase touching real connector data must say so explicitly in its title and doc; nothing in this plan authorizes that transition.

## 12. Owner Approval Required for Every Connector Scope

No connector scope (which connector, which account, which resource) may be assumed carried-over from a prior phase. Each new scope requires explicit Owner approval.

## 13. Owner Approval Required for Every Connector Action

No connector action (read, preview, write) may be assumed authorized by a prior approval. Each action requires its own explicit Owner approval.

## 14. Ambiguous Permission Must Fail Closed

If it is unclear whether an action is permitted under the current phase's authorization, the default behavior is to refuse / stop and report — never to proceed.

## 15. No Write By Default

- no send
- no delete
- no archive
- no label
- no calendar create/update/delete
- no Drive write
- no Sheets write
- no GitHub write
- no Slack send
- no external side effects

## 16. Forbidden Connector Actions (this phase and until explicitly authorized)

- send email
- create draft
- send draft
- forward email
- archive email
- delete email
- apply Gmail label
- bulk label matching emails
- create calendar event
- update calendar event
- delete calendar event
- respond calendar invitation
- write Google Drive
- write Google Sheets
- write Slack
- write GitHub issue / PR / commit

## 17. Forbidden Runtime Actions (this phase)

- connector call
- connector metadata read
- connector content read
- connector write
- Dashboard modification
- POST/form/button/action URL/control
- Hermes runtime activation
- Hermes memory read
- Hermes tool call
- Blackboard write
- queue write
- audit trail write
- automatic follow-up task creation
- Worker call
- OpenClaw call
- Google Sheets touch
- route / endpoint / webhook / connector runtime
- secrets read
- production/shared DB
- Remote Blackboard API runtime

## 18. Required Future Sequence

1. v0.9.5-B Limited Connector Trial Scope Selection
2. v0.9.5-C Single Connector Read-only Metadata Preview
3. v0.9.5-D Connector Trial Dashboard Read-only View
4. v0.9.5-E Connector Content Preview Gate (optional)
5. v0.9.5-R Limited Connector Trial Closeout

## 19. Safety Reminders

- Connector boundary plan is not connector activation.
- Connector read is not connector write.
- Connector preview is not external side effect permission.
- Hermes advice is not Owner approval.
- Hermes readback is not automatic follow-up execution.
- OpenClaw command envelope is not OpenClaw call.
- Mock gateway is not production gateway.

## 20. Required Safety Statements

- No connector call is performed in this phase.
- No connector metadata read is performed in this phase.
- No connector content read is performed in this phase.
- No connector write is performed in this phase.
- No external side effects are performed in this phase.
- Owner approval is required for every connector scope.
- Owner approval is required for every connector action.
- Ambiguous permission must fail closed.
- No Dashboard controls, POST, form, button, or action URL are added in this phase.
- No Hermes runtime activation occurs in this phase.
- No Worker call occurs in this phase.
- No OpenClaw call occurs in this phase.
- No Blackboard write occurs in this phase.
- No queue write occurs in this phase.
- No audit trail write occurs in this phase.
- No production/shared DB or Remote Blackboard API runtime is created in this phase.
