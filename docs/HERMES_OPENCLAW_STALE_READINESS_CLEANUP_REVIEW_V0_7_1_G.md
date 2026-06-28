# Hermes × OpenClaw Adapter — Stale Readiness Cleanup Review (v0.7.1-G)

> **Status: ADDITIVE.** This version adds a current-state regression aggregator,
> a policy document, and a self-readiness check. It does **not** modify, delete,
> or "repair" any historical readiness script, and it does not touch any app
> functionality.
>
> Boundary declarations for this version:
>
> - No app/main.py modification.
> - No queue_store.py modification.
> - No worker.py modification.
> - No result_sink.py modification.
> - No queue_intake_bridge_v0_7.py modification.
> - No security_gates_v0_7.py modification.
> - No approval_security_gate_v0_7.py modification.
> - No dashboard_intake_view_v0_7.py modification.
> - No templates modification.
> - No static modification.
> - No route wiring.
> - No new route.
> - No new POST handler.
> - No DB schema change.
> - No Worker start.
> - No OpenClaw execution.
> - No Hermes webhook.
> - No Google Sheets write.
> - No Queue status mutation.

---

## 1. Purpose

Several early plan-only readiness scripts (v0.7.1-A / C / C2 / D) now exit
non-zero on current master. This is **by design**: each was a frozen snapshot of
"what must not yet exist" at its own version, and later versions intentionally
delivered exactly those things.

This document and the accompanying current-state aggregator separate two
concerns:

1. **Historical readiness scripts** — version-time audit snapshots, kept as-is.
2. **Current-state regression** — a single aggregator that asserts what current
   master *should* look like, and is the regression gate going forward.

Key rulings recorded here:

- v0.7.1-G does not modify stale readiness scripts.
- v0.7.1-G does not delete historical readiness scripts.
- A / C / C2 / D are expected stale because later implementation versions intentionally superseded their negative assertions.
- Current-state aggregator is the regression gate for current master.
- Historical readiness scripts are preserved as version-time audit snapshots.
- Do not require stale plan-only readiness scripts to be green in current-state regression.

---

## 2. Current Master State

- HEAD = origin/master = `b5e698d86fdac7b4ef97aec077a1b7557366fd93` (v0.7.1-F2).
- Working tree clean; no v0.7 tag.
- Implemented (landed): B intake bridge, C3 dashboard badge wiring, D2 security
  gates, E intake gate wiring, F approval gate helper.
- Plan-only (no wiring): A, C2, D, F2.
- Not yet wired: F2-A (API approve route), F2-B (Dashboard approve route).

---

## 3. Why Stale Readiness Exists

Each plan-only readiness encodes negative assertions of the form "module X must
not exist in app/" or "app/main.py must not import Y". Those assertions are
correct **at that version**. When the next version ships the module or the
wiring, the earlier negative assertion necessarily flips to red. This is a
version-timing artifact, not a defect.

---

## 4. Readiness Execution Matrix

Observed on master `b5e698d`:

| Version | Readiness | Exit | Result |
|---------|-----------|------|--------|
| A  | controlled_queue_intake_plan | 1 | RED (expected stale) |
| B  | local_only_queue_intake_bridge | 0 | GREEN |
| C  | dashboard_intake_status_view_model | 1 | RED (expected stale) |
| C2 | web_dashboard_read_only_status_badges_plan | 1 | RED (expected stale) |
| C3 | web_dashboard_read_only_status_badges | 0 | GREEN |
| D  | kill_switch_audit_allowlist_plan | 1 | RED (expected stale) |
| D2 | local_only_security_gates | 0 | GREEN |
| E  | local_only_intake_security_gates | 0 | GREEN |
| F  | approval_to_queued_security_gate | 0 | GREEN |
| F2 | approve_route_wiring_plan | 0 | GREEN |

`compileall app scripts` → exit 0; `from app.main import app` → import OK.

---

## 5. Green Readiness Checks

B, C3, D2, E, F, F2. These already assert the landed-state correctly and pass on
current master. The current-state aggregator re-runs these as hard gates.

---

## 6. Expected-Stale Readiness Checks

A, C, C2, D. These are **expected red** on current master and are explicitly
excluded from the current-state regression gate (see the allowlist in section
13). They remain in the repository unchanged as historical snapshots.

---

## 7. Why A Is Expected Stale

v0.7.1-A (`check_..._controlled_queue_intake_plan_v0_7_1_a.py`) asserts that
app/ contains no intake implementation module. v0.7.1-B intentionally added
`app/queue_intake_bridge_v0_7.py`. Failure line:
`app/ 未新增 intake 實作模組（找到：['queue_intake_bridge_v0_7.py']）`.
Superseded by v0.7.1-B queue_intake_bridge_v0_7.py.

---

## 8. Why C Is Expected Stale

v0.7.1-C (`check_..._dashboard_intake_status_view_model_v0_7_1_c_readiness.py`)
asserts that the view-model is not wired into the web layer: `app/main.py 未
import dashboard_intake_view_v0_7` and `templates/task_detail.html 未加入 intake
顯示欄位`. v0.7.1-C3 intentionally wired both. Superseded by v0.7.1-C3 dashboard
wiring.

---

## 9. Why C2 Is Expected Stale

v0.7.1-C2 (`check_..._web_dashboard_read_only_status_badges_plan_v0_7_1_c2.py`)
is a plan-only badge plan asserting no wiring yet: `app/main.py 未含接線痕跡
「dashboard_intake_view_v0_7」`, `app/main.py 未含接線痕跡
「derive_intake_status_view」`, and `templates/task_detail.html 未加入 intake
badge`. v0.7.1-C3 intentionally delivered that wiring. Superseded by v0.7.1-C3
dashboard badge wiring.

---

## 10. Why D Is Expected Stale

v0.7.1-D (`check_..._kill_switch_audit_allowlist_plan_v0_7_1_d.py`) is a
plan-only version asserting app/ contains no security gate module: `app/ 未新增
security gate 模組（找到：['approval_security_gate_v0_7.py',
'security_gates_v0_7.py']）`. v0.7.1-D2 added `security_gates_v0_7.py` and
v0.7.1-F added `approval_security_gate_v0_7.py`. Superseded by v0.7.1-D2 and
v0.7.1-F security gate modules.

---

## 11. Historical Snapshot Policy

- Historical readiness scripts are preserved as version-time audit snapshots.
- They are never modified to pretend to be current-state, and never deleted.
- They document "what was true / forbidden at version N" and retain audit value.

---

## 12. Current-State Aggregator Policy

- Current-state aggregator is the regression gate for current master.
- It uses **positive** assertions describing how master should look now, plus a
  small set of boundary assertions (what must not yet be wired).
- It re-runs the green readiness scripts (B/C3/D2/E/F/F2) as hard gates.
- It does not run A/C/C2/D as hard gates; it only prints the expected-stale
  allowlist for transparency.
- Do not require stale plan-only readiness scripts to be green in current-state
  regression.

---

## 13. Expected-Stale Allowlist

```python
EXPECTED_STALE_READINESS = {
    "v0.7.1-A": "superseded by v0.7.1-B queue_intake_bridge_v0_7.py",
    "v0.7.1-C": "superseded by v0.7.1-C3 dashboard wiring",
    "v0.7.1-C2": "superseded by v0.7.1-C3 dashboard badge wiring",
    "v0.7.1-D": "superseded by v0.7.1-D2 and v0.7.1-F security gate modules",
}
```

---

## 14. Current-State Truths

On current master the aggregator asserts:

- All A–F2 docs exist; B/C3/D2/E/F modules exist.
- `app/main.py` contains C3 dashboard badge wiring (`dashboard_intake_view_v0_7`,
  `derive_intake_status_view`) and does **not** import `approval_security_gate_v0_7`.
- `templates/task_detail.html` contains the read-only intake/status badge markup.
- `app/queue_intake_bridge_v0_7.py` contains E intake gate wiring
  (`INTAKE_SECURITY_GATES_ENABLED`, `evaluate_security_gates`, `requested_tools`,
  `GLOBAL_KILL_SWITCH`).
- `app/security_gates_v0_7.py` exposes `evaluate_security_gates`,
  `evaluate_tool_allowlist`, `build_audit_event`, `redact_audit_metadata`.
- `app/approval_security_gate_v0_7.py` exposes `evaluate_approval_to_queued` and
  references `approval_security_gates_enabled`, `executable_by_worker`,
  `requested_tools`.
- `queue_store.py` / `worker.py` / `result_sink.py` do not import or call the
  approval gate.
- No `GOOGLE_SHEETS_ENABLED=true`, no real secrets, no v0.7 tag.

---

## 15. What The Aggregator Checks

- Artifact existence (docs + modules).
- Green readiness scripts B/C3/D2/E/F/F2 (subprocess, exit 0).
- Current implementation truths (C3 wiring, E wiring, security-gate symbols,
  approval-gate symbols).
- Boundary checks (approval gate not yet wired into main/queue_store/worker/
  result_sink; no F2-A/F2-B route wiring).
- Safety checks (no Sheets-enabled true, no full spreadsheet URL/ID, no real
  token/secret/key, no new `run_openclaw_cli` call site).
- Prints the expected-stale allowlist (informational only).

---

## 16. What The Aggregator Does Not Check

- It does not run A/C/C2/D as hard gates.
- It does not modify or repair stale scripts.
- It does not exercise the live approve route, worker, OpenClaw, Hermes, or
  Google Sheets.
- It does not read `.env`, credentials, tokens, or any secrets file.

---

## 17. Relationship To v0.7.1-F2

v0.7.1-F2 delivered the approve route wiring **plan** (plan-only). The aggregator
asserts that master is still at the F2 boundary: the approval gate helper exists
but is **not** wired into any route, queue_store, or worker. When a future
F2-A/F2-B lands, the aggregator's boundary assertions must be updated in lock
step.

---

## 18. Future Maintenance Rules

- When a new plan-only version ships, do not add it as a hard gate.
- When a plan-only version is later implemented, update the aggregator's positive
  assertions and add the now-superseded plan-only readiness to the expected-stale
  allowlist.
- Keep two distinct truths: aggregator = regression gate; historical readiness =
  audit snapshots (not required green).

---

## 19. Safety Boundaries

This version is purely additive (one doc + two scripts). It does not wire,
mutate, execute, or write anything in the running system. The aggregator is
read/observe-only and never transitions task state.

---

## 20. Security / Secrets Rules

- Do not read or display refresh tokens, client secrets, private keys, or full
  spreadsheet IDs.
- Sensitive checks use regex / format matching only.
- This version does not read `.env`, credentials, tokens, or any secrets file.

---

## 21. Explicit Non-goals

- No app/main.py modification.
- No queue_store.py modification.
- No worker.py modification.
- No result_sink.py modification.
- No queue_intake_bridge_v0_7.py modification.
- No security_gates_v0_7.py modification.
- No approval_security_gate_v0_7.py modification.
- No dashboard_intake_view_v0_7.py modification.
- No templates modification.
- No static modification.
- No route wiring.
- No new route.
- No new POST handler.
- No DB schema change.
- No Worker start.
- No OpenClaw execution.
- No Hermes webhook.
- No Google Sheets write.
- No Queue status mutation.
- No modification or deletion of any historical readiness script.

---

## 22. Final Recommendation

Adopt the current-state aggregator
(`scripts/check_hermes_openclaw_v0_7_1_current_state.py`) as the regression gate
for current master, and treat A/C/C2/D as expected-stale historical snapshots
that are preserved unchanged. Keep the aggregator's positive and boundary
assertions in sync with future implementation versions (F2-A/F2-B onward), and
never require stale plan-only readiness scripts to be green in current-state
regression.
