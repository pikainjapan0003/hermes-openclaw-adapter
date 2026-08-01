# Phase 9 N=1 Preflight Condition Catalog

> **Historical catalog wording.** The latest additive summary is
> `PREFLIGHT_CONDITION_CATALOG_V2.md`; the authoritative execution boundary
> remains `../09_N1_PREFLIGHT_RUNBOOK.md`. This file does not unlock any gate.

Status: **READ-ONLY CATALOG — BLOCKED, NOT AUTHORIZED**

Source of executable truth: `tests/test_n1_preflight_dryrun.py`. The preflight
uses all-of semantics: all twelve conditions must be true in the same authorized
session. Tests exhaust all 4,095 non-all-green combinations and prove they remain
BLOCKED. This catalog cannot change a value or supply evidence.

| # | Condition | Current value | Why READY/BLOCKED now | What would be required to become/remain green | Owner gate? |
|---:|---|---|---|---|---|
| 1 | `blackboard_contract` | **PASS / READY prerequisite** | The checked approval-packet fixture validates against the current closed contract. | Keep Phase 3/4 schemas, fixture, validator, and negative tests green at the exact future checkout. Any schema drift must be reviewed before the session. | No new Owner act while unchanged; a schema change is separately governed. |
| 2 | `approval_exact_target` | **PASS / READY prerequisite** | The packet carries a non-empty exact target for the synthetic N=1 query. | Rebuild/inspect the future packet for the one approved query and prove target IDs/action match its dry-run evidence. | Owner must approve the eventual exact query scope, but this static field check is not itself an Owner-only action. |
| 3 | `dry_run_result_refs` | **PASS / READY prerequisite** | All checked `dry_run_evidence` references are non-empty in the fixture. | At the future checkpoint, prove dry-run/result/command/task references link to the same inspected N=1 chain. | No new act for static checking; Owner approval of the actual packet remains separate. |
| 4 | `evidence_hash` | **PASS / READY prerequisite** | The stored synthetic evidence hash recomputes successfully. | Recompute independently from the exact future evidence; any mutation or mismatch blocks the session. | No; verification is mechanical. It grants no execution permission. |
| 5 | `expected_side_effects_empty` | **PASS / READY prerequisite** | The N=1 evidence lists no expected side effects. | The future packet/evidence must still specify an empty list and the target must remain a harmless read-only query. | Owner confirms the eventual exact scope; no model may redefine a side effect as harmless. |
| 6 | `token_schema_allows_live_token` | **FAIL / BLOCK** | Phase 4 schema locks `single_use_execution_token` to `null`. | A separately designed and Owner-authorized Phase 9 token/gate contract, schemas/fixtures/tests, adversarial review, and explicit replacement of the null-only phase boundary. | **Yes. Only Owner can authorize the contract change; night batches cannot.** |
| 7 | `packet_contains_live_token` | **FAIL / BLOCK** | The valid packet contains `null`, as required by the current schema. | Only after condition 6 is legitimately changed: issue one fresh, exact-scope, expiring/single-use token through the separately approved gate for the Owner-present session. | **Yes. Night work cannot mint, insert, simulate as real, or reuse a token.** |
| 8 | `phase7_writer_exists` | **FAIL / BLOCK** | `app/audit_writer_local.py` does not exist; Phase 7 persistence is intentionally absent. | Owner must provide the exact Phase 7 instruction in an implementation turn; implement only the reviewed local append-only writer package; adversarial review; Owner inspects the resulting local audit file and signs off. | **Yes. Exact instruction required: `允許寫入 data/audit_dev.jsonl（local dev append-only）`. Quoting it here is not authorization.** |
| 9 | `phase9_gate_exists` | **FAIL / BLOCK** | `app/n1_execution_gate.py` does not exist and no execution gate is authorized. | After Phase 7 closeout and separate Phase 9 design approval, implement and review an all-of, single-use, exact-scope gate with no approval→dispatch shortcut. | **Yes. Separate Owner instruction after Phase 7; never a nightly-batch inference.** |
| 10 | `owner_synchronously_present` | **FAIL / BLOCK** | A repository test cannot establish a human's live presence; current rehearsal is offline. | Owner deliberately schedules and remains present for the exact N=1 session and confirms readiness at the live checkpoint. | **Yes; only the Owner can supply presence.** |
| 11 | `fresh_owner_token_supplied` | **FAIL / BLOCK** | No token exists and the present contract forbids one. | Conditions 6/9 must be completed first; Owner then supplies/approves the fresh exact token through the governed mechanism in that session. | **Yes; cannot be prefilled by docs, fixtures, tests, Fable 5, or Codex.** |
| 12 | `runtime_rehearsal_authorized` | **FAIL / BLOCK** | All existing chains are mock/in-memory/read-only; no real OpenClaw call is authorized. | Owner issues the exact harmless-query authorization only after conditions 1–11 are independently verified at the same checkpoint. | **Yes. It is the final live authorization, not implied by earlier green checks.** |

## Who can move what

- Tests/reviewers may only re-measure conditions 1–5 and report drift.
- Phase 7 implementation can occur only after the new exact Owner instruction;
  it cannot be initiated by this catalog or a nightly batch.
- Token schema, token issuance, and the Phase 9 gate require separate Owner-
  governed design and implementation packages after Phase 7.
- Conditions 10–12 exist only in a synchronous Owner-present session. No
  repository artifact can pre-satisfy them.

## Fail-closed reading

1. A PASS is evidence for one prerequisite, not permission.
2. Seven current FAIL values are deliberate safety gates, not defects for a
   night batch to repair.
3. One green condition cannot compensate for another red condition.
4. A test-memory all-green counterfactual proves Boolean semantics only; it is
   not a token, Owner presence, writer, gate, or runtime authorization.
5. Until all twelve are independently true in the authorized live checkpoint,
   the only valid final result is `FINAL | BLOCKED`.
