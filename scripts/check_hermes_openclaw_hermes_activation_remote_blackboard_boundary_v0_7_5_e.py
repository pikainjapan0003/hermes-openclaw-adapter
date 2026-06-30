"""v0.7.5-E readiness check: Hermes Activation with Remote Blackboard Boundary (plan-first).

Plan-first / boundary verification. Checks that the v0.7.5-E plan document exists and
contains the required sections (1-33), the current-master marker, the v0.7.5-E plan-first
markers, the problem statement markers, the Hermes activation definition markers, the
Hermes-remains-inactive boundary markers, the Remote Blackboard mode definition markers,
the Blackboard-mode-optional markers, the entering-Blackboard-mode-is-not-execution-
permission markers, the Hermes advice / task draft / decision boundary markers, the Owner
approval / activation boundary markers, the OpenClaw / Worker / Hermes separation boundary
markers, the Remote Blackboard API relationship markers, the memory and learning boundary
markers, the privacy and conversation logging boundary markers, the autonomy and
delegation boundary markers, the queue and data boundary markers, the secrets and
credentials boundary markers, the network / webhook / connector boundary markers, the
runtime host relationship markers, the failure / rollback / audit boundary markers, the
source-of-truth boundary markers, the Blackboard message compatibility markers, the
candidate future Hermes activation mode markers, the current safe posture markers, the
validation summary markers, the safety grep summary markers, and the next recommended step
— and that it asserts no unsafe "activated / connected / created / implemented / enabled /
called / started / written / dispatched / self-approved / moved / migrated / changed"
claim and contains no secret.

The document is allowed to contain safe negations; those that literally embed a
forbidden substring are scrubbed before the forbidden scan so they are not mis-flagged.

This script only reads the plan document. It does NOT read .env, credentials, tokens, or
secrets, makes no network call, imports no app logic (no app.main, no QueueStore), adds
no API route / router / Hermes client / OpenClaw client / database client / migration,
creates no production / shared DB, activates no Hermes, connects no OpenClaw, starts no
Worker, opens no shared write, and writes no Google Sheets.
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
    / "HERMES_OPENCLAW_HERMES_ACTIVATION_REMOTE_BLACKBOARD_BOUNDARY_V0_7_5_E.md"
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
ok("v0.7.5-E plan doc 存在") if DOC_PATH.exists() else xx("v0.7.5-E plan doc 存在")
if not DOC_PATH.exists():
    print("\nXX plan doc 不存在，無法繼續")
    sys.exit(1)

doc = DOC_PATH.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# [2] 必須包含的章節（1-33）
# ---------------------------------------------------------------------------
print("[2] 必須包含的章節")
REQUIRED_SECTIONS = [
    "1. Purpose",
    "2. Current master",
    "3. Scope",
    "4. Relationship to v0.7.5-A / B / C / D",
    "5. Problem statement",
    "6. Hermes activation definition",
    "7. Hermes remains inactive boundary",
    "8. Remote Blackboard mode definition",
    "9. Blackboard mode is optional",
    "10. Entering Blackboard mode is not execution permission",
    "11. Hermes advice boundary",
    "12. Hermes task draft boundary",
    "13. Hermes decision boundary",
    "14. Owner approval and activation boundary",
    "15. OpenClaw / Worker / Hermes separation boundary",
    "16. Remote Blackboard API relationship",
    "17. Memory and learning boundary",
    "18. Privacy and conversation logging boundary",
    "19. Autonomy and delegation boundary",
    "20. Queue and data boundary",
    "21. Secrets and credentials boundary",
    "22. Network / webhook / connector boundary",
    "23. Runtime host relationship",
    "24. Failure / rollback / audit boundary",
    "25. Source-of-truth boundary",
    "26. Blackboard message compatibility",
    "27. Candidate future Hermes activation modes",
    "28. Current safe system posture",
    "29. Validation summary",
    "30. Safety grep summary",
    "31. Non-goals",
    "32. Acceptance criteria",
    "33. Next recommended step",
]
for section in REQUIRED_SECTIONS:
    ok(f"doc 含章節「{section}」") if section in doc else xx(f"doc 含章節「{section}」")

# ---------------------------------------------------------------------------
# [3] 必須包含的 markers
# ---------------------------------------------------------------------------
print("[3] 必須包含的 markers")
REQUIRED = [
    # version
    "v0.7.5-E",
    "Hermes Activation with Remote Blackboard Boundary",
    # current master
    "HEAD = origin/master = c871ecea5dfc1f83c492fdc2415f1c2dffa41cb1",
    "docs: plan core runtime host",
    # v0.7.5-E plan-first markers
    "v0.7.5-E Hermes Activation with Remote Blackboard Boundary is plan-first.",
    "v0.7.5-E does not activate Hermes.",
    "v0.7.5-E does not connect Hermes.",
    "v0.7.5-E does not connect OpenClaw.",
    "v0.7.5-E does not start Worker.",
    "v0.7.5-E does not create Hermes runtime.",
    "v0.7.5-E does not create Hermes activation runtime.",
    "v0.7.5-E does not create OpenClaw runtime.",
    "v0.7.5-E does not create Worker runtime.",
    "v0.7.5-E does not implement Remote Blackboard API runtime.",
    "v0.7.5-E does not create production DB.",
    "v0.7.5-E does not create shared DB.",
    "v0.7.5-E does not create remote shared DB.",
    "v0.7.5-E does not migrate queue data.",
    "v0.7.5-E does not sync local queue and remote queue.",
    "v0.7.5-E does not open shared write.",
    "v0.7.5-E does not write Google Sheets.",
    "v0.7.5-E does not create webhook.",
    # problem statement markers
    "Hermes is intended as Owner proxy / strategy / memory layer.",
    "Hermes is not currently active.",
    "Hermes is not currently connected to OpenClaw.",
    "Hermes is not currently connected to Worker.",
    "Hermes is not currently connected to Remote Blackboard API.",
    "Remote Blackboard mode must be optional and Owner-directed.",
    "Entering Blackboard mode must not imply execution permission.",
    "Hermes activation requires a separate future plan and Owner approval.",
    "Planning Hermes activation is not activating Hermes.",
    # Hermes activation definition markers
    "Hermes activation means a future approved mode where Hermes may participate in Owner-supervised coordination.",
    "Hermes activation may eventually read Blackboard messages after approval.",
    "Hermes activation may eventually write Advice Messages after approval.",
    "Hermes activation may eventually draft Task Messages after approval.",
    "Hermes activation must preserve Owner review.",
    "Hermes activation must preserve decision and dispatch separation.",
    "Hermes activation must preserve audit trail.",
    "Hermes activation is not implemented in v0.7.5-E.",
    "Hermes activation is not Worker dispatch.",
    "Hermes activation is not OpenClaw call.",
    # Hermes remains inactive boundary markers
    "Hermes remains Not Connected.",
    "Hermes is not activated in v0.7.5-E.",
    "Hermes is not called in v0.7.5-E.",
    "Hermes runtime is not created in v0.7.5-E.",
    "Hermes activation runtime is not created in v0.7.5-E.",
    "Hermes does not read queue data in v0.7.5-E.",
    "Hermes does not write Blackboard messages in v0.7.5-E.",
    "Hermes does not call OpenClaw in v0.7.5-E.",
    "Hermes does not start Worker in v0.7.5-E.",
    # Remote Blackboard mode definition markers
    "Remote Blackboard mode is a future coordination mode.",
    "Remote Blackboard mode may allow Hermes to read Task Messages after approval.",
    "Remote Blackboard mode may allow Hermes to write Advice Messages after approval.",
    "Remote Blackboard mode may allow Hermes to draft Task Messages after approval.",
    "Remote Blackboard mode is not enabled in v0.7.5-E.",
    "Remote Blackboard mode is not Remote Blackboard API runtime.",
    "Remote Blackboard mode is not shared write by default.",
    "Remote Blackboard mode is not Worker dispatch.",
    "Remote Blackboard mode is not OpenClaw call.",
    # Blackboard mode optional markers
    "Blackboard mode is optional.",
    "Owner decides whether to enter Blackboard mode.",
    "Owner decides when to exit Blackboard mode.",
    "Not every conversation enters Blackboard mode.",
    "Not every conversation is logged to Blackboard.",
    "Entering normal chat is not Blackboard mode.",
    "Planning Blackboard mode is not enabling Blackboard mode.",
    # entering Blackboard mode not execution permission markers
    "Entering Blackboard mode is not execution permission.",
    "Writing a task to Blackboard is not Worker dispatch.",
    "Writing Advice Message is not OpenClaw call.",
    "Writing Decision Message is audit record, not command.",
    "Approval readiness is not execution permission.",
    "Owner approval message is not automatic dispatch.",
    "Hermes recommendation is not execution permission.",
    "Hermes advice is not automatic follow-up execution.",
    # Hermes advice / task draft / decision boundary markers
    "Hermes Advice Message is advisory.",
    "Hermes Advice Message is not command.",
    "Hermes Advice Message is not Worker dispatch.",
    "Hermes Advice Message is not OpenClaw call.",
    "Hermes Advice Message is not Google Sheets write.",
    "Hermes Task Message draft is draft only.",
    "Hermes Task Message draft requires Owner review.",
    "Hermes Task Message draft is not queue write by itself.",
    "Hermes Task Message draft is not execution permission.",
    "Hermes must not make final Owner decisions.",
    "Owner remains final approval authority.",
    "Decision Message remains Owner-supervised audit record.",
    # Owner approval and activation boundary markers
    "Owner approval is required before activating Hermes.",
    "Owner approval is required before connecting Hermes to Remote Blackboard.",
    "Owner approval is required before allowing Hermes to write Advice Messages.",
    "Owner approval is required before allowing Hermes to draft Task Messages.",
    "Owner approval is required before connecting Hermes to OpenClaw.",
    "Owner approval is required before starting Worker.",
    "Owner approval is required before opening shared write.",
    "Owner approval is required before creating Remote Blackboard API runtime.",
    "Plan approval is not Hermes activation approval.",
    "Plan approval is not OpenClaw connection approval.",
    "Plan approval is not Worker start approval.",
    "Plan approval is not shared write approval.",
    # OpenClaw / Worker / Hermes separation markers
    "Hermes is strategy / proxy / memory layer.",
    "OpenClaw is execution / gateway / tools layer.",
    "Worker is dispatch runtime.",
    "Hermes must not bypass OpenClaw boundary.",
    "Hermes must not bypass Worker boundary.",
    "Hermes advice is not OpenClaw execution.",
    "Hermes advice is not Worker dispatch.",
    "OpenClaw remains Not Connected.",
    "Worker remains OFF.",
    # Remote Blackboard API relationship markers
    "Remote Blackboard API runtime is not implemented in v0.7.5-E.",
    "Remote Blackboard API is not called in v0.7.5-E.",
    "Remote Blackboard API write is not enabled in v0.7.5-E.",
    "Remote Blackboard API read is not enabled in v0.7.5-E.",
    "Remote Blackboard API must preserve Owner review.",
    "Remote Blackboard API must preserve audit trail.",
    "Remote Blackboard API must preserve decision and dispatch separation.",
    "Hermes Remote Blackboard access requires separate future plan and Owner approval.",
    # memory / learning / privacy markers
    "Hermes memory store is not created in v0.7.5-E.",
    "Hermes learning runtime is not created in v0.7.5-E.",
    "Hermes does not train on queue data in v0.7.5-E.",
    "Hermes does not train on private conversations in v0.7.5-E.",
    "No private conversation log is created in v0.7.5-E.",
    "No all-conversation logging is enabled in v0.7.5-E.",
    "No personal memory migration is performed in v0.7.5-E.",
    "Future Hermes memory requires separate future plan and Owner approval.",
    # autonomy / delegation markers
    "Owner remains final approval authority.",
    "Hermes may eventually propose.",
    "Hermes may eventually advise.",
    "Hermes may eventually draft.",
    "Hermes must not self-approve.",
    "Hermes must not self-dispatch.",
    "Hermes must not execute external actions by itself.",
    "Hermes must not call OpenClaw without explicit future approval.",
    "Hermes autonomy requires separate future plan and Owner approval.",
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
    "Hermes activation planning is not queue migration approval.",
    "Hermes activation planning is not shared write approval.",
    # secrets and credentials boundary markers
    "No secrets are read in v0.7.5-E.",
    "No secrets are copied in v0.7.5-E.",
    "No secrets are created in v0.7.5-E.",
    "No .env file is created in v0.7.5-E.",
    "No credentials are moved to Hermes in v0.7.5-E.",
    "No credentials are moved to OpenClaw in v0.7.5-E.",
    "No credentials are moved to any runtime host in v0.7.5-E.",
    "Hermes credentials require separate future plan and Owner approval.",
    # network / webhook / connector boundary markers
    "No webhook is created.",
    "No webhook receiver is created.",
    "No connector is created.",
    "No external network call is added.",
    "No inbound listener is added.",
    "No outbound integration is added.",
    "No port exposure is configured.",
    "No Hermes connector is created.",
    "No OpenClaw connector is created.",
    "Network activation requires separate future plan and Owner approval.",
    # runtime host relationship markers
    "Core runtime host plan does not activate Hermes.",
    "Runtime host selection is not Hermes activation.",
    "Runtime host activation is not Hermes activation by itself.",
    "Hermes activation may require a future runtime host after approval.",
    "No Core runtime host is created in v0.7.5-E.",
    "No Worker runtime is created in v0.7.5-E.",
    "No Hermes runtime is created in v0.7.5-E.",
    # failure / rollback / audit boundary markers
    "Future Hermes actions must be auditable.",
    "Future Hermes actions must include rollback notes when external actions are involved.",
    "Future Hermes failures must not silently retry external actions.",
    "Future Hermes failures must not bypass Owner approval.",
    "Future Hermes failures must not write Google Sheets by default.",
    "Future Hermes failures must not call OpenClaw by default.",
    "Future Hermes failures must not start Worker by default.",
    "No Hermes failure handling runtime is implemented in v0.7.5-E.",
    # source-of-truth boundary markers
    "Hermes activation is not source-of-truth switch.",
    "Hermes Blackboard participation is not queue migration by itself.",
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
    "Entering Blackboard mode is not execution permission.",
    "Result Message is not next dispatch permission.",
    "Advice Message is not automatic follow-up execution.",
    # candidate future Hermes activation mode markers
    "Candidate Hermes activation mode: inactive planning only.",
    "Candidate Hermes activation mode: read-only Blackboard observer.",
    "Candidate Hermes activation mode: Advice Message writer after Owner approval.",
    "Candidate Hermes activation mode: Task Message draft proposer after Owner approval.",
    "Candidate Hermes activation mode: Owner-supervised strategy agent.",
    "Candidate Hermes activation modes are planning notes only.",
    "No Hermes activation mode is implemented in v0.7.5-E.",
    "No Hermes activation mode is enabled in v0.7.5-E.",
    # current safe posture markers
    "Dashboard read-only / controlled local route behavior.",
    "Worker OFF.",
    "OpenClaw Not Connected.",
    "Hermes Not Connected.",
    "Google Sheets Disabled.",
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
    "v0.7.5-R — Remote Blackboard Preparation Closeout",
    "v0.7.5-R must remain docs-only closeout.",
    "v0.7.5-R must not activate Hermes.",
    "v0.7.5-R must not connect OpenClaw.",
    "v0.7.5-R must not start Worker.",
    "v0.7.5-R must not create production DB.",
    "v0.7.5-R must not create Remote Blackboard API runtime.",
    "v0.7.5-R must not migrate queue data.",
    "v0.7.5-R must not open shared write.",
    "v0.7.5-R must not write Google Sheets.",
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
    "does not implement Remote Blackboard API runtime",
    "does not create Hermes runtime",
    "does not create Hermes activation runtime",
    "does not create OpenClaw runtime",
    "does not create Worker runtime",
    "v0.7.5-R must not create Remote Blackboard API runtime",
    "v0.7.5-R must not create production DB",
    "v0.7.5-E does not create production DB",
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
    print(f"\nXX v0.7.5-E readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print(
        "\nv0.7.5-E Hermes Activation with Remote Blackboard Boundary readiness: ALL PASS"
    )
    sys.exit(0)
