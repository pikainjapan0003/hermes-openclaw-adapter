# Core Document Review — 00 Round 2

Status: **review complete; environment facts corrected; safety-semantic changes
remain proposals only.** This review does not authorize execution, persistence,
runtime wiring, token changes, or a change to an Owner gate.

## Method

All problem cards D-01 through D-18 in `00_QUICK_DIAGNOSIS.md` were reread
against the current repository structure and the current 01/05/40 governance
boundary. Environment/inventory facts that were demonstrably historical were
corrected in 00. Anything that could change authorization or safety meaning is
listed below and was not edited.

## Per-card disposition

| Card | Disposition | Round-2 result |
|---|---|---|
| D-01 | Environment wording fixed | Historical document counts no longer masquerade as a current inventory. Canonical safety source remains 01. |
| D-02 | Environment wording fixed | Historical script counts are labelled; the schema-test example now points to the existing test and F7 profiles. |
| D-03 | Proposal only | Its “instruction wins over plan” sentence can conflict with batch instructions that explicitly make 05 authoritative. Do not change precedence without Owner governance review. |
| D-04 | Environment wording fixed | Mutable README/doc counts were removed; the current-state route through 05 §5 remains intact. |
| D-05 | No change | Routing remains a governance rule, not an environment fact. |
| D-06 | Environment wording fixed; proposal open | Mutable file counts were removed. The mandatory delegation threshold is orchestration policy and must not be changed by this package. |
| D-07 | No change | Fresh-context/adversarial review remains aligned with the batch-review model. |
| D-08 | Proposal only | The sample authorization-block syntax and named target file are safety semantics. They require a dedicated review before any wording change. |
| D-09 | No change | Current null-token override and legacy real-capability exceptions are explicit. |
| D-10 | Proposal only | The scope-packet levels remain Phase-10 planning; no implemented schema or connector permission may be inferred. |
| D-11 | No change | Freshness rules already defer to tools actually available in the active session. |
| D-12 | No change | It correctly limits Replit evidence to HTTP reachability and deployed hash unknown. |
| D-13 | Proposal only | “Write a scratch file” can exceed a package whitelist. Future wording should require that the active instruction authorize the handoff location. |
| D-14 | Proposal only | Automatic lesson-file edits after every incident can exceed scope; keep as historical guidance pending governance wording. |
| D-15 | No change | It names roles/capability, not a hard-coded current model SKU. |
| D-16 | Environment wording fixed | Removed the false invariant that the repo always lives in WSL; checkout proof is now host-neutral. |
| D-17 | Proposal only | Missing phase mapping and stop/ask behavior are authorization semantics. |
| D-18 | No change | The truncation sentinel remains a fail-closed historical protocol. |

## Findings requiring later decision

| ID | Severity | Location | Finding |
|---|---|---|---|
| C00R2-01 | P2 | D-03 | Precedence wording can contradict an issued package that designates 05 as source of truth. |
| C00R2-02 | P2 | D-08, D-17 | Authorization-block and phase-mapping syntax are historical conventions, not proof that every current Owner instruction uses them. |
| C00R2-03 | P3 | D-10 | The four connector levels are still planning language without an executable scope-packet contract. |
| C00R2-04 | P3 | D-13, D-14 | Emergency/lesson “write” instructions need an explicit active-whitelist precondition. |

No P0/P1 finding was found. The direct edits in 00 only remove stale
environment assumptions; they do not resolve these four safety-semantic items.
