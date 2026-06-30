"""v0.8.1-B readiness check: Local Mock Data Fixture Contract Plan (plan-first / contract-first).

Plan-first / contract verification. Checks that the v0.8.1-B plan document exists and contains
the required sections (1-40), the current-master marker, the v0.8.1-B plan-first markers, the
relationship-to-v0.8.1-A markers, the problem-statement markers, the Local Mock Data Fixture
Contract definition markers, the fixture file / schema / synthetic-local-only boundary markers,
the per-message-family fixture contract markers (Mock Task Message / Mock Decision Message /
Mock Result Message / Mock Advice Message / Mock Badge Status / Mock Runtime-off Status), the
required field contract markers, the forbidden field contract markers, the boolean safety
invariant contract markers, the message family contract markers, the preview consumer boundary
markers, the read-only fixture output markers, the Dashboard display relationship markers, the
Dashboard route / template / static boundary markers, the app / runtime boundary markers, the
queue and real data boundary markers, the Remote Blackboard API relationship markers, the Worker
/ OpenClaw / Hermes separation markers, the Google Sheets boundary markers, the secrets /
privacy / memory boundary markers, the network / webhook / connector boundary markers, the
failure / rollback / audit boundary markers, the candidate fixture validation rules markers, the
candidate future phases markers, the disabled runtime list markers, the current safe posture
markers, the validation summary markers, the safety grep summary markers, and the next
recommended step (v0.8.1-C) — and that it asserts no unsafe "implemented / created / added /
enabled / activated / connected / called / started / written / read / modified / moved /
migrated" claim and contains no real secret value.

The document is allowed to contain safe negations and forbidden-field planning tokens (bare
field names such as refresh_token / client_secret / private_key / spreadsheet_id, listed in the
Forbidden field contract). Safe negations that literally embed a forbidden substring are
scrubbed before the forbidden scan; the secret patterns only match value-bearing forms
(name = "value"), so bare planning tokens are not mis-flagged.

This script only reads the plan document. It does NOT read .env, credentials, tokens, or
secrets, makes no network call, imports no app logic (no app.main, no QueueStore), adds no
API route / router / Dashboard route / template / static / database client / migration,
creates no production / shared DB, creates no fixture JSON, no mock data file, no fixture
directory, no preview data loader, builds no fixture loader runtime, no Dashboard preview
display runtime, reads no real queue DB, writes no queue, sends no POST, starts no Worker,
connects no OpenClaw, activates no Hermes, opens no shared write, and reads/writes no Google
Sheets.
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
    / "HERMES_OPENCLAW_LOCAL_MOCK_DATA_FIXTURE_CONTRACT_PLAN_V0_8_1_B.md"
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
ok("v0.8.1-B plan doc 存在") if DOC_PATH.exists() else xx("v0.8.1-B plan doc 存在")
if not DOC_PATH.exists():
    print("\nXX plan doc 不存在，無法繼續")
    sys.exit(1)

doc = DOC_PATH.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# [2] 必須包含的章節（1-40）
# ---------------------------------------------------------------------------
print("[2] 必須包含的章節")
REQUIRED_SECTIONS = [
    "1. Purpose",
    "2. Current master",
    "3. Scope",
    "4. Relationship to v0.8.1-A Local Mock Data Preview Implementation Boundary Plan",
    "5. Problem statement",
    "6. Local Mock Data Fixture Contract definition",
    "7. Fixture file boundary",
    "8. Fixture schema boundary",
    "9. Synthetic local-only data boundary",
    "10. Mock Task Message fixture contract",
    "11. Mock Decision Message fixture contract",
    "12. Mock Result Message fixture contract",
    "13. Mock Advice Message fixture contract",
    "14. Mock Badge Status fixture contract",
    "15. Mock Runtime-off Status fixture contract",
    "16. Required field contract",
    "17. Forbidden field contract",
    "18. Boolean safety invariant contract",
    "19. Message family contract",
    "20. Preview consumer boundary",
    "21. Read-only fixture output boundary",
    "22. Dashboard display relationship",
    "23. Dashboard route / template / static boundary",
    "24. App / runtime boundary",
    "25. Queue and real data boundary",
    "26. Remote Blackboard API relationship",
    "27. Worker / OpenClaw / Hermes separation boundary",
    "28. Google Sheets boundary",
    "29. Secrets / privacy / memory boundary",
    "30. Network / webhook / connector boundary",
    "31. Failure / rollback / audit boundary",
    "32. Candidate fixture validation rules",
    "33. Candidate future phases",
    "34. Disabled runtime list",
    "35. Current safe system posture",
    "36. Validation summary",
    "37. Safety grep summary",
    "38. Non-goals",
    "39. Acceptance criteria",
    "40. Next recommended step",
]
for section in REQUIRED_SECTIONS:
    ok(f"doc 含章節「{section}」") if section in doc else xx(f"doc 含章節「{section}」")

# ---------------------------------------------------------------------------
# [3] 必須包含的 markers
# ---------------------------------------------------------------------------
print("[3] 必須包含的 markers")
REQUIRED = [
    # version
    "v0.8.1-B",
    "Local Mock Data Fixture Contract Plan",
    # current master
    "HEAD = origin/master = 1492cad3bd473a6cfe3e37ba238e6f223d338e8d",
    "docs: plan local mock data preview boundary",
    # v0.8.1-B plan-first markers
    "v0.8.1-B Local Mock Data Fixture Contract Plan is plan-first.",
    "v0.8.1-B does not create fixture JSON.",
    "v0.8.1-B does not create mock data file.",
    "v0.8.1-B does not create seed data file.",
    "v0.8.1-B does not create fixture directory.",
    "v0.8.1-B does not create preview data loader.",
    "v0.8.1-B does not implement fixture loader runtime.",
    "v0.8.1-B does not implement Dashboard preview display runtime.",
    "v0.8.1-B does not implement local mock data preview runtime.",
    "v0.8.1-B does not create Dashboard route.",
    "v0.8.1-B does not create Dashboard endpoint.",
    "v0.8.1-B does not create Dashboard template.",
    "v0.8.1-B does not create Dashboard static asset.",
    "v0.8.1-B does not modify app.",
    "v0.8.1-B does not modify templates.",
    "v0.8.1-B does not modify static.",
    "v0.8.1-B does not read real queue DB.",
    "v0.8.1-B does not write queue data.",
    "v0.8.1-B does not send POST.",
    "v0.8.1-B does not start Worker.",
    "v0.8.1-B does not connect OpenClaw.",
    "v0.8.1-B does not activate Hermes.",
    "v0.8.1-B does not connect Hermes.",
    "v0.8.1-B does not read Google Sheets.",
    "v0.8.1-B does not write Google Sheets.",
    "v0.8.1-B does not read secrets.",
    "v0.8.1-B does not create .env.",
    "v0.8.1-B does not create webhook.",
    "v0.8.1-B does not create connector.",
    "v0.8.1-B does not create Remote Blackboard API runtime.",
    "v0.8.1-B does not create production DB.",
    "v0.8.1-B does not create shared DB.",
    "v0.8.1-B does not open shared write.",
    # relationship to v0.8.1-A
    "v0.8.1-A Local Mock Data Preview Implementation Boundary Plan is complete.",
    "v0.8.1-B starts the Local Mock Data Fixture Contract planning step.",
    "v0.8.1-B builds on Local Mock Data Preview Implementation Boundary planning.",
    "v0.8.1-B plans the fixture data contract before any fixture file is created.",
    "v0.8.1-B preserves Owner final approval authority.",
    "v0.8.1-B preserves decision and dispatch separation.",
    "v0.8.1-B preserves audit trail.",
    "v0.8.1-B preserves dispatch-disabled boundary.",
    "v0.8.1-B preserves local mock data preview boundary.",
    "v0.8.1-B preserves read-only Dashboard display boundary.",
    "v0.8.1-B does not change any v0.8.1-A boundary.",
    "v0.8.1-B does not change any v0.8.0-G boundary.",
    "v0.8.1-B does not change any v0.8.0-F boundary.",
    "v0.8.1-B does not change any v0.8.0-A boundary.",
    "v0.8.1-B does not change any v0.7.5 boundary.",
    # problem statement
    "The system needs a planned mock data fixture contract before any fixture file can be drafted.",
    "Fixture contract must not become execution permission.",
    "Fixture contract must not become Worker dispatch.",
    "Fixture contract must not call OpenClaw.",
    "Fixture contract must not activate Hermes.",
    "Fixture contract must not write queue data.",
    "A fixture without an agreed contract could leak real data or be mistaken for an execution surface.",
    "Planning the fixture contract is not creating the fixture.",
    "Planning the fixture contract is not running the loop.",
    # definition
    "Local Mock Data Fixture Contract means the agreed data contract a future synthetic local-only mock data fixture must satisfy.",
    "Local Mock Data Fixture Contract is a planning artifact in v0.8.1-B.",
    "Local Mock Data Fixture Contract is not runtime code.",
    "Local Mock Data Fixture Contract is not a fixture JSON file.",
    "Local Mock Data Fixture Contract is not a mock data file.",
    "Local Mock Data Fixture Contract is not a preview data loader.",
    "Local Mock Data Fixture Contract requires separate future plan and Owner approval before fixture implementation.",
    # safety principles
    "Approval is not execution.",
    "Approval readiness is not execution permission.",
    "Decision and dispatch remain separate.",
    "Fixture contract is not fixture implementation.",
    "Fixture contract is not execution permission.",
    "Fixture contract is not Worker dispatch.",
    "Fixture contract is not OpenClaw call.",
    "Fixture contract is not Hermes action.",
    "Fixture contract must not read real queue DB.",
    "Fixture contract must not send POST.",
    "Fixture contract must not create fixture JSON.",
    "Fixture contract must not create preview data loader.",
    "Dashboard preview display is read-only.",
    # fixture file boundary
    "Fixture file boundary is planning only.",
    "A future fixture file must be synthetic local-only sample data.",
    "A future fixture file must not contain real queue data.",
    "A future fixture file must not contain secrets.",
    "No fixture file is created in v0.8.1-B.",
    "No fixture JSON is created in v0.8.1-B.",
    "No fixture directory is created in v0.8.1-B.",
    # fixture schema boundary
    "Fixture schema boundary is planning only.",
    "A future fixture schema must carry a schema_version.",
    "A future fixture schema must mark every record is_mock = true.",
    "A future fixture schema must declare its message_family.",
    "No fixture schema is implemented in v0.8.1-B.",
    "No schema migration is performed in v0.8.1-B.",
    # synthetic local-only data boundary
    "Mock fixture data is synthetic local-only sample data.",
    "Synthetic local-only data does not come from real queue DB.",
    "Synthetic local-only data does not come from Google Sheets.",
    "Synthetic local-only data does not come from Remote Blackboard API.",
    "Synthetic local-only data does not come from secrets.",
    "Synthetic local-only data does not switch source-of-truth.",
    "No synthetic local-only data source reader is implemented in v0.8.1-B.",
    # message families
    "Mock Task Message",
    "Mock Decision Message",
    "Mock Result Message",
    "Mock Advice Message",
    "Mock Badge Status",
    "Mock Runtime-off Status",
    # Mock Task Message fixture contract
    "Mock Task Message fixture record is synthetic local-only sample data.",
    "Mock Task Message fixture record must set is_mock = true.",
    "Mock Task Message fixture record is display-only.",
    "Mock Task Message fixture record is not execution permission.",
    "Mock Task Message fixture record is not Worker dispatch.",
    "Mock Task Message fixture record must not contain real queue data.",
    "No Mock Task Message fixture is created in v0.8.1-B.",
    # Mock Decision Message fixture contract
    "Mock Decision Message fixture record is synthetic local-only sample data.",
    "Mock Decision Message fixture record must set is_mock = true.",
    "Mock Decision Message fixture record is display-only.",
    "Mock Decision Message fixture record is not decision execution.",
    "Mock Decision Message fixture record must not contain real queue data.",
    "No Mock Decision Message fixture is created in v0.8.1-B.",
    # Mock Result Message fixture contract
    "Mock Result Message fixture record is synthetic local-only sample data.",
    "Mock Result Message fixture record must set is_mock = true.",
    "Mock Result Message fixture record is display-only.",
    "Mock Result Message fixture record must not contain real queue data.",
    "No Mock Result Message fixture is created in v0.8.1-B.",
    # Mock Advice Message fixture contract
    "Mock Advice Message fixture record is synthetic local-only sample data.",
    "Mock Advice Message fixture record must set is_mock = true.",
    "Mock Advice Message fixture record is display-only.",
    "Mock Advice Message fixture record is not Hermes action.",
    "Mock Advice Message fixture record must not contain real queue data.",
    "No Mock Advice Message fixture is created in v0.8.1-B.",
    # Mock Badge Status fixture contract
    "Mock Badge Status fixture record is synthetic local-only sample data.",
    "Mock Badge Status fixture record must set is_mock = true.",
    "Mock Badge Status fixture record is display-only.",
    "Mock Badge Status fixture record must not enable dispatch gate.",
    "Mock Badge Status fixture record must not contain real queue data.",
    "No Mock Badge Status fixture is created in v0.8.1-B.",
    # Mock Runtime-off Status fixture contract
    "Mock Runtime-off Status fixture record is synthetic local-only sample data.",
    "Mock Runtime-off Status fixture record must set is_mock = true.",
    "Mock Runtime-off Status fixture record may show DISPATCH OFF.",
    "Mock Runtime-off Status fixture record may show WORKER OFF.",
    "Mock Runtime-off Status fixture record may show OPENCLAW NOT CONNECTED.",
    "Mock Runtime-off Status fixture record may show HERMES NOT CONNECTED.",
    "Mock Runtime-off Status fixture record may show GOOGLE SHEETS DISABLED.",
    "Mock Runtime-off Status fixture record is display-only.",
    "Mock Runtime-off Status fixture record must not start Worker.",
    "Mock Runtime-off Status fixture record must not connect OpenClaw.",
    "Mock Runtime-off Status fixture record must not activate Hermes.",
    "No Mock Runtime-off Status fixture is created in v0.8.1-B.",
    # badge words
    "DISPATCH OFF",
    "WORKER OFF",
    "OPENCLAW NOT CONNECTED",
    "HERMES NOT CONNECTED",
    "GOOGLE SHEETS DISABLED",
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
    "Required field contract is planning only.",
    "No required field is implemented in v0.8.1-B.",
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
    "Forbidden field contract is planning only.",
    "No forbidden field value is included in v0.8.1-B.",
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
    "Boolean safety invariant contract is planning only.",
    "No boolean safety invariant runtime is implemented in v0.8.1-B.",
    # message family contract
    "Message family contract enumerates the mock fixture families.",
    "Message family contract is planning only.",
    "No message family runtime is implemented in v0.8.1-B.",
    # preview consumer boundary
    "A future preview consumer may read the fixture in read-only mode.",
    "Preview consumer is display-only.",
    "Preview consumer is not execution permission.",
    "Preview consumer must not write the fixture.",
    "Preview consumer must not read real queue DB.",
    "Preview consumer must not send POST.",
    "No preview consumer runtime is implemented in v0.8.1-B.",
    "No preview data loader is implemented in v0.8.1-B.",
    # read-only fixture output boundary
    "Fixture output is read-only.",
    "Fixture output is display-only.",
    "Fixture output is not execution permission.",
    "Fixture output must not write queue data.",
    "Fixture output must not send POST.",
    "Fixture output must not dispatch Worker.",
    "Fixture output must not call OpenClaw.",
    "Fixture output must not call Hermes.",
    "Fixture output must not write Google Sheets.",
    "No fixture output renderer is implemented in v0.8.1-B.",
    # Dashboard display relationship
    "Dashboard may eventually display local mock data fixture records.",
    "No Dashboard fixture display runtime is implemented in v0.8.1-B.",
    # Dashboard route / template / static boundary
    "Dashboard route boundary is planning only.",
    "No Dashboard route is created in v0.8.1-B.",
    "No Dashboard endpoint is created in v0.8.1-B.",
    "No Dashboard template is created in v0.8.1-B.",
    "No Dashboard static asset is created in v0.8.1-B.",
    "No app route is modified in v0.8.1-B.",
    "No template file is modified in v0.8.1-B.",
    "No static file is modified in v0.8.1-B.",
    # app / runtime boundary
    "App / runtime boundary is planning only.",
    "No app module is modified in v0.8.1-B.",
    "No app.main import is performed in v0.8.1-B.",
    "No QueueStore import is performed in v0.8.1-B.",
    "No runtime host is created in v0.8.1-B.",
    "No daemon is created in v0.8.1-B.",
    "No systemd service is created in v0.8.1-B.",
    "No Docker deployment is created in v0.8.1-B.",
    "No fixture loader runtime is created in v0.8.1-B.",
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
    "Remote Blackboard API runtime is not implemented in v0.8.1-B.",
    "Remote Blackboard API read is not enabled in v0.8.1-B.",
    "Remote Blackboard API write is not enabled in v0.8.1-B.",
    "Remote Blackboard API is not required for fixture contract planning.",
    # separation
    "Worker remains OFF.",
    "OpenClaw remains Not Connected.",
    "Hermes remains Not Connected.",
    "Worker is dispatch runtime.",
    "OpenClaw is execution / gateway / tools layer.",
    "Hermes is strategy / proxy / memory layer.",
    "Worker must not run from plan-only fixture contract.",
    "OpenClaw must not execute from plan-only fixture contract.",
    "Hermes must not act from plan-only fixture contract.",
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
    "Future fixture contract changes must be auditable.",
    "Future fixture actions must include rollback notes when external actions are involved.",
    "Future fixture failures must not silently retry external actions.",
    "Future fixture failures must not bypass Owner approval.",
    "Future fixture failures must not write Google Sheets by default.",
    "Future fixture failures must not call OpenClaw by default.",
    "Future fixture failures must not start Worker by default.",
    "No fixture failure handling runtime is implemented in v0.8.1-B.",
    # candidate fixture validation rules
    "Candidate fixture validation rule: is_mock must remain true.",
    "Candidate fixture validation rule: schema_version must be present.",
    "Candidate fixture validation rule: message_family must be one of the agreed families.",
    "Candidate fixture validation rule: dispatch_enabled must remain false.",
    "Candidate fixture validation rule: worker_running must remain false.",
    "Candidate fixture validation rule: openclaw_connected must remain false.",
    "Candidate fixture validation rule: hermes_connected must remain false.",
    "Candidate fixture validation rule: google_sheets_enabled must remain false.",
    "Candidate fixture validation rule: approval_is_execution must remain false.",
    "Candidate fixture validation rule: approval_readiness_is_execution must remain false.",
    "Candidate fixture validation rule: external_side_effects must remain false.",
    "Candidate fixture validation rule: no forbidden field may be present.",
    "Candidate fixture validation rule: fixture output must remain read-only.",
    "Candidate fixture validation rules are planning only.",
    "No fixture validation runtime is implemented in v0.8.1-B.",
    # candidate future phases
    "Candidate future phase: docs-only local mock data fixture contract plan.",
    "Candidate future phase: local mock data fixture draft plan.",
    "Candidate future phase: candidate fixture record inventory.",
    "Candidate future phase: read-only Mock Task Message fixture draft.",
    "Candidate future phase: read-only Mock Decision Message fixture draft.",
    "Candidate future phase: read-only Mock Result Message fixture draft.",
    "Candidate future phase: read-only Mock Advice Message fixture draft.",
    "Candidate future phase: read-only Mock Badge Status fixture draft.",
    "Candidate future phase: read-only Mock Runtime-off Status fixture draft.",
    "Candidate future phases are planning notes only.",
    "No candidate future phase is implemented in v0.8.1-B.",
    "No candidate future phase is enabled in v0.8.1-B.",
    # disabled runtime list
    "Fixture loader runtime is disabled.",
    "Preview data loader runtime is disabled.",
    "Local mock data preview runtime is disabled.",
    "Dashboard fixture display runtime is disabled.",
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
    "No tag.",
    # validation summary
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
    "v0.8.1-C — Local Mock Data Fixture Draft Plan",
    "v0.8.1-C must not start unless separately approved by Owner.",
    "v0.8.1-C must remain fixture draft planning unless separately approved.",
    "v0.8.1-C must not create fixture JSON unless separately approved.",
    "v0.8.1-C must not create preview data loader.",
    "v0.8.1-C must not modify Dashboard route/template/static.",
    "v0.8.1-C must not read real queue DB.",
    "v0.8.1-C must not send POST.",
    "v0.8.1-C must not start Worker.",
    "v0.8.1-C must not call OpenClaw.",
    "v0.8.1-C must not activate Hermes.",
    "v0.8.1-C must not read or write Google Sheets.",
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
    "A future fixture schema must not require real queue DB read.",
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
    "Dashboard fixture display runtime created",
    "Dashboard fixture display runtime implemented",
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
    print(f"\nXX v0.8.1-B readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print(
        "\nv0.8.1-B Local Mock Data Fixture Contract Plan readiness: ALL PASS"
    )
    sys.exit(0)
