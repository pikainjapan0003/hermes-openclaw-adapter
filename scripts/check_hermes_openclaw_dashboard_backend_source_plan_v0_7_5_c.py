"""v0.7.5-C readiness check: Dashboard Backend Source Plan (plan-first).

Plan-first / boundary verification. Checks that the v0.7.5-C plan document exists and
contains the required sections (1-29), the current-master marker, the v0.7.5-C plan-first
markers, the problem statement markers, the Dashboard backend source definition markers,
the current local source boundary markers, the Replit local source boundary markers, the
future remote blackboard source boundary markers, the source identity / labeling boundary
markers, the read-only source selection boundary markers, the source switching boundary
markers, the queue sync / migration boundary markers, the data freshness / staleness
boundary markers, the Owner visibility / safety indicator boundary markers, the Blackboard
message compatibility markers, the Owner approval / activation boundary markers, the
candidate future dashboard source model markers, the current safe posture markers, the
validation summary markers, the safety grep summary markers, and the next recommended step
— and that it asserts no unsafe "implemented / created / added / switched / migrated /
moved / copied / merged / backfilled / synchronized / enabled / connected / applied /
started / called / written / changed" claim and contains no secret.

The document is allowed to contain safe negations; those that literally embed a
forbidden substring are scrubbed before the forbidden scan so they are not mis-flagged.

This script only reads the plan document. It does NOT read .env, credentials, tokens, or
secrets, makes no network call, imports no app logic (no app.main, no QueueStore), adds
no API route / router / dashboard backend client / database client / migration, creates no
production / shared DB, switches no source, syncs no queue, opens no shared write, starts
no Worker, and calls no OpenClaw / Hermes / Google Sheets.
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
    / "HERMES_OPENCLAW_DASHBOARD_BACKEND_SOURCE_PLAN_V0_7_5_C.md"
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
ok("v0.7.5-C plan doc 存在") if DOC_PATH.exists() else xx("v0.7.5-C plan doc 存在")
if not DOC_PATH.exists():
    print("\nXX plan doc 不存在，無法繼續")
    sys.exit(1)

doc = DOC_PATH.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# [2] 必須包含的章節（1-29）
# ---------------------------------------------------------------------------
print("[2] 必須包含的章節")
REQUIRED_SECTIONS = [
    "1. Purpose",
    "2. Current master",
    "3. Scope",
    "4. Relationship to v0.7.5-A and v0.7.5-B",
    "5. Problem statement",
    "6. Dashboard backend source definition",
    "7. Current local source boundary",
    "8. Replit local source boundary",
    "9. Future remote blackboard source boundary",
    "10. Source identity and labeling boundary",
    "11. Read-only source selection boundary",
    "12. Source switching boundary",
    "13. Dashboard update boundary",
    "14. Queue sync and migration boundary",
    "15. Source-of-truth boundary",
    "16. Data freshness and staleness boundary",
    "17. Owner visibility and safety indicator boundary",
    "18. Error / unavailable source boundary",
    "19. Blackboard message compatibility",
    "20. Owner approval and activation boundary",
    "21. Worker / OpenClaw / Hermes boundary",
    "22. Data and secrets boundary",
    "23. Candidate future dashboard source models",
    "24. Current safe system posture",
    "25. Validation summary",
    "26. Safety grep summary",
    "27. Non-goals",
    "28. Acceptance criteria",
    "29. Next recommended step",
]
for section in REQUIRED_SECTIONS:
    ok(f"doc 含章節「{section}」") if section in doc else xx(f"doc 含章節「{section}」")

# ---------------------------------------------------------------------------
# [3] 必須包含的 markers
# ---------------------------------------------------------------------------
print("[3] 必須包含的 markers")
REQUIRED = [
    # version
    "v0.7.5-C",
    "Dashboard Backend Source Plan",
    # current master
    "HEAD = origin/master = 12e1286196753e181200eb0aea8f0797a9833e53",
    "docs: plan local versus remote queue boundary",
    # v0.7.5-C plan-first markers
    "v0.7.5-C Dashboard Backend Source Plan is plan-first.",
    "v0.7.5-C does not implement Dashboard backend source runtime.",
    "v0.7.5-C does not implement source switching runtime.",
    "v0.7.5-C does not implement Remote Blackboard API runtime.",
    "v0.7.5-C does not create production DB.",
    "v0.7.5-C does not create shared DB.",
    "v0.7.5-C does not create remote shared DB.",
    "v0.7.5-C does not migrate queue data.",
    "v0.7.5-C does not sync local queue and remote queue.",
    "v0.7.5-C does not open shared write.",
    "v0.7.5-C does not start Worker.",
    "v0.7.5-C does not call OpenClaw.",
    "v0.7.5-C does not call Hermes.",
    "v0.7.5-C does not write Google Sheets.",
    "v0.7.5-C does not create webhook.",
    # problem statement markers
    "Dashboard currently displays local application data from the environment where it runs.",
    "Windows WSL local queue and Replit local queue are currently separate.",
    "Future remote blackboard may become a dashboard-readable backend source.",
    "Dashboard backend source selection is not queue synchronization.",
    "Dashboard backend source selection is not source-of-truth switch.",
    "Dashboard update is not backend source migration.",
    "GitHub push is not backend source migration.",
    "Future dashboard source switching requires a separate future plan and Owner approval.",
    # Dashboard backend source definition markers
    "Dashboard backend source means the data source the Dashboard reads for display.",
    "Dashboard backend source may be local WSL queue in local development.",
    "Dashboard backend source may be Replit local queue in Replit Preview.",
    "Dashboard backend source may eventually be future remote blackboard.",
    "Dashboard backend source is not Worker dispatch.",
    "Dashboard backend source is not OpenClaw.",
    "Dashboard backend source is not Hermes.",
    "Dashboard backend source is not Google Sheets.",
    "Dashboard backend source is not source-of-truth switch by itself.",
    # current local source boundary markers
    "Local WSL source remains local.",
    "Local WSL source is not automatically visible to Replit.",
    "Local WSL source is not automatically remote blackboard.",
    "Reading local WSL source is not shared write.",
    "Reading local WSL source is not Worker dispatch.",
    "No local WSL queue data is moved in v0.7.5-C.",
    # Replit local source boundary markers
    "Replit local source remains separate.",
    "Replit local source is Preview / observation data.",
    "Replit local source is not production DB.",
    "Replit local source is not automatically authoritative.",
    "Replit local source is not automatically synchronized with WSL.",
    "Reading Replit local source is not reading future remote blackboard.",
    "No Replit queue data is moved in v0.7.5-C.",
    # future remote blackboard source boundary markers
    "Future remote blackboard source is planning only.",
    "Future remote blackboard source is not implemented in v0.7.5-C.",
    "Future remote blackboard source is not production DB in v0.7.5-C.",
    "Future remote blackboard source is not an execution dispatcher.",
    "Future remote blackboard source requires separate Owner approval before runtime.",
    "Future remote blackboard source must preserve Owner review.",
    "Future remote blackboard source must preserve audit trail.",
    "Future remote blackboard source must preserve decision and dispatch separation.",
    # source identity / labeling boundary markers
    "Dashboard must eventually show which backend source is being viewed.",
    "Dashboard must eventually label local WSL source distinctly.",
    "Dashboard must eventually label Replit local source distinctly.",
    "Dashboard must eventually label remote blackboard source distinctly.",
    "Dashboard source label must not imply execution permission.",
    "Dashboard source label must not imply shared write.",
    "Dashboard source label must not imply queue synchronization.",
    "No source label UI is implemented in v0.7.5-C.",
    # read-only source selection boundary markers
    "Dashboard source read is not queue write.",
    "Dashboard source read is not shared write.",
    "Dashboard source read is not Worker dispatch.",
    "Dashboard source read is not OpenClaw call.",
    "Dashboard source read is not Hermes action.",
    "Dashboard source read is not Google Sheets write.",
    "Read-only source selection is planning only in v0.7.5-C.",
    # source switching boundary markers
    "No source switching runtime is implemented.",
    "No Dashboard source switch button is added.",
    "No Dashboard source switch route is added.",
    "No backend source client is added.",
    "No source-of-truth switch is performed.",
    "No source configuration is changed.",
    "Source switching requires a separate future plan and Owner approval.",
    # queue sync / migration boundary markers
    "No queue synchronization is performed.",
    "No queue migration is performed.",
    "No local queue data is moved.",
    "No Replit queue data is moved.",
    "No production queue data is created.",
    "No remote shared DB is created.",
    "No data backfill is performed.",
    "No queue merge is performed.",
    "No conflict resolver is implemented.",
    "Dashboard backend source planning is not sync approval.",
    "Dashboard backend source planning is not migration approval.",
    # data freshness / staleness boundary markers
    "Dashboard should eventually show data source freshness.",
    "Dashboard should eventually show when a source is stale.",
    "Dashboard should eventually show when a remote source is unavailable.",
    "Stale data must not be treated as execution permission.",
    "Unavailable source must not trigger fallback writes.",
    "Unavailable source must not start Worker.",
    "Unavailable source must not call OpenClaw or Hermes.",
    "No freshness indicator is implemented in v0.7.5-C.",
    # Owner visibility / safety indicator boundary markers
    "Owner must be able to see which backend source Dashboard is reading.",
    "Owner must be able to see whether the source is local or remote.",
    "Owner must be able to see whether the source is read-only.",
    "Owner must be able to see whether Worker is OFF.",
    "Owner must be able to see whether OpenClaw is Not Connected.",
    "Owner must be able to see whether Hermes is Not Connected.",
    "Owner must be able to see whether Google Sheets is Disabled.",
    "No safety indicator UI is implemented in v0.7.5-C.",
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
    "Owner approval is required before any Dashboard backend source runtime.",
    "Owner approval is required before any source switching runtime.",
    "Owner approval is required before any remote blackboard runtime.",
    "Owner approval is required before any shared DB.",
    "Owner approval is required before any queue migration.",
    "Owner approval is required before any queue synchronization.",
    "Owner approval is required before any shared write.",
    "Owner approval is required before any source-of-truth switch.",
    "Plan approval is not runtime approval.",
    "Plan approval is not source switching approval.",
    "Plan approval is not migration approval.",
    "Plan approval is not shared write approval.",
    # candidate future dashboard source model markers
    "Candidate dashboard source model: local-only dashboard source.",
    "Candidate dashboard source model: Replit local preview source.",
    "Candidate dashboard source model: remote read-only blackboard source.",
    "Candidate dashboard source model: selectable read-only source view.",
    "Candidate dashboard source model: local runtime with remote audit mirror display.",
    "Candidate dashboard source models are planning notes only.",
    "No dashboard source model is implemented in v0.7.5-C.",
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
    "No Dashboard backend source runtime.",
    "No source switching runtime.",
    "No queue synchronization.",
    "No queue migration.",
    "No queue backfill.",
    "No queue merge.",
    "No conflict resolver.",
    "No connector.",
    "No tag.",
    # validation summary markers
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
    "v0.7.5-D — Core Runtime Host Plan",
    "v0.7.5-D must remain plan-first unless separately approved.",
    "v0.7.5-D must not create production DB.",
    "v0.7.5-D must not create Remote Blackboard API runtime.",
    "v0.7.5-D must not migrate queue data.",
    "v0.7.5-D must not open shared write.",
    "v0.7.5-D must not start Worker / OpenClaw / Hermes / Google Sheets.",
]
for token in REQUIRED:
    ok(f"doc 含「{token}」") if token in doc else xx(f"doc 含「{token}」")

# ---------------------------------------------------------------------------
# [4] 禁止包含的不安全聲明 / 機密
#     先移除合法的安全否定句（其字面含 forbidden 子字串），再掃 forbidden。
# ---------------------------------------------------------------------------
print("[4] 禁止包含的不安全聲明 / 機密")
SAFE_NEGATIONS = [
    "No source switching runtime is implemented",
    "No Dashboard source switch button is added",
    "No Dashboard source switch route is added",
    "No backend source client is added",
    "No source-of-truth switch is performed",
    "No source configuration is changed",
    "No conflict resolver is implemented",
    "Unavailable source must not trigger fallback writes",
    "Future remote blackboard source is not implemented in v0.7.5-C",
    "does not implement Dashboard backend source runtime",
    "does not implement source switching runtime",
    "does not implement Remote Blackboard API runtime",
    "v0.7.5-D must not create Remote Blackboard API runtime",
    "v0.7.5-D must not create production DB",
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
    "Dashboard backend source runtime implemented",
    "source switching runtime created",
    "source switching runtime implemented",
    "Dashboard source switch button added",
    "Dashboard source switch route added",
    "backend source client added",
    "remote backend client added",
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
    print(f"\nXX v0.7.5-C readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print(
        "\nv0.7.5-C Dashboard Backend Source Plan readiness: ALL PASS"
    )
    sys.exit(0)
