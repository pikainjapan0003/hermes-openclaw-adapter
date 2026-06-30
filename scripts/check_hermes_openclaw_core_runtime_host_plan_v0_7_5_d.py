"""v0.7.5-D readiness check: Core Runtime Host Plan (plan-first).

Plan-first / boundary verification. Checks that the v0.7.5-D plan document exists and
contains the required sections (1-31), the current-master marker, the v0.7.5-D plan-first
markers, the problem statement markers, the core runtime host definition markers, the
runtime-host-is-not-Dashboard-host markers, the GitHub / WSL / Replit / runtime host
boundary markers, the candidate host option markers, the Replit boundary markers, the
Windows WSL boundary markers, the VPS / Mac mini / home server boundary markers, the
Worker / OpenClaw / Hermes boundary markers, the Remote Blackboard API host boundary
markers, the Dashboard backend source relationship markers, the queue and data boundary
markers, the secrets and credentials boundary markers, the network / webhook / connector
boundary markers, the deployment and process boundary markers, the Owner approval /
activation boundary markers, the failure / rollback / audit boundary markers, the
source-of-truth boundary markers, the Blackboard message compatibility markers, the
current safe posture markers, the validation summary markers, the safety grep summary
markers, and the next recommended step — and that it asserts no unsafe "implemented /
created / added / selected / provisioned / deployed / configured / installed / migrated /
moved / copied / read / started / connected / enabled / applied / called / written /
changed" claim and contains no secret.

The document is allowed to contain safe negations; those that literally embed a
forbidden substring are scrubbed before the forbidden scan so they are not mis-flagged.

This script only reads the plan document. It does NOT read .env, credentials, tokens, or
secrets, makes no network call, imports no app logic (no app.main, no QueueStore), adds
no API route / router / runtime host client / database client / migration, creates no
production / shared DB, provisions no host, deploys nothing, syncs no queue, opens no
shared write, starts no Worker, and calls no OpenClaw / Hermes / Google Sheets.
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
    / "HERMES_OPENCLAW_CORE_RUNTIME_HOST_PLAN_V0_7_5_D.md"
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
ok("v0.7.5-D plan doc 存在") if DOC_PATH.exists() else xx("v0.7.5-D plan doc 存在")
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
    "4. Relationship to v0.7.5-A / B / C",
    "5. Problem statement",
    "6. Core runtime host definition",
    "7. Runtime host is not Dashboard host",
    "8. GitHub / WSL / Replit / runtime host boundary",
    "9. Candidate host options",
    "10. Replit boundary",
    "11. Windows WSL boundary",
    "12. VPS / Mac mini / home server boundary",
    "13. Worker host boundary",
    "14. OpenClaw host boundary",
    "15. Hermes host boundary",
    "16. Remote Blackboard API host boundary",
    "17. Dashboard backend source relationship",
    "18. Queue and data boundary",
    "19. Secrets and credentials boundary",
    "20. Network / webhook / connector boundary",
    "21. Deployment and process boundary",
    "22. Owner approval and activation boundary",
    "23. Failure / rollback / audit boundary",
    "24. Source-of-truth boundary",
    "25. Blackboard message compatibility",
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
    "v0.7.5-D",
    "Core Runtime Host Plan",
    # current master
    "HEAD = origin/master = 7b5337cc88354626b41e414ea70d5a71189c9d76",
    "docs: plan dashboard backend source",
    # v0.7.5-D plan-first markers
    "v0.7.5-D Core Runtime Host Plan is plan-first.",
    "v0.7.5-D does not create Core runtime host.",
    "v0.7.5-D does not deploy VPS.",
    "v0.7.5-D does not deploy Mac mini.",
    "v0.7.5-D does not deploy home server.",
    "v0.7.5-D does not create systemd service.",
    "v0.7.5-D does not create daemon.",
    "v0.7.5-D does not create Docker deployment.",
    "v0.7.5-D does not implement Worker runtime.",
    "v0.7.5-D does not implement OpenClaw runtime.",
    "v0.7.5-D does not implement Hermes runtime.",
    "v0.7.5-D does not implement Remote Blackboard API runtime.",
    "v0.7.5-D does not create production DB.",
    "v0.7.5-D does not create shared DB.",
    "v0.7.5-D does not create remote shared DB.",
    "v0.7.5-D does not migrate queue data.",
    "v0.7.5-D does not sync local queue and remote queue.",
    "v0.7.5-D does not open shared write.",
    "v0.7.5-D does not start Worker.",
    "v0.7.5-D does not call OpenClaw.",
    "v0.7.5-D does not call Hermes.",
    "v0.7.5-D does not write Google Sheets.",
    "v0.7.5-D does not create webhook.",
    # problem statement markers
    "Core runtime host is not yet selected.",
    "Dashboard host and core runtime host may be separate.",
    "Replit is a remote observation station, not production executor.",
    "GitHub is clean source of code and docs, not runtime host.",
    "Windows WSL is primary local development environment, not always-on production runtime.",
    "Future Worker / OpenClaw / Hermes execution requires a controlled runtime host.",
    "Runtime host activation requires a separate future plan and Owner approval.",
    "Planning a host is not deploying a host.",
    # core runtime host definition markers
    "Core runtime host means the future machine or service that may run long-lived runtime processes.",
    "Core runtime host may eventually run Worker.",
    "Core runtime host may eventually coordinate OpenClaw.",
    "Core runtime host may eventually coordinate Hermes.",
    "Core runtime host may eventually read or write Remote Blackboard API after approval.",
    "Core runtime host is not implemented in v0.7.5-D.",
    "Core runtime host is not Dashboard by default.",
    "Core runtime host is not GitHub.",
    "Core runtime host must preserve Owner approval.",
    "Core runtime host must preserve audit trail.",
    "Core runtime host must preserve decision and dispatch separation.",
    # runtime host is not Dashboard host markers
    "Dashboard host displays state.",
    "Runtime host executes long-lived processes only after approval.",
    "Dashboard update is not runtime deployment.",
    "Dashboard restart is not Worker start.",
    "Dashboard backend source selection is not runtime host activation.",
    "Dashboard host must not imply execution permission.",
    "Runtime host must not be activated by Dashboard display.",
    "No Dashboard runtime host coupling is implemented in v0.7.5-D.",
    # GitHub / WSL / Replit / runtime host boundary markers
    "GitHub remains clean source of code and docs, not queue DB and not secrets store.",
    "Windows WSL remains primary local development environment.",
    "Replit remains remote observation station / Preview Dashboard.",
    "Future runtime host is separate from GitHub.",
    "Future runtime host is separate from Replit Preview unless separately approved.",
    "Future runtime host is separate from Dashboard display.",
    "No host role is changed in v0.7.5-D.",
    # candidate host option markers
    "Candidate runtime host option: VPS.",
    "Candidate runtime host option: Mac mini.",
    "Candidate runtime host option: home server.",
    "Candidate runtime host option: Windows WSL local development only.",
    "Candidate runtime host option: Replit Preview observation only.",
    "Candidate runtime host options are planning notes only.",
    "No candidate runtime host is provisioned in v0.7.5-D.",
    "No candidate runtime host is selected in v0.7.5-D.",
    # Replit boundary markers
    "Replit remains Preview / observation station.",
    "Replit must not become production executor in v0.7.5-D.",
    "Replit must not start Worker in v0.7.5-D.",
    "Replit must not receive production secrets in v0.7.5-D.",
    "Replit local queue remains separate.",
    "Replit Dashboard update remains git pull plus Dashboard restart only.",
    "No Replit runtime deployment is performed in v0.7.5-D.",
    # Windows WSL boundary markers
    "Windows WSL remains primary local development environment.",
    "Windows WSL may run local development checks.",
    "Windows WSL local queue remains local.",
    "Windows WSL is not automatically always-on production runtime.",
    "Windows WSL does not become Core runtime host in v0.7.5-D.",
    "No WSL runtime deployment is performed in v0.7.5-D.",
    # VPS / Mac mini / home server boundary markers
    "VPS is a candidate runtime host only.",
    "Mac mini is a candidate runtime host only.",
    "Home server is a candidate runtime host only.",
    "No VPS is provisioned in v0.7.5-D.",
    "No Mac mini is configured in v0.7.5-D.",
    "No home server is configured in v0.7.5-D.",
    "No SSH setup is performed in v0.7.5-D.",
    "No production process is installed in v0.7.5-D.",
    # Worker / OpenClaw / Hermes boundary markers
    "Worker remains OFF.",
    "Worker host is not selected in v0.7.5-D.",
    "Worker runtime is not implemented in v0.7.5-D.",
    "Worker is not started in v0.7.5-D.",
    "OpenClaw remains Not Connected.",
    "OpenClaw host is not selected in v0.7.5-D.",
    "OpenClaw runtime is not implemented in v0.7.5-D.",
    "OpenClaw is not called in v0.7.5-D.",
    "Hermes remains Not Connected.",
    "Hermes host is not selected in v0.7.5-D.",
    "Hermes runtime is not implemented in v0.7.5-D.",
    "Hermes is not called in v0.7.5-D.",
    # Remote Blackboard API host boundary markers
    "Remote Blackboard API runtime is not implemented in v0.7.5-D.",
    "Remote Blackboard API host is not selected in v0.7.5-D.",
    "Remote Blackboard API host is not provisioned in v0.7.5-D.",
    "Remote Blackboard API deployment requires separate future plan and Owner approval.",
    "Remote Blackboard API must preserve Owner review.",
    "Remote Blackboard API must preserve audit trail.",
    "Remote Blackboard API must preserve decision and dispatch separation.",
    # Dashboard backend source relationship markers
    "Dashboard backend source plan does not activate runtime host.",
    "Dashboard source label is not execution permission.",
    "Dashboard read is not Worker dispatch.",
    "Dashboard read is not OpenClaw call.",
    "Dashboard read is not Hermes action.",
    "Dashboard source switching is not runtime host activation.",
    "No Dashboard backend source runtime is implemented in v0.7.5-D.",
    # queue and data boundary markers
    "No queue synchronization is performed.",
    "No queue migration is performed.",
    "No local queue data is moved.",
    "No Replit queue data is moved.",
    "No production queue data is created.",
    "No remote shared DB is created.",
    "No data backfill is performed.",
    "No queue merge is performed.",
    "No conflict resolver is implemented.",
    "No source-of-truth switch is performed.",
    "Runtime host planning is not queue migration approval.",
    "Runtime host planning is not shared write approval.",
    # secrets and credentials boundary markers
    "No secrets are read in v0.7.5-D.",
    "No secrets are copied in v0.7.5-D.",
    "No secrets are created in v0.7.5-D.",
    "No .env file is created in v0.7.5-D.",
    "No credentials are moved to any host in v0.7.5-D.",
    "GitHub must not store secrets.",
    "Runtime host secrets require separate future plan and Owner approval.",
    # network / webhook / connector boundary markers
    "No webhook is created.",
    "No webhook receiver is created.",
    "No connector is created.",
    "No external network call is added.",
    "No inbound listener is added.",
    "No outbound integration is added.",
    "No port exposure is configured.",
    "Network activation requires separate future plan and Owner approval.",
    # deployment and process boundary markers
    "No systemd service is created.",
    "No daemon is created.",
    "No Docker deployment is created.",
    "No process manager is configured.",
    "No cron job is created.",
    "No background worker is started.",
    "No long-lived process is started.",
    "No production deployment is performed.",
    "Deployment requires separate future plan and Owner approval.",
    # Owner approval and activation boundary markers
    "Owner approval is required before selecting runtime host.",
    "Owner approval is required before provisioning runtime host.",
    "Owner approval is required before deploying runtime process.",
    "Owner approval is required before starting Worker.",
    "Owner approval is required before connecting OpenClaw.",
    "Owner approval is required before connecting Hermes.",
    "Owner approval is required before using production secrets.",
    "Owner approval is required before creating Remote Blackboard API runtime.",
    "Owner approval is required before opening shared write.",
    "Plan approval is not runtime approval.",
    "Plan approval is not deployment approval.",
    "Plan approval is not Worker start approval.",
    "Plan approval is not OpenClaw connection approval.",
    "Plan approval is not Hermes activation approval.",
    # failure / rollback / audit boundary markers
    "Future runtime host actions must be auditable.",
    "Future runtime host actions must include rollback notes.",
    "Future runtime host failures must not silently retry external actions.",
    "Future runtime host failures must not bypass Owner approval.",
    "Future runtime host failures must not write Google Sheets by default.",
    "Future runtime host failures must not call OpenClaw or Hermes by default.",
    "No runtime failure handling is implemented in v0.7.5-D.",
    # source-of-truth boundary markers
    "Runtime host selection is not source-of-truth switch.",
    "Runtime host activation is not queue migration by itself.",
    "Current source of truth remains local to each environment.",
    "Future remote authority requires separate future plan and Owner approval.",
    "GitHub remains clean source of code and docs, not queue DB.",
    # blackboard message compatibility markers
    "Task Message",
    "Decision Message",
    "Result Message",
    "Advice Message",
    "Decision Message is audit record, not command.",
    "approve is not execute.",
    "Writing a task to Blackboard is not Worker dispatch.",
    "Entering Blackboard mode is not execution permission.",
    "Result Message is not next dispatch permission.",
    "Advice Message is not automatic follow-up execution.",
    # current safe posture markers
    "Dashboard read-only / controlled local route behavior.",
    "Worker OFF.",
    "OpenClaw Not Connected.",
    "Hermes Not Connected.",
    "Google Sheets Disabled.",
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
    "No Hermes runtime.",
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
    "v0.7.5-E — Hermes Activation with Remote Blackboard Boundary",
    "v0.7.5-E must remain plan-first unless separately approved.",
    "v0.7.5-E must not activate Hermes.",
    "v0.7.5-E must not connect OpenClaw.",
    "v0.7.5-E must not start Worker.",
    "v0.7.5-E must not create production DB.",
    "v0.7.5-E must not create Remote Blackboard API runtime.",
    "v0.7.5-E must not migrate queue data.",
    "v0.7.5-E must not open shared write.",
    "v0.7.5-E must not write Google Sheets.",
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
    "No source-of-truth switch is performed",
    "No conflict resolver is implemented",
    "does not implement Worker runtime",
    "does not implement OpenClaw runtime",
    "does not implement Hermes runtime",
    "does not implement Remote Blackboard API runtime",
    "v0.7.5-E must not create Remote Blackboard API runtime",
    "v0.7.5-E must not create production DB",
    "v0.7.5-D must not create Remote Blackboard API runtime",
]
scrubbed = doc
for phrase in SAFE_NEGATIONS:
    scrubbed = scrubbed.replace(phrase, "")

FORBIDDEN_SUBSTR = [
    "GOOGLE_SHEETS_ENABLED=true",
    "Worker enabled",
    "OpenClaw connected",
    "Hermes connected",
    "Google Sheets live write enabled",
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
    "Dashboard backend source runtime created",
    "source switching runtime created",
    "Core runtime host created",
    "runtime host selected",
    "runtime host provisioned",
    "Worker runtime created",
    "Worker runtime implemented",
    "OpenClaw runtime created",
    "OpenClaw runtime implemented",
    "Hermes runtime created",
    "Hermes runtime implemented",
    "systemd service created",
    "daemon created",
    "Docker deployment created",
    "VPS deployed",
    "Mac mini configured",
    "home server configured",
    "SSH setup performed",
    "production process installed",
    "process manager configured",
    "cron job created",
    "background worker started",
    "long-lived process started",
    "production deployment performed",
    "production secrets copied",
    "production secrets added",
    ".env created",
    "secrets copied",
    "secrets read",
    "credentials moved",
    "port exposure configured",
    "inbound listener added",
    "outbound integration added",
    "external network call added",
    "webhook created",
    "webhook receiver created",
    "connector created",
    "Remote Blackboard API implemented",
    "Remote Blackboard API route added",
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
    "shared write enabled",
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
    "Worker started",
    "OpenClaw called",
    "Hermes called",
    "Google Sheets written",
    "tag created",
    "QueueStore runtime behavior changed",
    "app/queue_store.py changed",
    "approval routes changed",
    "dashboard auth changed",
    "status transition changed",
    "runtime guard implemented",
    "existing transition result changed",
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
    print(f"\nXX v0.7.5-D readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print(
        "\nv0.7.5-D Core Runtime Host Plan readiness: ALL PASS"
    )
    sys.exit(0)
