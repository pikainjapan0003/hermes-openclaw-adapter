# v0.9.5-D Connector Trial Dashboard Read-only View Boundary Plan

## 1. Phase Title

v0.9.5-D Connector Trial Dashboard Read-only View Boundary Plan

## 2. Baseline

v0.9.5-C completed, pushed, verified, closed.

```text
HEAD = 4e41a037648f4099774124bd191f2473d1bf4c36
commit = docs: add v0.9.5 connector metadata preview gate
```

## 3. Purpose

Define the future Dashboard read-only display boundary for a later Owner-approved connector metadata preview.

## 4. Phase Classification

L0 documentation-only / check-only boundary plan.

## 5. Binding Ruling

- v0.9.5-D does not implement Dashboard UI.
- v0.9.5-D does not modify app/main.py.
- v0.9.5-D does not modify templates/system.html.
- v0.9.5-D does not modify static/dashboard.css.
- v0.9.5-D does not add routes, endpoints, POST, forms, buttons, action URLs, or controls.
- v0.9.5-D does not authorize connector selection.
- v0.9.5-D does not authorize connector call.
- v0.9.5-D does not authorize connector metadata read.
- v0.9.5-D does not authorize connector content read.
- v0.9.5-D does not authorize connector write.
- Any actual Dashboard read-only connector metadata preview requires separate Owner instruction after explicit connector scope approval.

## 6. Future Dashboard Display Principles

- Dashboard may only display approved metadata fields.
- Dashboard must display connector disabled / read-only / no-write safety state.
- Dashboard must display Owner Review required.
- Dashboard must display max result count.
- Dashboard must display no-content-read status.
- Dashboard must display redaction status.
- Dashboard must display that preview is not execution permission.
- Dashboard must display that connector read is not connector write.
- Dashboard must display that connector preview is not external side effect permission.

## 7. Future Allowed Display Categories (only if separately approved)

- connector name
- scope summary
- exact allowed operation
- read-only metadata-only status
- time range
- max result count
- approved metadata field names
- redacted sample values
- safety flags
- stop condition
- audit note
- rollback note

## 8. Future Forbidden Display Categories

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
- full spreadsheet IDs unless synthetic/redacted and explicitly approved
- production endpoint URLs
- full private payloads
- private connector content
- any unapproved metadata field
- any raw connector response

## 9. Future Forbidden Controls

- approve button
- reject button
- execute button
- dispatch button
- send button
- archive button
- delete button
- label button
- create draft button
- forward button
- calendar create/update/delete controls
- Drive write controls
- Sheets write controls
- Slack send controls
- GitHub write controls
- any POST/form/button/action URL/control

## 10. Read-Only Rendering Rules

- render only from an approved preview artifact or approved in-memory safe preview
- never render raw connector payloads
- never persist private connector payloads in repo
- never write queue
- never write audit trail
- never write Blackboard
- never trigger Worker
- never call OpenClaw
- never activate Hermes runtime
- never perform external side effects

## 11. Required Labels for Future UI

- CONNECTOR DISABLED unless explicitly enabled by Owner
- READ ONLY
- METADATA ONLY
- NO CONTENT READ
- NO WRITE
- NO EXTERNAL SIDE EFFECTS
- OWNER REVIEW REQUIRED
- PREVIEW IS NOT EXECUTION PERMISSION
- CONNECTOR READ IS NOT CONNECTOR WRITE

## 12. Fail-Closed Rules

- Missing Owner scope packet = HOLD.
- Missing connector name = HOLD.
- Missing exact operation = HOLD.
- Missing max result count = HOLD.
- Missing allowed metadata fields = HOLD.
- Missing no-content-read statement = HOLD.
- Any raw content field = HOLD.
- Any write-capable action = HOLD.
- Any Dashboard control = HOLD.
- Any POST/form/button/action URL = HOLD.
- Any ambiguous permission = HOLD.

## 13. Future Sequence

- Owner must first provide explicit connector scope packet.
- A later separate phase may perform a limited L1 metadata preview only if Owner explicitly approves.
- A later separate phase may implement Dashboard read-only display only after safe metadata preview exists.
- v0.9.5-E Connector Content Preview Gate remains optional and not authorized.
- v0.9.5-R Limited Connector Trial Closeout remains future.

## 14. Explicit Non-Goals

- no Dashboard implementation
- no Dashboard file modification
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

- Dashboard view boundary is not Dashboard implementation.
- Dashboard display is not execution permission.
- Connector preview is not connector activation.
- Connector read is not connector write.
- Connector preview is not external side effect permission.
- Owner scope approval is not Worker dispatch.
- Hermes advice is not Owner approval.
- Decision event is not dispatch.

## 16. Required Safety Statements

- v0.9.5-D is L0 documentation-only / check-only.
- v0.9.5-D does not implement Dashboard UI.
- v0.9.5-D does not modify app/main.py.
- v0.9.5-D does not modify templates/system.html.
- v0.9.5-D does not modify static/dashboard.css.
- No routes / endpoints / POST / forms / buttons / action URLs / controls are added in this phase.
- No connector selection occurs in this phase.
- No connector call occurs in this phase.
- No connector metadata read occurs in this phase.
- No connector content read occurs in this phase.
- No connector write occurs in this phase.
- No Hermes runtime activation occurs in this phase.
- No Worker call occurs in this phase.
- No OpenClaw call occurs in this phase.
- No Blackboard write occurs in this phase.
- No queue write occurs in this phase.
- No audit trail write occurs in this phase.
- No production/shared DB or Remote Blackboard API runtime is created in this phase.
