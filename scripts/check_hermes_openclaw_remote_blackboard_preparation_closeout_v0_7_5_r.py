"""v0.7.5-R readiness check: Remote Blackboard Preparation Closeout (docs-only).

Docs-only closeout / boundary verification. Checks that the v0.7.5-R closeout document
exists and contains the required sections (1-28), the current-master marker, the v0.7.5-R
docs-only closeout markers, the v0.7.5 line summary markers, the per-plan closeout markers
(A/B/C/D/E), the Remote Blackboard API boundary markers, the local queue vs remote
blackboard boundary markers, the Dashboard backend source boundary markers, the Core
runtime host boundary markers, the Hermes activation boundary markers, the Blackboard mode
boundary markers, the Owner approval / activation boundary markers, the Blackboard message
compatibility markers, the GitHub / WSL / Replit / runtime host boundary markers, the
queue / data / source-of-truth boundary markers, the Worker / OpenClaw / Hermes / Google
Sheets boundary markers, the secrets / privacy / memory boundary markers, the network /
webhook / connector / deployment boundary markers, the current safe posture markers, the
validation summary markers, the safety grep summary markers, and the next recommended step
— and that it asserts no unsafe "implemented / created / added / enabled / activated /
connected / called / started / written / moved / migrated / changed" claim and contains no
secret.

The document is allowed to contain safe negations; those that literally embed a
forbidden substring are scrubbed before the forbidden scan so they are not mis-flagged.

This script only reads the closeout document. It does NOT read .env, credentials, tokens,
or secrets, makes no network call, imports no app logic (no app.main, no QueueStore), adds
no API route / router / database client / migration, creates no production / shared DB,
activates no Hermes, connects no OpenClaw, starts no Worker, opens no shared write, and
writes no Google Sheets.
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
    / "HERMES_OPENCLAW_REMOTE_BLACKBOARD_PREPARATION_CLOSEOUT_V0_7_5_R.md"
)


def ok(label):
    PASS.append(label)
    print(f"  ok : {label}")


def xx(label):
    FAIL.append(label)
    print(f"  XX : {label}")


# ---------------------------------------------------------------------------
# [1] closeout 文件存在
# ---------------------------------------------------------------------------
print("[1] closeout 文件存在")
ok("v0.7.5-R closeout doc 存在") if DOC_PATH.exists() else xx("v0.7.5-R closeout doc 存在")
if not DOC_PATH.exists():
    print("\nXX closeout doc 不存在，無法繼續")
    sys.exit(1)

doc = DOC_PATH.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# [2] 必須包含的章節（1-28）
# ---------------------------------------------------------------------------
print("[2] 必須包含的章節")
REQUIRED_SECTIONS = [
    "1. Purpose",
    "2. Current master",
    "3. Scope",
    "4. v0.7.5 line summary",
    "5. v0.7.5-A Remote Blackboard API Plan closeout",
    "6. v0.7.5-B Local vs Remote Queue Boundary closeout",
    "7. v0.7.5-C Dashboard Backend Source Plan closeout",
    "8. v0.7.5-D Core Runtime Host Plan closeout",
    "9. v0.7.5-E Hermes Activation with Remote Blackboard Boundary closeout",
    "10. Remote Blackboard API boundary",
    "11. Local queue vs remote blackboard boundary",
    "12. Dashboard backend source boundary",
    "13. Core runtime host boundary",
    "14. Hermes activation boundary",
    "15. Blackboard mode boundary",
    "16. Owner approval and activation boundary",
    "17. Blackboard message compatibility",
    "18. GitHub / WSL / Replit / runtime host boundary",
    "19. Queue / data / source-of-truth boundary",
    "20. Worker / OpenClaw / Hermes / Google Sheets boundary",
    "21. Secrets / privacy / memory boundary",
    "22. Network / webhook / connector / deployment boundary",
    "23. Current safe system posture",
    "24. Validation summary",
    "25. Safety grep summary",
    "26. Non-goals",
    "27. Acceptance criteria",
    "28. Next recommended step",
]
for section in REQUIRED_SECTIONS:
    ok(f"doc 含章節「{section}」") if section in doc else xx(f"doc 含章節「{section}」")

# ---------------------------------------------------------------------------
# [3] 必須包含的 markers
# ---------------------------------------------------------------------------
print("[3] 必須包含的 markers")
REQUIRED = [
    # version
    "v0.7.5-R",
    "Remote Blackboard Preparation Closeout",
    # current master
    "HEAD = origin/master = 2adea1a42c49f125c75e351b50a3df79b145bdd1",
    "docs: plan hermes activation blackboard boundary",
    # v0.7.5-R docs-only closeout markers
    "v0.7.5-R Remote Blackboard Preparation Closeout is docs-only.",
    "v0.7.5-R closes the v0.7.5 Remote Blackboard Preparation line.",
    "v0.7.5-R does not implement Remote Blackboard API runtime.",
    "v0.7.5-R does not create production DB.",
    "v0.7.5-R does not create shared DB.",
    "v0.7.5-R does not create remote shared DB.",
    "v0.7.5-R does not migrate queue data.",
    "v0.7.5-R does not sync local queue and remote queue.",
    "v0.7.5-R does not open shared write.",
    "v0.7.5-R does not create Dashboard backend source runtime.",
    "v0.7.5-R does not create source switching runtime.",
    "v0.7.5-R does not create Core runtime host.",
    "v0.7.5-R does not activate Hermes.",
    "v0.7.5-R does not connect Hermes.",
    "v0.7.5-R does not connect OpenClaw.",
    "v0.7.5-R does not start Worker.",
    "v0.7.5-R does not write Google Sheets.",
    "v0.7.5-R does not create webhook.",
    # v0.7.5 line summary markers
    "v0.7.5-A Remote Blackboard API Plan is complete.",
    "v0.7.5-B Local vs Remote Queue Boundary is complete.",
    "v0.7.5-C Dashboard Backend Source Plan is complete.",
    "v0.7.5-D Core Runtime Host Plan is complete.",
    "v0.7.5-E Hermes Activation with Remote Blackboard Boundary is complete.",
    "v0.7.5 Remote Blackboard Preparation line is complete.",
    # v0.7.5-A closeout markers
    "v0.7.5-A planned Remote Blackboard API boundaries.",
    "v0.7.5-A did not implement Remote Blackboard API runtime.",
    "v0.7.5-A did not create production DB.",
    "v0.7.5-A did not create shared DB.",
    "v0.7.5-A did not migrate queue data.",
    "v0.7.5-A did not open shared write.",
    "v0.7.5-A preserved Owner review.",
    "v0.7.5-A preserved audit trail.",
    "v0.7.5-A preserved decision and dispatch separation.",
    # v0.7.5-B closeout markers
    "v0.7.5-B defined Local Queue is not Remote Blackboard.",
    "v0.7.5-B defined WSL local queue is not Replit local queue.",
    "v0.7.5-B defined Dashboard update is not queue synchronization.",
    "v0.7.5-B defined GitHub push is not queue synchronization.",
    "v0.7.5-B did not migrate queue data.",
    "v0.7.5-B did not sync queue data.",
    "v0.7.5-B did not backfill queue data.",
    "v0.7.5-B did not merge queue data.",
    "v0.7.5-B did not implement conflict resolver.",
    # v0.7.5-C closeout markers
    "v0.7.5-C defined Dashboard backend source as display data source.",
    "v0.7.5-C defined Dashboard backend source is not Worker dispatch.",
    "v0.7.5-C defined source label is not execution permission.",
    "v0.7.5-C defined source label is not shared write.",
    "v0.7.5-C defined source label is not queue synchronization.",
    "v0.7.5-C defined source switching requires separate future plan and Owner approval.",
    "v0.7.5-C did not create Dashboard backend source runtime.",
    "v0.7.5-C did not create source switching runtime.",
    "v0.7.5-C did not create remote backend client.",
    # v0.7.5-D closeout markers
    "v0.7.5-D defined Dashboard host is not runtime host.",
    "v0.7.5-D defined Replit is observation station, not production executor.",
    "v0.7.5-D defined Windows WSL is local development, not automatically always-on runtime.",
    "v0.7.5-D defined planning a host is not deploying a host.",
    "v0.7.5-D defined runtime host activation requires separate future plan and Owner approval.",
    "v0.7.5-D did not create Core runtime host.",
    "v0.7.5-D did not create Worker runtime.",
    "v0.7.5-D did not create OpenClaw runtime.",
    "v0.7.5-D did not create Hermes runtime.",
    "v0.7.5-D did not create systemd / daemon / Docker / VPS / Mac mini / home server deployment.",
    # v0.7.5-E closeout markers
    "v0.7.5-E defined Hermes remains Not Connected.",
    "v0.7.5-E defined Blackboard mode is optional.",
    "v0.7.5-E defined entering Blackboard mode is not execution permission.",
    "v0.7.5-E defined Hermes advice is not command.",
    "v0.7.5-E defined Hermes draft is not dispatch.",
    "v0.7.5-E defined Owner remains final approval authority.",
    "v0.7.5-E defined Hermes activation requires separate future plan and Owner approval.",
    "v0.7.5-E did not activate Hermes.",
    "v0.7.5-E did not connect Hermes.",
    "v0.7.5-E did not connect OpenClaw.",
    "v0.7.5-E did not start Worker.",
    "v0.7.5-E did not create Hermes memory store.",
    "v0.7.5-E did not enable all-conversation logging.",
    # Remote Blackboard API boundary markers
    "Remote Blackboard API remains planning only.",
    "Remote Blackboard API runtime is not implemented.",
    "Remote Blackboard API route is not added.",
    "Remote Blackboard API read is not enabled.",
    "Remote Blackboard API write is not enabled.",
    "Remote Blackboard API is not production DB.",
    "Remote Blackboard API is not execution dispatcher.",
    "Remote Blackboard API requires separate future plan and Owner approval before runtime.",
    # Local queue vs remote blackboard boundary markers
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
    # Dashboard backend source boundary markers
    "Dashboard backend source means display data source.",
    "Dashboard backend source is not Worker dispatch.",
    "Dashboard backend source is not OpenClaw call.",
    "Dashboard backend source is not Hermes action.",
    "Dashboard source label is not execution permission.",
    "Dashboard source label is not shared write.",
    "Dashboard source label is not queue synchronization.",
    "Dashboard source switching is not source-of-truth switch.",
    "Dashboard source switching requires separate future plan and Owner approval.",
    "No Dashboard backend source runtime is implemented.",
    "No source switching runtime is implemented.",
    # Core runtime host boundary markers
    "Core runtime host is not selected.",
    "Core runtime host is not created.",
    "Runtime host is not Dashboard host by default.",
    "Dashboard update is not runtime deployment.",
    "Dashboard restart is not Worker start.",
    "Replit remains observation station.",
    "Windows WSL remains local development environment.",
    "Runtime host activation requires separate future plan and Owner approval.",
    "No Worker runtime is created.",
    "No OpenClaw runtime is created.",
    "No Hermes runtime is created.",
    "No systemd service is created.",
    "No daemon is created.",
    "No Docker deployment is created.",
    # Hermes activation boundary markers
    "Hermes remains Not Connected.",
    "Hermes is not activated.",
    "Hermes is not called.",
    "Hermes runtime is not created.",
    "Hermes activation runtime is not created.",
    "Hermes memory store is not created.",
    "Hermes learning runtime is not created.",
    "Blackboard mode is optional.",
    "Owner decides whether to enter Blackboard mode.",
    "Not every conversation enters Blackboard mode.",
    "Not every conversation is logged to Blackboard.",
    "Entering Blackboard mode is not execution permission.",
    "Hermes advice is not command.",
    "Hermes advice is not Worker dispatch.",
    "Hermes advice is not OpenClaw call.",
    "Hermes draft is not queue write by itself.",
    "Hermes draft requires Owner review.",
    "Owner remains final approval authority.",
    # Blackboard mode boundary markers
    "Entering normal chat is not Blackboard mode.",
    "Hermes blackboard mode is not enabled.",
    "Blackboard shared write is not enabled.",
    # Owner approval and activation boundary markers
    "Owner approval is required before Remote Blackboard API runtime.",
    "Owner approval is required before shared DB.",
    "Owner approval is required before shared write.",
    "Owner approval is required before queue synchronization.",
    "Owner approval is required before queue migration.",
    "Owner approval is required before source-of-truth switch.",
    "Owner approval is required before Dashboard source switching runtime.",
    "Owner approval is required before Core runtime host selection.",
    "Owner approval is required before runtime host deployment.",
    "Owner approval is required before Hermes activation.",
    "Owner approval is required before connecting Hermes to Remote Blackboard.",
    "Owner approval is required before connecting OpenClaw.",
    "Owner approval is required before starting Worker.",
    "Plan approval is not runtime approval.",
    "Plan approval is not migration approval.",
    "Plan approval is not shared write approval.",
    "Plan approval is not Hermes activation approval.",
    # Blackboard message compatibility markers
    "Task Message",
    "Decision Message",
    "Result Message",
    "Advice Message",
    "Decision Message is audit record, not command.",
    "approve is not execute.",
    "Writing a task to Blackboard is not Worker dispatch.",
    "Result Message is not next dispatch permission.",
    "Advice Message is not automatic follow-up execution.",
    "Hermes Advice Message is advisory.",
    "Hermes Task Message draft requires Owner review.",
    # GitHub / WSL / Replit / runtime host boundary markers
    "GitHub remains clean source of code and docs, not queue DB and not secrets store.",
    "Windows WSL remains primary local development environment.",
    "Replit remains remote observation station / Preview Dashboard.",
    "Dashboard update remains git pull plus Dashboard restart only.",
    "Dashboard update does not sync queue.",
    "Dashboard update does not start Worker.",
    "Dashboard update does not connect OpenClaw.",
    "Dashboard update does not activate Hermes.",
    "Future runtime host remains separate until separately approved.",
    "No host role is changed in v0.7.5-R.",
    # queue / data / source-of-truth boundary markers
    "No queue DB change.",
    "No local queue data change.",
    "No Replit queue data change.",
    "No real queue DB read.",
    "No production queue data is created.",
    "No remote shared DB is created.",
    "No data backfill is performed.",
    "No source-of-truth switch is performed.",
    "Current source of truth remains local to each environment.",
    "Future remote authority requires separate future plan and Owner approval.",
    # Worker / OpenClaw / Hermes / Google Sheets boundary markers
    "Worker OFF.",
    "OpenClaw Not Connected.",
    "Hermes Not Connected.",
    "Google Sheets Disabled.",
    "No Worker execution.",
    "No Worker started.",
    "No Worker dispatch enabled.",
    "No OpenClaw call.",
    "No OpenClaw connected.",
    "No Hermes call.",
    "No Hermes activated.",
    "No Google Sheets write.",
    "No Google Sheets live write enabled.",
    # secrets / privacy / memory boundary markers
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
    # network / webhook / connector / deployment boundary markers
    "No webhook is created.",
    "No webhook receiver is created.",
    "No connector is created.",
    "No external network call is added.",
    "No inbound listener is added.",
    "No outbound integration is added.",
    "No port exposure is configured.",
    "No VPS deployment is created.",
    "No Mac mini deployment is created.",
    "No home server deployment is created.",
    "No production deployment is performed.",
    # current safe posture markers
    "Dashboard read-only / controlled local route behavior.",
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
    # validation summary markers
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
    # safety grep summary markers
    "No real unsafe claim was found.",
    "No real secret was found.",
    "Readiness forbidden-pattern matches are benign.",
    # next recommended step
    "v0.8.0-A — Owner-supervised Blackboard Loop MVP Plan",
    "v0.8.0-A must remain plan-first unless separately approved.",
    "v0.8.0-A must not activate Hermes.",
    "v0.8.0-A must not connect OpenClaw.",
    "v0.8.0-A must not start Worker.",
    "v0.8.0-A must not create production DB.",
    "v0.8.0-A must not create Remote Blackboard API runtime unless separately approved.",
    "v0.8.0-A must not migrate queue data.",
    "v0.8.0-A must not open shared write.",
    "v0.8.0-A must not write Google Sheets.",
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
    "No Worker started.",
    "No Worker dispatch enabled.",
    "No OpenClaw connected.",
    "No Hermes activated.",
    "No Google Sheets live write enabled.",
    "No source-of-truth switch is performed",
    "No conflict resolver is implemented",
    "did not implement Remote Blackboard API runtime",
    "does not implement Remote Blackboard API runtime",
    "must not create Remote Blackboard API runtime unless separately approved",
    "must not create production DB",
]
scrubbed = doc
for phrase in SAFE_NEGATIONS:
    scrubbed = scrubbed.replace(phrase, "")

FORBIDDEN_SUBSTR = [
    "GOOGLE_SHEETS_ENABLED=true",
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
    print(f"\nXX v0.7.5-R readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print(
        "\nv0.7.5-R Remote Blackboard Preparation Closeout readiness: ALL PASS"
    )
    sys.exit(0)
