"""v0.7.4-R readiness check: Topology + Queue + Audit Display Closeout.

Line-level closeout / current-state verification. Checks that the v0.7.4-R closeout
document exists and contains the required sections (1-25), the current-master marker,
the v0.7.4-A / B / C / D / D-R / E / F / F-R completion markers, the topology boundary
markers, the Blackboard message family markers, the state-transition-guard markers, the
audit-trail-display markers, the Replit GET-only validation markers, the cleanup-plan
markers, the safe-cleanup dry-run markers, the fixed safety value markers, the current
safe posture markers, the validation summary markers, the safety grep summary markers,
and the next recommended step — and that it asserts no unsafe "applied / deleted /
archived / modified / enabled / connected / POST-was-sent / started / called / written /
created / added / changed / implemented" claim and contains no secret.

The document is allowed to contain safe negations; those that literally embed a
forbidden substring are scrubbed before the forbidden scan so they are not mis-flagged.

This script only reads the closeout document. It does NOT read .env, credentials,
tokens, or secrets, makes no network call, imports no app logic (no app.main, no
QueueStore), starts no Worker, performs no cleanup, performs no apply, reads no real
queue DB, and calls no OpenClaw / Hermes / Google Sheets.
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
    / "HERMES_OPENCLAW_TOPOLOGY_QUEUE_AUDIT_DISPLAY_CLOSEOUT_V0_7_4_R.md"
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
ok("v0.7.4-R closeout doc 存在") if DOC_PATH.exists() else xx("v0.7.4-R closeout doc 存在")
if not DOC_PATH.exists():
    print("\nXX closeout doc 不存在，無法繼續")
    sys.exit(1)

doc = DOC_PATH.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# [2] 必須包含的章節（1-25）
# ---------------------------------------------------------------------------
print("[2] 必須包含的章節")
REQUIRED_SECTIONS = [
    "1. Purpose",
    "2. Current master",
    "3. Scope",
    "4. v0.7.4 line summary",
    "5. v0.7.4-A topology closeout",
    "6. v0.7.4-B queue / blackboard lifecycle closeout",
    "7. v0.7.4-C state transition guard plan closeout",
    "8. v0.7.4-D audit trail display closeout",
    "9. v0.7.4-D-R Replit GET-only validation closeout",
    "10. v0.7.4-E demo task cleanup plan closeout",
    "11. v0.7.4-F safe local cleanup tool closeout",
    "12. v0.7.4-F-R safe local cleanup tool closeout",
    "13. Current architecture boundary",
    "14. Blackboard message family boundary",
    "15. Audit trail display boundary",
    "16. Cleanup / apply boundary",
    "17. Replit / GitHub / WSL boundary",
    "18. QueueStore / queue data boundary",
    "19. Runtime / external side-effect boundary",
    "20. Current safe system posture",
    "21. Validation summary",
    "22. Safety grep summary",
    "23. Non-goals",
    "24. Acceptance criteria",
    "25. Next recommended step",
]
for section in REQUIRED_SECTIONS:
    ok(f"doc 含章節「{section}」") if section in doc else xx(f"doc 含章節「{section}」")

# ---------------------------------------------------------------------------
# [3] 必須包含的 markers
# ---------------------------------------------------------------------------
print("[3] 必須包含的 markers")
REQUIRED = [
    # version
    "v0.7.4-R",
    "Topology + Queue + Audit Display",
    # current master
    "HEAD = origin/master = cec4ef9855a4ae1da50b770fcb29d05cc50f2812",
    "docs: close out safe local cleanup tool",
    # v0.7.4 line completion markers
    "v0.7.4-A Core Topology / Dashboard Update / Core Independence Plan is complete.",
    "v0.7.4-B Queue / Blackboard Lifecycle Plan is complete.",
    "v0.7.4-C State Transition Guard Plan is complete.",
    "v0.7.4-D Audit Trail Display is complete.",
    "v0.7.4-D-R Audit Trail Display Replit GET-only Validation Closeout is complete.",
    "v0.7.4-E Demo Task Cleanup Plan is complete.",
    "v0.7.4-F Safe Local Cleanup Tool is complete.",
    "v0.7.4-F-R Safe Local Cleanup Tool Closeout is complete.",
    "v0.7.4 Topology + Queue + Audit Display line is complete.",
    # A topology markers
    "GitHub is clean source of code and docs, not queue DB or secrets store.",
    "Windows WSL is primary local development environment.",
    "Replit is remote observation station / Preview Dashboard.",
    "Dashboard update means git pull plus Dashboard restart.",
    "Dashboard update does not start Worker.",
    "Dashboard update does not call OpenClaw.",
    "Dashboard update does not call Hermes.",
    "Dashboard update does not write Google Sheets.",
    "Current Windows WSL local queue and Replit local queue are separate.",
    # B queue / blackboard markers
    "Task Message",
    "Decision Message",
    "Result Message",
    "Advice Message",
    "Decision Message is audit record, not command.",
    "approve is not execute.",
    "Owner decision event is not Worker dispatch.",
    "Writing a task to Blackboard is not Worker dispatch.",
    "Entering Blackboard mode is not execution permission.",
    # C guard markers
    "State Transition Guard is a safety contract.",
    "v0.7.4-C does not modify current status transitions.",
    "v0.7.4-C does not enforce runtime guards.",
    "Approval readiness is not execution permission.",
    "Execution dispatch remains separately gated.",
    # D audit display markers
    "Audit Trail Display is read-only.",
    "Audit Trail Display does not change lifecycle state.",
    "Audit Trail Display does not enforce guard.",
    "Audit Trail Display does not grant execution permission.",
    "Audit Trail Display does not dispatch Worker.",
    "Audit Trail Display does not call OpenClaw.",
    "Audit Trail Display does not call Hermes.",
    "Audit Trail Display does not write Google Sheets.",
    "Result Message remains future-only in v0.7.4.",
    "Advice Message remains future-only in v0.7.4.",
    # D-R Replit validation markers
    "Replit GET-only validation passed.",
    "No POST was sent.",
    "No queue write validation was performed.",
    "No Worker / OpenClaw / Hermes / Google Sheets was called.",
    "Replit Preview validation did not clean Replit queue.",
    "Replit Preview validation did not start Worker.",
    # E cleanup plan markers
    "Cleanup Plan is not cleanup apply.",
    "Cleanup dry-run is not cleanup apply.",
    "Cleanup apply requires separate Owner approval.",
    "Cleanup apply requires an explicit apply flag.",
    "Cleanup apply requires a second confirmation flag.",
    "WSL cleanup tooling must not clean Replit queue.",
    # F / F-R safe cleanup markers
    "v0.7.4-F is dry-run-only.",
    "v0.7.4-F does not implement cleanup apply.",
    "v0.7.4-F does not delete tasks.",
    "v0.7.4-F does not archive tasks.",
    "v0.7.4-F does not modify queue DB.",
    "v0.7.4-F does not modify local queue data.",
    "v0.7.4-F does not modify Replit queue data.",
    "v0.7.4-F does not read real queue DB.",
    "v0.7.4-F requires explicit JSON input.",
    "v0.7.4-F writes report to stdout only.",
    "CLI rejects --apply.",
    "CLI rejects --confirm-apply.",
    "CLI rejects apply-like arguments.",
    "No Replit POST validation is required for v0.7.4-F.",
    "No Replit queue cleanup is allowed.",
    # fixed safety value markers
    'execution_mode = "dry_run_only"',
    "dry_run = True",
    "apply_requested = False",
    "apply_allowed = False",
    "would_delete = False",
    "would_archive = False",
    "would_modify = False",
    "external_side_effects = False",
    "owner_approval_required = True",
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
    "No remote shared DB.",
    "No Remote Blackboard API runtime.",
    "No connector.",
    "No tag.",
    # validation summary markers
    "v0.7.4-R closeout readiness: ALL PASS.",
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
    "v0.8.0-A must be plan-first.",
    "v0.8.0-A must not start Worker / OpenClaw / Hermes / Google Sheets.",
    "v0.8.0-A must not create Remote Blackboard API runtime unless separately approved.",
    "v0.8.0-A must not perform cleanup apply.",
]
for token in REQUIRED:
    ok(f"doc 含「{token}」") if token in doc else xx(f"doc 含「{token}」")

# ---------------------------------------------------------------------------
# [4] 禁止包含的不安全聲明 / 機密
#     先移除合法的安全否定句（其字面含 forbidden 子字串），再掃 forbidden。
# ---------------------------------------------------------------------------
print("[4] 禁止包含的不安全聲明 / 機密")
SAFE_NEGATIONS = [
    "must not create Remote Blackboard API runtime unless separately approved",
    "Replit Preview validation did not clean Replit queue",
    "WSL cleanup tooling must not clean Replit queue",
    "No Replit queue cleanup is allowed",
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
    "cleanup route added",
    "cleanup button added",
    "cleanup form added",
    "QueueStore runtime behavior changed",
    "app/queue_store.py changed",
    "approval routes changed",
    "dashboard auth changed",
    "status transition changed",
    "runtime guard implemented",
    "existing transition result changed",
    "Remote Blackboard API runtime created",
    "connector created",
    "tag created",
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
    print(f"\nXX v0.7.4-R readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print(
        "\nv0.7.4-R Topology + Queue + Audit Display Closeout readiness: ALL PASS"
    )
    sys.exit(0)
