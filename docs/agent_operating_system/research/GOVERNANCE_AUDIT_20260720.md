# Governance Cross-Consistency Audit — 2026-07-20

Status: **REVIEW ONLY — FINDINGS ARE NOT FIXES OR AUTHORIZATION**

## 1. Scope and method

Reviewed as one authority chain:

- `00_QUICK_DIAGNOSIS.md`
- `01_SAFETY_BOUNDARIES.md`
- `05_VERIFIED_LONG_TERM_PLAN.md`
- `07_AUDIT_WRITE_DESIGN.md`
- `09_N1_PREFLIGHT_RUNBOOK.md`
- `40_MAINTENANCE_PROTOCOL.md`
- repository `README.md`

The review looked for invalid paths, mutually incompatible rules, stale current-state
claims, and sentences a weak model could mistake for authority. Referenced paths and
the relevant current repository files were checked. Per the package instruction, no
finding was corrected in this commit.

Severity meaning: P0 permits immediate unsafe action; P1 can directly cause an
authorization/governance violation; P2 can materially misroute work or misstate a
safety boundary; P3 is stale or ambiguous but has a nearby correction.

## 2. Summary

| Severity | Count |
|---|---:|
| P0 | 0 |
| P1 | 1 |
| P2 | 5 |
| P3 | 4 |

No P0 was found. The Phase 7 design and Phase 9 runbook consistently state that the
audit writer, token, execution, and runtime paths remain unauthorized. The highest
risk is an unresolved disagreement over whether a successful night-batch review is
itself authority to merge and push.

## 3. Findings

### G-01 — P1 — Night-batch merge/push authority conflicts with both canonical authorization documents

Evidence:

- `05_VERIFIED_LONG_TERM_PLAN.md:467` says Fable 5 pass is followed directly by
  merge/push with no further Owner confirmation.
- `01_SAFETY_BOUNDARIES.md:71` says git commit/push do not accompany task authority
  and require an Owner instruction.
- `40_MAINTENANCE_PROTOCOL.md:10` says commit/push always require Owner instruction.
- `40_MAINTENANCE_PROTOCOL.md:74` repeats that commit occurs only when Owner directs it.

Impact: one model can treat review pass as sufficient external-write authority while
another must HOLD. Section 6 is newer than the old Phase text, but neither 01 nor 40
states that §6.13 is a scoped exception, and 01 declares itself the unique canonical
safety source. This can cause either an unauthorized push or a deadlocked release.

Decision needed: explicitly encode the night-batch exception in 01/40, or amend §6.13
to require the authorization form already required by 01/40.

### G-02 — P2 — README opening presents a real execution path as the present system

Evidence:

- `README.md:4` says the Adapter invokes OpenClaw CLI in the background and writes
  `results.jsonl`.
- `README.md:9-15` diagrams MCP dispatch, POST dispatch, OpenClaw CLI, and the result
  file without a historical label.
- `README.md:23` says there is no Worker dispatch, real OpenClaw call, Hermes runtime
  activation, connector call, or external side effect.
- `01_SAFETY_BOUNDARIES.md:40-47` keeps dispatch, real calls, runtime activation,
  connector access, and side effects separately forbidden.

Impact: the unlabelled project introduction appears before the “current state” caveat.
A weak model can cite it as an existing authorized architecture and route work toward
the live-looking POST/CLI path.

### G-03 — P2 — README current-state block is four completed phases behind

Evidence:

- `README.md:20-23` dates current state to 2026-07-07 and says development remains at
  v1.0-RC-R before v1.0 implementation.
- `README.md:28` says the next step is Phase 2 definition freeze.
- `05_VERIFIED_LONG_TERM_PLAN.md:286-290` records Phase 2 frozen and Phases 3–6
  complete on 2026-07-18/19.
- `05_VERIFIED_LONG_TERM_PLAN.md:292` records Phase 7 design prepared.

Impact: the repository's front door routes a new session to already completed work and
conceals the actual Phase 7/9 gates.

### G-04 — P2 — D-04 still names RC-R as the authoritative latest closeout

Evidence:

- `00_QUICK_DIAGNOSIS.md:90` says current state recognizes the plan plus the “latest
  closeout,” specifically RC-R.
- `README.md:27` instead declares the authority chain ending at the plan's §5 status
  table.
- `05_VERIFIED_LONG_TERM_PLAN.md:286-292` contains multiple post-RC-R completions and
  the current Phase 7 gate.

Impact: D-04 is intended to prevent reading stale history, but its own fixed closeout
pointer is now stale. Following it literally recreates the failure it was designed to
prevent.

### G-05 — P2 — Phase 0 calls Replit “aligned” without observing its deployed revision

Evidence:

- `00_QUICK_DIAGNOSIS.md:157` obtains only local Git state and the GitHub master hash.
- `00_QUICK_DIAGNOSIS.md:159` only checks that the Replit URL loads, then says “three
  sources aligned.”
- `05_VERIFIED_LONG_TERM_PLAN.md:108-110` distinguishes local/origin hash comparison
  from Replit HTTP availability.

Impact: HTTP 200 can be returned by a stale deployment. The procedure can establish
local/GitHub hash equality and Replit reachability, but not Replit revision equality.
The Phase 0 helper added in NIGHT-BATCH-7 reports this limitation; the governing text
does not yet do so.

### G-06 — P2 — Mirror workflow conflicts with the new automatic night-batch release flow

Evidence:

- `40_MAINTENANCE_PROTOCOL.md:81-83` mandates repo change -> commit -> copy each changed
  file to the Desktop mirror, with all three steps required.
- `05_VERIFIED_LONG_TERM_PLAN.md:466-469` defines the night-batch lifecycle as review,
  direct merge/push, and next batch, without a mirror step.

Impact: compliant release agents can either omit a mandatory mirror update or add an
out-of-repo write that the batch instruction did not authorize. The two workflows need
an explicit precedence and responsibility rule.

### G-07 — P3 — The plan's “current system state” still lists resolved Phase 2–4 gaps

Evidence:

- `05_VERIFIED_LONG_TERM_PLAN.md:36-43` is titled current system state and says
  Blackboard schema, approval packet, and v1.0 definition are not fixed.
- `05_VERIFIED_LONG_TERM_PLAN.md:286-289` says Phase 2 definition, Phase 3 schemas, and
  Phase 4 approval packet are complete.

Impact: the date at line 36 signals historical context, and §5 supplies the correction,
so this is not immediately unsafe. It still makes the same plan internally disagree
about prerequisites.

### G-08 — P3 — Phase 3 status retains a closed dependency debt

Evidence:

- `05_VERIFIED_LONG_TERM_PLAN.md:287` says `jsonschema` and `pytest` are not in the
  requirements files and remain separately outstanding.
- Current `requirements.txt:8` contains `jsonschema==4.26.0`.
- Current `requirements-dev.txt:1` contains `pytest==9.1.1`.

Impact: a future maintainer may schedule or repeat already completed dependency work.

### G-09 — P3 — Phase 4 output points to a nonexistent approval schema path

Evidence:

- `05_VERIFIED_LONG_TERM_PLAN.md:162` specifies
  `docs/schemas/approval_packet.json`.
- That path does not exist; the registered schema is
  `docs/schemas/blackboard/approval_packet.schema.json`.
- `05_VERIFIED_LONG_TERM_PLAN.md:288` records the Phase as complete but does not correct
  the path in the Phase section.

Impact: a weak model following the Phase section can create a duplicate schema or
report the completed contract missing.

### G-10 — P3 — Signed Phase 2 text remains phrased as an unsigned candidate

Evidence:

- `05_VERIFIED_LONG_TERM_PLAN.md:286` says the v1.0 definition is frozen and Owner
  signed.
- `05_VERIFIED_LONG_TERM_PLAN.md:344` still labels §6.3 a candidate.
- `05_VERIFIED_LONG_TERM_PLAN.md:355` says formal Phase 2 signoff is still required and
  forbids claiming the definition is frozen.

Impact: §5 has a clear later completion record, so the safe result is to treat Phase 2
as complete. The unresolved candidate wording nevertheless causes contradictory
answers to a mechanical “is v1.0 frozen?” check.

## 4. Clean checks

No inconsistency was found in these high-risk statements:

1. `07_AUDIT_WRITE_DESIGN.md:3-7` does not authorize the audit writer or file.
2. `07_AUDIT_WRITE_DESIGN.md:201-206` distinguishes the existing pure rollback
   builder from the unauthorized writer.
3. `09_N1_PREFLIGHT_RUNBOOK.md:21-23` states that audit persistence and the Phase 9
   gate are absent.
4. `09_N1_PREFLIGHT_RUNBOOK.md:55-57` forbids changing the null token merely to make
   the runbook runnable.
5. `01_SAFETY_BOUNDARIES.md:94-98` makes `execution_class` descriptive rather than
   present authority.

## 5. Recommended disposition

Owner/Fable should decide G-01 and G-06 before the next automatic release. The next
authorized governance cleanup can then update the stale state/routing/path items
mechanically while preserving all Phase 7 and Phase 9 gates. This report itself makes
no such changes.
