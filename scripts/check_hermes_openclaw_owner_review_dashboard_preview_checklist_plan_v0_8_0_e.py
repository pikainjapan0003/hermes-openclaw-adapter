"""v0.8.0-E readiness check: Owner Review Dashboard Preview Checklist Plan (plan-first).

Plan-first / boundary verification. Checks that the v0.8.0-E plan document exists and
contains the required sections (1-39), the current-master marker, the v0.8.0-E plan-first
markers, the relationship-to-v0.8.0-D markers, the problem-statement markers, the Owner Review
Dashboard Preview Checklist definition markers, the checklist contract / item / Owner decision
visibility markers, the approval-is-not-execution and approval-readiness markers, the Decision
audit checklist markers, the dispatch-disabled checklist markers, the Task / Result / Advice
checklist markers, the Dashboard display relationship markers, the Dashboard route / template
/ static boundary markers, the checklist source / input / output boundary markers, the
local-only Dashboard checklist markers, the queue and data boundary markers, the Remote
Blackboard API relationship markers, the Worker / OpenClaw / Hermes separation markers, the
Google Sheets boundary markers, the secrets / privacy / memory boundary markers, the network /
webhook / connector boundary markers, the failure / rollback / audit boundary markers, the
candidate Owner review checklist fields markers, the candidate validation rules markers, the
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
creates no production / shared DB, builds no Blackboard Loop runtime, no Owner review
checklist runtime, no Dashboard preview display runtime, reads no real queue DB, writes no
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
    / "HERMES_OPENCLAW_OWNER_REVIEW_DASHBOARD_PREVIEW_CHECKLIST_PLAN_V0_8_0_E.md"
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
ok("v0.8.0-E plan doc 存在") if DOC_PATH.exists() else xx("v0.8.0-E plan doc 存在")
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
    "4. Relationship to v0.8.0-D Read-only Dashboard Blackboard Loop Preview Display Plan",
    "5. Problem statement",
    "6. Owner Review Dashboard Preview Checklist definition",
    "7. Owner review checklist contract boundary",
    "8. Checklist item boundary",
    "9. Owner decision visibility boundary",
    "10. Approval is not execution boundary",
    "11. Approval readiness boundary",
    "12. Decision audit checklist boundary",
    "13. Dispatch-disabled checklist boundary",
    "14. Task draft checklist boundary",
    "15. Result observation checklist boundary",
    "16. Advice observation checklist boundary",
    "17. Dashboard display relationship",
    "18. Dashboard route / template / static boundary",
    "19. Checklist source boundary",
    "20. Checklist input boundary",
    "21. Checklist output boundary",
    "22. Local-only Dashboard checklist boundary",
    "23. Queue and data boundary",
    "24. Remote Blackboard API relationship",
    "25. Worker / OpenClaw / Hermes separation boundary",
    "26. Google Sheets boundary",
    "27. Secrets / privacy / memory boundary",
    "28. Network / webhook / connector boundary",
    "29. Failure / rollback / audit boundary",
    "30. Candidate Owner review checklist fields",
    "31. Candidate Owner review checklist validation rules",
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
    "v0.8.0-E",
    "Owner Review Dashboard Preview Checklist Plan",
    # current master
    "HEAD = origin/master = 586f5b72c1b66154caa3ba663de7eddfa178d1cd",
    "docs: plan read-only dashboard blackboard preview display",
    # v0.8.0-E plan-first markers
    "v0.8.0-E Owner Review Dashboard Preview Checklist Plan is plan-first.",
    "v0.8.0-E does not implement Blackboard Loop runtime.",
    "v0.8.0-E does not implement Owner review checklist runtime.",
    "v0.8.0-E does not implement Dashboard preview display runtime.",
    "v0.8.0-E does not implement preview runtime.",
    "v0.8.0-E does not create preview renderer runtime.",
    "v0.8.0-E does not create Dashboard route.",
    "v0.8.0-E does not create Dashboard endpoint.",
    "v0.8.0-E does not create Dashboard template.",
    "v0.8.0-E does not create Dashboard static asset.",
    "v0.8.0-E does not modify Dashboard runtime.",
    "v0.8.0-E does not modify app.",
    "v0.8.0-E does not modify templates.",
    "v0.8.0-E does not modify static.",
    "v0.8.0-E does not implement loop contract runtime.",
    "v0.8.0-E does not implement state machine runtime.",
    "v0.8.0-E does not create loop scheduler.",
    "v0.8.0-E does not enable dispatch gate.",
    "v0.8.0-E does not enable autonomous execution.",
    "v0.8.0-E does not activate Hermes.",
    "v0.8.0-E does not connect Hermes.",
    "v0.8.0-E does not connect OpenClaw.",
    "v0.8.0-E does not start Worker.",
    "v0.8.0-E does not create Hermes runtime.",
    "v0.8.0-E does not create OpenClaw runtime.",
    "v0.8.0-E does not create Worker runtime.",
    "v0.8.0-E does not implement Remote Blackboard API runtime.",
    "v0.8.0-E does not create production DB.",
    "v0.8.0-E does not create shared DB.",
    "v0.8.0-E does not create remote shared DB.",
    "v0.8.0-E does not read real queue DB.",
    "v0.8.0-E does not modify queue data.",
    "v0.8.0-E does not migrate queue data.",
    "v0.8.0-E does not sync local queue and remote queue.",
    "v0.8.0-E does not open shared write.",
    "v0.8.0-E does not read Google Sheets.",
    "v0.8.0-E does not write Google Sheets.",
    "v0.8.0-E does not send POST.",
    "v0.8.0-E does not create webhook.",
    # relationship to v0.8.0-D
    "v0.8.0-D Read-only Dashboard Blackboard Loop Preview Display Plan is complete.",
    "v0.8.0-E starts the Owner Review Dashboard Preview Checklist planning step.",
    "v0.8.0-E builds on Read-only Dashboard Blackboard Loop Preview Display planning.",
    "v0.8.0-E plans Owner review checklist display before any Dashboard runtime change.",
    "v0.8.0-E preserves Owner final approval authority.",
    "v0.8.0-E preserves decision and dispatch separation.",
    "v0.8.0-E preserves audit trail.",
    "v0.8.0-E preserves dispatch-disabled boundary.",
    "v0.8.0-E preserves local dry-run preview boundary.",
    "v0.8.0-E preserves read-only Dashboard display boundary.",
    "v0.8.0-E does not change any v0.8.0-D boundary.",
    "v0.8.0-E does not change any v0.8.0-C boundary.",
    "v0.8.0-E does not change any v0.8.0-B boundary.",
    "v0.8.0-E does not change any v0.8.0-A boundary.",
    "v0.8.0-E does not change any v0.7.5 boundary.",
    # problem statement
    "The system needs a planned Owner review Dashboard preview checklist before any checklist runtime can be implemented.",
    "The Owner review checklist must not become execution permission.",
    "The Owner review checklist must not become Worker dispatch.",
    "The Owner review checklist must not call OpenClaw.",
    "The Owner review checklist must not activate Hermes.",
    "The Owner review checklist must not write queue data.",
    "The Owner review checklist must not read real queue DB.",
    "The Owner review checklist must not send POST.",
    "The Owner review checklist must not read or write Google Sheets.",
    "Planning Owner review Dashboard preview checklist is not implementing Dashboard runtime.",
    "Planning Owner review Dashboard preview checklist is not running the loop.",
    # checklist definition
    "Owner Review Dashboard Preview Checklist means a future read-only Dashboard checklist that helps the Owner review planned loop preview items.",
    "Owner Review Dashboard Preview Checklist is a planning artifact in v0.8.0-E.",
    "Owner Review Dashboard Preview Checklist is not runtime code.",
    "Owner Review Dashboard Preview Checklist is not Dashboard route implementation.",
    "Owner Review Dashboard Preview Checklist is not template implementation.",
    "Owner Review Dashboard Preview Checklist is not static asset implementation.",
    "Owner Review Dashboard Preview Checklist is not execution permission.",
    "Owner Review Dashboard Preview Checklist is not queue write.",
    "Owner Review Dashboard Preview Checklist is not real queue DB read.",
    "Owner Review Dashboard Preview Checklist is not Worker dispatch.",
    "Owner Review Dashboard Preview Checklist is not OpenClaw call.",
    "Owner Review Dashboard Preview Checklist is not Hermes activation.",
    "Owner Review Dashboard Preview Checklist is not Google Sheets write.",
    "Owner Review Dashboard Preview Checklist requires separate future plan and Owner approval before implementation.",
    # checklist contract boundary
    "Owner review checklist contract describes what a future read-only Owner checklist may show.",
    "Owner review checklist contract is not execution permission.",
    "Owner review checklist contract is not runtime approval.",
    "Owner review checklist contract is not API route.",
    "Owner review checklist contract is not database schema.",
    "Owner review checklist contract is not Worker dispatch.",
    "Owner review checklist contract is not OpenClaw call.",
    "Owner review checklist contract is not Hermes action.",
    "No Owner review checklist contract runtime is implemented in v0.8.0-E.",
    # checklist item boundary
    "Checklist item boundary is planning only.",
    "Checklist item may describe planned message family.",
    "Checklist item may describe planned state.",
    "Checklist item may describe required Owner review.",
    "Checklist item may describe dispatch-disabled status.",
    "Checklist item may describe external side effect status.",
    "Checklist item must not execute action.",
    "Checklist item must not mutate queue.",
    "Checklist item must not start Worker.",
    "Checklist item must not call OpenClaw.",
    "Checklist item must not call Hermes.",
    "No checklist item runtime is implemented in v0.8.0-E.",
    # Owner decision visibility
    "Owner decision visibility means a future checklist may show that Owner decision is required.",
    "Owner decision visibility is not Owner decision execution.",
    "Owner decision visibility is not Worker dispatch.",
    "Owner decision visibility is not OpenClaw call.",
    "Owner decision visibility is not Hermes action.",
    "Owner decision visibility must preserve Owner final approval authority.",
    "No Owner decision visibility runtime is implemented in v0.8.0-E.",
    # approval is not execution
    "Approval is not execution.",
    "Owner approval display is not runtime dispatch.",
    "Owner approval display is not Worker dispatch.",
    "Owner approval display is not OpenClaw call.",
    "Owner approval display is not Hermes action.",
    "Owner approval display must preserve decision and dispatch separation.",
    "No approval execution runtime is implemented in v0.8.0-E.",
    # approval readiness
    "Approval readiness is not execution permission.",
    "Approval readiness is not dispatch permission.",
    "Approval readiness is not queue mutation.",
    "Approval readiness is not Worker dispatch.",
    "Approval readiness is not OpenClaw call.",
    "Approval readiness is not Hermes action.",
    "No approval readiness runtime is implemented in v0.8.0-E.",
    # Decision audit checklist
    "Decision audit checklist is display-only.",
    "Decision audit checklist is audit checklist, not command.",
    "Decision audit checklist is not Worker dispatch.",
    "Decision audit checklist is not OpenClaw call.",
    "Decision audit checklist is not Hermes action.",
    "Decision audit checklist must preserve audit trail.",
    "No Decision audit checklist runtime is implemented in v0.8.0-E.",
    # Dispatch-disabled checklist
    "Dispatch-disabled checklist means future checklist must visibly show dispatch is off.",
    "Dispatch-disabled checklist must block Worker dispatch.",
    "Dispatch-disabled checklist must block OpenClaw call.",
    "Dispatch-disabled checklist must block Hermes action.",
    "Dispatch-disabled checklist must block Google Sheets write.",
    "Dispatch gate remains disabled in v0.8.0-E.",
    "No dispatch-disabled checklist runtime is implemented in v0.8.0-E.",
    # Task draft checklist
    "Task draft checklist is display-only.",
    "Task draft checklist is not queue write.",
    "Task draft checklist is not Worker dispatch.",
    "Task draft checklist is not OpenClaw call.",
    "Task draft checklist is not Hermes action.",
    "No Task draft checklist runtime is implemented in v0.8.0-E.",
    # Result observation checklist
    "Result observation checklist is display-only.",
    "Result observation checklist is not next dispatch permission.",
    "Result observation checklist is not automatic follow-up execution.",
    "Result observation checklist is not Google Sheets write.",
    "No Result observation checklist runtime is implemented in v0.8.0-E.",
    # Advice observation checklist
    "Advice observation checklist is display-only.",
    "Advice observation checklist is advisory display, not command.",
    "Advice observation checklist is not Worker dispatch.",
    "Advice observation checklist is not OpenClaw call.",
    "Advice observation checklist is not automatic execution.",
    "No Advice observation checklist runtime is implemented in v0.8.0-E.",
    # Dashboard display relationship
    "Dashboard may eventually display Owner review checklist.",
    "Dashboard Owner review checklist display is read-only.",
    "Dashboard Owner review checklist display is not dispatch.",
    "Dashboard Owner review checklist display is not execution permission.",
    "No Dashboard Owner review checklist display runtime is implemented in v0.8.0-E.",
    # Dashboard route / template / static boundary
    "Dashboard route boundary is planning only.",
    "No Dashboard route is created in v0.8.0-E.",
    "No Dashboard endpoint is created in v0.8.0-E.",
    "No Dashboard template is created in v0.8.0-E.",
    "No Dashboard static asset is created in v0.8.0-E.",
    "No app route is modified in v0.8.0-E.",
    "No template file is modified in v0.8.0-E.",
    "No static file is modified in v0.8.0-E.",
    # checklist source boundary
    "Checklist source boundary is planning only.",
    "Checklist source boundary does not select production queue.",
    "Checklist source boundary does not read real queue DB.",
    "Checklist source boundary does not read Remote Blackboard API.",
    "Checklist source boundary does not read Google Sheets.",
    "Checklist source boundary does not switch source-of-truth.",
    "No checklist source reader is implemented in v0.8.0-E.",
    # checklist input boundary
    "Checklist input may be future mock Task Message data.",
    "Checklist input may be future mock Decision Message data.",
    "Checklist input may be future mock Result Message data.",
    "Checklist input may be future mock Advice Message data.",
    "Checklist input must not require real queue DB read in v0.8.0-E.",
    "Checklist input must not require secrets.",
    "Checklist input must not require Google Sheets.",
    "Checklist input must not require Remote Blackboard API runtime.",
    "No checklist input reader is implemented in v0.8.0-E.",
    # checklist output boundary
    "Checklist output may be future read-only checklist card.",
    "Checklist output may be future read-only checklist table.",
    "Checklist output may be future read-only Owner action reminder.",
    "Checklist output may be future read-only dispatch-disabled badge.",
    "Checklist output must not write queue data.",
    "Checklist output must not send POST.",
    "Checklist output must not dispatch Worker.",
    "Checklist output must not call OpenClaw.",
    "Checklist output must not call Hermes.",
    "Checklist output must not write Google Sheets.",
    "No checklist output renderer is implemented in v0.8.0-E.",
    # local-only Dashboard checklist boundary
    "Local-only Dashboard checklist plan does not select production host.",
    "Local-only Dashboard checklist plan does not create runtime host.",
    "Local-only Dashboard checklist plan does not deploy service.",
    "Local-only Dashboard checklist plan does not create systemd service.",
    "Local-only Dashboard checklist plan does not create daemon.",
    "Local-only Dashboard checklist plan does not create Docker deployment.",
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
    "Remote Blackboard API runtime is not implemented in v0.8.0-E.",
    "Remote Blackboard API read is not enabled in v0.8.0-E.",
    "Remote Blackboard API write is not enabled in v0.8.0-E.",
    "Remote Blackboard API is not required for Owner review checklist planning.",
    # separation
    "Worker remains OFF.",
    "OpenClaw remains Not Connected.",
    "Hermes remains Not Connected.",
    "Worker is dispatch runtime.",
    "OpenClaw is execution / gateway / tools layer.",
    "Hermes is strategy / proxy / memory layer.",
    "Worker must not run from plan-only Owner review checklist.",
    "OpenClaw must not execute from plan-only Owner review checklist.",
    "Hermes must not act from plan-only Owner review checklist.",
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
    "Future Owner review checklist changes must be auditable.",
    "Future Owner review checklist actions must include rollback notes when external actions are involved.",
    "Future Owner review checklist failures must not silently retry external actions.",
    "Future Owner review checklist failures must not bypass Owner approval.",
    "Future Owner review checklist failures must not write Google Sheets by default.",
    "Future Owner review checklist failures must not call OpenClaw by default.",
    "Future Owner review checklist failures must not start Worker by default.",
    "No Owner review checklist failure handling runtime is implemented in v0.8.0-E.",
    # candidate Owner review checklist fields
    "Candidate Owner review checklist field: checklist_id.",
    "Candidate Owner review checklist field: preview_id.",
    "Candidate Owner review checklist field: checklist_mode.",
    "Candidate Owner review checklist field: message_family.",
    "Candidate Owner review checklist field: planned_state.",
    "Candidate Owner review checklist field: owner_review_required.",
    "Candidate Owner review checklist field: owner_decision_required.",
    "Candidate Owner review checklist field: approval_is_execution.",
    "Candidate Owner review checklist field: approval_readiness_is_execution.",
    "Candidate Owner review checklist field: dispatch_enabled.",
    "Candidate Owner review checklist field: dispatch_disabled_badge.",
    "Candidate Owner review checklist field: external_side_effects.",
    "Candidate Owner review checklist field: queue_read_required.",
    "Candidate Owner review checklist field: queue_write_required.",
    "Candidate Owner review checklist field: worker_dispatch_allowed.",
    "Candidate Owner review checklist field: openclaw_call_allowed.",
    "Candidate Owner review checklist field: hermes_action_allowed.",
    "Candidate Owner review checklist field: google_sheets_write_allowed.",
    "Candidate Owner review checklist field: safety_notes.",
    "Candidate Owner review checklist field: next_owner_action.",
    "Candidate Owner review checklist fields are planning only.",
    "No candidate Owner review checklist field is implemented in v0.8.0-E.",
    "No schema migration is performed in v0.8.0-E.",
    # candidate validation rules
    "Candidate Owner review checklist validation rule: approval_is_execution must remain false.",
    "Candidate Owner review checklist validation rule: approval_readiness_is_execution must remain false.",
    "Candidate Owner review checklist validation rule: dispatch_enabled must remain false.",
    "Candidate Owner review checklist validation rule: external_side_effects must remain false.",
    "Candidate Owner review checklist validation rule: queue_read_required must remain false unless separately approved.",
    "Candidate Owner review checklist validation rule: queue_write_required must remain false.",
    "Candidate Owner review checklist validation rule: worker_dispatch_allowed must remain false.",
    "Candidate Owner review checklist validation rule: openclaw_call_allowed must remain false.",
    "Candidate Owner review checklist validation rule: hermes_action_allowed must remain false.",
    "Candidate Owner review checklist validation rule: google_sheets_write_allowed must remain false.",
    "Candidate Owner review checklist validation rules are planning only.",
    "No Owner review checklist validation runtime is implemented in v0.8.0-E.",
    # candidate future phases
    "Candidate future phase: docs-only Owner review checklist plan.",
    "Candidate future phase: candidate Owner review checklist field inventory.",
    "Candidate future phase: local mock-data read-only Owner review checklist display.",
    "Candidate future phase: read-only Owner decision visibility display.",
    "Candidate future phase: read-only dispatch-disabled checklist badge display.",
    "Candidate future phase: read-only Decision audit checklist display.",
    "Candidate future phases are planning notes only.",
    "No candidate future phase is implemented in v0.8.0-E.",
    "No candidate future phase is enabled in v0.8.0-E.",
    # disabled runtime list
    "Blackboard Loop runtime is disabled.",
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
    "v0.8.0-F — Decision Audit Dashboard Preview Display Plan",
    "v0.8.0-F must remain plan-first unless separately approved.",
    "v0.8.0-F must not implement Blackboard Loop runtime.",
    "v0.8.0-F must not implement Owner review checklist runtime.",
    "v0.8.0-F must not implement Dashboard preview display runtime.",
    "v0.8.0-F must not enable dispatch gate.",
    "v0.8.0-F must not activate Hermes.",
    "v0.8.0-F must not connect OpenClaw.",
    "v0.8.0-F must not start Worker.",
    "v0.8.0-F must not create production DB.",
    "v0.8.0-F must not create Remote Blackboard API runtime unless separately approved.",
    "v0.8.0-F must not migrate queue data.",
    "v0.8.0-F must not open shared write.",
    "v0.8.0-F must not write Google Sheets.",
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
    "Checklist input must not require real queue DB read in v0.8.0-E.",
    "Owner Review Dashboard Preview Checklist is not real queue DB read.",
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
    print(f"\nXX v0.8.0-E readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print(
        "\nv0.8.0-E Owner Review Dashboard Preview Checklist Plan readiness: ALL PASS"
    )
    sys.exit(0)
