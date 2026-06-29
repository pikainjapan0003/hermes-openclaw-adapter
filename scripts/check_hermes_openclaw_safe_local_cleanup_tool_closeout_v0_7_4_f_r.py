"""v0.7.4-F-R readiness check: Safe Local Cleanup Tool Closeout.

Closeout / current-state verification. Checks that the v0.7.4-F-R closeout document
exists and contains the required sections (1-20), the current-master marker, the
v0.7.4-F completion markers, the five v0.7.4-F file markers, the helper validation
markers, the fixed safety value markers, the CLI validation markers, the test / check
PASS markers, the safety grep summary markers, the No-Replit-POST validation markers,
the cleanup / apply forbidden-boundary markers, the QueueStore / queue-data boundary
markers, the runtime / external side-effect boundary markers, and the next recommended
step — and that it asserts no unsafe "applied / deleted / archived / modified / enabled
/ connected / POST-was-sent / started / called / written / created / added / changed /
implemented" claim and contains no secret.

The document is allowed to contain safe negations (e.g. "No Replit Preview POST was
sent.", "No live local queue write validation."); those are scrubbed before the
forbidden scan so they are not mis-flagged.

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
    / "HERMES_OPENCLAW_SAFE_LOCAL_CLEANUP_TOOL_CLOSEOUT_V0_7_4_F_R.md"
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
ok("v0.7.4-F-R closeout doc 存在") if DOC_PATH.exists() else xx("v0.7.4-F-R closeout doc 存在")
if not DOC_PATH.exists():
    print("\nXX closeout doc 不存在，無法繼續")
    sys.exit(1)

doc = DOC_PATH.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# [2] 必須包含的章節（1-20）
# ---------------------------------------------------------------------------
print("[2] 必須包含的章節")
REQUIRED_SECTIONS = [
    "1. Purpose",
    "2. Current master",
    "3. Scope",
    "4. Relationship to v0.7.4-F",
    "5. Relationship to v0.7.4-E",
    "6. Files added in v0.7.4-F",
    "7. Dry-run-only helper validation",
    "8. CLI validation",
    "9. Synthetic test validation",
    "10. Readiness validation",
    "11. Prior regression checks",
    "12. Safety grep summary",
    "13. No Replit POST validation required",
    "14. No cleanup / apply boundary",
    "15. QueueStore / queue data boundary",
    "16. Runtime / external side-effect boundary",
    "17. Current safe system posture",
    "18. Non-goals",
    "19. Acceptance criteria",
    "20. Next recommended step",
]
for section in REQUIRED_SECTIONS:
    ok(f"doc 含章節「{section}」") if section in doc else xx(f"doc 含章節「{section}」")

# ---------------------------------------------------------------------------
# [3] 必須包含的 markers
# ---------------------------------------------------------------------------
print("[3] 必須包含的 markers")
REQUIRED = [
    # version
    "v0.7.4-F-R",
    "Safe Local Cleanup Tool",
    # current master
    "HEAD = origin/master = dce39f871f0119f72d24f8cf2ea6a54ef0bf6de0",
    "feat: add dry-run demo task cleanup tool",
    # v0.7.4-F completion markers
    "v0.7.4-F Safe Local Cleanup Tool is complete.",
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
    # five v0.7.4-F file markers
    "app/demo_task_cleanup_v0_7.py",
    "scripts/demo_task_cleanup_dry_run_v0_7_4_f.py",
    "docs/HERMES_OPENCLAW_SAFE_LOCAL_CLEANUP_TOOL_V0_7_4_F.md",
    "scripts/check_hermes_openclaw_safe_local_cleanup_tool_v0_7_4_f.py",
    "scripts/test_demo_task_cleanup_dry_run_v0_7_4_f.py",
    # helper validation markers
    "derive_demo_task_cleanup_dry_run_report exists.",
    "Helper is pure dry-run classifier.",
    "Helper does not import app.main.",
    "Helper does not import QueueStore.",
    "Helper does not read real queue DB.",
    "Helper does not mutate input.",
    "Helper does not delete tasks.",
    "Helper does not archive tasks.",
    "Helper does not modify queue data.",
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
    # CLI validation markers
    "CLI requires explicit JSON input.",
    "CLI writes JSON report to stdout only.",
    "CLI rejects --apply.",
    "CLI rejects --confirm-apply.",
    "CLI rejects apply-like arguments.",
    "CLI provides no apply path.",
    "CLI does not read real queue DB.",
    "CLI does not POST.",
    # test / check PASS markers
    "v0.7.4-F readiness: ALL PASS.",
    "v0.7.4-F dry-run tool test: ALL PASS.",
    "v0.7.4-E check: ALL PASS.",
    "v0.7.4-D-R check: ALL PASS.",
    "v0.7.4-D readiness and helper test: ALL PASS.",
    "v0.7.4-C / B / A checks: ALL PASS.",
    "v0.7.3 checks: ALL PASS.",
    "prior F-line checks: ALL PASS.",
    "compileall app + scripts: PASS.",
    # safety grep summary markers
    "No real unsafe claim was found.",
    "No real secret was found.",
    "Helper secret-like key names are defensive markers, not secret values.",
    "Synthetic test fixture secret-like value is fake and used only to verify blocking/redaction behavior.",
    "Readiness forbidden-pattern matches are benign.",
    # No Replit POST validation markers
    "No Replit POST validation is required for v0.7.4-F.",
    "No Replit queue cleanup is allowed.",
    "No Replit Preview POST was sent.",
    "No Replit queue data was modified.",
    # cleanup / apply forbidden-boundary markers
    "No cleanup demo task.",
    "No cleanup apply.",
    "No --apply.",
    "No task deletion.",
    "No task archive.",
    "No cleanup route.",
    "No cleanup button.",
    "No cleanup form.",
    # QueueStore / queue-data boundary markers
    "No queue DB change.",
    "No local queue data change.",
    "No Replit queue data change.",
    "No real queue DB read.",
    "No QueueStore runtime behavior change.",
    "No app/queue_store.py change.",
    # runtime / external side-effect boundary markers
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
    "No approval routes change.",
    "No dashboard auth change.",
    "No status transition change.",
    "No runtime guard.",
    "No existing transition result change.",
    # next recommended step
    "v0.7.4-R — Topology + Queue + Audit Display Closeout",
    "v0.7.4-R must remain closeout / docs-only unless separately approved.",
    "v0.7.4-R must not perform cleanup apply.",
    "v0.7.4-R must not start Worker / OpenClaw / Hermes / Google Sheets.",
]
for token in REQUIRED:
    ok(f"doc 含「{token}」") if token in doc else xx(f"doc 含「{token}」")

# ---------------------------------------------------------------------------
# [4] 禁止包含的不安全聲明 / 機密
#     先移除合法的安全否定句（其字面含 forbidden 子字串），再掃 forbidden。
# ---------------------------------------------------------------------------
print("[4] 禁止包含的不安全聲明 / 機密")
SAFE_NEGATIONS = [
    "No Replit Preview POST was sent",        # 含 'POST ... was sent'
    "No live local queue write validation",   # 含 'queue write validation'
    "No Replit queue cleanup is allowed",     # 含 'Replit queue clean...'
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
    print(f"\nXX v0.7.4-F-R readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print(
        "\nv0.7.4-F-R Safe Local Cleanup Tool Closeout readiness: ALL PASS"
    )
    sys.exit(0)
