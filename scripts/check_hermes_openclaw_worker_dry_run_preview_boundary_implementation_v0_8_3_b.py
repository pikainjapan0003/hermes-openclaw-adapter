"""v0.8.3-B readiness check: Worker Dry-run Preview Boundary Implementation (synthetic local-only).

Pure local filesystem + git metadata validation, plus a local import of this round's own standalone
builder module to confirm its returned model stays read-only and safe. This script reads only the
v0.8.3-B doc/fixture/builder/readiness-script and confirms the tracked/untracked state of those four
files and the surfaces they must not touch (app/main.py, templates/system.html, static/dashboard.css,
the v0.8.3-A plan doc/readiness script, the v0.8.2-F closeout doc/readiness script, the v0.8.2-E
validation script, the v0.8.2-D plan doc/readiness script, the v0.8.2-C validation script, the v0.8.2-B
plan doc/readiness script, the v0.8.2-A validation script, the P loader, the V adapter, the old v0.8.1
fixture JSON, and the W/X/Y/Z artifacts). It uses `git` read-only (ls-files / diff / status / merge-base)
to confirm tracked status, ancestry, and that no tracked file was modified; it never modifies the git
index.

It does NOT import app runtime, Dashboard runtime, QueueStore, Worker/OpenClaw/Hermes/Google Sheets
integration, the v0.8.1-P loader, or the v0.8.1-V adapter; it never starts a server; it reads no real
queue DB, sends no POST, makes no network call, reads no secrets, writes no repo file, and modifies no
git index. It only imports this round's own builder module (standard library only) to call its public
function and inspect the returned dict.
"""
from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

B_DOC_REL = "docs/HERMES_OPENCLAW_WORKER_DRY_RUN_PREVIEW_BOUNDARY_IMPLEMENTATION_V0_8_3_B.md"
B_DOC_PATH = REPO_ROOT / B_DOC_REL
B_FIXTURE_REL = "fixtures/local_mock_data/hermes_openclaw_worker_dry_run_preview_v0_8_3_b.json"
B_FIXTURE_PATH = REPO_ROOT / B_FIXTURE_REL
B_BUILDER_REL = "scripts/worker_dry_run_preview_boundary_v0_8_3_b.py"
B_BUILDER_PATH = REPO_ROOT / B_BUILDER_REL
B_SCRIPT_REL = "scripts/check_hermes_openclaw_worker_dry_run_preview_boundary_implementation_v0_8_3_b.py"
B_SCRIPT_PATH = REPO_ROOT / B_SCRIPT_REL

MAIN_PY_REL = "app/main.py"
SYSTEM_HTML_REL = "templates/system.html"
DASHBOARD_CSS_REL = "static/dashboard.css"

A_DOC_REL = "docs/HERMES_OPENCLAW_WORKER_DRY_RUN_PREVIEW_BOUNDARY_PLAN_V0_8_3_A.md"
A_SCRIPT_REL = "scripts/check_hermes_openclaw_worker_dry_run_preview_boundary_plan_v0_8_3_a.py"

F_DOC_REL = "docs/HERMES_OPENCLAW_DASHBOARD_READ_ONLY_PREVIEW_VALIDATION_CLOSEOUT_HANDOFF_PLAN_V0_8_2_F.md"
F_SCRIPT_REL = "scripts/check_hermes_openclaw_dashboard_read_only_preview_validation_closeout_handoff_plan_v0_8_2_f.py"

E_SCRIPT_REL = "scripts/check_hermes_openclaw_dashboard_read_only_preview_ui_validation_hardening_v0_8_2_e.py"

D_DOC_REL = "docs/HERMES_OPENCLAW_DASHBOARD_READ_ONLY_PREVIEW_UI_VALIDATION_HARDENING_PLAN_V0_8_2_D.md"
D_SCRIPT_REL = "scripts/check_hermes_openclaw_dashboard_read_only_preview_ui_validation_hardening_plan_v0_8_2_d.py"

C_SCRIPT_REL = "scripts/check_hermes_openclaw_dashboard_read_only_preview_ui_refinement_v0_8_2_c.py"

V082B_DOC_REL = "docs/HERMES_OPENCLAW_DASHBOARD_READ_ONLY_PREVIEW_UI_REFINEMENT_PLAN_V0_8_2_B.md"
V082B_SCRIPT_REL = "scripts/check_hermes_openclaw_dashboard_read_only_preview_ui_refinement_plan_v0_8_2_b.py"

V082A_SCRIPT_REL = "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_read_only_display_integration_v0_8_2_a.py"

P_LOADER_REL = "scripts/load_local_mock_fixture_preview_v0_8_1.py"
V_ADAPTER_REL = "scripts/local_mock_fixture_dashboard_preview_adapter_v0_8_1.py"
OLD_FIXTURE_JSON_REL = "fixtures/local_mock_data/hermes_openclaw_local_mock_messages_v0_8_1.json"
PROTECTED_WXYZ = {
    "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_runtime_check_v0_8_1_w.py",
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_DASHBOARD_PREVIEW_ADAPTER_INTEGRATION_BOUNDARY_PLAN_V0_8_1_X.md",
    "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_integration_boundary_plan_v0_8_1_x.py",
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_DASHBOARD_PREVIEW_ADAPTER_INTEGRATION_AUTHORIZATION_PLAN_V0_8_1_Y.md",
    "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_integration_authorization_plan_v0_8_1_y.py",
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_DASHBOARD_PREVIEW_ADAPTER_INTEGRATION_IMPLEMENTATION_PLAN_V0_8_1_Z.md",
    "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_integration_implementation_plan_v0_8_1_z.py",
}

EXPECTED_BASE_HEAD = "b9b9afd610d174aca3a9b54d978000399e46622c"

ALLOWED_NEW_UNTRACKED = {B_DOC_REL, B_FIXTURE_REL, B_BUILDER_REL, B_SCRIPT_REL}

EXACT_V083C_PHRASE = (
    "批准規劃 v0.8.3-C — Worker Dry-run Preview Dashboard Read-only Display Plan，"
    "僅允許規劃如何在 Dashboard 以 GET-only、read-only、synthetic local-only 方式顯示 "
    "v0.8.3-B 的 Worker dry-run preview model；不得修改 Dashboard route，不得新增 POST，"
    "不得新增 button/form/action URL，不得啟動 Worker，不得執行 Worker loop，不得呼叫 OpenClaw，"
    "不得啟動或連接 Hermes，不得讀寫 Google Sheets，不得讀 real queue DB，不得寫 queue，"
    "不得讀 secrets，不得建立 webhook/endpoint/connector，不得建立 production/shared DB 或 "
    "Remote Blackboard API runtime。"
)

REQUIRED_TEXT_MARKERS = [
    "synthetic local-only boundary implementation",
    "Worker status: OFF / NOT STARTED",
    "OpenClaw status: NOT CONNECTED / NOT CALLED",
    "Hermes status: NOT CONNECTED / NOT CALLED",
    "Google Sheets status: DISABLED / NOT READ / NOT WRITTEN",
]

PERMISSION_KEYS = (
    "execution_permission",
    "dispatch_permission",
    "external_side_effects_permission",
)

RUNTIME_STATE_KEYS = (
    "worker_started",
    "worker_loop_started",
    "openclaw_called",
    "hermes_called",
    "google_sheets_enabled",
    "real_queue_db_read",
    "queue_written",
    "post_enabled",
    "secrets_read",
    "webhook_created",
    "endpoint_created",
    "connector_created",
    "production_db_created",
    "remote_blackboard_api_runtime_created",
)

FORBIDDEN_CONTROL_URL_KEYS = (
    "action_url",
    "post_url",
    "webhook_url",
    "endpoint_url",
    "execute_url",
    "dispatch_url",
    "send_url",
)

REQUIRED_MODEL_KEYS = (
    "schema_version",
    "dry_run_id",
    "source",
    "task_title",
    "proposed_worker_action",
    "dry_run_status",
    "owner_review_required",
    "permissions",
    "runtime_state",
    "boundary_summary",
    "review_notice",
)

FORBIDDEN_IMPORT_PATTERN = re.compile(
    r"^\s*(import|from)\s+"
    r"(app(\.\w+)?|queue_store|QueueStore|worker(?!_dry_run_preview_boundary)\b"
    r"|openclaw|hermes|google|sheets|requests|httpx|socket|urllib|subprocess)\b",
    re.IGNORECASE,
)

# Built via concatenation (not literal contiguous substrings) - this file's own definitions must not
# self-trip the AM self-scan below, which reads this entire file's text as source.
FORBIDDEN_CALL_SUBSTRINGS = (
    "subprocess" + ".",
    "os." + "environ",
    "requests" + ".",
    "httpx" + ".",
    "socket" + ".",
    "urllib" + ".",
    "." + "post(",
)

# This readiness script itself legitimately imports subprocess and calls subprocess.run(["git", ...])
# read-only, the same way every prior readiness script in this repo does. That is not "the builder
# calling out to the world" - it is this script inspecting local git metadata. So the self-check below
# excludes subprocess from the forbidden set; everything else (network/app/runtime imports) still applies.
SELF_FORBIDDEN_IMPORT_PATTERN = re.compile(
    r"^\s*(import|from)\s+"
    r"(app(\.\w+)?|queue_store|QueueStore|worker(?!_dry_run_preview_boundary)\b"
    r"|openclaw|hermes|google|sheets|requests|httpx|socket|urllib)\b",
    re.IGNORECASE,
)

# Built via concatenation (not literal contiguous substrings) so that this file's own definition of
# the forbidden-call list does not trip its own self-scan below - only an *actual* dangerous call
# elsewhere in the file (written as contiguous text, not split like this) would match.
SELF_FORBIDDEN_CALL_SUBSTRINGS = (
    "os." + "environ",
    "requests" + ".",
    "httpx" + ".",
    "socket" + ".",
    "urllib" + ".",
    "." + "post(",
)

UNSAFE_DONE_CLAIMS = [
    "Worker started",
    "Worker loop started",
    "OpenClaw connected",
    "OpenClaw called",
    "Hermes connected",
    "Hermes called",
    "Google Sheets enabled",
    "real queue DB read",
    "queue write enabled",
    "POST enabled",
    "secrets read",
    "webhook created",
    "endpoint created",
    "connector created",
    "production DB created",
    "Remote Blackboard API runtime created",
    "v0.8.3-C started",
    "tag created",
]

PASS: list[str] = []
FAIL: list[str] = []


def ok(label: str) -> None:
    PASS.append(label)
    print(f"  ok : {label}")


def xx(label: str) -> None:
    FAIL.append(label)
    print(f"  XX : {label}")


def check(label: str, condition: bool) -> None:
    ok(label) if condition else xx(label)


def run_git(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args],
        capture_output=True,
        text=True,
    )


def git_lines(args: list[str]) -> list[str]:
    out = run_git(args)
    return [line for line in out.stdout.splitlines() if line.strip()]


def git_tracked(rel: str) -> bool:
    out = run_git(["ls-files", "--", rel])
    return out.returncode == 0 and out.stdout.strip() != ""


def working_tree_change_names() -> set[str]:
    return set(git_lines(["diff", "--name-only"]))


def untracked_names() -> set[str]:
    return set(git_lines(["ls-files", "--others", "--exclude-standard"]))


def find_forbidden_imports(source_text: str, pattern: re.Pattern[str] = FORBIDDEN_IMPORT_PATTERN) -> list[str]:
    found = []
    for line in source_text.splitlines():
        if pattern.match(line):
            found.append(line.strip())
    return found


def find_forbidden_calls(
    source_text: str, substrings: tuple[str, ...] = FORBIDDEN_CALL_SUBSTRINGS
) -> list[str]:
    return [needle for needle in substrings if needle in source_text]


# ---------------------------------------------------------------------------
# [A] current HEAD contains EXPECTED_BASE_HEAD in git history
# ---------------------------------------------------------------------------
print("[A] current HEAD contains EXPECTED_BASE_HEAD in git history")
ancestor_check = run_git(["merge-base", "--is-ancestor", EXPECTED_BASE_HEAD, "HEAD"])
check(
    f"A. HEAD contains {EXPECTED_BASE_HEAD} in git history",
    ancestor_check.returncode == 0,
)

# ---------------------------------------------------------------------------
# [B-E] v0.8.3-B files exist at expected paths
# ---------------------------------------------------------------------------
print("[B] B implementation doc exists at expected path")
check("B. B implementation doc exists at expected path", B_DOC_PATH.exists())

print("[C] B synthetic fixture exists at expected path")
check("C. B synthetic fixture exists at expected path", B_FIXTURE_PATH.exists())

print("[D] B standalone builder exists at expected path")
check("D. B standalone builder exists at expected path", B_BUILDER_PATH.exists())

print("[E] B readiness script exists at expected path")
check("E. B readiness script exists at expected path", B_SCRIPT_PATH.exists())

# ---------------------------------------------------------------------------
# [F] all four B files are currently untracked (Owner Review phase)
# ---------------------------------------------------------------------------
print("[F] all four B files are currently untracked in Owner Review phase")
check(
    "F. all four B files are currently untracked in Owner Review phase",
    not git_tracked(B_DOC_REL)
    and not git_tracked(B_FIXTURE_REL)
    and not git_tracked(B_BUILDER_REL)
    and not git_tracked(B_SCRIPT_REL),
)

# ---------------------------------------------------------------------------
# [G] git diff has no tracked file changes
# ---------------------------------------------------------------------------
print("[G] git diff has no tracked file changes")
tracked_changed = working_tree_change_names()
check(
    f"G. git diff has no tracked file changes（found {sorted(tracked_changed)}）"
    if tracked_changed
    else "G. git diff has no tracked file changes",
    not tracked_changed,
)

# ---------------------------------------------------------------------------
# [H] untracked files allowed only: the four B files, patches/*
# ---------------------------------------------------------------------------
print("[H] untracked files allowed only: the four B files, patches/*")
untracked = untracked_names()
unexpected_untracked = {
    u for u in untracked if u not in ALLOWED_NEW_UNTRACKED and not u.startswith("patches/")
}
check(
    f"H. no unexpected untracked files（found {sorted(unexpected_untracked)}）"
    if unexpected_untracked
    else "H. no unexpected untracked files",
    not unexpected_untracked,
)

# ---------------------------------------------------------------------------
# [I-V] no protected artifact modified
# ---------------------------------------------------------------------------
print("[I] app/main.py is not modified")
check("I. app/main.py is not modified", MAIN_PY_REL not in tracked_changed)

print("[J] templates/system.html is not modified")
check("J. templates/system.html is not modified", SYSTEM_HTML_REL not in tracked_changed)

print("[K] static/dashboard.css is not modified")
check("K. static/dashboard.css is not modified", DASHBOARD_CSS_REL not in tracked_changed)

print("[L] A plan doc/readiness are not modified")
check(
    "L. A plan doc/readiness are not modified",
    A_DOC_REL not in tracked_changed and A_SCRIPT_REL not in tracked_changed,
)

print("[M] F closeout doc/readiness are not modified")
check(
    "M. F closeout doc/readiness are not modified",
    F_DOC_REL not in tracked_changed and F_SCRIPT_REL not in tracked_changed,
)

print("[N] E validation script is not modified")
check("N. E validation script is not modified", E_SCRIPT_REL not in tracked_changed)

print("[O] D plan/readiness are not modified")
check(
    "O. D plan/readiness are not modified",
    D_DOC_REL not in tracked_changed and D_SCRIPT_REL not in tracked_changed,
)

print("[P] C validation script is not modified")
check("P. C validation script is not modified", C_SCRIPT_REL not in tracked_changed)

print("[Q] v0.8.2-B doc/readiness are not modified")
check(
    "Q. v0.8.2-B doc/readiness are not modified",
    V082B_DOC_REL not in tracked_changed and V082B_SCRIPT_REL not in tracked_changed,
)

print("[R] v0.8.2-A validation script is not modified")
check("R. v0.8.2-A validation script is not modified", V082A_SCRIPT_REL not in tracked_changed)

print("[S] P loader is not modified")
check("S. P loader is not modified", P_LOADER_REL not in tracked_changed)

print("[T] V adapter is not modified")
check("T. V adapter is not modified", V_ADAPTER_REL not in tracked_changed)

print("[U] old v0.8.1 fixture JSON is not modified")
check("U. old v0.8.1 fixture JSON is not modified", OLD_FIXTURE_JSON_REL not in tracked_changed)

print("[V] W/X/Y/Z artifacts are not modified")
check("V. W/X/Y/Z artifacts are not modified", not (tracked_changed & PROTECTED_WXYZ))

# ---------------------------------------------------------------------------
# [W-AB] B doc content checks
# ---------------------------------------------------------------------------
b_doc_text = B_DOC_PATH.read_text(encoding="utf-8") if B_DOC_PATH.exists() else ""

print('[W] B doc contains "synthetic local-only boundary implementation"')
check(
    'W. B doc contains "synthetic local-only boundary implementation"',
    REQUIRED_TEXT_MARKERS[0] in b_doc_text,
)

print('[X] B doc contains "Worker status: OFF / NOT STARTED"')
check('X. B doc contains "Worker status: OFF / NOT STARTED"', REQUIRED_TEXT_MARKERS[1] in b_doc_text)

print('[Y] B doc contains "OpenClaw status: NOT CONNECTED / NOT CALLED"')
check(
    'Y. B doc contains "OpenClaw status: NOT CONNECTED / NOT CALLED"',
    REQUIRED_TEXT_MARKERS[2] in b_doc_text,
)

print('[Z] B doc contains "Hermes status: NOT CONNECTED / NOT CALLED"')
check(
    'Z. B doc contains "Hermes status: NOT CONNECTED / NOT CALLED"',
    REQUIRED_TEXT_MARKERS[3] in b_doc_text,
)

print('[AA] B doc contains "Google Sheets status: DISABLED / NOT READ / NOT WRITTEN"')
check(
    'AA. B doc contains "Google Sheets status: DISABLED / NOT READ / NOT WRITTEN"',
    REQUIRED_TEXT_MARKERS[4] in b_doc_text,
)

print("[AB] B doc contains exact future v0.8.3-C authorization phrase exactly once")
check(
    "AB. B doc contains exact future v0.8.3-C authorization phrase exactly once",
    b_doc_text.count(EXACT_V083C_PHRASE) == 1,
)

# ---------------------------------------------------------------------------
# [AC-AH] B fixture content checks
# ---------------------------------------------------------------------------
fixture_data: dict[str, object] = {}
fixture_load_error: str | None = None
if B_FIXTURE_PATH.exists():
    try:
        fixture_data = json.loads(B_FIXTURE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fixture_load_error = str(exc)

print("[AC] B fixture source == synthetic_local_only")
check("AC. B fixture source == synthetic_local_only", fixture_data.get("source") == "synthetic_local_only")

print("[AD] B fixture dry_run_status == preview_only_not_executed")
check(
    "AD. B fixture dry_run_status == preview_only_not_executed",
    fixture_data.get("dry_run_status") == "preview_only_not_executed",
)

print("[AE] B fixture owner_review_required is true")
check("AE. B fixture owner_review_required is true", fixture_data.get("owner_review_required") is True)

print("[AF] B fixture permission flags are all false")
check(
    "AF. B fixture permission flags are all false",
    all(fixture_data.get(key) is False for key in PERMISSION_KEYS),
)

print("[AG] B fixture runtime state flags are all false")
check(
    "AG. B fixture runtime state flags are all false",
    all(fixture_data.get(key) is False for key in RUNTIME_STATE_KEYS),
)

print("[AH] B fixture contains no forbidden control URL keys")
check(
    "AH. B fixture contains no forbidden control URL keys",
    not any(key in fixture_data for key in FORBIDDEN_CONTROL_URL_KEYS),
)

# ---------------------------------------------------------------------------
# [AI] B builder contains no forbidden imports / calls
# ---------------------------------------------------------------------------
builder_text = B_BUILDER_PATH.read_text(encoding="utf-8") if B_BUILDER_PATH.exists() else ""
builder_forbidden_imports = find_forbidden_imports(builder_text)
builder_forbidden_calls = find_forbidden_calls(builder_text)

print("[AI] B builder contains no forbidden imports / calls")
check(
    f"AI. B builder contains no forbidden imports / calls"
    f"（imports {builder_forbidden_imports}, calls {builder_forbidden_calls}）"
    if (builder_forbidden_imports or builder_forbidden_calls)
    else "AI. B builder contains no forbidden imports / calls",
    not builder_forbidden_imports and not builder_forbidden_calls,
)

# ---------------------------------------------------------------------------
# [AJ-AL] B builder functional check: import and call the builder
# ---------------------------------------------------------------------------
built_model: dict[str, object] = {}
builder_import_error: str | None = None
if B_BUILDER_PATH.exists():
    try:
        spec = importlib.util.spec_from_file_location(
            "worker_dry_run_preview_boundary_v0_8_3_b", B_BUILDER_PATH
        )
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        built_model = module.build_worker_dry_run_preview_model()
    except Exception as exc:  # noqa: BLE001 - readiness check wants to report, not raise
        builder_import_error = f"{type(exc).__name__}: {exc}"

print("[AJ] B builder returns a model with required keys")
check(
    f"AJ. B builder returns a model with required keys（error: {builder_import_error}）"
    if builder_import_error
    else "AJ. B builder returns a model with required keys",
    builder_import_error is None and all(key in built_model for key in REQUIRED_MODEL_KEYS),
)

print("[AK] B builder returned permissions are all false")
built_permissions = built_model.get("permissions", {}) if isinstance(built_model, dict) else {}
check(
    "AK. B builder returned permissions are all false",
    isinstance(built_permissions, dict)
    and all(built_permissions.get(key) is False for key in PERMISSION_KEYS),
)

print("[AL] B builder returned runtime_state flags are all false")
built_runtime_state = built_model.get("runtime_state", {}) if isinstance(built_model, dict) else {}
check(
    "AL. B builder returned runtime_state flags are all false",
    isinstance(built_runtime_state, dict)
    and all(built_runtime_state.get(key) is False for key in RUNTIME_STATE_KEYS),
)

# ---------------------------------------------------------------------------
# [AM] B validation script itself contains no forbidden imports
# ---------------------------------------------------------------------------
self_text = B_SCRIPT_PATH.read_text(encoding="utf-8") if B_SCRIPT_PATH.exists() else ""
self_forbidden_imports = find_forbidden_imports(self_text, SELF_FORBIDDEN_IMPORT_PATTERN)
self_forbidden_calls = find_forbidden_calls(self_text, SELF_FORBIDDEN_CALL_SUBSTRINGS)

print("[AM] B validation script itself contains no forbidden imports")
check(
    f"AM. B validation script itself contains no forbidden imports"
    f"（imports {self_forbidden_imports}, calls {self_forbidden_calls}）"
    if (self_forbidden_imports or self_forbidden_calls)
    else "AM. B validation script itself contains no forbidden imports",
    not self_forbidden_imports and not self_forbidden_calls,
)

# ---------------------------------------------------------------------------
# [AN] B doc / fixture / builder do not contain unsafe done-claims
# ---------------------------------------------------------------------------
combined_text = b_doc_text + "\n" + json.dumps(fixture_data, ensure_ascii=False) + "\n" + builder_text
found_unsafe = [c for c in UNSAFE_DONE_CLAIMS if c in combined_text]

print("[AN] B doc / fixture / builder do not contain unsafe done-claims")
check(
    f"AN. B doc / fixture / builder do not contain unsafe done-claims（found {found_unsafe}）"
    if found_unsafe
    else "AN. B doc / fixture / builder do not contain unsafe done-claims",
    not found_unsafe,
)

# ---------------------------------------------------------------------------
# [AO] patches/ remains untracked and untouched
# ---------------------------------------------------------------------------
print("[AO] patches/ remains untracked and untouched")
check(
    "AO. patches/ remains untracked and untouched",
    not any(p.startswith("patches/") for p in tracked_changed),
)

# ---------------------------------------------------------------------------
# 結果
# ---------------------------------------------------------------------------
total = len(PASS) + len(FAIL)
print(f"\n合計：{len(PASS)}/{total} 通過")
if FAIL:
    print(f"\nXX v0.8.3-B readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print("PASS: v0.8.3-B worker dry-run preview boundary implementation")
    sys.exit(0)
