"""v0.8.1-W runtime check: Dashboard Preview Adapter Validation Runtime Check.

v0.8.1-W is Dashboard preview adapter runtime validation/check only.
v0.8.1-W only validates the v0.8.1-V read-only Dashboard preview adapter at runtime.
v0.8.1-W does not modify Dashboard.
v0.8.1-W does not create Dashboard route.
v0.8.1-W does not create Dashboard endpoint.
v0.8.1-W does not create Dashboard template.
v0.8.1-W does not create Dashboard static asset.
v0.8.1-W does not modify adapter.
v0.8.1-W does not modify loader.
v0.8.1-W does not read fixture JSON directly.
v0.8.1-W does not read real queue DB.
v0.8.1-W does not write queue data.
v0.8.1-W does not send POST.
v0.8.1-W does not make network calls.
v0.8.1-W does not start Worker.
v0.8.1-W does not call OpenClaw.
v0.8.1-W does not activate Hermes.
v0.8.1-W does not read Google Sheets.
v0.8.1-W does not write Google Sheets.
v0.8.1-W does not read secrets.
v0.8.1-W does not create .env.
v0.8.1-W does not create webhook.
v0.8.1-W does not create connector.
v0.8.1-W does not create production DB.
v0.8.1-W does not create shared DB.
v0.8.1-W does not create Remote Blackboard API runtime.
v0.8.1-W does not commit.
v0.8.1-W does not push.
v0.8.1-W does not tag.

Pure local filesystem validation. This script statically inspects the v0.8.1-V adapter source (AST
imports, tokenize NAME identifiers, raw fixture-path-literal substring check), confirms the tracked
state of the L/M/N/O/P/Q/R/S/T/U/V artifacts, dynamically imports the V adapter (which in turn
imports the already-authorized v0.8.1-P loader) to re-run and re-verify the adapter's import
self-test, output contract, row contract, permission flags, runtime badges, and object-identity
safety, and uses `git` read-only (ls-files / diff / status) to confirm tracked status and that no
extra repo files exist. It never modifies the git index or any repo file.

It does NOT import Dashboard, app runtime, QueueStore, or any Worker/OpenClaw/Hermes/Google Sheets
integration; it reads no real queue DB, sends no POST, makes no network call, reads no secrets,
writes no repo file, modifies no adapter, modifies no loader, and modifies no Dashboard. It does not
read the fixture JSON directly itself; the only fixture read happens inside the already-authorized
v0.8.1-P loader that the v0.8.1-V adapter calls.
"""
from __future__ import annotations

import ast
import importlib.util
import io
import subprocess
import sys
import tokenize
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

W_SCRIPT_PATH = REPO_ROOT / "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_runtime_check_v0_8_1_w.py"

V_ADAPTER_PATH = REPO_ROOT / "scripts/local_mock_fixture_dashboard_preview_adapter_v0_8_1.py"
V_READINESS_PATH = REPO_ROOT / "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_v0_8_1_v.py"

FIXTURE_PATH = REPO_ROOT / "fixtures/local_mock_data/hermes_openclaw_local_mock_messages_v0_8_1.json"
P_LOADER_PATH = REPO_ROOT / "scripts/load_local_mock_fixture_preview_v0_8_1.py"

M_DOC_PATH = REPO_ROOT / "docs/HERMES_OPENCLAW_LOCAL_MOCK_DATA_FIXTURE_JSON_ARTIFACT_VALIDATION_V0_8_1_M.md"
M_SCRIPT_PATH = REPO_ROOT / "scripts/check_hermes_openclaw_local_mock_data_fixture_json_artifact_validation_v0_8_1_m.py"

N_DOC_PATH = REPO_ROOT / "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_PLAN_V0_8_1_N.md"
N_SCRIPT_PATH = REPO_ROOT / "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_plan_v0_8_1_n.py"

O_DOC_PATH = REPO_ROOT / "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_IMPLEMENTATION_AUTHORIZATION_PLAN_V0_8_1_O.md"
O_SCRIPT_PATH = REPO_ROOT / "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_implementation_authorization_plan_v0_8_1_o.py"

Q_DOC_PATH = REPO_ROOT / "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_VALIDATION_PLAN_V0_8_1_Q.md"
Q_SCRIPT_PATH = REPO_ROOT / "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_validation_plan_v0_8_1_q.py"

R_SCRIPT_PATH = REPO_ROOT / "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_runtime_check_v0_8_1_r.py"

S_DOC_PATH = REPO_ROOT / "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_DASHBOARD_INTEGRATION_BOUNDARY_PLAN_V0_8_1_S.md"
S_SCRIPT_PATH = REPO_ROOT / "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_dashboard_integration_boundary_plan_v0_8_1_s.py"

T_DOC_PATH = REPO_ROOT / "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_DASHBOARD_INTEGRATION_AUTHORIZATION_PLAN_V0_8_1_T.md"
T_SCRIPT_PATH = REPO_ROOT / "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_dashboard_integration_authorization_plan_v0_8_1_t.py"

U_DOC_PATH = REPO_ROOT / "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_DASHBOARD_PREVIEW_INTEGRATION_IMPLEMENTATION_PLAN_V0_8_1_U.md"
U_SCRIPT_PATH = REPO_ROOT / "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_dashboard_preview_integration_implementation_plan_v0_8_1_u.py"

EXPECTED_BASE_HEAD = "c1c6b171084b9a75ceb53d1dfb7ed5017806ce37"
EXPECTED_SCHEMA_VERSION = "v0.8.1-dashboard-preview-adapter-1"
EXPECTED_ADAPTER_VERSION = "v0.8.1-V"
EXPECTED_ROW_COUNT = 6

EXPECTED_RUNTIME_BADGES = [
    "DISPATCH OFF",
    "WORKER OFF",
    "OPENCLAW NOT CONNECTED",
    "HERMES NOT CONNECTED",
    "GOOGLE SHEETS DISABLED",
]

ALLOWED_IMPORT_ROOTS = {
    "__future__",
    "copy",
    "typing",
    "load_local_mock_fixture_preview_v0_8_1",
}

FORBIDDEN_IDENTIFIERS = {
    "argparse",
    "click",
    "typer",
    "flask",
    "fastapi",
    "requests",
    "httpx",
    "urllib",
    "socket",
    "sqlite3",
    "sqlalchemy",
    "QueueStore",
    "app",
    "dashboard_route",
    "dashboard_endpoint",
    "render_template",
    "Blueprint",
    "route",
    "endpoint",
    "template",
    "static",
    "openclaw",
    "hermes",
    "google",
    "dotenv",
    "write_text",
    "open",
    "remove",
    "unlink",
    "post",
    "urlopen",
    "system",
    "popen",
}

FORBIDDEN_ROW_FIELDS = {
    "action_url",
    "post_url",
    "webhook_url",
    "endpoint_url",
    "execute_url",
    "dispatch_url",
    "execution_button",
    "dispatch_button",
    "execution_controls",
    "dispatch_controls",
    "external_action",
    "external_actions",
}

FIXTURE_PATH_LITERALS = [
    "fixtures/local_mock_data/hermes_openclaw_local_mock_messages_v0_8_1.json",
    "hermes_openclaw_local_mock_messages_v0_8_1.json",
]

DIRECT_READ_MARKERS = ["read_text", "json.load", "json.loads", "Path.read_text", "open("]

FORBIDDEN_WRITE_MARKERS = [
    "write_text(",
    ".write(",
    "os.remove(",
    "os.unlink(",
    "shutil.rmtree(",
    '"w"',
    "'w'",
    '"wb"',
    "'wb'",
    '"a"',
    "'a'",
]

DASHBOARD_PROTECTED_PREFIXES = [
    "app/",
    "templates/",
    "static/",
]

PASS: list[str] = []
FAIL: list[str] = []


def ok(label: str) -> None:
    PASS.append(label)
    print(f"  ok : {label}")


def xx(label: str) -> None:
    FAIL.append(label)
    print(f"  XX : {label}")


def git_tracked(rel: str) -> bool:
    out = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "ls-files", "--", rel],
        capture_output=True,
        text=True,
    )
    return out.returncode == 0 and out.stdout.strip() != ""


# ---------------------------------------------------------------------------
# [A] W runtime check script path is correct
# ---------------------------------------------------------------------------
print("[A] W runtime check script path is correct")
ok("A. W runtime check script exists at expected path") if W_SCRIPT_PATH.exists() else xx(
    "A. W runtime check script exists at expected path"
)

# ---------------------------------------------------------------------------
# [B/C] V adapter + V readiness script exist and are tracked
# ---------------------------------------------------------------------------
print("[B] V adapter exists and is tracked")
ok("B. V adapter exists") if V_ADAPTER_PATH.exists() else xx("B. V adapter exists")
ok("B. V adapter is tracked") if git_tracked(
    "scripts/local_mock_fixture_dashboard_preview_adapter_v0_8_1.py"
) else xx("B. V adapter is tracked")
if not V_ADAPTER_PATH.exists():
    print("\nXX V adapter 不存在，無法繼續")
    sys.exit(1)

print("[C] V readiness script exists and is tracked")
ok("C. V readiness script exists") if V_READINESS_PATH.exists() else xx("C. V readiness script exists")
ok("C. V readiness script is tracked") if git_tracked(
    "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_v0_8_1_v.py"
) else xx("C. V readiness script is tracked")

adapter_source = V_ADAPTER_PATH.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# [D-M] L/M/N/O/P/Q/R/S/T/U artifacts exist and are tracked
# ---------------------------------------------------------------------------
print("[D] L fixture JSON exists and is tracked")
ok("D. L fixture JSON exists") if FIXTURE_PATH.exists() else xx("D. L fixture JSON exists")
ok("D. L fixture JSON is tracked") if git_tracked(
    "fixtures/local_mock_data/hermes_openclaw_local_mock_messages_v0_8_1.json"
) else xx("D. L fixture JSON is tracked")

print("[E] M validation doc/script exist and are tracked")
ok("E. M validation doc exists") if M_DOC_PATH.exists() else xx("E. M validation doc exists")
ok("E. M validation doc is tracked") if git_tracked(
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_DATA_FIXTURE_JSON_ARTIFACT_VALIDATION_V0_8_1_M.md"
) else xx("E. M validation doc is tracked")
ok("E. M validation script exists") if M_SCRIPT_PATH.exists() else xx("E. M validation script exists")
ok("E. M validation script is tracked") if git_tracked(
    "scripts/check_hermes_openclaw_local_mock_data_fixture_json_artifact_validation_v0_8_1_m.py"
) else xx("E. M validation script is tracked")

print("[F] N plan doc/script exist and are tracked")
ok("F. N plan doc exists") if N_DOC_PATH.exists() else xx("F. N plan doc exists")
ok("F. N plan doc is tracked") if git_tracked(
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_PLAN_V0_8_1_N.md"
) else xx("F. N plan doc is tracked")
ok("F. N readiness script exists") if N_SCRIPT_PATH.exists() else xx("F. N readiness script exists")
ok("F. N readiness script is tracked") if git_tracked(
    "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_plan_v0_8_1_n.py"
) else xx("F. N readiness script is tracked")

print("[G] O authorization doc/script exist and are tracked")
ok("G. O authorization doc exists") if O_DOC_PATH.exists() else xx("G. O authorization doc exists")
ok("G. O authorization doc is tracked") if git_tracked(
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_IMPLEMENTATION_AUTHORIZATION_PLAN_V0_8_1_O.md"
) else xx("G. O authorization doc is tracked")
ok("G. O readiness script exists") if O_SCRIPT_PATH.exists() else xx("G. O readiness script exists")
ok("G. O readiness script is tracked") if git_tracked(
    "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_implementation_authorization_plan_v0_8_1_o.py"
) else xx("G. O readiness script is tracked")

print("[H] P loader exists and is tracked")
ok("H. P loader exists") if P_LOADER_PATH.exists() else xx("H. P loader exists")
ok("H. P loader is tracked") if git_tracked(
    "scripts/load_local_mock_fixture_preview_v0_8_1.py"
) else xx("H. P loader is tracked")

print("[I] Q validation doc/script exist and are tracked")
ok("I. Q validation doc exists") if Q_DOC_PATH.exists() else xx("I. Q validation doc exists")
ok("I. Q validation doc is tracked") if git_tracked(
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_VALIDATION_PLAN_V0_8_1_Q.md"
) else xx("I. Q validation doc is tracked")
ok("I. Q readiness script exists") if Q_SCRIPT_PATH.exists() else xx("I. Q readiness script exists")
ok("I. Q readiness script is tracked") if git_tracked(
    "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_validation_plan_v0_8_1_q.py"
) else xx("I. Q readiness script is tracked")

print("[J] R runtime check script exists and is tracked")
ok("J. R runtime check script exists") if R_SCRIPT_PATH.exists() else xx("J. R runtime check script exists")
ok("J. R runtime check script is tracked") if git_tracked(
    "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_runtime_check_v0_8_1_r.py"
) else xx("J. R runtime check script is tracked")

print("[K] S boundary doc/script exist and are tracked")
ok("K. S boundary doc exists") if S_DOC_PATH.exists() else xx("K. S boundary doc exists")
ok("K. S boundary doc is tracked") if git_tracked(
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_DASHBOARD_INTEGRATION_BOUNDARY_PLAN_V0_8_1_S.md"
) else xx("K. S boundary doc is tracked")
ok("K. S readiness script exists") if S_SCRIPT_PATH.exists() else xx("K. S readiness script exists")
ok("K. S readiness script is tracked") if git_tracked(
    "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_dashboard_integration_boundary_plan_v0_8_1_s.py"
) else xx("K. S readiness script is tracked")

print("[L] T authorization doc/script exist and are tracked")
ok("L. T authorization doc exists") if T_DOC_PATH.exists() else xx("L. T authorization doc exists")
ok("L. T authorization doc is tracked") if git_tracked(
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_DASHBOARD_INTEGRATION_AUTHORIZATION_PLAN_V0_8_1_T.md"
) else xx("L. T authorization doc is tracked")
ok("L. T readiness script exists") if T_SCRIPT_PATH.exists() else xx("L. T readiness script exists")
ok("L. T readiness script is tracked") if git_tracked(
    "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_dashboard_integration_authorization_plan_v0_8_1_t.py"
) else xx("L. T readiness script is tracked")

print("[M] U implementation plan doc/script exist and are tracked")
ok("M. U implementation plan doc exists") if U_DOC_PATH.exists() else xx("M. U implementation plan doc exists")
ok("M. U implementation plan doc is tracked") if git_tracked(
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_DASHBOARD_PREVIEW_INTEGRATION_IMPLEMENTATION_PLAN_V0_8_1_U.md"
) else xx("M. U implementation plan doc is tracked")
ok("M. U readiness script exists") if U_SCRIPT_PATH.exists() else xx("M. U readiness script exists")
ok("M. U readiness script is tracked") if git_tracked(
    "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_dashboard_preview_integration_implementation_plan_v0_8_1_u.py"
) else xx("M. U readiness script is tracked")

# ---------------------------------------------------------------------------
# [N] current HEAD contains EXPECTED_BASE_HEAD in git history
# ---------------------------------------------------------------------------
print("[N] current HEAD contains EXPECTED_BASE_HEAD in git history")
ancestor_check = subprocess.run(
    ["git", "-C", str(REPO_ROOT), "merge-base", "--is-ancestor", EXPECTED_BASE_HEAD, "HEAD"],
    capture_output=True,
    text=True,
)
ok(f"N. HEAD contains {EXPECTED_BASE_HEAD} in git history") if ancestor_check.returncode == 0 else xx(
    f"N. HEAD contains {EXPECTED_BASE_HEAD} in git history（merge-base check failed）"
)

# ---------------------------------------------------------------------------
# [O/P] no __main__ block / no CLI entrypoint
# ---------------------------------------------------------------------------
print("[O] V adapter has no __main__ block")
ok("O. V adapter has no __main__ block") if "__main__" not in adapter_source else xx(
    "O. V adapter has no __main__ block"
)

print("[P] V adapter has no CLI entrypoint")
cli_markers = ["ArgumentParser", "sys.argv", "argv[1:]", "add_argument"]
found_cli = [m for m in cli_markers if m in adapter_source]
ok("P. V adapter has no CLI entrypoint") if not found_cli else xx(
    f"P. V adapter has no CLI entrypoint（found {found_cli}）"
)

# ---------------------------------------------------------------------------
# [Q/R/S] AST-based import check
# ---------------------------------------------------------------------------
print("[Q] V adapter imports only allowed modules")
tree = ast.parse(adapter_source, filename=str(V_ADAPTER_PATH))
import_roots: set[str] = set()
imported_names: set[str] = set()
for node in ast.walk(tree):
    if isinstance(node, ast.Import):
        for alias in node.names:
            import_roots.add(alias.name.split(".")[0])
    elif isinstance(node, ast.ImportFrom):
        if node.module:
            import_roots.add(node.module.split(".")[0])
        for alias in node.names:
            imported_names.add(alias.name)

disallowed_roots = import_roots - ALLOWED_IMPORT_ROOTS
ok("Q. V adapter imports only allowed modules") if not disallowed_roots else xx(
    f"Q. V adapter imports only allowed modules（found disallowed roots {sorted(disallowed_roots)}）"
)

print("[R] V adapter imports load_local_mock_fixture_preview")
ok("R. V adapter imports load_local_mock_fixture_preview") if "load_local_mock_fixture_preview" in imported_names else xx(
    "R. V adapter imports load_local_mock_fixture_preview"
)

print("[S] V adapter imports validate_local_mock_fixture_preview_object")
ok("S. V adapter imports validate_local_mock_fixture_preview_object") if "validate_local_mock_fixture_preview_object" in imported_names else xx(
    "S. V adapter imports validate_local_mock_fixture_preview_object"
)

# ---------------------------------------------------------------------------
# [T] fixture path literal must not appear (raw substring check)
# ---------------------------------------------------------------------------
print("[T] V adapter does not contain fixture path literal")
found_literals = [lit for lit in FIXTURE_PATH_LITERALS if lit in adapter_source]
ok("T. V adapter does not contain fixture path literal") if not found_literals else xx(
    f"T. V adapter does not contain fixture path literal（found {found_literals}）"
)

# ---------------------------------------------------------------------------
# [U] adapter does not directly read fixture JSON (no direct file I/O calls)
# ---------------------------------------------------------------------------
print("[U] V adapter does not directly read fixture JSON")
found_read_markers = [m for m in DIRECT_READ_MARKERS if m in adapter_source]
ok("U. V adapter does not directly read fixture JSON") if not found_read_markers else xx(
    f"U. V adapter does not directly read fixture JSON（found {found_read_markers}）"
)

# ---------------------------------------------------------------------------
# [V] forbidden identifiers must not appear as NAME tokens
# ---------------------------------------------------------------------------
print("[V] V adapter has no forbidden identifiers")
name_tokens: set[str] = set()
with open(V_ADAPTER_PATH, "rb") as f:
    for tok in tokenize.tokenize(f.readline):
        if tok.type == tokenize.NAME:
            name_tokens.add(tok.string)
found_forbidden = sorted(name_tokens & FORBIDDEN_IDENTIFIERS)
ok("V. V adapter has no forbidden identifiers") if not found_forbidden else xx(
    f"V. V adapter has no forbidden identifiers（found {found_forbidden}）"
)

# ---------------------------------------------------------------------------
# [W-Y] adapter exposes required functions
# ---------------------------------------------------------------------------
print("[W] V adapter exposes build_dashboard_preview_rows")
ok("W. V adapter exposes build_dashboard_preview_rows") if "build_dashboard_preview_rows" in adapter_source else xx(
    "W. V adapter exposes build_dashboard_preview_rows"
)

print("[X] V adapter exposes build_dashboard_preview_model")
ok("X. V adapter exposes build_dashboard_preview_model") if "build_dashboard_preview_model" in adapter_source else xx(
    "X. V adapter exposes build_dashboard_preview_model"
)

print("[Y] V adapter exposes validate_dashboard_preview_model")
ok("Y. V adapter exposes validate_dashboard_preview_model") if "validate_dashboard_preview_model" in adapter_source else xx(
    "Y. V adapter exposes validate_dashboard_preview_model"
)

# ---------------------------------------------------------------------------
# [Z-BE] functional runtime re-validation: dynamically import the V adapter
#        (scripts/ dir temporarily added to sys.path so the adapter's plain
#        import of the P loader module resolves) and re-exercise the built
#        rows/model.
# ---------------------------------------------------------------------------
print("[Z-BE] functional runtime re-validation")
scripts_dir = str(REPO_ROOT / "scripts")
sys_path_inserted = False
rows: list[dict[str, Any]] | None = None
model: dict[str, Any] | None = None
functional_error: str | None = None
module: Any = None
try:
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
        sys_path_inserted = True

    spec = importlib.util.spec_from_file_location(
        "local_mock_fixture_dashboard_preview_adapter_v0_8_1_w_check", V_ADAPTER_PATH
    )
    if spec is None or spec.loader is None:
        raise ImportError("could not load V adapter module spec")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    rows = module.build_dashboard_preview_rows()
    model = module.build_dashboard_preview_model()
except Exception as exc:  # noqa: BLE001 - surfaced as a single readiness failure below
    functional_error = f"{type(exc).__name__}: {exc}"
finally:
    if sys_path_inserted and scripts_dir in sys.path:
        sys.path.remove(scripts_dir)
        sys_path_inserted = False

SKIP_LABELS = [
    "AA. build_dashboard_preview_model() returns dict",
    "AB. model source = local_mock_fixture_dashboard_preview_adapter",
    "AC. model schema_version = v0.8.1-dashboard-preview-adapter-1",
    "AD. model adapter_version = v0.8.1-V",
    "AE. model is_mock = True",
    "AF. model local_only = True",
    "AG. model read_only = True",
    "AH. model execution_permission = False",
    "AI. model dispatch_permission = False",
    "AJ. model external_side_effects_permission = False",
    "AK. model runtime_badges exactly disabled badges",
    "AL. model row_count = 6",
    "AM. model rows list length = 6",
    "AN. model controls execution_controls_visible = False",
    "AO. model controls dispatch_controls_visible = False",
    "AP. model controls external_actions_visible = False",
    "AQ. every row has row_id",
    "AR. every row has display_index",
    "AS. every row has display_title",
    "AT. every row has display_summary",
    "AU. every row has local_only = True",
    "AV. every row has read_only = True",
    "AW. every row has execution_permission = False",
    "AX. every row has dispatch_permission = False",
    "AY. every row has external_side_effects_permission = False",
    "AZ. every row has exact disabled runtime badges",
    "BA. every row has no action_url/post_url/webhook_url/endpoint_url",
    "BB. every row has no execute_url/dispatch_url/execution_button/dispatch_button",
    "BC. rows are not the same object as loader preview records",
    "BD. build_dashboard_preview_rows() rows are not the same object as model rows",
    "BE. validate_dashboard_preview_model(model) passes",
]

if functional_error is not None or rows is None or model is None:
    xx(f"Z. build_dashboard_preview_rows() returns {EXPECTED_ROW_COUNT} rows（error: {functional_error}）")
    for label in SKIP_LABELS:
        xx(f"{label}（skipped, functional adapter unavailable）")
else:
    rows_ok = isinstance(rows, list) and len(rows) == EXPECTED_ROW_COUNT
    ok(f"Z. build_dashboard_preview_rows() returns {EXPECTED_ROW_COUNT} rows") if rows_ok else xx(
        f"Z. build_dashboard_preview_rows() returns {EXPECTED_ROW_COUNT} rows（found {len(rows) if isinstance(rows, list) else rows!r}）"
    )

    ok("AA. build_dashboard_preview_model() returns dict") if isinstance(model, dict) else xx(
        "AA. build_dashboard_preview_model() returns dict"
    )

    ok("AB. model source = local_mock_fixture_dashboard_preview_adapter") if model.get("source") == "local_mock_fixture_dashboard_preview_adapter" else xx(
        f"AB. model source = local_mock_fixture_dashboard_preview_adapter（found {model.get('source')!r}）"
    )
    ok("AC. model schema_version = v0.8.1-dashboard-preview-adapter-1") if model.get("schema_version") == EXPECTED_SCHEMA_VERSION else xx(
        f"AC. model schema_version = v0.8.1-dashboard-preview-adapter-1（found {model.get('schema_version')!r}）"
    )
    ok("AD. model adapter_version = v0.8.1-V") if model.get("adapter_version") == EXPECTED_ADAPTER_VERSION else xx(
        f"AD. model adapter_version = v0.8.1-V（found {model.get('adapter_version')!r}）"
    )
    ok("AE. model is_mock = True") if model.get("is_mock") is True else xx("AE. model is_mock = True")
    ok("AF. model local_only = True") if model.get("local_only") is True else xx("AF. model local_only = True")
    ok("AG. model read_only = True") if model.get("read_only") is True else xx("AG. model read_only = True")
    ok("AH. model execution_permission = False") if model.get("execution_permission") is False else xx(
        "AH. model execution_permission = False"
    )
    ok("AI. model dispatch_permission = False") if model.get("dispatch_permission") is False else xx(
        "AI. model dispatch_permission = False"
    )
    ok("AJ. model external_side_effects_permission = False") if model.get("external_side_effects_permission") is False else xx(
        "AJ. model external_side_effects_permission = False"
    )
    ok("AK. model runtime_badges exactly disabled badges") if model.get("runtime_badges") == EXPECTED_RUNTIME_BADGES else xx(
        f"AK. model runtime_badges exactly disabled badges（found {model.get('runtime_badges')!r}）"
    )
    ok("AL. model row_count = 6") if model.get("row_count") == EXPECTED_ROW_COUNT else xx(
        f"AL. model row_count = 6（found {model.get('row_count')!r}）"
    )

    model_rows = model.get("rows")
    model_rows_ok = isinstance(model_rows, list) and len(model_rows) == EXPECTED_ROW_COUNT
    ok("AM. model rows list length = 6") if model_rows_ok else xx(
        f"AM. model rows list length = 6（found {len(model_rows) if isinstance(model_rows, list) else model_rows!r}）"
    )

    controls = model.get("controls")
    controls_ok = isinstance(controls, dict)
    ok("AN. model controls execution_controls_visible = False") if controls_ok and controls.get("execution_controls_visible") is False else xx(
        "AN. model controls execution_controls_visible = False"
    )
    ok("AO. model controls dispatch_controls_visible = False") if controls_ok and controls.get("dispatch_controls_visible") is False else xx(
        "AO. model controls dispatch_controls_visible = False"
    )
    ok("AP. model controls external_actions_visible = False") if controls_ok and controls.get("external_actions_visible") is False else xx(
        "AP. model controls external_actions_visible = False"
    )

    if model_rows_ok:
        assert model_rows is not None
        ok("AQ. every row has row_id") if all("row_id" in r for r in model_rows) else xx("AQ. every row has row_id")
        ok("AR. every row has display_index") if all("display_index" in r for r in model_rows) else xx(
            "AR. every row has display_index"
        )
        ok("AS. every row has display_title") if all("display_title" in r for r in model_rows) else xx(
            "AS. every row has display_title"
        )
        ok("AT. every row has display_summary") if all("display_summary" in r for r in model_rows) else xx(
            "AT. every row has display_summary"
        )
        ok("AU. every row has local_only = True") if all(r.get("local_only") is True for r in model_rows) else xx(
            "AU. every row has local_only = True"
        )
        ok("AV. every row has read_only = True") if all(r.get("read_only") is True for r in model_rows) else xx(
            "AV. every row has read_only = True"
        )
        ok("AW. every row has execution_permission = False") if all(r.get("execution_permission") is False for r in model_rows) else xx(
            "AW. every row has execution_permission = False"
        )
        ok("AX. every row has dispatch_permission = False") if all(r.get("dispatch_permission") is False for r in model_rows) else xx(
            "AX. every row has dispatch_permission = False"
        )
        ok("AY. every row has external_side_effects_permission = False") if all(
            r.get("external_side_effects_permission") is False for r in model_rows
        ) else xx("AY. every row has external_side_effects_permission = False")
        ok("AZ. every row has exact disabled runtime badges") if all(
            r.get("runtime_badges") == EXPECTED_RUNTIME_BADGES for r in model_rows
        ) else xx("AZ. every row has exact disabled runtime badges")

        offending_a = [r for r in model_rows if {"action_url", "post_url", "webhook_url", "endpoint_url"} & set(r.keys())]
        ok("BA. every row has no action_url/post_url/webhook_url/endpoint_url") if not offending_a else xx(
            f"BA. every row has no action_url/post_url/webhook_url/endpoint_url（found in {len(offending_a)} row(s)）"
        )

        offending_b = [
            r for r in model_rows
            if {"execute_url", "dispatch_url", "execution_button", "dispatch_button"} & set(r.keys())
        ]
        ok("BB. every row has no execute_url/dispatch_url/execution_button/dispatch_button") if not offending_b else xx(
            f"BB. every row has no execute_url/dispatch_url/execution_button/dispatch_button（found in {len(offending_b)} row(s)）"
        )
    else:
        for label in [
            "AQ. every row has row_id",
            "AR. every row has display_index",
            "AS. every row has display_title",
            "AT. every row has display_summary",
            "AU. every row has local_only = True",
            "AV. every row has read_only = True",
            "AW. every row has execution_permission = False",
            "AX. every row has dispatch_permission = False",
            "AY. every row has external_side_effects_permission = False",
            "AZ. every row has exact disabled runtime badges",
            "BA. every row has no action_url/post_url/webhook_url/endpoint_url",
            "BB. every row has no execute_url/dispatch_url/execution_button/dispatch_button",
        ]:
            xx(f"{label}（skipped, model rows shape invalid）")

    # BC: rows returned by build_dashboard_preview_rows() must not be the same
    # object as the loader's own preview["records"] list.
    try:
        loader_spec = importlib.util.spec_from_file_location(
            "load_local_mock_fixture_preview_v0_8_1_w_check", P_LOADER_PATH
        )
        if loader_spec is None or loader_spec.loader is None:
            raise ImportError("could not load P loader module spec")
        loader_module = importlib.util.module_from_spec(loader_spec)
        loader_spec.loader.exec_module(loader_module)
        loader_preview = loader_module.load_local_mock_fixture_preview()
        identity_violation = rows_ok and rows is loader_preview.get("records")
        ok("BC. rows are not the same object as loader preview records") if not identity_violation else xx(
            "BC. rows are not the same object as loader preview records"
        )
    except Exception as exc:  # noqa: BLE001
        xx(f"BC. rows are not the same object as loader preview records（error: {type(exc).__name__}: {exc}）")

    # BD: rows returned by a fresh call to build_dashboard_preview_rows() must
    # not be the same list object as model["rows"] (each call builds new rows).
    identity_violation_bd = rows_ok and model_rows_ok and rows is model_rows
    ok("BD. build_dashboard_preview_rows() rows are not the same object as model rows") if not identity_violation_bd else xx(
        "BD. build_dashboard_preview_rows() rows are not the same object as model rows"
    )

    try:
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
            sys_path_inserted = True
        module.validate_dashboard_preview_model(model)
        ok("BE. validate_dashboard_preview_model(model) passes")
    except Exception as exc:  # noqa: BLE001
        xx(f"BE. validate_dashboard_preview_model(model) passes（error: {type(exc).__name__}: {exc}）")
    finally:
        if sys_path_inserted and scripts_dir in sys.path:
            sys.path.remove(scripts_dir)
            sys_path_inserted = False

# ---------------------------------------------------------------------------
# [BF] adapter source contains copy.deepcopy / copy.copy safe-copy behavior
# ---------------------------------------------------------------------------
print("[BF] V adapter source contains copy.deepcopy or copy.copy / safe copy behavior")
found_copy = [m for m in ["copy.deepcopy", "copy.copy"] if m in adapter_source]
ok("BF. V adapter source contains copy.deepcopy or copy.copy") if found_copy else xx(
    "BF. V adapter source contains copy.deepcopy or copy.copy"
)

# ---------------------------------------------------------------------------
# [BG] adapter source has no raw file-write code identifiers
# ---------------------------------------------------------------------------
print("[BG] V adapter source has no raw file-write code identifiers")
found_write_markers = [m for m in FORBIDDEN_WRITE_MARKERS if m in adapter_source]
ok("BG. V adapter source has no raw file-write code identifiers") if not found_write_markers else xx(
    f"BG. V adapter source has no raw file-write code identifiers（found {found_write_markers}）"
)

# ---------------------------------------------------------------------------
# [BH] no tracked working-tree modifications
# ---------------------------------------------------------------------------
print("[BH] no tracked working-tree modifications")
diff_out = subprocess.run(
    ["git", "-C", str(REPO_ROOT), "diff", "--name-only"],
    capture_output=True,
    text=True,
)
tracked_changes = [l for l in diff_out.stdout.splitlines() if l.strip()]
ok("BH. no tracked working-tree modifications") if not tracked_changes else xx(
    f"BH. no tracked working-tree modifications（found {tracked_changes}）"
)

# ---------------------------------------------------------------------------
# [BI] no Dashboard/app/templates/static files changed (staged or unstaged)
# ---------------------------------------------------------------------------
print("[BI] no Dashboard/app/templates/static files changed")
status_out = subprocess.run(
    ["git", "-C", str(REPO_ROOT), "status", "--porcelain"],
    capture_output=True,
    text=True,
)
changed_paths = []
for line in status_out.stdout.splitlines():
    if not line.strip():
        continue
    # porcelain format: XY <path>  (path starts at column 3)
    path = line[3:].strip()
    changed_paths.append(path)
dashboard_changes = [
    p for p in changed_paths if any(p.startswith(pref) for pref in DASHBOARD_PROTECTED_PREFIXES)
]
ok("BI. no Dashboard/app/templates/static files changed") if not dashboard_changes else xx(
    f"BI. no Dashboard/app/templates/static files changed（found {dashboard_changes}）"
)

# ---------------------------------------------------------------------------
# [BJ] no extra untracked files beyond allowed W file and existing patches/
# ---------------------------------------------------------------------------
print("[BJ] no extra untracked files beyond allowed W file and patches/")
others_out = subprocess.run(
    ["git", "-C", str(REPO_ROOT), "ls-files", "--others", "--exclude-standard"],
    capture_output=True,
    text=True,
)
ALLOWED_UNTRACKED = {
    "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_runtime_check_v0_8_1_w.py",
}
untracked = [l for l in others_out.stdout.splitlines() if l.strip()]
unexpected = [
    u for u in untracked if u not in ALLOWED_UNTRACKED and not u.startswith("patches/")
]
ok("BJ. no unexpected untracked files") if not unexpected else xx(
    f"BJ. no unexpected untracked files（found {unexpected}）"
)

# ---------------------------------------------------------------------------
# 結果
# ---------------------------------------------------------------------------
total = len(PASS) + len(FAIL)
print(f"\n合計：{len(PASS)}/{total} 通過")
if FAIL:
    print(f"\nXX v0.8.1-W readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print("PASS: v0.8.1-W dashboard preview adapter runtime check")
    sys.exit(0)
