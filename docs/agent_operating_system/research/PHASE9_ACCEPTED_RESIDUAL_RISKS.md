# Phase 9 Accepted Residual Risks

Status: **PLANNING ONLY. NOT AUTHORIZED FOR IMPLEMENTATION OR EXECUTION.**

Date: 2026-08-03
Authority: `05_VERIFIED_LONG_TERM_PLAN.md` §6.16, commit `e34ca1c`.

This register records risks that the Owner knowingly accepted after the
Fable 5 + Opus review. **Accepted does not mean solved, mitigated away, or
mechanically prevented.** The current design defends accidental overreach by a
non-adversarial model. A deliberately evasive model is outside scope.

The accepted conclusions below are cited from
`05_VERIFIED_LONG_TERM_PLAN.md` §6.16 (line 455 at commit `e34ca1c`). The shell
commands and displayed result lines below are **reconstructed evidence forms,
not a verbatim transcript**; they were not rerun in this docs-only batch. This
batch did not write any audit, artifact, configuration, or runtime file.

## 1. Review finding P0-1 — local root is obtainable

**Recorded measured conclusion from §6.16 (not remeasured in this batch)**

**PLANNING ONLY, NOT AUTHORIZED**

```text
$ wsl.exe -d Ubuntu -u root -- id -u
0

$ wsl.exe -d Ubuntu -- id
uid=1000(lnovo) ... 27(sudo) ...
```

The model session can start WSL as root without a password. A local uid split
therefore does not stop a model that deliberately chooses to bypass it.

**Why accepted under §6.16:** a different local uid/SID still reduces accidental
cross-visibility and accidental token handling by an over-helpful model. The
design makes no claim against intentional privilege escalation.

**If the threat model changes:** move token ingress, egress, gate, and Owner
challenge handling to a separate physical device that this Windows/WSL host
cannot administer, mount, debug, or impersonate. A second uid on this host is
not sufficient for an adversarial threat model.

## 2. Review finding P0-2 — local gate code and environment are writable

**Recorded measured conclusion from §6.16 (not remeasured in this batch)**

**PLANNING ONLY, NOT AUTHORIZED**

```text
$ test -w /mnt/c/Users/Lnovo/Desktop/hermes-adapter-work; echo $?
0
$ test -w /mnt/c/Users/Lnovo/Desktop/hermes-adapter-work/app; echo $?
0
$ test -w /mnt/c/Users/Lnovo/Desktop/hermes-adapter-work/.venv; echo $?
0
```

`/mnt/c` is exposed through DrvFs, whose Unix-looking mode/ownership metadata is
synthesized and may not represent the effective Windows ACL. Therefore
`test -w` alone is **not** a reliable Windows-ACL measurement. The accepted
conclusion that the repo, `app/`, and `.venv` are writable by `lnovo` is also
supported directly by the Owner ruling in §6.16; the reconstructed command form
above is supporting context, not sole proof. A deliberately evasive model could
change future gate code or its dependencies before launch.

**Why accepted under §6.16:** ordinary accidental overreach is constrained by
reviewed code, frozen digests, fail-closed checks, and an Owner-present script.
Those controls remain useful even though they do not resist intentional
self-modification.

**If the threat model changes:** run a signed, measured gate on an off-host
Owner-controlled device; verify its code and dependency image outside this
machine; allow this host to submit only a frozen request and receive a bounded
result.

## 3. Review finding P1-1 — local burn and frozen evidence are deliberately mutable

**Derived risk from the recorded writable-parent conclusion**

**PLANNING ONLY, NOT AUTHORIZED**

```text
$ test -w /mnt/c/Users/Lnovo/Desktop/hermes-adapter-work; echo $?
0
```

The burn ledger and frozen Phase 9 artifacts are proposed local descendants of
this writable repo/data authority. Their future mutability is **derived** from
the recorded writable-parent conclusion; it was not separately measured and no
Phase 9 ledger exists. A model acting deliberately could therefore delete,
replace, or roll back those future files.

**Why accepted under §6.16:** append-before-call, hash checks, the second fresh
challenge, and fail-closed restart behavior protect accidental replay and
crash-resume mistakes. They are not represented as tamper resistance against a
deliberate local administrator.

**If the threat model changes:** put the authoritative burn ledger and frozen
artifact store on the off-host Owner-controlled gate device, with durable
one-use state and authenticated append/read interfaces that this host cannot
reset or rewrite.

## 4. Review finding P1-2 — local OpenClaw configuration is writable

**Recorded measured conclusion from §6.16 (not remeasured in this batch)**

**PLANNING ONLY, NOT AUTHORIZED**

```text
$ test -w "$HOME/.openclaw"; echo $?
0
```

The recorded environment also showed `~/.openclaw/` containing local
configuration/state such as `agents`, `cache`, and `devices`. A deliberately
evasive model could change that configuration before the one call.

**Why accepted under §6.16:** the Owner-present facts check, frozen action
digest, before/after inventory, exact one-call posture, and immediate abort on
drift are aimed at mistakes and unplanned changes. They do not claim to defeat
intentional configuration tampering by the same host owner.

**If the threat model changes:** operate OpenClaw from the same off-host trusted
device as the gate, with an Owner-controlled immutable configuration snapshot;
do not treat this host's `~/.openclaw/` as authoritative.

## 5. Seven-document consistency matrix

| Document | Threat model | Safety wording | OOB decision | Accepted-risk handling |
|---|---|---|---|---|
| `OPENCLAW_CLI_FACTS.md` | quotes §6.16 | best-effort, non-adversarial | no CLI/OOB assumption promoted to fact | accepted risks are not CLI facts to “fix” |
| `PHASE9_TOKEN_DESIGN.md` | quotes §6.16 | no absolute model-exclusion claim | local different uid/SID may be accepted; same model session/terminal remains prohibited | P0-1/P0-2/P1-1/P1-2 remain explicit |
| `PHASE9_EXECUTION_GATE_DESIGN.md` | quotes §6.16 | procedural constraint plus best-effort isolation | six-predicate presence uses best-effort isolation evidence | deliberate local bypass is outside gate claim |
| `PHASE9_TOKEN_SCHEMA_PROPOSAL.md` | quotes §6.16 | schema validity is not adversarial isolation | schema choice does not choose an OOB path | schema cannot resolve these four risks |
| `PHASE9_SIX_STEP_SCRIPT.md` | quotes §6.16 | Owner-present checks target accidental overreach | selected ingress/egress must avoid the model session/terminal | deliberate-bypass signs invoke abort, not a success claim |
| `PHASE9_ABORT_PLAYBOOK.md` | quotes §6.16 | fail-closed without claiming adversarial containment | drift or suspected bypass closes the ceremony | scenario 17 preserves the “accepted, not solved” classification |
| `PHASE9_OWNER_BRIEF.md` | quotes §6.16 in plain language | says what is and is not defended | presents recommendations mapped to still-blank §8 decision fields; it records no selection | names all four accepted risks without calling them fixed |

## 6. Boundary if deliberate bypass is suspected

Acceptance of these risks is not permission to continue through evidence of a
deliberate bypass. The correct response is the abort path in
`PHASE9_ABORT_PLAYBOOK.md`: stop, prevent any new call, preserve the available
evidence without improvising a new write location, notify the Owner, and require
a new threat-model decision before any future Phase 9 attempt.
