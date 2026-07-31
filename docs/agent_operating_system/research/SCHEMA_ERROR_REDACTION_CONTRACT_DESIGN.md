# Schema Error Redaction Contract Design

Status: **PLANNING ONLY, NOT AUTHORIZED**  
Prepared: 2026-07-24  
Scope: Blackboard and remote read-only projection JSON Schema validation errors

This document designs the error boundary between JSON Schema validation and a
future display/logging surface. It does not authorize changes to
`app/blackboard_validators.py`, any route, any runtime connection, or any
persistent sink.

## 1. Goal and fail-closed boundary

Validation must remain useful to a caller without echoing untrusted message
content. A weak model should be able to reject malformed data from an error
code and a structural location; it must not need the rejected value, property
name, or full instance path.

The redacted error contract applies before an error is exposed outside the
in-process validation caller. If redaction cannot classify an error safely, it
must return a generic validation failure rather than the original
`jsonschema.ValidationError.message`.

## 2. Safe-to-expose fields

| Field | Exposure | Constraint |
|---|---|---|
| `valid` | Safe | Boolean only. |
| `message_type` | Safe after allowlist check | Only a value already present in `SCHEMA_FILES`; unknown input is represented as `null` plus a generic selection code. |
| `schema_file` | Safe after allowlist check | Basename from `SCHEMA_FILES`, never a filesystem path. |
| `error_code` | Safe | Fixed enum owned by the adapter, for example `required`, `type`, `enum`, `const`, `additional_properties`, `format`, `schema_selection`, or `validation_failed`. |
| `validator` | Safe | Fixed validator keyword after mapping through an allowlist; unknown keywords become `validation_failed`. |
| `schema_path` | Safe with normalization | Schema-owned path only; array indexes and keywords are allowed, but schema literals are not copied into the message. |
| `field_class` | Safe | Coarse enum such as `common_field`, `safety_flag`, `message_field`, or `unknown`; it must not contain an instance property name. |
| `message` | Safe only when adapter-authored | Fixed template selected from `error_code`; no string interpolation from the rejected instance or raw `jsonschema` message. |

## 3. Fields that must be masked

| Source material | Required representation | Reason |
|---|---|---|
| Rejected instance value | Omit entirely | It may contain tokens, credentials, payloads, URLs, or local paths. |
| Unknown/additional property name | Omit or replace with `<redacted-property>` | `jsonschema` commonly embeds the property name in its message. Property names are untrusted input. |
| Instance path | Replace with a coarse field class or `$` | Path segments are derived from untrusted property names and can leak identifiers. Array positions add little value at this boundary. |
| Allowed enum/const literals | Do not interpolate into `message` | Contract literals may reveal internal capability names; callers can inspect the authority schema separately. |
| Exception text from schema loading | Do not expose outside a trusted local diagnostic channel | OS and JSON decoder exceptions can contain absolute paths or nearby document content. |

The internal validator may retain richer Python objects during a call, but no
masked item may enter the returned public dictionary, dashboard content,
Blackboard message, audit preview, or log record.

## 4. Minimum useful debugging information

A future redacted error should contain only:

1. the allowlisted `message_type`, if selection succeeded;
2. the allowlisted schema basename;
3. a stable `error_code`;
4. an allowlisted validator keyword;
5. a normalized schema path;
6. a coarse `field_class`; and
7. a fixed adapter-authored message.

Example target shape:

```json
{
  "valid": false,
  "message_type": "task_draft",
  "schema_file": "task_draft.schema.json",
  "errors": [
    {
      "error_code": "type",
      "validator": "type",
      "schema_path": "$.properties.task_id.type",
      "field_class": "message_field",
      "message": "A field has the wrong JSON type."
    }
  ]
}
```

The example is data shape only. It is not validator implementation
authorization.

## 5. E-02 remote projection validator boundary

E-02 is a distinct exposure boundary, not merely another Blackboard schema.
`validate_remote_readonly_projection` validates a deliberately lossy display
object intended for a future remote-facing presentation layer. Even though the
current projection is offline-only, an echoed instance value, property name,
or instance path would be closer to an eventual remote exposure than an
in-process Blackboard validation error. The consequence of leakage is
therefore higher, and remote wiring must remain blocked until this boundary has
an implemented, mechanically tested redaction gate.

### 5.1 Remote projection exposure table

| Validator material | Exposure | E-02 rule |
|---|---|---|
| Fixed schema identity | Safe | Expose only the adapter-owned literal `remote_readonly_projection`; never expose `$id` or a schema filesystem path. |
| Stable error code | Safe | Adapter-owned enum only; unknown validator keywords collapse to `validation_failed`. |
| Validator keyword | Safe after allowlist | Map `required`, `type`, `enum`, `const`, `additionalProperties`, `format`, `pattern`, and the adapter-owned `projectionLeak`; all others collapse. |
| Schema path | Safe after normalization | May identify a schema-owned projection field, but must not include schema literal values or a local path. |
| Coarse projection field class | Safe | Use an enum such as `identity`, `freshness`, `status`, `safety_summary`, `decision_summary`, `evidence_reference`, or `unknown`. |
| Adapter-authored message | Safe | Fixed template only; it must not interpolate `jsonschema.ValidationError.message` or leak-guard findings. |
| Rejected projection value | Must omit | It may contain a secret, URL, filesystem path, source identifier, or unapproved payload despite the projection allowlist. |
| Unknown/additional property name | Must mask | Replace with `<redacted-property>` or omit; remote consumers do not need an attacker-controlled key. |
| Instance path | Must mask | Reduce to `$` or the coarse field class because path segments may be attacker-controlled. |
| `jsonschema` error message | Must mask | It can echo values, property names, enum literals, and patterns. |
| `_projection_leaks` finding path | Must mask | The current path identifies the rejected key; export only `projection_leak` plus a coarse field class. |
| Schema-loader/decoder exception | Must mask | Never expose absolute paths, decoder context, stack text, or environment details. |

### 5.2 Minimum E-02 debugging information

The exportable remote projection error needs only:

1. `valid=false`;
2. schema identity `remote_readonly_projection`;
3. a stable adapter-owned error code;
4. an allowlisted validator class;
5. a normalized schema-owned path when safe;
6. a coarse projection field class; and
7. a fixed adapter-authored message.

It must not contain source task identifiers, display identifiers, commit
values, timestamps, evidence hashes, rejected safety values, unknown property
names, URLs, or paths. Trusted local diagnosis may retain a richer internal
object only under Option C; that object is never exportable.

### 5.3 Difference from E-01

E-01 protects ten Blackboard message validators whose present callers are
local contract code. E-02 protects a display projection specifically designed
to cross into a future remote read-only presentation layer. Both require the
same denylist categories, but E-02 additionally masks display identifiers,
freshness metadata, commit/evidence references, and leak-guard paths. A future
remote route or transport remains a separate Owner gate; this design does not
authorize one.

## 6. Design options

### Option A — redact inside each validator

`validate_blackboard_message` would return only the public redacted contract.

- Benefit: one boundary and the smallest chance that raw errors escape.
- Risk: trusted test/debug callers lose precise errors unless a separate,
  explicitly trusted API is later designed.
- Weak-model misread surface: low; there is no raw result to forward.

### Option B — keep validator output and redact only at exposure points

The validator would keep today's structured errors, while every dashboard,
logging, projection, and future API boundary would be responsible for
redaction.

- Benefit: richest local diagnostics.
- Risk: every new exposure point becomes a possible leak; a weak model can
  easily forward the wrong object.
- Weak-model misread surface: high because both safe and unsafe shapes coexist.

### Option C — double-layer contract

An internal validation result remains process-local, and a mandatory pure
redaction function converts it to the only exportable error contract. Static
tests forbid the internal shape from routes, templates, projections, and
persistent sinks.

- Benefit: preserves local diagnosis while creating an explicit export gate.
- Risk: requires naming, import, and test discipline; a caller can still bypass
  the gate unless later static guards cover every exposure surface.
- Weak-model misread surface: medium if types/names are distinct and the raw
  object is documented as non-exportable.

For E-02, the same choice applies to
`validate_remote_readonly_projection`: A changes its returned shape, B makes a
future display boundary solely responsible, and C retains a process-local raw
result plus a mandatory export-safe conversion. No option authorizes remote
wiring.

## 7. Recommendation

**Recommended: Option C**, with Option A as the fail-safe fallback if the
export-boundary guard cannot be made mechanically complete. The public
redacted shape should be a new explicit contract rather than a silent change to
the current validator return value. The implementation package must include
the following future acceptance items:

- leak-marker tests for all ten Blackboard schemas;
- a payload-free schema-selection error test; and
- a remote projection validator leak-marker test covering E-02 with the same
  mechanical no-payload assertion.

This recommendation is not a decision and grants no permission to implement.

## 8. Owner decision

Owner decision (choose A, B, or C): **__________**

Decision date: **__________**

Notes: **__________**

