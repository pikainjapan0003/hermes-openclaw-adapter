"""v0.7.4-F readiness check: Safe Local Cleanup Tool (dry-run-only).

Verifies that the v0.7.4-F dry-run cleanup tool's five files exist and carry the
required markers: the helper function and its fixed safety values (and that the
helper / CLI import no QueueStore / app.main / sqlite / requests / urllib / socket /
subprocess / secrets), the doc sections (1-22), the current-master marker, the
v0.7.4-E completion markers, the tool boundary, the explicit-input requirement, the
candidate classifier markers, the blocked-item rules, the apply-rejection markers,
the QueueStore boundary, the Route / POST boundary, the runtime / external side-
effect boundary, and the next recommended step — and that the doc asserts no unsafe
"enabled / connected / cleanup-applied / tasks-deleted / apply-allowed / dry_run-
false / would-*-true / external-side-effects-true / POST-to / started / called /
written / created / changed / implemented" claim and contains no secret.

This script only reads files. It does NOT read .env, credentials, tokens, or
secrets, makes no network call, imports no app logic, starts no Worker, and calls
no OpenClaw / Hermes / Google Sheets.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
PASS = []
FAIL = []

HELPER_PATH = ROOT / "app" / "demo_task_cleanup_v0_7.py"
CLI_PATH = ROOT / "scripts" / "demo_task_cleanup_dry_run_v0_7_4_f.py"
DOC_PATH = ROOT / "docs" / "HERMES_OPENCLAW_SAFE_LOCAL_CLEANUP_TOOL_V0_7_4_F.md"
TEST_PATH = ROOT / "scripts" / "test_demo_task_cleanup_dry_run_v0_7_4_f.py"
SELF_PATH = ROOT / "scripts" / "check_hermes_openclaw_safe_local_cleanup_tool_v0_7_4_f.py"


def ok(label):
    PASS.append(label)
    print(f"  ok : {label}")


def xx(label):
    FAIL.append(label)
    print(f"  XX : {label}")


# ---------------------------------------------------------------------------
# [1] 必要檔案存在
# ---------------------------------------------------------------------------
print("[1] 必要檔案存在")
REQUIRED_FILES = [HELPER_PATH, CLI_PATH, DOC_PATH, SELF_PATH, TEST_PATH]
missing = False
for p in REQUIRED_FILES:
    if p.exists():
        ok(f"檔案存在：{p.relative_to(ROOT)}")
    else:
        xx(f"檔案存在：{p.relative_to(ROOT)}")
        missing = True
if missing:
    print("\nXX 必要檔案缺失，無法繼續")
    sys.exit(1)

helper_src = HELPER_PATH.read_text(encoding="utf-8")
cli_src = CLI_PATH.read_text(encoding="utf-8")
doc = DOC_PATH.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# [2] helper：函式 + 固定安全值
# ---------------------------------------------------------------------------
print("[2] helper 函式與固定安全值")
HELPER_MARKERS = [
    "def derive_demo_task_cleanup_dry_run_report",
    '"execution_mode": "dry_run_only"',
    '"dry_run": True',
    '"apply_requested": False',
    '"apply_allowed": False',
    '"would_delete": False',
    '"would_archive": False',
    '"would_modify": False',
    '"external_side_effects": False',
    '"owner_approval_required": True',
    # candidate classifier markers
    "demo_task",
    "sample_task",
    "preview_task",
    "test_task",
    "cleanup_classification",
    "task_classification",
    # blocked item reasons
    "no explicit demo/sample/preview/test marker",
    "target_environment is not local or preview",
    "production marker present",
    "external side effect marker present",
    "secret-like marker present",
    "origin unknown",
    "needed for active validation without owner_approved_replacement",
]
for token in HELPER_MARKERS:
    ok(f"helper 含「{token}」") if token in helper_src else xx(f"helper 含「{token}」")

# ---------------------------------------------------------------------------
# [3] helper / CLI import 邊界（只看 import 行）
# ---------------------------------------------------------------------------
print("[3] helper / CLI import 邊界")
FORBIDDEN_IMPORT_TOKENS = [
    "app.main",
    "queue_store",
    "QueueStore",
    "sqlite",
    "requests",
    "urllib",
    "socket",
    "subprocess",
    "secrets",
]


def _import_lines(src):
    return [
        ln.strip()
        for ln in src.splitlines()
        if ln.strip().startswith("import ") or ln.strip().startswith("from ")
    ]


for label, src in (("helper", helper_src), ("CLI", cli_src)):
    violations = [
        (ln, tok) for ln in _import_lines(src) for tok in FORBIDDEN_IMPORT_TOKENS if tok in ln
    ]
    if violations:
        for ln, tok in violations:
            xx(f"{label} 不得 import「{tok}」（{ln}）")
    else:
        ok(f"{label} 未 import QueueStore / app.main / sqlite / requests / urllib / socket / subprocess / secrets")

# ---------------------------------------------------------------------------
# [4] CLI：explicit input + apply rejection
# ---------------------------------------------------------------------------
print("[4] CLI explicit input 與 apply rejection")
CLI_MARKERS = [
    '"--input"',
    "required=True",
    "_reject_apply_like_arguments",
    '"apply" in token',
    "sys.exit(2)",
    "stdout",
]
for token in CLI_MARKERS:
    ok(f"CLI 含「{token}」") if token in cli_src else xx(f"CLI 含「{token}」")
# CLI 不得提供 apply path：不得出現「執行 apply」的字樣
ok("CLI 不含 apply 執行字樣「def apply」") if "def apply" not in cli_src else xx("CLI 不含「def apply」")

# ---------------------------------------------------------------------------
# [5] 文件章節（1-22）
# ---------------------------------------------------------------------------
print("[5] 文件章節")
REQUIRED_SECTIONS = [
    "1. Purpose",
    "2. Current master",
    "3. Scope",
    "4. Relationship to v0.7.4-E",
    "5. Tool boundary",
    "6. Helper contract",
    "7. CLI contract",
    "8. Explicit input requirement",
    "9. Candidate classifier",
    "10. Blocked item rules",
    "11. Dry-run report format",
    "12. Fixed safety values",
    "13. Apply prohibition in v0.7.4-F",
    "14. Owner approval boundary",
    "15. Local queue vs Replit queue boundary",
    "16. QueueStore boundary",
    "17. Route / POST boundary",
    "18. Runtime / external side-effect boundary",
    "19. Tests and readiness",
    "20. Non-goals",
    "21. Acceptance criteria",
    "22. Next recommended step",
]
for section in REQUIRED_SECTIONS:
    ok(f"doc 含章節「{section}」") if section in doc else xx(f"doc 含章節「{section}」")

# ---------------------------------------------------------------------------
# [6] 文件 markers
# ---------------------------------------------------------------------------
print("[6] 文件 markers")
REQUIRED = [
    # version
    "v0.7.4-F",
    "Safe Local Cleanup Tool",
    # current master
    "HEAD = origin/master = 110285ba7f243f0e75f1a5208f95ad0d8f46c655",
    "docs: plan demo task cleanup safety",
    # v0.7.4-E completion
    "v0.7.4-E Demo Task Cleanup Plan is complete.",
    "Cleanup Plan is not cleanup apply.",
    "Cleanup dry-run is not cleanup apply.",
    "Cleanup apply requires separate Owner approval.",
    "Cleanup apply requires an explicit apply flag.",
    "Cleanup apply requires a second confirmation flag.",
    "WSL cleanup tooling must not clean Replit queue.",
    # tool boundary
    "v0.7.4-F Safe Local Cleanup Tool is dry-run-only.",
    "v0.7.4-F does not implement cleanup apply.",
    "v0.7.4-F does not delete tasks.",
    "v0.7.4-F does not archive tasks.",
    "v0.7.4-F does not modify queue DB.",
    "v0.7.4-F does not modify local queue data.",
    "v0.7.4-F does not modify Replit queue data.",
    "v0.7.4-F does not read real queue DB.",
    "v0.7.4-F requires explicit JSON input.",
    "v0.7.4-F writes report to stdout only.",
    # fixed safety values (documented)
    'execution_mode = "dry_run_only"',
    "dry_run = True",
    "apply_requested = False",
    "apply_allowed = False",
    "would_delete = False",
    "would_archive = False",
    "would_modify = False",
    "external_side_effects = False",
    "owner_approval_required = True",
    # dry-run report format fields
    "report_id",
    "generated_at",
    "candidate_count",
    "blocked_count",
    "candidates",
    "blocked_items",
    "source_queue",
    "target_environment",
    "rollback_note",
    "safety_notes",
    # candidate classifier
    "metadata.demo_task = true",
    "metadata.sample_task = true",
    "metadata.preview_task = true",
    "metadata.test_task = true",
    "metadata.cleanup_classification = demo/sample/preview/test",
    "metadata.task_classification = demo/sample/preview/test",
    # blocked item rules
    "A task with no explicit demo marker is blocked.",
    "A target_environment that is not local or preview blocks every task.",
    "A task with a production marker is blocked.",
    "A task with an external side effect marker is blocked.",
    "A task with a secret-like marker is blocked.",
    "A task with unknown origin is blocked.",
    "A task needed for active validation is blocked unless metadata.owner_approved_replacement = true.",
    # explicit input requirement
    "The CLI requires an explicit `--input` JSON file",
    # apply prohibition
    "No apply path exists in v0.7.4-F.",
    "The CLI must reject --apply.",
    "The CLI must reject --confirm-apply.",
    "The CLI must reject apply-like arguments.",
    "Owner approval of v0.7.4-F does not approve cleanup apply.",
    # QueueStore boundary
    "QueueStore runtime behavior is unchanged in v0.7.4-F.",
    "v0.7.4-F does not modify app/queue_store.py.",
    "v0.7.4-F does not add QueueStore methods.",
    "v0.7.4-F does not modify payload persistence.",
    "v0.7.4-F does not modify status persistence.",
    # Route / POST boundary
    "v0.7.4-F does not add POST routes.",
    "v0.7.4-F does not add cleanup route.",
    "v0.7.4-F does not add cleanup button.",
    "v0.7.4-F does not add cleanup form.",
    # safe posture / side-effect boundary
    "no Worker",
    "no OpenClaw call",
    "no Hermes call",
    "no Google Sheets write",
    # next recommended step
    "v0.7.4-F-R — Safe Local Cleanup Tool Closeout",
    "No Replit POST validation is required for v0.7.4-F.",
    "No Replit queue cleanup is allowed.",
]
for token in REQUIRED:
    ok(f"doc 含「{token}」") if token in doc else xx(f"doc 含「{token}」")

# ---------------------------------------------------------------------------
# [7] 禁止包含的不安全聲明 / 機密（掃 doc，先 scrub 合法否定句）
# ---------------------------------------------------------------------------
print("[7] 禁止包含的不安全聲明 / 機密")
SAFE_NEGATIONS = []  # doc 以否定句撰寫，不含 forbidden 子字串
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
    print(f"\nXX v0.7.4-F readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print("\nv0.7.4-F Safe Local Cleanup Tool readiness: ALL PASS")
    sys.exit(0)
