# v0.9.5-B Limited Connector Trial Scope Selection

## 1. Phase Title

v0.9.5-B Limited Connector Trial Scope Selection

## 2. Baseline

v0.9.5-A completed, pushed, verified, closed.

```text
HEAD = 404cdfe9edef92cabb2f2d8b5181ff4549d259d1
commit = docs: add v0.9.5 limited connector trial boundary plan
```

## 3. Purpose

Define the Owner-required scope selection contract for any future Limited Connector Trial.

## 4. Phase Classification

L0 documentation-only / check-only.

## 5. Binding Ruling

- v0.9.5-B does not authorize connector execution.
- v0.9.5-B does not authorize L1 metadata preview.
- v0.9.5-B does not authorize L2 content preview.
- v0.9.5-B only defines the scope fields that Owner must explicitly approve before v0.9.5-C.

## 6. Required Owner-Specified Fields for Any Future Connector Trial

- connector name
- exact allowed operation
- read-only vs write-capable classification
- data scope
- time range
- max result count
- whether private content may be read
- whether only metadata may be read
- forbidden actions
- expected output format
- stop condition
- rollback note
- audit note
- safety classification
- Owner approval statement

## 7. Connector-Name Rule

This phase may define the required field "connector name", but must not select the actual connector.

## 8. Operation Rule

The exact allowed operation must be single-purpose and explicit. Ambiguous operations fail closed.

## 9. Read-Only Rule

- Read-only metadata preview may only be authorized in v0.9.5-C or later by separate Owner instruction.
- Content preview may only be authorized in v0.9.5-E or later by separate Owner instruction.
- Write-capable actions remain out of scope by default.

## 10. Data-Scope Rule

Scope must be narrow, time-bounded, and max-result bounded.

## 11. Private-Content Rule

Private content is forbidden unless a later Owner instruction explicitly allows L2 content preview.

## 12. Forbidden-by-Default Actions

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
- any external side effect

## 13. Future Sequence

1. v0.9.5-C Single Connector Read-only Metadata Preview
2. v0.9.5-D Connector Trial Dashboard Read-only View
3. v0.9.5-E Connector Content Preview Gate (optional)
4. v0.9.5-R Limited Connector Trial Closeout

## 14. Explicit Non-Goals

- no connector selected
- no connector called
- no connector metadata read
- no connector content read
- no connector write
- no Dashboard change
- no POST/form/button/action URL/control
- no Hermes runtime activation
- no Worker call
- no OpenClaw call
- no Blackboard write
- no queue write
- no audit trail write
- no production/shared DB
- no Remote Blackboard API runtime
- no external side effects

## 15. Safety Reminders

- Scope selection is not connector activation.
- Connector read is not connector write.
- Connector preview is not external side effect permission.
- Hermes advice is not Owner approval.
- Owner approval for scope is not Worker dispatch.
- Decision event is not dispatch.

## 16. Required Safety Statements

- v0.9.5-B is L0 documentation-only / check-only.
- v0.9.5-B does not authorize connector execution.
- v0.9.5-B does not authorize L1 metadata preview.
- v0.9.5-B does not authorize L2 content preview.
- This phase must not select the actual connector.
- Ambiguous operations fail closed.
- Read-only metadata preview requires later Owner instruction.
- Content preview requires later Owner instruction.
- Write-capable actions remain out of scope by default.
- No Dashboard controls, POST, form, button, or action URL are added in this phase.
- No Hermes runtime activation occurs in this phase.
- No Worker call occurs in this phase.
- No OpenClaw call occurs in this phase.
- No Blackboard write occurs in this phase.
- No queue write occurs in this phase.
- No audit trail write occurs in this phase.
- No production/shared DB or Remote Blackboard API runtime is created in this phase.
