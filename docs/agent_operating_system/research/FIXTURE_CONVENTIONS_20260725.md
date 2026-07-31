# Fixture Naming and Loading Conventions — 2026-07-25

Status: documentation of the tracked fixture layout; no fixture is moved,
rewritten, added, or deleted.

Authority basis: the 50-file inventory in
`FIXTURE_INVENTORY_20260724.md` and the loaders that currently exercise those
files. These conventions are fail-closed repository hygiene, not a runtime
contract.

## Shared rules

1. A fixture is an immediate `.json` child of one of the four allowlisted
   directories below; nested fixture directories are not part of the current
   layout.
2. File names use lowercase ASCII letters, digits, `_`, and, where a case
   suffix is part of the contract, `.`. Names contain no spaces.
3. New files must be loaded by a test through one of the explicit mechanisms
   below. Merely mentioning a fixture in a document does not count as a loader.
4. Adding a directory, case class, or naming family requires an explicit
   conventions update in the same authorized package.
5. Existing fixtures must not be moved or renamed merely to satisfy style.

## Directory conventions

| Directory | File-name rule | Required loading/reference method |
|---|---|---|
| `fixtures/blackboard_contract/` | `<message_type>.<case>.json`; `message_type` must be in `SCHEMA_FILES`; case is exactly `valid`, `invalid_missing_common`, or `invalid_extra_safety_flag` | `test_blackboard_schemas.py` must enumerate the directory and assert the exact three-case inventory for every registered type. |
| `fixtures/builder_golden_vectors/` | `<builder>_vectors.json`; current closed builders are `approval_packet` and `evidence_bundle` | `test_builder_golden_vectors.py` must name and load each vector file directly. |
| `fixtures/hash_chain_vectors/` | lowercase snake-case `<vector_name>.json` | `test_hash_chain_vectors.py` must load the directory with an explicit `*.json` inventory and assert the expected stems. |
| `fixtures/local_mock_data/` | lowercase compatibility name ending in `.json`; dotted case suffixes such as `.valid` and `.invalid_*` are allowed | Every basename must occur in executable test/app/script Python source that loads it directly or through a named preview/check loader. |

## Mechanical acceptance for a new fixture

A fixture addition is acceptable only when all answers are yes:

- Is its parent one of the four allowlisted directories?
- Does its basename match that directory's rule?
- Does the corresponding test loader enumerate or name it?
- Does the loader validate the expected JSON root/contract rather than merely
  opening the file?
- Do the exact-inventory tests still make an unreviewed extra file fail?

This document does not authorize a fixture addition. It defines how an
otherwise authorized addition is checked.
