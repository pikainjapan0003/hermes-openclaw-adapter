# Three-source Report Field Semantics — 2026-07-27

Status: documentation of the existing read-only script and schema; no schema,
script, synchronization, deployment, or repair behavior is changed.

## Facts represented

| Field | Meaning |
|---|---|
| `sources.local.value` | Local `git rev-parse HEAD`, or `UNREACHABLE` when it cannot be read as a 40-character hash. |
| `sources.github.value` | `git ls-remote` hash for the selected remote branch, or `UNREACHABLE`. |
| `sources.replit.value` | HTTP reachability only: `REACHABLE` for status 200–399, otherwise `UNREACHABLE`. The probe does not read or parse the response body, so it makes no claim about body content, body size, or deployed version. It is not a revision identifier. |
| each `detail` | Diagnostic description produced by the corresponding read-only probe. It is not authority or proof of synchronization. |

## Explicit unknown placeholders

The report does not read a Replit deployment revision. Therefore all valid
reports must contain:

```text
deployed_hash = null
deployed_hash_status = "UNKNOWN"
deployed_hash_verified = false
```

These fields mean “not measured.” The script deliberately does not consume the
response body, so malformed, truncated, or large body content is outside this
reachability-only contract. HTTP reachability must never be rewritten as a
content-validity claim, deployed hash, alignment proof, or GitHub→Replit
synchronization result.

## Verdict produced by the current script

| Verdict | Script rule | Exit code |
|---|---|---:|
| `INCOMPLETE` | Any of local, GitHub, or Replit has value `UNREACHABLE`. | 2 |
| `DRIFT` | All three probes are reachable, but local and GitHub hashes differ. | 1 |
| `ALIGNED` | All three probes are reachable and local equals GitHub. | 0 |

`ALIGNED` means only local HEAD equals the selected GitHub branch and the
Replit URL is HTTP-reachable. It does not mean Replit runs that commit.

## Contract limitation

The current JSON Schema validates the closed field shape, the verdict enum, and
the three fixed unknown placeholders. It does not conditionally recompute or
couple `verdict` to the source values. Consumers requiring semantic assurance
must use output produced by `scripts/check_three_source_readonly.py` or
independently recompute the rules above; schema validity alone is insufficient.
Changing that limitation requires a separately authorized schema package.
