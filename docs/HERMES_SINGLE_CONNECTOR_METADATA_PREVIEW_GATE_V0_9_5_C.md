# v0.9.5-C Single Connector Read-only Metadata Preview Gate

## 1. Phase Title

v0.9.5-C Single Connector Read-only Metadata Preview Gate

## 2. Baseline

v0.9.5-B completed, pushed, verified, closed.

```text
HEAD = e6b45ed25b54acbea0931c81b835b69d8fd2babf
commit = docs: add v0.9.5 connector trial scope selection plan
```

## 3. Purpose

Define the gate and Owner scope intake template required before any future L1 Single Connector Read-only Metadata Preview.

## 4. Phase Classification

L0 documentation-only / check-only gate.

## 5. Binding Ruling

- v0.9.5-C gate does not authorize actual connector selection.
- v0.9.5-C gate does not authorize connector call.
- v0.9.5-C gate does not authorize connector metadata read.
- v0.9.5-C gate does not authorize connector content read.
- v0.9.5-C gate does not authorize connector write.
- v0.9.5-C gate does not authorize Dashboard implementation.
- Any actual L1 metadata preview requires separate Owner instruction with explicit connector scope.

## 6. Required Owner Scope Packet for Any Future L1 Metadata Preview

- connector name
- exact allowed operation
- read-only metadata only statement
- explicit no-content-read statement
- data scope
- time range
- max result count
- allowed metadata fields
- forbidden metadata fields
- private content exclusion
- expected output format
- stop condition
- rollback note
- audit note
- safety classification
- Owner approval statement

## 7. Allowed Future L1 Metadata Categories

- non-content identifier or redacted identifier
- timestamp/date metadata
- sender/owner/source metadata where explicitly approved
- title/subject/name metadata where explicitly approved
- size/count/status metadata where explicitly approved
- link/reference metadata only if non-secret and explicitly approved

## 8. Forbidden Metadata/Content Categories

- message body
- email body
- file content
- calendar description
- attachment content
- private notes
- secrets
- tokens
- passwords
- webhook URLs
- spreadsheet IDs unless explicitly synthetic/redacted
- production endpoint URLs
- full private payloads
- private connector content
- any field not explicitly approved by Owner

## 9. Output Rules for Future Metadata Preview

- max result count must be enforced
- output must be minimal
- private content must be excluded
- secrets must be redacted
- no payload persistence in repo
- no queue write
- no audit trail write
- no Blackboard write
- no external write

## 10. Fail-Closed Rules

- Missing connector name = HOLD.
- Missing operation = HOLD.
- Missing data scope = HOLD.
- Missing max result count = HOLD.
- Missing allowed metadata fields = HOLD.
- Missing no-content-read statement = HOLD.
- Any write-capable action = HOLD.
- Any ambiguous permission = HOLD.
- Any private content request without later L2 authorization = HOLD.

## 11. Future Sequence

- After this gate, Owner may provide an explicit scope packet.
- Only after explicit Owner scope approval may a separate later phase attempt L1 metadata preview.
- v0.9.5-D Connector Trial Dashboard Read-only View remains not started.
- v0.9.5-E Connector Content Preview Gate remains optional and not authorized.
- v0.9.5-R Limited Connector Trial Closeout remains future.

## 12. Explicit Non-Goals

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

## 13. Safety Reminders

- Metadata preview gate is not metadata preview.
- Scope packet is not connector activation.
- Connector read is not connector write.
- Connector preview is not external side effect permission.
- Owner scope approval is not Worker dispatch.
- Hermes advice is not Owner approval.
- Decision event is not dispatch.

## 14. Required Safety Statements

- v0.9.5-C gate is L0 documentation-only / check-only.
- This gate does not authorize actual connector selection.
- This gate does not authorize connector call.
- This gate does not authorize connector metadata read.
- This gate does not authorize connector content read.
- This gate does not authorize connector write.
- Actual L1 metadata preview requires separate Owner instruction.
- No Dashboard controls, POST, form, button, or action URL are added in this phase.
- No Hermes runtime activation occurs in this phase.
- No Worker call occurs in this phase.
- No OpenClaw call occurs in this phase.
- No Blackboard write occurs in this phase.
- No queue write occurs in this phase.
- No audit trail write occurs in this phase.
- No production/shared DB or Remote Blackboard API runtime is created in this phase.
