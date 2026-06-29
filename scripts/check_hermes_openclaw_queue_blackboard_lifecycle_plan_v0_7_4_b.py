"""v0.7.4-B readiness check: Queue / Blackboard Lifecycle Plan.

Plan / current-state verification. Checks that the v0.7.4-B queue / blackboard
lifecycle planning document exists and contains the required sections (1-24), the
current-master marker, the v0.7.4-A and v0.7.3-R completion markers, the Blackboard
message family, the Task / Decision / Result / Advice Message lifecycles, the queue
lifecycle planning vocabulary, the dispatch-separation boundary, the Worker /
OpenClaw read boundary, the Hermes advice boundary, the Dashboard display boundary,
the local-vs-Replit queue boundary, the Remote Blackboard future-only direction,
the State Transition Guard preparation, the safe system posture, and the next
recommended step — and that it asserts no unsafe "enabled / connected / auto-
executable / message-is-command / grants-permission / dispatches / live-output /
approves / approve-triggers / display-changes / ran-in / claimed-by / dispatched-
to / implemented / POST-to / clicked / seeded / cleaned-up / live-write-performed"
claim and contains no secret.

This script only reads the planning document. It does NOT read .env, credentials,
tokens, or secrets, makes no network call, imports no app logic (no app.main, no
QueueStore), starts no Worker, and calls no OpenClaw / Hermes / Google Sheets.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
PASS = []
FAIL = []

DOC_PATH = (
    ROOT / "docs" / "HERMES_OPENCLAW_QUEUE_BLACKBOARD_LIFECYCLE_PLAN_V0_7_4_B.md"
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
ok("v0.7.4-B plan doc 存在") if DOC_PATH.exists() else xx("v0.7.4-B plan doc 存在")
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
    "4. Relationship to v0.7.4-A",
    "5. Relationship to v0.7.3-R",
    "6. Blackboard lifecycle summary",
    "7. Queue lifecycle summary",
    "8. Message family overview",
    "9. Task Message lifecycle",
    "10. Decision Message lifecycle",
    "11. Result Message lifecycle",
    "12. Advice Message lifecycle",
    "13. Owner Review boundary",
    "14. Dispatch separation boundary",
    "15. Worker / OpenClaw read boundary",
    "16. Hermes advice boundary",
    "17. Dashboard display boundary",
    "18. Local queue vs Replit queue boundary",
    "19. Remote Blackboard future path",
    "20. State Transition Guard preparation",
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
    "v0.7.4-B",
    "Queue / Blackboard Lifecycle Plan",
    # current master
    "HEAD = origin/master = 1c507b995f44264bf973bd196e35d9ee8a88e983",
    "docs: plan core topology and dashboard independence",
    # v0.7.4-A completion markers
    "v0.7.4-A Core Topology / Dashboard Update / Core Independence Plan is complete.",
    "GitHub is the clean source of truth for code and docs.",
    "Windows WSL is the primary local development environment.",
    "Replit is a remote observation station / Preview Dashboard.",
    "Dashboard update means git pull plus Dashboard restart.",
    "Dashboard update does not start Worker.",
    "Dashboard update does not call OpenClaw.",
    "Dashboard update does not call Hermes.",
    "Dashboard update does not write Google Sheets.",
    "The core blackboard loop should not depend on whether Replit Dashboard is updated.",
    "Current Windows WSL local queue and Replit local queue are separate.",
    "Remote Blackboard API / shared DB is future planning only.",
    # v0.7.3-R completion markers
    "v0.7.3 Approval Decision Layer is complete.",
    "approval_decision_events are Decision Messages.",
    "Decision Messages are blackboard audit records, not execution commands.",
    "approve is not execute.",
    "Owner decision event is not Worker dispatch.",
    "No Worker / OpenClaw / Hermes / Google Sheets execution was enabled.",
    # message family
    "Task Message",
    "Decision Message",
    "Result Message",
    "Advice Message",
    # Task Message markers
    "Task Message describes proposed work.",
    "Task Message is not automatically executable.",
    "Task Message requires Owner review before any future dispatch.",
    "Task Message may carry annotation, approval_readiness, safety_snapshot, and audit metadata.",
    "Task Message does not call Worker.",
    "Task Message does not call OpenClaw.",
    "Task Message does not call Hermes.",
    "Task Message does not write Google Sheets.",
    # Decision Message markers
    "Decision Message records an Owner decision.",
    "Decision Message is an audit record.",
    "Decision Message is not a Worker command.",
    "Decision Message is not an OpenClaw command.",
    "Decision Message is not a Hermes instruction.",
    "Decision Message does not grant execution permission.",
    "Decision Message does not dispatch.",
    # Result Message markers
    "Result Message records an execution result or dry-run result.",
    "Result Message is future planning only in v0.7.4-B.",
    "Result Message does not exist as a live Worker output yet.",
    "Result Message must be append-only when implemented.",
    "Result Message must not erase Task Message or Decision Message history.",
    "Result Message must not contain secrets.",
    # Advice Message markers
    "Advice Message records Hermes guidance.",
    "Advice Message is future planning only in v0.7.4-B.",
    "Advice Message is advisory, not approval.",
    "Advice Message is not an Owner decision.",
    "Advice Message is not Worker dispatch.",
    "Advice Message must not bypass Owner Review.",
    # Queue lifecycle markers
    "Queue lifecycle is a planning model in v0.7.4-B.",
    "Queue lifecycle does not change runtime status transitions in v0.7.4-B.",
    "Queue lifecycle does not enforce new state guards in v0.7.4-B.",
    "Queue lifecycle prepares v0.7.4-C State Transition Guard.",
    # lifecycle vocabulary
    "draft_or_created",
    "annotated",
    "owner_review",
    "owner_decided",
    "dispatch_candidate",
    "dry_run_claimed",
    "dry_run_result_recorded",
    "advice_recorded",
    "archived_or_closed",
    # dispatch separation
    "Owner approval does not automatically imply Worker execution.",
    "Decision and execution dispatch remain separate.",
    "Approval readiness is not execution permission.",
    "Decision Message is not dispatch permission.",
    "dispatch_candidate is future planning only.",
    "execution_permission = False",
    "dispatch_allowed = False",
    "execution_permission_at_decision = False",
    "dispatch_allowed_at_decision = False",
    # Worker / OpenClaw read boundary
    "Worker / OpenClaw read boundary is future planning only in v0.7.4-B.",
    "Worker must not run in v0.7.4-B.",
    "OpenClaw must not be called in v0.7.4-B.",
    "No task is claimed by Worker in v0.7.4-B.",
    "No task is dispatched to OpenClaw in v0.7.4-B.",
    # Hermes advice boundary
    "Hermes advice boundary is future planning only in v0.7.4-B.",
    "Hermes must not be called in v0.7.4-B.",
    "Hermes Advice Message must not approve tasks.",
    "Hermes Advice Message must not dispatch tasks.",
    "Hermes Advice Message must not write external systems.",
    "Owner remains the approval authority.",
    # Dashboard display boundary
    "Dashboard may display lifecycle state.",
    "Dashboard display does not change lifecycle state.",
    "Dashboard display does not grant execution permission.",
    "Dashboard display does not dispatch Worker.",
    "Dashboard display does not call OpenClaw.",
    "Dashboard display does not call Hermes.",
    "Dashboard display does not write Google Sheets.",
    # local queue vs Replit queue
    "They do not automatically sync.",
    "Replit pull updates code, not queue data.",
    "GitHub push updates code, not queue data.",
    "A shared blackboard requires a future Remote Blackboard API or shared DB.",
    # Remote Blackboard future-only
    "Remote Blackboard API / shared DB is future planning only in v0.7.4-B.",
    "v0.7.4-B does not implement production DB.",
    "v0.7.4-B does not migrate queues.",
    "v0.7.4-B does not enable shared writes.",
    "v0.7.4-B does not create webhooks.",
    "v0.7.4-B does not start Worker.",
    # safe system posture
    "Dashboard read-only / controlled local route behavior",
    "Worker OFF",
    "OpenClaw Not Connected",
    "Hermes Not Connected",
    "Google Sheets Disabled",
    "No external side effects",
    "No --apply",
    "No demo task cleanup",
    "No seed demo task",
    "No secrets read",
    "No webhook",
    "No tag",
    # next recommended step
    "v0.7.4-C — State Transition Guard",
    "v0.7.4-C must remain Owner-approved.",
    "It should translate the v0.7.4-B lifecycle plan into guarded transition rules.",
    "No Worker dispatch.",
]
for token in REQUIRED:
    ok(f"doc 含「{token}」") if token in doc else xx(f"doc 含「{token}」")

# ---------------------------------------------------------------------------
# [4] 禁止包含的不安全聲明 / 機密
#     先移除合法的安全否定句（其字面含 forbidden 子字串），再掃 forbidden。
# ---------------------------------------------------------------------------
print("[4] 禁止包含的不安全聲明 / 機密")
SAFE_NEGATIONS = []  # 本 doc 以否定句撰寫，不含任何 forbidden 子字串
scrubbed = doc
for phrase in SAFE_NEGATIONS:
    scrubbed = scrubbed.replace(phrase, "")

FORBIDDEN_SUBSTR = [
    "GOOGLE_SHEETS_ENABLED=true",
    "Worker enabled",
    "OpenClaw connected",
    "Hermes connected",
    "Google Sheets live write enabled",
    "Task Message is automatically executable",
    "Task Message calls Worker",
    "Task Message calls OpenClaw",
    "Task Message calls Hermes",
    "Task Message writes Google Sheets",
    "Decision Message is a Worker command",
    "Decision Message is an OpenClaw command",
    "Decision Message is a Hermes instruction",
    "Decision Message grants execution permission",
    "Decision Message dispatches",
    "Result Message exists as a live Worker output",
    "Advice Message approves tasks",
    "Advice Message dispatches tasks",
    "Advice Message writes external systems",
    "Owner approval triggers Worker execution",
    "approve triggers dispatch",
    "approve calls OpenClaw",
    "approve calls Hermes",
    "approve writes Google Sheets",
    "Dashboard display changes lifecycle state",
    "Dashboard display grants execution permission",
    "Dashboard display dispatches Worker",
    "Dashboard display calls OpenClaw",
    "Dashboard display calls Hermes",
    "Dashboard display writes Google Sheets",
    "Worker ran in v0.7.4-B",
    "OpenClaw called in v0.7.4-B",
    "Hermes called in v0.7.4-B",
    "task claimed by Worker in v0.7.4-B",
    "task dispatched to OpenClaw in v0.7.4-B",
    "Remote Blackboard API implemented",
    "production DB implemented",
    "shared writes enabled",
    "webhook receiver created",
    "POST to Replit Preview",
    "POST to real queue",
    "clicked approve",
    "clicked reject",
    "clicked cancel",
    "clicked retry",
    "clicked archive",
    "live queue write validation performed",
    "demo task cleaned up",
    "seeded demo task",
]
for token in FORBIDDEN_SUBSTR:
    ok(f"doc 無「{token}」") if token not in scrubbed else xx(f"doc 不得含「{token}」")

FORBIDDEN_PATTERNS = [
    (r"spreadsheets/d/[A-Za-z0-9_-]{20,}", "real spreadsheet URL"),
    (r'"?refresh_token"?\s*[:=]\s*"[^"]+"', "refresh token value"),
    (r'"?client_secret"?\s*[:=]\s*"[^"]+"', "client secret value"),
    (r"-----BEGIN[ A-Z]*PRIVATE KEY-----", "private key value"),
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
    print(f"\nXX v0.7.4-B readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print("\nv0.7.4-B Queue / Blackboard Lifecycle Plan readiness: ALL PASS")
    sys.exit(0)
