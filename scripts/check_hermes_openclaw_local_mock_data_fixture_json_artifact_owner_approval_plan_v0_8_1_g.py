"""v0.8.1-G readiness check: Local Mock Data Fixture JSON Artifact Owner Approval Plan (plan-first / artifact-owner-approval-plan-only).

Owner-approval-plan verification. Checks that the v0.8.1-G plan document exists and contains the
required sections (1-51), the current-master marker, the v0.8.1-G plan-first /
artifact-owner-approval-plan-only markers, the relationship-to-v0.8.1-F markers, the
problem-statement markers, the Local Mock Data Fixture JSON Artifact Owner Approval Plan definition
markers, the Owner approval planning / artifact prohibition boundary markers, the candidate
artifact relationship / path / filename / schema version reminder markers, the Owner approval
request shape / required fields markers, the Owner approval decision fields / decision values
markers, the acceptance / rejection criteria markers, the audit trail / rollback note markers, the
approval-is-not-execution / approval-readiness-is-not-execution / decision-vs-dispatch / artifact
creation permission boundary markers, the future fixture JSON creation / content / loader /
Dashboard preview boundary markers, the Dashboard route / template / static boundary markers, the
app / runtime boundary markers, the queue and real data boundary markers, the Remote Blackboard
API relationship markers, the Worker / OpenClaw / Hermes separation markers, the Google Sheets
boundary markers, the secrets / privacy / memory boundary markers, the network / webhook /
connector boundary markers, the failure / rollback / audit boundary markers, the Owner approval /
rejection / record / validation checklist markers, the forbidden fields rejection checklist
markers, the boolean safety invariant checklist markers, the message family approval checklist
markers, the disabled runtime list markers, the current safe posture markers, the validation
summary markers, the safety grep summary markers, and the next recommended step (v0.8.1-H) — and
that it asserts no unsafe "implemented / created / added / enabled / activated / connected /
called / started / written / read / modified / moved / migrated" claim, no execution / dispatch /
external-side-effects permission grant, and contains no real secret value.

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
    / "HERMES_OPENCLAW_LOCAL_MOCK_DATA_FIXTURE_JSON_ARTIFACT_OWNER_APPROVAL_PLAN_V0_8_1_G.md"
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
ok("v0.8.1-G plan doc 存在") if DOC_PATH.exists() else xx("v0.8.1-G plan doc 存在")
if not DOC_PATH.exists():
    print("\nXX plan doc 不存在，無法繼續")
    sys.exit(1)

doc = DOC_PATH.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# [2] 必須包含的章節（1-51）
# ---------------------------------------------------------------------------
print("[2] 必須包含的章節")
REQUIRED_SECTIONS = [
    "1. Purpose",
    "2. Current master",
    "3. Scope",
    "4. Relationship to v0.8.1-F Local Mock Data Fixture JSON Candidate Artifact Plan",
    "5. Problem statement",
    "6. Local Mock Data Fixture JSON Artifact Owner Approval Plan definition",
    "7. Owner approval planning boundary",
    "8. Fixture JSON artifact prohibition boundary",
    "9. Candidate artifact relationship",
    "10. Candidate artifact path reminder",
    "11. Candidate artifact filename reminder",
    "12. Candidate schema version reminder",
    "13. Owner approval request shape",
    "14. Owner approval request required fields",
    "15. Owner approval decision fields",
    "16. Owner approval decision values",
    "17. Owner approval acceptance criteria",
    "18. Owner rejection criteria",
    "19. Owner audit trail requirements",
    "20. Owner rollback note requirements",
    "21. Approval-is-not-execution boundary",
    "22. Approval-readiness-is-not-execution boundary",
    "23. Decision-vs-dispatch boundary",
    "24. Artifact creation permission boundary",
    "25. Future fixture JSON creation boundary",
    "26. Future fixture JSON content boundary",
    "27. Future read-only loader boundary",
    "28. Future Dashboard preview boundary",
    "29. Dashboard route / template / static boundary",
    "30. App / runtime boundary",
    "31. Queue and real data boundary",
    "32. Remote Blackboard API relationship",
    "33. Worker / OpenClaw / Hermes separation boundary",
    "34. Google Sheets boundary",
    "35. Secrets / privacy / memory boundary",
    "36. Network / webhook / connector boundary",
    "37. Failure / rollback / audit boundary",
    "38. Owner approval checklist",
    "39. Owner rejection checklist",
    "40. Owner approval record checklist",
    "41. Owner approval validation checklist",
    "42. Forbidden fields rejection checklist",
    "43. Boolean safety invariant checklist",
    "44. Message family approval checklist",
    "45. Disabled runtime list",
    "46. Current safe system posture",
    "47. Validation summary",
    "48. Safety grep summary",
    "49. Non-goals",
    "50. Acceptance criteria",
    "51. Next recommended step",
]
for section in REQUIRED_SECTIONS:
    ok(f"doc 含章節「{section}」") if section in doc else xx(f"doc 含章節「{section}」")

# ---------------------------------------------------------------------------
# [3] 必須包含的 markers
# ---------------------------------------------------------------------------
print("[3] 必須包含的 markers")
REQUIRED = [
    # version
    "v0.8.1-G",
    "Local Mock Data Fixture JSON Artifact Owner Approval Plan",
    # current master
    "HEAD = origin/master = 5d1aa2cdac52cf5ff546071adcdf5e31154122a6",
    "docs: plan local mock data fixture json candidate artifact",
    # v0.8.1-G plan-first / artifact-owner-approval-plan-only markers
    "v0.8.1-G Local Mock Data Fixture JSON Artifact Owner Approval Plan is plan-first.",
    "v0.8.1-G Local Mock Data Fixture JSON Artifact Owner Approval Plan is artifact-owner-approval-plan-only.",
    "v0.8.1-G does not create fixture JSON.",
    "v0.8.1-G does not create .json artifact.",
    "v0.8.1-G does not create mock data file.",
    "v0.8.1-G does not create seed data file.",
    "v0.8.1-G does not create fixture directory.",
    "v0.8.1-G does not create preview data loader.",
    "v0.8.1-G does not implement fixture loader runtime.",
    "v0.8.1-G does not implement Dashboard preview display runtime.",
    "v0.8.1-G does not implement local mock data preview runtime.",
    "v0.8.1-G does not create Dashboard route.",
    "v0.8.1-G does not create Dashboard endpoint.",
    "v0.8.1-G does not create Dashboard template.",
    "v0.8.1-G does not create Dashboard static asset.",
    "v0.8.1-G does not modify app.",
    "v0.8.1-G does not modify templates.",
    "v0.8.1-G does not modify static.",
    "v0.8.1-G does not read real queue DB.",
    "v0.8.1-G does not write queue data.",
    "v0.8.1-G does not send POST.",
    "v0.8.1-G does not start Worker.",
    "v0.8.1-G does not connect OpenClaw.",
    "v0.8.1-G does not activate Hermes.",
    "v0.8.1-G does not connect Hermes.",
    "v0.8.1-G does not read Google Sheets.",
    "v0.8.1-G does not write Google Sheets.",
    "v0.8.1-G does not read secrets.",
    "v0.8.1-G does not create .env.",
    "v0.8.1-G does not create webhook.",
    "v0.8.1-G does not create connector.",
    "v0.8.1-G does not create Remote Blackboard API runtime.",
    "v0.8.1-G does not create production DB.",
    "v0.8.1-G does not create shared DB.",
    "v0.8.1-G does not open shared write.",
    # relationship to v0.8.1-F
    "v0.8.1-F Local Mock Data Fixture JSON Candidate Artifact Plan is complete.",
    "v0.8.1-G starts the Local Mock Data Fixture JSON Artifact Owner Approval planning step.",
    "v0.8.1-G builds on Local Mock Data Fixture JSON Candidate Artifact planning.",
    "v0.8.1-G plans Owner approval before any fixture JSON is created.",
    "v0.8.1-G preserves Owner final approval authority.",
    "v0.8.1-G preserves decision and dispatch separation.",
    "v0.8.1-G preserves audit trail.",
    "v0.8.1-G preserves dispatch-disabled boundary.",
    "v0.8.1-G preserves local mock data preview boundary.",
    "v0.8.1-G preserves the fixture contract boundary.",
    "v0.8.1-G preserves the fixture draft boundary.",
    "v0.8.1-G preserves the fixture JSON approval boundary.",
    "v0.8.1-G preserves the fixture JSON creation boundary.",
    "v0.8.1-G preserves the candidate artifact planning boundary.",
    "v0.8.1-G preserves read-only Dashboard display boundary.",
    "v0.8.1-G does not change any v0.8.1-F boundary.",
    "v0.8.1-G does not change any v0.8.1-E boundary.",
    "v0.8.1-G does not change any v0.8.1-D boundary.",
    "v0.8.1-G does not change any v0.8.1-C boundary.",
    "v0.8.1-G does not change any v0.8.1-B boundary.",
    "v0.8.1-G does not change any v0.8.1-A boundary.",
    "v0.8.1-G does not change any v0.8.0-G boundary.",
    "v0.8.1-G does not change any v0.8.0-F boundary.",
    # definition
    "Local Mock Data Fixture JSON Artifact Owner Approval Plan means the agreed way the Owner would review, approve, reject, and audit a future fixture JSON artifact creation.",
    "Local Mock Data Fixture JSON Artifact Owner Approval Plan is a planning artifact in v0.8.1-G.",
    "Local Mock Data Fixture JSON Artifact Owner Approval Plan is not runtime code.",
    "Local Mock Data Fixture JSON Artifact Owner Approval Plan is not a fixture JSON file.",
    "Local Mock Data Fixture JSON Artifact Owner Approval Plan is not a mock data file.",
    "Local Mock Data Fixture JSON Artifact Owner Approval Plan is not a preview data loader.",
    "Local Mock Data Fixture JSON Artifact Owner Approval Plan requires separate future plan and Owner approval before artifact creation.",
    # safety principles
    "Approval is not execution.",
    "Approval readiness is not execution permission.",
    "Owner approval is not dispatch permission.",
    "Decision and dispatch remain separate.",
    "Fixture JSON artifact Owner approval planning is not fixture JSON creation.",
    "Fixture JSON artifact Owner approval planning is not mock data file creation.",
    "Fixture JSON artifact Owner approval planning is not execution permission.",
    "Fixture JSON artifact Owner approval planning is not Worker dispatch.",
    "Fixture JSON artifact Owner approval planning is not OpenClaw call.",
    "Fixture JSON artifact Owner approval planning is not Hermes action.",
    "Fixture JSON artifact Owner approval planning must not read real queue DB.",
    "Fixture JSON artifact Owner approval planning must not send POST.",
    "Fixture JSON artifact Owner approval planning must not create fixture JSON.",
    "Fixture JSON artifact Owner approval planning must not create preview data loader.",
    "Dashboard preview display is read-only.",
    # Owner approval planning boundary
    "Owner approval planning boundary is planning only.",
    "Owner approval planning is expressed as text and pseudo-field descriptions only.",
    "No Owner approval planning runtime is implemented in v0.8.1-G.",
    # artifact prohibition boundary
    "Fixture JSON artifact prohibition boundary is planning only.",
    "No fixture JSON is created in v0.8.1-G.",
    "No .json artifact is created in v0.8.1-G.",
    "No JSON object is created in v0.8.1-G.",
    "Fixture JSON artifact creation requires separate Owner approval.",
    # candidate artifact relationship
    "Candidate artifact relationship is planning only.",
    "The Owner approval plan reviews the v0.8.1-F candidate artifact plan.",
    "The Owner approval plan does not create the candidate artifact.",
    "The Owner approval plan does not modify the candidate artifact plan.",
    "No candidate artifact runtime is implemented in v0.8.1-G.",
    # candidate artifact path reminder
    "Candidate fixture JSON path: fixtures/local_mock_data/hermes_openclaw_local_mock_messages_v0_8_1.json",
    "Candidate fixture JSON path is planning only.",
    "Candidate fixture JSON path is not created in v0.8.1-G.",
    "Candidate fixture directory is not created in v0.8.1-G.",
    "Candidate fixture JSON file is not created in v0.8.1-G.",
    "Candidate artifact path is inherited from v0.8.1-F planning.",
    # candidate artifact filename reminder
    "Candidate fixture JSON filename: hermes_openclaw_local_mock_messages_v0_8_1.json",
    "Candidate fixture JSON filename is planning only.",
    "Candidate fixture JSON filename is not created in v0.8.1-G.",
    # candidate schema version reminder
    "Candidate fixture JSON schema_version: v0.8.1-local-mock-1.",
    "Candidate schema version is planning only.",
    "Candidate schema version is not implemented in v0.8.1-G.",
    "No schema migration is performed in v0.8.1-G.",
    # Owner approval request shape
    "Owner approval request shape is planning only.",
    "Owner approval request is not implemented in v0.8.1-G.",
    "Owner approval request may include approval_request_id.",
    "Owner approval request may include candidate_artifact_plan_version.",
    "Owner approval request may include candidate_fixture_path.",
    "Owner approval request may include candidate_schema_version.",
    "Owner approval request may include approval_scope.",
    "Owner approval request may include approval_question.",
    "Owner approval request may include acceptance_criteria_summary.",
    "Owner approval request may include rejection_criteria_summary.",
    "Owner approval request may include safety_invariant_summary.",
    "Owner approval request may include requested_owner_decision.",
    "Owner approval request may include created_for.",
    "Owner approval request may include audit_notes.",
    "No Owner approval request record is created in v0.8.1-G.",
    # Owner approval decision fields
    "Owner approval decision fields are planning only.",
    "Owner approval decision may include approval_decision_id.",
    "Owner approval decision may include approval_request_id.",
    "Owner approval decision may include owner_decision.",
    "Owner approval decision may include approved_scope.",
    "Owner approval decision may include rejected_reason.",
    "Owner approval decision may include approval_timestamp.",
    "Owner approval decision may include approval_notes.",
    "Owner approval decision may include rollback_notes.",
    "Owner approval decision may include execution_permission.",
    "Owner approval decision may include dispatch_permission.",
    "Owner approval decision may include external_side_effects_permission.",
    "No Owner approval decision record is created in v0.8.1-G.",
    # decision values
    "Owner decision value: approve_candidate_artifact_creation_plan.",
    "Owner decision value: reject_candidate_artifact_creation_plan.",
    "Owner decision value: request_revision.",
    "Owner decision value: defer_decision.",
    "Owner approval decision values are planning only.",
    "No Owner approval decision runtime is implemented in v0.8.1-G.",
    # approval-is-not-execution
    "Owner approval of fixture JSON artifact creation plan is not execution permission.",
    "Owner approval of fixture JSON artifact creation plan is not Worker dispatch permission.",
    "Owner approval of fixture JSON artifact creation plan is not OpenClaw call permission.",
    "Owner approval of fixture JSON artifact creation plan is not Hermes activation permission.",
    "Owner approval of fixture JSON artifact creation plan is not Google Sheets permission.",
    "Owner approval of fixture JSON artifact creation plan is not POST permission.",
    "Owner approval of fixture JSON artifact creation plan only approves a future artifact creation step if separately scoped.",
    # execution flags false
    "execution_permission = false",
    "dispatch_permission = false",
    "external_side_effects_permission = false",
    # required field candidates (bare tokens)
    "approval_request_id",
    "candidate_artifact_plan_version",
    "candidate_fixture_path",
    "candidate_schema_version",
    "approval_scope",
    "approval_question",
    "acceptance_criteria_summary",
    "rejection_criteria_summary",
    "safety_invariant_summary",
    "requested_owner_decision",
    "created_for",
    "audit_notes",
    # decision field candidates (bare tokens)
    "approval_decision_id",
    "owner_decision",
    "approved_scope",
    "rejected_reason",
    "approval_timestamp",
    "approval_notes",
    "rollback_notes",
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
    "No boolean safety invariant runtime is implemented in v0.8.1-G.",
    # message families
    "Mock Task Message",
    "Mock Decision Message",
    "Mock Result Message",
    "Mock Advice Message",
    "Mock Badge Status",
    "Mock Runtime-off Status",
    # Owner approval checklist
    "Owner approval checklist: candidate artifact path is reviewed.",
    "Owner approval checklist: candidate schema_version is reviewed.",
    "Owner approval checklist: candidate artifact plan is reviewed.",
    "Owner approval checklist: candidate records collection is reviewed.",
    "Owner approval checklist: candidate message families are reviewed.",
    "Owner approval checklist: candidate required fields are reviewed.",
    "Owner approval checklist: candidate forbidden fields are reviewed as rejection triggers.",
    "Owner approval checklist: candidate boolean safety invariants are reviewed.",
    "Owner approval checklist: owner approval request shape is reviewed.",
    "Owner approval checklist: owner approval decision fields are reviewed.",
    "Owner approval checklist: approval-is-not-execution boundary is reviewed.",
    "Owner approval checklist: decision-vs-dispatch boundary is reviewed.",
    "Owner approval checklist: future artifact creation boundary is reviewed.",
    "Owner approval checklist: no real queue DB read is required.",
    "Owner approval checklist: no POST is required.",
    "Owner approval checklist: no Worker/OpenClaw/Hermes action is required.",
    "Owner approval checklist: no Google Sheets access is required.",
    "Owner approval checklist: no secrets access is required.",
    # Owner rejection checklist
    "Owner rejection checklist: reject approval if candidate artifact path is unclear.",
    "Owner rejection checklist: reject approval if schema_version is unclear.",
    "Owner rejection checklist: reject approval if approval scope is unclear.",
    "Owner rejection checklist: reject approval if acceptance criteria are incomplete.",
    "Owner rejection checklist: reject approval if rejection criteria are incomplete.",
    "Owner rejection checklist: reject approval if rollback notes are missing.",
    "Owner rejection checklist: reject approval if audit notes are missing.",
    "Owner rejection checklist: reject approval if execution permission is requested.",
    "Owner rejection checklist: reject approval if dispatch permission is requested.",
    "Owner rejection checklist: reject approval if external side effects are requested.",
    "Owner rejection checklist: reject approval if real queue DB read is required.",
    "Owner rejection checklist: reject approval if POST is required.",
    "Owner rejection checklist: reject approval if Worker/OpenClaw/Hermes action is required.",
    "Owner rejection checklist: reject approval if Google Sheets access is required.",
    "Owner rejection checklist: reject approval if secrets access is required.",
    # Owner approval record checklist
    "Owner approval record checklist: approval request must remain synthetic local-only.",
    "Owner approval record checklist: approval decision must remain synthetic local-only.",
    "Owner approval record checklist: approval request must not contain forbidden fields.",
    "Owner approval record checklist: approval decision must not contain forbidden fields.",
    "Owner approval record checklist: approval record must not contain real queue IDs.",
    "Owner approval record checklist: approval record must not contain real task IDs.",
    "Owner approval record checklist: approval record must not contain real user data.",
    "Owner approval record checklist: approval record must not contain spreadsheet IDs.",
    "Owner approval record checklist: approval record must not contain tokens.",
    "Owner approval record checklist: approval record must not contain secrets.",
    "Owner approval record checklist: approval record must not contain endpoints.",
    "Owner approval record checklist: approval record must preserve execution_permission = false.",
    "Owner approval record checklist: approval record must preserve dispatch_permission = false.",
    "Owner approval record checklist: approval record must preserve external_side_effects_permission = false.",
    # validation checklist
    "Validation checklist: owner approval plan must remain synthetic local-only.",
    "Validation checklist: owner approval plan must contain no fixture JSON.",
    "Validation checklist: owner approval plan must contain no JSON object.",
    "Validation checklist: owner approval plan must contain no mock data file.",
    "Validation checklist: owner approval plan must contain no fixture directory.",
    "Validation checklist: owner approval plan must contain no preview data loader.",
    "Validation checklist: owner approval plan must contain no runtime.",
    "Validation checklist: owner approval plan must contain no forbidden field values.",
    "Validation checklist: owner approval plan must satisfy boolean safety invariants.",
    "Validation checklist: owner approval plan must not enable dispatch.",
    "Validation checklist: owner approval plan must not enable Worker.",
    "Validation checklist: owner approval plan must not connect OpenClaw.",
    "Validation checklist: owner approval plan must not activate Hermes.",
    "Validation checklist: owner approval plan must not enable Google Sheets.",
    "Validation checklist: owner approval plan must not read real queue DB.",
    "Validation checklist: owner approval plan must not send POST.",
    "Validation checklist: owner approval plan must not read secrets.",
    # forbidden field rejection checklist
    "Forbidden field rejection checklist: reject if real_queue_id appears as a field.",
    "Forbidden field rejection checklist: reject if real_task_id appears as a field.",
    "Forbidden field rejection checklist: reject if real_user_secret appears as a field.",
    "Forbidden field rejection checklist: reject if spreadsheet_id appears as a field.",
    "Forbidden field rejection checklist: reject if refresh_token appears as a field.",
    "Forbidden field rejection checklist: reject if client_secret appears as a field.",
    "Forbidden field rejection checklist: reject if private_key appears as a field.",
    "Forbidden field rejection checklist: reject if webhook_url appears as a field.",
    "Forbidden field rejection checklist: reject if openclaw_endpoint appears as a field.",
    "Forbidden field rejection checklist: reject if hermes_endpoint appears as a field.",
    "Forbidden field rejection checklist: reject if production_db_url appears as a field.",
    "Forbidden field rejection checklist: reject if remote_blackboard_api_url appears as a field.",
    # separation
    "Worker remains OFF.",
    "OpenClaw remains Not Connected.",
    "Hermes remains Not Connected.",
    "Worker is dispatch runtime.",
    "OpenClaw is execution / gateway / tools layer.",
    "Hermes is strategy / proxy / memory layer.",
    "Worker must not run from plan-only fixture JSON artifact Owner approval planning.",
    "OpenClaw must not execute from plan-only fixture JSON artifact Owner approval planning.",
    "Hermes must not act from plan-only fixture JSON artifact Owner approval planning.",
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
    # disabled runtime list
    "Fixture JSON artifact Owner approval planning runtime is disabled.",
    "Owner approval request runtime is disabled.",
    "Owner approval decision runtime is disabled.",
    "Fixture loader runtime is disabled.",
    "Preview data loader runtime is disabled.",
    "Local mock data preview runtime is disabled.",
    "Dashboard fixture preview runtime is disabled.",
    "Blackboard Loop runtime is disabled.",
    "Dashboard badge display runtime is disabled.",
    "Decision audit display runtime is disabled.",
    "Owner review checklist runtime is disabled.",
    "Dashboard preview display runtime is disabled.",
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
    "No Owner approval request runtime.",
    "No Owner approval decision runtime.",
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
    "v0.8.1-G readiness: ALL PASS.",
    "v0.8.1-F readiness: ALL PASS.",
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
    "v0.8.1-H — Local Mock Data Fixture JSON Creation Authorization Plan",
    "v0.8.1-H must not start unless separately approved by Owner.",
    "v0.8.1-H must not create fixture JSON unless separately approved by Owner.",
    "v0.8.1-H must not create preview data loader.",
    "v0.8.1-H must not modify Dashboard route/template/static.",
    "v0.8.1-H must not read real queue DB.",
    "v0.8.1-H must not send POST.",
    "v0.8.1-H must not start Worker.",
    "v0.8.1-H must not call OpenClaw.",
    "v0.8.1-H must not activate Hermes.",
    "v0.8.1-H must not read or write Google Sheets.",
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
    "Owner approval checklist: no real queue DB read is required.",
    "Owner rejection checklist: reject approval if real queue DB read is required.",
    "Rejection criteria: real queue DB read, POST, Worker, OpenClaw, Hermes, Google Sheets, or secrets access is required.",
    "real queue DB read is required.",
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
    "Dashboard fixture preview runtime created",
    "Dashboard fixture preview runtime implemented",
    "Owner approval request runtime created",
    "Owner approval decision runtime created",
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
    "execution_permission = True",
    "dispatch_permission = True",
    "external_side_effects_permission = True",
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
    print(f"\nXX v0.8.1-G readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print(
        "\nv0.8.1-G Local Mock Data Fixture JSON Artifact Owner Approval Plan readiness: ALL PASS"
    )
    sys.exit(0)
