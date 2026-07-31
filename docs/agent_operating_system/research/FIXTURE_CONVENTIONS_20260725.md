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
3. New files must satisfy the directory-specific mechanical method below.
   The first three families are loaded by named pytest modules. For
   `local_mock_data`, the current guard proves only that the basename occurs in
   executable test/app/script Python source; it does not prove that pytest
   loads the file or validates its contents. Merely mentioning a fixture in a
   document never counts.
4. Adding a directory, case class, or naming family requires an explicit
   conventions update in the same authorized package.
5. Existing fixtures must not be moved or renamed merely to satisfy style.

## Directory conventions

| Directory | File-name rule | Required loading/reference method |
|---|---|---|
| `fixtures/blackboard_contract/` | `<message_type>.<case>.json`; `message_type` must be in `SCHEMA_FILES`; case is exactly `valid`, `invalid_missing_common`, or `invalid_extra_safety_flag` | `test_blackboard_schemas.py` must enumerate the directory and assert the exact three-case inventory for every registered type. |
| `fixtures/builder_golden_vectors/` | `<builder>_vectors.json`; current closed builders are `approval_packet` and `evidence_bundle` | `test_builder_golden_vectors.py` must name and load each vector file directly. |
| `fixtures/hash_chain_vectors/` | lowercase snake-case `<vector_name>.json` | `test_hash_chain_vectors.py` must load the directory with an explicit `*.json` inventory and assert the expected stems. |
| `fixtures/local_mock_data/` | lowercase compatibility name ending in `.json`; dotted case suffixes such as `.valid` and `.invalid_*` are allowed | The current mechanical guard requires every basename to occur somewhere in executable test/app/script Python source. This is a source-reference check, not proof of loading or semantic validation; the inventory separately distinguishes pytest-covered files from historical script references. |

## Mechanical acceptance for a new fixture

A fixture addition is acceptable only when all answers are yes:

- Is its parent one of the four allowlisted directories?
- Does its basename match that directory's rule?
- Does it satisfy the exact directory-specific loading/reference method above?
- For the three pytest-loaded families, does the loader validate the expected
  JSON root/contract rather than merely opening the file?
- For `local_mock_data`, has a reviewer distinguished a real loader reference
  from a comment/string mention and recorded whether pytest actually exercises
  it? The current mechanical test alone cannot answer this.
- Do the exact-inventory tests still make an unreviewed extra file fail?

This document does not authorize a fixture addition. It defines how an
otherwise authorized addition is checked.
