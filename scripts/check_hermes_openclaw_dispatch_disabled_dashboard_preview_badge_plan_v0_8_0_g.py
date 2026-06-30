"""v0.8.0-G readiness check: Dispatch-disabled Dashboard Preview Badge Plan (plan-first).

Plan-first / boundary verification. Checks that the v0.8.0-G plan document exists and
contains the required sections (1-41), the current-master marker, the v0.8.0-G plan-first
markers, the relationship-to-v0.8.0-F markers, the problem-statement markers, the
Dispatch-disabled Dashboard Preview Badge definition markers, the badge display contract /
badge item / per-badge (DISPATCH OFF / WORKER OFF / OPENCLAW NOT CONNECTED / HERMES NOT
CONNECTED / GOOGLE SHEETS DISABLED) boundary markers, the runtime-off and dispatch-gate
visibility markers, the Owner review and Decision audit relationship markers, the
approval/dispatch separation markers, the Dashboard display relationship markers, the Dashboard
route / template / static boundary markers, the badge source / input / output boundary markers,
the local-only Dashboard badge display markers, the queue and data boundary markers, the Remote
Blackboard API relationship markers, the Worker / OpenClaw / Hermes separation markers, the
Google Sheets boundary markers, the secrets / privacy / memory boundary markers, the network /
webhook / connector boundary markers, the failure / rollback / audit boundary markers, the
candidate badge display fields markers, the candidate badge validation rules markers, the
candidate future phases markers, the disabled runtime list markers, the current safe posture
markers, the validation summary markers, the safety grep summary markers, and the next
recommended step — and that it asserts no unsafe "implemented / created / added / enabled /
activated / connected / called / started / written / read / modified / moved / migrated" claim
and contains no secret.

The document is allowed to contain safe negations; those that literally embed a
forbidden substring are scrubbed before the forbidden scan so they are not mis-flagged.

This script only reads the plan document. It does NOT read .env, credentials, tokens, or
secrets, makes no network call, imports no app logic (no app.main, no QueueStore), adds no
API route / router / Dashboard route / template / static / database client / migration,
creates no production / shared DB, builds no Blackboard Loop runtime, no Dashboard badge
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
    / "HERMES_OPENCLAW_DISPATCH_DISABLED_DASHBOARD_PREVIEW_BADGE_PLAN_V0_8_0_G.md"
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
ok("v0.8.0-G plan doc 存在") if DOC_PATH.exists() else xx("v0.8.0-G plan doc 存在")
if not DOC_PATH.exists():
    print("\nXX plan doc 不存在，無法繼續")
    sys.exit(1)

doc = DOC_PATH.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# [2] 必須包含的章節（1-41）
# ---------------------------------------------------------------------------
print("[2] 必須包含的章節")
REQUIRED_SECTIONS = [
    "1. Purpose",
    "2. Current master",
    "3. Scope",
    "4. Relationship to v0.8.0-F Decision Audit Dashboard Preview Display Plan",
    "5. Problem statement",
    "6. Dispatch-disabled Dashboard Preview Badge definition",
    "7. Badge display contract boundary",
    "8. Badge item boundary",
    "9. DISPATCH OFF badge boundary",
    "10. WORKER OFF badge boundary",
    "11. OPENCLAW NOT CONNECTED badge boundary",
    "12. HERMES NOT CONNECTED badge boundary",
    "13. GOOGLE SHEETS DISABLED badge boundary",
    "14. Runtime-off visibility boundary",
    "15. Dispatch gate visibility boundary",
    "16. Owner review relationship",
    "17. Decision audit relationship",
    "18. Approval and dispatch separation boundary",
    "19. Dashboard display relationship",
    "20. Dashboard route / template / static boundary",
    "21. Badge source boundary",
    "22. Badge input boundary",
    "23. Badge output boundary",
    "24. Local-only Dashboard badge display boundary",
    "25. Queue and data boundary",
    "26. Remote Blackboard API relationship",
    "27. Worker / OpenClaw / Hermes separation boundary",
    "28. Google Sheets boundary",
    "29. Secrets / privacy / memory boundary",
    "30. Network / webhook / connector boundary",
    "31. Failure / rollback / audit boundary",
    "32. Candidate badge display fields",
    "33. Candidate badge validation rules",
    "34. Candidate future phases",
    "35. Disabled runtime list",
    "36. Current safe system posture",
    "37. Validation summary",
    "38. Safety grep summary",
    "39. Non-goals",
    "40. Acceptance criteria",
    "41. Next recommended step",
]
for section in REQUIRED_SECTIONS:
    ok(f"doc 含章節「{section}」") if section in doc else xx(f"doc 含章節「{section}」")

# ---------------------------------------------------------------------------
# [3] 必須包含的 markers
# ---------------------------------------------------------------------------
print("[3] 必須包含的 markers")
REQUIRED = [
    # version
    "v0.8.0-G",
    "Dispatch-disabled Dashboard Preview Badge Plan",
    # current master
    "HEAD = origin/master = 01899264c91975dabfdbf8c75d23c3090e976229",
    "docs: plan decision audit dashboard preview display",
    # v0.8.0-G plan-first markers
    "v0.8.0-G Dispatch-disabled Dashboard Preview Badge Plan is plan-first.",
    "v0.8.0-G does not implement Blackboard Loop runtime.",
    "v0.8.0-G does not implement Dashboard preview display runtime.",
    "v0.8.0-G does not implement Decision audit display runtime.",
    "v0.8.0-G does not implement Owner review checklist runtime.",
    "v0.8.0-G does not create Dashboard route.",
    "v0.8.0-G does not create Dashboard endpoint.",
    "v0.8.0-G does not create Dashboard template.",
    "v0.8.0-G does not create Dashboard static asset.",
    "v0.8.0-G does not modify app.",
    "v0.8.0-G does not modify templates.",
    "v0.8.0-G does not modify static.",
    "v0.8.0-G does not enable dispatch gate.",
    "v0.8.0-G does not start Worker.",
    "v0.8.0-G does not connect OpenClaw.",
    "v0.8.0-G does not activate Hermes.",
    "v0.8.0-G does not connect Hermes.",
    "v0.8.0-G does not read Google Sheets.",
    "v0.8.0-G does not write Google Sheets.",
    "v0.8.0-G does not read real queue DB.",
    "v0.8.0-G does not write queue data.",
    "v0.8.0-G does not send POST.",
    "v0.8.0-G does not create webhook.",
    "v0.8.0-G does not create connector.",
    "v0.8.0-G does not read secrets.",
    "v0.8.0-G does not create .env.",
    "v0.8.0-G does not create Remote Blackboard API runtime.",
    "v0.8.0-G does not create production DB.",
    "v0.8.0-G does not create shared DB.",
    "v0.8.0-G does not open shared write.",
    # relationship to v0.8.0-F
    "v0.8.0-F Decision Audit Dashboard Preview Display Plan is complete.",
    "v0.8.0-G starts the Dispatch-disabled Dashboard Preview Badge planning step.",
    "v0.8.0-G builds on Decision Audit Dashboard Preview Display planning.",
    "v0.8.0-G plans dispatch-disabled Dashboard preview badges before any Dashboard runtime change.",
    "v0.8.0-G preserves Owner final approval authority.",
    "v0.8.0-G preserves decision and dispatch separation.",
    "v0.8.0-G preserves audit trail.",
    "v0.8.0-G preserves dispatch-disabled boundary.",
    "v0.8.0-G preserves local dry-run preview boundary.",
    "v0.8.0-G preserves read-only Dashboard display boundary.",
    "v0.8.0-G preserves Owner review checklist boundary.",
    "v0.8.0-G does not change any v0.8.0-F boundary.",
    "v0.8.0-G does not change any v0.8.0-E boundary.",
    "v0.8.0-G does not change any v0.8.0-D boundary.",
    "v0.8.0-G does not change any v0.8.0-C boundary.",
    "v0.8.0-G does not change any v0.8.0-B boundary.",
    "v0.8.0-G does not change any v0.8.0-A boundary.",
    "v0.8.0-G does not change any v0.7.5 boundary.",
    # problem statement
    "The system needs a planned dispatch-disabled Dashboard preview badge before any badge display runtime can be implemented.",
    "The dispatch-disabled badge must not become execution permission.",
    "The dispatch-disabled badge must not become Worker dispatch.",
    "The dispatch-disabled badge must not call OpenClaw.",
    "The dispatch-disabled badge must not activate Hermes.",
    "The dispatch-disabled badge must not write queue data.",
    "The dispatch-disabled badge must not read real queue DB.",
    "The dispatch-disabled badge must not send POST.",
    "The dispatch-disabled badge must not read or write Google Sheets.",
    "A preview without a visible dispatch-disabled badge could be mistaken for an execution surface.",
    "Planning the dispatch-disabled Dashboard preview badge is not implementing Dashboard runtime.",
    "Planning the dispatch-disabled Dashboard preview badge is not running the loop.",
    # definition
    "Dispatch-disabled Dashboard Preview Badge means a future read-only Dashboard indicator that visibly shows dispatch is off and the execution-bearing runtimes are not connected.",
    "Dispatch-disabled Dashboard Preview Badge is a planning artifact in v0.8.0-G.",
    "Dispatch-disabled Dashboard Preview Badge is not runtime code.",
    "Dispatch-disabled Dashboard Preview Badge is not Dashboard route implementation.",
    "Dispatch-disabled Dashboard Preview Badge is not template implementation.",
    "Dispatch-disabled Dashboard Preview Badge is not static asset implementation.",
    "Dispatch-disabled Dashboard Preview Badge is not execution permission.",
    "Dispatch-disabled Dashboard Preview Badge is not queue write.",
    "Dispatch-disabled Dashboard Preview Badge is not real queue DB read.",
    "Dispatch-disabled Dashboard Preview Badge is not Worker dispatch.",
    "Dispatch-disabled Dashboard Preview Badge is not OpenClaw call.",
    "Dispatch-disabled Dashboard Preview Badge is not Hermes activation.",
    "Dispatch-disabled Dashboard Preview Badge is not Google Sheets write.",
    "Dispatch-disabled Dashboard Preview Badge requires separate future plan and Owner approval before implementation.",
    # badge display contract
    "Badge display contract describes what a future read-only dispatch-disabled badge display may show.",
    "Badge display contract is not execution permission.",
    "Badge display contract is not runtime approval.",
    "Badge display contract is not API route.",
    "Badge display contract is not database schema.",
    "Badge display contract is not Worker dispatch.",
    "Badge display contract is not OpenClaw call.",
    "Badge display contract is not Hermes action.",
    "No badge display contract runtime is implemented in v0.8.0-G.",
    # badge item boundary
    "Badge item boundary is planning only.",
    "Badge item may describe dispatch-disabled status.",
    "Badge item may describe Worker-off status.",
    "Badge item may describe OpenClaw-not-connected status.",
    "Badge item may describe Hermes-not-connected status.",
    "Badge item may describe Google-Sheets-disabled status.",
    "Badge item must not execute action.",
    "Badge item must not mutate queue.",
    "Badge item must not start Worker.",
    "Badge item must not call OpenClaw.",
    "Badge item must not call Hermes.",
    "No badge item runtime is implemented in v0.8.0-G.",
    # badge words
    "DISPATCH OFF",
    "WORKER OFF",
    "OPENCLAW NOT CONNECTED",
    "HERMES NOT CONNECTED",
    "GOOGLE SHEETS DISABLED",
    # DISPATCH OFF badge boundary
    "DISPATCH OFF badge visibly shows the dispatch gate is disabled.",
    "DISPATCH OFF badge is display-only.",
    "DISPATCH OFF badge is not execution permission.",
    "DISPATCH OFF badge is not Worker dispatch.",
    "DISPATCH OFF badge is not OpenClaw call.",
    "DISPATCH OFF badge is not Hermes action.",
    "DISPATCH OFF badge must not enable dispatch gate.",
    "No DISPATCH OFF badge runtime is implemented in v0.8.0-G.",
    # WORKER OFF badge boundary
    "WORKER OFF badge visibly shows the Worker is not running.",
    "WORKER OFF badge is display-only.",
    "WORKER OFF badge is not execution permission.",
    "WORKER OFF badge is not Worker dispatch.",
    "WORKER OFF badge must not start Worker.",
    "No WORKER OFF badge runtime is implemented in v0.8.0-G.",
    # OPENCLAW NOT CONNECTED badge boundary
    "OPENCLAW NOT CONNECTED badge visibly shows OpenClaw is not connected.",
    "OPENCLAW NOT CONNECTED badge is display-only.",
    "OPENCLAW NOT CONNECTED badge is not execution permission.",
    "OPENCLAW NOT CONNECTED badge is not OpenClaw call.",
    "OPENCLAW NOT CONNECTED badge must not connect OpenClaw.",
    "No OPENCLAW NOT CONNECTED badge runtime is implemented in v0.8.0-G.",
    # HERMES NOT CONNECTED badge boundary
    "HERMES NOT CONNECTED badge visibly shows Hermes is not connected.",
    "HERMES NOT CONNECTED badge is display-only.",
    "HERMES NOT CONNECTED badge is not execution permission.",
    "HERMES NOT CONNECTED badge is not Hermes action.",
    "HERMES NOT CONNECTED badge must not activate Hermes.",
    "HERMES NOT CONNECTED badge must not connect Hermes.",
    "No HERMES NOT CONNECTED badge runtime is implemented in v0.8.0-G.",
    # GOOGLE SHEETS DISABLED badge boundary
    "GOOGLE SHEETS DISABLED badge visibly shows Google Sheets is disabled.",
    "GOOGLE SHEETS DISABLED badge is display-only.",
    "GOOGLE SHEETS DISABLED badge is not execution permission.",
    "GOOGLE SHEETS DISABLED badge is not Google Sheets write.",
    "GOOGLE SHEETS DISABLED badge must not enable Google Sheets.",
    "No GOOGLE SHEETS DISABLED badge runtime is implemented in v0.8.0-G.",
    # runtime-off visibility
    "Runtime-off visibility means a future display may show that execution-bearing runtimes are off.",
    "Runtime-off visibility is not execution permission.",
    "Runtime-off visibility is not Worker dispatch.",
    "Runtime-off visibility is not OpenClaw call.",
    "Runtime-off visibility is not Hermes action.",
    "Runtime-off visibility must preserve Owner final approval authority.",
    "No Runtime-off visibility runtime is implemented in v0.8.0-G.",
    # dispatch gate visibility
    "Dispatch gate visibility means a future display may show that the dispatch gate is disabled.",
    "Dispatch gate visibility is not dispatch gate enablement.",
    "Dispatch gate visibility is not execution permission.",
    "Dispatch gate visibility is not Worker dispatch.",
    "Dispatch gate visibility is not OpenClaw call.",
    "Dispatch gate visibility is not Hermes action.",
    "Dispatch gate remains disabled in v0.8.0-G.",
    "No Dispatch gate visibility runtime is implemented in v0.8.0-G.",
    # Owner review relationship
    "Owner review relationship means the future dispatch-disabled badge may support Owner review context.",
    "Owner review relationship is display-only.",
    "Owner review relationship is not Owner decision execution.",
    "Owner review relationship is not Worker dispatch.",
    "Owner review relationship is not OpenClaw call.",
    "Owner review relationship is not Hermes action.",
    "No Owner review relationship runtime is implemented in v0.8.0-G.",
    # Decision audit relationship
    "Decision audit relationship means the future dispatch-disabled badge may appear alongside Decision audit preview records.",
    "Decision audit relationship is display-only.",
    "Decision audit relationship is not decision execution.",
    "Decision audit relationship is not Worker dispatch.",
    "Decision audit relationship is not OpenClaw call.",
    "Decision audit relationship is not Hermes action.",
    "No Decision audit relationship runtime is implemented in v0.8.0-G.",
    # approval and dispatch separation
    "Approval is not execution.",
    "Approval readiness is not execution permission.",
    "Decision and dispatch remain separate.",
    "Approval display is not runtime dispatch.",
    "Approval display is not Worker dispatch.",
    "Approval display is not OpenClaw call.",
    "Approval display is not Hermes action.",
    "Approval display must preserve decision and dispatch separation.",
    "No approval dispatch runtime is implemented in v0.8.0-G.",
    # Dashboard display relationship
    "Dashboard may eventually display dispatch-disabled preview badges.",
    "Dispatch-disabled badge is display-only.",
    "Dispatch-disabled badge is not execution permission.",
    "Dispatch-disabled badge is not Worker dispatch.",
    "Dispatch-disabled badge is not OpenClaw call.",
    "Dispatch-disabled badge is not Hermes action.",
    "Dashboard badge display is read-only.",
    "No Dashboard badge display runtime is implemented in v0.8.0-G.",
    # Dashboard route / template / static boundary
    "Dashboard route boundary is planning only.",
    "No Dashboard route is created in v0.8.0-G.",
    "No Dashboard endpoint is created in v0.8.0-G.",
    "No Dashboard template is created in v0.8.0-G.",
    "No Dashboard static asset is created in v0.8.0-G.",
    "No app route is modified in v0.8.0-G.",
    "No template file is modified in v0.8.0-G.",
    "No static file is modified in v0.8.0-G.",
    # badge source boundary
    "Badge source boundary is planning only.",
    "Badge source boundary does not select production queue.",
    "Badge source boundary does not read real queue DB.",
    "Badge source boundary does not read Remote Blackboard API.",
    "Badge source boundary does not read Google Sheets.",
    "Badge source boundary does not switch source-of-truth.",
    "No badge source reader is implemented in v0.8.0-G.",
    # badge input boundary
    "Badge input may be future static safety-posture flags.",
    "Badge input may be future mock runtime-status data.",
    "Badge input must not require real queue DB read in v0.8.0-G.",
    "Badge input must not require secrets.",
    "Badge input must not require Google Sheets.",
    "Badge input must not require Remote Blackboard API runtime.",
    "No badge input reader is implemented in v0.8.0-G.",
    # badge output boundary
    "Badge output may be future read-only DISPATCH OFF badge.",
    "Badge output may be future read-only WORKER OFF badge.",
    "Badge output may be future read-only OPENCLAW NOT CONNECTED badge.",
    "Badge output may be future read-only HERMES NOT CONNECTED badge.",
    "Badge output may be future read-only GOOGLE SHEETS DISABLED badge.",
    "Badge output must not write queue data.",
    "Badge output must not send POST.",
    "Badge output must not dispatch Worker.",
    "Badge output must not call OpenClaw.",
    "Badge output must not call Hermes.",
    "Badge output must not write Google Sheets.",
    "No badge output renderer is implemented in v0.8.0-G.",
    # local-only Dashboard badge display boundary
    "Local-only Dashboard badge display plan does not select production host.",
    "Local-only Dashboard badge display plan does not create runtime host.",
    "Local-only Dashboard badge display plan does not deploy service.",
    "Local-only Dashboard badge display plan does not create systemd service.",
    "Local-only Dashboard badge display plan does not create daemon.",
    "Local-only Dashboard badge display plan does not create Docker deployment.",
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
    "Remote Blackboard API runtime is not implemented in v0.8.0-G.",
    "Remote Blackboard API read is not enabled in v0.8.0-G.",
    "Remote Blackboard API write is not enabled in v0.8.0-G.",
    "Remote Blackboard API is not required for dispatch-disabled badge planning.",
    # separation
    "Worker remains OFF.",
    "OpenClaw remains Not Connected.",
    "Hermes remains Not Connected.",
    "Worker is dispatch runtime.",
    "OpenClaw is execution / gateway / tools layer.",
    "Hermes is strategy / proxy / memory layer.",
    "Worker must not run from plan-only dispatch-disabled badge.",
    "OpenClaw must not execute from plan-only dispatch-disabled badge.",
    "Hermes must not act from plan-only dispatch-disabled badge.",
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
    "Future dispatch-disabled badge changes must be auditable.",
    "Future dispatch-disabled badge actions must include rollback notes when external actions are involved.",
    "Future dispatch-disabled badge failures must not silently retry external actions.",
    "Future dispatch-disabled badge failures must not bypass Owner approval.",
    "Future dispatch-disabled badge failures must not write Google Sheets by default.",
    "Future dispatch-disabled badge failures must not call OpenClaw by default.",
    "Future dispatch-disabled badge failures must not start Worker by default.",
    "No dispatch-disabled badge failure handling runtime is implemented in v0.8.0-G.",
    # candidate badge display fields
    "Candidate badge display field: badge_id.",
    "Candidate badge display field: preview_id.",
    "Candidate badge display field: badge_mode.",
    "Candidate badge display field: dispatch_off_badge.",
    "Candidate badge display field: worker_off_badge.",
    "Candidate badge display field: openclaw_not_connected_badge.",
    "Candidate badge display field: hermes_not_connected_badge.",
    "Candidate badge display field: google_sheets_disabled_badge.",
    "Candidate badge display field: dispatch_enabled.",
    "Candidate badge display field: worker_running.",
    "Candidate badge display field: openclaw_connected.",
    "Candidate badge display field: hermes_connected.",
    "Candidate badge display field: google_sheets_enabled.",
    "Candidate badge display field: approval_is_execution.",
    "Candidate badge display field: approval_readiness_is_execution.",
    "Candidate badge display field: external_side_effects.",
    "Candidate badge display field: safety_notes.",
    "Candidate badge display field: next_owner_action.",
    "Candidate badge display fields are planning only.",
    "No candidate badge display field is implemented in v0.8.0-G.",
    "No schema migration is performed in v0.8.0-G.",
    # candidate badge validation rules
    "Candidate badge validation rule: dispatch_enabled must remain false.",
    "Candidate badge validation rule: worker_running must remain false.",
    "Candidate badge validation rule: openclaw_connected must remain false.",
    "Candidate badge validation rule: hermes_connected must remain false.",
    "Candidate badge validation rule: google_sheets_enabled must remain false.",
    "Candidate badge validation rule: approval_is_execution must remain false.",
    "Candidate badge validation rule: approval_readiness_is_execution must remain false.",
    "Candidate badge validation rule: external_side_effects must remain false.",
    "Candidate badge validation rule: dispatch_off_badge must remain visible when dispatch is off.",
    "Candidate badge validation rule: worker_off_badge must remain visible when Worker is off.",
    "Candidate badge validation rules are planning only.",
    "No badge validation runtime is implemented in v0.8.0-G.",
    # candidate future phases
    "Candidate future phase: docs-only dispatch-disabled badge plan.",
    "Candidate future phase: candidate badge display field inventory.",
    "Candidate future phase: local mock-data read-only badge display.",
    "Candidate future phase: read-only DISPATCH OFF badge display.",
    "Candidate future phase: read-only WORKER OFF badge display.",
    "Candidate future phase: read-only OPENCLAW NOT CONNECTED badge display.",
    "Candidate future phase: read-only HERMES NOT CONNECTED badge display.",
    "Candidate future phase: read-only GOOGLE SHEETS DISABLED badge display.",
    "Candidate future phases are planning notes only.",
    "No candidate future phase is implemented in v0.8.0-G.",
    "No candidate future phase is enabled in v0.8.0-G.",
    # disabled runtime list
    "Blackboard Loop runtime is disabled.",
    "Dashboard badge display runtime is disabled.",
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
    "DISPATCH OFF.",
    "WORKER OFF.",
    "OPENCLAW NOT CONNECTED.",
    "HERMES NOT CONNECTED.",
    "GOOGLE SHEETS DISABLED.",
    "No Blackboard Loop runtime.",
    "No Dashboard badge display runtime.",
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
    "No connector.",
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
    "No tag.",
    # validation summary
    "v0.8.0-G readiness: ALL PASS.",
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
    "v0.8.1 — Local Mock Data Preview Implementation",
    "v0.8.1 must not start unless separately approved by Owner.",
    "v0.8.1 must remain mock-data / local read-only preview unless separately approved.",
    "v0.8.1 must not read real queue DB.",
    "v0.8.1 must not send POST.",
    "v0.8.1 must not start Worker.",
    "v0.8.1 must not call OpenClaw.",
    "v0.8.1 must not activate Hermes.",
    "v0.8.1 must not read or write Google Sheets.",
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
    "Badge input must not require real queue DB read in v0.8.0-G.",
    "Dispatch-disabled Dashboard Preview Badge is not real queue DB read.",
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
    "Dashboard badge display runtime created",
    "Dashboard badge display runtime implemented",
    "Dashboard badge display runtime enabled",
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
    "badge display runtime created",
    "badge display runtime implemented",
    "badge renderer runtime created",
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
    print(f"\nXX v0.8.0-G readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print(
        "\nv0.8.0-G Dispatch-disabled Dashboard Preview Badge Plan readiness: ALL PASS"
    )
    sys.exit(0)
