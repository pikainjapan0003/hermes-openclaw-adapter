# Hermes x OpenClaw — Jarvis Owner Control Room Visual Design Plan (v0.7.2-UI-C)

> **Plan only.** This document is a *visual design plan*. v0.7.2-UI-C does not
> implement, commit, or push any UI change. It describes the target look for a
> later implementation pass and records strict boundaries so the safety posture
> of the read-only dashboard is preserved.

---

## 1. Purpose

The Owner asked for a "Jarvis-style" / Iron-Man HUD / command-center feeling for
the Hermes x OpenClaw dashboard — a **Owner Control Room** that *looks* like a
futuristic command deck while staying **clear, readable, and safe**.

This plan extracts **only the UI/UX visual elements** from the attached research
report's "科技感 Jarvis dashboard" material. It deliberately adopts **none of the
functional integrations** (no API, no LLM, no WebSocket, no voice, no 3D engine,
no external data feeds). The current dashboard is **Jinja templates + a single
static CSS file**, and any later implementation should stay within that stack.

The output of UI-C is two artifacts:

1. this design plan, and
2. a readiness check script that verifies the plan exists and is complete and
   that it carries **no external side effects** and no secrets.

UI-C produces **no runtime behavior change**.

---

## 2. Current dashboard UI inventory

Read-only inventory of what exists today (repo is the source of truth):

| File | Role |
| --- | --- |
| `templates/base.html` | Shell: `.topbar` title + `Read-only Dashboard` badge, `.nav` (Overview / Tasks / Reviews / System / Logout), `.content` block, footer note. |
| `templates/dashboard.html` | Overview: three `.card`s — System Health (kv table), Queue Counts (badges), Quick Links. |
| `templates/login.html` | Dashboard token login form (`DASHBOARD_AUTH_ENABLED`). |
| `templates/tasks.html` | Task list with status filter pills + grid table. |
| `templates/task_detail.html` | Single task view + comments. |
| `templates/reviews.html` | Pending reviews / approval surface. |
| `templates/system.html` | System health detail. |
| `static/dashboard.css` | The only stylesheet. Light theme (`#f2f4f7` bg, dark `#20232a` topbar). Defines `.card`, `.badge-*`, `.nav`, tables, buttons, mobile rules. No framework, no CDN, no external font. |
| `app/main.py` dashboard routes | `/` → 303 → `/dashboard`; `/dashboard`, `/dashboard/tasks`, `/dashboard/reviews`, `/dashboard/system`, `/dashboard/login`, `/dashboard/logout`. Auth middleware at `_dashboard_auth_middleware`. |
| `app/dashboard_intake_view_v0_7.py` | Read-only intake status view model. |

Key current facts that constrain the redesign:

- The theme is **light**. Jarvis is **dark**. UI-C proposes a dark cockpit theme.
- All visuals come from **one CSS file** + inline Jinja. No JS bundle exists.
- The dashboard is **Read-only**; it only reads `/queue/*` observability data.

---

## 3. Design reference extracted from research report

UI-C uses **only** the UI/UX visual elements from the research report. **No
functional integration is adopted.** Extracted, allowed visual elements:

1. Dark background ("dark cockpit")
2. Neon blue / cyan-green / white highlights
3. Glassmorphism (frosted, translucent panels) — `glass`
4. HUD-style layered floating cards — `HUD`
5. Circular gauges / progress rings
6. Radar-sweep accent — `radar`
7. Particle grid / tech wireframe background (CSS-only, subtle)
8. Holographic floating panel feel
9. Futuristic type + linear (outline) iconography
10. Hover glow / border glow / status pulse (restrained)

Adopted **as CSS/markup only**. Where the report shows these effects via heavy
JS/3D, UI-C re-expresses them with plain CSS (gradients, `backdrop-filter`,
`box-shadow`, `@keyframes`) so **no new dependency** is introduced. The accent
color is `neon` cyan.

---

## 4. Jarvis Owner Control Room concept

A single-glance **command deck** for the Owner:

- **Title:** Hermes x OpenClaw Owner Control Room
- **Subtitle:** Read-only command deck for queue, approvals, and system safety.

The screen reads like a cockpit: a dark field, a subtle grid, glass panels that
float above it, and a small set of always-visible **status cards** across the
top that answer "is the system safe right now?" before anything else. It is a
**Read-only**, **Safe** surface — it never gains new control actions in UI-C.

---

## 5. Visual language

- **Readable first, futuristic second.** Contrast and legibility win over flair.
- **Restraint on motion.** No aggressive flashing; at most a slow `status pulse`
  and a single slow `radar` sweep. Respect `prefers-reduced-motion`.
- **Layering = HUD.** Panels sit on a darkened grid with soft glow borders to
  imply depth (holographic feel) without 3D.
- **Glass over grid.** Panels use translucent `glass` surfaces with blur.
- **One accent.** Neon cyan is the primary accent; status colors stay semantic
  (green ok, amber waiting, red danger) but tuned for a dark field.

---

## 6. Layout proposal

```
┌──────────────────────────────────────────────────────────────────────┐
│  Hermes x OpenClaw Owner Control Room        [Read-only]  [Safe Mode]  │  topbar
│  Read-only command deck for queue, approvals, and system safety.       │
├──────────────────────────────────────────────────────────────────────┤
│  TOP STATUS CARDS (HUD ribbon, 8 small glass cards)                     │
│  [System Mode][Queue Intake][Approval Gate][Worker]                     │
│  [OpenClaw][Hermes][Google Sheets][Kill Switch]                        │
├───────────────┬────────────────────────────┬───────────────────────────┤
│  LEFT         │  CENTER                     │  RIGHT                     │
│  Queue        │  Command Core /             │  Pending Reviews /        │
│  Overview     │  Current System State       │  Next Manual Actions      │
│  (counts +    │  (rings + state readout)    │  (review queue)           │
│   rings)      │                             │                           │
├───────────────┴────────────────────────────┴───────────────────────────┤
│  BOTTOM: Recent Errors · Safety Boundaries · System Health             │
└──────────────────────────────────────────────────────────────────────┘
```

- **Left:** Queue Overview (counts, small progress rings).
- **Center:** Command Core / Current System State (the focal panel).
- **Right:** Pending Reviews / Next Manual Actions.
- **Bottom:** Recent Errors / Safety Boundaries / System Health.

Implemented with CSS grid/flex over the existing `.cards`/`.card` structure;
collapses to a single column on mobile (keep current `@media (max-width:640px)`).

---

## 7. Color system

Dark cockpit palette (CSS custom properties, dark field + neon cyan accent):

| Token | Value (proposed) | Use |
| --- | --- | --- |
| `--bg-deep` | `#070b12` | Deep cockpit background |
| `--bg-grid` | `rgba(80,160,200,0.06)` | Subtle grid lines |
| `--glass` | `rgba(18,28,40,0.55)` | Glass panel fill |
| `--glass-border` | `rgba(80,200,230,0.35)` | Neon border |
| `--neon` | `#34e1ff` | Primary neon cyan accent |
| `--neon-soft` | `rgba(52,225,255,0.25)` | Glow / pulse |
| `--ok` | `#39d98a` | Safe / online |
| `--warn` | `#ffcf5c` | Waiting / attention |
| `--danger` | `#ff6b6b` | Error / stop |
| `--text` | `#dceaf2` | Primary text (high contrast on dark) |
| `--muted` | `#7c93a5` | Secondary text |

Contrast targets: body text ≥ 7:1 on `--bg-deep`; status text ≥ 4.5:1.

---

## 8. Typography and icon direction

- **Type:** keep the existing system font stack (no external/CDN font, to honor
  "no new dependency"). A wide letter-spaced uppercase treatment on panel titles
  supplies the futuristic feel without a webfont.
- **Mono:** keep `ui-monospace` for IDs/values (already in CSS as `.mono`).
- **Icons:** inline SVG **outline (linear)** icons only — no icon font, no CDN.
  Small set: queue, review, system, worker, shield (safety), power (kill switch).

---

## 9. Dashboard overview page design

The overview (`dashboard.html`) becomes the Control Room:

- Topbar shows the **title**, **subtitle**, and two pill chips: `Read-only` and
  `Safe`.
- The HUD ribbon of **status cards** (section 11) sits directly under the topbar.
- Below: the three-column layout (section 6) reusing existing data — Queue
  Counts → Left, System Health → Center rings, Quick Links / Reviews → Right.
- Background: `--bg-deep` with a CSS-only grid and one slow `radar` sweep accent.
- No new data sources; same read-only `/queue/*`-derived context as today.

---

## 10. Login page design

`login.html` becomes the "access terminal":

- Same dark cockpit field + single centered glass panel.
- Title "Owner Control Room — Access", subtitle noting Read-only and that the
  token is from `DASHBOARD_TOKEN` (Replit Secrets, never in git).
- Token input styled as a HUD field with a neon focus glow.
- **No secret values are ever rendered.** The form posts to the existing
  `/dashboard/login` route; auth behavior is unchanged.

---

## 11. Status cards design

Eight small glass HUD cards in a top ribbon. Each card = label + state badge +
optional ring. Values reflect the **current safe posture** (static/derived, not
new integrations):

| Card | State (current posture) |
| --- | --- |
| System Mode | Read-only / Safe |
| Queue Intake | Local-only |
| Approval Gate | Owner Required |
| Worker | Worker: OFF |
| OpenClaw | OpenClaw: Not Connected |
| Hermes | Hermes: Not Connected |
| Google Sheets | Google Sheets: Disabled |
| Kill Switch | Visible |

- Safe/neutral states use `--ok`/`--muted`; "Not Connected"/"OFF"/"Disabled" are
  shown as calm neutral states (not alarming red), because they are the
  **intended safe default**.
- `Kill Switch` is always **Visible** as a clearly labeled, prominent control
  affordance in the design (its wiring is out of scope for UI-C).

---

## 12. Queue / Review / System panels

- **Queue Overview (left):** existing Queue Counts badges, plus small CSS
  progress rings for queued/running/waiting; no new queries.
- **Pending Reviews (right):** existing reviews list styled as glass cards;
  read-only — UI-C adds **no** approve/reject behavior.
- **System panel / Command Core (center):** existing System Health kv data
  rendered as a HUD readout with circular status rings (Adapter online, Worker
  status, Queue DB, OpenClaw CLI path).
- **Bottom strip:** Recent Errors (links to failed tasks), Safety Boundaries
  (section 13), System Health summary.

All panels reuse current template context variables; no QueueStore change, no
new route, no live DB beyond what the read-only dashboard already reads.

---

## 13. Safety boundary indicators

A dedicated **Safety Boundaries** panel makes the safe posture legible:

- Read-only — dashboard only reads observability data.
- Worker: OFF.
- OpenClaw: Not Connected.
- Hermes: Not Connected.
- Google Sheets: Disabled.
- Approval Gate: Owner Required.
- Kill Switch: Visible.

These indicators are **display-only**. They assert boundaries; they do not add
controls. The design has **no external side effects**.

---

## 14. Replit Preview acceptance criteria

**Replit Preview acceptance criteria** for the *eventual* implementation
(not part of UI-C itself):

1. Preview renders the dark Owner Control Room without console errors.
2. Topbar shows title, subtitle, `Read-only` and `Safe` chips.
3. All eight status cards render with the correct current-posture states
   (Worker: OFF, OpenClaw: Not Connected, Hermes: Not Connected, Google Sheets:
   Disabled, Kill Switch Visible).
4. Layout shows Left/Center/Right + Bottom regions on desktop and collapses to a
   single column on mobile.
5. Text remains readable (contrast targets in section 7 met).
6. No aggressive flashing; motion respects `prefers-reduced-motion`.
7. Login page renders the access terminal; auth flow unchanged.
8. No network calls to external hosts from the page (no CDN, no API).

---

## 15. Non-goals

UI-C explicitly does **not**:

- Implement any UI (this is a plan only).
- Add Three.js / WebGL / any 3D engine.
- Add WebSocket or any live-push transport.
- Add voice input.
- Call any LLM API or external data API.
- Add a new front-end framework or any new JS/CSS package or CDN.
- Modify `app/`, `templates/`, `static/`, auth, README, `.replit`, or `.claude`.
- Change QueueStore, start the Worker, or call OpenClaw / Hermes.
- Write Google Sheets or read secrets.
- Create webhooks.

The mentions of Three.js / WebSocket / LLM API above are **exclusions**, not
adoptions.

---

## 16. Allowed files for later implementation

When the Owner approves implementation (a future task, not UI-C), the changes
should be limited to these **Allowed files**:

- `templates/base.html` — dark shell, topbar title/subtitle, chips.
- `templates/dashboard.html` — Control Room overview layout.
- `templates/login.html` — access terminal styling.
- `static/dashboard.css` — dark cockpit theme, glass/HUD/neon/radar styles.
- (Optional) `static/control-room.css` — a new **local** stylesheet, if a
  separate file is cleaner; still no CDN, no external font, no JS.

No changes to `app/` routes, QueueStore, Worker, or any integration are needed
for the visual redesign.

---

## 17. Risks

- **Contrast regressions** on a dark theme — mitigated by the contrast targets
  in section 7 and the Preview acceptance check.
- **Motion sensitivity** — mitigated by `prefers-reduced-motion` and "no
  aggressive flashing".
- **Scope creep** toward real integrations — mitigated by sections 13/15 and the
  readiness script's forbidden-pattern checks (no external side effects, no
  secrets, no new WebSocket/LLM/Three.js implementation).
- **Backdrop-filter support** varies by browser — provide a solid-fill fallback
  for the glass panels.

---

## 18. Acceptance criteria

UI-C (this plan) is accepted when:

1. This plan doc exists at the documented path and contains sections 1–18.
2. The readiness script
   `scripts/check_hermes_openclaw_dashboard_jarvis_owner_control_room_visual_plan_v0_7_2_ui_c.py`
   exists and reports **ALL PASS**.
3. The plan records the full status-card set, the layout, and the Visual language
   (glass / HUD / neon / radar, status cards).
4. The plan states **Non-goals** and **Allowed files**.
5. The plan and script carry **no external side effects** and no secrets, and the
   script does not read `.env`, credentials, tokens, or secrets.
6. Only two files are added; no `app/templates/static/auth/QueueStore/Worker/
   OpenClaw/Hermes/Google Sheets` change; nothing committed, pushed, or tagged.
