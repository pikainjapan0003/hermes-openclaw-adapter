# `produced_by` Option Impact Analysis

Status: **PLANNING ONLY, NOT AUTHORIZED — PB DECISION BLANK**

Source: `13_HERMES_WIRING_DESIGN.md` §4.1. Current schemas require only a
non-empty string. The proposed canonical Hermes values are
`hermes:gpt-5.5`, `hermes:minimax-m3`, and `hermes:deepseek-v4-pro`.
Provenance is not authentication, approval, role authority, or execution
permission under any option.

PB decision: **________**

## PB-A — exact enum (source recommendation)

### Change surface

| Area | Impact |
|---|---|
| Schemas | First inventory which of the ten Blackboard message types can actually be Hermes-produced. The source recommendation limits the first enum to N=1 `task_draft` and `annotation`; applying it to all schemas would wrongly exclude builders/workers/Owner records. |
| Fixtures | Update the affected valid fixtures to one canonical value and add negatives for unknown, misspelled, wrong case, empty, and canonical-looking non-Hermes values. Preserve non-Hermes producer fixtures for unaffected schemas. |
| Validators/tests | Existing validators mechanically enforce the enum after schema change. Inventory and mutation tests must prove exact affected-schema scope and that enum membership grants no permission. |
| Adapter | Future trusted adapter must select the exact value from authenticated/local provider metadata, never from model prose. Source disagreement or unknown source remains HOLD. |
| Documentation | Update 13, schema INDEX/descriptions, fixtures conventions, full-chain rehearsal, renderer docs, and migration notes. |

Work estimate: **3–4 packages** after selection (inventory/design; schema+
fixtures; regression/migration; fresh review). No schema package is authorized
by this analysis.

### Migration cost

- **Now:** medium. Only synthetic fixtures/tests exist and no Hermes runtime is
  wired, but exact per-schema scope must be established.
- **After records exist:** high. Renaming a provider requires schema versioning
  or compatibility policy, and historical records must retain their original
  provenance value.
- **Reversal:** medium-high. Relaxing enum later is easy syntactically but can
  silently admit values previously rejected; tightening/renaming can invalidate
  old data.

### Misread risk

Weak models may treat “enum-valid” as authenticated/trusted. Every description
and test must state that an enum checks spelling only; trusted envelope
construction remains separate.

## PB-B — namespace pattern plus exact adapter registry

### Change surface

| Area | Impact |
|---|---|
| Schemas | Affected schemas accept a versioned pattern such as the source example `^hermes:[a-z0-9][a-z0-9.-]*$`; the exact pattern, length, Unicode/case, and version behavior require design. |
| Registry | Define a local, closed, reviewed registry with canonical name, provider identity mapping, aliases/migration state, and unknown handling. Registry authority/ownership must be explicit. |
| Fixtures | Pattern-valid/registry-valid, pattern-valid/registry-unknown, malformed namespace, case, length, separator, and confusable cases. |
| Tests | Schema pattern tests plus adapter registry tests proving both layers are required; fuzz pattern/registry disagreement; no network lookup. |
| Documentation | 13, schema/index, registry ownership and update procedure, migration/version policy, and fail-closed source-disagreement rules. |

Work estimate: **4–5 packages** after selection. A registry proposal must precede
any schema edit.

### Migration cost

- **Now:** medium-high because a new authority artifact and ownership process
  are needed even before runtime exists.
- **Adding a provider:** medium if namespace is stable; update registry/tests,
  not necessarily schema.
- **Renaming namespace/pattern:** high; both stored values and schema versions
  may need compatibility handling.
- **Reversal:** high if consumers begin treating the registry as identity proof.

### Misread risk

The pattern accepts invented strings such as `hermes:trusted`; registry passage
is still required. Registry membership itself remains provenance policy, not
cryptographic authentication or action authority.

## PB-C — policy-only non-empty string

### Change surface

| Area | Impact |
|---|---|
| Schemas | None; all ten continue accepting any non-empty `produced_by`. |
| Adapter policy | Future adapter must carry the exact three-value allowlist, prove source from trusted envelope metadata, and reject unknown/disagreement before constructing a Blackboard message. |
| Fixtures/tests | Keep broad schema examples but add adapter-policy tests for exact allowlist, mismatch, empty/unknown, confusables, and untrusted model-supplied producer text. |
| Documentation | Clearly state that standalone schema validation cannot reject an unknown producer and cannot substitute for adapter policy. |

Work estimate: **2–3 packages** after selection (policy contract; adapter tests/
future implementation; adversarial review). Runtime wiring remains separately
gated.

### Migration cost

- **Now:** low contract cost; no schema migration.
- **Adding/renaming a provider:** low-medium in adapter policy, but every trusted
  adapter implementation must update consistently.
- **Later moving to enum/pattern:** high if historical arbitrary strings already
  exist; inventory and version/migration rules become mandatory.
- **Reversal:** low mechanically, high assurance risk because schema-only weak
  consumers cannot see the policy.

### Misread risk

This option preserves the largest gap between “schema valid” and “known
producer.” A weak model instructed only to reject malformed schema will accept
an unknown producer unless the trusted adapter gate is always in front.

## Comparative summary

| Option | Mechanical schema rejection | Provider-change flexibility | New authority artifact | Long-term migration risk |
|---|---|---|---|---|
| A exact enum | Strongest for affected schemas | Lowest | No registry; schema itself carries values | Medium-high on rename/version |
| B pattern + registry | Pattern only; exactness in registry | Highest after registry exists | Yes, local registry | High if registry ownership drifts |
| C policy-only | None beyond non-empty | High in adapter code | Adapter allowlist policy | High when later tightening stored data |

## Boundaries common to all options

1. Inventory affected producers/message types before implementation.
2. Never accept `produced_by` from model-generated content as trusted truth.
3. Unknown, empty, conflicting, or unprovable provenance remains HOLD.
4. `role` and `produced_by` remain separate.
5. No option grants authentication, approval, token, dispatch, runtime, or
   connector permission.
6. Selection requires later exact schema/policy/adapter packages; the Owner field
   above remains blank.
