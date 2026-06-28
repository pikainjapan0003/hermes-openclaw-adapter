# Hermes × OpenClaw Adapter — Queue Task Annotation / Approval Readiness Plan (v0.7.2-F-A)

> **Status: PLAN ONLY.** This document plans future Queue Task Annotation and an
> Approval Readiness model so the Owner can judge each task safely. It implements
> nothing, commits nothing, pushes nothing, and migrates no schema.
>
> Boundary declarations:
>
> - This is planning only.
> - No QueueStore runtime behavior changes.
> - No approval wiring changes.
> - No Worker execution.
> - No OpenClaw call.
> - No Hermes call.
> - No Google Sheets write.
> - No secrets read.
> - No webhook.
> - No external side effects.
> - No schema migration in this segment.
> - No demo task cleanup in this segment.

---

## 1. Purpose

Plan a richer, **annotation-driven** view of each queue task plus an explicit
**Approval Readiness** model, so the Owner can answer — at a glance and safely —
"where did this come from, why does it need me, how risky is it, can I approve it,
and what happens next?". This is design planning; no code changes here.

---

## 2. Current baseline

Current master = cc8807d7eca86cda360c12b1e76fcbad8e37ee6a.

- QueueStore schema columns: `task_id`, `created_at`, `updated_at`, `status`,
  `title`, `task_text`, `safety_level` (INTEGER), `attempts`, `max_attempts`,
  `error`, `result_ref`, `correlation_id`, `payload` (JSON TEXT).
- Task statuses: queued, running, completed, failed, cancelled, waiting_review,
  rejected, archived. Initial allowed: queued, waiting_review.
- `safety_level` is a column; `requires_confirmation`, `risk_level`,
  `source_mode`, `executable_by_worker`, `approval_status` currently live inside
  `payload.metadata` and are surfaced read-only via
  `app/dashboard_intake_view_v0_7.py` (`derive_intake_status_view`).
- Approval routes (`/dashboard/tasks/{id}/approve|reject` and
  cancel/retry/archive) only drive the QueueStore state machine; they never start
  the Worker and never call OpenClaw.
- `app/auto_approval_policy_v0_7.py` already defines a policy decision enum
  (`auto_approved` / `needs_owner_approval` / `prohibited`) and explicitly notes
  that `auto_approved` "仍不可執行、不可 queued" — i.e. policy decision is already
  conceptually separate from execution.
- The Owner Review Panel (UI-E) shows: task id, title, safety_level / risk,
  requires_confirmation, current status, created at, and the intake snapshot.

Safe posture: Dashboard read-only; Worker OFF / not running; OpenClaw Not
Connected; Hermes Not Connected; Google Sheets Disabled; no external side effects.

---

## 3. Why this is still v0.7.2

This remains presentation + decision-support, not execution. It adds annotation
and an approval *readiness* signal to help the Owner decide; it does not wire
approval to execution, change the Worker, or connect any external system. The
v0.7.x safety envelope (read-only / local-only / Owner-gated) is unchanged.

---

## 4. Queue task annotation goal

Give each task a consistent, human-readable annotation set that explains its
origin, the reason Owner review is needed, its risk and side-effect profile, the
next step if approved, and whether it can only run as dry-run / mock — so the
Owner never has to infer safety from sparse fields.

---

## 5. Owner problem

Today the Owner must infer intent and risk from `safety_level`, a derived
`approval_status`, and free-text. There is no explicit provenance (who/where it
came from), no explicit "why owner is required", no explicit
approve-then-what, and no explicit "will this cause an external side effect"
marker. That makes confident approval hard.

---

## 6. Proposed annotation fields

Future, **planned** annotation fields (stored in `payload.metadata`, surfaced
read-only; not added in this segment):

| Field | Meaning |
| --- | --- |
| `task_origin` | Where the task originated (e.g. owner-cli, hermes-intake, dashboard, demo). |
| `requested_by` | Who/what requested it (identity label, not a secret). |
| `request_channel` | Channel of arrival (local, mock, replit-local, etc.). |
| `owner_reason` | Why this task needs Owner review, in plain language. |
| `approval_readiness` | The readiness state (see section 7). |
| `approval_blockers` | List of concrete reasons it is not yet approvable. |
| `risk_summary` | Human-readable risk explanation. |
| `side_effect_summary` | What external effects it *would* have if executed. |
| `next_step_if_approved` | What happens after approval (still gated). |
| `execution_mode` | Planned execution mode (dry-run / mock / real). |
| `external_touchpoints` | External systems it would touch (OpenClaw/Hermes/Sheets/none). |
| `dry_run_available` | Whether a dry-run path exists. |
| `mock_available` | Whether a mock path exists. |
| `rollback_note` | How to undo / that it is not auto-undoable. |
| `human_readable_summary` | One-paragraph plain summary for the Owner. |

All fields are **annotation/metadata only** — display and decision-support. They
do not, by themselves, grant execution.

---

## 7. Proposed approval readiness model

A conservative `approval_readiness` state machine (planned enum, display-only):

| State | Meaning |
| --- | --- |
| `not_ready` | 資訊不足，Owner 不應核准 (information insufficient; do not approve). |
| `owner_review_required` | 需要 Owner 看過，但還可能缺資料 (needs Owner review; may still lack data). |
| `ready_for_owner_decision` | 資訊足夠，Owner 可做核准/拒絕判斷 (enough info to decide). |
| `blocked_by_policy` | 被安全政策擋住，不應核准 (blocked by safety policy). |
| `prohibited` | 禁止執行 (prohibited). |

Mapping intent (planned): align with `auto_approval_policy_v0_7` —
`needs_owner_approval` → `owner_review_required` / `ready_for_owner_decision`
depending on annotation completeness; `prohibited` → `prohibited`; protected/policy
hits → `blocked_by_policy`.

> **Approval readiness is not execution permission.**
> **Owner approval does not automatically imply Worker execution.**
> Future implementation must keep approval decision and execution dispatch separate.

---

## 8. Proposed risk explanation model

`risk_summary` + `side_effect_summary` translate `safety_level` / risk into plain
language: what could go wrong, what it would touch, and whether the effect is
reversible. Severity tiers map to existing `safety_level` (0–3+) without changing
the column. This is explanation, not new enforcement.

---

## 9. Proposed source / origin model

`task_origin` + `requested_by` + `request_channel` give provenance so the Owner
knows whether a task came from a trusted local CLI, a mock fixture, a demo seed,
or a (future) Hermes intake. Provenance is descriptive metadata; it must never
embed secrets.

---

## 10. Proposed next-step explanation model

`next_step_if_approved` states, in plain language, what approval *queues* (not
executes), e.g. "approve → status becomes queued; Worker remains OFF; execution
is a separate, future, explicitly-dispatched step." This reinforces the
decision/execution separation from section 7.

---

## 11. Proposed dry-run / mock / real boundary model

`execution_mode` + `dry_run_available` + `mock_available` + `external_touchpoints`
make the current safe default explicit: tasks are local-only / mock / dry-run
unless and until a future, separately-approved real-execution path exists. The
annotation surfaces this; it does not enable real execution.

---

## 12. Dashboard / Owner Review Panel display impact

When implemented (future segment), the Owner Review Panel and task detail would
show: `human_readable_summary`, `approval_readiness`, `approval_blockers`,
`risk_summary`, `side_effect_summary`, `task_origin` / `requested_by`,
`next_step_if_approved`, and the dry-run/mock/real markers — all read-only,
Chinese-first with English sublabels, reusing existing UI-D/UI-E styles. No new
route is required for display.

---

## 13. QueueStore compatibility plan

Annotations live inside the existing `payload` JSON (`payload.metadata`), so the
SQLite schema does not change. `derive_intake_status_view` (or a sibling
read-only deriver) would compute display values, defaulting safely (unknown →
conservative). No new columns, no `QueueStore` runtime behavior change.

---

## 14. Backward compatibility

Tasks without the new annotation fields must render safely: missing →
`approval_readiness = not_ready` or `owner_review_required`, missing origin →
"unknown", missing dry-run/mock flags → treated as not available. Old tasks
remain valid; nothing is rewritten.

---

## 15. Data migration stance

No schema migration in this segment, and ideally none ever for this feature:
annotations are JSON metadata. If a future segment wants indexed columns, that is
a separate, explicitly-approved migration plan — out of scope here.

---

## 16. Safety boundaries

- This is planning only.
- No QueueStore runtime behavior changes.
- No approval wiring changes.
- No Worker execution.
- No OpenClaw call.
- No Hermes call.
- No Google Sheets write.
- No secrets read.
- No webhook.
- No external side effects.
- No schema migration in this segment.
- No demo task cleanup in this segment.
- Approval readiness is not execution permission.
- Owner approval does not automatically imply Worker execution.
- Future implementation must keep approval decision and execution dispatch separate.

Current safe posture (display-only): Worker OFF / not running; OpenClaw Not
Connected; Hermes Not Connected; Google Sheets Disabled.

---

## 17. Non-goals

UI/annotation v0.7.2-F-A explicitly does not:

- Implement annotation fields, derivers, or UI (plan only).
- Change approval wiring or any POST action behavior.
- Change QueueStore runtime behavior, add routes, or migrate schema.
- Start the Worker, call OpenClaw, call Hermes, or write Google Sheets.
- Read secrets, create webhooks, or add any external dependency.
- Seed (`--apply`) or clean up the demo task.

---

## 18. Implementation phases

Planned future phases (each requires explicit Owner approval to start):

1. **F-B (deriver, read-only):** add a pure annotation deriver + unit tests; no
   UI, no writes.
2. **F-C (display):** surface annotations in Owner Review Panel / task detail
   (templates + CSS only).
3. **F-D (authoring, optional):** allow annotations to be set at intake time via
   `payload.metadata` (no schema change).
4. **F-R (closeout):** current-state record + readiness.

Execution dispatch wiring is explicitly **not** in this feature line.

---

## 19. Readiness criteria

Before any implementation phase begins:

- The annotation field set and `approval_readiness` enum are Owner-approved.
- The deriver is specified as pure / read-only with conservative defaults.
- The decision/execution separation is restated in the implementing segment.
- Backward-compatibility defaults are defined for annotation-less tasks.

---

## 20. Risks

- **Over-trust:** a readiness label could be misread as permission — mitigated by
  the explicit "approval readiness is not execution permission" rule and keeping
  the deriver conservative.
- **Annotation drift:** metadata could go stale — mitigated by deriving display
  values at render time, not caching.
- **Scope creep into execution** — mitigated by the boundary block, section 17,
  and the readiness script's forbidden-pattern checks.
- **PII / secrets in provenance** — mitigated by the rule that provenance is
  labels only, never secrets.

---

## 21. Acceptance criteria

v0.7.2-F-A (this plan) is accepted when:

1. This plan exists at the documented path and contains sections 1–21.
2. The readiness script
   `scripts/check_hermes_openclaw_queue_task_annotation_approval_readiness_plan_v0_7_2_f_a.py`
   exists and reports ALL PASS.
3. The plan defines the annotation fields (section 6) and the `approval_readiness`
   model (section 7), including the decision/execution separation statements.
4. The plan states Non-goals, the QueueStore compatibility / no-migration stance,
   and the safety boundaries.
5. The plan carries no external side effects and no secrets.
6. Nothing is implemented, committed, pushed, or tagged in this segment without
   Owner approval.
