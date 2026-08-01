# Phase 9 N=1 Preflight Condition Catalog v2

**PLANNING ONLY, NOT AUTHORIZED.** This is a read-only catalogue of the
current Phase 9 preflight. It does not issue a token, change a schema, create
an audit writer, start a runtime, call OpenClaw, or grant execution permission.

## Source of truth and evaluation rule

The executable read-only check is
`tests/test_n1_preflight_dryrun.py::evaluate_preflight`. The runbook is
`docs/agent_operating_system/09_N1_PREFLIGHT_RUNBOOK.md`. A session is READY
only when every condition is true in the same separately authorised,
Owner-present session. Any false condition makes the final result
`FINAL | BLOCKED`; a green rehearsal or counterfactual does not unlock a
runtime path.

## Current catalogue

| # | Condition (test name) | Current state | Evidence / source | What a future change would require | Owner gate? |
|---:|---|---|---|---|---|
| 1 | `blackboard_contract` | PASS prerequisite | Approval-packet fixture is selected and validates through `validate_blackboard_message`. | Revalidate the exact frozen checkout, fixtures, schemas, and negative tests before the session. | No new act while unchanged; schema changes remain separately governed. |
| 2 | `approval_exact_target` | PASS prerequisite | The packet has a non-empty `exact_target` object. | Inspect the future packet and prove its target and action are the one approved query. | The eventual exact scope is an Owner decision. |
| 3 | `dry_run_result_refs` | PASS prerequisite | All values in `approval_packet.dry_run_evidence` are non-empty. | Recheck that task, command, dry-run, and result references identify one chain. | The actual packet still requires Owner approval. |
| 4 | `evidence_hash` | PASS prerequisite | The local evidence fixture passes `verify_bundle_hash`. | Recompute the hash independently from the frozen future evidence; mismatch blocks. | No; this is mechanical evidence only. |
| 5 | `expected_side_effects_empty` | PASS prerequisite | The evidence fixture has an empty `expected_side_effects` list. | Keep the action a harmless read-only query and verify the list is still empty. | Owner confirms the exact scope; no model may redefine a side effect as harmless. |
| 6 | `token_schema_allows_live_token` | FAIL / BLOCKED | `approval_packet.schema.json` requires `single_use_execution_token` to be `null`. | A separately designed, reviewed, and explicitly Owner-authorised Phase 9 token contract must replace the null-only boundary. | **Yes. Night batches cannot alter this.** |
| 7 | `packet_contains_live_token` | FAIL / BLOCKED | The valid packet contains `single_use_execution_token: null`. | Only after condition 6 is legitimately changed may a fresh exact-scope single-use token be supplied by the Owner in-session. | **Yes. No fixture or test may simulate one as live.** |
| 8 | `phase7_writer_exists` | FAIL / BLOCKED | `app/audit_writer_local.py` is absent by design. | A separately instructed Phase 7 implementation, review, local append-only inspection, and Owner sign-off are required. | **Yes. The exact Owner instruction is a separate gate.** |
| 9 | `phase9_gate_exists` | FAIL / BLOCKED | `app/n1_execution_gate.py` is absent and no execution gate is authorised. | After Phase 7 closeout, a separately designed all-of, exact-scope, single-use gate must be reviewed and authorised. | **Yes.** |
| 10 | `owner_synchronously_present` | FAIL / BLOCKED | Repository tests cannot establish live human presence; the rehearsal is offline. | The Owner must remain present for the exact live checkpoint and confirm the displayed action. | **Yes.** |
| 11 | `fresh_owner_token_supplied` | FAIL / BLOCKED | No token exists and the current contract forbids one. | Conditions 6 and 9 must be complete; the Owner then supplies a fresh, expiring, exact-scope token through the governed mechanism. | **Yes.** |
| 12 | `runtime_rehearsal_authorized` | FAIL / BLOCKED | Existing chains are mock/in-memory/read-only; no real OpenClaw call is authorised. | Only the Owner may issue the final harmless-query authorization after conditions 1–11 are independently checked. | **Yes.** |

## Required evidence ordering

The future session must freeze and revalidate the contract records before any
Owner checkpoint. The order is: task/command/result references, evidence hash,
approval packet and exact target, audit preview and rollback preview, then the
Owner's live decision and separately governed token/gate. A later check cannot
repair an earlier failure, and no document, fixture, test, or preflight report
can satisfy conditions 6–12 by itself.

## Fail-closed interpretation

1. PASS means only that one prerequisite was measured; it is not permission.
2. The current FAIL values are intentional safety gates, not night-batch bugs.
3. The all-green test-memory counterfactual proves Boolean AND semantics only.
4. A preflight report must not be parsed as dispatch input or imported by a
   runtime component.
5. Until all twelve conditions are true in the authorised live checkpoint, the
   only valid outcome is `FINAL | BLOCKED`.

## Change-control note

Any future edit to this catalogue must be accompanied by an update to the
executable condition names and a fresh review against the runbook and Phase 9
status. This document cannot authorize Phase 7, Phase 9, v1.1, or any remote
operation.
