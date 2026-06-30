"""v0.8.0-A readiness check: Owner-supervised Blackboard Loop MVP Plan (plan-first).

Plan-first / boundary verification. Checks that the v0.8.0-A plan document exists and
contains the required sections (1-31), the current-master marker, the v0.8.0-A plan-first
markers, the relationship-to-v0.7.5 markers, the problem-statement markers, the
Owner-supervised Blackboard Loop MVP definition markers, the loop actors and roles markers,
the Blackboard message families markers, the loop lifecycle draft markers, the Owner review
gate markers, the decision-versus-dispatch boundary markers, the Task / Advice / Result
boundary markers, the Worker / OpenClaw / Hermes separation boundary markers, the Remote
Blackboard API relationship markers, the local queue vs remote blackboard boundary markers,
the Dashboard display boundary markers, the Core runtime host relationship markers, the
source-of-truth and data boundary markers, the secrets / privacy / memory boundary markers,
the network / webhook / connector boundary markers, the failure / rollback / audit boundary
markers, the candidate MVP phases markers, the disabled runtime list markers, the current
safe posture markers, the validation summary markers, the safety grep summary markers, and
the next recommended step — and that it asserts no unsafe "implemented / created / added /
enabled / activated / connected / called / started / written / moved / migrated / changed"
claim and contains no secret.

The document is allowed to contain safe negations; those that literally embed a
forbidden substring are scrubbed before the forbidden scan so they are not mis-flagged.

This script only reads the plan document. It does NOT read .env, credentials, tokens, or
secrets, makes no network call, imports no app logic (no app.main, no QueueStore), adds no
API route / router / database client / migration, creates no production / shared DB, builds
no Blackboard Loop runtime, starts no loop scheduler, enables no dispatch gate, activates no
Hermes, connects no OpenClaw, starts no Worker, opens no shared write, and writes no Google
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
    / "HERMES_OPENCLAW_OWNER_SUPERVISED_BLACKBOARD_LOOP_MVP_PLAN_V0_8_0_A.md"
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
ok("v0.8.0-A plan doc 存在") if DOC_PATH.exists() else xx("v0.8.0-A plan doc 存在")
if not DOC_PATH.exists():
    print("\nXX plan doc 不存在，無法繼續")
    sys.exit(1)

doc = DOC_PATH.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# [2] 必須包含的章節（1-31）
# ---------------------------------------------------------------------------
print("[2] 必須包含的章節")
REQUIRED_SECTIONS = [
    "1. Purpose",
    "2. Current master",
    "3. Scope",
    "4. Relationship to v0.7.5 Remote Blackboard Preparation",
    "5. Problem statement",
    "6. Owner-supervised Blackboard Loop MVP definition",
    "7. Loop actors and roles",
    "8. Blackboard message families",
    "9. Loop lifecycle draft",
    "10. Owner review gate",
    "11. Decision vs dispatch boundary",
    "12. Task draft boundary",
    "13. Advice boundary",
    "14. Result boundary",
    "15. Worker / OpenClaw / Hermes separation boundary",
    "16. Remote Blackboard API relationship",
    "17. Local queue vs remote blackboard boundary",
    "18. Dashboard display boundary",
    "19. Core runtime host relationship",
    "20. Source-of-truth and data boundary",
    "21. Secrets / privacy / memory boundary",
    "22. Network / webhook / connector boundary",
    "23. Failure / rollback / audit boundary",
    "24. Candidate MVP phases",
    "25. Disabled runtime list",
    "26. Current safe system posture",
    "27. Validation summary",
    "28. Safety grep summary",
    "29. Non-goals",
    "30. Acceptance criteria",
    "31. Next recommended step",
]
for section in REQUIRED_SECTIONS:
    ok(f"doc 含章節「{section}」") if section in doc else xx(f"doc 含章節「{section}」")

# ---------------------------------------------------------------------------
# [3] 必須包含的 markers
# ---------------------------------------------------------------------------
print("[3] 必須包含的 markers")
REQUIRED = [
    # version
    "v0.8.0-A",
    "Owner-supervised Blackboard Loop MVP Plan",
    # current master
    "HEAD = origin/master = 1c59bd3484729fbe17026a747603d88f5d3ed6de",
    "docs: close out remote blackboard preparation",
    # v0.8.0-A plan-first markers
    "v0.8.0-A Owner-supervised Blackboard Loop MVP Plan is plan-first.",
    "v0.8.0-A does not implement Blackboard Loop runtime.",
    "v0.8.0-A does not create loop scheduler.",
    "v0.8.0-A does not enable dispatch gate.",
    "v0.8.0-A does not enable autonomous execution.",
    "v0.8.0-A does not activate Hermes.",
    "v0.8.0-A does not connect Hermes.",
    "v0.8.0-A does not connect OpenClaw.",
    "v0.8.0-A does not start Worker.",
    "v0.8.0-A does not create Hermes runtime.",
    "v0.8.0-A does not create OpenClaw runtime.",
    "v0.8.0-A does not create Worker runtime.",
    "v0.8.0-A does not implement Remote Blackboard API runtime.",
    "v0.8.0-A does not create production DB.",
    "v0.8.0-A does not create shared DB.",
    "v0.8.0-A does not create remote shared DB.",
    "v0.8.0-A does not migrate queue data.",
    "v0.8.0-A does not sync local queue and remote queue.",
    "v0.8.0-A does not open shared write.",
    "v0.8.0-A does not write Google Sheets.",
    "v0.8.0-A does not create webhook.",
    # relationship to v0.7.5
    "v0.7.5 Remote Blackboard Preparation line is complete.",
    "v0.8.0-A starts the Owner-supervised Blackboard Loop MVP planning line.",
    "v0.8.0-A builds on Remote Blackboard API planning.",
    "v0.8.0-A builds on local queue vs remote blackboard boundary.",
    "v0.8.0-A builds on Dashboard backend source planning.",
    "v0.8.0-A builds on Core runtime host planning.",
    "v0.8.0-A builds on Hermes activation boundary planning.",
    "v0.8.0-A does not change any v0.7.5 boundary.",
    # problem statement
    "The system needs a planned Owner-supervised loop before any runtime loop can be implemented.",
    "The loop must preserve Owner final approval.",
    "The loop must preserve decision and dispatch separation.",
    "The loop must preserve audit trail.",
    "The loop must not turn Blackboard messages into automatic commands.",
    "The loop must not make Hermes autonomous.",
    "The loop must not start Worker.",
    "The loop must not call OpenClaw.",
    "Planning the loop is not running the loop.",
    # MVP definition
    "Owner-supervised Blackboard Loop MVP means a future workflow that coordinates Blackboard messages under Owner review.",
    "Owner-supervised Blackboard Loop MVP may eventually organize Task Messages, Decision Messages, Result Messages, and Advice Messages.",
    "Owner-supervised Blackboard Loop MVP may eventually support Owner review before any dispatch.",
    "Owner-supervised Blackboard Loop MVP may eventually support dry-run loop previews.",
    "Owner-supervised Blackboard Loop MVP is not implemented in v0.8.0-A.",
    "Owner-supervised Blackboard Loop MVP is not autonomous execution.",
    "Owner-supervised Blackboard Loop MVP is not Worker dispatch.",
    "Owner-supervised Blackboard Loop MVP is not OpenClaw call.",
    "Owner-supervised Blackboard Loop MVP is not Hermes activation.",
    # loop actors and roles
    "Owner is final approval authority.",
    "ChatGPT is external advisor / prompt writer / architecture reviewer.",
    "Hermes is future strategy / proxy / memory layer, not active.",
    "OpenClaw is future execution / gateway / tools layer, not connected.",
    "Worker is future dispatch runtime, currently OFF.",
    "Dashboard is display / observation surface.",
    "Remote Blackboard API is future shared coordination backend, not implemented.",
    "GitHub is clean source of code and docs, not queue DB and not secrets store.",
    "Windows WSL is primary local development environment.",
    "Replit is remote observation station / Preview Dashboard.",
    # Blackboard message families
    "Task Message",
    "Decision Message",
    "Result Message",
    "Advice Message",
    "Task Message is not Worker dispatch.",
    "Decision Message is audit record, not command.",
    "Result Message is not next dispatch permission.",
    "Advice Message is advisory, not command.",
    "Hermes Advice Message is not automatic execution.",
    "Hermes Task Message draft requires Owner review.",
    "No new Blackboard message family is implemented in v0.8.0-A.",
    "No message schema migration is performed in v0.8.0-A.",
    # loop lifecycle draft
    "Loop lifecycle draft step: Task draft.",
    "Loop lifecycle draft step: Owner review.",
    "Loop lifecycle draft step: Decision audit.",
    "Loop lifecycle draft step: Dispatch gate remains disabled.",
    "Loop lifecycle draft step: Result observation.",
    "Loop lifecycle draft step: Advice observation.",
    "Loop lifecycle draft is planning only.",
    "Loop lifecycle is not implemented in v0.8.0-A.",
    "Loop lifecycle does not start Worker.",
    "Loop lifecycle does not call OpenClaw.",
    "Loop lifecycle does not activate Hermes.",
    # Owner review gate
    "Owner review gate is required before any future dispatch.",
    "Owner review gate must be visible.",
    "Owner review gate must be auditable.",
    "Owner review gate must preserve approve is not execute.",
    "Owner review gate must preserve approval readiness is not execution permission.",
    "Owner review gate must preserve Owner decision event is not Worker dispatch.",
    "Owner review gate is not implemented in v0.8.0-A.",
    "Owner approval remains separate from runtime dispatch.",
    # decision vs dispatch boundary
    "Decision is not dispatch.",
    "Approve is not execute.",
    "Approval readiness is not execution permission.",
    "Owner decision message is audit record, not command.",
    "Writing a task to Blackboard is not Worker dispatch.",
    "Entering Blackboard mode is not execution permission.",
    "Dispatch requires separate future runtime plan and Owner approval.",
    "Dispatch gate remains disabled in v0.8.0-A.",
    # Task / Advice / Result boundary
    "Task draft is draft only.",
    "Task draft requires Owner review.",
    "Task draft is not queue write by itself.",
    "Task draft is not Worker dispatch.",
    "Task draft is not OpenClaw call.",
    "Advice is advisory only.",
    "Advice is not command.",
    "Advice is not Worker dispatch.",
    "Advice is not OpenClaw call.",
    "Advice is not Google Sheets write.",
    "Result is observation only.",
    "Result is not next dispatch permission.",
    "Result is not automatic follow-up execution.",
    "Result is not Google Sheets write.",
    # Worker / OpenClaw / Hermes separation
    "Worker remains OFF.",
    "OpenClaw remains Not Connected.",
    "Hermes remains Not Connected.",
    "Worker is dispatch runtime.",
    "OpenClaw is execution / gateway / tools layer.",
    "Hermes is strategy / proxy / memory layer.",
    "Hermes must not bypass Owner review.",
    "Hermes must not bypass OpenClaw boundary.",
    "Hermes must not bypass Worker boundary.",
    "OpenClaw must not execute without Owner-approved dispatch path.",
    "Worker must not run from plan-only loop.",
    # Remote Blackboard API relationship
    "Remote Blackboard API remains planning only.",
    "Remote Blackboard API runtime is not implemented in v0.8.0-A.",
    "Remote Blackboard API route is not added in v0.8.0-A.",
    "Remote Blackboard API read is not enabled in v0.8.0-A.",
    "Remote Blackboard API write is not enabled in v0.8.0-A.",
    "Remote Blackboard API is not execution dispatcher.",
    "Remote Blackboard API is not production DB.",
    "Remote Blackboard API runtime requires separate future plan and Owner approval.",
    # local queue vs remote blackboard boundary
    "Local Queue is not Remote Blackboard.",
    "Remote Blackboard is not local queue.",
    "WSL local queue remains local.",
    "Replit local queue remains separate.",
    "Dashboard update is not queue synchronization.",
    "GitHub push is not queue synchronization.",
    "No queue synchronization is performed.",
    "No queue migration is performed.",
    "No queue backfill is performed.",
    "No queue merge is performed.",
    "No conflict resolver is implemented.",
    # Dashboard display boundary
    "Dashboard displays state.",
    "Dashboard display is not dispatch.",
    "Dashboard display is not execution permission.",
    "Dashboard backend source is display data source.",
    "Dashboard source label is not execution permission.",
    "Dashboard source label is not shared write.",
    "Dashboard source switching requires separate future plan and Owner approval.",
    "No Dashboard runtime change is implemented in v0.8.0-A.",
    "No Dashboard backend source runtime is implemented in v0.8.0-A.",
    # Core runtime host relationship
    "Core runtime host is not selected.",
    "Core runtime host is not created.",
    "Runtime host selection is not loop activation.",
    "Runtime host activation is not Worker start by itself.",
    "Dashboard host is not runtime host by default.",
    "Replit remains observation station.",
    "Windows WSL remains local development environment.",
    "No systemd service is created.",
    "No daemon is created.",
    "No Docker deployment is created.",
    "No VPS deployment is created.",
    # source-of-truth and data boundary
    "No source-of-truth switch is performed.",
    "Current source of truth remains local to each environment.",
    "Future remote authority requires separate future plan and Owner approval.",
    "No queue DB change.",
    "No local queue data change.",
    "No Replit queue data change.",
    "No real queue DB read.",
    "No production queue data is created.",
    "No remote shared DB is created.",
    "No shared write is enabled.",
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
    "No personal memory migration is performed.",
    "GitHub must not store secrets.",
    "Replit must not receive production secrets.",
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
    "Network activation requires separate future plan and Owner approval.",
    # failure / rollback / audit boundary
    "Future loop actions must be auditable.",
    "Future loop actions must include rollback notes when external actions are involved.",
    "Future loop failures must not silently retry external actions.",
    "Future loop failures must not bypass Owner approval.",
    "Future loop failures must not write Google Sheets by default.",
    "Future loop failures must not call OpenClaw by default.",
    "Future loop failures must not start Worker by default.",
    "No loop failure handling runtime is implemented in v0.8.0-A.",
    # candidate MVP phases
    "Candidate MVP phase: docs-only loop plan.",
    "Candidate MVP phase: local dry-run loop preview.",
    "Candidate MVP phase: read-only Dashboard loop display.",
    "Candidate MVP phase: Owner review gate display.",
    "Candidate MVP phase: Decision audit confirmation.",
    "Candidate MVP phase: Result and Advice read-only display.",
    "Candidate MVP phase: Remote Blackboard read-only mirror after approval.",
    "Candidate MVP phases are planning notes only.",
    "No candidate MVP phase is implemented in v0.8.0-A.",
    "No candidate MVP phase is enabled in v0.8.0-A.",
    # disabled runtime list
    "Blackboard Loop runtime is disabled.",
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
    "No loop scheduler.",
    "No dispatch gate enabled.",
    "No autonomous execution.",
    "No Hermes activation.",
    "No Hermes blackboard mode.",
    "No Hermes runtime.",
    "No Hermes activation runtime.",
    "No Hermes memory store.",
    "No Hermes learning runtime.",
    "No all-conversation logging.",
    "No cleanup demo task.",
    "No cleanup apply.",
    "No --apply.",
    "No task deletion.",
    "No task archive.",
    "No POST.",
    "No live local queue write validation.",
    "No Worker execution.",
    "No OpenClaw call.",
    "No Hermes call.",
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
    "No Dashboard backend source runtime.",
    "No source switching runtime.",
    "No Core runtime host.",
    "No Worker runtime.",
    "No OpenClaw runtime.",
    "No systemd service.",
    "No daemon.",
    "No Docker deployment.",
    "No VPS deployment.",
    "No Mac mini deployment.",
    "No home server deployment.",
    "No queue synchronization.",
    "No queue migration.",
    "No queue backfill.",
    "No queue merge.",
    "No conflict resolver.",
    "No connector.",
    "No tag.",
    # validation summary
    "v0.8.0-A readiness: ALL PASS.",
    "v0.7.5-R readiness: ALL PASS.",
    "v0.7.5-E readiness: ALL PASS.",
    "v0.7.5-D readiness: ALL PASS.",
    "v0.7.5-C readiness: ALL PASS.",
    "v0.7.5-B readiness: ALL PASS.",
    "v0.7.5-A readiness: ALL PASS.",
    "v0.7.4-R readiness: ALL PASS.",
    "v0.7.4-F-R readiness: ALL PASS.",
    "v0.7.4-F readiness: ALL PASS.",
    "v0.7.4-F dry-run tool test: ALL PASS.",
    "v0.7.4-E check: ALL PASS.",
    "v0.7.4-D-R check: ALL PASS.",
    "v0.7.4-D readiness and helper test: ALL PASS.",
    "v0.7.4-C / B / A checks: ALL PASS.",
    "v0.7.3 checks: ALL PASS.",
    "prior F-line checks: ALL PASS.",
    "compileall scripts: PASS.",
    # safety grep summary
    "No real unsafe claim was found.",
    "No real secret was found.",
    "Readiness forbidden-pattern matches are benign.",
    # next recommended step
    "v0.8.0-B — Blackboard Loop Contract and State Boundary Plan",
    "v0.8.0-B must remain plan-first unless separately approved.",
    "v0.8.0-B must not implement Blackboard Loop runtime.",
    "v0.8.0-B must not activate Hermes.",
    "v0.8.0-B must not connect OpenClaw.",
    "v0.8.0-B must not start Worker.",
    "v0.8.0-B must not create production DB.",
    "v0.8.0-B must not create Remote Blackboard API runtime unless separately approved.",
    "v0.8.0-B must not migrate queue data.",
    "v0.8.0-B must not open shared write.",
    "v0.8.0-B must not write Google Sheets.",
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
]
scrubbed = doc
for phrase in SAFE_NEGATIONS:
    scrubbed = scrubbed.replace(phrase, "")

FORBIDDEN_SUBSTR = [
    "GOOGLE_SHEETS_ENABLED=true",
    "Blackboard Loop runtime created",
    "Blackboard Loop runtime implemented",
    "Blackboard Loop runtime enabled",
    "loop scheduler created",
    "loop scheduler enabled",
    "dispatch gate enabled",
    "autonomous execution enabled",
    "agent autonomy runtime created",
    "Owner approval bypassed",
    "Owner review bypassed",
    "Worker enabled",
    "OpenClaw connected",
    "Hermes connected",
    "Hermes activated",
    "Hermes activation enabled",
    "Hermes blackboard mode enabled",
    "Hermes runtime created",
    "Hermes activation runtime created",
    "Hermes memory store created",
    "Hermes learning runtime created",
    "Hermes called",
    "Hermes wrote Blackboard message",
    "Hermes wrote Advice Message",
    "Hermes drafted Task Message",
    "Hermes self-approved",
    "Hermes self-dispatched",
    "Hermes executed external action",
    "Hermes connector created",
    "Hermes credentials moved",
    "OpenClaw called",
    "OpenClaw runtime created",
    "OpenClaw connector created",
    "Worker started",
    "Worker runtime created",
    "Worker dispatch enabled",
    "Google Sheets live write enabled",
    "Google Sheets written",
    "cleanup applied",
    "demo task cleaned up",
    "tasks deleted",
    "tasks archived",
    "payload modified",
    "status modified",
    "queue DB modified",
    "local queue data modified",
    "Replit queue cleaned",
    "production DB cleaned",
    "remote shared DB cleaned",
    "shared DB created",
    "production DB created",
    "Remote Blackboard API runtime created",
    "Remote Blackboard API implemented",
    "Remote Blackboard API route added",
    "Remote Blackboard API read enabled",
    "Remote Blackboard API write enabled",
    "shared write enabled",
    "Blackboard shared write enabled",
    "Dashboard backend source runtime created",
    "source switching runtime created",
    "Core runtime host created",
    "runtime host selected",
    "runtime host provisioned",
    "systemd service created",
    "daemon created",
    "Docker deployment created",
    "VPS deployed",
    "Mac mini configured",
    "home server configured",
    "production process installed",
    "all-conversation logging enabled",
    "private conversation log created",
    "personal memory migration performed",
    "API route added",
    "FastAPI router added",
    "database client added",
    "migration added",
    "message schema migration performed",
    "queue migration performed",
    "queue data moved",
    "queue data copied",
    "queue data merged",
    "queue data backfilled",
    "queue data synchronized",
    "conflict resolver implemented",
    "source-of-truth switch performed",
    "remote blackboard authority enabled",
    "source configuration changed",
    "fallback write triggered",
    "cleanup apply approved",
    "apply_allowed = True",
    "apply_requested = True",
    "dry_run = False",
    "would_delete = True",
    "would_archive = True",
    "would_modify = True",
    "external_side_effects = True",
    "Owner approval granted cleanup apply",
    "POST to Replit Preview was sent",
    "POST to real queue was sent",
    "live queue write validation performed",
    "webhook created",
    "webhook receiver created",
    "connector created",
    "tag created",
    "QueueStore runtime behavior changed",
    "app/queue_store.py changed",
    "approval routes changed",
    "dashboard auth changed",
    "status transition changed",
    "runtime guard implemented",
    "existing transition result changed",
    "secrets read",
    "secrets copied",
    "secrets created",
    ".env created",
    "credentials moved",
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
    print(f"\nXX v0.8.0-A readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print(
        "\nv0.8.0-A Owner-supervised Blackboard Loop MVP Plan readiness: ALL PASS"
    )
    sys.exit(0)
