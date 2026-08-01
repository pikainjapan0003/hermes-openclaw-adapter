# 01 Safety Boundaries wording proposal — 2026-08-01

Status: **PLANNING ONLY, NOT AUTHORIZED — Owner decision required**

This file is a proposal for the one finding that touches the F2-governed
`01_SAFETY_BOUNDARIES.md`. It does not modify 01, grant an authorization, or
change any prohibition. The historical 00 findings C01-01 through C01-04 are
addressed in `00_QUICK_DIAGNOSIS.md`; the canonical 01 file remains byte-for-byte
unchanged in this package.

## C01-05 — discoverability of the narrow night-batch exception

Source finding: `research/CORE_DOCS_REVIEW_00_01.md` C01-05, concerning
`01_SAFETY_BOUNDARIES.md` §2 and §4.5.

### Suggested wording (Owner may accept, edit, or reject)

> **Cross-reference only; no new permission:** §2 remains the canonical rule that
> valid authorization exists only in the active Owner instruction. The narrow
> night-batch merge/push exception already recorded in §4.5 is governed by
> `05_VERIFIED_LONG_TERM_PLAN.md` §6.13: it applies only to the current Owner-
> specified night-batch branch, only after Fable 5 batch review passes and the
> Owner explicitly covers that batch, and it does not authorize Phase 7 audit
> writing, Phase 9 execution, runtime/remote wiring, token changes, or any other
> action. No dashboard display, plan text, prior-session approval, or model
> inference can substitute for the active Owner instruction.

### Why this is safer

- It points a reader from §2 to an already documented narrow exception without
  weakening the default prohibition.
- It states the exact gates (Owner instruction, Fable 5 pass, §6.13) and closes
  the likely weak-model overread into writer, execution, token, or runtime work.
- It does not make the exception a general repository permission or carry it
  across sessions or unrelated branches.

## Owner decision

Owner response: **____________________________**

Until the Owner accepts exact wording through an explicitly authorized F2
documentation package, do not edit `01_SAFETY_BOUNDARIES.md`.
