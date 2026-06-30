"""v0.8.0-F readiness check: Decision Audit Dashboard Preview Display Plan (plan-first).

Plan-first / boundary verification. Checks that the v0.8.0-F plan document exists and
contains the required sections (1-39), the current-master marker, the v0.8.0-F plan-first
markers, the relationship-to-v0.8.0-E markers, the problem-statement markers, the Decision
Audit Dashboard Preview Display definition markers, the display contract / audit item / record
visibility / audit trail preservation markers, the Owner review relationship and
approval/dispatch separation markers, the dispatch-disabled audit display markers, the Task /
Result / Advice audit display markers, the Dashboard display relationship markers, the
Dashboard route / template / static boundary markers, the Decision audit source / input /
output boundary markers, the local-only Dashboard audit display markers, the queue and data
boundary markers, the Remote Blackboard API relationship markers, the Worker / OpenClaw /
Hermes separation markers, the Google Sheets boundary markers, the secrets / privacy / memory
boundary markers, the network / webhook / connector boundary markers, the failure / rollback /
audit boundary markers, the candidate Decision audit display fields markers, the candidate
validation rules markers, the candidate future phases markers, the disabled runtime list
markers, the current safe posture markers, the validation summary markers, the safety grep
summary markers, and the next recommended step — and that it asserts no unsafe "implemented /
created / added / enabled / activated / connected / called / started / written / read /
modified / moved / migrated" claim and contains no secret.

The document is allowed to contain safe negations; those that literally embed a
forbidden substring are scrubbed before the forbidden scan so they are not mis-flagged.

This script only reads the plan document. It does NOT read .env, credentials, tokens, or
secrets, makes no network call, imports no app logic (no app.main, no QueueStore), adds no
API route / router / Dashboard route / template / static / database client / migration,
creates no production / shared DB, builds no Blackboard Loop runtime, no Decision audit
display runtime, no Dashboard preview display runtime, reads no real queue DB, writes no
queue, sends no POST, starts no Worker, connects no OpenClaw, activates no Hermes, opens no
shared write, and reads/writes no Google Sheets.
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
    / "HERMES_OPENCLAW_DECISION_AUDIT_DASHBOARD_PREVIEW_DISPLAY_PLAN_V0_8_0_F.md"
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
ok("v0.8.0-F plan doc 存在") if DOC_PATH.exists() else xx("v0.8.0-F plan doc 存在")
if not DOC_PATH.exists():
    print("\nXX plan doc 不存在，無法繼續")
    sys.exit(1)

doc = DOC_PATH.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# [2] 必須包含的章節（1-39）
# ---------------------------------------------------------------------------
print("[2] 必須包含的章節")
REQUIRED_SECTIONS = [
    "1. Purpose",
    "2. Current master",
    "3. Scope",
    "4. Relationship to v0.8.0-E Owner Review Dashboard Preview Checklist Plan",
    "5. Problem statement",
    "6. Decision Audit Dashboard Preview Display definition",
    "7. Decision audit display contract boundary",
    "8. Audit item boundary",
    "9. Decision record visibility boundary",
    "10. Audit trail preservation boundary",
    "11. Owner review relationship boundary",
    "12. Approval and dispatch separation boundary",
    "13. Dispatch-disabled audit display boundary",
    "14. Task draft audit display boundary",
    "15. Result observation audit display boundary",
    "16. Advice observation audit display boundary",
    "17. Dashboard display relationship",
    "18. Dashboard route / template / static boundary",
    "19. Decision audit source boundary",
    "20. Decision audit input boundary",
    "21. Decision audit output boundary",
    "22. Local-only Dashboard audit display boundary",
    "23. Queue and data boundary",
    "24. Remote Blackboard API relationship",
    "25. Worker / OpenClaw / Hermes separation boundary",
    "26. Google Sheets boundary",
    "27. Secrets / privacy / memory boundary",
    "28. Network / webhook / connector boundary",
    "29. Failure / rollback / audit boundary",
    "30. Candidate Decision audit display fields",
    "31. Candidate Decision audit display validation rules",
    "32. Candidate future phases",
    "33. Disabled runtime list",
    "34. Current safe system posture",
    "35. Validation summary",
    "36. Safety grep summary",
    "37. Non-goals",
    "38. Acceptance criteria",
    "39. Next recommended step",
]
for section in REQUIRED_SECTIONS:
    ok(f"doc 含章節「{section}」") if section in doc else xx(f"doc 含章節「{section}」")

# ---------------------------------------------------------------------------
# [3] 必須包含的 markers
# ---------------------------------------------------------------------------
print("[3] 必須包含的 markers")
REQUIRED = [
    # version
    "v0.8.0-F",
    "Decision Audit Dashboard Preview Display Plan",
    # current master
    "HEAD = origin/master = 73bb1d94d3ace3c10878da998f21ca48602ef575",
    "docs: plan owner review dashboard preview checklist",
    # v0.8.0-F plan-first markers
    "v0.8.0-F Decision Audit Dashboard Preview Display Plan is plan-first.",
    "v0.8.0-F does not implement Blackboard Loop runtime.",
    "v0.8.0-F does not implement Decision audit display runtime.",
    "v0.8.0-F does not implement Owner review checklist runtime.",
    "v0.8.0-F does not implement Dashboard preview display runtime.",
    "v0.8.0-F does not implement preview runtime.",
    "v0.8.0-F does not create preview renderer runtime.",
    "v0.8.0-F does not create Dashboard route.",
    "v0.8.0-F does not create Dashboard endpoint.",
    "v0.8.0-F does not create Dashboard template.",
    "v0.8.0-F does not create Dashboard static asset.",
    "v0.8.0-F does not modify Dashboard runtime.",
    "v0.8.0-F does not modify app.",
    "v0.8.0-F does not modify templates.",
    "v0.8.0-F does not modify static.",
    "v0.8.0-F does not implement loop contract runtime.",
    "v0.8.0-F does not implement state machine runtime.",
    "v0.8.0-F does not create loop scheduler.",
    "v0.8.0-F does not enable dispatch gate.",
    "v0.8.0-F does not enable autonomous execution.",
    "v0.8.0-F does not activate Hermes.",
    "v0.8.0-F does not connect Hermes.",
    "v0.8.0-F does not connect OpenClaw.",
    "v0.8.0-F does not start Worker.",
    "v0.8.0-F does not create Hermes runtime.",
    "v0.8.0-F does not create OpenClaw runtime.",
    "v0.8.0-F does not create Worker runtime.",
    "v0.8.0-F does not implement Remote Blackboard API runtime.",
    "v0.8.0-F does not create production DB.",
    "v0.8.0-F does not create shared DB.",
    "v0.8.0-F does not create remote shared DB.",
    "v0.8.0-F does not read real queue DB.",
    "v0.8.0-F does not modify queue data.",
    "v0.8.0-F does not migrate queue data.",
    "v0.8.0-F does not sync local queue and remote queue.",
    "v0.8.0-F does not open shared write.",
    "v0.8.0-F does not read Google Sheets.",
    "v0.8.0-F does not write Google Sheets.",
    "v0.8.0-F does not send POST.",
    "v0.8.0-F does not create webhook.",
    # relationship to v0.8.0-E
    "v0.8.0-E Owner Review Dashboard Preview Checklist Plan is complete.",
    "v0.8.0-F starts the Decision Audit Dashboard Preview Display planning step.",
    "v0.8.0-F builds on Owner Review Dashboard Preview Checklist planning.",
    "v0.8.0-F plans Decision audit Dashboard preview display before any Dashboard runtime change.",
    "v0.8.0-F preserves Owner final approval authority.",
    "v0.8.0-F preserves decision and dispatch separation.",
    "v0.8.0-F preserves audit trail.",
    "v0.8.0-F preserves dispatch-disabled boundary.",
    "v0.8.0-F preserves local dry-run preview boundary.",
    "v0.8.0-F preserves read-only Dashboard display boundary.",
    "v0.8.0-F preserves Owner review checklist boundary.",
    "v0.8.0-F does not change any v0.8.0-E boundary.",
    "v0.8.0-F does not change any v0.8.0-D boundary.",
    "v0.8.0-F does not change any v0.8.0-C boundary.",
    "v0.8.0-F does not change any v0.8.0-B boundary.",
    "v0.8.0-F does not change any v0.8.0-A boundary.",
    "v0.8.0-F does not change any v0.7.5 boundary.",
    # problem statement
    "The system needs a planned Decision audit Dashboard preview display before any decision audit display runtime can be implemented.",
    "The Decision audit display must not become execution permission.",
    "The Decision audit display must not become Worker dispatch.",
    "The Decision audit display must not call OpenClaw.",
    "The Decision audit display must not activate Hermes.",
    "The Decision audit display must not write queue data.",
    "The Decision audit display must not read real queue DB.",
    "The Decision audit display must not send POST.",
    "The Decision audit display must not read or write Google Sheets.",
    "Planning Decision audit Dashboard preview display is not implementing Dashboard runtime.",
    "Planning Decision audit Dashboard preview display is not running the loop.",
    # definition
    "Decision Audit Dashboard Preview Display means a future read-only Dashboard display that helps the Owner inspect planned decision records and audit notes.",
    "Decision Audit Dashboard Preview Display is a planning artifact in v0.8.0-F.",
    "Decision Audit Dashboard Preview Display is not runtime code.",
    "Decision Audit Dashboard Preview Display is not Dashboard route implementation.",
    "Decision Audit Dashboard Preview Display is not template implementation.",
    "Decision Audit Dashboard Preview Display is not static asset implementation.",
    "Decision Audit Dashboard Preview Display is not execution permission.",
    "Decision Audit Dashboard Preview Display is not queue write.",
    "Decision Audit Dashboard Preview Display is not real queue DB read.",
    "Decision Audit Dashboard Preview Display is not Worker dispatch.",
    "Decision Audit Dashboard Preview Display is not OpenClaw call.",
    "Decision Audit Dashboard Preview Display is not Hermes activation.",
    "Decision Audit Dashboard Preview Display is not Google Sheets write.",
    "Decision Audit Dashboard Preview Display requires separate future plan and Owner approval before implementation.",
    # display contract boundary
    "Decision audit display contract describes what a future read-only decision audit display may show.",
    "Decision audit display contract is not execution permission.",
    "Decision audit display contract is not runtime approval.",
    "Decision audit display contract is not API route.",
    "Decision audit display contract is not database schema.",
    "Decision audit display contract is not Worker dispatch.",
    "Decision audit display contract is not OpenClaw call.",
    "Decision audit display contract is not Hermes action.",
    "No Decision audit display contract runtime is implemented in v0.8.0-F.",
    # audit item boundary
    "Audit item boundary is planning only.",
    "Audit item may describe planned decision family.",
    "Audit item may describe planned state.",
    "Audit item may describe required Owner review.",
    "Audit item may describe dispatch-disabled status.",
    "Audit item may describe external side effect status.",
    "Audit item may describe decision reason summary.",
    "Audit item must not execute action.",
    "Audit item must not mutate queue.",
    "Audit item must not start Worker.",
    "Audit item must not call OpenClaw.",
    "Audit item must not call Hermes.",
    "No audit item runtime is implemented in v0.8.0-F.",
    # decision record visibility
    "Decision record visibility means a future display may show that a decision record exists or is required.",
    "Decision record visibility is not decision execution.",
    "Decision record visibility is not Worker dispatch.",
    "Decision record visibility is not OpenClaw call.",
    "Decision record visibility is not Hermes action.",
    "Decision record visibility must preserve Owner final approval authority.",
    "No Decision record visibility runtime is implemented in v0.8.0-F.",
    # audit trail preservation
    "Audit trail preservation means future display must preserve reviewability of planned decisions.",
    "Audit trail preservation is not execution permission.",
    "Audit trail preservation is not queue mutation.",
    "Audit trail preservation is not Worker dispatch.",
    "Audit trail preservation is not OpenClaw call.",
    "Audit trail preservation is not Hermes action.",
    "No audit trail preservation runtime is implemented in v0.8.0-F.",
    # Owner review relationship
    "Owner review relationship means future Decision audit display may support Owner review checklist context.",
    "Owner review relationship is display-only.",
    "Owner review relationship is not Owner decision execution.",
    "Owner review relationship is not Worker dispatch.",
    "Owner review relationship is not OpenClaw call.",
    "Owner review relationship is not Hermes action.",
    "No Owner review relationship runtime is implemented in v0.8.0-F.",
    # approval and dispatch separation
    "Approval is not execution.",
    "Approval readiness is not execution permission.",
    "Approval display is not runtime dispatch.",
    "Approval display is not Worker dispatch.",
    "Approval display is not OpenClaw call.",
    "Approval display is not Hermes action.",
    "Approval display must preserve decision and dispatch separation.",
    "No approval dispatch runtime is implemented in v0.8.0-F.",
    # dispatch-disabled audit display
    "Dispatch-disabled audit display means future display must visibly show dispatch is off.",
    "Dispatch-disabled audit display must block Worker dispatch.",
    "Dispatch-disabled audit display must block OpenClaw call.",
    "Dispatch-disabled audit display must block Hermes action.",
    "Dispatch-disabled audit display must block Google Sheets write.",
    "Dispatch gate remains disabled in v0.8.0-F.",
    "No dispatch-disabled audit display runtime is implemented in v0.8.0-F.",
    # Task draft audit display
    "Task draft audit display is display-only.",
    "Task draft audit display is not queue write.",
    "Task draft audit display is not Worker dispatch.",
    "Task draft audit display is not OpenClaw call.",
    "Task draft audit display is not Hermes action.",
    "No Task draft audit display runtime is implemented in v0.8.0-F.",
    # Result observation audit display
    "Result observation audit display is display-only.",
    "Result observation audit display is not next dispatch permission.",
    "Result observation audit display is not automatic follow-up execution.",
    "Result observation audit display is not Google Sheets write.",
    "No Result observation audit display runtime is implemented in v0.8.0-F.",
    # Advice observation audit display
    "Advice observation audit display is display-only.",
    "Advice observation audit display is advisory display, not command.",
    "Advice observation audit display is not Worker dispatch.",
    "Advice observation audit display is not OpenClaw call.",
    "Advice observation audit display is not automatic execution.",
    "No Advice observation audit display runtime is implemented in v0.8.0-F.",
    # Dashboard display relationship
    "Dashboard may eventually display Decision audit preview records.",
    "Dashboard Decision audit display is read-only.",
    "Dashboard Decision audit display is not dispatch.",
    "Dashboard Decision audit display is not execution permission.",
    "No Dashboard Decision audit display runtime is implemented in v0.8.0-F.",
    # Dashboard route / template / static boundary
    "Dashboard route boundary is planning only.",
    "No Dashboard route is created in v0.8.0-F.",
    "No Dashboard endpoint is created in v0.8.0-F.",
    "No Dashboard template is created in v0.8.0-F.",
    "No Dashboard static asset is created in v0.8.0-F.",
    "No app route is modified in v0.8.0-F.",
    "No template file is modified in v0.8.0-F.",
    "No static file is modified in v0.8.0-F.",
    # Decision audit source boundary
    "Decision audit source boundary is planning only.",
    "Decision audit source boundary does not select production queue.",
    "Decision audit source boundary does not read real queue DB.",
    "Decision audit source boundary does not read Remote Blackboard API.",
    "Decision audit source boundary does not read Google Sheets.",
    "Decision audit source boundary does not switch source-of-truth.",
    "No Decision audit source reader is implemented in v0.8.0-F.",
    # Decision audit input boundary
    "Decision audit input may be future mock Task Message data.",
    "Decision audit input may be future mock Decision Message data.",
    "Decision audit input may be future mock Result Message data.",
    "Decision audit input may be future mock Advice Message data.",
    "Decision audit input must not require real queue DB read in v0.8.0-F.",
    "Decision audit input must not require secrets.",
    "Decision audit input must not require Google Sheets.",
    "Decision audit input must not require Remote Blackboard API runtime.",
    "No Decision audit input reader is implemented in v0.8.0-F.",
    # Decision audit output boundary
    "Decision audit output may be future read-only audit card.",
    "Decision audit output may be future read-only audit table.",
    "Decision audit output may be future read-only decision reason summary.",
    "Decision audit output may be future read-only dispatch-disabled badge.",
    "Decision audit output must not write queue data.",
    "Decision audit output must not send POST.",
    "Decision audit output must not dispatch Worker.",
    "Decision audit output must not call OpenClaw.",
    "Decision audit output must not call Hermes.",
    "Decision audit output must not write Google Sheets.",
    "No Decision audit output renderer is implemented in v0.8.0-F.",
    # local-only Dashboard audit display boundary
    "Local-only Dashboard audit display plan does not select production host.",
    "Local-only Dashboard audit display plan does not create runtime host.",
    "Local-only Dashboard audit display plan does not deploy service.",
    "Local-only Dashboard audit display plan does not create systemd service.",
    "Local-only Dashboard audit display plan does not create daemon.",
    "Local-only Dashboard audit display plan does not create Docker deployment.",
    # queue and data boundary
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
    # Remote Blackboard API relationship
    "Remote Blackboard API remains planning only.",
    "Remote Blackboard API runtime is not implemented in v0.8.0-F.",
    "Remote Blackboard API read is not enabled in v0.8.0-F.",
    "Remote Blackboard API write is not enabled in v0.8.0-F.",
    "Remote Blackboard API is not required for Decision audit display planning.",
    # separation
    "Worker remains OFF.",
    "OpenClaw remains Not Connected.",
    "Hermes remains Not Connected.",
    "Worker is dispatch runtime.",
    "OpenClaw is execution / gateway / tools layer.",
    "Hermes is strategy / proxy / memory layer.",
    "Worker must not run from plan-only Decision audit display.",
    "OpenClaw must not execute from plan-only Decision audit display.",
    "Hermes must not act from plan-only Decision audit display.",
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
    "Future Decision audit display changes must be auditable.",
    "Future Decision audit display actions must include rollback notes when external actions are involved.",
    "Future Decision audit display failures must not silently retry external actions.",
    "Future Decision audit display failures must not bypass Owner approval.",
    "Future Decision audit display failures must not write Google Sheets by default.",
    "Future Decision audit display failures must not call OpenClaw by default.",
    "Future Decision audit display failures must not start Worker by default.",
    "No Decision audit display failure handling runtime is implemented in v0.8.0-F.",
    # candidate Decision audit display fields
    "Candidate Decision audit display field: audit_id.",
    "Candidate Decision audit display field: preview_id.",
    "Candidate Decision audit display field: audit_mode.",
    "Candidate Decision audit display field: message_family.",
    "Candidate Decision audit display field: planned_state.",
    "Candidate Decision audit display field: decision_record_required.",
    "Candidate Decision audit display field: decision_reason_summary.",
    "Candidate Decision audit display field: owner_review_required.",
    "Candidate Decision audit display field: owner_decision_required.",
    "Candidate Decision audit display field: approval_is_execution.",
    "Candidate Decision audit display field: approval_readiness_is_execution.",
    "Candidate Decision audit display field: dispatch_enabled.",
    "Candidate Decision audit display field: dispatch_disabled_badge.",
    "Candidate Decision audit display field: external_side_effects.",
    "Candidate Decision audit display field: queue_read_required.",
    "Candidate Decision audit display field: queue_write_required.",
    "Candidate Decision audit display field: worker_dispatch_allowed.",
    "Candidate Decision audit display field: openclaw_call_allowed.",
    "Candidate Decision audit display field: hermes_action_allowed.",
    "Candidate Decision audit display field: google_sheets_write_allowed.",
    "Candidate Decision audit display field: safety_notes.",
    "Candidate Decision audit display field: next_owner_action.",
    "Candidate Decision audit display fields are planning only.",
    "No candidate Decision audit display field is implemented in v0.8.0-F.",
    "No schema migration is performed in v0.8.0-F.",
    # candidate validation rules
    "Candidate Decision audit display validation rule: approval_is_execution must remain false.",
    "Candidate Decision audit display validation rule: approval_readiness_is_execution must remain false.",
    "Candidate Decision audit display validation rule: dispatch_enabled must remain false.",
    "Candidate Decision audit display validation rule: external_side_effects must remain false.",
    "Candidate Decision audit display validation rule: queue_read_required must remain false unless separately approved.",
    "Candidate Decision audit display validation rule: queue_write_required must remain false.",
    "Candidate Decision audit display validation rule: worker_dispatch_allowed must remain false.",
    "Candidate Decision audit display validation rule: openclaw_call_allowed must remain false.",
    "Candidate Decision audit display validation rule: hermes_action_allowed must remain false.",
    "Candidate Decision audit display validation rule: google_sheets_write_allowed must remain false.",
    "Candidate Decision audit display validation rules are planning only.",
    "No Decision audit display validation runtime is implemented in v0.8.0-F.",
    # candidate future phases
    "Candidate future phase: docs-only Decision audit display plan.",
    "Candidate future phase: candidate Decision audit display field inventory.",
    "Candidate future phase: local mock-data read-only Decision audit display.",
    "Candidate future phase: read-only decision record visibility display.",
    "Candidate future phase: read-only dispatch-disabled audit badge display.",
    "Candidate future phase: read-only audit trail preservation display.",
    "Candidate future phases are planning notes only.",
    "No candidate future phase is implemented in v0.8.0-F.",
    "No candidate future phase is enabled in v0.8.0-F.",
    # disabled runtime list
    "Blackboard Loop runtime is disabled.",
    "Decision audit display runtime is disabled.",
    "Owner review checklist runtime is disabled.",
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
    "No Decision audit display runtime.",
    "No Owner review checklist runtime.",
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
    "v0.8.0-F readiness: ALL PASS.",
    "v0.8.0-E readiness: ALL PASS.",
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
    "v0.8.0-G — Dispatch-disabled Dashboard Preview Badge Plan",
    "v0.8.0-G must remain plan-first unless separately approved.",
    "v0.8.0-G must not implement Blackboard Loop runtime.",
    "v0.8.0-G must not implement Decision audit display runtime.",
    "v0.8.0-G must not implement Owner review checklist runtime.",
    "v0.8.0-G must not implement Dashboard preview display runtime.",
    "v0.8.0-G must not enable dispatch gate.",
    "v0.8.0-G must not activate Hermes.",
    "v0.8.0-G must not connect OpenClaw.",
    "v0.8.0-G must not start Worker.",
    "v0.8.0-G must not create production DB.",
    "v0.8.0-G must not create Remote Blackboard API runtime unless separately approved.",
    "v0.8.0-G must not migrate queue data.",
    "v0.8.0-G must not open shared write.",
    "v0.8.0-G must not write Google Sheets.",
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
    "Decision audit input must not require real queue DB read in v0.8.0-F.",
    "Decision Audit Dashboard Preview Display is not real queue DB read.",
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
    "Decision audit display runtime created",
    "Decision audit display runtime implemented",
    "Decision audit display runtime enabled",
    "Owner review checklist runtime created",
    "Owner review checklist runtime implemented",
    "Owner review checklist runtime enabled",
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
    "approval_is_execution = True",
    "approval_readiness_is_execution = True",
    "dispatch_enabled = True",
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
    print(f"\nXX v0.8.0-F readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print(
        "\nv0.8.0-F Decision Audit Dashboard Preview Display Plan readiness: ALL PASS"
    )
    sys.exit(0)
