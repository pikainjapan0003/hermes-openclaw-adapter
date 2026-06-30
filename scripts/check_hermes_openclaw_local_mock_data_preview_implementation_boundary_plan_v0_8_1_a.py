"""v0.8.1-A readiness check: Local Mock Data Preview Implementation Boundary Plan (plan-first).

Plan-first / boundary verification. Checks that the v0.8.1-A plan document exists and
contains the required sections (1-36), the current-master marker, the v0.8.1-A plan-first
markers, the relationship-to-v0.8.0-G markers, the problem-statement markers, the Local Mock
Data Preview Implementation Boundary definition markers, the mock data source boundary markers,
the per-message-family preview boundary markers (Mock Task Message / Mock Decision Message /
Mock Result Message / Mock Advice Message / Mock Badge Status / Mock Runtime-off Status), the
mock runtime-off Badge preview boundary markers (DISPATCH OFF / WORKER OFF / OPENCLAW NOT
CONNECTED / HERMES NOT CONNECTED / GOOGLE SHEETS DISABLED), the preview input / output boundary
markers, the read-only preview markers, the Dashboard display relationship markers, the
Dashboard route / template / static boundary markers, the app / runtime boundary markers, the
queue and real data boundary markers, the Remote Blackboard API relationship markers, the Worker
/ OpenClaw / Hermes separation markers, the Google Sheets boundary markers, the secrets /
privacy / memory boundary markers, the network / webhook / connector boundary markers, the
failure / rollback / audit boundary markers, the candidate mock data families markers, the
candidate mock data fields markers, the candidate preview validation rules markers, the
candidate future phases markers, the disabled runtime list markers, the current safe posture
markers, the validation summary markers, the safety grep summary markers, and the next
recommended step (v0.8.1-B) — and that it asserts no unsafe "implemented / created / added /
enabled / activated / connected / called / started / written / read / modified / moved /
migrated" claim and contains no secret.

The document is allowed to contain safe negations; those that literally embed a
forbidden substring are scrubbed before the forbidden scan so they are not mis-flagged.

This script only reads the plan document. It does NOT read .env, credentials, tokens, or
secrets, makes no network call, imports no app logic (no app.main, no QueueStore), adds no
API route / router / Dashboard route / template / static / database client / migration,
creates no production / shared DB, builds no local mock data preview runtime, no mock data
fixture file, no preview data loader, no Dashboard preview display runtime, reads no real queue
DB, writes no queue, sends no POST, starts no Worker, connects no OpenClaw, activates no Hermes,
opens no shared write, and reads/writes no Google Sheets.
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
    / "HERMES_OPENCLAW_LOCAL_MOCK_DATA_PREVIEW_IMPLEMENTATION_BOUNDARY_PLAN_V0_8_1_A.md"
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
ok("v0.8.1-A plan doc 存在") if DOC_PATH.exists() else xx("v0.8.1-A plan doc 存在")
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
    "4. Relationship to v0.8.0-G Dispatch-disabled Dashboard Preview Badge Plan",
    "5. Problem statement",
    "6. Local Mock Data Preview Implementation Boundary definition",
    "7. Mock data source boundary",
    "8. Mock Task Message preview boundary",
    "9. Mock Decision Message preview boundary",
    "10. Mock Result Message preview boundary",
    "11. Mock Advice Message preview boundary",
    "12. Mock runtime-off Badge preview boundary",
    "13. Preview input boundary",
    "14. Preview output boundary",
    "15. Read-only preview boundary",
    "16. Dashboard display relationship",
    "17. Dashboard route / template / static boundary",
    "18. App / runtime boundary",
    "19. Queue and real data boundary",
    "20. Remote Blackboard API relationship",
    "21. Worker / OpenClaw / Hermes separation boundary",
    "22. Google Sheets boundary",
    "23. Secrets / privacy / memory boundary",
    "24. Network / webhook / connector boundary",
    "25. Failure / rollback / audit boundary",
    "26. Candidate mock data families",
    "27. Candidate mock data fields",
    "28. Candidate preview validation rules",
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
    "v0.8.1-A",
    "Local Mock Data Preview Implementation Boundary Plan",
    # current master
    "HEAD = origin/master = c6dda5017f660a8737955f40d65d9e2acde4be1d",
    "docs: plan dispatch disabled dashboard preview badge",
    # v0.8.1-A plan-first markers
    "v0.8.1-A Local Mock Data Preview Implementation Boundary Plan is plan-first.",
    "v0.8.1-A does not implement Dashboard preview display runtime.",
    "v0.8.1-A does not implement local mock data preview runtime.",
    "v0.8.1-A does not create mock data fixture file.",
    "v0.8.1-A does not create preview data loader.",
    "v0.8.1-A does not create Dashboard route.",
    "v0.8.1-A does not create Dashboard endpoint.",
    "v0.8.1-A does not create Dashboard template.",
    "v0.8.1-A does not create Dashboard static asset.",
    "v0.8.1-A does not modify app.",
    "v0.8.1-A does not modify templates.",
    "v0.8.1-A does not modify static.",
    "v0.8.1-A does not read real queue DB.",
    "v0.8.1-A does not write queue data.",
    "v0.8.1-A does not send POST.",
    "v0.8.1-A does not start Worker.",
    "v0.8.1-A does not connect OpenClaw.",
    "v0.8.1-A does not activate Hermes.",
    "v0.8.1-A does not connect Hermes.",
    "v0.8.1-A does not read Google Sheets.",
    "v0.8.1-A does not write Google Sheets.",
    "v0.8.1-A does not read secrets.",
    "v0.8.1-A does not create .env.",
    "v0.8.1-A does not create webhook.",
    "v0.8.1-A does not create connector.",
    "v0.8.1-A does not create Remote Blackboard API runtime.",
    "v0.8.1-A does not create production DB.",
    "v0.8.1-A does not create shared DB.",
    "v0.8.1-A does not open shared write.",
    # relationship to v0.8.0-G
    "v0.8.0-G Dispatch-disabled Dashboard Preview Badge Plan is complete.",
    "v0.8.1-A starts the Local Mock Data Preview Implementation Boundary planning step.",
    "v0.8.1-A builds on Dispatch-disabled Dashboard Preview Badge planning.",
    "v0.8.1-A plans local mock data preview boundaries before any Dashboard runtime change.",
    "v0.8.1-A preserves Owner final approval authority.",
    "v0.8.1-A preserves decision and dispatch separation.",
    "v0.8.1-A preserves audit trail.",
    "v0.8.1-A preserves dispatch-disabled boundary.",
    "v0.8.1-A preserves local dry-run preview boundary.",
    "v0.8.1-A preserves read-only Dashboard display boundary.",
    "v0.8.1-A preserves Owner review checklist boundary.",
    "v0.8.1-A preserves dispatch-disabled Dashboard preview badge boundary.",
    "v0.8.1-A does not change any v0.8.0-G boundary.",
    "v0.8.1-A does not change any v0.8.0-F boundary.",
    "v0.8.1-A does not change any v0.8.0-A boundary.",
    "v0.8.1-A does not change any v0.7.5 boundary.",
    # problem statement
    "The system needs a planned local mock data preview boundary before any mock data preview runtime can be implemented.",
    "Mock data preview must not become execution permission.",
    "Mock data preview must not become Worker dispatch.",
    "Mock data preview must not call OpenClaw.",
    "Mock data preview must not activate Hermes.",
    "Mock data preview must not write queue data.",
    "Mock data preview must not read real queue DB.",
    "Mock data preview must not send POST.",
    "Mock data preview must not read or write Google Sheets.",
    "A preview built on real data or live runtime could be mistaken for an execution surface.",
    "Planning the local mock data preview boundary is not implementing Dashboard runtime.",
    "Planning the local mock data preview boundary is not running the loop.",
    # definition
    "Local Mock Data Preview Implementation Boundary means the agreed limits for a future read-only Dashboard preview that renders synthetic local-only mock message data.",
    "Local Mock Data Preview Implementation Boundary is a planning artifact in v0.8.1-A.",
    "Local Mock Data Preview Implementation Boundary is not runtime code.",
    "Local Mock Data Preview Implementation Boundary is not Dashboard route implementation.",
    "Local Mock Data Preview Implementation Boundary is not a mock data fixture file.",
    "Local Mock Data Preview Implementation Boundary is not a preview data loader.",
    "Local Mock Data Preview Implementation Boundary is not execution permission.",
    "Local Mock Data Preview Implementation Boundary is not queue write.",
    "Local Mock Data Preview Implementation Boundary is not real queue DB read.",
    "Local Mock Data Preview Implementation Boundary is not Worker dispatch.",
    "Local Mock Data Preview Implementation Boundary is not OpenClaw call.",
    "Local Mock Data Preview Implementation Boundary is not Hermes activation.",
    "Local Mock Data Preview Implementation Boundary is not Google Sheets write.",
    "Local Mock Data Preview Implementation Boundary requires separate future plan and Owner approval before implementation.",
    # mock data source boundary
    "Mock data source boundary is planning only.",
    "Mock data source is synthetic local-only sample data.",
    "Mock data source does not select production queue.",
    "Mock data source does not read real queue DB.",
    "Mock data source does not read Remote Blackboard API.",
    "Mock data source does not read Google Sheets.",
    "Mock data source does not read secrets.",
    "Mock data source does not switch source-of-truth.",
    "No mock data source reader is implemented in v0.8.1-A.",
    "No mock data fixture file is created in v0.8.1-A.",
    # message families
    "Mock Task Message",
    "Mock Decision Message",
    "Mock Result Message",
    "Mock Advice Message",
    "Mock Badge Status",
    "Mock Runtime-off Status",
    # Mock Task Message preview boundary
    "Mock Task Message is synthetic local-only sample data.",
    "Mock Task Message preview is display-only.",
    "Mock Task Message preview is not execution permission.",
    "Mock Task Message preview is not Worker dispatch.",
    "Mock Task Message preview is not OpenClaw call.",
    "Mock Task Message preview is not Hermes action.",
    "Mock Task Message preview must not write queue data.",
    "Mock Task Message preview must not read real queue DB.",
    "No Mock Task Message preview runtime is implemented in v0.8.1-A.",
    # Mock Decision Message preview boundary
    "Mock Decision Message is synthetic local-only sample data.",
    "Mock Decision Message preview is display-only.",
    "Mock Decision Message preview is not execution permission.",
    "Mock Decision Message preview is not decision execution.",
    "Mock Decision Message preview is not Worker dispatch.",
    "Mock Decision Message preview is not OpenClaw call.",
    "Mock Decision Message preview is not Hermes action.",
    "Mock Decision Message preview must not write queue data.",
    "Mock Decision Message preview must not read real queue DB.",
    "No Mock Decision Message preview runtime is implemented in v0.8.1-A.",
    # Mock Result Message preview boundary
    "Mock Result Message is synthetic local-only sample data.",
    "Mock Result Message preview is display-only.",
    "Mock Result Message preview is not execution permission.",
    "Mock Result Message preview is not Worker dispatch.",
    "Mock Result Message preview is not OpenClaw call.",
    "Mock Result Message preview is not Hermes action.",
    "Mock Result Message preview must not write queue data.",
    "Mock Result Message preview must not read real queue DB.",
    "No Mock Result Message preview runtime is implemented in v0.8.1-A.",
    # Mock Advice Message preview boundary
    "Mock Advice Message is synthetic local-only sample data.",
    "Mock Advice Message preview is display-only.",
    "Mock Advice Message preview is not execution permission.",
    "Mock Advice Message preview is not Worker dispatch.",
    "Mock Advice Message preview is not OpenClaw call.",
    "Mock Advice Message preview is not Hermes action.",
    "Mock Advice Message preview must not write queue data.",
    "Mock Advice Message preview must not read real queue DB.",
    "No Mock Advice Message preview runtime is implemented in v0.8.1-A.",
    # Mock runtime-off Badge preview boundary
    "Mock Badge Status is synthetic local-only sample data.",
    "Mock Runtime-off Status is synthetic local-only sample data.",
    "Mock runtime-off Badge preview may show DISPATCH OFF.",
    "Mock runtime-off Badge preview may show WORKER OFF.",
    "Mock runtime-off Badge preview may show OPENCLAW NOT CONNECTED.",
    "Mock runtime-off Badge preview may show HERMES NOT CONNECTED.",
    "Mock runtime-off Badge preview may show GOOGLE SHEETS DISABLED.",
    "Mock runtime-off Badge preview is display-only.",
    "Mock runtime-off Badge preview is not execution permission.",
    "Mock runtime-off Badge preview must not enable dispatch gate.",
    "Mock runtime-off Badge preview must not start Worker.",
    "Mock runtime-off Badge preview must not connect OpenClaw.",
    "Mock runtime-off Badge preview must not activate Hermes.",
    "Mock runtime-off Badge preview must not enable Google Sheets.",
    "No Mock runtime-off Badge preview runtime is implemented in v0.8.1-A.",
    # badge words
    "DISPATCH OFF",
    "WORKER OFF",
    "OPENCLAW NOT CONNECTED",
    "HERMES NOT CONNECTED",
    "GOOGLE SHEETS DISABLED",
    # preview input boundary
    "Preview input may be future synthetic local-only mock message data.",
    "Preview input may be future static safety-posture flags.",
    "Preview input must not require real queue DB read in v0.8.1-A.",
    "Preview input must not require secrets.",
    "Preview input must not require Google Sheets.",
    "Preview input must not require Remote Blackboard API runtime.",
    "No preview input reader is implemented in v0.8.1-A.",
    "No preview data loader is implemented in v0.8.1-A.",
    # preview output boundary
    "Preview output may be future read-only Mock Task Message preview.",
    "Preview output may be future read-only Mock Decision Message preview.",
    "Preview output may be future read-only Mock Result Message preview.",
    "Preview output may be future read-only Mock Advice Message preview.",
    "Preview output may be future read-only Mock Badge Status preview.",
    "Preview output may be future read-only Mock Runtime-off Status preview.",
    "Preview output must not write queue data.",
    "Preview output must not send POST.",
    "Preview output must not dispatch Worker.",
    "Preview output must not call OpenClaw.",
    "Preview output must not call Hermes.",
    "Preview output must not write Google Sheets.",
    "No preview output renderer is implemented in v0.8.1-A.",
    # read-only preview boundary / safety principles
    "Approval is not execution.",
    "Approval readiness is not execution permission.",
    "Decision and dispatch remain separate.",
    "Mock data preview is display-only.",
    "Mock data preview is not execution permission.",
    "Mock data preview is not Worker dispatch.",
    "Mock data preview is not OpenClaw call.",
    "Mock data preview is not Hermes action.",
    "Dashboard preview display is read-only.",
    "No read-only preview runtime is implemented in v0.8.1-A.",
    # Dashboard display relationship
    "Dashboard may eventually display local mock data preview.",
    "No Dashboard mock data preview runtime is implemented in v0.8.1-A.",
    # Dashboard route / template / static boundary
    "Dashboard route boundary is planning only.",
    "No Dashboard route is created in v0.8.1-A.",
    "No Dashboard endpoint is created in v0.8.1-A.",
    "No Dashboard template is created in v0.8.1-A.",
    "No Dashboard static asset is created in v0.8.1-A.",
    "No app route is modified in v0.8.1-A.",
    "No template file is modified in v0.8.1-A.",
    "No static file is modified in v0.8.1-A.",
    # app / runtime boundary
    "App / runtime boundary is planning only.",
    "No app module is modified in v0.8.1-A.",
    "No app.main import is performed in v0.8.1-A.",
    "No QueueStore import is performed in v0.8.1-A.",
    "No runtime host is created in v0.8.1-A.",
    "No daemon is created in v0.8.1-A.",
    "No systemd service is created in v0.8.1-A.",
    "No Docker deployment is created in v0.8.1-A.",
    "No local mock data preview runtime is created in v0.8.1-A.",
    # queue and real data boundary
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
    "Remote Blackboard API runtime is not implemented in v0.8.1-A.",
    "Remote Blackboard API read is not enabled in v0.8.1-A.",
    "Remote Blackboard API write is not enabled in v0.8.1-A.",
    "Remote Blackboard API is not required for local mock data preview planning.",
    # separation
    "Worker remains OFF.",
    "OpenClaw remains Not Connected.",
    "Hermes remains Not Connected.",
    "Worker is dispatch runtime.",
    "OpenClaw is execution / gateway / tools layer.",
    "Hermes is strategy / proxy / memory layer.",
    "Worker must not run from plan-only mock data preview boundary.",
    "OpenClaw must not execute from plan-only mock data preview boundary.",
    "Hermes must not act from plan-only mock data preview boundary.",
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
    "Future mock data preview changes must be auditable.",
    "Future mock data preview actions must include rollback notes when external actions are involved.",
    "Future mock data preview failures must not silently retry external actions.",
    "Future mock data preview failures must not bypass Owner approval.",
    "Future mock data preview failures must not write Google Sheets by default.",
    "Future mock data preview failures must not call OpenClaw by default.",
    "Future mock data preview failures must not start Worker by default.",
    "No mock data preview failure handling runtime is implemented in v0.8.1-A.",
    # candidate mock data families
    "Candidate mock data families are planning only.",
    "No mock data family is implemented in v0.8.1-A.",
    # candidate mock data fields
    "Candidate mock data field: message_id.",
    "Candidate mock data field: preview_id.",
    "Candidate mock data field: family.",
    "Candidate mock data field: mock_mode.",
    "Candidate mock data field: task_summary.",
    "Candidate mock data field: decision_outcome.",
    "Candidate mock data field: result_summary.",
    "Candidate mock data field: advice_text.",
    "Candidate mock data field: badge_status.",
    "Candidate mock data field: runtime_off_status.",
    "Candidate mock data field: dispatch_enabled.",
    "Candidate mock data field: worker_running.",
    "Candidate mock data field: openclaw_connected.",
    "Candidate mock data field: hermes_connected.",
    "Candidate mock data field: google_sheets_enabled.",
    "Candidate mock data field: approval_is_execution.",
    "Candidate mock data field: approval_readiness_is_execution.",
    "Candidate mock data field: external_side_effects.",
    "Candidate mock data field: is_mock.",
    "Candidate mock data field: safety_notes.",
    "Candidate mock data field: next_owner_action.",
    "Candidate mock data fields are planning only.",
    "No candidate mock data field is implemented in v0.8.1-A.",
    "No schema migration is performed in v0.8.1-A.",
    # candidate preview validation rules
    "Candidate preview validation rule: is_mock must remain true.",
    "Candidate preview validation rule: dispatch_enabled must remain false.",
    "Candidate preview validation rule: worker_running must remain false.",
    "Candidate preview validation rule: openclaw_connected must remain false.",
    "Candidate preview validation rule: hermes_connected must remain false.",
    "Candidate preview validation rule: google_sheets_enabled must remain false.",
    "Candidate preview validation rule: approval_is_execution must remain false.",
    "Candidate preview validation rule: approval_readiness_is_execution must remain false.",
    "Candidate preview validation rule: external_side_effects must remain false.",
    "Candidate preview validation rule: mock data source must remain synthetic local-only.",
    "Candidate preview validation rule: preview output must remain read-only.",
    "Candidate preview validation rules are planning only.",
    "No preview validation runtime is implemented in v0.8.1-A.",
    # candidate future phases
    "Candidate future phase: docs-only local mock data preview boundary plan.",
    "Candidate future phase: local mock data fixture contract plan.",
    "Candidate future phase: candidate mock data field inventory.",
    "Candidate future phase: read-only Mock Task Message preview.",
    "Candidate future phase: read-only Mock Decision Message preview.",
    "Candidate future phase: read-only Mock Result Message preview.",
    "Candidate future phase: read-only Mock Advice Message preview.",
    "Candidate future phase: read-only Mock Badge Status preview.",
    "Candidate future phase: read-only Mock Runtime-off Status preview.",
    "Candidate future phases are planning notes only.",
    "No candidate future phase is implemented in v0.8.1-A.",
    "No candidate future phase is enabled in v0.8.1-A.",
    # disabled runtime list
    "Local mock data preview runtime is disabled.",
    "Mock data fixture loader is disabled.",
    "Preview data loader runtime is disabled.",
    "Dashboard mock data preview runtime is disabled.",
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
    "No local mock data preview runtime.",
    "No mock data fixture file.",
    "No preview data loader.",
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
    "v0.8.1-A readiness: ALL PASS.",
    "v0.8.0-G readiness: ALL PASS.",
    "v0.8.0-F readiness: ALL PASS.",
    "v0.8.0-A readiness: ALL PASS.",
    "v0.7.5-A readiness: ALL PASS.",
    "compileall scripts: PASS.",
    # safety grep summary
    "No real unsafe claim was found.",
    "No real secret was found.",
    "Readiness forbidden-pattern matches are benign.",
    # next recommended step
    "v0.8.1-B — Local Mock Data Fixture Contract Plan",
    "v0.8.1-B must not start unless separately approved by Owner.",
    "v0.8.1-B must remain mock-data contract planning unless separately approved.",
    "v0.8.1-B must not modify Dashboard route/template/static.",
    "v0.8.1-B must not create runtime preview loader unless separately approved.",
    "v0.8.1-B must not read real queue DB.",
    "v0.8.1-B must not send POST.",
    "v0.8.1-B must not start Worker.",
    "v0.8.1-B must not call OpenClaw.",
    "v0.8.1-B must not activate Hermes.",
    "v0.8.1-B must not read or write Google Sheets.",
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
    "Preview input must not require real queue DB read in v0.8.1-A.",
    "Local Mock Data Preview Implementation Boundary is not real queue DB read.",
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
    "local mock data preview runtime created",
    "local mock data preview runtime implemented",
    "local mock data preview runtime enabled",
    "mock data fixture file created",
    "mock data fixture loader created",
    "preview data loader created",
    "preview data loader implemented",
    "JSON fixture created",
    "seed script created",
    "Blackboard Loop runtime created",
    "Blackboard Loop runtime implemented",
    "Blackboard Loop runtime enabled",
    "Dashboard badge display runtime created",
    "Dashboard badge display runtime implemented",
    "Dashboard badge display runtime enabled",
    "Decision audit display runtime created",
    "Decision audit display runtime implemented",
    "Owner review checklist runtime created",
    "Owner review checklist runtime implemented",
    "Dashboard preview display runtime created",
    "Dashboard preview display runtime implemented",
    "Dashboard preview display runtime enabled",
    "Dashboard mock data preview runtime created",
    "Dashboard mock data preview runtime implemented",
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
    print(f"\nXX v0.8.1-A readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print(
        "\nv0.8.1-A Local Mock Data Preview Implementation Boundary Plan readiness: ALL PASS"
    )
    sys.exit(0)
