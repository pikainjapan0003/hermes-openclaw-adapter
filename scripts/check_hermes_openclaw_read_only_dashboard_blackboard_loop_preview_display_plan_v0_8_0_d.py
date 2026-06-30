"""v0.8.0-D readiness check: Read-only Dashboard Blackboard Loop Preview Display Plan.

Plan-first / boundary verification. Checks that the v0.8.0-D plan document exists and
contains the required sections (1-36), the current-master marker, the v0.8.0-D plan-first
markers, the relationship-to-v0.8.0-C markers, the problem-statement markers, the read-only
Dashboard preview display definition markers, the Dashboard display contract / source / input
/ output boundary markers, the read-only display state markers, the Owner review checklist /
Decision audit / dispatch-disabled display markers, the Task / Result / Advice display
markers, the local-only Dashboard display markers, the queue and data display markers, the
Dashboard route / template / static boundary markers, the Remote Blackboard API relationship
markers, the Worker / OpenClaw / Hermes separation markers, the Google Sheets boundary
markers, the secrets / privacy / memory boundary markers, the network / webhook / connector
boundary markers, the failure / rollback / audit boundary markers, the candidate Dashboard
display fields markers, the candidate Dashboard display validation rules markers, the
candidate future phases markers, the disabled runtime list markers, the current safe posture
markers, the validation summary markers, the safety grep summary markers, and the next
recommended step — and that it asserts no unsafe "implemented / created / added / enabled /
activated / connected / called / started / written / read / modified / moved / migrated"
claim and contains no secret.

The document is allowed to contain safe negations; those that literally embed a
forbidden substring are scrubbed before the forbidden scan so they are not mis-flagged.

This script only reads the plan document. It does NOT read .env, credentials, tokens, or
secrets, makes no network call, imports no app logic (no app.main, no QueueStore), adds no
API route / router / Dashboard route / template / static / database client / migration,
creates no production / shared DB, builds no Blackboard Loop runtime, no Dashboard preview
display runtime, no preview renderer, reads no real queue DB, writes no queue, sends no POST,
starts no Worker, connects no OpenClaw, activates no Hermes, opens no shared write, and
reads/writes no Google Sheets.
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
    / "HERMES_OPENCLAW_READ_ONLY_DASHBOARD_BLACKBOARD_LOOP_PREVIEW_DISPLAY_PLAN_V0_8_0_D.md"
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
ok("v0.8.0-D plan doc 存在") if DOC_PATH.exists() else xx("v0.8.0-D plan doc 存在")
if not DOC_PATH.exists():
    print("\nXX plan doc 不存在，無法繼續")
    sys.exit(1)

doc = DOC_PATH.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# [2] 必須包含的章節（1-36）
# ---------------------------------------------------------------------------
print("[2] 必須包含的章節")
REQUIRED_SECTIONS = [
    "1. Purpose",
    "2. Current master",
    "3. Scope",
    "4. Relationship to v0.8.0-C Local Dry-run Blackboard Loop Preview Plan",
    "5. Problem statement",
    "6. Read-only Dashboard Blackboard Loop preview display definition",
    "7. Dashboard display contract boundary",
    "8. Dashboard source boundary",
    "9. Dashboard preview input boundary",
    "10. Dashboard preview output boundary",
    "11. Read-only display state boundary",
    "12. Owner review checklist display boundary",
    "13. Decision audit display boundary",
    "14. Dispatch-disabled display boundary",
    "15. Task draft display boundary",
    "16. Result observation display boundary",
    "17. Advice observation display boundary",
    "18. Local-only Dashboard display boundary",
    "19. Queue and data display boundary",
    "20. Dashboard route / template / static boundary",
    "21. Remote Blackboard API relationship",
    "22. Worker / OpenClaw / Hermes separation boundary",
    "23. Google Sheets boundary",
    "24. Secrets / privacy / memory boundary",
    "25. Network / webhook / connector boundary",
    "26. Failure / rollback / audit boundary",
    "27. Candidate Dashboard display fields",
    "28. Candidate Dashboard display validation rules",
    "29. Candidate future phases",
    "30. Disabled runtime list",
    "31. Current safe system posture",
    "32. Validation summary",
    "33. Safety grep summary",
    "34. Non-goals",
    "35. Acceptance criteria",
    "36. Next recommended step",
]
for section in REQUIRED_SECTIONS:
    ok(f"doc 含章節「{section}」") if section in doc else xx(f"doc 含章節「{section}」")

# ---------------------------------------------------------------------------
# [3] 必須包含的 markers
# ---------------------------------------------------------------------------
print("[3] 必須包含的 markers")
REQUIRED = [
    # version
    "v0.8.0-D",
    "Read-only Dashboard Blackboard Loop Preview Display Plan",
    # current master
    "HEAD = origin/master = 94f5f51dfcf404b5ebc87aa9d1830a05ee8be353",
    "docs: plan local dry-run blackboard loop preview",
    # v0.8.0-D plan-first markers
    "v0.8.0-D Read-only Dashboard Blackboard Loop Preview Display Plan is plan-first.",
    "v0.8.0-D does not implement Blackboard Loop runtime.",
    "v0.8.0-D does not implement Dashboard preview display runtime.",
    "v0.8.0-D does not implement preview runtime.",
    "v0.8.0-D does not create preview renderer runtime.",
    "v0.8.0-D does not create Dashboard route.",
    "v0.8.0-D does not create Dashboard endpoint.",
    "v0.8.0-D does not create Dashboard template.",
    "v0.8.0-D does not create Dashboard static asset.",
    "v0.8.0-D does not modify Dashboard runtime.",
    "v0.8.0-D does not modify app.",
    "v0.8.0-D does not modify templates.",
    "v0.8.0-D does not modify static.",
    "v0.8.0-D does not implement loop contract runtime.",
    "v0.8.0-D does not implement state machine runtime.",
    "v0.8.0-D does not create loop scheduler.",
    "v0.8.0-D does not enable dispatch gate.",
    "v0.8.0-D does not enable autonomous execution.",
    "v0.8.0-D does not activate Hermes.",
    "v0.8.0-D does not connect Hermes.",
    "v0.8.0-D does not connect OpenClaw.",
    "v0.8.0-D does not start Worker.",
    "v0.8.0-D does not create Hermes runtime.",
    "v0.8.0-D does not create OpenClaw runtime.",
    "v0.8.0-D does not create Worker runtime.",
    "v0.8.0-D does not implement Remote Blackboard API runtime.",
    "v0.8.0-D does not create production DB.",
    "v0.8.0-D does not create shared DB.",
    "v0.8.0-D does not create remote shared DB.",
    "v0.8.0-D does not read real queue DB.",
    "v0.8.0-D does not modify queue data.",
    "v0.8.0-D does not migrate queue data.",
    "v0.8.0-D does not sync local queue and remote queue.",
    "v0.8.0-D does not open shared write.",
    "v0.8.0-D does not read Google Sheets.",
    "v0.8.0-D does not write Google Sheets.",
    "v0.8.0-D does not send POST.",
    "v0.8.0-D does not create webhook.",
    # relationship to v0.8.0-C
    "v0.8.0-C Local Dry-run Blackboard Loop Preview Plan is complete.",
    "v0.8.0-D starts the Read-only Dashboard Blackboard Loop Preview Display planning step.",
    "v0.8.0-D builds on Local Dry-run Blackboard Loop Preview planning.",
    "v0.8.0-D plans read-only Dashboard preview display before any Dashboard runtime change.",
    "v0.8.0-D preserves Owner final approval authority.",
    "v0.8.0-D preserves decision and dispatch separation.",
    "v0.8.0-D preserves audit trail.",
    "v0.8.0-D preserves dispatch-disabled boundary.",
    "v0.8.0-D preserves local dry-run preview boundary.",
    "v0.8.0-D does not change any v0.8.0-C boundary.",
    "v0.8.0-D does not change any v0.8.0-B boundary.",
    "v0.8.0-D does not change any v0.8.0-A boundary.",
    "v0.8.0-D does not change any v0.7.5 boundary.",
    # problem statement
    "The system needs a planned read-only Dashboard preview display before any Dashboard preview runtime can be implemented.",
    "The Dashboard preview display must not read real queue DB.",
    "The Dashboard preview display must not write queue data.",
    "The Dashboard preview display must not send POST.",
    "The Dashboard preview display must not become Worker dispatch.",
    "The Dashboard preview display must not call OpenClaw.",
    "The Dashboard preview display must not activate Hermes.",
    "The Dashboard preview display must not write Google Sheets.",
    "Planning read-only Dashboard preview display is not implementing Dashboard runtime.",
    "Planning read-only Dashboard preview display is not running the loop.",
    # display definition
    "Read-only Dashboard Blackboard Loop preview display means a future Dashboard-only display of planned loop preview states and messages.",
    "Read-only Dashboard Blackboard Loop preview display is a planning artifact in v0.8.0-D.",
    "Read-only Dashboard Blackboard Loop preview display is not runtime code.",
    "Read-only Dashboard Blackboard Loop preview display is not Dashboard route implementation.",
    "Read-only Dashboard Blackboard Loop preview display is not template implementation.",
    "Read-only Dashboard Blackboard Loop preview display is not static asset implementation.",
    "Read-only Dashboard Blackboard Loop preview display is not queue write.",
    "Read-only Dashboard Blackboard Loop preview display is not real queue DB read.",
    "Read-only Dashboard Blackboard Loop preview display is not Worker dispatch.",
    "Read-only Dashboard Blackboard Loop preview display is not OpenClaw call.",
    "Read-only Dashboard Blackboard Loop preview display is not Hermes activation.",
    "Read-only Dashboard Blackboard Loop preview display is not Google Sheets write.",
    "Read-only Dashboard Blackboard Loop preview display requires separate future plan and Owner approval before implementation.",
    # Dashboard display contract boundary
    "Dashboard display contract describes what a future read-only Dashboard preview may show.",
    "Dashboard display contract is not execution permission.",
    "Dashboard display contract is not runtime approval.",
    "Dashboard display contract is not API route.",
    "Dashboard display contract is not database schema.",
    "Dashboard display contract is not Worker dispatch.",
    "Dashboard display contract is not OpenClaw call.",
    "Dashboard display contract is not Hermes action.",
    "No Dashboard display contract runtime is implemented in v0.8.0-D.",
    # Dashboard source boundary
    "Dashboard source boundary is planning only.",
    "Dashboard source boundary does not select production queue.",
    "Dashboard source boundary does not read real queue DB.",
    "Dashboard source boundary does not read Remote Blackboard API.",
    "Dashboard source boundary does not read Google Sheets.",
    "Dashboard source boundary does not switch source-of-truth.",
    "No Dashboard source reader is implemented in v0.8.0-D.",
    # Dashboard preview input boundary
    "Dashboard preview input may be future mock Task Message data.",
    "Dashboard preview input may be future mock Decision Message data.",
    "Dashboard preview input may be future mock Result Message data.",
    "Dashboard preview input may be future mock Advice Message data.",
    "Dashboard preview input must not require real queue DB read in v0.8.0-D.",
    "Dashboard preview input must not require secrets.",
    "Dashboard preview input must not require Google Sheets.",
    "Dashboard preview input must not require Remote Blackboard API runtime.",
    "No Dashboard preview input reader is implemented in v0.8.0-D.",
    # Dashboard preview output boundary
    "Dashboard preview output may be future read-only card display.",
    "Dashboard preview output may be future read-only state table.",
    "Dashboard preview output may be future read-only Owner review checklist.",
    "Dashboard preview output may be future read-only dispatch-disabled badge.",
    "Dashboard preview output must not write queue data.",
    "Dashboard preview output must not send POST.",
    "Dashboard preview output must not dispatch Worker.",
    "Dashboard preview output must not call OpenClaw.",
    "Dashboard preview output must not call Hermes.",
    "Dashboard preview output must not write Google Sheets.",
    "No Dashboard preview output renderer is implemented in v0.8.0-D.",
    # read-only display state boundary
    "Read-only display state is display-only planning state.",
    "Read-only display state is not execution permission.",
    "Read-only display state is not queue mutation.",
    "Read-only display state is not Worker dispatch.",
    "Read-only display state is not OpenClaw call.",
    "Read-only display state is not Hermes action.",
    "Read-only display state is not Google Sheets write.",
    "No read-only display state runtime is implemented in v0.8.0-D.",
    # Owner review checklist display boundary
    "Owner review checklist display is display-only.",
    "Owner review checklist display is not execution permission.",
    "Owner review checklist display is not Worker dispatch.",
    "Owner review checklist display must preserve approve is not execute.",
    "Owner review checklist display must preserve approval readiness is not execution permission.",
    "No Owner review checklist display runtime is implemented in v0.8.0-D.",
    # Decision audit display boundary
    "Decision audit display is display-only.",
    "Decision audit display is audit display, not command.",
    "Decision audit display is not Worker dispatch.",
    "Decision audit display is not OpenClaw call.",
    "Decision audit display is not Hermes action.",
    "No Decision audit display runtime is implemented in v0.8.0-D.",
    # Dispatch-disabled display boundary
    "Dispatch-disabled display means future Dashboard display must visibly show dispatch is off.",
    "Dispatch-disabled display must block Worker dispatch.",
    "Dispatch-disabled display must block OpenClaw call.",
    "Dispatch-disabled display must block Hermes action.",
    "Dispatch-disabled display must block Google Sheets write.",
    "Dispatch gate remains disabled in v0.8.0-D.",
    "No dispatch-disabled display runtime is implemented in v0.8.0-D.",
    # Task draft display boundary
    "Task draft display is display-only.",
    "Task draft display is not queue write.",
    "Task draft display is not Worker dispatch.",
    "Task draft display is not OpenClaw call.",
    "Task draft display is not Hermes action.",
    "No Task draft display runtime is implemented in v0.8.0-D.",
    # Result observation display boundary
    "Result observation display is display-only.",
    "Result observation display is not next dispatch permission.",
    "Result observation display is not automatic follow-up execution.",
    "Result observation display is not Google Sheets write.",
    "No Result observation display runtime is implemented in v0.8.0-D.",
    # Advice observation display boundary
    "Advice observation display is display-only.",
    "Advice observation display is advisory display, not command.",
    "Advice observation display is not Worker dispatch.",
    "Advice observation display is not OpenClaw call.",
    "Advice observation display is not automatic execution.",
    "No Advice observation display runtime is implemented in v0.8.0-D.",
    # local-only Dashboard display boundary
    "Local-only Dashboard display plan does not select production host.",
    "Local-only Dashboard display plan does not create runtime host.",
    "Local-only Dashboard display plan does not deploy service.",
    "Local-only Dashboard display plan does not create systemd service.",
    "Local-only Dashboard display plan does not create daemon.",
    "Local-only Dashboard display plan does not create Docker deployment.",
    # queue and data display boundary
    "No source-of-truth switch is performed.",
    "No queue DB change.",
    "No local queue data change.",
    "No Replit queue data change.",
    "No real queue DB read.",
    "No queue migration is performed.",
    "No queue synchronization is performed.",
    "No queue backfill is performed.",
    "No queue merge is performed.",
    "No conflict resolver is implemented.",
    "No shared write is enabled.",
    # Dashboard route / template / static boundary
    "Dashboard route boundary is planning only.",
    "No Dashboard route is created in v0.8.0-D.",
    "No Dashboard endpoint is created in v0.8.0-D.",
    "No Dashboard template is created in v0.8.0-D.",
    "No Dashboard static asset is created in v0.8.0-D.",
    "No app route is modified in v0.8.0-D.",
    "No template file is modified in v0.8.0-D.",
    "No static file is modified in v0.8.0-D.",
    # Remote Blackboard API relationship
    "Remote Blackboard API remains planning only.",
    "Remote Blackboard API runtime is not implemented in v0.8.0-D.",
    "Remote Blackboard API read is not enabled in v0.8.0-D.",
    "Remote Blackboard API write is not enabled in v0.8.0-D.",
    "Remote Blackboard API is not required for read-only Dashboard preview display planning.",
    # separation
    "Worker remains OFF.",
    "OpenClaw remains Not Connected.",
    "Hermes remains Not Connected.",
    "Worker is dispatch runtime.",
    "OpenClaw is execution / gateway / tools layer.",
    "Hermes is strategy / proxy / memory layer.",
    "Worker must not run from plan-only Dashboard display.",
    "OpenClaw must not execute from plan-only Dashboard display.",
    "Hermes must not act from plan-only Dashboard display.",
    # Google Sheets boundary
    "Google Sheets remains Disabled.",
    "No Google Sheets read is required.",
    "No Google Sheets write is performed.",
    "No Google Sheets live write is enabled.",
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
    # failure / rollback / audit boundary
    "Future Dashboard display changes must be auditable.",
    "Future Dashboard display actions must include rollback notes when external actions are involved.",
    "Future Dashboard display failures must not silently retry external actions.",
    "Future Dashboard display failures must not bypass Owner approval.",
    "Future Dashboard display failures must not write Google Sheets by default.",
    "Future Dashboard display failures must not call OpenClaw by default.",
    "Future Dashboard display failures must not start Worker by default.",
    "No Dashboard display failure handling runtime is implemented in v0.8.0-D.",
    # candidate Dashboard display fields
    "Candidate Dashboard display field: preview_id.",
    "Candidate Dashboard display field: preview_mode.",
    "Candidate Dashboard display field: message_family.",
    "Candidate Dashboard display field: planned_state.",
    "Candidate Dashboard display field: owner_review_required.",
    "Candidate Dashboard display field: dispatch_enabled.",
    "Candidate Dashboard display field: dispatch_disabled_badge.",
    "Candidate Dashboard display field: external_side_effects.",
    "Candidate Dashboard display field: queue_read_required.",
    "Candidate Dashboard display field: queue_write_required.",
    "Candidate Dashboard display field: worker_dispatch_allowed.",
    "Candidate Dashboard display field: openclaw_call_allowed.",
    "Candidate Dashboard display field: hermes_action_allowed.",
    "Candidate Dashboard display field: google_sheets_write_allowed.",
    "Candidate Dashboard display field: safety_notes.",
    "Candidate Dashboard display field: next_owner_action.",
    "Candidate Dashboard display fields are planning only.",
    "No candidate Dashboard display field is implemented in v0.8.0-D.",
    "No schema migration is performed in v0.8.0-D.",
    # candidate Dashboard display validation rules
    "Candidate Dashboard display validation rule: dispatch_enabled must remain false.",
    "Candidate Dashboard display validation rule: external_side_effects must remain false.",
    "Candidate Dashboard display validation rule: queue_read_required must remain false unless separately approved.",
    "Candidate Dashboard display validation rule: queue_write_required must remain false.",
    "Candidate Dashboard display validation rule: worker_dispatch_allowed must remain false.",
    "Candidate Dashboard display validation rule: openclaw_call_allowed must remain false.",
    "Candidate Dashboard display validation rule: hermes_action_allowed must remain false.",
    "Candidate Dashboard display validation rule: google_sheets_write_allowed must remain false.",
    "Candidate Dashboard display validation rules are planning only.",
    "No Dashboard display validation runtime is implemented in v0.8.0-D.",
    # candidate future phases
    "Candidate future phase: docs-only Dashboard display plan.",
    "Candidate future phase: candidate Dashboard display field inventory.",
    "Candidate future phase: local mock-data read-only Dashboard preview display.",
    "Candidate future phase: read-only Owner review checklist display.",
    "Candidate future phase: read-only dispatch-disabled badge display.",
    "Candidate future phase: read-only Result and Advice observation display.",
    "Candidate future phases are planning notes only.",
    "No candidate future phase is implemented in v0.8.0-D.",
    "No candidate future phase is enabled in v0.8.0-D.",
    # disabled runtime list
    "Blackboard Loop runtime is disabled.",
    "Dashboard preview display runtime is disabled.",
    "Local dry-run preview runtime is disabled.",
    "Preview renderer runtime is disabled.",
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
    "No Dashboard preview display runtime.",
    "No local dry-run preview runtime.",
    "No preview renderer runtime.",
    "No loop contract runtime.",
    "No state machine runtime.",
    "No loop scheduler.",
    "No dispatch gate enabled.",
    "No autonomous execution.",
    "No Hermes activation.",
    "No Hermes blackboard mode.",
    "No Hermes runtime.",
    "No Hermes memory store.",
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
    "No Google Sheets read.",
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
    "No Dashboard route created.",
    "No Dashboard endpoint created.",
    "No Dashboard template created.",
    "No Dashboard static asset created.",
    "No app route modified.",
    "No template file modified.",
    "No static file modified.",
    "No Core runtime host.",
    "No Worker runtime.",
    "No OpenClaw runtime.",
    "No systemd service.",
    "No daemon.",
    "No Docker deployment.",
    "No queue synchronization.",
    "No queue migration.",
    "No queue backfill.",
    "No queue merge.",
    "No conflict resolver.",
    "No connector.",
    "No tag.",
    # validation summary
    "v0.8.0-D readiness: ALL PASS.",
    "v0.8.0-C readiness: ALL PASS.",
    "v0.8.0-B readiness: ALL PASS.",
    "v0.8.0-A readiness: ALL PASS.",
    "v0.7.5-R readiness: ALL PASS.",
    "v0.7.5-E readiness: ALL PASS.",
    "v0.7.5-D readiness: ALL PASS.",
    "v0.7.5-C readiness: ALL PASS.",
    "v0.7.5-B readiness: ALL PASS.",
    "v0.7.5-A readiness: ALL PASS.",
    "compileall scripts: PASS.",
    # safety grep summary
    "No real unsafe claim was found.",
    "No real secret was found.",
    "Readiness forbidden-pattern matches are benign.",
    # next recommended step
    "v0.8.0-E — Owner Review Dashboard Preview Checklist Plan",
    "v0.8.0-E must remain plan-first unless separately approved.",
    "v0.8.0-E must not implement Blackboard Loop runtime.",
    "v0.8.0-E must not implement Dashboard preview display runtime.",
    "v0.8.0-E must not implement preview runtime.",
    "v0.8.0-E must not enable dispatch gate.",
    "v0.8.0-E must not activate Hermes.",
    "v0.8.0-E must not connect OpenClaw.",
    "v0.8.0-E must not start Worker.",
    "v0.8.0-E must not create production DB.",
    "v0.8.0-E must not create Remote Blackboard API runtime unless separately approved.",
    "v0.8.0-E must not migrate queue data.",
    "v0.8.0-E must not open shared write.",
    "v0.8.0-E must not write Google Sheets.",
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
    "No real queue DB read.",
    "Dashboard preview input must not require real queue DB read in v0.8.0-D.",
    "Read-only Dashboard Blackboard Loop preview display is not real queue DB read.",
    "No Google Sheets read is required.",
    "No Google Sheets read.",
    "No Dashboard route created.",
    "No Dashboard endpoint created.",
    "No Dashboard template created.",
    "No Dashboard static asset created.",
    "No app route modified.",
    "No template file modified.",
    "No static file modified.",
]
scrubbed = doc
for phrase in SAFE_NEGATIONS:
    scrubbed = scrubbed.replace(phrase, "")

FORBIDDEN_SUBSTR = [
    "GOOGLE_SHEETS_ENABLED=true",
    "Blackboard Loop runtime created",
    "Blackboard Loop runtime implemented",
    "Blackboard Loop runtime enabled",
    "Dashboard preview display runtime created",
    "Dashboard preview display runtime implemented",
    "Dashboard preview display runtime enabled",
    "local dry-run preview runtime created",
    "local dry-run preview runtime implemented",
    "local dry-run preview runtime enabled",
    "dry-run preview tool created",
    "preview renderer runtime created",
    "preview renderer runtime implemented",
    "Dashboard route created",
    "Dashboard endpoint created",
    "Dashboard template created",
    "Dashboard static asset created",
    "app route modified",
    "template file modified",
    "static file modified",
    "loop contract runtime created",
    "state machine runtime created",
    "state machine runtime implemented",
    "loop scheduler created",
    "loop scheduler enabled",
    "dispatch gate enabled",
    "autonomous execution enabled",
    "agent autonomy runtime created",
    "Worker enabled",
    "Worker started",
    "Worker runtime created",
    "Worker dispatch enabled",
    "OpenClaw connected",
    "OpenClaw called",
    "OpenClaw runtime created",
    "Hermes connected",
    "Hermes activated",
    "Hermes called",
    "Hermes runtime created",
    "Hermes memory store created",
    "Hermes learning runtime created",
    "Hermes blackboard mode enabled",
    "Google Sheets live write enabled",
    "Google Sheets read",
    "Google Sheets written",
    "Remote Blackboard API runtime created",
    "Remote Blackboard API implemented",
    "Remote Blackboard API route added",
    "Remote Blackboard API read enabled",
    "Remote Blackboard API write enabled",
    "production DB created",
    "shared DB created",
    "remote shared DB created",
    "queue DB read",
    "real queue DB read",
    "queue DB modified",
    "local queue data modified",
    "Replit queue data modified",
    "queue migration performed",
    "queue data synchronized",
    "queue data moved",
    "queue data copied",
    "queue data merged",
    "queue data backfilled",
    "conflict resolver implemented",
    "shared write enabled",
    "Blackboard shared write enabled",
    "POST to Replit Preview was sent",
    "POST to real queue was sent",
    "live queue write validation performed",
    "webhook created",
    "webhook receiver created",
    "connector created",
    "external network call added",
    "API route added",
    "FastAPI router added",
    "database client added",
    "migration added",
    "schema migration performed",
    "message schema migration performed",
    "source-of-truth switch performed",
    "cleanup applied",
    "demo task cleaned up",
    "tasks deleted",
    "tasks archived",
    "apply_allowed = True",
    "apply_requested = True",
    "dry_run = False",
    "external_side_effects = True",
    "secrets read",
    "secrets copied",
    "secrets created",
    ".env created",
    "credentials moved",
    "tag created",
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
    print(f"\nXX v0.8.0-D readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print(
        "\nv0.8.0-D Read-only Dashboard Blackboard Loop Preview Display Plan readiness: ALL PASS"
    )
    sys.exit(0)
