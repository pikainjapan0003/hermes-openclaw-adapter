"""v0.7.4-E readiness check: Demo Task Cleanup Plan.

Plan / current-state verification. Checks that the v0.7.4-E demo task cleanup
planning document exists and contains the required sections (1-27), the current-
master marker, the v0.7.4-D-R / D / C / B / A completion markers, the demo task
definition, the cleanup / non-cleanup candidate rules, the cleanup safety
conditions, the dry-run report format with its fixed safety values, the Owner
approval gate, the plan / dry-run / apply distinction, the local-vs-Replit queue
boundary, the QueueStore boundary, the Route / POST boundary, the safe system
posture, and the next recommended step — and that it asserts no unsafe "enabled /
connected / cleanup-applied / tasks-deleted / apply-allowed / dry_run-false /
external-side-effects-true / POST-to / started / called / written / created /
changed / implemented" claim and contains no secret.

The document is allowed to contain safe negations (e.g. "No cleanup applied.");
those are scrubbed before the forbidden scan so they are not mis-flagged.

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

DOC_PATH = ROOT / "docs" / "HERMES_OPENCLAW_DEMO_TASK_CLEANUP_PLAN_V0_7_4_E.md"


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
ok("v0.7.4-E plan doc 存在") if DOC_PATH.exists() else xx("v0.7.4-E plan doc 存在")
if not DOC_PATH.exists():
    print("\nXX plan doc 不存在，無法繼續")
    sys.exit(1)

doc = DOC_PATH.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# [2] 必須包含的章節（1-27）
# ---------------------------------------------------------------------------
print("[2] 必須包含的章節")
REQUIRED_SECTIONS = [
    "1. Purpose",
    "2. Current master",
    "3. Scope",
    "4. Relationship to v0.7.4-D-R",
    "5. Relationship to v0.7.4-D",
    "6. Relationship to v0.7.4-C",
    "7. Relationship to v0.7.4-B",
    "8. Relationship to v0.7.4-A",
    "9. Why demo task cleanup needs a plan",
    "10. Demo task definition",
    "11. Cleanup candidate rules",
    "12. Non-cleanup candidate rules",
    "13. Cleanup safety conditions",
    "14. Dry-run cleanup report format",
    "15. Owner approval gate",
    "16. Plan vs dry-run vs apply",
    "17. Local queue vs Replit queue boundary",
    "18. QueueStore boundary",
    "19. Route / POST boundary",
    "20. Runtime / external side-effect boundary",
    "21. Forbidden cleanup actions",
    "22. Future v0.7.4-F Safe Local Cleanup Tool boundary",
    "23. Current safe system posture",
    "24. Tests and readiness",
    "25. Non-goals",
    "26. Acceptance criteria",
    "27. Next recommended step",
]
for section in REQUIRED_SECTIONS:
    ok(f"doc 含章節「{section}」") if section in doc else xx(f"doc 含章節「{section}」")

# ---------------------------------------------------------------------------
# [3] 必須包含的 markers
# ---------------------------------------------------------------------------
print("[3] 必須包含的 markers")
REQUIRED = [
    # version
    "v0.7.4-E",
    "Demo Task Cleanup Plan",
    # current master
    "HEAD = origin/master = 17ddd421b5f1c482e2ca74b0933d11b1bfe2c332",
    "docs: close out audit trail display replit validation",
    # v0.7.4-D-R completion
    "v0.7.4-D-R Audit Trail Display Replit GET-only Validation Closeout is complete.",
    "Replit GET-only validation passed.",
    "No POST was sent.",
    "No queue write validation was performed.",
    "No Worker / OpenClaw / Hermes / Google Sheets was called.",
    # v0.7.4-D completion
    "v0.7.4-D Audit Trail Display is complete.",
    "Audit Trail Display is read-only.",
    "Audit Trail Display does not change lifecycle state.",
    "Audit Trail Display does not enforce guard.",
    "Audit Trail Display does not grant execution permission.",
    "Audit Trail Display does not dispatch Worker.",
    "Audit Trail Display does not call OpenClaw.",
    "Audit Trail Display does not call Hermes.",
    "Audit Trail Display does not write Google Sheets.",
    "Result Message remains future-only in v0.7.4-E.",
    "Advice Message remains future-only in v0.7.4-E.",
    # v0.7.4-C completion
    "v0.7.4-C State Transition Guard Plan is complete.",
    "State Transition Guard is a safety contract.",
    "v0.7.4-C does not modify current status transitions.",
    "v0.7.4-C does not enforce runtime guards.",
    # v0.7.4-B completion
    "v0.7.4-B Queue / Blackboard Lifecycle Plan is complete.",
    "Task Message",
    "Decision Message",
    "Result Message",
    "Advice Message",
    "Decision Message is audit record, not command.",
    "approve is not execute.",
    "Owner decision event is not Worker dispatch.",
    # v0.7.4-A completion
    "v0.7.4-A Core Topology / Dashboard Update / Core Independence Plan is complete.",
    "GitHub is clean source of code and docs, not queue DB or secrets store.",
    "Windows WSL is primary local development environment.",
    "Replit is remote observation station / Preview Dashboard.",
    "Dashboard update means git pull plus Dashboard restart.",
    "Dashboard update does not start Worker.",
    "Dashboard update does not call OpenClaw.",
    "Dashboard update does not call Hermes.",
    "Dashboard update does not write Google Sheets.",
    "Current Windows WSL local queue and Replit local queue are separate.",
    # demo task definition
    "Demo task is a local / preview sample task used for UI validation, route validation, or readiness demonstration.",
    "Demo task is not production work.",
    "Demo task cleanup must not affect production task data.",
    "Demo task cleanup must not be inferred from task name alone.",
    "Demo task cleanup requires explicit classification rules.",
    # cleanup candidate rules
    "A cleanup candidate must be explicitly identified as demo / sample / preview / test data.",
    "A cleanup candidate must be local-only or preview-only.",
    "A cleanup candidate must have no production owner dependency.",
    "A cleanup candidate must not be linked to external execution.",
    "A cleanup candidate must not contain secrets.",
    "A cleanup candidate must not be needed for current validation unless Owner approves replacement.",
    "A cleanup candidate must appear in a dry-run report before apply.",
    # non-cleanup candidate rules
    "Production-looking tasks are not cleanup candidates.",
    "Tasks with unclear origin are not cleanup candidates.",
    "Tasks with external side effect history are not cleanup candidates.",
    "Tasks with missing classification are not cleanup candidates.",
    "Tasks needed for active validation are not cleanup candidates unless replacement is planned.",
    "Tasks containing secrets must not be printed and must not be cleaned by automated tooling.",
    "Tasks in Replit queue must not be cleaned from WSL tooling.",
    "Tasks in remote shared DB are out of scope.",
    # cleanup safety conditions
    "Cleanup Plan is not cleanup apply.",
    "Cleanup dry-run is not cleanup apply.",
    "Cleanup apply requires separate Owner approval.",
    "Cleanup apply requires an explicit apply flag.",
    "Cleanup apply requires a second confirmation flag.",
    "Cleanup apply must be local-only in v0.7.4-F.",
    "Cleanup apply must not touch Replit Preview.",
    "Cleanup apply must not touch production DB.",
    "Cleanup apply must not touch remote shared DB.",
    "Cleanup apply must not call Worker.",
    "Cleanup apply must not call OpenClaw.",
    "Cleanup apply must not call Hermes.",
    "Cleanup apply must not write Google Sheets.",
    "Cleanup apply must not create webhook.",
    # dry-run report format fields
    "report_id",
    "generated_at",
    "execution_mode",
    "dry_run",
    "apply_requested",
    "apply_allowed",
    "candidate_count",
    "blocked_count",
    "candidates",
    "blocked_items",
    "reason",
    "source_queue",
    "target_environment",
    "would_delete",
    "would_archive",
    "would_modify",
    "external_side_effects",
    "owner_approval_required",
    "rollback_note",
    # fixed safety values
    "dry_run = True",
    "apply_requested = False",
    "apply_allowed = False",
    "external_side_effects = False",
    "owner_approval_required = True",
    # Owner approval gate
    "Owner approval for this plan does not approve cleanup apply.",
    "Owner review of dry-run report does not approve cleanup apply.",
    "Cleanup apply requires separate explicit Owner approval.",
    "Cleanup apply requires exact command approval.",
    "Cleanup apply requires local-only target confirmation.",
    "Cleanup apply requires rollback note confirmation.",
    # plan vs dry-run vs apply
    "Plan = documentation and safety contract only.",
    "Dry-run = local read-only candidate report only.",
    "Apply = local data-changing cleanup action, prohibited until separately approved.",
    # local vs Replit queue
    "Windows WSL local queue and Replit local queue are separate.",
    "Replit pull updates code, not queue data.",
    "GitHub push updates code, not queue data.",
    "WSL cleanup tooling must not clean Replit queue.",
    "Replit Preview GET validation must not become POST or cleanup.",
    "Remote shared DB is future-only.",
    # QueueStore boundary
    "QueueStore runtime behavior is unchanged in v0.7.4-E.",
    "v0.7.4-E does not modify app/queue_store.py.",
    "v0.7.4-E does not add QueueStore methods.",
    "v0.7.4-E does not delete tasks.",
    "v0.7.4-E does not archive tasks.",
    "v0.7.4-E does not modify payload persistence.",
    "v0.7.4-E does not modify status persistence.",
    # Route / POST boundary
    "v0.7.4-E does not add POST routes.",
    "v0.7.4-E does not modify approval POST behavior.",
    "v0.7.4-E does not modify reject POST behavior.",
    "v0.7.4-E does not modify cancel POST behavior.",
    "v0.7.4-E does not modify retry POST behavior.",
    "v0.7.4-E does not modify archive POST behavior.",
    "v0.7.4-E does not add cleanup route.",
    "v0.7.4-E does not add cleanup button.",
    "v0.7.4-E does not add cleanup form.",
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
    "v0.7.4-F — Safe Local Cleanup Tool",
    "v0.7.4-F must start with dry-run only.",
    "v0.7.4-F apply must require separate Owner approval.",
    "v0.7.4-F apply must require dual explicit flags.",
    "v0.7.4-F must remain local-only.",
]
for token in REQUIRED:
    ok(f"doc 含「{token}」") if token in doc else xx(f"doc 含「{token}」")

# ---------------------------------------------------------------------------
# [4] 禁止包含的不安全聲明 / 機密
#     先移除合法的安全否定句（其字面含 forbidden 子字串），再掃 forbidden。
# ---------------------------------------------------------------------------
print("[4] 禁止包含的不安全聲明 / 機密")
SAFE_NEGATIONS = [
    "No cleanup applied",  # 含 'cleanup applied'
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
    "Replit queue cleaned",
    "production DB cleaned",
    "remote shared DB cleaned",
    "cleanup apply approved",
    "apply_allowed = True",
    "apply_requested = True",
    "dry_run = False",
    "external_side_effects = True",
    "Owner approval granted cleanup apply",
    "POST to Replit Preview",
    "POST to real queue",
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
    print(f"\nXX v0.7.4-E readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print("\nv0.7.4-E Demo Task Cleanup Plan readiness: ALL PASS")
    sys.exit(0)
