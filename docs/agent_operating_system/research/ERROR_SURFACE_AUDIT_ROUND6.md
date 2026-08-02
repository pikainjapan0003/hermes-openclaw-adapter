# Error Surface Audit — Round 6

Date: 2026-08-03

Status: completed review plus test-only guard. This report does not authorize
output persistence, schema changes, runtime wiring, or remote publication.

## Scope boundary

This round reviews the stdout-only schema renderer after its composite-type
repair and the read-only mirror drift reporter. Both tools intentionally expose
some caller-controlled labels: the renderer prints the selected schema title,
relative source name, field names, descriptions, const/enum values, and declared
constraints; the mirror report prints relative filenames. Those documented
surfaces remain in the existing 14-xfail redaction baseline and are not silently
reclassified as secret-safe.

The narrower fail-closed claim tested here is that neither tool additionally
echoes raw file contents, absolute root paths, environment details, or schema
metadata that is outside its documented field table.

## Findings

| ID | Severity | Result | Evidence |
|---|---|---|---|
| ESR6-01 | — | Pass | Composite `oneOf`/`anyOf`/`allOf` type rendering emits only derived JSON type names; hidden `$comment`, `examples`, and `default` content is not copied into the table. |
| ESR6-02 | — | Pass | Mirror comparison hashes file bytes and prints only status, relative path, and fixed detail; raw file bodies and absolute repo/mirror roots are absent. |
| ESR6-03 | P3, carried | Open | Intended labels and relative paths remain caller-controlled stdout surfaces. The exact existing xfail inventory is unchanged rather than weakened. |

## Mechanical evidence

`tests/test_readonly_output_redaction_round6.py` injects a synthetic secret and
absolute-path marker into non-presented schema metadata, mirror file contents,
and mirror root directory names. The rendered reports must omit both markers
while still showing the public type/status facts. All filesystem activity is
restricted to pytest `tmp_path`.

The test neither edits the existing xfail file nor changes the declared count.
