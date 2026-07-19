# v1.2 First Real Code Task Acceptance Design

Status: **PLANNING ONLY, NOT AUTHORIZED**

**前置＝v1.1 簽核完成。** v1.1 未完成簽核時，本文件不能解鎖任何真實代碼
任務。即使 v1.1 完成，v1.2 仍需要新的 Owner instruction、明確任務範圍、packet/
token 及驗收裁決。本文件不是授權，不建立 worker、role router、dispatch、runtime、
audit writer、execution gate 或自動合併路徑。

## 1. Purpose and N=1 boundary

v1.2 的第一個真實代碼任務只驗證一件事：一個狹窄、可回滾的 Owner 痛點，能否
從精確任務定義走到可審查 patch，並以獨立測試與多審查員證據收工。它不是「讓 AI
自行接手 repo」，也不是多 worker 上線。

First-run constraints:

1. One task, one repository, one pinned base commit, and one intended code behavior.
2. A small exact file allowlist and explicit out-of-scope list.
3. No dependency, schema, route, persistence, authentication, authorization, connector,
   or runtime change unless each is named by the new Owner instruction.
4. No production/shared data and no live service call in tests.
5. No automatic follow-up, retry, merge, push, or next-task creation.
6. The first task must be reversible by a single Git revert and have no external side
   effect that Git cannot undo.

If a candidate cannot satisfy all six constraints, it is not the first v1.2 task.

## 2. Required task packet

The Owner-reviewed task definition should freeze:

| Item | Required content |
|---|---|
| Identity | task id, parent plan id, Owner instruction reference |
| Repository state | repository id, base commit, branch, clean/known worktree statement |
| Problem | reproducible current behavior and exact desired behavior |
| Scope | allowed files, allowed operation types, forbidden files and systems |
| Acceptance | targeted tests, full-suite command, warning/type gates, expected observable result |
| Safety | execution class, expected side effects, secret/data classification, stop conditions |
| Review | named independent reviewer roles/models and artifacts each must inspect |
| Rollback | proposed code-task commit boundary, revert target, post-revert validation |
| Expiry | instruction/session validity and no cross-session authority inheritance |

Natural-language task text or a role prompt cannot enlarge these fields. Any mismatch
between packet, base, worktree, or requested patch is HOLD.

## 3. Task decomposition

The N=1 task is split into evidence-producing stages. A later stage consumes evidence;
it does not inherit permission to perform additional work.

### Stage A — reproduce and freeze

- Verify the pinned base and inventory existing user changes without altering them.
- Run the smallest deterministic reproduction and retain its exact output.
- Record expected failure before the patch. A test that already passes does not prove
  the defect and requires task re-evaluation.
- Freeze the file allowlist and acceptance commands before implementation.

### Stage B — patch preview

- Produce the smallest patch that changes only the accepted behavior.
- Explain each changed hunk against an acceptance condition.
- Refuse opportunistic cleanup, unrelated formatting, dependency upgrades, or file
  moves.
- Run the targeted test and inspect the diff before any commit is proposed.

### Stage C — independent verification

- Reproduce the original defect against the documented base or a faithful fixture.
- Verify the targeted test fails for the right reason before the fix and passes after.
- Run the full repository suite, configured warning gate, and configured static/type
  checks.
- Check that negative and boundary cases fail closed and that no forbidden path was
  introduced.

### Stage D — adversarial review

- Review authorization scope, diff, tests, side-effect claims, and rollback plan from a
  fresh context.
- Search for hidden execution/dispatch, persistence, route, token, credential, and
  external-network effects.
- Report P0–P3 findings with file/line evidence. Findings are not silently waived by
  the implementer.

### Stage E — Owner acceptance and closeout

- Present the exact diff, test transcripts, reviewer reports, residual risks, and
  proposed commit/revert identifiers.
- Owner accepts, edits, or rejects the code task as data; acceptance is not permission
  for a new task.
- Only the release action explicitly covered by the active instruction may occur.

## 4. Reviewer independence

`20_JUDGMENT_RUBRICS.md` R-13 governs high-risk review. Any first code task that
touches a safety boundary, write path, execution gate, authentication/authorization,
or Owner-signoff artifact requires at least two different-model fresh-context
reviewers. A single model reviewing its own patch is never sufficient.

For a non-high-risk first code task, the minimum separation is still:

1. implementer produces the patch and implementation evidence;
2. tester independently reproduces and runs acceptance checks;
3. reviewer examines scope, diff, and rollback without relying on the implementer's
   reasoning transcript.

If R-13 triggers, the tester does not substitute for either of the two required
different-model reviewers unless that tester is explicitly assigned as one and meets
the fresh-context/model-independence rule. Reviewer disagreements are itemized for the
Owner; the implementer cannot silently arbitrate them.

## 5. Test-green acceptance rule

The task is not complete merely because the patch looks correct. All applicable gates
must be green in the same candidate state:

1. deterministic pre-fix reproduction captured;
2. targeted regression test passes after the patch;
3. boundary/negative tests pass;
4. complete repository test suite passes with the repository's default warning policy;
5. configured type/static checks pass;
6. no test was deleted, skipped, weakened, or reclassified merely to obtain green;
7. changed-file inventory equals the packet allowlist;
8. fresh-context review has no unresolved P0/P1 and all P2/P3 dispositions are visible
   to the Owner.

“Not run,” partial green, an interrupted suite, or results from another commit are not
green. A flaky or environment-blocked test remains an unresolved acceptance item; the
model records the limitation and stops rather than claiming success.

## 6. Git rollback design

Git is the code rollback boundary. The accepted task should form one reviewable code
commit whose parent is the reviewed candidate state. Its rollback target is that exact
commit, not a branch name, moving HEAD, guessed hash, or broad file checkout.

The rollback rehearsal design is:

1. record the accepted code commit and its parent;
2. verify the commit contains only the approved files/hunks;
3. prepare a descriptive rollback preview naming the one commit;
4. obtain the required rollback authority for the active session;
5. create a normal Git revert commit without force, reset-hard, or history rewrite;
6. rerun the targeted regression and full-suite checks in the expected post-revert
   state;
7. retain both forward and revert evidence for Owner closeout.

Rollback cannot undo an external side effect. Therefore any first-task candidate with
such an effect is rejected at selection time. Failure to revert cleanly is HOLD; do not
try another destructive command or widen the revert.

## 7. O2 role-worker integration point

`research/O2_ROLE_WORKER_PROPOSAL.md` remains a proposal. Its role ids, prompts,
registry locations, maintenance rights, and multi-worker stages are drafts and have no
runtime effect.

If the Owner later ratifies O2, this acceptance design can map evidence ownership as
follows without changing authority:

| Proposed role | v1.2 evidence responsibility | Never gains automatically |
|---|---|---|
| `openclaw_engineer` | Patch preview, hunk-to-requirement map, targeted-test output | Permission to merge, push, expand scope, or assign follow-ups |
| `openclaw_tester` | Independent reproduction, negative/full-suite/type evidence | Permission to modify the patch or waive a failure |
| `openclaw_security_reviewer` | P0–P3 boundary findings and HOLD recommendation | Owner approval or execution authority |

The initial v1.2 rehearsal remains single-worker/sequential even after role language is
used. Multi-worker routing requires O1/O2 decisions, assignment contracts, idempotent
claim/cancel/revoke controls, and separate authorization. A `role` field records
provenance; it does not prove identity or confer capability.

## 8. Stop conditions

Immediately HOLD the affected stage if:

- v1.1 is not signed off or the new v1.2 Owner instruction is absent/ambiguous;
- base commit, worktree, task packet, or file allowlist differs from observation;
- the reproduction cannot be made deterministic;
- the task requires a forbidden external effect or a non-Git rollback;
- tests require weakening, skipping, or unexplained fixture replacement;
- the patch reaches runtime, dispatch, persistence, token, connector, or new route
  behavior outside exact scope;
- required independent reviewers are unavailable;
- any test/type/warning gate is red or was not run;
- rollback target or post-revert state is ambiguous.

HOLD means preserve evidence and ask the Owner the exact unresolved question. It does
not authorize a workaround, retry, alternate task, or broader refactor.

## 9. Owner signoff checklist for a future v1.2 package

- [ ] v1.1 signed off and cited.
- [ ] New Owner instruction identifies the exact task, repo, base, files, and actions.
- [ ] First-task constraints in §1 all pass.
- [ ] Reproduction and expected result are frozen.
- [ ] Test, warning, type/static, and changed-file gates are explicit.
- [ ] R-13 reviewer assignments are satisfied where triggered.
- [ ] O2 role language, if used, is provenance only unless separately ratified.
- [ ] Git revert target and post-revert checks are exact.
- [ ] No external effect exists that Git cannot undo.
- [ ] No automatic merge, push, next task, retry, or dispatch follows acceptance.

Until every prerequisite and a new Owner instruction exist, this remains a planning
artifact only.
