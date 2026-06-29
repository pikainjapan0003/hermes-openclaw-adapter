"""v0.7.4-C readiness check: State Transition Guard Plan.

Plan / current-state verification. Checks that the v0.7.4-C state transition guard
planning document exists and contains the required sections (1-24), the current-
master marker, the v0.7.4-B / v0.7.4-A / v0.7.3-R completion markers, the guard
purpose, the unchanged current-state-model markers, the planned lifecycle
vocabulary, the proposed allowed and blocked transitions, the Owner decision /
dispatch candidate / Worker / OpenClaw / Hermes / Dashboard / QueueStore / runtime
boundaries, the local-vs-Replit queue boundary, the Remote Blackboard future-only
direction, the safe system posture, and the next recommended step — and that it
asserts no unsafe "enabled / connected / guard-dispatches / modifies-transitions /
enforces / implements / owner-decision-directly / dispatch_candidate-is-permission
/ ran-in / called-in / display-changes / queuestore-changed / implemented / POST-to
/ clicked / seeded / cleaned-up / live-write-performed" claim and contains no
secret.

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
    ROOT / "docs" / "HERMES_OPENCLAW_STATE_TRANSITION_GUARD_PLAN_V0_7_4_C.md"
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
ok("v0.7.4-C plan doc 存在") if DOC_PATH.exists() else xx("v0.7.4-C plan doc 存在")
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
    "4. Relationship to v0.7.4-B",
    "5. Relationship to v0.7.4-A",
    "6. Relationship to v0.7.3-R",
    "7. Guard purpose",
    "8. Current state model",
    "9. Planned lifecycle vocabulary",
    "10. Proposed allowed transitions",
    "11. Proposed blocked transitions",
    "12. Owner decision transition boundary",
    "13. Dispatch candidate boundary",
    "14. Worker / OpenClaw boundary",
    "15. Hermes advice boundary",
    "16. Dashboard display boundary",
    "17. QueueStore boundary",
    "18. Runtime implementation boundary",
    "19. Local queue vs Replit queue boundary",
    "20. Remote Blackboard future path",
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
    "v0.7.4-C",
    "State Transition Guard Plan",
    # current master
    "HEAD = origin/master = 0c3f80ce59bd44a180cbef7a7fff0070de85e61a",
    "docs: plan queue blackboard lifecycle",
    # v0.7.4-B completion markers
    "v0.7.4-B Queue / Blackboard Lifecycle Plan is complete.",
    "Task Message",
    "Decision Message",
    "Result Message",
    "Advice Message",
    "Queue lifecycle is a planning model in v0.7.4-B.",
    "Queue lifecycle does not change runtime status transitions in v0.7.4-B.",
    "Queue lifecycle prepares v0.7.4-C State Transition Guard.",
    # v0.7.4-A completion markers
    "v0.7.4-A Core Topology / Dashboard Update / Core Independence Plan is complete.",
    "Replit is a remote observation station / Preview Dashboard.",
    "Dashboard update means git pull plus Dashboard restart.",
    "Dashboard update does not start Worker.",
    "The core blackboard loop should not depend on whether Replit Dashboard is updated.",
    "Current Windows WSL local queue and Replit local queue are separate.",
    "Remote Blackboard API / shared DB is future planning only.",
    # v0.7.3-R completion markers
    "v0.7.3 Approval Decision Layer is complete.",
    "approval_decision_events are Decision Messages.",
    "Decision Messages are blackboard audit records, not execution commands.",
    "approve is not execute.",
    "Owner decision event is not Worker dispatch.",
    # guard purpose
    "State Transition Guard defines allowed and blocked transitions before runtime enforcement.",
    "State Transition Guard is a safety contract.",
    "State Transition Guard is not Worker dispatch.",
    "State Transition Guard is not OpenClaw execution.",
    "State Transition Guard is not Hermes execution.",
    "State Transition Guard is not Google Sheets write.",
    # current state model
    "Current runtime status model remains unchanged in v0.7.4-C.",
    "v0.7.4-C does not modify current status transitions.",
    "v0.7.4-C does not enforce runtime guards.",
    "v0.7.4-C only plans guard rules.",
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
    # allowed transitions
    "draft_or_created -> annotated",
    "annotated -> owner_review",
    "owner_review -> owner_decided",
    "owner_decided -> dispatch_candidate",
    "dispatch_candidate -> dry_run_claimed",
    "dry_run_claimed -> dry_run_result_recorded",
    "dry_run_result_recorded -> advice_recorded",
    "advice_recorded -> owner_review",
    "owner_review -> archived_or_closed",
    "owner_decided -> archived_or_closed",
    "Proposed allowed transitions are planning rules only in v0.7.4-C.",
    "They are not runtime-enforced in v0.7.4-C.",
    # blocked transitions
    "draft_or_created -> dry_run_claimed is blocked.",
    "annotated -> dry_run_claimed is blocked.",
    "owner_review -> dry_run_claimed is blocked.",
    "owner_review -> dry_run_result_recorded is blocked.",
    "owner_decided -> dry_run_result_recorded is blocked unless future Worker dry-run claim exists.",
    "Decision Message -> Worker dispatch is blocked.",
    "Advice Message -> Worker dispatch is blocked.",
    "Dashboard display -> lifecycle mutation is blocked.",
    "GitHub push -> queue mutation is blocked.",
    "Replit pull -> queue mutation is blocked.",
    # Owner decision boundary
    "Owner decision may move a task toward owner_decided.",
    "Owner decision may not directly move a task to dry_run_claimed.",
    "Owner decision may not directly move a task to dry_run_result_recorded.",
    "Owner decision may not directly dispatch Worker.",
    "Owner decision may not call OpenClaw.",
    "Owner decision may not call Hermes.",
    "Owner decision may not write Google Sheets.",
    # dispatch candidate boundary
    "dispatch_candidate is future planning only in v0.7.4-C.",
    "dispatch_candidate is not execution permission.",
    "dispatch_candidate is not dispatch_allowed.",
    "dispatch_candidate is not Worker claim.",
    "dispatch_candidate is not OpenClaw command.",
    "execution_permission = False",
    "dispatch_allowed = False",
    # Worker / OpenClaw boundary
    "Worker / OpenClaw boundary is future planning only in v0.7.4-C.",
    "Worker must not run in v0.7.4-C.",
    "OpenClaw must not be called in v0.7.4-C.",
    "No task is claimed by Worker in v0.7.4-C.",
    "No task is dispatched to OpenClaw in v0.7.4-C.",
    # Hermes advice boundary
    "Hermes advice boundary is future planning only in v0.7.4-C.",
    "Hermes must not be called in v0.7.4-C.",
    "Hermes Advice Message must not approve tasks.",
    "Hermes Advice Message must not dispatch tasks.",
    "Hermes Advice Message must not write external systems.",
    "Owner remains the approval authority.",
    # Dashboard display boundary
    "Dashboard may display planned lifecycle state.",
    "Dashboard display does not change lifecycle state.",
    "Dashboard display does not enforce guard.",
    "Dashboard display does not grant execution permission.",
    "Dashboard display does not dispatch Worker.",
    "Dashboard display does not call OpenClaw.",
    "Dashboard display does not call Hermes.",
    "Dashboard display does not write Google Sheets.",
    # QueueStore boundary
    "QueueStore runtime behavior is unchanged in v0.7.4-C.",
    "v0.7.4-C does not modify app/queue_store.py.",
    "v0.7.4-C does not add QueueStore methods.",
    "v0.7.4-C does not change status persistence.",
    "v0.7.4-C does not change payload persistence.",
    # runtime implementation boundary
    "Runtime guard implementation is future work after v0.7.4-C.",
    "v0.7.4-C does not implement runtime guard.",
    "v0.7.4-C does not add route enforcement.",
    "v0.7.4-C does not change approval behavior.",
    "v0.7.4-C does not change archive behavior.",
    "v0.7.4-C does not change retry behavior.",
    # local queue vs Replit queue
    "They do not automatically sync.",
    "Replit pull updates code, not queue data.",
    "GitHub push updates code, not queue data.",
    "A shared blackboard requires a future Remote Blackboard API or shared DB.",
    # Remote Blackboard future-only
    "Remote Blackboard API / shared DB is future planning only in v0.7.4-C.",
    "v0.7.4-C does not implement production DB.",
    "v0.7.4-C does not migrate queues.",
    "v0.7.4-C does not enable shared writes.",
    "v0.7.4-C does not create webhooks.",
    "v0.7.4-C does not start Worker.",
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
    "v0.7.4-D — Audit Trail Display",
    "v0.7.4-D should remain display-only unless separately approved.",
    "It should display lifecycle / audit trail information without changing state.",
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
    "State Transition Guard dispatches Worker",
    "State Transition Guard calls OpenClaw",
    "State Transition Guard calls Hermes",
    "State Transition Guard writes Google Sheets",
    "v0.7.4-C modifies current status transitions",
    "v0.7.4-C enforces runtime guards",
    "v0.7.4-C implements runtime guard",
    "v0.7.4-C adds route enforcement",
    "v0.7.4-C changes approval behavior",
    "v0.7.4-C changes archive behavior",
    "v0.7.4-C changes retry behavior",
    "Owner decision directly moves a task to dry_run_claimed",
    "Owner decision directly moves a task to dry_run_result_recorded",
    "Owner decision directly dispatches Worker",
    "Owner decision calls OpenClaw",
    "Owner decision calls Hermes",
    "Owner decision writes Google Sheets",
    "dispatch_candidate is execution permission",
    "dispatch_candidate is dispatch_allowed",
    "dispatch_candidate is Worker claim",
    "dispatch_candidate is OpenClaw command",
    "Worker ran in v0.7.4-C",
    "OpenClaw called in v0.7.4-C",
    "Hermes called in v0.7.4-C",
    "task claimed by Worker in v0.7.4-C",
    "task dispatched to OpenClaw in v0.7.4-C",
    "Dashboard display changes lifecycle state",
    "Dashboard display enforces guard",
    "Dashboard display grants execution permission",
    "Dashboard display dispatches Worker",
    "Dashboard display calls OpenClaw",
    "Dashboard display calls Hermes",
    "Dashboard display writes Google Sheets",
    "QueueStore runtime behavior changed",
    "v0.7.4-C modifies app/queue_store.py",
    "v0.7.4-C adds QueueStore methods",
    "v0.7.4-C changes status persistence",
    "v0.7.4-C changes payload persistence",
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
    print(f"\nXX v0.7.4-C readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print("\nv0.7.4-C State Transition Guard Plan readiness: ALL PASS")
    sys.exit(0)
