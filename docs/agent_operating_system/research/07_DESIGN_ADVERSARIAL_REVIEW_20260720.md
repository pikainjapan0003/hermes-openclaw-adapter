# Phase 7 Design Fresh-Context Adversarial Review — 2026-07-20

Review target: `docs/agent_operating_system/07_AUDIT_WRITE_DESIGN.md` at
`777aa8c`. Review posture: fresh-context, fail-closed, findings only.

This review does not authorize implementation, persistence, creation of
`data/audit_dev.jsonl`, audit append, rollback execution, dispatch, runtime wiring, or
any other write path. No design or product file was changed as part of this review.

## 1. Conclusion

No P0 or P1 defect was found. The design keeps its authorization boundary explicit at
lines 3–7, 27–28, and 277–287, and the current implementation surface contains only the
pure in-memory hash-chain helper and pure rollback-preview builder. Four P2/P3
documentation-to-implementation drifts remain. They do not create a current write or
execution path, but they should be resolved in a separately authorized design revision
before a future audit-writer implementation is reviewed.

The persistent-writer portion remains **HOLD**: no audit writer exists, the exact Owner
authorization is absent from this batch, and checklist items that require real writer
code cannot be answered affirmatively.

## 2. Findings summary

| ID | Severity | Finding | Primary evidence |
|---|---|---|---|
| F-01 | P2 | The global input allowlist omits `result_message`, while the approved rollback-preview contract and implementation require it. | Design lines 30–37 vs. 195–197; `app/rollback_preview_builder.py` lines 66–70 |
| F-02 | P3 | Lifecycle wording still describes the rollback builder as current/future work even though the pure builder already exists. | Design lines 193 and 263–269; builder lines 1 and 66–175 |
| F-03 | P3 | `prev_entry_hash: null` is tied to “before hash-chain implementation,” but canonicalization and in-memory chain verification already exist. | Design line 207; `app/hash_chain.py` lines 46–93 |
| F-04 | P3 | “Validated inputs” is a caller precondition, not a property enforced by the rollback builder itself. | Design lines 93–107 and 195–197; builder lines 73–150 |

## 3. Detailed findings

### F-01 — P2 — Existing-contract input allowlist conflicts with the rollback contract

The design says that a future implementation may consume only four sources, listing
the audit-event schema, rollback-event schema, evidence bundle, and corresponding
fixture or builder output (lines 30–37). It does not list the result-message contract.
The later, Owner-adjudicated rollback section requires three validated inputs, including
`result_message` (lines 195–197), and the implemented function accepts that third input
at `app/rollback_preview_builder.py` lines 66–70.

A literal weak-model implementation of the earlier “only” allowlist could reject the
approved builder interface, while an implementation following section 6 must violate
the earlier wording. This is a normative contradiction, not merely stale status text.
It does not create a write path today, but the global allowlist should be reconciled
before an audit writer package relies on it.

### F-02 — P3 — Rollback-builder lifecycle text is stale

The section heading states that implementation occurs in the current batch (line 193),
while the proposed future implementation boundaries still say that a later package may
add `app/rollback_preview_builder.py` (lines 263–269). That module already exists and is
a pure three-input builder (`app/rollback_preview_builder.py` lines 1 and 66–175).

The top-level document status still clearly says planning only and not authorized, so
the stale wording does not grant audit-write authority. It can nevertheless cause a
fresh implementer to recreate or replace reviewed code, or to conflate the already
implemented non-writing half with the still-forbidden writer half.

### F-03 — P3 — The `prev_entry_hash` boundary names the wrong unfinished component

The rollback field table fixes `prev_entry_hash` to null “before §4 hash-chain
implementation” (line 207). Canonical JSON, complete-event SHA-256, genesis handling,
and in-memory link verification are already implemented in `app/hash_chain.py` lines
46–93. What remains unimplemented and unauthorized is file-backed verification and
persistence, not the entire section 4 hash-chain rule.

The current builder correctly returns null at line 157, and the behavior is safe. The
risk is specification drift: a future reviewer may think the null constraint expires
merely because the pure hash helper exists, or may incorrectly conclude that the
canonicalization work is still absent. A later design revision should name the precise
gate without changing the current constant in this review package.

### F-04 — P3 — Full schema validation remains external to the rollback builder

The design declares that canonicalization receives an object that already passed the
audit schema (lines 93–107) and that the rollback builder accepts three validated
inputs (lines 195–197). The builder enforces the N=1 safety-critical subset at lines
73–150 and verifies the evidence hash, but it does not itself invoke the three complete
schemas. This is consistent with a caller-precondition architecture, yet the phrase
“validated inputs” can be misread as a guarantee produced by the builder.

There is no current persistence or execution consequence because the builder is pure
and returns preview-only data. Before a writer is authorized, its call graph must show
where complete schema validation happens and must not rely on the rollback builder's
partial checks as a substitute.

## 4. Section 10 adversarial checklist

| # | Result | Evidence and assessment |
|---:|---|---|
| 1 | HOLD | No writer exists. The design limits the future target at lines 19 and 39–41, but no code can yet prove that it is the only possible target. |
| 2 | HOLD | No writer/path-resolution code exists, so argument, environment, symlink, traversal, import-hook, and test-override resistance cannot be tested. |
| 3 | PASS for current code | `app/hash_chain.py` lines 1–5 and `app/rollback_preview_builder.py` lines 1–8 show pure imports; their bodies contain no filesystem, queue, network, runtime, or persistence call. |
| 4 | HOLD | Full physical-chain verification before append is specified at design lines 160–177 and 302–304 but has no writer implementation. |
| 5 | PASS for implemented in-memory domain | Design lines 91–134 align with `app/hash_chain.py` lines 20–66: exact dict/list domain, float rejection, NFC checks, sorted keys, UTF-8, compact separators, and no trailing LF. Duplicate-key rejection is explicitly assigned to a future decoder at design lines 103–107. |
| 6 | PASS | Design lines 138–145 align with `app/hash_chain.py` lines 69–72: the complete event, including `prev_entry_hash`, is hashed; canonical bytes contain no physical LF. |
| 7 | PASS for in-memory verifier | Design lines 153–158 align with `app/hash_chain.py` lines 75–93: null is expected only at index zero and later links must equal the preceding event hash. |
| 8 | HOLD | No append operation or concurrency control exists. Partial-write and race behavior cannot be assessed. |
| 9 | HOLD | Existing tests exercise in-memory records, not a physical audit file; the design itself requires physical tamper tests at lines 298–304. |
| 10 | PASS | Design lines 179–189 explicitly deny clean-suffix-truncation detection without a trusted external tail or count. The in-memory verifier makes no stronger claim. |
| 11 | PASS for current code | The current hash and rollback modules expose no enqueue, dispatch, execution, OpenClaw, Hermes, connector, task-state, or permission-grant path. Audit success cannot be assessed because no writer exists. |
| 12 | PASS | Design lines 241–243 and builder lines 66–175 keep rollback output descriptive; the module imports only typing support and evidence-hash verification and supplies no executable command. |
| 13 | PASS | The reviewed implementation surface adds no route, dashboard control, token, runtime, remote, production, queue, or Blackboard write path. |
| 14 | HOLD | There is no active Owner-authorized writer diff to compare. This review package itself changes only this research document. |
| 15 | HOLD | The active NIGHT-BATCH-6 request explicitly forbids audit writing and does not contain the exact sentence required at design line 282. |

## 5. Hidden preview-to-write path review

No hidden preview-to-write path was found. The rollback builder returns a plain
dictionary, fixes `preview_only` true and `rollback_path` null, and imports no executor
or runtime (`app/rollback_preview_builder.py` lines 152–175). The hash-chain module
operates only on in-memory mappings and sequences (`app/hash_chain.py` lines 46–93).
Repository search found no `app/audit_writer_local.py` and no implemented reference to
`data/audit_dev.jsonl` under `app/`.

The remaining risk is future integration ambiguity rather than present capability:
section 5 uses present-tense file-verifier language (design lines 160–177), while the
only verifier currently present is in-memory. A future implementation review must not
infer that physical decode, duplicate-key rejection, path confinement, final-LF rules,
or atomic append already exist.

## 6. Required disposition before writer implementation

This review does not fix the findings. Before a separately authorized audit-writer
package begins, a reviewed design revision should:

1. reconcile the section 2 input allowlist with the three-input rollback contract;
2. distinguish already-implemented pure helpers from still-unimplemented persistence;
3. replace the ambiguous hash-chain timing phrase with the actual persistence gate; and
4. identify the exact layer that performs complete schema validation before any append.

Until then, the exact Owner authorization gate and every writer-dependent HOLD result
above remain in force.
