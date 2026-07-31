# Dependency Declaration Authority Proposal — 2026-07-26

Status: **PLANNING ONLY — OWNER DECISION REQUIRED**

This proposal compares how the repository could resolve the current split
between `[project].dependencies`, `requirements.txt`, and
`requirements-dev.txt`. It does not authorize changes to any dependency file,
installation workflow, CI job, runtime, or live Google capability.

## Current verified state

| Declaration | Current role | Gap |
|---|---|---|
| `pyproject.toml` `[project].dependencies` | Packaging metadata for the original web-service subset | Omits `jsonschema` and the two guarded Google distributions; has no dev optional group |
| `requirements.txt` | Actual production/local installation input, with ten exact direct pins and comments for guarded live-only dependencies | Duplicates seven pins from `pyproject.toml`; has no machine guard against drift |
| `requirements-dev.txt` | Actual test/type-check installation input, with four exact direct pins | Not represented in project optional dependencies |

The requirements-based workflow is currently complete. Installing the project
from `pyproject.toml` alone is not equivalent. All three files are declarations,
not permission to import or invoke a guarded live capability.

## Option A — `pyproject.toml` is authority; requirements are generated

Move the full production direct set to `[project].dependencies`, add a dev
optional-dependency group, and mechanically generate both requirements files.

- Advantages: one structured authority; standard package metadata becomes
  truthful; a sync check can reproduce generated files.
- Risks: a generator and its exact invocation become new maintenance surface;
  comments explaining guarded Google dependencies need a preserved source;
  weak models may mistake “declared” for “authorized to use.”
- Migration burden: highest. The generator, output format, extras policy, and
  Replit/local install commands must be selected together.

## Option B — requirements files are authority

Declare `requirements.txt` and `requirements-dev.txt` as the operational
authority. Keep `pyproject.toml` metadata intentionally minimal or replace its
duplicated list with an explicit non-authoritative statement in a later
authorized change.

- Advantages: matches today's successful WSL/Replit-oriented install workflow;
  preserves comments beside guarded live dependencies; least immediate change.
- Risks: standard `pip install .` metadata remains incomplete; external tools
  can reasonably assume `[project].dependencies` is authoritative; leaving a
  duplicated subset invites future drift.
- Migration burden: low, but the packaging semantics must be documented
  unambiguously.

## Option C — maintain both tracks with a synchronization test

Retain all three hand-edited declarations. Add a mechanical test that compares
the intended production overlap and, if desired, a documented exception list
for guarded or development-only dependencies.

- Advantages: minimal workflow disruption; drift becomes visible immediately;
  explanatory comments remain in requirements files.
- Risks: two authorities still require synchronized human edits; exception
  allowlists can grow into a silent escape hatch; a passing overlap test does
  not make `pip install .` equivalent to requirements installation.
- Migration burden: medium-low.

## Recommendation

**Recommend Option A**, implemented later as a dedicated packaging change with
a generated-file drift test. It gives future tools one machine-readable
authority and removes the present semantic mismatch. Until that migration is
separately authorized and completed, the safe operational rule remains:
install from `requirements.txt` plus `requirements-dev.txt`; do not claim that
`pyproject.toml` is complete.

No option changes transitive locking; that is a separate decision in
`DEPENDENCY_LOCK_OPTIONS_20260726.md`.

## Owner decision

Owner choice (A, B, or C): **__________**

Decision date: **__________**

Notes: **__________**
