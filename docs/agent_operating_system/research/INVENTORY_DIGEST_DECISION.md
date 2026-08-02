# Artifact Inventory Digest Decision — 2026-08-05

Status: documentation and test decision only. No production writer, archive,
move, deletion, or persistence behavior is authorized.

## Existing authority is retained

The existing artifact inventory remains a closed path list. `tests/
test_artifact_integrity_v4.py` pins the reviewed non-research schemas and
fixtures together with normalized content SHA-256 values. Round five extends
the discovered set to scripts and schema documentation, and round six adds the
top-level governance-document path list. Those content checks remain the
authoritative way to detect bytes changing.

The collection is deliberately not expanded to every `research/` report. The
research directory has its own governance and dated reports; adding a report
must not silently change the non-research artifact contract.

The v5 normalized content-manifest value was also recomputed after the
authorized renderer documentation/conditional-rule changes in NIGHT-BATCH-22
packages 3 and 4. The path list and normalization rule did not change; the
expected content digest changed from the stale pre-change value to
`2eb06ec52dc21d16085b5d4edd9ff33b9f91f9d86d7752d4e49424f0106a2504`.

## Added collection/path-set digest

Round six now also pins a collection digest in
`tests/test_artifact_integrity_v6.py`:

| Item | Definition | What it detects | What it cannot detect |
|---|---|---|---|
| Path list | Exact set of the round-five paths plus the 19 top-level governance paths | Unregistered, missing, or renamed membership | Content changes at an existing path |
| Collection digest | SHA-256 of sorted relative UTF-8 paths, one `\n` per path | Any change to that exact collection or its path spelling | Content changes; it has no file bytes |
| Normalized content digest | SHA-256 after CRLF→LF normalization per existing inventory | Byte/content drift at each listed path | A newly added path unless the closed path assertion also fails |

The pinned current collection is 297 paths with digest
`83c6d61ab243390a3825fedfa55b7eba52f754dfdbbb978fe066348c4cad1e22`.
The path-set digest is a second guard, not a replacement for the path list or
the per-file normalized-content checks. A reviewer can recompute it from the
same sorted relative-path rule without reading private state.

## Decision and update rule

Decision: retain the closed path list and add the collection/path-set digest.
Do not replace the existing content digests with a single aggregate hash. If a
future authorized package adds or removes an in-scope artifact, it must update
the explicit path list, the expected count, and the collection digest in one
reviewed change; the corresponding content digest must also be added or
removed. A content-only edit must change only the relevant content digest and
must not be “approved” merely because the collection digest is unchanged.

This decision does not authorize archive/move/delete actions, generation of an
inventory file at runtime, or any persistence path.
