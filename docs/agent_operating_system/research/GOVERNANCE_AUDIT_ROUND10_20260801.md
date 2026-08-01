# Governance Audit Round 10 — 2026-08-01

**REVIEW ONLY — FINDINGS RECORDED, NOTHING FIXED OR AUTHORIZED**

## Scope and method

This fresh-context review checked the current front door (`README.md`), the
core safety and plan files (`00`, `01`, `05`, `07`, `09`, `11`, `12`, `13`,
`14`), the preflight catalog, and the v1.1/`produced_by` impact summaries. It
looked for stale current-state claims, path/reference drift, option relabeling,
and sentences that a weak implementation agent could read as permission. It
also checked that the new v2 planning artifacts carry explicit non-authorizing
status and leave Owner fields blank.

This report does not repair any finding, choose AUD/RB/PB/ROOT, change a
schema, create persistence, or authorize Phase 7/9/v1.1/v1.2 work.

## Findings

| ID | Severity | Location | Finding |
|---|---|---|---|
| R10-01 | P2 | `README.md:6-16` | The opening architecture diagram presents `POST /tasks/dispatch`, the OpenClaw CLI, and `data/results.jsonl` before the current-state safety banner. The diagram is an intended historical topology, but it is not labelled as historical/planning at the point a new reader sees it. A weak model can therefore treat the top diagram as an active dispatch path, contradicting the current read-only/no-runtime status. |
| R10-02 | P2 | `README.md:254-263` | The API table lists `POST /tasks/dispatch` and an adapter token without a local historical/planning heading. The v0.4 history heading is much earlier, so a reader jumping to the API section can infer that the POST route and token are current. This is a documentation boundary defect, not evidence that a new route was added. |
| R10-03 | P3 | `docs/agent_operating_system/research/PREFLIGHT_CONDITION_CATALOG_V2.md` versus `09_N1_PREFLIGHT_RUNBOOK.md` and `research/PREFLIGHT_CONDITION_CATALOG.md` | The v2 catalog is an accurate additive summary, but the authoritative runbook and original catalog do not point to it. A fresh reader may use either catalog without knowing which is the latest wording. No condition or gate is changed; an index/cross-reference update would be a later docs-only repair. |
| R10-04 | P3 | `11_V1_1_FIRST_REAL_WRITE_DESIGN.md:90-113,210-230` and `14_V1_2_FIRST_CODE_TASK_DESIGN.md:180-208` | Future token/write/revert steps are written as imperative rehearsal sequences. File-level planning banners and hard-gate text are present, so this is not an authorization defect today, but copied subsections could be mistaken for an executable runbook unless every excerpt retains the planning boundary. |

No P0 or P1 finding was identified. No current product code, route, schema,
token value, writer, dispatch path, or runtime connection was found or changed
by this review.

## Option and gate consistency

| Topic | Result |
|---|---|
| AUD/RB | A/B/C labels and recommendations remain aligned with the v1.1 source; Owner fields remain blank. |
| `produced_by` | Enum, namespace/registry, and policy-only options remain distinct; no option is treated as authentication. |
| ROOT/projection | The `parent_task_id: null` limitation remains disclosed; no guessed mapping was added. |
| Phase 7 | Writer and persistent audit path remain absent and unauthorized. |
| Phase 9 | Null-token contract, absent gate, absent writer, and synchronous Owner requirement remain blockers. |
| Night-batch boundary | Findings are recorded only; this report adds no implementation authorization. |

## Resolution disposition

R10-01 through R10-04 are open documentation findings. They are deliberately
not fixed in this review package. A future repair must preserve the historical
record, add an explicit current/historical boundary at the point of use, and
run the documentation drift and cross-reference tests. Any repair that would
touch a current route, schema, token contract, or runtime remains out of scope.
