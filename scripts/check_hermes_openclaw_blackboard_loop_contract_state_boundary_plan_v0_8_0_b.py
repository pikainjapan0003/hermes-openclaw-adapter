"""v0.8.0-B readiness check: Blackboard Loop Contract and State Boundary Plan (plan-first).

Plan-first / boundary verification. Checks that the v0.8.0-B plan document exists and
contains the required sections (1-35), the current-master marker, the v0.8.0-B plan-first
markers, the relationship-to-v0.8.0-A markers, the problem-statement markers, the Blackboard
Loop contract definition markers, the Blackboard Loop state boundary definition markers, the
Blackboard message contract boundary markers, the Task state boundary markers, the Owner
review state boundary markers, the Decision audit state boundary markers, the
dispatch-disabled state boundary markers, the dry-run preview state boundary markers, the
Result observation state boundary markers, the Advice observation state boundary markers, the
contract-is-not-execution-permission markers, the state transition boundary markers, the
candidate state machine draft markers, the runtime disabled boundary markers, the Worker /
OpenClaw / Hermes separation boundary markers, the Dashboard display boundary markers, the
Remote Blackboard API relationship markers, the local queue vs remote blackboard boundary
markers, the source-of-truth and data boundary markers, the secrets / privacy / memory
boundary markers, the network / webhook / connector boundary markers, the failure / rollback
/ audit boundary markers, the candidate future phases markers, the disabled runtime list
markers, the current safe posture markers, the validation summary markers, the safety grep
summary markers, and the next recommended step — and that it asserts no unsafe "implemented /
created / added / enabled / activated / connected / called / started / written / moved /
migrated / changed" claim and contains no secret.

The document is allowed to contain safe negations; those that literally embed a
forbidden substring are scrubbed before the forbidden scan so they are not mis-flagged.

This script only reads the plan document. It does NOT read .env, credentials, tokens, or
secrets, makes no network call, imports no app logic (no app.main, no QueueStore), adds no
API route / router / database client / migration, creates no production / shared DB, builds
no Blackboard Loop runtime, no loop contract runtime, no state machine runtime, starts no
loop scheduler, enables no dispatch gate, activates no Hermes, connects no OpenClaw, starts
no Worker, opens no shared write, and writes no Google Sheets.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
PASS = []
FAIL = []

DOC_PATH = (
    ROOT
    / "docs"
    / "HERMES_OPENCLAW_BLACKBOARD_LOOP_CONTRACT_STATE_BOUNDARY_PLAN_V0_8_0_B.md"
)


def ok(label):
    PASS.append(label)
    print(f"  ok : {label}")


def xx(label):
    FAIL.append(label)
    print(f"  XX : {label}")


# ---------------------------------------------------------------------------
# [1] plan 文件存在
# ---------------------------------------------------------------------------
print("[1] plan 文件存在")
ok("v0.8.0-B plan doc 存在") if DOC_PATH.exists() else xx("v0.8.0-B plan doc 存在")
if not DOC_PATH.exists():
    print("\nXX plan doc 不存在，無法繼續")
    sys.exit(1)

doc = DOC_PATH.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# [2] 必須包含的章節（1-35）
# ---------------------------------------------------------------------------
print("[2] 必須包含的章節")
REQUIRED_SECTIONS = [
    "1. Purpose",
    "2. Current master",
    "3. Scope",
    "4. Relationship to v0.8.0-A Owner-supervised Blackboard Loop MVP Plan",
    "5. Problem statement",
    "6. Blackboard Loop contract definition",
    "7. Blackboard Loop state boundary definition",
    "8. Blackboard message contract boundary",
    "9. Task state boundary",
    "10. Owner review state boundary",
    "11. Decision audit state boundary",
    "12. Dispatch-disabled state boundary",
    "13. Dry-run preview state boundary",
    "14. Result observation state boundary",
    "15. Advice observation state boundary",
    "16. Contract is not execution permission",
    "17. State transition boundary",
    "18. Candidate state machine draft",
    "19. Runtime disabled boundary",
    "20. Worker / OpenClaw / Hermes separation boundary",
    "21. Dashboard display boundary",
    "22. Remote Blackboard API relationship",
    "23. Local queue vs remote blackboard boundary",
    "24. Source-of-truth and data boundary",
    "25. Secrets / privacy / memory boundary",
    "26. Network / webhook / connector boundary",
    "27. Failure / rollback / audit boundary",
    "28. Candidate future phases",
    "29. Disabled runtime list",
    "30. Current safe system posture",
    "31. Validation summary",
    "32. Safety grep summary",
    "33. Non-goals",
    "34. Acceptance criteria",
    "35. Next recommended step",
]
for section in REQUIRED_SECTIONS:
    ok(f"doc 含章節「{section}」") if section in doc else xx(f"doc 含章節「{section}」")

# ---------------------------------------------------------------------------
# [3] 必須包含的 markers
# ---------------------------------------------------------------------------
print("[3] 必須包含的 markers")
REQUIRED = [
    # version
    "v0.8.0-B",
    "Blackboard Loop Contract and State Boundary Plan",
    # current master
    "HEAD = origin/master = 9debb74b05007428a137fe35342eb00e8183fb28",
    "docs: plan owner supervised blackboard loop",
    # v0.8.0-B plan-first markers
    "v0.8.0-B Blackboard Loop Contract and State Boundary Plan is plan-first.",
    "v0.8.0-B does not implement Blackboard Loop runtime.",
    "v0.8.0-B does not implement loop contract runtime.",
    "v0.8.0-B does not implement state machine runtime.",
    "v0.8.0-B does not create loop scheduler.",
    "v0.8.0-B does not enable dispatch gate.",
    "v0.8.0-B does not enable autonomous execution.",
    "v0.8.0-B does not activate Hermes.",
    "v0.8.0-B does not connect Hermes.",
    "v0.8.0-B does not connect OpenClaw.",
    "v0.8.0-B does not start Worker.",
    "v0.8.0-B does not create Hermes runtime.",
    "v0.8.0-B does not create OpenClaw runtime.",
    "v0.8.0-B does not create Worker runtime.",
    "v0.8.0-B does not implement Remote Blackboard API runtime.",
    "v0.8.0-B does not create production DB.",
    "v0.8.0-B does not create shared DB.",
    "v0.8.0-B does not create remote shared DB.",
    "v0.8.0-B does not migrate queue data.",
    "v0.8.0-B does not sync local queue and remote queue.",
    "v0.8.0-B does not open shared write.",
    "v0.8.0-B does not write Google Sheets.",
    "v0.8.0-B does not create webhook.",
    # relationship to v0.8.0-A
    "v0.8.0-A Owner-supervised Blackboard Loop MVP Plan is complete.",
    "v0.8.0-B starts the Blackboard Loop contract and state boundary planning step.",
    "v0.8.0-B builds on Owner-supervised Blackboard Loop MVP planning.",
    "v0.8.0-B defines contract and state boundaries before any runtime loop.",
    "v0.8.0-B preserves Owner final approval authority.",
    "v0.8.0-B preserves decision and dispatch separation.",
    "v0.8.0-B preserves audit trail.",
    "v0.8.0-B does not change any v0.8.0-A boundary.",
    "v0.8.0-B does not change any v0.7.5 boundary.",
    # problem statement
    "The system needs a planned Blackboard Loop contract before any runtime loop can be implemented.",
    "The system needs planned state boundaries before any state machine can be implemented.",
    "The loop contract must not become an execution command.",
    "The loop state must not become execution permission.",
    "The Owner review state must not become Worker dispatch.",
    "The Decision audit state must not become command.",
    "The dispatch-disabled state must remain disabled.",
    "The dry-run preview state must not write queue data.",
    "Planning contract and state boundaries is not running the loop.",
    # contract definition
    "Blackboard Loop contract means a future agreement about allowed message families, allowed states, required Owner review, and disabled dispatch.",
    "Blackboard Loop contract is a planning artifact in v0.8.0-B.",
    "Blackboard Loop contract is not runtime code.",
    "Blackboard Loop contract is not API route.",
    "Blackboard Loop contract is not database schema.",
    "Blackboard Loop contract is not Worker dispatch.",
    "Blackboard Loop contract is not OpenClaw call.",
    "Blackboard Loop contract is not Hermes activation.",
    "Blackboard Loop contract requires separate future plan and Owner approval before implementation.",
    # state boundary definition
    "Blackboard Loop state boundary means a planned distinction between display state, review state, audit state, preview state, and dispatch state.",
    "Display state is not execution permission.",
    "Review state is not execution permission.",
    "Audit state is not command.",
    "Preview state is not queue write.",
    "Dispatch state remains disabled.",
    "State boundary is planning only in v0.8.0-B.",
    "No state machine runtime is implemented in v0.8.0-B.",
    "No state persistence runtime is implemented in v0.8.0-B.",
    # message contract boundary
    "Task Message",
    "Decision Message",
    "Result Message",
    "Advice Message",
    "Task Message is draft or request, not Worker dispatch.",
    "Decision Message is audit record, not command.",
    "Result Message is observation, not next dispatch permission.",
    "Advice Message is advisory, not command.",
    "Hermes Advice Message is not automatic execution.",
    "Hermes Task Message draft requires Owner review.",
    "No new Blackboard message family is implemented in v0.8.0-B.",
    "No message schema migration is performed in v0.8.0-B.",
    # Task state boundary
    "Task state is draft or pending review until Owner decision.",
    "Task draft is not queue write by itself.",
    "Task draft is not Worker dispatch.",
    "Task draft is not OpenClaw call.",
    "Task draft is not Hermes action.",
    "Task state must show review requirement.",
    "Task state must not imply execution permission.",
    "No Task state runtime is implemented in v0.8.0-B.",
    # Owner review state boundary
    "Owner review state is required before any future dispatch.",
    "Owner review state must be visible.",
    "Owner review state must be auditable.",
    "Owner review state must preserve approve is not execute.",
    "Owner review state must preserve approval readiness is not execution permission.",
    "Owner review state must preserve Owner decision event is not Worker dispatch.",
    "Owner review state is not implemented as runtime in v0.8.0-B.",
    "Owner approval remains separate from runtime dispatch.",
    # Decision audit state boundary
    "Decision audit state records Owner decision.",
    "Decision audit state is audit record, not command.",
    "Decision audit state is not Worker dispatch.",
    "Decision audit state is not OpenClaw call.",
    "Decision audit state is not Hermes action.",
    "Decision audit state is not Google Sheets write.",
    "Decision audit state must remain append-only when future runtime exists.",
    "No Decision audit runtime change is implemented in v0.8.0-B.",
    # Dispatch-disabled state boundary
    "Dispatch-disabled state means future dispatch path is explicitly off.",
    "Dispatch-disabled state must be visible.",
    "Dispatch-disabled state must be auditable.",
    "Dispatch-disabled state must block Worker dispatch.",
    "Dispatch-disabled state must block OpenClaw call.",
    "Dispatch-disabled state must block Hermes action.",
    "Dispatch-disabled state must block Google Sheets write.",
    "Dispatch gate remains disabled in v0.8.0-B.",
    "No dispatch gate runtime is implemented in v0.8.0-B.",
    # Dry-run preview state boundary
    "Dry-run preview state means future loop preview without external side effects.",
    "Dry-run preview state is not queue write.",
    "Dry-run preview state is not Worker dispatch.",
    "Dry-run preview state is not OpenClaw call.",
    "Dry-run preview state is not Hermes action.",
    "Dry-run preview state is not Google Sheets write.",
    "Dry-run preview state must not read real queue DB unless separately approved.",
    "Dry-run preview state must not modify local queue or Replit queue.",
    "No dry-run preview runtime is implemented in v0.8.0-B.",
    # Result / Advice observation state
    "Result observation state is read-only observation.",
    "Result observation state is not next dispatch permission.",
    "Result observation state is not automatic follow-up execution.",
    "Result observation state is not Google Sheets write.",
    "No Result observation runtime is implemented in v0.8.0-B.",
    "Advice observation state is read-only advisory display.",
    "Advice observation state is not command.",
    "Advice observation state is not Worker dispatch.",
    "Advice observation state is not OpenClaw call.",
    "Advice observation state is not automatic execution.",
    "No Advice observation runtime is implemented in v0.8.0-B.",
    # contract is not execution permission
    "Contract approval is not runtime approval.",
    "Contract approval is not dispatch approval.",
    "Contract approval is not migration approval.",
    "Contract approval is not shared write approval.",
    "Contract approval is not Hermes activation approval.",
    "State label is not execution permission.",
    "Review label is not execution permission.",
    "Approved label is not execute.",
    "Dispatch-ready label is not Worker dispatch.",
    # state transition boundary
    "State transition planning is not runtime transition implementation.",
    "State transition label is not queue mutation.",
    "State transition label is not Worker dispatch.",
    "State transition label is not OpenClaw call.",
    "State transition label is not Hermes action.",
    "State transition requires future runtime plan before implementation.",
    "No state transition runtime is implemented in v0.8.0-B.",
    "No existing status transition is changed in v0.8.0-B.",
    # candidate state machine draft
    "Candidate state: draft.",
    "Candidate state: pending_owner_review.",
    "Candidate state: decision_recorded.",
    "Candidate state: dispatch_disabled.",
    "Candidate state: dry_run_preview.",
    "Candidate state: result_observed.",
    "Candidate state: advice_observed.",
    "Candidate state: closed_by_owner.",
    "Candidate state machine is planning only.",
    "No candidate state is implemented in v0.8.0-B.",
    "No state machine runtime is enabled in v0.8.0-B.",
    # runtime disabled boundary
    "Blackboard Loop runtime remains disabled.",
    "Loop contract runtime remains disabled.",
    "State machine runtime remains disabled.",
    "Loop scheduler remains disabled.",
    "Dispatch gate remains disabled.",
    "Worker runtime remains disabled.",
    "OpenClaw runtime remains disabled.",
    "Hermes runtime remains disabled.",
    "Remote Blackboard API runtime remains disabled.",
    "Shared write remains disabled.",
    "Google Sheets write remains disabled.",
    "Autonomous execution remains disabled.",
    # separation
    "Worker remains OFF.",
    "OpenClaw remains Not Connected.",
    "Hermes remains Not Connected.",
    "Worker is dispatch runtime.",
    "OpenClaw is execution / gateway / tools layer.",
    "Hermes is strategy / proxy / memory layer.",
    "Hermes must not bypass Owner review.",
    "Hermes must not bypass OpenClaw boundary.",
    "Hermes must not bypass Worker boundary.",
    "OpenClaw must not execute without Owner-approved dispatch path.",
    "Worker must not run from plan-only contract.",
    # Dashboard display boundary
    "Dashboard displays state.",
    "Dashboard display is not dispatch.",
    "Dashboard display is not execution permission.",
    "Dashboard contract label is not execution permission.",
    "Dashboard state label is not execution permission.",
    "Dashboard source label is not shared write.",
    "Dashboard source switching requires separate future plan and Owner approval.",
    "No Dashboard runtime change is implemented in v0.8.0-B.",
    "No Dashboard backend source runtime is implemented in v0.8.0-B.",
    # Remote Blackboard API relationship
    "Remote Blackboard API remains planning only.",
    "Remote Blackboard API runtime is not implemented in v0.8.0-B.",
    "Remote Blackboard API route is not added in v0.8.0-B.",
    "Remote Blackboard API read is not enabled in v0.8.0-B.",
    "Remote Blackboard API write is not enabled in v0.8.0-B.",
    "Remote Blackboard API is not execution dispatcher.",
    "Remote Blackboard API is not production DB.",
    "Remote Blackboard API runtime requires separate future plan and Owner approval.",
    # local queue vs remote blackboard boundary
    "Local Queue is not Remote Blackboard.",
    "Remote Blackboard is not local queue.",
    "WSL local queue remains local.",
    "Replit local queue remains separate.",
    "Dashboard update is not queue synchronization.",
    "GitHub push is not queue synchronization.",
    "No queue synchronization is performed.",
    "No queue migration is performed.",
    "No queue backfill is performed.",
    "No queue merge is performed.",
    "No conflict resolver is implemented.",
    # source-of-truth and data boundary
    "No source-of-truth switch is performed.",
    "Current source of truth remains local to each environment.",
    "Future remote authority requires separate future plan and Owner approval.",
    "No queue DB change.",
    "No local queue data change.",
    "No Replit queue data change.",
    "No real queue DB read.",
    "No production queue data is created.",
    "No remote shared DB is created.",
    "No shared write is enabled.",
    # secrets / privacy / memory boundary
    "No secrets are read.",
    "No secrets are copied.",
    "No secrets are created.",
    "No .env file is created.",
    "No credentials are moved.",
    "No production secrets are copied.",
    "No Hermes memory store is created.",
    "No Hermes learning runtime is created.",
    "No private conversation log is created.",
    "No all-conversation logging is enabled.",
    "No personal memory migration is performed.",
    "GitHub must not store secrets.",
    "Replit must not receive production secrets.",
    # network / webhook / connector boundary
    "No webhook is created.",
    "No webhook receiver is created.",
    "No connector is created.",
    "No external network call is added.",
    "No inbound listener is added.",
    "No outbound integration is added.",
    "No port exposure is configured.",
    "No POST is sent.",
    "No live queue write validation is performed.",
    "Network activation requires separate future plan and Owner approval.",
    # failure / rollback / audit boundary
    "Future contract changes must be auditable.",
    "Future state transitions must be auditable.",
    "Future loop actions must include rollback notes when external actions are involved.",
    "Future loop failures must not silently retry external actions.",
    "Future loop failures must not bypass Owner approval.",
    "Future loop failures must not write Google Sheets by default.",
    "Future loop failures must not call OpenClaw by default.",
    "Future loop failures must not start Worker by default.",
    "No loop failure handling runtime is implemented in v0.8.0-B.",
    # candidate future phases
    "Candidate future phase: docs-only contract plan.",
    "Candidate future phase: contract field inventory.",
    "Candidate future phase: local dry-run state preview.",
    "Candidate future phase: read-only Dashboard state display.",
    "Candidate future phase: Owner review state display.",
    "Candidate future phase: Decision audit state confirmation.",
    "Candidate future phase: dispatch-disabled guard display.",
    "Candidate future phase: Result and Advice observation display.",
    "Candidate future phases are planning notes only.",
    "No candidate future phase is implemented in v0.8.0-B.",
    "No candidate future phase is enabled in v0.8.0-B.",
    # disabled runtime list
    "Blackboard Loop runtime is disabled.",
    "Loop contract runtime is disabled.",
    "State machine runtime is disabled.",
    "Loop scheduler is disabled.",
    "Dispatch gate is disabled.",
    "Worker runtime is disabled.",
    "OpenClaw runtime is disabled.",
    "Hermes runtime is disabled.",
    "Remote Blackboard API runtime is disabled.",
    "Shared write is disabled.",
    "Google Sheets write is disabled.",
    "Autonomous execution is disabled.",
    # current safe posture
    "Dashboard read-only / controlled local route behavior.",
    "Worker OFF.",
    "OpenClaw Not Connected.",
    "Hermes Not Connected.",
    "Google Sheets Disabled.",
    "No Blackboard Loop runtime.",
    "No loop contract runtime.",
    "No state machine runtime.",
    "No loop scheduler.",
    "No dispatch gate enabled.",
    "No autonomous execution.",
    "No Hermes activation.",
    "No Hermes blackboard mode.",
    "No Hermes runtime.",
    "No Hermes activation runtime.",
    "No Hermes memory store.",
    "No Hermes learning runtime.",
    "No all-conversation logging.",
    "No cleanup demo task.",
    "No cleanup apply.",
    "No --apply.",
    "No task deletion.",
    "No task archive.",
    "No queue DB change.",
    "No local queue data change.",
    "No Replit queue data change.",
    "No real queue DB read.",
    "No POST.",
    "No live local queue write validation.",
    "No Worker execution.",
    "No OpenClaw call.",
    "No Hermes call.",
    "No Google Sheets write.",
    "No secrets read.",
    "No secrets copied.",
    "No .env created.",
    "No webhook.",
    "No external side effects.",
    "No production DB.",
    "No shared DB.",
    "No remote shared DB.",
    "No Remote Blackboard API runtime.",
    "No Dashboard backend source runtime.",
    "No source switching runtime.",
    "No Core runtime host.",
    "No Worker runtime.",
    "No OpenClaw runtime.",
    "No systemd service.",
    "No daemon.",
    "No Docker deployment.",
    "No VPS deployment.",
    "No Mac mini deployment.",
    "No home server deployment.",
    "No queue synchronization.",
    "No queue migration.",
    "No queue backfill.",
    "No queue merge.",
    "No conflict resolver.",
    "No connector.",
    "No tag.",
    # validation summary
    "v0.8.0-B readiness: ALL PASS.",
    "v0.8.0-A readiness: ALL PASS.",
    "v0.7.5-R readiness: ALL PASS.",
    "v0.7.5-E readiness: ALL PASS.",
    "v0.7.5-D readiness: ALL PASS.",
    "v0.7.5-C readiness: ALL PASS.",
    "v0.7.5-B readiness: ALL PASS.",
    "v0.7.5-A readiness: ALL PASS.",
    "v0.7.4-R readiness: ALL PASS.",
    "v0.7.4-F-R readiness: ALL PASS.",
    "v0.7.4-F readiness: ALL PASS.",
    "v0.7.4-F dry-run tool test: ALL PASS.",
    "v0.7.4-E check: ALL PASS.",
    "v0.7.4-D-R check: ALL PASS.",
    "v0.7.4-D readiness and helper test: ALL PASS.",
    "v0.7.4-C / B / A checks: ALL PASS.",
    "v0.7.3 checks: ALL PASS.",
    "prior F-line checks: ALL PASS.",
    "compileall scripts: PASS.",
    # safety grep summary
    "No real unsafe claim was found.",
    "No real secret was found.",
    "Readiness forbidden-pattern matches are benign.",
    # next recommended step
    "v0.8.0-C — Local Dry-run Blackboard Loop Preview Plan",
    "v0.8.0-C must remain plan-first unless separately approved.",
    "v0.8.0-C must not implement Blackboard Loop runtime.",
    "v0.8.0-C must not enable dispatch gate.",
    "v0.8.0-C must not activate Hermes.",
    "v0.8.0-C must not connect OpenClaw.",
    "v0.8.0-C must not start Worker.",
    "v0.8.0-C must not create production DB.",
    "v0.8.0-C must not create Remote Blackboard API runtime unless separately approved.",
    "v0.8.0-C must not migrate queue data.",
    "v0.8.0-C must not open shared write.",
    "v0.8.0-C must not write Google Sheets.",
]
for token in REQUIRED:
    ok(f"doc 含「{token}」") if token in doc else xx(f"doc 含「{token}」")

# ---------------------------------------------------------------------------
# [4] 禁止包含的不安全聲明 / 機密
#     先移除合法的安全否定句（其字面含 forbidden 子字串），再掃 forbidden。
# ---------------------------------------------------------------------------
print("[4] 禁止包含的不安全聲明 / 機密")
SAFE_NEGATIONS = [
    "No secrets read.",
    "No secrets copied.",
    "No .env created.",
    "No dispatch gate enabled.",
]
scrubbed = doc
for phrase in SAFE_NEGATIONS:
    scrubbed = scrubbed.replace(phrase, "")

FORBIDDEN_SUBSTR = [
    "GOOGLE_SHEETS_ENABLED=true",
    "Blackboard Loop runtime created",
    "Blackboard Loop runtime implemented",
    "Blackboard Loop runtime enabled",
    "loop contract runtime created",
    "loop contract runtime implemented",
    "loop contract runtime enabled",
    "state machine runtime created",
    "state machine runtime implemented",
    "state machine runtime enabled",
    "state persistence runtime created",
    "state transition runtime created",
    "Task state runtime implemented",
    "Decision audit runtime implemented",
    "Result observation runtime implemented",
    "Advice observation runtime implemented",
    "loop scheduler created",
    "loop scheduler enabled",
    "dispatch gate enabled",
    "dispatch gate runtime implemented",
    "autonomous execution enabled",
    "agent autonomy runtime created",
    "Owner approval bypassed",
    "Owner review bypassed",
    "Worker enabled",
    "OpenClaw connected",
    "Hermes connected",
    "Hermes activated",
    "Hermes activation enabled",
    "Hermes blackboard mode enabled",
    "Hermes runtime created",
    "Hermes activation runtime created",
    "Hermes memory store created",
    "Hermes learning runtime created",
    "Hermes called",
    "Hermes wrote Blackboard message",
    "Hermes wrote Advice Message",
    "Hermes drafted Task Message",
    "Hermes self-approved",
    "Hermes self-dispatched",
    "Hermes executed external action",
    "Hermes connector created",
    "Hermes credentials moved",
    "OpenClaw called",
    "OpenClaw runtime created",
    "OpenClaw connector created",
    "Worker started",
    "Worker runtime created",
    "Worker dispatch enabled",
    "Google Sheets live write enabled",
    "Google Sheets written",
    "cleanup applied",
    "demo task cleaned up",
    "tasks deleted",
    "tasks archived",
    "payload modified",
    "status modified",
    "queue DB modified",
    "local queue data modified",
    "Replit queue cleaned",
    "production DB cleaned",
    "remote shared DB cleaned",
    "shared DB created",
    "production DB created",
    "Remote Blackboard API runtime created",
    "Remote Blackboard API implemented",
    "Remote Blackboard API route added",
    "Remote Blackboard API read enabled",
    "Remote Blackboard API write enabled",
    "shared write enabled",
    "Blackboard shared write enabled",
    "Dashboard backend source runtime created",
    "source switching runtime created",
    "Core runtime host created",
    "runtime host selected",
    "runtime host provisioned",
    "systemd service created",
    "daemon created",
    "Docker deployment created",
    "VPS deployed",
    "Mac mini configured",
    "home server configured",
    "production process installed",
    "all-conversation logging enabled",
    "private conversation log created",
    "personal memory migration performed",
    "API route added",
    "FastAPI router added",
    "database client added",
    "migration added",
    "message schema migration performed",
    "queue migration performed",
    "queue data moved",
    "queue data copied",
    "queue data merged",
    "queue data backfilled",
    "queue data synchronized",
    "conflict resolver implemented",
    "source-of-truth switch performed",
    "remote blackboard authority enabled",
    "source configuration changed",
    "fallback write triggered",
    "cleanup apply approved",
    "apply_allowed = True",
    "apply_requested = True",
    "dry_run = False",
    "would_delete = True",
    "would_archive = True",
    "would_modify = True",
    "external_side_effects = True",
    "Owner approval granted cleanup apply",
    "POST to Replit Preview was sent",
    "POST to real queue was sent",
    "live queue write validation performed",
    "webhook created",
    "webhook receiver created",
    "connector created",
    "tag created",
    "QueueStore runtime behavior changed",
    "app/queue_store.py changed",
    "approval routes changed",
    "dashboard auth changed",
    "status transition changed",
    "runtime guard implemented",
    "existing transition result changed",
    "secrets read",
    "secrets copied",
    "secrets created",
    ".env created",
    "credentials moved",
]
for token in FORBIDDEN_SUBSTR:
    ok(f"doc 無「{token}」") if token not in scrubbed else xx(f"doc 不得含「{token}」")

FORBIDDEN_PATTERNS = [
    (r"spreadsheets/d/[A-Za-z0-9_-]{20,}", "real spreadsheet URL"),
    (r'"?refresh_token"?\s*[:=]\s*"[^"]+"', "refresh token value"),
    (r'"?client_secret"?\s*[:=]\s*"[^"]+"', "client secret value"),
    (r"-----BEGIN[ A-Z]*PRIVATE KEY-----", "private key value"),
    (r"dashboard_token\s*=\s*[A-Za-z0-9_\-]{8,}", "dashboard token value"),
]
for pat, label in FORBIDDEN_PATTERNS:
    found = bool(re.search(pat, doc, re.IGNORECASE))
    ok(f"doc 無「{label}」") if not found else xx(f"doc 不得含「{label}」")

# ---------------------------------------------------------------------------
# 結果
# ---------------------------------------------------------------------------
total = len(PASS) + len(FAIL)
print(f"\n合計：{len(PASS)}/{total} 通過")
if FAIL:
    print(f"\nXX v0.8.0-B readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print(
        "\nv0.8.0-B Blackboard Loop Contract and State Boundary Plan readiness: ALL PASS"
    )
    sys.exit(0)
