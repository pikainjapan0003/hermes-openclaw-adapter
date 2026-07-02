"""v0.8.3-C readiness check: Worker Dry-run Preview Dashboard Read-only Display Plan (plan-only).

Pure local filesystem + git metadata validation, plus a local import of the v0.8.3-B standalone
builder module (read-only reference check) to confirm its returned model stays safe. This script
reads only the v0.8.3-C doc/readiness-script and the v0.8.3-B doc/fixture/builder/readiness-script,
and confirms the tracked/untracked state of the v0.8.3-C files and the surfaces they must not touch
(app/main.py, templates/system.html, static/dashboard.css, the v0.8.3-B doc/fixture/builder/readiness
script, the v0.8.3-A plan doc/readiness script, the v0.8.2-F closeout doc/readiness script, the
v0.8.2-E validation script, the v0.8.2-D plan doc/readiness script, the v0.8.2-C validation script,
the v0.8.2-B plan doc/readiness script, the v0.8.2-A validation script, the P loader, the V adapter,
the old v0.8.1 fixture JSON, and the W/X/Y/Z artifacts). It uses `git` read-only (ls-files / diff /
status / merge-base) to confirm tracked status, ancestry, and that no tracked file was modified; it
never modifies the git index.

It does NOT import app runtime, Dashboard runtime, QueueStore, Worker/OpenClaw/Hermes/Google Sheets
integration, the v0.8.1-P loader, or the v0.8.1-V adapter; it never starts a server; it reads no real
queue DB, sends no POST, makes no network call, reads no secrets, writes no repo file, and modifies no
git index. It only imports the v0.8.3-B builder module (standard library only) to call its public
function and inspect the returned dict, as a read-only reference re-check.
"""
from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

C_DOC_REL = "docs/HERMES_OPENCLAW_WORKER_DRY_RUN_PREVIEW_DASHBOARD_READ_ONLY_DISPLAY_PLAN_V0_8_3_C.md"
C_DOC_PATH = REPO_ROOT / C_DOC_REL
C_SCRIPT_REL = "scripts/check_hermes_openclaw_worker_dry_run_preview_dashboard_read_only_display_plan_v0_8_3_c.py"
C_SCRIPT_PATH = REPO_ROOT / C_SCRIPT_REL

B_DOC_REL = "docs/HERMES_OPENCLAW_WORKER_DRY_RUN_PREVIEW_BOUNDARY_IMPLEMENTATION_V0_8_3_B.md"
B_FIXTURE_REL = "fixtures/local_mock_data/hermes_openclaw_worker_dry_run_preview_v0_8_3_b.json"
B_BUILDER_REL = "scripts/worker_dry_run_preview_boundary_v0_8_3_b.py"
B_BUILDER_PATH = REPO_ROOT / B_BUILDER_REL
B_SCRIPT_REL = "scripts/check_hermes_openclaw_worker_dry_run_preview_boundary_implementation_v0_8_3_b.py"

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

C_V082_SCRIPT_REL = "scripts/check_hermes_openclaw_dashboard_read_only_preview_ui_refinement_v0_8_2_c.py"

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

EXPECTED_BASE_HEAD = "8d99aea9a214b40359a2fd47cab413d47a0ae017"

ALLOWED_NEW_UNTRACKED = {C_DOC_REL, C_SCRIPT_REL}

EXACT_V083D_PHRASE = (
    "批准實作 v0.8.3-D — Worker Dry-run Preview Dashboard Read-only Display Implementation，"
    "僅允許在既有 Dashboard GET-only `/dashboard/system` 中以 read-only、synthetic local-only "
    "方式顯示 v0.8.3-B 的 Worker dry-run preview model；僅允許修改 app/main.py、"
    "templates/system.html、static/dashboard.css 與新增 v0.8.3-D validation script；"
    "不得新增 POST，不得新增 button/form/action URL，不得啟動 Worker，不得執行 Worker loop，"
    "不得呼叫 OpenClaw，不得啟動或連接 Hermes，不得讀寫 Google Sheets，不得讀 real queue DB，"
    "不得寫 queue，不得讀 secrets，不得建立 webhook/endpoint/connector，不得建立 "
    "production/shared DB 或 Remote Blackboard API runtime。"
)

REQUIRED_TEXT_MARKERS = [
    "plan-only / Dashboard read-only display plan",
    "Dashboard route status: NOT MODIFIED",
    "Dashboard template status: NOT MODIFIED",
    "Dashboard CSS status: NOT MODIFIED",
    "Worker status: OFF / NOT STARTED",
    "OpenClaw status: NOT CONNECTED / NOT CALLED",
    "Hermes status: NOT CONNECTED / NOT CALLED",
    "Google Sheets status: DISABLED / NOT READ / NOT WRITTEN",
]

REQUIRED_DISPLAY_FIELDS = (
    "dry_run_id",
    "source",
    "task_title",
    "task_summary",
    "source_role",
    "target_role",
    "proposed_worker_action",
    "dry_run_status",
    "owner_review_required",
    "review_notice",
    "boundary_summary",
)

REQUIRED_PERMISSION_TEXT = (
    "execution_permission = false",
    "dispatch_permission = false",
    "external_side_effects_permission = false",
)

REQUIRED_RUNTIME_TEXT = (
    "worker_started = false",
    "worker_loop_started = false",
    "openclaw_called = false",
    "hermes_called = false",
    "google_sheets_enabled = false",
    "real_queue_db_read = false",
    "queue_written = false",
    "post_enabled = false",
    "secrets_read = false",
    "webhook_created = false",
    "endpoint_created = false",
    "connector_created = false",
    "production_db_created = false",
    "remote_blackboard_api_runtime_created = false",
)

REQUIRED_FORBIDDEN_PHRASES = (
    "no Worker runtime",
    "no Worker loop",
    "no OpenClaw call",
    "no Hermes activation",
    "no Google Sheets read/write",
    "no reading or writing of the real queue DB",
    "no queue write",
    "no POST",
    "no execute/dispatch/send controls",
    "no secrets",
    "no webhook/endpoint/connector",
    "no production/shared DB",
    "no Remote Blackboard API runtime",
)

UNSAFE_DONE_CLAIMS = [
    "Dashboard integrated",
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
    "v0.8.3-D started",
    "tag created",
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

FORBIDDEN_IMPORT_PATTERN = re.compile(
    r"^\s*(import|from)\s+"
    r"(app(\.\w+)?|queue_store|QueueStore|worker(?!_dry_run_preview_boundary)\b"
    r"|openclaw|hermes|google|sheets|requests|httpx|socket|urllib)\b",
    re.IGNORECASE,
)

# Built via concatenation (not literal contiguous substrings) so this file's own definition of the
# forbidden-call list does not trip its own self-scan below - only an *actual* dangerous call
# elsewhere in the file (written as contiguous text, not split like this) would match.
FORBIDDEN_CALL_SUBSTRINGS = (
    "os." + "environ",
    "requests" + ".",
    "httpx" + ".",
    "socket" + ".",
    "urllib" + ".",
    "." + "post(",
)

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


def find_forbidden_imports(source_text: str) -> list[str]:
    found = []
    for line in source_text.splitlines():
        if FORBIDDEN_IMPORT_PATTERN.match(line):
            found.append(line.strip())
    return found


def find_forbidden_calls(source_text: str) -> list[str]:
    return [needle for needle in FORBIDDEN_CALL_SUBSTRINGS if needle in source_text]


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
# [B-C] v0.8.3-C files exist at expected paths
# ---------------------------------------------------------------------------
print("[B] C display plan doc exists at expected path")
check("B. C display plan doc exists at expected path", C_DOC_PATH.exists())

print("[C] C readiness script exists at expected path")
check("C. C readiness script exists at expected path", C_SCRIPT_PATH.exists())

# ---------------------------------------------------------------------------
# [D-E] v0.8.3-C files are currently untracked (Owner Review phase)
# ---------------------------------------------------------------------------
print("[D] C display plan doc is currently untracked in Owner Review phase")
check(
    "D. C display plan doc is currently untracked in Owner Review phase",
    not git_tracked(C_DOC_REL),
)

print("[E] C readiness script is currently untracked in Owner Review phase")
check(
    "E. C readiness script is currently untracked in Owner Review phase",
    not git_tracked(C_SCRIPT_REL),
)

# ---------------------------------------------------------------------------
# [F] git diff has no tracked file changes
# ---------------------------------------------------------------------------
print("[F] git diff has no tracked file changes")
tracked_changed = working_tree_change_names()
check(
    f"F. git diff has no tracked file changes（found {sorted(tracked_changed)}）"
    if tracked_changed
    else "F. git diff has no tracked file changes",
    not tracked_changed,
)

# ---------------------------------------------------------------------------
# [G] untracked files allowed only: C doc, C script, patches/*
# ---------------------------------------------------------------------------
print("[G] untracked files allowed only: C doc, C script, patches/*")
untracked = untracked_names()
unexpected_untracked = {
    u for u in untracked if u not in ALLOWED_NEW_UNTRACKED and not u.startswith("patches/")
}
check(
    f"G. no unexpected untracked files（found {sorted(unexpected_untracked)}）"
    if unexpected_untracked
    else "G. no unexpected untracked files",
    not unexpected_untracked,
)

# ---------------------------------------------------------------------------
# [H-V] no protected artifact modified
# ---------------------------------------------------------------------------
print("[H] app/main.py is not modified")
check("H. app/main.py is not modified", MAIN_PY_REL not in tracked_changed)

print("[I] templates/system.html is not modified")
check("I. templates/system.html is not modified", SYSTEM_HTML_REL not in tracked_changed)

print("[J] static/dashboard.css is not modified")
check("J. static/dashboard.css is not modified", DASHBOARD_CSS_REL not in tracked_changed)

print("[K] B implementation doc / fixture / builder / readiness script are not modified")
check(
    "K. B implementation doc / fixture / builder / readiness script are not modified",
    B_DOC_REL not in tracked_changed
    and B_FIXTURE_REL not in tracked_changed
    and B_BUILDER_REL not in tracked_changed
    and B_SCRIPT_REL not in tracked_changed,
)

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

print("[P] C v0.8.2 validation script is not modified")
check("P. C v0.8.2 validation script is not modified", C_V082_SCRIPT_REL not in tracked_changed)

print("[Q] B v0.8.2 doc/readiness are not modified")
check(
    "Q. B v0.8.2 doc/readiness are not modified",
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
# [W-AD] C doc status/type content checks
# ---------------------------------------------------------------------------
c_doc_text = C_DOC_PATH.read_text(encoding="utf-8") if C_DOC_PATH.exists() else ""

print('[W] C doc contains "plan-only / Dashboard read-only display plan"')
check(
    'W. C doc contains "plan-only / Dashboard read-only display plan"',
    REQUIRED_TEXT_MARKERS[0] in c_doc_text,
)

print('[X] C doc contains "Dashboard route status: NOT MODIFIED"')
check('X. C doc contains "Dashboard route status: NOT MODIFIED"', REQUIRED_TEXT_MARKERS[1] in c_doc_text)

print('[Y] C doc contains "Dashboard template status: NOT MODIFIED"')
check(
    'Y. C doc contains "Dashboard template status: NOT MODIFIED"', REQUIRED_TEXT_MARKERS[2] in c_doc_text
)

print('[Z] C doc contains "Dashboard CSS status: NOT MODIFIED"')
check('Z. C doc contains "Dashboard CSS status: NOT MODIFIED"', REQUIRED_TEXT_MARKERS[3] in c_doc_text)

print('[AA] C doc contains "Worker status: OFF / NOT STARTED"')
check('AA. C doc contains "Worker status: OFF / NOT STARTED"', REQUIRED_TEXT_MARKERS[4] in c_doc_text)

print('[AB] C doc contains "OpenClaw status: NOT CONNECTED / NOT CALLED"')
check(
    'AB. C doc contains "OpenClaw status: NOT CONNECTED / NOT CALLED"',
    REQUIRED_TEXT_MARKERS[5] in c_doc_text,
)

print('[AC] C doc contains "Hermes status: NOT CONNECTED / NOT CALLED"')
check(
    'AC. C doc contains "Hermes status: NOT CONNECTED / NOT CALLED"',
    REQUIRED_TEXT_MARKERS[6] in c_doc_text,
)

print('[AD] C doc contains "Google Sheets status: DISABLED / NOT READ / NOT WRITTEN"')
check(
    'AD. C doc contains "Google Sheets status: DISABLED / NOT READ / NOT WRITTEN"',
    REQUIRED_TEXT_MARKERS[7] in c_doc_text,
)

# ---------------------------------------------------------------------------
# [AE] C doc contains exact future v0.8.3-D authorization phrase exactly once
# ---------------------------------------------------------------------------
print("[AE] C doc contains exact future v0.8.3-D authorization phrase exactly once")
check(
    "AE. C doc contains exact future v0.8.3-D authorization phrase exactly once",
    c_doc_text.count(EXACT_V083D_PHRASE) == 1,
)

# ---------------------------------------------------------------------------
# [AF] C doc contains proposed display section name "worker-dry-run-preview"
# ---------------------------------------------------------------------------
print('[AF] C doc contains proposed display section name "worker-dry-run-preview"')
check(
    'AF. C doc contains proposed display section name "worker-dry-run-preview"',
    "worker-dry-run-preview" in c_doc_text,
)

# ---------------------------------------------------------------------------
# [AG] C doc contains all required future display fields
# ---------------------------------------------------------------------------
missing_display_fields = [f for f in REQUIRED_DISPLAY_FIELDS if f not in c_doc_text]
print("[AG] C doc contains all required future display fields")
check(
    f"AG. C doc contains all required future display fields（missing {missing_display_fields}）"
    if missing_display_fields
    else "AG. C doc contains all required future display fields",
    not missing_display_fields,
)

# ---------------------------------------------------------------------------
# [AH] C doc contains all required permission flags
# ---------------------------------------------------------------------------
missing_permission_text = [p for p in REQUIRED_PERMISSION_TEXT if p not in c_doc_text]
print("[AH] C doc contains all required permission flags")
check(
    f"AH. C doc contains all required permission flags（missing {missing_permission_text}）"
    if missing_permission_text
    else "AH. C doc contains all required permission flags",
    not missing_permission_text,
)

# ---------------------------------------------------------------------------
# [AI] C doc contains all required runtime flags
# ---------------------------------------------------------------------------
missing_runtime_text = [r for r in REQUIRED_RUNTIME_TEXT if r not in c_doc_text]
print("[AI] C doc contains all required runtime flags")
check(
    f"AI. C doc contains all required runtime flags（missing {missing_runtime_text}）"
    if missing_runtime_text
    else "AI. C doc contains all required runtime flags",
    not missing_runtime_text,
)

# ---------------------------------------------------------------------------
# [AJ] C doc contains all forbidden boundary phrases
# ---------------------------------------------------------------------------
missing_forbidden_phrases = [p for p in REQUIRED_FORBIDDEN_PHRASES if p not in c_doc_text]
print("[AJ] C doc contains all forbidden boundary phrases")
check(
    f"AJ. C doc contains all forbidden boundary phrases（missing {missing_forbidden_phrases}）"
    if missing_forbidden_phrases
    else "AJ. C doc contains all forbidden boundary phrases",
    not missing_forbidden_phrases,
)

# ---------------------------------------------------------------------------
# [AK] C doc does not contain unsafe done-claims
# ---------------------------------------------------------------------------
found_unsafe = [c for c in UNSAFE_DONE_CLAIMS if c in c_doc_text]
print("[AK] C doc does not contain unsafe done-claims")
check(
    f"AK. C doc does not contain unsafe done-claims（found {found_unsafe}）"
    if found_unsafe
    else "AK. C doc does not contain unsafe done-claims",
    not found_unsafe,
)

# ---------------------------------------------------------------------------
# [AL-AO] B builder local preview re-check (read-only reference)
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
else:
    builder_import_error = "B builder not found"

print("[AL] B builder local preview still returns source == synthetic_local_only")
check(
    f"AL. B builder local preview still returns source == synthetic_local_only（error: {builder_import_error}）"
    if builder_import_error
    else "AL. B builder local preview still returns source == synthetic_local_only",
    builder_import_error is None and built_model.get("source") == "synthetic_local_only",
)

print("[AM] B builder local preview still returns dry_run_status == preview_only_not_executed")
check(
    "AM. B builder local preview still returns dry_run_status == preview_only_not_executed",
    builder_import_error is None
    and built_model.get("dry_run_status") == "preview_only_not_executed",
)

print("[AN] B builder local preview permissions are all false")
built_permissions = built_model.get("permissions", {}) if isinstance(built_model, dict) else {}
check(
    "AN. B builder local preview permissions are all false",
    isinstance(built_permissions, dict)
    and all(built_permissions.get(key) is False for key in PERMISSION_KEYS),
)

print("[AO] B builder local preview runtime_state flags are all false")
built_runtime_state = built_model.get("runtime_state", {}) if isinstance(built_model, dict) else {}
check(
    "AO. B builder local preview runtime_state flags are all false",
    isinstance(built_runtime_state, dict)
    and all(built_runtime_state.get(key) is False for key in RUNTIME_STATE_KEYS),
)

# ---------------------------------------------------------------------------
# [AP] C readiness script itself contains no forbidden imports / runtime calls
# ---------------------------------------------------------------------------
self_text = C_SCRIPT_PATH.read_text(encoding="utf-8") if C_SCRIPT_PATH.exists() else ""
self_forbidden_imports = find_forbidden_imports(self_text)
self_forbidden_calls = find_forbidden_calls(self_text)

print("[AP] C readiness script itself contains no forbidden imports / runtime calls")
check(
    f"AP. C readiness script itself contains no forbidden imports / runtime calls"
    f"（imports {self_forbidden_imports}, calls {self_forbidden_calls}）"
    if (self_forbidden_imports or self_forbidden_calls)
    else "AP. C readiness script itself contains no forbidden imports / runtime calls",
    not self_forbidden_imports and not self_forbidden_calls,
)

# ---------------------------------------------------------------------------
# [AQ] patches/ remains untracked and untouched
# ---------------------------------------------------------------------------
print("[AQ] patches/ remains untracked and untouched")
check(
    "AQ. patches/ remains untracked and untouched",
    not any(p.startswith("patches/") for p in tracked_changed),
)

# ---------------------------------------------------------------------------
# 結果
# ---------------------------------------------------------------------------
total = len(PASS) + len(FAIL)
print(f"\n合計：{len(PASS)}/{total} 通過")
if FAIL:
    print(f"\nXX v0.8.3-C readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print("PASS: v0.8.3-C worker dry-run preview dashboard read-only display plan")
    sys.exit(0)
