# Three-source Repository-State Field Proposal — 2026-08-05

Status: proposal only. No schema, script, Git command, synchronization, or
deployment behavior is authorized by this document.

## Why this proposal exists

The current three-source report records a local `git rev-parse HEAD` value, an
optional `git ls-remote` value, and Replit HTTP reachability. It intentionally
does not claim a deployed revision. A detached HEAD or shallow clone can still
produce a syntactically valid HEAD hash, but the current report has no field
that describes those repository conditions. The existing tests therefore must
not claim that those conditions are rejected or detected. This proposal gives
the Owner choices for a future, separately authorized contract change.

The present contract remains the authority until one option is selected and
implemented with its own schema, script, fixtures, and tests. In particular,
`ALIGNED` continues to mean only local HEAD equals the selected remote branch
and the Replit endpoint is HTTP-reachable; it does not mean that Replit runs
that commit.

## Design requirements shared by all options

1. Keep the helper read-only: no checkout, fetch, pull, push, reset, repair,
   deployment, or remote API runtime.
2. Preserve fail-closed reporting. If a state cannot be measured, represent it
   as an explicit unknown/unreachable result rather than inferring a safe state.
3. Keep Replit's `deployed_hash = null`, status `UNKNOWN`, and verified `false`
   unless an independently authorized source supplies deployment evidence.
4. Define detached and shallow semantics using observable Git state, not test
   doubles. The acceptance tests must run against real temporary repositories
   prepared for each state and must not mutate the caller's repository.
5. State whether a state affects the verdict, or is merely diagnostic context.
   A schema-valid object alone must not silently become a synchronization proof.
6. Any future schema change requires a new version, fixture updates, and a
   migration note; this proposal does not change the existing schema.

## Option A — Extend each Git source state

Add a closed `repository_state` object to `sources.local` (and, if the remote
probe can measure it without a local checkout, to `sources.github`). Candidate
fields are `detached`, `shallow`, and a bounded `measurement_status` enum such
as `MEASURED`/`UNKNOWN`. The existing hash and detail fields remain unchanged.

**Advantages**

- The state is adjacent to the hash whose interpretation it qualifies.
- Existing consumers can continue reading `value` while upgraded consumers
  require the new object.
- A per-source `UNKNOWN` can distinguish “not measured” from `false`.

**Risks and weak-model misreadings**

- A model may treat `detached: false` as proof that a local branch is tracking
  the selected remote branch; it is not.
- GitHub's `ls-remote` result has no working-copy detached/shallow context, so
  inventing those fields on the remote source would be false evidence.
- Adding nullable fields can make a structurally valid report look complete
  when the measurement failed unless the schema couples the status fields.

**Owner decision:** ______________________________________________

## Option B — Add a top-level repository-context object

Add a single `repository_context` object beside `sources`, describing only the
local checkout used for the report. It could contain a closed `head_mode` enum
(`BRANCH`, `DETACHED`, `UNKNOWN`), a closed `history_depth` enum
(`FULL`, `SHALLOW`, `UNKNOWN`), and a `measurement_status` enum. The source
objects retain their current shape.

**Advantages**

- It avoids pretending that a remote hash has local checkout properties.
- One place defines how the local checkout was measured and whether the result
  is known.
- The existing three-source verdict can remain unchanged while callers choose
  to require `measurement_status == MEASURED` for a stronger workflow.

**Risks and weak-model misreadings**

- A consumer may incorrectly apply local context to GitHub or Replit.
- A new top-level required object would be a breaking schema change for saved
  reports unless versioning and migration are explicit.
- `BRANCH` does not prove that the branch is named `master` or points at the
  selected remote; those are separate facts already represented by the probes.

**Owner decision:** ______________________________________________

## Option C — Separate repository-state report

Keep `three_source_report.schema.json` unchanged. Produce a separately named,
versioned repository-state report (and schema) whose sole subject is the local
checkout. The three-source command may later compose the two reports in memory,
but the state report is not allowed to alter the existing three-source verdict
unless a future Owner decision explicitly defines that coupling.

**Advantages**

- No breaking change to the existing three-source contract.
- Detached/shallow behavior can be designed, tested, and reviewed independently.
- The boundary makes it harder for a weak model to turn a diagnostic state into
  a claim about remote synchronization.

**Risks and weak-model misreadings**

- Two reports can be presented together and mistaken for one atomic snapshot
  unless both carry timestamps or a shared measurement identifier (which would
  itself require a later contract decision).
- Callers may ignore the second report and continue using the weaker verdict.
- A separate schema increases inventory, fixture, and documentation burden.

**Owner decision:** ______________________________________________

## Comparison and recommendation

| Option | Contract impact | Detached/shallow clarity | Main risk | Recommendation |
|---|---|---|---|---|
| A — per-source state | Add fields to existing source objects | Medium | Remote source may be given inapplicable local state | Not preferred |
| B — top-level context | Add one object to existing report | High | Breaking change and context misapplication | Viable if one atomic report is required |
| C — separate report | Preserve current schema; add a new contract | Highest boundary clarity | Consumers may ignore the second report | **Preferred for fail-closed separation** |

Recommendation is not a decision. Until the Owner selects an option and gives
an implementation instruction, the current report and its tests remain
unchanged, and detached/shallow requirements remain HOLD.

## Required follow-up after Owner selection

The selected option must specify the exact observable Git commands or library
queries, the meaning of an unavailable measurement, whether unknown state is a
verdict blocker, schema versioning/migration, and real-repository fixtures for
normal, detached, shallow, non-Git, and remote-error cases. A separate review
must then check that no output claims Replit deployment identity or authorizes
any write, execution, or synchronization path.

**Owner selection:** ______________________________________________
