# Weak-Model Onboarding Review, Round 2 — 2026-07-27

Status: review only. Findings are not fixes, authorization, or permission to
rewrite governance.

## Simulation

Reader profile: a fresh weak model with no conversation history. The only
permitted entry path is:

1. repository `CLAUDE.md`;
2. `docs/agent_operating_system/README.md`;
3. `docs/agent_operating_system/05_VERIFIED_LONG_TERM_PLAN.md` §5.

At each hop the reader must answer:

1. Where is the system now?
2. What work may it do now?
3. What remains forbidden?

## Hop results

### Hop 1 — `CLAUDE.md`

The Round 1 repair is effective. Lines 3–16 now appear before the legacy loop
contract and answer all three questions:

- current-state authority is README, checked against 05 §5;
- only Owner-listed work and already assigned §6.13 night packages are allowed;
- Phase 7, Phase 9, v1.1, and v1.2 remain separate fail-closed gates;
- the mainline next steps are Phase 7's exact Owner instruction and an
  Owner-present Phase 9 session.

A weak model can answer the safety questions after one short block, before any
cross-file jump. It must still follow the links to verify phase facts.

### Hop 2 — Agent Operating System `README.md`

Lines 5–10 give the phase position and repeat that no real write, dispatch, or
call is authorized. The distinction `decision ≠ dispatch` makes the existing
review POST exception visible. The file also says Phase 2–6 are complete,
Phase 7 is design-only, Phase 8 planning is complete, and Phase 9 needs the
Owner.

One stale volatile value remains in line 7 (`HEAD 7a93127e`) even though line 9
says the entry does not carry volatile commit facts. The phase answer remains
usable, but the checkout claim is not reliable.

### Hop 3 — `05_VERIFIED_LONG_TERM_PLAN.md` §5

Lines 282–298 are mechanically clear enough to confirm:

- allowed work is Owner-listed scope plus already assigned §6.13 packages;
- Phase 7 persistence, Phase 9, v1.1, and v1.2 remain blocked by their own gates;
- Phase 2–6 are complete, Phase 7 is design-ready only, Phase 8 is planning
  complete, and Phase 9 is not started;
- Phase 7 and Phase 9 are the final two v1.0 gates.

The reader can answer all three questions without reading the rest of 05.

## Three-question answer a weak model should produce

- **Where now:** the non-executing contract, approval, evidence, and dashboard
  phases are complete; Phase 7 has design/hash/preview work but no authorized
  writer; Phase 8 planning/offline projection exists; Phase 9 is not unlocked.
- **May do now:** only the exact current Owner assignment or an exact package
  already issued under §6.13, with its package boundaries and review process.
- **Forbidden:** persistent audit writing, formal runtime data creation,
  execution/dispatch/OpenClaw runtime calls, Phase 9 without the Owner and its
  token gate, or v1.1/v1.2 without their separate instructions.

## Findings

| ID | Severity | Location | Finding |
|---|---|---|---|
| O2-01 | P2 | `docs/agent_operating_system/README.md:7,9` | The entry still states a historical `HEAD 7a93127e` while later claiming it does not carry volatile branch/commit facts. A fresh model can mistake that hash for the current checkout. |
| O2-02 | P3 | `docs/agent_operating_system/05_VERIFIED_LONG_TERM_PLAN.md:292` | The Phase 3 row still says `jsonschema/pytest` are not in requirements, but dependency files now contain them. This is stale closeout detail, not a phase-status error. |
| O2-03 | P3 | `docs/agent_operating_system/README.md:9` | “批審通過即合，免逐次蓋章” is safe only when read with `CLAUDE.md:8-13`. Read alone, a weak model may generalize it to unassigned packages or Owner-gated phases. |

No finding authorizes an edit in this review package.

## Five sentences most likely to be misread

1. **“全系統處於 read-only / mock / dry-run rehearsal 狀態。”**
   Misread: there are no POST routes. Correct reading: the existing
   `/dashboard/reviews` decision route is an explicit legacy exception and is
   still not dispatch.
2. **“批審通過即合，免逐次蓋章。”**
   Misread: any useful night work may be invented and merged. Correct reading:
   only packages already assigned under §6.13 qualify; no package may be added
   or widened.
3. **“Owner 逐字授權句『允許寫入 data/audit_dev.jsonl（local dev
   append-only）』。”**
   Misread: seeing the sentence quoted in a document supplies authorization.
   Correct reading: only a new Owner instruction addressed to the implementation
   turn can satisfy the gate.
4. **“Phase 2/3/4/5/6 已完成。”**
   Misread: v1.0 is complete. Correct reading: Phase 7 and Owner-present Phase 9
   remain the two completion gates.
5. **“9–11 未開始。”**
   Misread: Phase 11 health reports do not exist, or later-numbered research
   advances Phase 9. Correct reading: reports and planning are non-authorizing;
   they do not change implementation status or satisfy an earlier gate.

## Conclusion

The Round 1 entry-path repair succeeded: the three questions are answerable at
the top of `CLAUDE.md` and confirmed in two short follow-up regions. Round 2
found one misleading volatile hash and two lower-severity wording/detail risks.
They remain findings only.
