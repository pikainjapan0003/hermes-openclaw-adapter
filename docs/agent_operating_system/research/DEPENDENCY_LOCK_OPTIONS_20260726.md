# Transitive Dependency Lock Options — 2026-07-26

Status: **PLANNING ONLY — OWNER DECISION REQUIRED**

The repository exactly pins its 14 direct production/development
distributions, but does not lock the resolver-selected transitive graph. This
document compares reproducibility options only. It does not authorize a lock
file, new tooling, dependency upgrades, or installation changes.

## Decision criteria

- reproducible resolution across clean environments;
- ability to install from an offline wheel cache;
- compatibility with the current requirements-based night-batch workflow;
- reviewability of dependency changes; and
- maintenance cost for one Owner and weak implementation models.

## Option A — dedicated resolver lock file

Adopt a tool-owned lock artifact containing direct and transitive versions,
hashes, and environment markers.

- Reproducibility: strongest when the same Python/platform target is used.
- Offline install: strong when paired with a wheel cache matching the lock.
- Maintenance: highest; the repository must choose and pin the lock tool,
  regeneration command, supported platforms, and review rules.
- Night-batch compatibility: low until tooling is installed and authorized;
  automated regeneration must never happen as an incidental test step.
- Weak-model risk: generated lock churn can hide an unintended upgrade or a
  platform-specific omission.

## Option B — generated constraints file

Keep direct declarations as the human input and generate a constraints file
that pins the resolved transitive graph. Installation uses the direct
requirements together with `-c <constraints>`.

- Reproducibility: strong for the recorded Python/platform target, although
  extras and markers still require explicit verification.
- Offline install: good with a matching wheel cache; the constraints file
  alone does not contain packages.
- Maintenance: medium; regeneration and diff review are straightforward and
  preserve readable direct requirements.
- Night-batch compatibility: strongest of the three because normal install
  commands remain requirements-based.
- Weak-model risk: forgetting `-c` silently returns to unlocked resolution;
  the install/check command therefore needs a mechanical guard.

## Option C — pin transitives directly in `pyproject.toml`

List selected transitive packages as if they were project dependencies.

- Reproducibility: superficially improved but incomplete; environment-specific
  markers and optional extras remain difficult to model correctly.
- Offline install: no better than current direct pins without a wheel cache.
- Maintenance: deceptively high because upstream implementation details become
  first-class project declarations.
- Night-batch compatibility: poor unless dependency authority first moves to
  `pyproject.toml`.
- Weak-model risk: obsolete transitive pins can be mistaken for dependencies
  the application intentionally imports.

## Recommendation

**Recommend Option B**, after the declaration-authority decision. A generated
constraints file is the smallest change compatible with today's workflow and
produces reviewable transitive diffs without pretending transitives are direct
application dependencies. A later authorized package must still define:

1. the exact generator and pinned generator version;
2. Python/platform targets;
3. hash policy;
4. regeneration and drift-check commands; and
5. offline wheel-cache procedure.

Until then, the truthful state is “direct versions pinned, transitive graph not
locked.” No lock proposal authorizes dependency changes or network access.

## Owner decision

Owner choice (A, B, or C): **__________**

Decision date: **__________**

Notes: **__________**
