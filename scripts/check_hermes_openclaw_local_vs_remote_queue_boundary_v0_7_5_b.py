"""v0.7.5-B readiness check: Local vs Remote Queue Boundary (plan-first).

Plan-first / boundary verification. Checks that the v0.7.5-B plan document exists and
contains the required sections (1-28), the current-master marker, the v0.7.5-B plan-first
markers, the problem statement markers, the local queue definition markers, the remote
blackboard definition markers, the WSL / Replit queue separation markers, the read / write
boundary markers, the sync / migration boundary markers, the source-of-truth planning
boundary markers, the Blackboard message compatibility markers, the Owner approval /
activation boundary markers, the candidate future transition model markers, the current
safe posture markers, the validation summary markers, the safety grep summary markers, and
the next recommended step — and that it asserts no unsafe "implemented / created / added /
migrated / moved / copied / merged / backfilled / synchronized / enabled / connected /
applied / started / called / written / changed" claim and contains no secret.

The document is allowed to contain safe negations; those that literally embed a
forbidden substring are scrubbed before the forbidden scan so they are not mis-flagged.

This script only reads the plan document. It does NOT read .env, credentials, tokens, or
secrets, makes no network call, imports no app logic (no app.main, no QueueStore), adds
no API route / router / database client / migration, creates no production / shared DB,
syncs no queue, opens no shared write, starts no Worker, and calls no OpenClaw / Hermes /
Google Sheets.
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
    / "HERMES_OPENCLAW_LOCAL_VS_REMOTE_QUEUE_BOUNDARY_V0_7_5_B.md"
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
ok("v0.7.5-B plan doc 存在") if DOC_PATH.exists() else xx("v0.7.5-B plan doc 存在")
if not DOC_PATH.exists():
    print("\nXX plan doc 不存在，無法繼續")
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
    "4. Relationship to v0.7.5-A",
    "5. Problem statement",
    "6. Local queue definition",
    "7. Remote blackboard definition",
    "8. Local queue is not remote blackboard",
    "9. Current WSL / Replit queue separation",
    "10. GitHub / WSL / Replit boundary",
    "11. Dashboard read boundary",
    "12. Local write boundary",
    "13. Remote write boundary",
    "14. Sync boundary",
    "15. Migration boundary",
    "16. Backfill / merge / conflict boundary",
    "17. Source-of-truth planning boundary",
    "18. Blackboard message compatibility",
    "19. Owner approval and activation boundary",
    "20. Worker / OpenClaw / Hermes boundary",
    "21. Data and secrets boundary",
    "22. Candidate future transition models",
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
    "v0.7.5-B",
    "Local vs Remote Queue Boundary",
    # current master
    "HEAD = origin/master = eda58e5976bda6f313e10071ca4733dd2f465aad",
    "docs: plan remote blackboard api",
    # v0.7.5-B plan-first markers
    "v0.7.5-B Local vs Remote Queue Boundary is plan-first.",
    "v0.7.5-B does not implement Remote Blackboard API runtime.",
    "v0.7.5-B does not create production DB.",
    "v0.7.5-B does not create shared DB.",
    "v0.7.5-B does not create remote shared DB.",
    "v0.7.5-B does not migrate queue data.",
    "v0.7.5-B does not sync local queue and remote queue.",
    "v0.7.5-B does not open shared write.",
    "v0.7.5-B does not start Worker.",
    "v0.7.5-B does not call OpenClaw.",
    "v0.7.5-B does not call Hermes.",
    "v0.7.5-B does not write Google Sheets.",
    "v0.7.5-B does not create webhook.",
    # problem statement markers
    "Windows WSL local queue and Replit local queue are currently separate.",
    "Local queue is a local development/runtime data store.",
    "Remote blackboard is a future shared coordination backend.",
    "Local queue is not automatically synced to remote blackboard.",
    "Remote blackboard is not automatically authoritative.",
    "Dashboard update is not queue synchronization.",
    "GitHub push is not queue synchronization.",
    "Future synchronization requires a separate future plan and Owner approval.",
    # local queue definition markers
    "Local queue may exist in Windows WSL.",
    "Local queue may exist in Replit Preview.",
    "Windows WSL local queue and Replit local queue are separate.",
    "Local queue is local runtime/development data.",
    "Local queue is not GitHub.",
    "Local queue is not remote shared DB.",
    "Local queue is not Remote Blackboard API.",
    "Local queue must not store secrets.",
    "Local queue must not imply Worker dispatch.",
    # remote blackboard definition markers
    "Remote blackboard is a future shared coordination surface.",
    "Remote blackboard may eventually store Task Messages.",
    "Remote blackboard may eventually store Decision Messages.",
    "Remote blackboard may eventually store Result Messages.",
    "Remote blackboard may eventually store Advice Messages.",
    "Remote blackboard is not implemented in v0.7.5-B.",
    "Remote blackboard is not production DB in v0.7.5-B.",
    "Remote blackboard is not an execution dispatcher.",
    "Remote blackboard is not OpenClaw.",
    "Remote blackboard is not Hermes.",
    "Remote blackboard is not Google Sheets.",
    # queue separation markers
    "Current Windows WSL local queue remains separate.",
    "Current Replit local queue remains separate.",
    "No queue data is copied.",
    "No queue data is moved.",
    "No queue data is merged.",
    "No queue data is backfilled.",
    "No queue data is synchronized.",
    "No conflict resolver is implemented.",
    "No source-of-truth switch is performed.",
    # read / write boundary markers
    "Dashboard read is not queue write.",
    "Dashboard display is not execution permission.",
    "Reading local queue is not reading remote blackboard.",
    "Reading remote blackboard is not Worker dispatch.",
    "Writing local queue is not writing remote blackboard.",
    "Writing remote blackboard is not OpenClaw call.",
    "Writing remote blackboard is not Hermes action.",
    "Writing remote blackboard is not external side effect by itself.",
    "Shared write remains disabled in v0.7.5-B.",
    # sync / migration boundary markers
    "No queue synchronization is performed.",
    "No queue migration is performed.",
    "No local queue data is moved.",
    "No Replit queue data is moved.",
    "No production queue data is created.",
    "No remote shared DB is created.",
    "No data backfill is performed.",
    "No queue merge is performed.",
    "Sync requires a separate future plan and Owner approval.",
    "Migration requires a separate future plan and Owner approval.",
    # source-of-truth planning boundary markers
    "Current source of truth remains local to each environment.",
    "Windows WSL local queue is not automatically source of truth for Replit.",
    "Replit local queue is not automatically source of truth for WSL.",
    "Future remote blackboard authority is not enabled in v0.7.5-B.",
    "Future source-of-truth switch requires separate Owner approval.",
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
    # Owner approval and activation boundary markers
    "Owner approval is required before any remote blackboard runtime.",
    "Owner approval is required before any shared DB.",
    "Owner approval is required before any queue migration.",
    "Owner approval is required before any queue synchronization.",
    "Owner approval is required before any shared write.",
    "Owner approval is required before any source-of-truth switch.",
    "Plan approval is not runtime approval.",
    "Plan approval is not migration approval.",
    "Plan approval is not shared write approval.",
    # candidate future transition model markers
    "Candidate transition model: local-only remains source.",
    "Candidate transition model: remote read mirror.",
    "Candidate transition model: remote write draft only.",
    "Candidate transition model: remote authoritative blackboard.",
    "Candidate transition model: hybrid local runtime with remote audit mirror.",
    "Candidate transition models are planning notes only.",
    "No transition model is implemented in v0.7.5-B.",
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
    "No webhook.",
    "No external side effects.",
    "No production DB.",
    "No shared DB.",
    "No remote shared DB.",
    "No Remote Blackboard API runtime.",
    "No queue synchronization.",
    "No queue migration.",
    "No queue backfill.",
    "No queue merge.",
    "No conflict resolver.",
    "No connector.",
    "No tag.",
    # validation summary markers
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
    "v0.7.5-C — Dashboard Backend Source Plan",
    "v0.7.5-C must remain plan-first unless separately approved.",
    "v0.7.5-C must not create production DB.",
    "v0.7.5-C must not create Remote Blackboard API runtime.",
    "v0.7.5-C must not migrate queue data.",
    "v0.7.5-C must not open shared write.",
    "v0.7.5-C must not start Worker / OpenClaw / Hermes / Google Sheets.",
]
for token in REQUIRED:
    ok(f"doc 含「{token}」") if token in doc else xx(f"doc 含「{token}」")

# ---------------------------------------------------------------------------
# [4] 禁止包含的不安全聲明 / 機密
#     先移除合法的安全否定句（其字面含 forbidden 子字串），再掃 forbidden。
# ---------------------------------------------------------------------------
print("[4] 禁止包含的不安全聲明 / 機密")
SAFE_NEGATIONS = [
    "Remote blackboard is not implemented in v0.7.5-B",
    "No conflict resolver is implemented",
    "Future remote blackboard authority is not enabled in v0.7.5-B",
    "Shared write remains disabled in v0.7.5-B",
    "No source-of-truth switch is performed",
    "must not create Remote Blackboard API runtime",
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
    print(f"\nXX v0.7.5-B readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print(
        "\nv0.7.5-B Local vs Remote Queue Boundary readiness: ALL PASS"
    )
    sys.exit(0)
