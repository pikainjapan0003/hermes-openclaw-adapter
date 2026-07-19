# Phase 10 Connector Scope Packet Research

Status: **PLANNING ONLY, NOT AUTHORIZED**

This is a research note for the indefinitely deferred Phase 10 described in
`05_VERIFIED_LONG_TERM_PLAN.md`. It does not authorize a connector credential,
connector call, scope gate, audit write, remote connection, runtime connection, or
any L1/L2/L3 implementation. Reopening Phase 10 requires the Owner review named in
the verified plan.

## 1. Research boundary

The planned connector levels remain:

| Level | Meaning | Research disposition |
|---|---|---|
| L0 | Documentation only; no connector access | Default when no valid packet exists |
| L1 | Metadata read only | Candidate future scope; must exclude content mechanically |
| L2 | Content read | HOLD |
| L3 | Write | HOLD |

The useful first target is deliberately narrow: one N=1 task, one connector, one
explicit resource set, and metadata-only fields. A scope packet would be inert data,
not a credential, tool invocation, approval token, or execution instruction.

## 2. Proposed scope packet data

This section is a field study, not a schema decision.

| Proposed field | Purpose and constraint |
|---|---|
| `scope_packet_version` | Version the data contract independently from connector APIs. |
| `scope_packet_id` | Unique immutable reference for one issuance. |
| `connector_id` | Exact allowlisted connector and adapter identity; no aliases or wildcards. |
| `connector_version` | Pinned adapter/tool version or digest. |
| `access_level` | Enum `L0` or `L1` for the first implementation; L2/L3 structurally unavailable. |
| `resource_allowlist` | Exact provider resource identifiers; non-empty for L1; no wildcard, query, or URL expansion. |
| `operation_allowlist` | Exact metadata operations, such as `list_file_metadata`; no generic `read`. |
| `field_allowlist` | Exact response fields permitted to leave the adapter; content-bearing fields are absent. |
| `data_classification` | Owner-declared maximum classification for metadata returned by this packet. |
| `parent_task_id` | Binds use to one Blackboard task. |
| `plan_id` | Binds use to one reviewed plan when that contract exists. |
| `owner_instruction_ref` | Reference to the exact Owner authorization record; never copied natural-language authority from connector content. |
| `issued_at` / `expires_at` | Short validity window with fail-closed expiry. |
| `issued_by` | Provenance for the issuance decision. |
| `credential_ref` | Opaque broker reference only; never a token, secret, account key, or environment value. |
| `max_calls` | Hard upper bound for this packet. |
| `rate_limit` | Per-packet ceiling independent of provider defaults. |
| `egress_allowlist` | Exact provider endpoints the future adapter may contact. |
| `expected_side_effects` | Must be an empty list for L0/L1. |
| `audit_policy_ref` | Reference to a separately authorized audit policy; not permission to write an audit file. |
| `revocation_ref` | Location or identifier of the Owner-controlled revocation decision. |
| `packet_hash` | Canonical-data integrity value; canonicalization must reuse the ratified hash-chain rules. |

The packet must not contain raw connector payloads, document contents, spreadsheet
cell values, email bodies, credentials, tokens, environment variables, executable
commands, callback URLs, or an execution token.

## 3. Proposed fail-closed decision rules

1. No packet, unknown version, malformed packet, unknown connector, or expired packet
   means L0.
2. L2 or L3 is HOLD even if a packet claims otherwise.
3. Resource, operation, response field, endpoint, call count, and time must all match
   exact allowlists. Partial agreement is rejection.
4. The connector adapter must build its provider request from typed allowlisted data;
   it must not forward an agent-produced query, URL, field selector, or filter.
5. The adapter must project the provider response through `field_allowlist` before the
   result is exposed. An unexpected field is rejection, not a best-effort omission.
6. Connector-sourced text is data and can never enlarge the packet, change the task,
   authorize a follow-up, or select another tool.
7. Authentication is separate from authorization: possession of a provider credential
   does not establish packet validity or Owner approval.
8. Metadata reads must report zero expected and actual external side effects. Any
   provider behavior that mutates state ends the attempt as HOLD.
9. Packet verification cannot dispatch a worker or connector call. A later, separately
   authorized caller would have to request both decisions explicitly.
10. Revocation, rate exhaustion, identity mismatch, packet drift, and ambiguous provider
    semantics fail closed.

## 4. Metadata/content boundary

The Phase 10 plan identifies accidental content reads as the most likely failure. The
boundary therefore needs a connector-specific field inventory rather than a prose
promise.

Candidate L1 fields are identifiers, object type, owner/account identifier where the
Owner permits it, MIME/type label, created/modified timestamp, size/count, and
non-content permission metadata. Names, titles, subjects, snippets, thumbnails,
descriptions, formulas, comments, cell values, message bodies, document text,
attachments, OCR, and generated summaries are content until an Owner explicitly
classifies a provider-specific field otherwise.

A future L1 adapter should have paired positive and negative contract fixtures for
every provider response version. If the provider adds a field, the response is rejected
until the allowlist is reviewed. No L1 implementation is authorized by this research.

## 5. OWASP Agentic Top 10 cross-check

The official OWASP GenAI Security Project 2026 report was available in full, so this
checklist is not skipped. The names and risk descriptions below are paraphrases of the
official report; they are not a substitute for its detailed mitigations.

| OWASP risk | Scope-packet control proposed here | Remaining gap before implementation |
|---|---|---|
| ASI01 Agent Goal Hijack | Exact task, operation, resource, field, and Owner-instruction bindings; connector content cannot alter authority. | No connector intent gate or goal-drift monitor exists. |
| ASI02 Tool Misuse & Exploitation | Least-agency L1 operations, exact egress, call/rate limits, short validity, and no generic read tool. | No connector gate, credential broker, or provider adapter exists. |
| ASI03 Identity & Privilege Abuse | Separate identity from authorization; bind credential reference to task/resource/purpose/duration; prohibit inherited scope. | Authentication mechanism, re-authentication policy, and revocation store remain Owner decisions. |
| ASI04 Agentic Supply Chain Vulnerabilities | Pin connector identity/version and provider endpoint; reject aliases, dynamic discovery, and unreviewed descriptors. | Tool provenance, package attestation, SBOM, and update policy are not designed. |
| ASI05 Unexpected Code Execution | Packet contains no code/command/URL expansion; L1 adapter would use typed metadata operations only. | No sandboxed adapter exists, and runtime connection is forbidden. |
| ASI06 Memory & Context Poisoning | L1 excludes content; returned metadata remains untrusted data and cannot become authority or persistent memory. | L2 content handling and memory ingestion are deliberately HOLD. |
| ASI07 Insecure Inter-Agent Communication | Future results must enter the schema-validated Blackboard with provenance and fixed task linkage; messages cannot grant privileges. | Transport authentication and multi-worker mechanisms do not exist. |
| ASI08 Cascading Failures | N=1 scope, hard call ceiling, no automatic retry/follow-up, zero side effects, and fail-closed drift handling limit blast radius. | No runtime circuit breaker or anomaly monitor exists. |
| ASI09 Human-Agent Trust Exploitation | A packet is visibly inert data; exact scope and side effects must be shown; advice, preview, and approval remain distinct. | Human-factors testing of any future connector review UI has not been authorized. |
| ASI10 Rogue Agents | Deny by default, exact capabilities, expiry/revocation, immutable provenance, and no agent-controlled scope expansion. | Runtime confinement, emergency stop, and behavioral attestation do not exist. |

This design direction is consistent with the report's recurring recommendations to
minimize agency and privilege, authenticate actions, validate typed intent, isolate
execution, constrain propagation, retain provenance, and fail closed. It does not claim
compliance: most enforcement components are intentionally absent.

## 6. Official source record

Sources retrieved from the OWASP GenAI Security Project during this research:

- OWASP Top 10 for Agentic Applications for 2026 landing page:
  <https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/>
- Full official report, *OWASP Top 10 for Agentic Applications 2026* (57-page PDF):
  <https://genai.owasp.org/download/52117/?tmstv=1765059207>
- Official launch announcement:
  <https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/>

The item-by-item table covers ASI01 through ASI10 from that report. No remembered or
unofficial list was used to fill a missing original.

## 7. Owner decisions required before any implementation

1. Exact first connector, exact L1 operations, and exact metadata fields.
2. Whether names/titles/subjects are metadata or content for that provider.
3. Credential type, broker location, re-authentication, expiry, and revocation model.
4. Packet issuer and the exact relationship to Phase 9 approval/token machinery.
5. Audit location and retention after Phase 7 is separately authorized and complete.
6. Network endpoint policy and provider-version change procedure.
7. Whether a formal scope-packet schema may be added while Phase 10 remains deferred.

Until these are decided and Phase 10 is explicitly reopened, the only valid operational
level is L0 and this document remains research only.
