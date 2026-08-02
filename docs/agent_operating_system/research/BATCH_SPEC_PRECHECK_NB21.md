# NIGHT-BATCH-21 contract field precheck

Date: 2026-08-04

Scope: NIGHT-BATCH-21 packages that name fields from a machine contract.
Method: inspect the repository schemas first, then corroborate with a tracked valid fixture. Line numbers below are the evidence available at batch start (`7cd2d98`). This record is evidence for dispatch only; it changes no schema, validator, or runtime behavior.

## Result

No package in this batch names a contract field that is absent from the cited schema. Package 8 may proceed because all three named evidence-bundle objects exist. Packages 1 and 2 remain proposal-only because the inspection confirms the semantic gaps described in their briefs. No contract-related package is placed on HOLD by this precheck.

## Package-by-package evidence

| Package | Referenced field or shape | Schema evidence | Fixture evidence | Precheck decision |
|---|---|---|---|---|
| 1 | Blackboard `schema_version` is a non-empty string rather than a version allowlist | `docs/schemas/blackboard/approval_packet.schema.json:33-36` declares `type: string` and `minLength: 1`; the same common-field pattern is used by the ten Blackboard schemas | `fixtures/blackboard_contract/approval_packet.valid.json:2` supplies `"1.0"` | Proceed with proposal only; do not change schema or validator |
| 2 | Approval packet `task_id`, `execution_class`, `safety_flags` are top-level | `docs/schemas/blackboard/approval_packet.schema.json:12-19`, `:47-86`, `:95-97`, and `:121-124` | `fixtures/blackboard_contract/approval_packet.valid.json:5-24` and `:29` | Proceed with proposal only |
| 2 | Evidence bundle keeps `task_id` and `execution_class` under `.task`, and has no `safety_flags` property | `docs/schemas/evidence_bundle.json:8-20` is the closed top-level required list; `:22-26` starts its properties; `:26-37` defines `.task.task_id` and `.task.execution_class` | `fixtures/local_mock_data/n1_dry_run_evidence_bundle.json:6-12`; the complete fixture at `:1-61` contains no `safety_flags` | Proceed with proposal; do not invent a common shape |
| 8 | Evidence bundle has `.task`, `.command_envelope`, and `.mock_result` objects | `docs/schemas/evidence_bundle.json:13-15` requires all three; definitions are `:26-38`, `:39-70`, and `:71-133` | `fixtures/local_mock_data/n1_dry_run_evidence_bundle.json:6-12`, `:14-27`, and `:28-54` | Proceed with nested-structure mutation tests |
| 8 | Correlation fields used inside the three objects exist | `.task.task_id` at `docs/schemas/evidence_bundle.json:31`; `.command_envelope.task_id` and `.command_envelope.command_id` at `:57-58`; `.mock_result.gateway_response.command_id/task_id` at `:126-127` | `fixtures/local_mock_data/n1_dry_run_evidence_bundle.json:7`, `:15-16`, and `:49-50` | Proceed; mutations must target actual fields only |
| 10 | Three-source report has `verdict` and `sources.local/github/replit` | `docs/schemas/three_source_report.schema.json:8-20` and `:21-68` | The tool constructs the same closed shape in `scripts/check_three_source_readonly.py`; schema is the authority | Proceed with tests; no new report fields |
| 10 | Replit version knowledge is explicitly null/unknown/false | `docs/schemas/three_source_report.schema.json:39-64` | `scripts/check_three_source_readonly.py:172` constructs `deployed_hash_status: UNKNOWN` alongside the closed Replit status object | Proceed; detached/shallow/remote-name cases must still validate this existing shape |

## Packages reviewed but not field-bearing

- Package 5 discusses the renderer's display convention; it does not introduce a schema field.
- Package 11 checks mirror classification states (`SAME`, `BEHIND`, `AHEAD`, `DIFFERS`), which are a tool return contract rather than a JSON schema field list.
- Package 12 audits output leakage without adding or renaming fields.
- Package 18 extends the artifact inventory and does not change any artifact's data contract.

## L-008/F8 handoff

Any later discovery that a package needs an uncited field is a dispatch-spec defect. The affected package must be marked HOLD rather than repaired by inventing a field, weakening validation, or editing a schema outside its explicit authorization.
