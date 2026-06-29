"""v0.7.4-A readiness check: Core Topology / Dashboard Update / Core Independence Plan.

Plan / current-state verification. Checks that the v0.7.4-A core topology planning
document exists and contains the required sections (1-20), the current-master
marker, the v0.7.3 completion markers, the GitHub / Windows WSL / Replit
positioning, the Dashboard Update Rule, the Core Independence Rule, the local-vs-
Replit queue boundary, the Remote Blackboard future-only direction, the Blackboard
message family, the Decision Message positioning, the Hermes ↔ Blackboard ↔
OpenClaw loop, the safe system posture, and the next recommended step — and that
it asserts no unsafe "enabled / connected / production-host / auto-sync / shared-
write / implemented / decision-message-is-command / approve-triggers / POST-to /
clicked / seeded / cleaned-up / live-write-performed" claim and contains no secret.

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
    ROOT
    / "docs"
    / "HERMES_OPENCLAW_CORE_TOPOLOGY_DASHBOARD_UPDATE_CORE_INDEPENDENCE_PLAN_V0_7_4_A.md"
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
ok("v0.7.4-A plan doc 存在") if DOC_PATH.exists() else xx("v0.7.4-A plan doc 存在")
if not DOC_PATH.exists():
    print("\nXX plan doc 不存在，無法繼續")
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
    "4. Relationship to v0.7.3-R",
    "5. Core topology summary",
    "6. GitHub positioning",
    "7. Windows WSL positioning",
    "8. Replit positioning",
    "9. Dashboard Update Rule",
    "10. Core Independence Rule",
    "11. Local queue vs Replit queue boundary",
    "12. Remote Blackboard API / shared DB future path",
    "13. Blackboard message family",
    "14. Approval decision events as Decision Messages",
    "15. Hermes ↔ Blackboard ↔ OpenClaw loop",
    "16. Current safe system posture",
    "17. Deployment boundary decisions",
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
    "v0.7.4-A",
    "Core Topology / Dashboard Update / Core Independence Plan",
    # current master
    "HEAD = origin/master = 1ea988ef1ed089336f720358e0d24f4164cf572a",
    "docs: close out approval decision layer",
    # v0.7.3 completion markers
    "v0.7.3 Approval Decision Layer is complete.",
    "approval_decision_events are Decision Messages.",
    "Decision Messages are blackboard audit records, not execution commands.",
    "approve is not execute.",
    "Owner decision event is not Worker dispatch.",
    "No Worker / OpenClaw / Hermes / Google Sheets execution was enabled.",
    # GitHub positioning
    "GitHub = clean source of truth for code and docs.",
    "GitHub is not the queue database.",
    "GitHub is not the blackboard database.",
    "GitHub is not a secrets store.",
    "GitHub must not store .env, tokens, credentials, local queue DB, logs, private keys, or production secrets.",
    # Windows WSL positioning
    "Windows WSL = primary local development environment.",
    "Windows WSL is responsible for code edits, tests, commits, pushes, and local development validation.",
    "Windows WSL may have its own local queue and local logs.",
    "Windows WSL local queue does not automatically sync to Replit.",
    # Replit positioning
    "Replit = remote observation station / Preview Dashboard.",
    "Replit is not the production Worker host.",
    "Replit is not the production OpenClaw host.",
    "Replit is not the production Hermes host.",
    "Replit is not the production queue database.",
    "Replit is not the high-risk external execution host.",
    "Replit Dashboard is a remote monitor, not the factory itself.",
    # Dashboard Update Rule
    "Dashboard update means git pull plus Dashboard restart.",
    "Dashboard update only updates UI / dashboard code on that environment.",
    "Dashboard update does not sync WSL local queue.",
    "Dashboard update does not update Hermes memory.",
    "Dashboard update does not update OpenClaw execution state.",
    "Dashboard update does not start Worker.",
    "Dashboard update does not call OpenClaw.",
    "Dashboard update does not call Hermes.",
    "Dashboard update does not write Google Sheets.",
    "Dashboard update does not trigger webhook.",
    "Dashboard update does not cause external side effects.",
    # Core Independence Rule
    "The core blackboard loop should not depend on whether Replit Dashboard is updated.",
    "Dashboard can be stale.",
    "Dashboard can be offline.",
    "Dashboard can be temporarily unavailable.",
    "Core Blackboard / Queue / Worker / Hermes / OpenClaw should eventually live on a core host or shared backend.",
    "Dashboard is an Owner observation and review surface, not the system heart.",
    # local queue vs Replit queue boundary
    "Current Windows WSL local queue and Replit local queue are separate.",
    "They do not automatically sync.",
    "Replit pull updates code, not queue data.",
    "GitHub push updates code, not queue data.",
    "A shared blackboard requires a future Remote Blackboard API or shared DB.",
    # Remote Blackboard future-only
    "Remote Blackboard API / shared DB is future planning only in v0.7.4-A.",
    "v0.7.4-A does not implement production DB.",
    "v0.7.4-A does not migrate queues.",
    "v0.7.4-A does not enable shared writes.",
    "v0.7.4-A does not create webhooks.",
    "v0.7.4-A does not start Worker.",
    # Blackboard message family
    "Task Message",
    "Decision Message",
    "Result Message",
    "Advice Message",
    # Decision Message positioning
    "Decision Messages are blackboard audit records.",
    "Decision Messages are not Worker commands.",
    "Decision Messages are not OpenClaw commands.",
    "Decision Messages are not Hermes instructions.",
    # Hermes ↔ Blackboard ↔ OpenClaw loop
    "Hermes writes to Blackboard.",
    "OpenClaw / Worker reads from Blackboard.",
    "OpenClaw / Worker reports Result Messages back to Blackboard.",
    "Hermes reads Result Messages and produces Advice Messages.",
    "Owner monitors, approves, rejects, cancels, archives, and can interrupt the loop.",
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
    "v0.7.4-B — Queue / Blackboard Lifecycle Plan",
    "v0.7.4-B must remain plan-first.",
    "It should define Queue / Blackboard lifecycle and message family before any runtime enforcement.",
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
    "Replit is the production Worker host",
    "Replit is the production OpenClaw host",
    "Replit is the production Hermes host",
    "Replit is the production queue database",
    "Replit is the high-risk external execution host",
    "GitHub is the queue database",
    "GitHub is the blackboard database",
    "GitHub is a secrets store",
    "Dashboard update starts Worker",
    "Dashboard update calls OpenClaw",
    "Dashboard update calls Hermes",
    "Dashboard update writes Google Sheets",
    "Dashboard update triggers webhook",
    "Dashboard update causes external side effects",
    "WSL local queue automatically syncs to Replit",
    "Replit local queue automatically syncs to WSL",
    "Remote Blackboard API implemented",
    "production DB implemented",
    "shared writes enabled",
    "webhook receiver created",
    "Decision Messages are Worker commands",
    "Decision Messages are OpenClaw commands",
    "Decision Messages are Hermes instructions",
    "Owner approval triggers Worker execution",
    "approve triggers dispatch",
    "approve calls OpenClaw",
    "approve calls Hermes",
    "approve writes Google Sheets",
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
    print(f"\nXX v0.7.4-A readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print(
        "\nv0.7.4-A Core Topology / Dashboard Update / Core Independence Plan readiness: ALL PASS"
    )
    sys.exit(0)
