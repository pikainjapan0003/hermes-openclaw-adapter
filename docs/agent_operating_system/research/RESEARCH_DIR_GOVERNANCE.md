# `research/` Directory Governance Proposal — Version 2

Status: **PLANNING ONLY, NOT AUTHORIZED — OWNER DECISION BLANK**

This proposal responds to the 2026-07-27 observation that `research/` had grown
to 45 Markdown files and 4,732 lines. Those values are a dated observation, not
an automatic cleanup threshold. This document does not create an archive,
move, rename, compact, or delete any file, and it does not change the authority
of `00/01/05/10/20/30/40/90/99` or any Owner gate.

Version 2 turns the original alternatives into a reviewable SOP without
executing it. It incorporates the Round 8 rule that historical findings remain
unchanged while later disposition is recorded separately and visibly.

## 1. Proposed classifications

Every research document would carry exactly one primary class in a future
manifest. Classification describes use; it does not promote research into
governance authority.

| Class | Contents | Examples | Minimum retention proposal |
|---|---|---|---|
| `design` | Detailed contract or implementation design that another gated package may later use | Phase 7 package specification, redaction contract design | Keep at stable path while its governed feature is unresolved or active; after replacement, retain the superseded version for at least 365 days before archive eligibility |
| `review` | Findings from governance, onboarding, error-surface, or adversarial review | governance audit rounds, onboarding reviews | Keep at stable path until every finding has explicit resolution metadata; then retain at least 180 days before archive eligibility |
| `measurement` | Point-in-time health, coverage, capacity, dependency, or timing snapshot | Phase 11 health, stress/profile reports | Keep the latest two comparable snapshots at stable paths; older resolved snapshots become archive-eligible after 180 days |
| `proposal` | Alternatives awaiting Owner or governance selection | dependency authority, Owner choices, directory governance | Keep at stable path while any decision field is blank and for at least 365 days after a recorded decision/supersession |

“Archive-eligible” never means “move automatically.” Git history is not a
replacement for discoverable resolution metadata or a stable current source.

### 1.1 Classification decision tree

For a future manifest author, classify one file at a time in this order:

1. Does the file compare alternatives and leave an Owner/governance field open?
   If yes, classify `proposal`.
2. Does it specify a future contract, package, interface, or implementation
   shape? If yes, classify `design` even when it also contains alternatives.
3. Does it assign findings/severity or simulate a fresh-context reader? If yes,
   classify `review`.
4. Does it primarily record counts, timing, coverage, capacity, or dependency
   state at a date/checkpoint? If yes, classify `measurement`.
5. If none applies, HOLD classification and record why; do not invent a fifth
   class or move the file.

When a document mixes classes, select the class that controls its retention and
record secondary tags. An unresolved Owner field always forces `proposal` as
the retention-controlling class unless the document is an authoritative design
source with its own stable path.

## 2. Proposed naming convention

1. Dated review and measurement files use
   `<UPPER_SNAKE_TOPIC>_YYYYMMDD.md`; numbered rounds retain `ROUND<N>`.
2. Long-lived designs and proposals may omit a date only when they are the
   single current source for that topic; the document must then carry status
   and later-resolution metadata at the top.
3. A filename must state the artifact kind (`DESIGN`, `REVIEW`, `AUDIT`,
   `PROFILE`, `HEALTH`, `PROPOSAL`, or `ASSESSMENT`) unless the established name
   already does so unambiguously.
4. A successor must not silently reuse an older dated filename. It either adds
   a new dated file or records an in-place revision and resolution history in a
   deliberately stable long-lived source.
5. Paths cited by governance, tests, the contract index, backlog, or an open
   Owner decision are stable until a separately reviewed path map is accepted.

### 2.1 Naming SOP for a future new file

1. Choose the class using §1.1.
2. Pick a topic noun already used by the authoritative/source document; do not
   coin a synonym that can look like a competing system.
3. For a dated review/measurement, use UTC-independent calendar date supplied
   by the work order: `<TOPIC>_<YYYYMMDD>.md`.
4. For a numbered audit, keep a monotonic `ROUND<N>` and verify no file already
   uses that number.
5. For a stable design/proposal, add `DESIGN` or `PROPOSAL` to the filename and
   put version/status metadata inside the file rather than silently replacing
   its identity.
6. Run case-insensitive collision and reference searches before proposing the
   name. A collision is HOLD, not permission to overwrite.

## 3. Common metadata proposed for future files

```text
Class: design | review | measurement | proposal
Status: active | unresolved | resolved | superseded
Measured/reviewed at: YYYY-MM-DD (when applicable)
Supersedes: <path or none>
Superseded by: <path or none>
Resolution: <commit/Owner decision or blank>
Authority boundary: research only; named governance source remains authoritative
```

This block is a proposed human-readable convention, not a schema and not a
request to rewrite every historical file at once.

### 3.1 Proposed manifest/index fields

If Option B or C is later selected and separately authorized, the active
`research/INDEX.md` would contain one row per Markdown file:

| Field | Rule |
|---|---|
| `path` | Exact repository-relative current path; unique and case-sensitive |
| `class` | One of design/review/measurement/proposal |
| `status` | active/unresolved/resolved/superseded |
| `authority_source` | Named governing file, or `none`; research never names itself as L0 authority |
| `open_ids` | Finding/decision IDs still open, or `none` |
| `resolution` | Commit/Owner decision reference, or blank while unresolved |
| `successor` | Exact path or `none` |
| `retention_until` | Date derived from the selected policy, or `not eligible` |
| `archive_path` | Proposed/actual path or blank; never filled speculatively |

The index would be descriptive. It could not select an option, resolve a
finding, authorize movement, or override the source file.

## 4. Three governance options

### Option A — stable paths plus an index, no archive

- Add a manifest/index recording class, status, successor, and open findings.
- Leave every existing file at its current path indefinitely.
- Use dated successors and resolution metadata to distinguish current from
  historical material.

Benefits: lowest path-drift and tooling risk; no movement can hide evidence.
Risks: directory size and onboarding search noise continue to grow; a weak model
may still treat the first matching historical report as current.

### Option B — manifest-gated cold archive (**recommended**)

- First build and test a complete manifest at stable paths.
- Keep all active designs, unresolved reviews/proposals, latest two comparable
  measurements, Owner-choice sources, readiness reports, and current health/
  governance reports in `research/`.
- A resolved file becomes eligible only after the class-specific retention
  period, complete resolution metadata, and a tested old-path → new-path map.
- A separately authorized docs package may then move eligible files to a dated
  `research/archive/YYYY/` tree, update every reference atomically, and run all
  docs/path/onboarding guards before commit.
- Never delete historical evidence as part of archiving.

Benefits: reduces active-directory noise while keeping traceability and
recoverability. Risks: movement can break references or hide history if the
manifest, path map, or resolution metadata is incomplete; weak models may
mistake archived material as obsolete authority unless the manifest is read.

### Option C — periodic compaction into topic histories

- For each mature topic, produce a stable topic-history document containing the
  chronology, findings, resolutions, measurements, and links to originals.
- After the same retention and review gates, originals may become archive-
  eligible under a separate authorization.

Benefits: best narrative onboarding and fewer active files. Risks: highest
editorial-loss risk; paraphrase can change an Owner statement or severity, and
the compacted history can become a competing authority. It requires an exact
finding/rule crosswalk and fresh-context adversarial review.

## 5. Proposed archive trigger

Under the recommended Option B, a governance review would be requested—not
automatically run—when either condition is observed:

- more than 60 first-level `research/*.md` files; or
- more than 6,000 first-level Markdown lines.

The request should also be allowed when onboarding review proves that historical
search noise causes a concrete misread. Crossing a number grants no movement or
deletion authority. A proposal may instead conclude that no archive is needed.

### 5.1 Trigger-evaluation SOP

1. Count only first-level `research/*.md` files and their byte newline totals;
   print the exact command and environment.
2. Compare with both proposal observations, not with an invented percentage.
3. If neither is exceeded and there is no documented onboarding misread, record
   `NO REVIEW NEEDED` and stop.
4. If a trigger is met, produce a review request listing counts and candidate
   classes only. Do not create a directory or path map yet.
5. Confirm that an Owner option in §7 is actually selected. If blank, HOLD.
6. Obtain a separately issued docs-only work order before producing candidate
   movement artifacts.

## 6. Mandatory preconditions for any later movement

1. Owner selects an option in this document.
2. Every candidate has class, status, successor, and resolution metadata.
3. No candidate is an active Owner-choice source, unresolved finding/proposal,
   current readiness source, or latest comparable measurement.
4. A machine-readable old-path → proposed-path inventory is reviewed.
5. All incoming references are enumerated before movement.
6. Path, docs-drift, contract-index, cross-reference, and onboarding guards pass
   against the proposed map.
7. The later work order explicitly authorizes the exact docs-only moves.
8. No deletion occurs; recovery remains possible through both the archive and
   Git history.

## 6.1 Future Option-B archive SOP (not authorized)

The following sequence is executable only after §6 preconditions and an exact
later work order are satisfied:

1. Freeze a pre-move inventory of current paths, hashes, incoming references,
   class/status, and resolution metadata.
2. Select candidates mechanically from resolved status plus elapsed retention;
   manually exclude Owner-choice sources, open findings/proposals, readiness,
   current health/governance, and latest two comparable measurements.
3. Produce an old-path → proposed-path map without moving anything.
4. Run a fresh-context review of every candidate and map row. Any disputed
   status/path is removed from the candidate set rather than guessed.
5. In one atomic docs-only commit, create only the authorized year directory,
   move only listed candidates, and update all exact references.
6. Update the active index with new path, preserved hash, resolution, and
   successor; keep historical finding text byte-equivalent apart from any
   separately approved path-only reference repair.
7. Run docs-drift, cross-reference, contract-index, onboarding, compaction, and
   path guards plus `git diff --check`.
8. If any guard fails, revert the proposed commit before review; do not leave a
   half-moved tree.
9. Require Fable 5 fresh-context review before merge. No deletion is part of the
   SOP.

## 6.2 Index maintenance after an authorized archive

- Every later new research file gets an index row in the same package.
- A finding resolution updates the original review's visible disposition and
  its index row; it does not rewrite the original finding.
- A successor sets both directions: old `successor`, new `supersedes`.
- Measurements keep exact checkpoint/environment wording and never become
  “current” merely because the index lists them.
- Quarterly review checks missing files, duplicate/case-colliding paths, blank
  resolution on `resolved`, retention arithmetic, and orphaned incoming refs.
- An archived file returning to active/unresolved status requires a separately
  reviewed restoration map; copying it to two active paths is forbidden.

## 7. Recommendation and Owner decision

Recommendation: **Option B**, because it keeps unresolved/current material
stable while providing a reversible, manifest-gated route for old resolved
evidence. This recommendation is not a selection and creates no archive task.

Owner decision: **________**

Until that field is filled by the Owner, current files remain in place and no
archive directory, move, rename, compaction, or deletion is authorized.
