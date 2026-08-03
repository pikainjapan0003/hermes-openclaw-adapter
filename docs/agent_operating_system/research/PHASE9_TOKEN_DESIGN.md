# Phase 9 Single-Use Token Design

Status: **PLANNING ONLY. NOT AUTHORIZED FOR IMPLEMENTATION OR EXECUTION.**

Date: 2026-08-03
Scope: one Owner-present N=1 harmless-query attempt. A token authorizes neither
a worker nor a general action class. It is valid only when every independently
checked gate condition is green.

Authorization ladder: an Owner design selection chooses an option only; a later
exact instruction must separately authorize implementation; after that work
passes independent review, another exact Owner-present instruction must
authorize the one execution. No layer implies the next.

## 1. Non-negotiable properties

The future mechanism must satisfy all of these at the same time:

1. **Owner-originated authority.** A model cannot mint authority for itself.
2. **Unpredictable secret.** A token cannot be a date, task id, packet id, or
   approval word.
3. **Exact binding.** It binds one approval packet, action, target, frozen input
   set, expiration window, and attempt counter.
4. **Consume before call.** The durable burn decision happens before OpenClaw is
   allowed to start.
5. **One attempt, not one success.** Timeout, exception, ambiguous completion,
   or Owner abort still spends the token.
6. **No plaintext persistence.** Fixtures, logs, audit records, reports, argv,
   and error messages contain only a digest/reference, never the raw token.
7. **Fail closed.** Missing, invalid, expired, mismatched, or consumed means
   deny; the gate does not repair, refresh, or retry.
8. **Restart-safe replay denial.** A process restart cannot make a consumed
   token usable again.
9. **Concurrency-safe.** Two simultaneous presentations produce at most one
   winner and at most one OpenClaw start.
10. **No standing permission.** The mechanism returns to deny-all after the
    attempt. A second action needs a new packet and new Owner token.

The raw token is authentication material, not Blackboard content. The present
approval-packet field remains structurally `null` until the Owner chooses and
authorizes a Phase 9 schema design.

## 2. Owner authorization channel (out-of-band)

Token production and Owner authorization are separate facts. All token options
require both an **Owner-controlled, model-inaccessible ingress channel** and a
model-inaccessible **egress/display channel**. The raw token or authenticator
response reaches the future gate, and any secret/challenge/digest reaches the
Owner, without entering model context, model-visible terminal output, chat,
argv, environment variables, clipboard history, fixtures, reports, or audit
plaintext. A model-visible instruction may name the frozen action and a safe
token reference, but it must never carry the raw token.

### 2.1 Hard OS-principal prerequisite

The gate and every local ingress/egress endpoint that handles raw token material
**must run as an OS principal different from the model principal**, or the whole
secret-bearing channel must be moved off the local host. A different process,
terminal, filename, or window under the same principal is not separation.

Fable 5 measured the current WSL review environment as model session
`uid=1000(lnovo)`, `gid=1000(lnovo)`, Linux `ptrace_scope=1`, with same-uid
visibility into the model principal's own `/proc/<pid>/fd`; `/usr/bin/openclaw`
is a root-owned symbolic link. These facts are evidence, not authorization. The
root ownership of the OpenClaw link does not isolate a gate launched by the
model's `lnovo` principal.

**Same uid/principal = 不可實作.** Under the same uid, an ACL/mode check may
report the expected owner and permissions while the model still has the same
effective access, `/proc` visibility, inherited descriptors, terminal access,
or ability to replace/connect to an endpoint. Such a result is a **false pass**
and must never count as model-exclusion evidence. A usable design needs a
distinct uid/SID with no shared access-granting group or elevation path, or an
off-host channel whose secret never reaches the model's OS principal.

### 2.2 Mandatory platform-separation preflight

All checks are performed from both the gate principal and the model principal;
metadata inspection alone is insufficient. Any unknown or model-side success is
fail-closed:

| Check | Required evidence | Fail-closed condition |
|---|---|---|
| uid/gid or SID comparison | gate, ingress, egress, generator, and model effective identities are recorded; gate identity differs from model and shares no access-granting supplementary group | same uid/SID, unresolved identity, shared group grants access, or model can switch/elevate to gate identity |
| ACL/mode traversal | model-principal probes cannot list parent paths, open/read/write/replace the endpoint, or discover secret metadata; gate-principal probes can perform only the contracted operation | ACL evaluated only as gate user, model probe succeeds, parent directory permits replacement, or ownership changes |
| `ptrace_scope` and process inspection | current policy is recorded, and an actual model-principal probe cannot ptrace, inspect memory/environment, or use `/proc/<gate-pid>` to reach secret state | relying on `ptrace_scope=1` alone, same-principal trace/read remains possible, or result is unknown |
| `/proc` visibility | model-principal probes of gate `fd`, `fdinfo`, `environ`, `mem`, and process metadata fail at the required boundary | any secret-bearing fd/target or environment value is readable/discoverable |
| descriptor/handle inheritance | child-process table proves secret fds/handles are close-on-exec/non-inheritable; model and OpenClaw receive none | an unplanned child inherits, duplication is possible, or inheritance cannot be enumerated |
| TTY/console ownership | exact tty/session owner, controlling process, mode/ACL, echo state, readers, and input-injection rights are recorded; model-side open/read/write/ioctl probes fail | tty belongs to model uid, model is attached, echo/screen capture is enabled, injection/read succeeds, or owner changes |

The exclusion checks run once before the channel opens and are later repeated as
specified in §2.5. Passing on one machine or one earlier session is not reusable
evidence.

### 2.3 Ingress candidates re-evaluated for the measured host

The following remain Owner choices; this document selects none:

| Channel candidate | Same-uid local result | Conditions for possible use | Endpoint-specific requirements |
|---|---|---|---|
| OOB-A — one-read Owner deposit | **不可實作** when the deposit and gate are reachable as `uid=1000(lnovo)` | gate/deposit owned by a distinct non-model principal, or deposit entirely off-host; model cannot traverse, list, read, replace, link, inherit, or race the object | exact separately authorized object/path; atomic one-read semantics; anti-replacement and anti-hardlink/symlink checks; no fallback copy; crash/cleanup contract |
| OOB-B — separate Owner device | a separate device is **not sufficient** if its local socket/pipe receiver runs as the model uid; that arrangement is **不可實作** | distinct-principal local receiver or an endpoint wholly outside the model host; cryptographic device authentication binds the Owner device to the rehearsal | exact socket/pipe ownership and mode; exclusive non-model bind; peer credential check for the local receiver; mutual device authentication; anti-squatting/anti-takeover; bound nonce/deadline; replay cache or durable burn; one accepted connection; no unauthenticated fallback |
| OOB-C — isolated terminal input | **不可實作** when the tty/gate is owned by or attached to `uid=1000(lnovo)` | distinct-principal gate owns a dedicated tty/console and the model cannot open, read, inject, inspect, ptrace, or inherit it; otherwise terminal is off-host | echo disabled; controlling-session and tty ownership frozen; exclusive reader; non-inheritable stdin; screen/log capture disabled; model-side tty probes fail |

If no candidate satisfies §2.1–§2.3, **every token-production option is
不可實作**. “The model promises not to use what it saw” is not separation.

### 2.4 OOB egress/display requirements

Ingress isolation does not protect a token that the generator displays to the
model. The Owner must select and authorize one exact egress with the ingress:

| Egress candidate | Who starts/generates | Display destination | Required proof that the model cannot read it |
|---|---|---|---|
| E-A — distinct-principal isolated tty | an already authorized gate/generator running only as the distinct gate principal | exact gate-owned tty/console viewed directly by Owner | §2.2 tty/process probes pass; tty is not the model terminal; no stdout/stderr tee, scrollback sharing, screen capture, inherited fd, or model-readable log |
| E-B — paired separate Owner device | distinct-principal gate generator, or approved Owner-device authenticator | authenticated paired device display; raw secret is encrypted only to that device | mutual endpoint authentication, device/rehearsal binding, model-host output contains only non-secret references, and model-side socket/process probes cannot recover plaintext |
| E-C — off-host Owner authenticator | authenticator generates or derives the response on the Owner device | that device only; local gate receives only the authenticated response over approved ingress | raw token never exists on the model host; challenge, device identity, packet/action binding, and replay protection verify without a model-readable secret |

For every egress the design records who launched the generator, its OS
principal, exact output device/tty, all copy/log/clipboard sinks, and the
model-principal negative probes. A model-visible display invalidates the token
and ceremony.

### 2.5 Mechanical definition of `owner_synchronously_present`

`owner_synchronously_present` is a computed gate result, never a caller-supplied
boolean. It is true only when all of the following frozen predicates are true:

1. `owner_channel_contract_approved`: the Owner has selected one exact OOB
   channel and separately authorized its implementation and use.
2. `model_exclusion_attested`: the distinct-principal/off-host rule and every
   applicable §2.2 ingress and egress check pass and prove the model process has
   no read, write, inject, list, inspect, inherit, or replay access.
3. `fresh_challenge_bound`: the gate generated a cryptographically unpredictable,
   single-session challenge bound to the rehearsal id, packet digest, action
   digest, and a short deadline.
4. `owner_response_authenticated`: before that deadline, the chosen OOB channel
   delivered the correct response using an Owner-held authenticator or secret;
   the gate retains only response/challenge digests.
5. `final_presence_reconfirmed`: immediately before token burn, a second fresh
   bound challenge succeeds through the same still-isolated channel.
6. `channel_continuity_green`: ingress and egress identities, ACLs, endpoints,
   tty/device ownership, descriptors, and model exclusion have not drifted; the
   channel has not closed, timed out, or crossed the synchronous session
   boundary.

The value is `false` if any predicate is absent, unknown, stale, or changes. A
chat reply, dashboard click, copied token value, or human-readable claim cannot
set it to true.

### 2.6 Reconciliation with the frozen Owner-instruction rules

`05_VERIFIED_LONG_TERM_PLAN.md` Phase 9 says the token is provided by an “Owner
instruction”; `09_N1_PREFLIGHT_RUNBOOK.md` says “Only the Owner provides the
fresh token.” This design treats the authorization as a two-part Owner act:

1. the Owner's verbatim instruction authorizes the exact frozen packet/action
   and cites only the redacted token digest/reference; and
2. the Owner supplies the matching raw secret or authenticated response through
   the selected OOB channel.

Neither half is sufficient alone. The instruction creates no reusable secret,
and possession of the secret without the exact Owner instruction creates no
authority. Therefore only the Owner provides the token, while the raw value
never becomes model-readable. The Owner must approve this interpretation and
the selected channel before implementation; until then Phase 9 remains HOLD.

### 2.7 Phase 9 authorization-citation masking

The Owner's original instruction must be written without the raw token. Its
token reference uses exactly this human-visible form:

`token=<REDACTED:sha256[0:8]>`

Here `sha256[0:8]` is replaced by the first eight hexadecimal characters of the
raw token's SHA-256 digest. The same instruction must name the full packet digest
and action digest. The eight-character display is only a human correlation tag;
the gate compares the complete binding digest/HMAC supplied through the OOB
ceremony and never treats the short tag as authentication.

This satisfies `20_JUDGMENT_RUBRICS.md` R-06 without copying a secret because
the **verbatim instruction as originally authored** already contains the
redacted tag, packet digest, and action digest. Reports, authorization citations,
commit messages, and closeout text quote that original safe sentence exactly;
they do not take a raw-token sentence and redact it afterward. The packet/action
digests identify the exact authorized object, the full non-secret token digest
in the binding record proves which OOB token matched, and the instruction digest
ties the citation to the Owner's text.

This Phase 9 format still requires an Owner decision before implementation. It
does not modify `01_SAFETY_BOUNDARIES.md` or `20_JUDGMENT_RUBRICS.md`. If the
Owner's original instruction contains a raw token instead of the prescribed
tag, the ceremony is invalid: do not quote or persist it, revoke the exposed
token, and start a new ceremony with a new token.

## 3. Who produces the token — three options

| Option | Owner experience | Strengths | Weak-model / security risks | Verdict |
|---|---|---|---|---|
| T-A — Owner invents and supplies it | Owner creates a fresh secret and sends it only through the selected OOB channel | Authority visibly originates with Owner; no generator trust | Human entropy and reuse are likely; unsafe if copied through chat or model-visible terminal | Not recommended; **不可實作** without §2 separation |
| T-B — System generates once, Owner returns it OOB | After evidence is frozen, a separately authorized generator delivers one random token only to the Owner; the Owner returns it through the selected OOB channel | Strong entropy plus explicit Owner act; easy binding to displayed packet digest | Generator/display and return channel both require model exclusion; clipboard/chat exposure invalidates the token | May be selected only if §2 separation is mechanically proven; not unconditionally recommended |
| T-C — System challenge, Owner confirms with an authenticator | Gate creates a bound challenge; an approved Owner-held authenticator returns the response through the selected OOB channel | Raw bearer token need not be typed; strongest binding to live Owner confirmation | Highest complexity; authenticator, key custody, and recovery become new systems | May be selected only if §2 separation is mechanically proven |

For T-B, “system generates” is not self-authorization. Generation may occur only
after a separate Owner instruction authorizes that exact local generator step.
The token becomes eligible only when the Owner returns it through the selected
OOB channel and separately gives the exact action instruction described in
§2.6. If the generator display or return path is model-visible, T-B is
**不可實作**.

## 4. Binding contract

The token verifier should compare a canonical binding record, not free text.
The proposed binding fields are:

| Binding field | Required meaning | Mismatch disposition |
|---|---|---|
| `approval_packet_id` | Exact accepted packet identifier | burn presented session token; deny |
| `approval_packet_hash` | Canonical digest of the frozen packet excluding raw token material | burn; deny |
| `evidence_bundle_hash` | Already verified Phase 5 bundle digest | burn; deny |
| `action_hash` | Canonical digest of exact action, target, arguments, timeout, agent/session posture | burn; deny |
| `rehearsal_id` | One Owner-present session identifier | deny tokens from any other session |
| `issued_at` / `expires_at` | Short UTC issuance window; no clock rollback tolerance | expired or indeterminate clock means deny |
| `attempt_number` | Constant `1` for N=1 | any other value means deny |
| `nonce_digest` | Salted/HMAC digest of the raw token; never the raw value | mismatch means deny without revealing which component failed |
| `contract_version` | Exact Phase 9 token-binding version | unknown/downgraded version means deny |

`action_hash` must include every byte/field that can affect the runtime call.
Changing a prompt space, target, timeout, agent id, session id, output mode, or
capability posture invalidates the binding. The verifier must not normalize an
unexpected runtime value to make it match.

## 5. “Use once” persistence — three options

| Option | Mechanical rule | Crash/restart behavior | Risks | Verdict |
|---|---|---|---|---|
| B-A — Separate token marker file | Under an exclusive lock, create/append a consumed digest before the call; existing digest denies | Can be restart-safe if durable and atomic | Introduces a new persistent write target and its own chain/tamper/permission policy; currently unauthorized | Viable only with a new explicit path authorization |
| B-B — Memory claim plus audit result | Atomically claim token in process memory, then append an audit record | Memory claim disappears on restart; audit append races/crashes can leave ambiguity | Cannot prove replay denial after restart unless audit is authoritative; process-local locks do not cover another process | **不可單獨採用**; it may only be an in-session defense layered under B-A or B-C |
| B-C — Hash-chain burn event | Under one gate-level lock, scan/verify the Phase 7 chain, append a redacted burn event, fsync, reverify, and only then allow the call | A committed burn survives restart; crash after burn safely wastes the token | Existing audit schema does not yet define token-digest/binding/burn fields; uniqueness and atomic gate coordination need a separately authorized contract | **Recommended architecture, not yet implementable** |

The recommended B-C order is deliberately fail-safe: `verify chain → validate
binding → append burn → fsync → verify burn → one call`. A crash anywhere before
the verified burn causes no call. A crash after the burn causes no retry. The
burn record stores only a digest, binding hash, disposition, and timestamps.

The Phase 7 writer validates the current `audit_event` schema and hash chain,
but that does not automatically make it a token ledger. Before implementation,
the Owner must approve a machine contract able to represent the burn without
free-text encoding or raw-token leakage.

The validity upper bound is the live, mechanically verified synchronous Owner
session. `expires_at` may be earlier, but never later; channel loss, session end,
gate-process replacement, or failure of final presence reconfirmation expires
the token immediately. A token from one synchronous session is invalid in every
later process/session even if its wall-clock timestamp has not elapsed.

The gate also counts denied presentations for the same rehearsal. At cumulative
rejection count `N`, it freezes the rehearsal, closes the channel, and requires
fresh Owner agreement plus a new ceremony; it cannot reset the counter or ask a
model to keep trying. `N` is an Owner decision and remains unset below.

## 6. Token lifecycle and failure semantics

| State | Entry condition | Allowed next state | Runtime allowed? |
|---|---|---|---|
| `ABSENT` | default / no fresh Owner token | `ISSUED` only through chosen authorized ceremony | No |
| `ISSUED` | strong random token exists in the Owner/OOB ceremony but the gate has not accepted both Owner acts | `PRESENTED` or `EXPIRED` | No |
| `PRESENTED` | exact redacted Owner instruction and matching OOB token/response both validate against the frozen identifiers | `BURNED_DENY` or `BURNED_ATTEMPT` | No |
| `BURNED_DENY` | any binding/preflight/Owner-presence failure | terminal | No |
| `BURNED_ATTEMPT` | burn is durably committed immediately before the call | terminal after at most one start | At most one start |
| `EXPIRED` | expiration reached before verified burn | terminal | No |

There is no `RETRYABLE` state. “Invalid,” “expired,” and “already used” return a
single fail-closed denial class to callers; detailed reason codes may be visible
to the Owner but must not reveal token material. A known freshly issued token is
burned when a later gate fails. An unknown or forged string has no authoritative
token record to burn, but its presentation is denied and may be recorded using
only a non-reversible fingerprint.

## 7. Replay tests that count

A token is not “single-use” merely because a function returns an error twice.
The implementation package must include all of these mechanical proofs:

1. **Sequential replay:** first exact presentation results in one durable burn
   and exactly one fake-executor start; a second presentation of the same raw
   token and same packet returns consumed/deny, while executor start count stays
   exactly one.
2. **Concurrent replay:** two processes or independently locked contenders race
   the same token; exactly one can commit the burn and the executor start count
   is zero or one, never two.
3. **Restart replay:** after the first burn, reconstruct the gate in a fresh
   process and present the same token; denial must come from durable evidence.
4. **Crash boundary:** simulate crash after burn and before executor start;
   restart must deny and must not “finish” the missing call.
5. **Mismatch:** same token with changed packet/action/target/timeout is denied
   before any runtime start and cannot be reused with the original input later.
6. **Expiration:** advancing a controlled clock past expiry denies without call;
   clock uncertainty also denies.
7. **Redaction:** raw token is absent from audit bytes, exceptions, test output,
   reports, argv, environment snapshots, and fixtures.

The controlled test executor must be an in-memory counter, never OpenClaw. The
replay assertion is: **two presentations, one durable burn identity, at most one
executor invocation, and zero real runtime calls.**

## 8. Owner decision record

Owner-controlled OOB ingress (`OOB-A`, `OOB-B`, `OOB-C`, or separately reviewed
alternative): ____________________

Owner-controlled OOB egress (`E-A`, `E-B`, `E-C`, or separately reviewed
alternative): ____________________

Gate/generator OS principal or off-host location: ___________________________

Required channel-specific exclusion/authentication evidence: ________________

Token-production option (`T-A`, `T-B`, or `T-C`): ____________________

Burn/persistence option (`B-A` or `B-C`; `B-B` cannot stand alone): __________

Maximum validity window (must end no later than the synchronous session): ____

Cumulative rejection freeze threshold `N`: ____________________

Owner notes / required changes: ____________________________________________

Decision date and explicit implementation authorization: ____________________

Until every applicable field is filled by the Owner and converted into a
separate implementation brief, the token remains `null`, the gate remains
absent, and Phase 9 remains blocked.
