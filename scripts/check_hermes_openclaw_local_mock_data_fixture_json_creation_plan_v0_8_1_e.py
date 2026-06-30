"""v0.8.1-E readiness check: Local Mock Data Fixture JSON Creation Plan (plan-first / creation-plan-only).

Creation-plan verification. Checks that the v0.8.1-E plan document exists and contains the
required sections (1-49), the current-master marker, the v0.8.1-E plan-first / creation-plan-only
markers, the relationship-to-v0.8.1-D markers, the problem-statement markers, the Local Mock Data
Fixture JSON Creation Plan definition markers, the creation planning / artifact prohibition
boundary markers, the candidate artifact path / filename / schema version / top-level shape
markers, the candidate record family / count / ordering plan markers, the synthetic local-only
value policy markers, the example value policy markers, the required fields creation checklist
markers, the forbidden fields rejection checklist markers, the boolean safety invariant checklist
markers, the per-message-family candidate record plan markers (Mock Task Message / Mock Decision
Message / Mock Result Message / Mock Advice Message / Mock Badge Status / Mock Runtime-off
Status), the creation checklist markers, the validation checklist markers, the Owner approval gate
markers, the future implementation / loader / Dashboard preview boundary markers, the Dashboard
route / template / static boundary markers, the app / runtime boundary markers, the queue and
real data boundary markers, the Remote Blackboard API relationship markers, the Worker / OpenClaw
/ Hermes separation markers, the Google Sheets boundary markers, the secrets / privacy / memory
boundary markers, the network / webhook / connector boundary markers, the failure / rollback /
audit boundary markers, the candidate future phases markers, the disabled runtime list markers,
the current safe posture markers, the validation summary markers, the safety grep summary
markers, and the next recommended step (v0.8.1-F) — and that it asserts no unsafe "implemented /
created / added / enabled / activated / connected / called / started / written / read / modified /
moved / migrated" claim and contains no real secret value.

The document is allowed to contain safe negations and forbidden-field planning tokens (bare
field names such as refresh_token / client_secret / private_key / spreadsheet_id, listed in the
Forbidden fields rejection checklist). Safe negations that literally embed a forbidden substring
are scrubbed before the forbidden scan; the secret patterns only match value-bearing forms
(name = "value"), so bare planning tokens are not mis-flagged.

This script only reads the plan document. It does NOT read .env, credentials, tokens, or
secrets, makes no network call, imports no app logic (no app.main, no QueueStore), adds no
API route / router / Dashboard route / template / static / database client / migration,
creates no production / shared DB, creates no fixture JSON, no .json artifact, no mock data
file, no seed data file, no fixture directory, no preview data loader, builds no fixture loader
runtime, no Dashboard preview display runtime, reads no real queue DB, writes no queue, sends no
POST, starts no Worker, connects no OpenClaw, activates no Hermes, opens no shared write, and
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
    / "HERMES_OPENCLAW_LOCAL_MOCK_DATA_FIXTURE_JSON_CREATION_PLAN_V0_8_1_E.md"
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
ok("v0.8.1-E plan doc 存在") if DOC_PATH.exists() else xx("v0.8.1-E plan doc 存在")
if not DOC_PATH.exists():
    print("\nXX plan doc 不存在，無法繼續")
    sys.exit(1)

doc = DOC_PATH.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# [2] 必須包含的章節（1-49）
# ---------------------------------------------------------------------------
print("[2] 必須包含的章節")
REQUIRED_SECTIONS = [
    "1. Purpose",
    "2. Current master",
    "3. Scope",
    "4. Relationship to v0.8.1-D Local Mock Data Fixture JSON Approval Plan",
    "5. Problem statement",
    "6. Local Mock Data Fixture JSON Creation Plan definition",
    "7. Fixture JSON creation planning boundary",
    "8. Fixture JSON artifact prohibition boundary",
    "9. Fixture JSON candidate artifact path",
    "10. Fixture JSON candidate filename",
    "11. Fixture JSON candidate schema version",
    "12. Fixture JSON candidate top-level shape",
    "13. Fixture JSON candidate record family plan",
    "14. Fixture JSON candidate record count plan",
    "15. Fixture JSON candidate ordering plan",
    "16. Synthetic local-only value policy",
    "17. Example value policy",
    "18. Required fields creation checklist",
    "19. Forbidden fields rejection checklist",
    "20. Boolean safety invariant checklist",
    "21. Mock Task Message candidate record plan",
    "22. Mock Decision Message candidate record plan",
    "23. Mock Result Message candidate record plan",
    "24. Mock Advice Message candidate record plan",
    "25. Mock Badge Status candidate record plan",
    "26. Mock Runtime-off Status candidate record plan",
    "27. Fixture JSON creation checklist",
    "28. Fixture JSON validation checklist",
    "29. Owner approval gate before artifact creation",
    "30. Future fixture JSON implementation boundary",
    "31. Future read-only loader boundary",
    "32. Future Dashboard preview boundary",
    "33. Dashboard route / template / static boundary",
    "34. App / runtime boundary",
    "35. Queue and real data boundary",
    "36. Remote Blackboard API relationship",
    "37. Worker / OpenClaw / Hermes separation boundary",
    "38. Google Sheets boundary",
    "39. Secrets / privacy / memory boundary",
    "40. Network / webhook / connector boundary",
    "41. Failure / rollback / audit boundary",
    "42. Candidate future phases",
    "43. Disabled runtime list",
    "44. Current safe system posture",
    "45. Validation summary",
    "46. Safety grep summary",
    "47. Non-goals",
    "48. Acceptance criteria",
    "49. Next recommended step",
]
for section in REQUIRED_SECTIONS:
    ok(f"doc 含章節「{section}」") if section in doc else xx(f"doc 含章節「{section}」")

# ---------------------------------------------------------------------------
# [3] 必須包含的 markers
# ---------------------------------------------------------------------------
print("[3] 必須包含的 markers")
REQUIRED = [
    # version
    "v0.8.1-E",
    "Local Mock Data Fixture JSON Creation Plan",
    # current master
    "HEAD = origin/master = 26b24b2a1004b4d548ba9a6cfdff03680eb2e015",
    "docs: plan local mock data fixture json approval",
    # v0.8.1-E plan-first / creation-plan-only markers
    "v0.8.1-E Local Mock Data Fixture JSON Creation Plan is plan-first.",
    "v0.8.1-E Local Mock Data Fixture JSON Creation Plan is creation-plan-only.",
    "v0.8.1-E does not create fixture JSON.",
    "v0.8.1-E does not create .json artifact.",
    "v0.8.1-E does not create mock data file.",
    "v0.8.1-E does not create seed data file.",
    "v0.8.1-E does not create fixture directory.",
    "v0.8.1-E does not create preview data loader.",
    "v0.8.1-E does not implement fixture loader runtime.",
    "v0.8.1-E does not implement Dashboard preview display runtime.",
    "v0.8.1-E does not implement local mock data preview runtime.",
    "v0.8.1-E does not create Dashboard route.",
    "v0.8.1-E does not create Dashboard endpoint.",
    "v0.8.1-E does not create Dashboard template.",
    "v0.8.1-E does not create Dashboard static asset.",
    "v0.8.1-E does not modify app.",
    "v0.8.1-E does not modify templates.",
    "v0.8.1-E does not modify static.",
    "v0.8.1-E does not read real queue DB.",
    "v0.8.1-E does not write queue data.",
    "v0.8.1-E does not send POST.",
    "v0.8.1-E does not start Worker.",
    "v0.8.1-E does not connect OpenClaw.",
    "v0.8.1-E does not activate Hermes.",
    "v0.8.1-E does not connect Hermes.",
    "v0.8.1-E does not read Google Sheets.",
    "v0.8.1-E does not write Google Sheets.",
    "v0.8.1-E does not read secrets.",
    "v0.8.1-E does not create .env.",
    "v0.8.1-E does not create webhook.",
    "v0.8.1-E does not create connector.",
    "v0.8.1-E does not create Remote Blackboard API runtime.",
    "v0.8.1-E does not create production DB.",
    "v0.8.1-E does not create shared DB.",
    "v0.8.1-E does not open shared write.",
    # relationship to v0.8.1-D
    "v0.8.1-D Local Mock Data Fixture JSON Approval Plan is complete.",
    "v0.8.1-E starts the Local Mock Data Fixture JSON Creation planning step.",
    "v0.8.1-E builds on Local Mock Data Fixture JSON Approval planning.",
    "v0.8.1-E plans the artifact creation before any fixture JSON is created.",
    "v0.8.1-E preserves Owner final approval authority.",
    "v0.8.1-E preserves decision and dispatch separation.",
    "v0.8.1-E preserves audit trail.",
    "v0.8.1-E preserves dispatch-disabled boundary.",
    "v0.8.1-E preserves local mock data preview boundary.",
    "v0.8.1-E preserves the fixture contract boundary.",
    "v0.8.1-E preserves the fixture draft boundary.",
    "v0.8.1-E preserves the fixture JSON approval boundary.",
    "v0.8.1-E preserves read-only Dashboard display boundary.",
    "v0.8.1-E does not change any v0.8.1-D boundary.",
    "v0.8.1-E does not change any v0.8.1-C boundary.",
    "v0.8.1-E does not change any v0.8.1-B boundary.",
    "v0.8.1-E does not change any v0.8.1-A boundary.",
    "v0.8.1-E does not change any v0.8.0-G boundary.",
    "v0.8.1-E does not change any v0.8.0-F boundary.",
    "v0.8.1-E does not change any v0.8.0-A boundary.",
    "v0.8.1-E does not change any v0.7.5 boundary.",
    # problem statement
    "The system needs a planned creation method before any fixture JSON artifact can be created.",
    "Fixture JSON creation planning must not become execution permission.",
    "Fixture JSON creation planning must not become Worker dispatch.",
    "Fixture JSON creation planning must not call OpenClaw.",
    "Fixture JSON creation planning must not activate Hermes.",
    "Fixture JSON creation planning must not write queue data.",
    "A fixture JSON artifact created without a creation plan could leak real data or be mistaken for an execution surface.",
    "Planning the creation is not creating the fixture JSON.",
    "Planning the creation is not running the loop.",
    # definition
    "Local Mock Data Fixture JSON Creation Plan means the agreed method a future fixture JSON artifact must follow when created.",
    "Local Mock Data Fixture JSON Creation Plan is a planning artifact in v0.8.1-E.",
    "Local Mock Data Fixture JSON Creation Plan is not runtime code.",
    "Local Mock Data Fixture JSON Creation Plan is not a fixture JSON file.",
    "Local Mock Data Fixture JSON Creation Plan is not a mock data file.",
    "Local Mock Data Fixture JSON Creation Plan is not a preview data loader.",
    "Local Mock Data Fixture JSON Creation Plan requires separate future plan and Owner approval before artifact creation.",
    # safety principles
    "Approval is not execution.",
    "Approval readiness is not execution permission.",
    "Decision and dispatch remain separate.",
    "Fixture JSON creation planning is not fixture JSON creation.",
    "Fixture JSON creation planning is not mock data file creation.",
    "Fixture JSON creation planning is not execution permission.",
    "Fixture JSON creation planning is not Worker dispatch.",
    "Fixture JSON creation planning is not OpenClaw call.",
    "Fixture JSON creation planning is not Hermes action.",
    "Fixture JSON creation planning must not read real queue DB.",
    "Fixture JSON creation planning must not send POST.",
    "Fixture JSON creation planning must not create fixture JSON.",
    "Fixture JSON creation planning must not create preview data loader.",
    "Dashboard preview display is read-only.",
    # creation planning boundary
    "Fixture JSON creation planning boundary is planning only.",
    "Fixture JSON creation planning is expressed as text and pseudo-field descriptions only.",
    "No fixture JSON creation planning runtime is implemented in v0.8.1-E.",
    # artifact prohibition boundary
    "Fixture JSON artifact prohibition boundary is planning only.",
    "No fixture JSON is created in v0.8.1-E.",
    "No .json artifact is created in v0.8.1-E.",
    "No JSON object is created in v0.8.1-E.",
    "Fixture JSON artifact creation requires separate Owner approval.",
    # candidate artifact path
    "Candidate fixture JSON path: fixtures/local_mock_data/hermes_openclaw_local_mock_messages_v0_8_1.json",
    "Candidate fixture JSON path is planning only.",
    "Candidate fixture JSON path is not created in v0.8.1-E.",
    "Candidate fixture directory is not created in v0.8.1-E.",
    "Candidate fixture JSON file is not created in v0.8.1-E.",
    # candidate filename
    "Candidate fixture JSON filename: hermes_openclaw_local_mock_messages_v0_8_1.json",
    "Candidate fixture JSON filename is planning only.",
    "Candidate fixture JSON filename is not created in v0.8.1-E.",
    # candidate schema version
    "Candidate fixture JSON schema_version: v0.8.1-local-mock-1.",
    "Candidate schema version is planning only.",
    "Candidate schema version is not implemented in v0.8.1-E.",
    # candidate top-level shape
    "Candidate top-level shape is planning only.",
    "Candidate top-level shape may include schema_version.",
    "Candidate top-level shape may include fixture_id.",
    "Candidate top-level shape may include is_mock.",
    "Candidate top-level shape may include created_for.",
    "Candidate top-level shape may include records.",
    "Candidate top-level shape is not implemented in v0.8.1-E.",
    # candidate record family plan
    "Candidate record family plan is planning only.",
    "Candidate record family plan is not implemented in v0.8.1-E.",
    "No record family runtime is implemented in v0.8.1-E.",
    # candidate record count plan
    "Candidate record count plan is planning only.",
    "Candidate record count may include one record per message family.",
    "Candidate record count must remain small and reviewable.",
    "Candidate record count must not be generated from real queue data.",
    "Candidate record count must not be generated from Google Sheets.",
    "No records are created in v0.8.1-E.",
    # candidate ordering plan
    "Candidate ordering plan is planning only.",
    "Candidate ordering may group task, decision, result, advice, badge, runtime-off status.",
    "Candidate ordering must be deterministic.",
    "Candidate ordering must not depend on real queue timestamp.",
    "Candidate ordering must not depend on external service response.",
    "No ordering runtime is implemented in v0.8.1-E.",
    # synthetic local-only value policy
    "Synthetic local-only value policy: every value must be synthetic.",
    "Synthetic local-only value policy: every value must be local-only.",
    "Synthetic local-only value policy: no value comes from real queue DB.",
    "Synthetic local-only value policy: no value comes from Google Sheets.",
    "Synthetic local-only value policy: no value comes from Remote Blackboard API.",
    "Synthetic local-only value policy: no value comes from secrets.",
    "Synthetic local-only value policy: no source-of-truth switch is performed.",
    "No synthetic local-only value reader is implemented in v0.8.1-E.",
    # example value policy
    "Example values must be synthetic.",
    "Example values must be local-only.",
    "Example values must be non-secret.",
    "Example values must be clearly marked as mock.",
    "Example values must be safe to display.",
    "Example values must not contain real queue IDs.",
    "Example values must not contain real task IDs.",
    "Example values must not contain real user data.",
    "Example values must not contain spreadsheet IDs.",
    "Example values must not contain tokens.",
    "Example values must not contain endpoints.",
    "Example values must not contain production URLs.",
    # message families
    "Mock Task Message",
    "Mock Decision Message",
    "Mock Result Message",
    "Mock Advice Message",
    "Mock Badge Status",
    "Mock Runtime-off Status",
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
    "Required fields creation checklist is planning only.",
    "No required field is implemented in v0.8.1-E.",
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
    "Forbidden fields rejection checklist is planning only.",
    "No forbidden field value is included in v0.8.1-E.",
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
    "Boolean safety invariant checklist is planning only.",
    "No boolean safety invariant runtime is implemented in v0.8.1-E.",
    # per-family candidate record plans
    "Candidate Mock Task Message record plan:",
    "Candidate Mock Decision Message record plan:",
    "Candidate Mock Result Message record plan:",
    "Candidate Mock Advice Message record plan:",
    "Candidate Mock Badge Status record plan:",
    "Candidate Mock Runtime-off Status record plan:",
    "No Mock Task Message record is created in v0.8.1-E.",
    "No Mock Decision Message record is created in v0.8.1-E.",
    "No Mock Result Message record is created in v0.8.1-E.",
    "No Mock Advice Message record is created in v0.8.1-E.",
    "No Mock Badge Status record is created in v0.8.1-E.",
    "No Mock Runtime-off Status record is created in v0.8.1-E.",
    # creation checklist
    "Creation checklist: Owner has separately approved fixture JSON artifact creation.",
    "Creation checklist: candidate path is reviewed.",
    "Creation checklist: candidate filename is reviewed.",
    "Creation checklist: schema_version is reviewed.",
    "Creation checklist: every record remains synthetic local-only.",
    "Creation checklist: every record remains is_mock = true.",
    "Creation checklist: every message_family is one of the agreed mock families.",
    "Creation checklist: every required field is present.",
    "Creation checklist: no forbidden field is present.",
    "Creation checklist: all boolean safety invariants remain safe.",
    "Creation checklist: record count remains small and reviewable.",
    "Creation checklist: ordering remains deterministic.",
    "Creation checklist: no real queue DB read is required.",
    "Creation checklist: no POST is required.",
    "Creation checklist: no Worker/OpenClaw/Hermes action is required.",
    "Creation checklist: no Google Sheets access is required.",
    "Creation checklist: no secrets access is required.",
    # validation checklist
    "Validation checklist: fixture JSON must validate as synthetic local-only before future use.",
    "Validation checklist: fixture JSON must contain only approved message families.",
    "Validation checklist: fixture JSON must contain only approved required fields.",
    "Validation checklist: fixture JSON must contain no forbidden fields.",
    "Validation checklist: fixture JSON must satisfy boolean safety invariants.",
    "Validation checklist: fixture JSON must not include real queue IDs.",
    "Validation checklist: fixture JSON must not include real task IDs.",
    "Validation checklist: fixture JSON must not include real user data.",
    "Validation checklist: fixture JSON must not include spreadsheet IDs.",
    "Validation checklist: fixture JSON must not include tokens.",
    "Validation checklist: fixture JSON must not include secrets.",
    "Validation checklist: fixture JSON must not include endpoints.",
    "Validation checklist: fixture JSON must not enable dispatch.",
    "Validation checklist: fixture JSON must not enable Worker.",
    "Validation checklist: fixture JSON must not connect OpenClaw.",
    "Validation checklist: fixture JSON must not activate Hermes.",
    "Validation checklist: fixture JSON must not enable Google Sheets.",
    # Owner approval gate
    "Fixture JSON artifact must not be created until the Owner approves the creation plan.",
    "Owner approval gate is Owner-controlled.",
    "Owner approval gate must precede any fixture artifact.",
    "Owner approval gate must precede any preview data loader.",
    "Owner approval gate is not satisfied in v0.8.1-E.",
    # future fixture JSON implementation boundary
    "Future fixture JSON implementation requires separate Owner approval.",
    "Future fixture JSON implementation must remain synthetic local-only.",
    "Future fixture JSON implementation must not read real queue DB.",
    "Future fixture JSON implementation must not send POST.",
    "Future fixture JSON implementation must not start Worker.",
    "Future fixture JSON implementation must not call OpenClaw.",
    "Future fixture JSON implementation must not activate Hermes.",
    "Future fixture JSON implementation must not read or write Google Sheets.",
    "No fixture JSON implementation runtime is implemented in v0.8.1-E.",
    # future read-only loader boundary
    "A future read-only loader may read the approved fixture once it exists.",
    "Future read-only loader is display-only.",
    "Future read-only loader is not execution permission.",
    "Future read-only loader must not write the fixture.",
    "Future read-only loader must not read real queue DB.",
    "Future read-only loader must not send POST.",
    "No read-only loader runtime is implemented in v0.8.1-E.",
    "No preview data loader is implemented in v0.8.1-E.",
    # future Dashboard preview boundary
    "Dashboard may eventually display the approved local mock data fixture once created.",
    "Future Dashboard preview is display-only.",
    "No Dashboard fixture preview runtime is implemented in v0.8.1-E.",
    # Dashboard route / template / static boundary
    "Dashboard route boundary is planning only.",
    "No Dashboard route is created in v0.8.1-E.",
    "No Dashboard endpoint is created in v0.8.1-E.",
    "No Dashboard template is created in v0.8.1-E.",
    "No Dashboard static asset is created in v0.8.1-E.",
    "No app route is modified in v0.8.1-E.",
    "No template file is modified in v0.8.1-E.",
    "No static file is modified in v0.8.1-E.",
    # app / runtime boundary
    "App / runtime boundary is planning only.",
    "No app module is modified in v0.8.1-E.",
    "No app.main import is performed in v0.8.1-E.",
    "No QueueStore import is performed in v0.8.1-E.",
    "No runtime host is created in v0.8.1-E.",
    "No daemon is created in v0.8.1-E.",
    "No systemd service is created in v0.8.1-E.",
    "No Docker deployment is created in v0.8.1-E.",
    "No fixture loader runtime is created in v0.8.1-E.",
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
    "Remote Blackboard API runtime is not implemented in v0.8.1-E.",
    "Remote Blackboard API read is not enabled in v0.8.1-E.",
    "Remote Blackboard API write is not enabled in v0.8.1-E.",
    "Remote Blackboard API is not required for fixture JSON creation planning.",
    # separation
    "Worker remains OFF.",
    "OpenClaw remains Not Connected.",
    "Hermes remains Not Connected.",
    "Worker is dispatch runtime.",
    "OpenClaw is execution / gateway / tools layer.",
    "Hermes is strategy / proxy / memory layer.",
    "Worker must not run from plan-only fixture JSON creation planning.",
    "OpenClaw must not execute from plan-only fixture JSON creation planning.",
    "Hermes must not act from plan-only fixture JSON creation planning.",
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
    "Future fixture JSON creation changes must be auditable.",
    "Future fixture JSON actions must include rollback notes when external actions are involved.",
    "Future fixture JSON failures must not silently retry external actions.",
    "Future fixture JSON failures must not bypass Owner approval.",
    "Future fixture JSON failures must not write Google Sheets by default.",
    "Future fixture JSON failures must not call OpenClaw by default.",
    "Future fixture JSON failures must not start Worker by default.",
    "No fixture JSON creation failure handling runtime is implemented in v0.8.1-E.",
    # candidate future phases
    "Candidate future phase: docs-only local mock data fixture JSON creation plan.",
    "Candidate future phase: local mock data fixture JSON candidate artifact plan.",
    "Candidate future phase: candidate fixture JSON artifact review.",
    "Candidate future phase: read-only Mock Task Message fixture JSON record review.",
    "Candidate future phase: read-only Mock Decision Message fixture JSON record review.",
    "Candidate future phase: read-only Mock Result Message fixture JSON record review.",
    "Candidate future phase: read-only Mock Advice Message fixture JSON record review.",
    "Candidate future phase: read-only Mock Badge Status fixture JSON record review.",
    "Candidate future phase: read-only Mock Runtime-off Status fixture JSON record review.",
    "Candidate future phases are planning notes only.",
    "No candidate future phase is implemented in v0.8.1-E.",
    "No candidate future phase is enabled in v0.8.1-E.",
    # disabled runtime list
    "Fixture JSON creation planning runtime is disabled.",
    "Fixture loader runtime is disabled.",
    "Preview data loader runtime is disabled.",
    "Local mock data preview runtime is disabled.",
    "Dashboard fixture preview runtime is disabled.",
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
    "v0.8.1-E readiness: ALL PASS.",
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
    "v0.8.1-F — Local Mock Data Fixture JSON Candidate Artifact Plan",
    "v0.8.1-F must not start unless separately approved by Owner.",
    "v0.8.1-F must not create fixture JSON unless separately approved by Owner.",
    "v0.8.1-F must not create preview data loader.",
    "v0.8.1-F must not modify Dashboard route/template/static.",
    "v0.8.1-F must not read real queue DB.",
    "v0.8.1-F must not send POST.",
    "v0.8.1-F must not start Worker.",
    "v0.8.1-F must not call OpenClaw.",
    "v0.8.1-F must not activate Hermes.",
    "v0.8.1-F must not read or write Google Sheets.",
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
    "Creation checklist: no real queue DB read is required.",
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
    "Dashboard fixture preview runtime created",
    "Dashboard fixture preview runtime implemented",
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
    print(f"\nXX v0.8.1-E readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print(
        "\nv0.8.1-E Local Mock Data Fixture JSON Creation Plan readiness: ALL PASS"
    )
    sys.exit(0)
