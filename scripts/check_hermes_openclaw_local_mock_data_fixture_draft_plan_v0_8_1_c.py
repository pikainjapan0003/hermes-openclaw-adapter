"""v0.8.1-C readiness check: Local Mock Data Fixture Draft Plan (plan-first / draft-first).

Draft verification. Checks that the v0.8.1-C plan document exists and contains the required
sections (1-46), the current-master marker, the v0.8.1-C plan-first / draft-first markers, the
relationship-to-v0.8.1-B markers, the problem-statement markers, the Local Mock Data Fixture
Draft definition markers, the fixture draft / fixture JSON / mock data file / fixture directory
boundary markers, the draft record shape boundary markers, the draft example value policy
markers, the draft record count boundary markers, the draft ordering boundary markers, the
synthetic local-only draft markers, the per-message-family draft record shape markers (Mock Task
Message / Mock Decision Message / Mock Result Message / Mock Advice Message / Mock Badge Status /
Mock Runtime-off Status), the draft required field plan markers, the draft forbidden field plan
markers, the draft boolean safety invariant plan markers, the draft validation checklist
markers, the draft approval gate markers, the preview consumer boundary markers, the read-only
draft output markers, the Dashboard display relationship markers, the Dashboard route / template
/ static boundary markers, the app / runtime boundary markers, the queue and real data boundary
markers, the Remote Blackboard API relationship markers, the Worker / OpenClaw / Hermes
separation markers, the Google Sheets boundary markers, the secrets / privacy / memory boundary
markers, the network / webhook / connector boundary markers, the failure / rollback / audit
boundary markers, the candidate future phases markers, the disabled runtime list markers, the
current safe posture markers, the validation summary markers, the safety grep summary markers,
and the next recommended step (v0.8.1-D) — and that it asserts no unsafe "implemented / created /
added / enabled / activated / connected / called / started / written / read / modified / moved /
migrated" claim and contains no real secret value.

The document is allowed to contain safe negations and forbidden-field planning tokens (bare
field names such as refresh_token / client_secret / private_key / spreadsheet_id, listed in the
Draft forbidden field plan). Safe negations that literally embed a forbidden substring are
scrubbed before the forbidden scan; the secret patterns only match value-bearing forms
(name = "value"), so bare planning tokens are not mis-flagged.

This script only reads the plan document. It does NOT read .env, credentials, tokens, or
secrets, makes no network call, imports no app logic (no app.main, no QueueStore), adds no
API route / router / Dashboard route / template / static / database client / migration,
creates no production / shared DB, creates no fixture JSON, no mock data file, no seed data
file, no fixture directory, no preview data loader, builds no fixture loader runtime, no
Dashboard preview display runtime, reads no real queue DB, writes no queue, sends no POST,
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
    / "HERMES_OPENCLAW_LOCAL_MOCK_DATA_FIXTURE_DRAFT_PLAN_V0_8_1_C.md"
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
ok("v0.8.1-C plan doc 存在") if DOC_PATH.exists() else xx("v0.8.1-C plan doc 存在")
if not DOC_PATH.exists():
    print("\nXX plan doc 不存在，無法繼續")
    sys.exit(1)

doc = DOC_PATH.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# [2] 必須包含的章節（1-46）
# ---------------------------------------------------------------------------
print("[2] 必須包含的章節")
REQUIRED_SECTIONS = [
    "1. Purpose",
    "2. Current master",
    "3. Scope",
    "4. Relationship to v0.8.1-B Local Mock Data Fixture Contract Plan",
    "5. Problem statement",
    "6. Local Mock Data Fixture Draft definition",
    "7. Fixture draft boundary",
    "8. Fixture JSON boundary",
    "9. Mock data file boundary",
    "10. Fixture directory boundary",
    "11. Draft record shape boundary",
    "12. Draft example value policy",
    "13. Draft record count boundary",
    "14. Draft ordering boundary",
    "15. Synthetic local-only draft boundary",
    "16. Mock Task Message draft record shape",
    "17. Mock Decision Message draft record shape",
    "18. Mock Result Message draft record shape",
    "19. Mock Advice Message draft record shape",
    "20. Mock Badge Status draft record shape",
    "21. Mock Runtime-off Status draft record shape",
    "22. Draft required field plan",
    "23. Draft forbidden field plan",
    "24. Draft boolean safety invariant plan",
    "25. Draft validation checklist",
    "26. Draft approval gate before fixture JSON",
    "27. Preview consumer boundary",
    "28. Read-only draft output boundary",
    "29. Dashboard display relationship",
    "30. Dashboard route / template / static boundary",
    "31. App / runtime boundary",
    "32. Queue and real data boundary",
    "33. Remote Blackboard API relationship",
    "34. Worker / OpenClaw / Hermes separation boundary",
    "35. Google Sheets boundary",
    "36. Secrets / privacy / memory boundary",
    "37. Network / webhook / connector boundary",
    "38. Failure / rollback / audit boundary",
    "39. Candidate future phases",
    "40. Disabled runtime list",
    "41. Current safe system posture",
    "42. Validation summary",
    "43. Safety grep summary",
    "44. Non-goals",
    "45. Acceptance criteria",
    "46. Next recommended step",
]
for section in REQUIRED_SECTIONS:
    ok(f"doc 含章節「{section}」") if section in doc else xx(f"doc 含章節「{section}」")

# ---------------------------------------------------------------------------
# [3] 必須包含的 markers
# ---------------------------------------------------------------------------
print("[3] 必須包含的 markers")
REQUIRED = [
    # version
    "v0.8.1-C",
    "Local Mock Data Fixture Draft Plan",
    # current master
    "HEAD = origin/master = 1f965502f25eb5886a092d1ea26b45739ebd94d0",
    "docs: plan local mock data fixture contract",
    # v0.8.1-C plan-first / draft-first markers
    "v0.8.1-C Local Mock Data Fixture Draft Plan is plan-first.",
    "v0.8.1-C Local Mock Data Fixture Draft Plan is draft-first.",
    "v0.8.1-C does not create fixture JSON.",
    "v0.8.1-C does not create mock data file.",
    "v0.8.1-C does not create seed data file.",
    "v0.8.1-C does not create fixture directory.",
    "v0.8.1-C does not create preview data loader.",
    "v0.8.1-C does not implement fixture loader runtime.",
    "v0.8.1-C does not implement Dashboard preview display runtime.",
    "v0.8.1-C does not implement local mock data preview runtime.",
    "v0.8.1-C does not create Dashboard route.",
    "v0.8.1-C does not create Dashboard endpoint.",
    "v0.8.1-C does not create Dashboard template.",
    "v0.8.1-C does not create Dashboard static asset.",
    "v0.8.1-C does not modify app.",
    "v0.8.1-C does not modify templates.",
    "v0.8.1-C does not modify static.",
    "v0.8.1-C does not read real queue DB.",
    "v0.8.1-C does not write queue data.",
    "v0.8.1-C does not send POST.",
    "v0.8.1-C does not start Worker.",
    "v0.8.1-C does not connect OpenClaw.",
    "v0.8.1-C does not activate Hermes.",
    "v0.8.1-C does not connect Hermes.",
    "v0.8.1-C does not read Google Sheets.",
    "v0.8.1-C does not write Google Sheets.",
    "v0.8.1-C does not read secrets.",
    "v0.8.1-C does not create .env.",
    "v0.8.1-C does not create webhook.",
    "v0.8.1-C does not create connector.",
    "v0.8.1-C does not create Remote Blackboard API runtime.",
    "v0.8.1-C does not create production DB.",
    "v0.8.1-C does not create shared DB.",
    "v0.8.1-C does not open shared write.",
    # relationship to v0.8.1-B
    "v0.8.1-B Local Mock Data Fixture Contract Plan is complete.",
    "v0.8.1-C starts the Local Mock Data Fixture Draft planning step.",
    "v0.8.1-C builds on Local Mock Data Fixture Contract planning.",
    "v0.8.1-C plans the fixture draft shape before any fixture JSON is created.",
    "v0.8.1-C preserves Owner final approval authority.",
    "v0.8.1-C preserves decision and dispatch separation.",
    "v0.8.1-C preserves audit trail.",
    "v0.8.1-C preserves dispatch-disabled boundary.",
    "v0.8.1-C preserves local mock data preview boundary.",
    "v0.8.1-C preserves the fixture contract boundary.",
    "v0.8.1-C preserves read-only Dashboard display boundary.",
    "v0.8.1-C does not change any v0.8.1-B boundary.",
    "v0.8.1-C does not change any v0.8.1-A boundary.",
    "v0.8.1-C does not change any v0.8.0-G boundary.",
    "v0.8.1-C does not change any v0.8.0-F boundary.",
    "v0.8.1-C does not change any v0.8.0-A boundary.",
    "v0.8.1-C does not change any v0.7.5 boundary.",
    # problem statement
    "The system needs a planned fixture draft shape before any fixture JSON can be created.",
    "Fixture draft must not become execution permission.",
    "Fixture draft must not become Worker dispatch.",
    "Fixture draft must not call OpenClaw.",
    "Fixture draft must not activate Hermes.",
    "Fixture draft must not write queue data.",
    "A draft committed straight to JSON could leak real data or be mistaken for an execution surface.",
    "Planning the fixture draft shape is not creating the fixture JSON.",
    "Planning the fixture draft shape is not running the loop.",
    # definition
    "Local Mock Data Fixture Draft means the agreed text-only draft shape a future fixture must follow.",
    "Local Mock Data Fixture Draft is a planning artifact in v0.8.1-C.",
    "Local Mock Data Fixture Draft is not runtime code.",
    "Local Mock Data Fixture Draft is not a fixture JSON file.",
    "Local Mock Data Fixture Draft is not a mock data file.",
    "Local Mock Data Fixture Draft is not a preview data loader.",
    "Local Mock Data Fixture Draft requires separate future plan and Owner approval before fixture JSON.",
    # safety principles
    "Approval is not execution.",
    "Approval readiness is not execution permission.",
    "Decision and dispatch remain separate.",
    "Fixture draft is not fixture implementation.",
    "Fixture draft is not fixture JSON.",
    "Fixture draft is not mock data file creation.",
    "Fixture draft is not execution permission.",
    "Fixture draft is not Worker dispatch.",
    "Fixture draft is not OpenClaw call.",
    "Fixture draft is not Hermes action.",
    "Fixture draft must not read real queue DB.",
    "Fixture draft must not send POST.",
    "Fixture draft must not create fixture JSON.",
    "Fixture draft must not create preview data loader.",
    "Dashboard preview display is read-only.",
    # fixture draft boundary
    "Fixture draft boundary is planning only.",
    "Fixture draft is expressed as text and pseudo-field lists only.",
    "No fixture draft runtime is implemented in v0.8.1-C.",
    # fixture JSON boundary
    "Fixture JSON boundary is planning only.",
    "No fixture JSON is created in v0.8.1-C.",
    "No .json fixture artifact is created in v0.8.1-C.",
    "Fixture JSON creation requires separate Owner approval.",
    # mock data file boundary
    "Mock data file boundary is planning only.",
    "No mock data file is created in v0.8.1-C.",
    "No seed data file is created in v0.8.1-C.",
    # fixture directory boundary
    "Fixture directory boundary is planning only.",
    "No fixture directory is created in v0.8.1-C.",
    "No fixtures/ directory is created in v0.8.1-C.",
    # draft record shape boundary
    "Draft record shape boundary is planning only.",
    "Draft record shape is expressed as a pseudo-field list.",
    "Draft record shape is not JSON.",
    "Draft record shape must mark is_mock = true.",
    "Draft record shape must declare its message_family.",
    "Draft record shape must not contain real queue data.",
    "No draft record shape runtime is implemented in v0.8.1-C.",
    # example value policy
    "Example values must be synthetic.",
    "Example values must be local-only.",
    "Example values must be non-secret.",
    "Example values must not contain real queue IDs.",
    "Example values must not contain real task IDs.",
    "Example values must not contain real user data.",
    "Example values must not contain spreadsheet IDs.",
    "Example values must not contain tokens.",
    "Example values must not contain endpoints.",
    "Example values must not contain production URLs.",
    "Example values must be clearly marked as mock.",
    "Example values must be safe to display.",
    # record count boundary
    "Candidate draft record count is planning only.",
    "Candidate draft record count may include one record per message family.",
    "Candidate draft record count must remain small and reviewable.",
    "Candidate draft record count must not be generated from real queue data.",
    "Candidate draft record count must not be generated from Google Sheets.",
    "No draft records are created in v0.8.1-C.",
    # ordering boundary
    "Draft ordering is planning only.",
    "Candidate ordering may group task, decision, result, advice, badge, runtime-off status.",
    "Candidate ordering must be deterministic.",
    "Candidate ordering must not depend on real queue timestamp.",
    "Candidate ordering must not depend on external service response.",
    "No draft ordering runtime is implemented in v0.8.1-C.",
    # synthetic local-only draft boundary
    "Mock fixture draft data is synthetic local-only sample data.",
    "Synthetic local-only draft data does not come from real queue DB.",
    "Synthetic local-only draft data does not come from Google Sheets.",
    "Synthetic local-only draft data does not come from Remote Blackboard API.",
    "Synthetic local-only draft data does not come from secrets.",
    "Synthetic local-only draft data does not switch source-of-truth.",
    "No synthetic local-only draft source reader is implemented in v0.8.1-C.",
    # message families
    "Mock Task Message",
    "Mock Decision Message",
    "Mock Result Message",
    "Mock Advice Message",
    "Mock Badge Status",
    "Mock Runtime-off Status",
    # per-family draft shapes
    "Candidate Mock Task Message draft shape",
    "Candidate Mock Decision Message draft shape",
    "Candidate Mock Result Message draft shape",
    "Candidate Mock Advice Message draft shape",
    "Candidate Mock Badge Status draft shape",
    "Candidate Mock Runtime-off Status draft shape",
    "No Mock Task Message draft record is created in v0.8.1-C.",
    "No Mock Decision Message draft record is created in v0.8.1-C.",
    "No Mock Result Message draft record is created in v0.8.1-C.",
    "No Mock Advice Message draft record is created in v0.8.1-C.",
    "No Mock Badge Status draft record is created in v0.8.1-C.",
    "No Mock Runtime-off Status draft record is created in v0.8.1-C.",
    # required field candidates (bare tokens)
    "fixture_id",
    "schema_version",
    "is_mock",
    "message_family",
    "message_id",
    "preview_id",
    "created_for",
    "display_title",
    "display_summary",
    "safety_notes",
    "next_owner_action",
    "Draft required field plan is planning only.",
    "No required field is implemented in v0.8.1-C.",
    # forbidden field candidates (bare tokens — allowed planning tokens)
    "real_queue_id",
    "real_task_id",
    "real_user_secret",
    "spreadsheet_id",
    "refresh_token",
    "client_secret",
    "private_key",
    "webhook_url",
    "openclaw_endpoint",
    "hermes_endpoint",
    "production_db_url",
    "remote_blackboard_api_url",
    "Draft forbidden field plan is planning only.",
    "No forbidden field value is included in v0.8.1-C.",
    # boolean safety invariants
    "is_mock = true",
    "dispatch_enabled = false",
    "worker_running = false",
    "openclaw_connected = false",
    "hermes_connected = false",
    "google_sheets_enabled = false",
    "external_side_effects = false",
    "approval_is_execution = false",
    "approval_readiness_is_execution = false",
    "Draft boolean safety invariant plan is planning only.",
    "No boolean safety invariant runtime is implemented in v0.8.1-C.",
    # validation checklist
    "Draft validation checklist: confirm is_mock = true on every record.",
    "Draft validation checklist: confirm schema_version is present.",
    "Draft validation checklist: confirm message_family is one of the agreed families.",
    "Draft validation checklist: confirm no forbidden field is present.",
    "Draft validation checklist: confirm draft output remains read-only.",
    "Draft validation checklist is planning only.",
    "No draft validation runtime is implemented in v0.8.1-C.",
    # approval gate
    "Fixture JSON must not be created until the draft is approved by the Owner.",
    "Fixture JSON approval gate is Owner-controlled.",
    "Fixture JSON approval gate must precede any fixture artifact.",
    "Fixture JSON approval gate must precede any preview data loader.",
    "Fixture JSON approval gate is not satisfied in v0.8.1-C.",
    # preview consumer boundary
    "A future preview consumer may read the fixture draft in read-only mode once it exists.",
    "Preview consumer is display-only.",
    "Preview consumer is not execution permission.",
    "Preview consumer must not write the fixture.",
    "Preview consumer must not read real queue DB.",
    "Preview consumer must not send POST.",
    "No preview consumer runtime is implemented in v0.8.1-C.",
    "No preview data loader is implemented in v0.8.1-C.",
    # read-only draft output boundary
    "Draft output is read-only.",
    "Draft output is display-only.",
    "Draft output is not execution permission.",
    "Draft output must not write queue data.",
    "Draft output must not send POST.",
    "Draft output must not dispatch Worker.",
    "Draft output must not call OpenClaw.",
    "Draft output must not call Hermes.",
    "Draft output must not write Google Sheets.",
    "No draft output renderer is implemented in v0.8.1-C.",
    # Dashboard display relationship
    "Dashboard may eventually display local mock data fixture draft records once approved.",
    "No Dashboard fixture draft display runtime is implemented in v0.8.1-C.",
    # Dashboard route / template / static boundary
    "Dashboard route boundary is planning only.",
    "No Dashboard route is created in v0.8.1-C.",
    "No Dashboard endpoint is created in v0.8.1-C.",
    "No Dashboard template is created in v0.8.1-C.",
    "No Dashboard static asset is created in v0.8.1-C.",
    "No app route is modified in v0.8.1-C.",
    "No template file is modified in v0.8.1-C.",
    "No static file is modified in v0.8.1-C.",
    # app / runtime boundary
    "App / runtime boundary is planning only.",
    "No app module is modified in v0.8.1-C.",
    "No app.main import is performed in v0.8.1-C.",
    "No QueueStore import is performed in v0.8.1-C.",
    "No runtime host is created in v0.8.1-C.",
    "No daemon is created in v0.8.1-C.",
    "No systemd service is created in v0.8.1-C.",
    "No Docker deployment is created in v0.8.1-C.",
    "No fixture loader runtime is created in v0.8.1-C.",
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
    "Remote Blackboard API runtime is not implemented in v0.8.1-C.",
    "Remote Blackboard API read is not enabled in v0.8.1-C.",
    "Remote Blackboard API write is not enabled in v0.8.1-C.",
    "Remote Blackboard API is not required for fixture draft planning.",
    # separation
    "Worker remains OFF.",
    "OpenClaw remains Not Connected.",
    "Hermes remains Not Connected.",
    "Worker is dispatch runtime.",
    "OpenClaw is execution / gateway / tools layer.",
    "Hermes is strategy / proxy / memory layer.",
    "Worker must not run from plan-only fixture draft.",
    "OpenClaw must not execute from plan-only fixture draft.",
    "Hermes must not act from plan-only fixture draft.",
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
    "Future fixture draft changes must be auditable.",
    "Future fixture draft actions must include rollback notes when external actions are involved.",
    "Future fixture draft failures must not silently retry external actions.",
    "Future fixture draft failures must not bypass Owner approval.",
    "Future fixture draft failures must not write Google Sheets by default.",
    "Future fixture draft failures must not call OpenClaw by default.",
    "Future fixture draft failures must not start Worker by default.",
    "No fixture draft failure handling runtime is implemented in v0.8.1-C.",
    # candidate future phases
    "Candidate future phase: docs-only local mock data fixture draft plan.",
    "Candidate future phase: local mock data fixture JSON approval plan.",
    "Candidate future phase: candidate fixture JSON inventory.",
    "Candidate future phase: read-only Mock Task Message fixture draft review.",
    "Candidate future phase: read-only Mock Decision Message fixture draft review.",
    "Candidate future phase: read-only Mock Result Message fixture draft review.",
    "Candidate future phase: read-only Mock Advice Message fixture draft review.",
    "Candidate future phase: read-only Mock Badge Status fixture draft review.",
    "Candidate future phase: read-only Mock Runtime-off Status fixture draft review.",
    "Candidate future phases are planning notes only.",
    "No candidate future phase is implemented in v0.8.1-C.",
    "No candidate future phase is enabled in v0.8.1-C.",
    # disabled runtime list
    "Fixture draft runtime is disabled.",
    "Fixture loader runtime is disabled.",
    "Preview data loader runtime is disabled.",
    "Local mock data preview runtime is disabled.",
    "Dashboard fixture draft display runtime is disabled.",
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
    "No fixture JSON.",
    "No mock data file.",
    "No seed data file.",
    "No fixture directory.",
    "No fixture loader runtime.",
    "No preview data loader.",
    "No local mock data preview runtime.",
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
    "No fixture JSON created.",
    "No mock data file created.",
    "No seed data file created.",
    "No fixture directory created.",
    "No tag.",
    # validation summary
    "v0.8.1-C readiness: ALL PASS.",
    "v0.8.1-B readiness: ALL PASS.",
    "v0.8.1-A readiness: ALL PASS.",
    "v0.8.0-G readiness: ALL PASS.",
    "v0.8.0-F readiness: ALL PASS.",
    "v0.8.0-A readiness: ALL PASS.",
    "v0.7.5-A readiness: ALL PASS.",
    "compileall scripts: PASS.",
    # safety grep summary
    "No real unsafe claim was found.",
    "No real secret was found.",
    "Forbidden field names are allowed planning tokens.",
    "Readiness forbidden-pattern matches are benign.",
    # next recommended step
    "v0.8.1-D — Local Mock Data Fixture JSON Approval Plan",
    "v0.8.1-D must not start unless separately approved by Owner.",
    "v0.8.1-D must remain fixture JSON approval planning unless separately approved.",
    "v0.8.1-D must not create fixture JSON unless separately approved.",
    "v0.8.1-D must not create preview data loader.",
    "v0.8.1-D must not modify Dashboard route/template/static.",
    "v0.8.1-D must not read real queue DB.",
    "v0.8.1-D must not send POST.",
    "v0.8.1-D must not start Worker.",
    "v0.8.1-D must not call OpenClaw.",
    "v0.8.1-D must not activate Hermes.",
    "v0.8.1-D must not read or write Google Sheets.",
]
for token in REQUIRED:
    ok(f"doc 含「{token}」") if token in doc else xx(f"doc 含「{token}」")

# ---------------------------------------------------------------------------
# [4] 禁止包含的不安全聲明 / 機密
#     先移除合法的安全否定句（其字面含 forbidden 子字串），再掃 forbidden。
#     forbidden field 名稱（bare token）為 allowed planning token，僅以 value-form
#     pattern 偵測真實機密，故不會誤判。
# ---------------------------------------------------------------------------
print("[4] 禁止包含的不安全聲明 / 機密")
SAFE_NEGATIONS = [
    "No secrets read.",
    "No secrets copied.",
    "No .env created.",
    "No dispatch gate enabled.",
    "No real queue DB read.",
    "No fixture JSON created.",
    "No mock data file created.",
    "No seed data file created.",
    "No fixture directory created.",
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
    "fixture JSON created",
    "fixture directory created",
    "mock data file created",
    "seed data file created",
    "fixture loader runtime created",
    "fixture loader runtime implemented",
    "preview data loader created",
    "preview data loader implemented",
    "local mock data preview runtime created",
    "local mock data preview runtime implemented",
    "Dashboard fixture draft display runtime created",
    "Dashboard fixture draft display runtime implemented",
    "Blackboard Loop runtime created",
    "Blackboard Loop runtime implemented",
    "Blackboard Loop runtime enabled",
    "Dashboard badge display runtime created",
    "Dashboard preview display runtime created",
    "Dashboard preview display runtime implemented",
    "Dashboard preview display runtime enabled",
    "preview renderer runtime created",
    "Dashboard route created",
    "Dashboard endpoint created",
    "Dashboard template created",
    "Dashboard static asset created",
    "app route modified",
    "template file modified",
    "static file modified",
    "loop contract runtime created",
    "state machine runtime created",
    "loop scheduler created",
    "loop scheduler enabled",
    "dispatch gate enabled",
    "autonomous execution enabled",
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

# value-bearing secret patterns only (bare forbidden-field tokens are allowed planning tokens)
FORBIDDEN_PATTERNS = [
    (r"spreadsheets/d/[A-Za-z0-9_-]{20,}", "real spreadsheet URL"),
    (r'"?refresh_token"?\s*[:=]\s*"[^"]+"', "refresh token value"),
    (r'"?client_secret"?\s*[:=]\s*"[^"]+"', "client secret value"),
    (r'"?private_key"?\s*[:=]\s*"[^"]+"', "private key value"),
    (r"-----BEGIN[ A-Z]*PRIVATE KEY-----", "private key block"),
    (r'"?spreadsheet_id"?\s*[:=]\s*"[A-Za-z0-9_-]{20,}"', "spreadsheet id value"),
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
    print(f"\nXX v0.8.1-C readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print(
        "\nv0.8.1-C Local Mock Data Fixture Draft Plan readiness: ALL PASS"
    )
    sys.exit(0)
