# HERMES_OPENCLAW_DASHBOARD_ROOT_REDIRECT_REPLIT_SMOKE_PLAN_V0_7_2_UI_B

Version: v0.7.2-UI-B
Status: Implementation
Depends on: v0.7.2-UI-A (Dashboard Route Readiness Review)

---

## 1. Purpose

v0.7.2-UI-B only adds root redirect to /dashboard.

The sole change is adding `GET /` → 303 redirect to `/dashboard` in `app/main.py`.
This eliminates the bare 404 a user encounters when visiting the app's root URL.

---

## 2. UI-A Findings

UI-A (v0.7.2-UI-A) performed a full route audit against master commit
020e6c75aa4ad96bd38735b5fe017e477e72dd87 and found:

- `/dashboard` is registered and functional.
- `/dashbord` (typo, missing 'a') returned 404 — this is correct behaviour.
- `/` (root) returned 404 — this is the gap addressed here.
- `DASHBOARD_AUTH_ENABLED=true` in the Replit environment causes `/dashboard`
  to 303-redirect to `/dashboard/login` for unauthenticated requests.

---

## 3. /dashboard Exists

`GET /dashboard` (handler: `dashboard_home`) is registered in `app/main.py`
and backed by `templates/dashboard.html`, `static/dashboard.css`, and
`app/dashboard_intake_view_v0_7.py`.

No route change to `/dashboard` itself is made in UI-B.

---

## 4. /dashbord Is Typo

`/dashbord` (missing 'a') is a user typo, not a missing route.
v0.7.2-UI-B does not add a `/dashbord` alias or any redirect for it.
Typo aliases are not supported to avoid route pollution.

---

## 5. Root / Currently 404

Prior to UI-B, `GET /` returned 404 because no root route was registered.
FastAPI returns `{"detail":"Not Found"}` for unregistered paths.

---

## 6. Root Redirect Decision

Owner approved adding a single root route in `app/main.py`:

```python
@app.get("/")
def root() -> RedirectResponse:
    return RedirectResponse(url="/dashboard", status_code=303)
```

303 See Other is used for consistency with the existing dashboard auth redirect
pattern already in `app/main.py`.

---

## 7. Auth Redirect Behavior

When `DASHBOARD_AUTH_ENABLED=true` (set via Replit Secrets), the dashboard
auth middleware intercepts all `/dashboard/*` paths that are not exempt:

```
GET / → 303 /dashboard → (middleware) 303 /dashboard/login
```

The user must authenticate at `/dashboard/login` with the `DASHBOARD_TOKEN`
secret. Once authenticated, a httpOnly cookie is set and subsequent requests
to `/dashboard` are served directly.

When `DASHBOARD_AUTH_ENABLED=false` (default in code), the root redirect
leads directly to the dashboard page:

```
GET / → 303 /dashboard → 200 dashboard.html
```

---

## 8. Replit-local .replit Overlay

The Replit platform maintains a local `.replit` file that may differ from
the committed version. This file is always shown as `M .replit` in
`git status` within Replit.

v0.7.2-UI-B does not modify `.replit`.
`.replit` is not staged or committed.

---

## 9. .claude Local Metadata

The `.claude/` directory is a session-local metadata directory created by the
Claude Code CLI. It is untracked (`?? .claude/`) and is not staged or committed.

---

## 10. Browser Smoke Test Plan

After deploying UI-B, the following manual checks should be performed in a
browser against the Replit public URL:

1. Visit `https://<replit-url>/` — expect redirect to `/dashboard` or
   `/dashboard/login` (depending on auth setting).
2. Visit `https://<replit-url>/dashboard` — expect dashboard overview page
   or login redirect.
3. Visit `https://<replit-url>/dashboard/login` — expect login form if auth
   enabled; redirect to dashboard if auth disabled.
4. Visit `https://<replit-url>/dashbord` — expect 404 (intentional; typo not
   supported).
5. If auth enabled: submit correct `DASHBOARD_TOKEN` at `/dashboard/login`,
   verify redirect to `/dashboard` with overview content.
6. Verify nav links (Tasks, Reviews, System) work from the dashboard overview.

No Worker, OpenClaw, Hermes, or Google Sheets interaction is required for
these smoke tests.

---

## 11. Dashboard Visual Design Future Work

v0.7.2-UI-B does not redesign dashboard visuals.
v0.7.2-UI-B does not add approve-route behavior.

Potential future work (v0.7.2-UI-C or later):
- Intake gate status badges on the dashboard overview page.
- Auto-approval policy decision display on task detail.
- Enhanced filtering/sorting on `/dashboard/tasks`.
- Owner Control Room panel for manual approval queue.

These are deferred until Owner approves a visual design scope.

---

## 12. Not Connected Boundaries

The following components remain untouched and unconnected in UI-B:

- `app/queue_store.py` — not imported or called.
- `app/worker.py` — not imported or called.
- `app/result_sink.py` — not imported or called.
- `app/approval_security_gate_v0_7.py` — not wired to any route.
- `app/auto_approval_policy_v0_7.py` — not wired to any route.
- `app/queue_intake_bridge_v0_7.py` — not changed.
- `app/security_gates_v0_7.py` — not changed.
- `templates/` — not modified.
- `static/` — not modified.

---

## 13. No Worker / OpenClaw / Hermes

v0.7.2-UI-B does not start Worker.
v0.7.2-UI-B does not call OpenClaw.
v0.7.2-UI-B does not call Hermes.

---

## 14. No Google Sheets Live Write

v0.7.2-UI-B does not write Google Sheets.

---

## 15. No Secrets Read

v0.7.2-UI-B does not read or display secrets.
No `DASHBOARD_TOKEN`, `GOOGLE_*`, `refresh_token`, `client_secret`, or
`private_key` values are accessed or logged.

---

## 16. Future v0.7.2-UI-C

After Owner reviews the browser smoke test results, a potential v0.7.2-UI-C
may address:

- Dashboard overview enhancements (intake status, auto-approval decision display).
- Owner Control Room: dedicated approve/reject UI for `waiting_review` tasks.
- Any visual polish items surfaced during smoke testing.

v0.7.2-UI-C scope and implementation require explicit Owner approval.
