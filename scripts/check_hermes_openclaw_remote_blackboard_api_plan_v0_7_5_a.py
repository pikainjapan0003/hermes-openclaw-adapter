"""v0.7.5-A readiness check: Remote Blackboard API Plan (plan-first).

Plan-first / boundary verification. Checks that the v0.7.5-A plan document exists and
contains the required sections (1-24), the current-master marker, the v0.7.5-A plan-first
markers, the problem statement markers, the Remote Blackboard API definition markers, the
shared backend role markers, the Blackboard message compatibility markers, the future API
surface planning markers, the future auth / permission boundary markers, the read / write
boundary markers, the migration boundary markers, the candidate backend option markers,
the current safe posture markers, the validation summary markers, the safety grep summary
markers, and the next recommended step — and that it asserts no unsafe "implemented /
created / added / migrated / moved / enabled / connected / applied / started / called /
written / changed" claim and contains no secret.

The document is allowed to contain safe negations; those that literally embed a
forbidden substring are scrubbed before the forbidden scan so they are not mis-flagged.

This script only reads the plan document. It does NOT read .env, credentials, tokens, or
secrets, makes no network call, imports no app logic (no app.main, no QueueStore), adds
no API route / router / database client / migration, creates no production / shared DB,
starts no Worker, and calls no OpenClaw / Hermes / Google Sheets.
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
    / "HERMES_OPENCLAW_REMOTE_BLACKBOARD_API_PLAN_V0_7_5_A.md"
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
ok("v0.7.5-A plan doc 存在") if DOC_PATH.exists() else xx("v0.7.5-A plan doc 存在")
if not DOC_PATH.exists():
    print("\nXX plan doc 不存在，無法繼續")
    sys.exit(1)

doc = DOC_PATH.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# [2] 必須包含的章節（1-24）
# ---------------------------------------------------------------------------
print("[2] 必須包含的章節")
REQUIRED_SECTIONS = [
    "1. Purpose",
    "2. Current master",
    "3. Scope",
    "4. Relationship to v0.7.4-R",
    "5. Problem statement",
    "6. Remote Blackboard API definition",
    "7. Shared backend role",
    "8. Local queue vs remote blackboard boundary",
    "9. GitHub / WSL / Replit boundary",
    "10. Data and secret boundary",
    "11. Blackboard message compatibility",
    "12. Future API surface planning",
    "13. Future auth and permission boundary",
    "14. Read / write boundary",
    "15. Migration boundary",
    "16. Dashboard backend source boundary",
    "17. Worker / OpenClaw / Hermes boundary",
    "18. Owner approval and activation boundary",
    "19. Failure / rollback / audit planning",
    "20. Candidate backend options",
    "21. Current safe system posture",
    "22. Non-goals",
    "23. Acceptance criteria",
    "24. Next recommended step",
]
for section in REQUIRED_SECTIONS:
    ok(f"doc 含章節「{section}」") if section in doc else xx(f"doc 含章節「{section}」")

# ---------------------------------------------------------------------------
# [3] 必須包含的 markers
# ---------------------------------------------------------------------------
print("[3] 必須包含的 markers")
REQUIRED = [
    # version
    "v0.7.5-A",
    "Remote Blackboard API",
    # current master
    "HEAD = origin/master = d67c153f6e0a84023b85a0bfd19b6d76c20240d1",
    "docs: close out topology queue audit display line",
    # v0.7.5-A plan-first markers
    "v0.7.5-A Remote Blackboard API Plan is plan-first.",
    "v0.7.5-A does not implement Remote Blackboard API runtime.",
    "v0.7.5-A does not create production DB.",
    "v0.7.5-A does not create shared DB.",
    "v0.7.5-A does not create remote shared DB.",
    "v0.7.5-A does not migrate queue data.",
    "v0.7.5-A does not open shared write.",
    "v0.7.5-A does not start Worker.",
    "v0.7.5-A does not call OpenClaw.",
    "v0.7.5-A does not call Hermes.",
    "v0.7.5-A does not write Google Sheets.",
    "v0.7.5-A does not create webhook.",
    # problem statement markers
    "Windows WSL local queue and Replit local queue are currently separate.",
    "Replit Dashboard is a remote observation station, not the core system.",
    "GitHub is clean source of code and docs, not queue DB or secrets store.",
    "Dashboard update is git pull plus Dashboard restart only.",
    "Core Blackboard loop should not depend on Replit Dashboard update.",
    "Future shared blackboard requires Remote Blackboard API or shared DB.",
    # Remote Blackboard API definition markers
    "Remote Blackboard API is a future shared coordination backend.",
    "Remote Blackboard API is not implemented in v0.7.5-A.",
    "Remote Blackboard API runtime is not created in v0.7.5-A.",
    "Remote Blackboard API is not a webhook receiver in v0.7.5-A.",
    "Remote Blackboard API is not a production executor.",
    "Remote Blackboard API must preserve Owner review.",
    "Remote Blackboard API must preserve decision and dispatch separation.",
    "Remote Blackboard API must preserve audit trail.",
    # shared backend role markers
    "Shared backend may eventually store Task Messages.",
    "Shared backend may eventually store Decision Messages.",
    "Shared backend may eventually store Result Messages.",
    "Shared backend may eventually store Advice Messages.",
    "Shared backend must not store secrets.",
    "Shared backend must not store raw credentials.",
    "Shared backend must not bypass Owner approval.",
    "Shared backend must not imply Worker dispatch.",
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
    # future API surface planning markers
    "Future API surface may include read task messages.",
    "Future API surface may include create task draft.",
    "Future API surface may include append decision message.",
    "Future API surface may include append result message.",
    "Future API surface may include append advice message.",
    "Future API surface may include list audit trail.",
    "Future API surface may include owner review state.",
    "No API route is implemented in v0.7.5-A.",
    "No FastAPI router is added in v0.7.5-A.",
    "No database client is added in v0.7.5-A.",
    "No migration is added in v0.7.5-A.",
    # future auth and permission boundary markers
    "Future remote blackboard must require authentication.",
    "Future remote blackboard must require authorization.",
    "Future remote blackboard must separate read permission from write permission.",
    "Future remote blackboard must separate Owner decision from Worker dispatch.",
    "Future remote blackboard must not expose secrets in UI or logs.",
    "Future remote blackboard must support audit records.",
    "Future remote blackboard must support rollback notes for external actions.",
    # read / write boundary markers
    "Dashboard read is not queue write.",
    "Dashboard display is not execution permission.",
    "Remote blackboard read is not Worker dispatch.",
    "Remote blackboard write is not OpenClaw call.",
    "Remote blackboard write is not Hermes action.",
    "Remote blackboard write is not external side effect by itself.",
    "Shared write remains disabled in v0.7.5-A.",
    # migration boundary markers
    "No queue migration is performed.",
    "No local queue data is moved.",
    "No Replit queue data is moved.",
    "No production queue data is created.",
    "No remote shared DB is created.",
    "No data backfill is performed.",
    "Migration requires a separate future plan and Owner approval.",
    # candidate backend option markers
    "Candidate backend option: VPS-hosted API.",
    "Candidate backend option: Postgres.",
    "Candidate backend option: Redis.",
    "Candidate backend option: Supabase.",
    "Candidate backend option: Neon.",
    "Candidate backend option: Railway.",
    "Candidate backend option: Cloudflare D1.",
    "Candidate backend options are planning notes only.",
    "No candidate backend is provisioned in v0.7.5-A.",
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
    "No connector.",
    "No tag.",
    # validation summary markers
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
    "v0.7.5-B — Local vs Remote Queue Boundary",
    "v0.7.5-B must remain plan-first unless separately approved.",
    "v0.7.5-B must not create production DB.",
    "v0.7.5-B must not create Remote Blackboard API runtime.",
    "v0.7.5-B must not migrate queue data.",
    "v0.7.5-B must not open shared write.",
    "v0.7.5-B must not start Worker / OpenClaw / Hermes / Google Sheets.",
]
for token in REQUIRED:
    ok(f"doc 含「{token}」") if token in doc else xx(f"doc 含「{token}」")

# ---------------------------------------------------------------------------
# [4] 禁止包含的不安全聲明 / 機密
#     先移除合法的安全否定句（其字面含 forbidden 子字串），再掃 forbidden。
# ---------------------------------------------------------------------------
print("[4] 禁止包含的不安全聲明 / 機密")
SAFE_NEGATIONS = [
    "Remote Blackboard API runtime is not created in v0.7.5-A",
    "Remote Blackboard API is not implemented in v0.7.5-A",
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
    print(f"\nXX v0.7.5-A readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print(
        "\nv0.7.5-A Remote Blackboard API Plan readiness: ALL PASS"
    )
    sys.exit(0)
