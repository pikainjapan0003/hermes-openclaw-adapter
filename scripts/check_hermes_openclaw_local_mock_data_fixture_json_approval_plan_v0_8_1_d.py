"""v0.8.1-D readiness check: Local Mock Data Fixture JSON Approval Plan (plan-first / approval-first).

Approval-gate verification. Checks that the v0.8.1-D plan document exists and contains the
required sections (1-44), the current-master marker, the v0.8.1-D plan-first / approval-first
markers, the relationship-to-v0.8.1-C markers, the problem-statement markers, the Local Mock Data
Fixture JSON Approval definition markers, the fixture JSON approval / creation prohibition / mock
data file / fixture directory boundary markers, the approval precondition checklist markers, the
Owner review evidence checklist markers, the rejection condition checklist markers, the synthetic
local-only approval markers, the record shape approval markers, the required fields approval
checklist markers, the forbidden fields rejection checklist markers, the boolean safety invariant
approval checklist markers, the message family approval checklist markers (Mock Task Message /
Mock Decision Message / Mock Result Message / Mock Advice Message / Mock Badge Status / Mock
Runtime-off Status), the example value / record count / ordering approval checklist markers, the
fixture JSON artifact boundary markers, the future fixture JSON creation gate markers, the
preview consumer boundary markers, the read-only approval output markers, the Dashboard display
relationship markers, the Dashboard route / template / static boundary markers, the app / runtime
boundary markers, the queue and real data boundary markers, the Remote Blackboard API
relationship markers, the Worker / OpenClaw / Hermes separation markers, the Google Sheets
boundary markers, the secrets / privacy / memory boundary markers, the network / webhook /
connector boundary markers, the failure / rollback / audit boundary markers, the candidate future
phases markers, the disabled runtime list markers, the current safe posture markers, the
validation summary markers, the safety grep summary markers, and the next recommended step
(v0.8.1-E) — and that it asserts no unsafe "implemented / created / added / enabled / activated /
connected / called / started / written / read / modified / moved / migrated" claim and contains
no real secret value.

The document is allowed to contain safe negations and forbidden-field planning tokens (bare
field names such as refresh_token / client_secret / private_key / spreadsheet_id, listed in the
Forbidden fields rejection checklist). Safe negations that literally embed a forbidden substring
are scrubbed before the forbidden scan; the secret patterns only match value-bearing forms
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
    / "HERMES_OPENCLAW_LOCAL_MOCK_DATA_FIXTURE_JSON_APPROVAL_PLAN_V0_8_1_D.md"
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
ok("v0.8.1-D plan doc 存在") if DOC_PATH.exists() else xx("v0.8.1-D plan doc 存在")
if not DOC_PATH.exists():
    print("\nXX plan doc 不存在，無法繼續")
    sys.exit(1)

doc = DOC_PATH.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# [2] 必須包含的章節（1-44）
# ---------------------------------------------------------------------------
print("[2] 必須包含的章節")
REQUIRED_SECTIONS = [
    "1. Purpose",
    "2. Current master",
    "3. Scope",
    "4. Relationship to v0.8.1-C Local Mock Data Fixture Draft Plan",
    "5. Problem statement",
    "6. Local Mock Data Fixture JSON Approval definition",
    "7. Fixture JSON approval boundary",
    "8. Fixture JSON creation prohibition boundary",
    "9. Mock data file boundary",
    "10. Fixture directory boundary",
    "11. Approval precondition checklist",
    "12. Owner review evidence checklist",
    "13. Rejection condition checklist",
    "14. Synthetic local-only approval boundary",
    "15. Record shape approval boundary",
    "16. Required fields approval checklist",
    "17. Forbidden fields rejection checklist",
    "18. Boolean safety invariant approval checklist",
    "19. Message family approval checklist",
    "20. Example value approval checklist",
    "21. Record count approval checklist",
    "22. Ordering approval checklist",
    "23. Fixture JSON artifact boundary",
    "24. Future fixture JSON creation gate",
    "25. Preview consumer boundary",
    "26. Read-only approval output boundary",
    "27. Dashboard display relationship",
    "28. Dashboard route / template / static boundary",
    "29. App / runtime boundary",
    "30. Queue and real data boundary",
    "31. Remote Blackboard API relationship",
    "32. Worker / OpenClaw / Hermes separation boundary",
    "33. Google Sheets boundary",
    "34. Secrets / privacy / memory boundary",
    "35. Network / webhook / connector boundary",
    "36. Failure / rollback / audit boundary",
    "37. Candidate future phases",
    "38. Disabled runtime list",
    "39. Current safe system posture",
    "40. Validation summary",
    "41. Safety grep summary",
    "42. Non-goals",
    "43. Acceptance criteria",
    "44. Next recommended step",
]
for section in REQUIRED_SECTIONS:
    ok(f"doc 含章節「{section}」") if section in doc else xx(f"doc 含章節「{section}」")

# ---------------------------------------------------------------------------
# [3] 必須包含的 markers
# ---------------------------------------------------------------------------
print("[3] 必須包含的 markers")
REQUIRED = [
    # version
    "v0.8.1-D",
    "Local Mock Data Fixture JSON Approval Plan",
    # current master
    "HEAD = origin/master = 3bae7838ebc0d16e1ba10ada98277aec9a5caf3c",
    "docs: plan local mock data fixture draft",
    # v0.8.1-D plan-first / approval-first markers
    "v0.8.1-D Local Mock Data Fixture JSON Approval Plan is plan-first.",
    "v0.8.1-D Local Mock Data Fixture JSON Approval Plan is approval-first.",
    "v0.8.1-D does not create fixture JSON.",
    "v0.8.1-D does not create .json artifact.",
    "v0.8.1-D does not create mock data file.",
    "v0.8.1-D does not create seed data file.",
    "v0.8.1-D does not create fixture directory.",
    "v0.8.1-D does not create preview data loader.",
    "v0.8.1-D does not implement fixture loader runtime.",
    "v0.8.1-D does not implement Dashboard preview display runtime.",
    "v0.8.1-D does not implement local mock data preview runtime.",
    "v0.8.1-D does not create Dashboard route.",
    "v0.8.1-D does not create Dashboard endpoint.",
    "v0.8.1-D does not create Dashboard template.",
    "v0.8.1-D does not create Dashboard static asset.",
    "v0.8.1-D does not modify app.",
    "v0.8.1-D does not modify templates.",
    "v0.8.1-D does not modify static.",
    "v0.8.1-D does not read real queue DB.",
    "v0.8.1-D does not write queue data.",
    "v0.8.1-D does not send POST.",
    "v0.8.1-D does not start Worker.",
    "v0.8.1-D does not connect OpenClaw.",
    "v0.8.1-D does not activate Hermes.",
    "v0.8.1-D does not connect Hermes.",
    "v0.8.1-D does not read Google Sheets.",
    "v0.8.1-D does not write Google Sheets.",
    "v0.8.1-D does not read secrets.",
    "v0.8.1-D does not create .env.",
    "v0.8.1-D does not create webhook.",
    "v0.8.1-D does not create connector.",
    "v0.8.1-D does not create Remote Blackboard API runtime.",
    "v0.8.1-D does not create production DB.",
    "v0.8.1-D does not create shared DB.",
    "v0.8.1-D does not open shared write.",
    # relationship to v0.8.1-C
    "v0.8.1-C Local Mock Data Fixture Draft Plan is complete.",
    "v0.8.1-D starts the Local Mock Data Fixture JSON Approval planning step.",
    "v0.8.1-D builds on Local Mock Data Fixture Draft planning.",
    "v0.8.1-D plans the approval gate before any fixture JSON is created.",
    "v0.8.1-D preserves Owner final approval authority.",
    "v0.8.1-D preserves decision and dispatch separation.",
    "v0.8.1-D preserves audit trail.",
    "v0.8.1-D preserves dispatch-disabled boundary.",
    "v0.8.1-D preserves local mock data preview boundary.",
    "v0.8.1-D preserves the fixture contract boundary.",
    "v0.8.1-D preserves the fixture draft boundary.",
    "v0.8.1-D preserves read-only Dashboard display boundary.",
    "v0.8.1-D does not change any v0.8.1-C boundary.",
    "v0.8.1-D does not change any v0.8.1-B boundary.",
    "v0.8.1-D does not change any v0.8.1-A boundary.",
    "v0.8.1-D does not change any v0.8.0-G boundary.",
    "v0.8.1-D does not change any v0.8.0-F boundary.",
    "v0.8.1-D does not change any v0.8.0-A boundary.",
    "v0.8.1-D does not change any v0.7.5 boundary.",
    # problem statement
    "The system needs a planned approval gate before any fixture JSON can be created.",
    "Fixture JSON approval must not become execution permission.",
    "Fixture JSON approval must not become Worker dispatch.",
    "Fixture JSON approval must not call OpenClaw.",
    "Fixture JSON approval must not activate Hermes.",
    "Fixture JSON approval must not write queue data.",
    "A fixture JSON created without an approval gate could leak real data or be mistaken for an execution surface.",
    "Planning the approval gate is not creating the fixture JSON.",
    "Planning the approval gate is not running the loop.",
    # definition
    "Local Mock Data Fixture JSON Approval means the agreed Owner gate a future fixture JSON must clear before creation.",
    "Local Mock Data Fixture JSON Approval is a planning artifact in v0.8.1-D.",
    "Local Mock Data Fixture JSON Approval is not runtime code.",
    "Local Mock Data Fixture JSON Approval is not a fixture JSON file.",
    "Local Mock Data Fixture JSON Approval is not a mock data file.",
    "Local Mock Data Fixture JSON Approval is not a preview data loader.",
    "Local Mock Data Fixture JSON Approval requires separate future plan and Owner approval before fixture JSON creation.",
    # safety principles
    "Approval is not execution.",
    "Approval readiness is not execution permission.",
    "Decision and dispatch remain separate.",
    "Fixture JSON approval is not fixture JSON creation.",
    "Fixture JSON approval is not mock data file creation.",
    "Fixture JSON approval is not execution permission.",
    "Fixture JSON approval is not Worker dispatch.",
    "Fixture JSON approval is not OpenClaw call.",
    "Fixture JSON approval is not Hermes action.",
    "Fixture JSON approval must not read real queue DB.",
    "Fixture JSON approval must not send POST.",
    "Fixture JSON approval must not create fixture JSON.",
    "Fixture JSON approval must not create preview data loader.",
    "Dashboard preview display is read-only.",
    # fixture JSON approval boundary
    "Fixture JSON approval boundary is planning only.",
    "Fixture JSON approval is an Owner-controlled gate.",
    "Fixture JSON approval is recorded as Owner review evidence.",
    "Fixture JSON approval does not itself create any artifact.",
    "No fixture JSON approval runtime is implemented in v0.8.1-D.",
    # fixture JSON creation prohibition boundary
    "Fixture JSON creation prohibition boundary is planning only.",
    "No fixture JSON is created in v0.8.1-D.",
    "No .json artifact is created in v0.8.1-D.",
    "Fixture JSON creation requires separate Owner approval.",
    # mock data file boundary
    "Mock data file boundary is planning only.",
    "No mock data file is created in v0.8.1-D.",
    "No seed data file is created in v0.8.1-D.",
    # fixture directory boundary
    "Fixture directory boundary is planning only.",
    "No fixture directory is created in v0.8.1-D.",
    "No fixtures/ directory is created in v0.8.1-D.",
    # approval precondition checklist
    "Approval precondition: Owner has reviewed the fixture draft plan.",
    "Approval precondition: fixture JSON creation is separately requested.",
    "Approval precondition: every record remains synthetic local-only.",
    "Approval precondition: every record remains is_mock = true.",
    "Approval precondition: every message_family is one of the agreed mock families.",
    "Approval precondition: every required field is present.",
    "Approval precondition: no forbidden field is present.",
    "Approval precondition: all boolean safety invariants remain safe.",
    "Approval precondition: record count remains small and reviewable.",
    "Approval precondition: ordering remains deterministic.",
    "Approval precondition: no real queue DB read is required.",
    "Approval precondition: no POST is required.",
    "Approval precondition: no Worker/OpenClaw/Hermes action is required.",
    "Approval precondition: no Google Sheets access is required.",
    # Owner review evidence checklist
    "Owner review evidence: current HEAD and origin/master are recorded.",
    "Owner review evidence: fixture JSON creation scope is recorded.",
    "Owner review evidence: synthetic local-only policy is recorded.",
    "Owner review evidence: required fields are recorded.",
    "Owner review evidence: forbidden fields are recorded.",
    "Owner review evidence: boolean safety invariants are recorded.",
    "Owner review evidence: message families are recorded.",
    "Owner review evidence: no real queue DB boundary is recorded.",
    "Owner review evidence: no POST boundary is recorded.",
    "Owner review evidence: no Worker/OpenClaw/Hermes boundary is recorded.",
    "Owner review evidence: no Google Sheets boundary is recorded.",
    "Owner review evidence: no secrets boundary is recorded.",
    "Owner review evidence: rollback/audit notes are recorded.",
    # rejection condition checklist
    "Rejection condition: any real queue ID appears.",
    "Rejection condition: any real task ID appears.",
    "Rejection condition: any real user data appears.",
    "Rejection condition: any spreadsheet ID appears.",
    "Rejection condition: any token appears.",
    "Rejection condition: any secret value appears.",
    "Rejection condition: any private key appears.",
    "Rejection condition: any webhook URL appears.",
    "Rejection condition: any real endpoint appears.",
    "Rejection condition: any production URL appears.",
    "Rejection condition: is_mock is not true.",
    "Rejection condition: dispatch_enabled is not false.",
    "Rejection condition: worker_running is not false.",
    "Rejection condition: openclaw_connected is not false.",
    "Rejection condition: hermes_connected is not false.",
    "Rejection condition: google_sheets_enabled is not false.",
    "Rejection condition: external_side_effects is not false.",
    "Rejection condition: approval_is_execution is not false.",
    "Rejection condition: approval_readiness_is_execution is not false.",
    # synthetic local-only approval boundary
    "Approved fixture data must be synthetic local-only sample data.",
    "Synthetic local-only data does not come from real queue DB.",
    "Synthetic local-only data does not come from Google Sheets.",
    "Synthetic local-only data does not come from Remote Blackboard API.",
    "Synthetic local-only data does not come from secrets.",
    "Synthetic local-only data does not switch source-of-truth.",
    "No synthetic local-only approval source reader is implemented in v0.8.1-D.",
    # record shape approval boundary
    "Record shape approval boundary is planning only.",
    "Approved record shape is the agreed pseudo-field shape from the fixture draft plan.",
    "Approved record shape must mark is_mock = true.",
    "Approved record shape must declare its message_family.",
    "Approved record shape must not contain real queue data.",
    "No record shape approval runtime is implemented in v0.8.1-D.",
    # required fields approval checklist
    "Required field candidate: fixture_id.",
    "Required field candidate: schema_version.",
    "Required field candidate: is_mock.",
    "Required field candidate: message_family.",
    "Required field candidate: message_id.",
    "Required field candidate: preview_id.",
    "Required field candidate: created_for.",
    "Required field candidate: display_title.",
    "Required field candidate: display_summary.",
    "Required field candidate: safety_notes.",
    "Required field candidate: next_owner_action.",
    "Required fields approval checklist is planning only.",
    "No required field is implemented in v0.8.1-D.",
    # required field bare tokens
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
    # forbidden fields rejection checklist (bare tokens — allowed planning tokens)
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
    "Forbidden fields rejection checklist is planning only.",
    "No forbidden field value is included in v0.8.1-D.",
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
    "Boolean safety invariant approval checklist is planning only.",
    "No boolean safety invariant runtime is implemented in v0.8.1-D.",
    # message family approval checklist
    "Message family approval checklist enumerates the approvable mock families.",
    "Mock Task Message",
    "Mock Decision Message",
    "Mock Result Message",
    "Mock Advice Message",
    "Mock Badge Status",
    "Mock Runtime-off Status",
    "Message family approval checklist is planning only.",
    "No message family runtime is implemented in v0.8.1-D.",
    # example value approval checklist
    "Example value approval: values must be synthetic.",
    "Example value approval: values must be local-only.",
    "Example value approval: values must be non-secret.",
    "Example value approval: values must be clearly marked as mock.",
    "Example value approval: values must be safe to display.",
    "Example value approval checklist is planning only.",
    "No example value approval runtime is implemented in v0.8.1-D.",
    # record count approval checklist
    "Record count approval: count remains small and reviewable.",
    "Record count approval: count may include one record per message family.",
    "Record count approval: count must not be generated from real queue data.",
    "Record count approval: count must not be generated from Google Sheets.",
    "Record count approval checklist is planning only.",
    "No record count approval runtime is implemented in v0.8.1-D.",
    # ordering approval checklist
    "Ordering approval: ordering must be deterministic.",
    "Ordering approval: ordering may group task, decision, result, advice, badge, runtime-off status.",
    "Ordering approval: ordering must not depend on real queue timestamp.",
    "Ordering approval: ordering must not depend on external service response.",
    "Ordering approval checklist is planning only.",
    "No ordering approval runtime is implemented in v0.8.1-D.",
    # fixture JSON artifact boundary
    "Fixture JSON artifact boundary is planning only.",
    "No fixture JSON artifact is created in v0.8.1-D.",
    "No .json artifact is written in v0.8.1-D.",
    "Fixture JSON artifact creation requires separate Owner approval.",
    "Fixture JSON artifact must remain synthetic local-only when eventually created.",
    # future fixture JSON creation gate
    "Fixture JSON must not be created until the approval gate is satisfied.",
    "Fixture JSON creation gate is Owner-controlled.",
    "Fixture JSON creation gate must precede any fixture artifact.",
    "Fixture JSON creation gate must precede any preview data loader.",
    "Fixture JSON creation gate is not satisfied in v0.8.1-D.",
    # preview consumer boundary
    "A future preview consumer may read the approved fixture in read-only mode once it exists.",
    "Preview consumer is display-only.",
    "Preview consumer is not execution permission.",
    "Preview consumer must not write the fixture.",
    "Preview consumer must not read real queue DB.",
    "Preview consumer must not send POST.",
    "No preview consumer runtime is implemented in v0.8.1-D.",
    "No preview data loader is implemented in v0.8.1-D.",
    # read-only approval output boundary
    "Approval output is read-only.",
    "Approval output is display-only.",
    "Approval output is not execution permission.",
    "Approval output must not write queue data.",
    "Approval output must not send POST.",
    "Approval output must not dispatch Worker.",
    "Approval output must not call OpenClaw.",
    "Approval output must not call Hermes.",
    "Approval output must not write Google Sheets.",
    "No approval output renderer is implemented in v0.8.1-D.",
    # Dashboard display relationship
    "Dashboard may eventually display approved local mock data fixture records once created.",
    "No Dashboard fixture approval display runtime is implemented in v0.8.1-D.",
    # Dashboard route / template / static boundary
    "Dashboard route boundary is planning only.",
    "No Dashboard route is created in v0.8.1-D.",
    "No Dashboard endpoint is created in v0.8.1-D.",
    "No Dashboard template is created in v0.8.1-D.",
    "No Dashboard static asset is created in v0.8.1-D.",
    "No app route is modified in v0.8.1-D.",
    "No template file is modified in v0.8.1-D.",
    "No static file is modified in v0.8.1-D.",
    # app / runtime boundary
    "App / runtime boundary is planning only.",
    "No app module is modified in v0.8.1-D.",
    "No app.main import is performed in v0.8.1-D.",
    "No QueueStore import is performed in v0.8.1-D.",
    "No runtime host is created in v0.8.1-D.",
    "No daemon is created in v0.8.1-D.",
    "No systemd service is created in v0.8.1-D.",
    "No Docker deployment is created in v0.8.1-D.",
    "No fixture loader runtime is created in v0.8.1-D.",
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
    "Remote Blackboard API runtime is not implemented in v0.8.1-D.",
    "Remote Blackboard API read is not enabled in v0.8.1-D.",
    "Remote Blackboard API write is not enabled in v0.8.1-D.",
    "Remote Blackboard API is not required for fixture JSON approval planning.",
    # separation
    "Worker remains OFF.",
    "OpenClaw remains Not Connected.",
    "Hermes remains Not Connected.",
    "Worker is dispatch runtime.",
    "OpenClaw is execution / gateway / tools layer.",
    "Hermes is strategy / proxy / memory layer.",
    "Worker must not run from plan-only fixture JSON approval.",
    "OpenClaw must not execute from plan-only fixture JSON approval.",
    "Hermes must not act from plan-only fixture JSON approval.",
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
    "Future fixture JSON approval changes must be auditable.",
    "Future fixture JSON actions must include rollback notes when external actions are involved.",
    "Future fixture JSON failures must not silently retry external actions.",
    "Future fixture JSON failures must not bypass Owner approval.",
    "Future fixture JSON failures must not write Google Sheets by default.",
    "Future fixture JSON failures must not call OpenClaw by default.",
    "Future fixture JSON failures must not start Worker by default.",
    "No fixture JSON approval failure handling runtime is implemented in v0.8.1-D.",
    # candidate future phases
    "Candidate future phase: docs-only local mock data fixture JSON approval plan.",
    "Candidate future phase: local mock data fixture JSON creation plan.",
    "Candidate future phase: candidate fixture JSON creation inventory.",
    "Candidate future phase: read-only Mock Task Message fixture JSON review.",
    "Candidate future phase: read-only Mock Decision Message fixture JSON review.",
    "Candidate future phase: read-only Mock Result Message fixture JSON review.",
    "Candidate future phase: read-only Mock Advice Message fixture JSON review.",
    "Candidate future phase: read-only Mock Badge Status fixture JSON review.",
    "Candidate future phase: read-only Mock Runtime-off Status fixture JSON review.",
    "Candidate future phases are planning notes only.",
    "No candidate future phase is implemented in v0.8.1-D.",
    "No candidate future phase is enabled in v0.8.1-D.",
    # disabled runtime list
    "Fixture JSON approval runtime is disabled.",
    "Fixture loader runtime is disabled.",
    "Preview data loader runtime is disabled.",
    "Local mock data preview runtime is disabled.",
    "Dashboard fixture approval display runtime is disabled.",
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
    "No .json artifact.",
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
    "v0.8.1-D readiness: ALL PASS.",
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
    "v0.8.1-E — Local Mock Data Fixture JSON Creation Plan",
    "v0.8.1-E must not start unless separately approved by Owner.",
    "v0.8.1-E must remain fixture JSON creation planning unless separately approved.",
    "v0.8.1-E must not create fixture JSON unless separately approved.",
    "v0.8.1-E must not create preview data loader.",
    "v0.8.1-E must not modify Dashboard route/template/static.",
    "v0.8.1-E must not read real queue DB.",
    "v0.8.1-E must not send POST.",
    "v0.8.1-E must not start Worker.",
    "v0.8.1-E must not call OpenClaw.",
    "v0.8.1-E must not activate Hermes.",
    "v0.8.1-E must not read or write Google Sheets.",
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
    "Approval precondition: no real queue DB read is required.",
    "A fixture JSON created without an approval gate could leak real data or be mistaken for an execution surface.",
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
    "Dashboard fixture approval display runtime created",
    "Dashboard fixture approval display runtime implemented",
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
    print(f"\nXX v0.8.1-D readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print(
        "\nv0.8.1-D Local Mock Data Fixture JSON Approval Plan readiness: ALL PASS"
    )
    sys.exit(0)
