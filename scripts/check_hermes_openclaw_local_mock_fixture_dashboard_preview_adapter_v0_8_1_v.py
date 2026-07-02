"""v0.8.1-V readiness check: Local Mock Fixture Dashboard Preview Adapter.

Pure local filesystem validation. This script statically inspects the v0.8.1-V adapter source (AST
imports, tokenize NAME identifiers, raw fixture-path-literal substring check), confirms the tracked
state of the L/M/N/O/P/Q/R/S/T/U artifacts, dynamically imports the V adapter (which in turn imports
the already-authorized v0.8.1-P loader) to functionally validate the produced preview model, and uses
`git` read-only (ls-files / diff / status) to confirm tracked status and that no extra repo files
exist. It never modifies the git index or any repo file.

It does NOT import Dashboard, app runtime, QueueStore, or any Worker/OpenClaw/Hermes/Google Sheets
integration; it reads no real queue DB, sends no POST, makes no network call, reads no secrets,
writes no repo file, modifies no loader, and modifies no Dashboard. It does not read the fixture JSON
directly itself; the only fixture read happens inside the already-authorized v0.8.1-P loader that the
adapter calls.
"""
from __future__ import annotations

import ast
import importlib.util
import subprocess
import sys
import tokenize
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

V_ADAPTER_PATH = REPO_ROOT / "scripts/local_mock_fixture_dashboard_preview_adapter_v0_8_1.py"
V_SCRIPT_PATH = REPO_ROOT / "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_v0_8_1_v.py"

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

EXPECTED_HEAD = "acf6dd4493b4c99b11c608476d161f29beca8c9e"
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

REQUIRED_ADAPTER_PHRASES = [
    "v0.8.1-V is read-only Dashboard preview adapter implementation.",
    "v0.8.1-V only converts the v0.8.1-P loader returned in-memory preview object into read-only Dashboard display rows.",
    "v0.8.1-V does not modify Dashboard.",
    "v0.8.1-V does not create Dashboard route.",
    "v0.8.1-V does not create Dashboard endpoint.",
    "v0.8.1-V does not create Dashboard template.",
    "v0.8.1-V does not create Dashboard static asset.",
    "v0.8.1-V does not modify loader.",
    "v0.8.1-V does not read fixture JSON directly.",
    "v0.8.1-V does not read real queue DB.",
    "v0.8.1-V does not write queue data.",
    "v0.8.1-V does not send POST.",
    "v0.8.1-V does not make network calls.",
    "v0.8.1-V does not start Worker.",
    "v0.8.1-V does not call OpenClaw.",
    "v0.8.1-V does not activate Hermes.",
    "v0.8.1-V does not read Google Sheets.",
    "v0.8.1-V does not write Google Sheets.",
    "v0.8.1-V does not read secrets.",
    "v0.8.1-V does not create .env.",
    "v0.8.1-V does not create webhook.",
    "v0.8.1-V does not create connector.",
    "v0.8.1-V does not create production DB.",
    "v0.8.1-V does not create shared DB.",
    "v0.8.1-V does not create Remote Blackboard API runtime.",
    "v0.8.1-V does not commit.",
    "v0.8.1-V does not push.",
    "v0.8.1-V does not tag.",
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

FIXTURE_PATH_LITERALS = [
    "fixtures/local_mock_data/hermes_openclaw_local_mock_messages_v0_8_1.json",
    "hermes_openclaw_local_mock_messages_v0_8_1.json",
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
# [A/B] V adapter + readiness script exist
# ---------------------------------------------------------------------------
print("[A] V adapter exists")
ok("A. V adapter exists") if V_ADAPTER_PATH.exists() else xx("A. V adapter exists")
if not V_ADAPTER_PATH.exists():
    print("\nXX V adapter 不存在，無法繼續")
    sys.exit(1)

print("[B] V validation/readiness script path is correct")
ok("B. V validation/readiness script exists at expected path") if V_SCRIPT_PATH.exists() else xx(
    "B. V validation/readiness script exists at expected path"
)

adapter_source = V_ADAPTER_PATH.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# [C-L] L/M/N/O/P/Q/R/S/T/U artifacts exist and are tracked
# ---------------------------------------------------------------------------
print("[C] L fixture JSON exists and is tracked")
ok("C. L fixture JSON exists") if FIXTURE_PATH.exists() else xx("C. L fixture JSON exists")
ok("C. L fixture JSON is tracked") if git_tracked(
    "fixtures/local_mock_data/hermes_openclaw_local_mock_messages_v0_8_1.json"
) else xx("C. L fixture JSON is tracked")

print("[D] M validation doc/script exist and are tracked")
ok("D. M validation doc exists") if M_DOC_PATH.exists() else xx("D. M validation doc exists")
ok("D. M validation doc is tracked") if git_tracked(
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_DATA_FIXTURE_JSON_ARTIFACT_VALIDATION_V0_8_1_M.md"
) else xx("D. M validation doc is tracked")
ok("D. M validation script exists") if M_SCRIPT_PATH.exists() else xx("D. M validation script exists")
ok("D. M validation script is tracked") if git_tracked(
    "scripts/check_hermes_openclaw_local_mock_data_fixture_json_artifact_validation_v0_8_1_m.py"
) else xx("D. M validation script is tracked")

print("[E] N plan doc/script exist and are tracked")
ok("E. N plan doc exists") if N_DOC_PATH.exists() else xx("E. N plan doc exists")
ok("E. N plan doc is tracked") if git_tracked(
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_PLAN_V0_8_1_N.md"
) else xx("E. N plan doc is tracked")
ok("E. N readiness script exists") if N_SCRIPT_PATH.exists() else xx("E. N readiness script exists")
ok("E. N readiness script is tracked") if git_tracked(
    "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_plan_v0_8_1_n.py"
) else xx("E. N readiness script is tracked")

print("[F] O authorization doc/script exist and are tracked")
ok("F. O authorization doc exists") if O_DOC_PATH.exists() else xx("F. O authorization doc exists")
ok("F. O authorization doc is tracked") if git_tracked(
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_IMPLEMENTATION_AUTHORIZATION_PLAN_V0_8_1_O.md"
) else xx("F. O authorization doc is tracked")
ok("F. O readiness script exists") if O_SCRIPT_PATH.exists() else xx("F. O readiness script exists")
ok("F. O readiness script is tracked") if git_tracked(
    "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_implementation_authorization_plan_v0_8_1_o.py"
) else xx("F. O readiness script is tracked")

print("[G] P loader exists and is tracked")
ok("G. P loader exists") if P_LOADER_PATH.exists() else xx("G. P loader exists")
ok("G. P loader is tracked") if git_tracked(
    "scripts/load_local_mock_fixture_preview_v0_8_1.py"
) else xx("G. P loader is tracked")

print("[H] Q validation doc/script exist and are tracked")
ok("H. Q validation doc exists") if Q_DOC_PATH.exists() else xx("H. Q validation doc exists")
ok("H. Q validation doc is tracked") if git_tracked(
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_VALIDATION_PLAN_V0_8_1_Q.md"
) else xx("H. Q validation doc is tracked")
ok("H. Q readiness script exists") if Q_SCRIPT_PATH.exists() else xx("H. Q readiness script exists")
ok("H. Q readiness script is tracked") if git_tracked(
    "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_validation_plan_v0_8_1_q.py"
) else xx("H. Q readiness script is tracked")

print("[I] R runtime check script exists and is tracked")
ok("I. R runtime check script exists") if R_SCRIPT_PATH.exists() else xx("I. R runtime check script exists")
ok("I. R runtime check script is tracked") if git_tracked(
    "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_runtime_check_v0_8_1_r.py"
) else xx("I. R runtime check script is tracked")

print("[J] S boundary doc/script exist and are tracked")
ok("J. S boundary doc exists") if S_DOC_PATH.exists() else xx("J. S boundary doc exists")
ok("J. S boundary doc is tracked") if git_tracked(
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_DASHBOARD_INTEGRATION_BOUNDARY_PLAN_V0_8_1_S.md"
) else xx("J. S boundary doc is tracked")
ok("J. S readiness script exists") if S_SCRIPT_PATH.exists() else xx("J. S readiness script exists")
ok("J. S readiness script is tracked") if git_tracked(
    "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_dashboard_integration_boundary_plan_v0_8_1_s.py"
) else xx("J. S readiness script is tracked")

print("[K] T authorization doc/script exist and are tracked")
ok("K. T authorization doc exists") if T_DOC_PATH.exists() else xx("K. T authorization doc exists")
ok("K. T authorization doc is tracked") if git_tracked(
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_DASHBOARD_INTEGRATION_AUTHORIZATION_PLAN_V0_8_1_T.md"
) else xx("K. T authorization doc is tracked")
ok("K. T readiness script exists") if T_SCRIPT_PATH.exists() else xx("K. T readiness script exists")
ok("K. T readiness script is tracked") if git_tracked(
    "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_dashboard_integration_authorization_plan_v0_8_1_t.py"
) else xx("K. T readiness script is tracked")

print("[L] U implementation plan doc/script exist and are tracked")
ok("L. U implementation plan doc exists") if U_DOC_PATH.exists() else xx("L. U implementation plan doc exists")
ok("L. U implementation plan doc is tracked") if git_tracked(
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_DASHBOARD_PREVIEW_INTEGRATION_IMPLEMENTATION_PLAN_V0_8_1_U.md"
) else xx("L. U implementation plan doc is tracked")
ok("L. U readiness script exists") if U_SCRIPT_PATH.exists() else xx("L. U readiness script exists")
ok("L. U readiness script is tracked") if git_tracked(
    "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_dashboard_preview_integration_implementation_plan_v0_8_1_u.py"
) else xx("L. U readiness script is tracked")

# ---------------------------------------------------------------------------
# [M] V adapter positioning / safety boundary phrases
# ---------------------------------------------------------------------------
print("[M] V adapter contains v0.8.1-V positioning and safety boundaries")
missing_phrases = [p for p in REQUIRED_ADAPTER_PHRASES if p not in adapter_source]
ok("M. V adapter contains all required positioning/safety phrases") if not missing_phrases else xx(
    f"M. V adapter contains all required positioning/safety phrases（missing {missing_phrases}）"
)

# ---------------------------------------------------------------------------
# [N/O] no __main__ block / no CLI entrypoint
# ---------------------------------------------------------------------------
print("[N] V adapter has no __main__ block")
ok("N. V adapter has no __main__ block") if "__main__" not in adapter_source else xx(
    "N. V adapter has no __main__ block"
)

print("[O] V adapter has no CLI entrypoint")
cli_markers = ["ArgumentParser", "sys.argv", "argv[1:]", "add_argument"]
found_cli = [m for m in cli_markers if m in adapter_source]
ok("O. V adapter has no CLI entrypoint") if not found_cli else xx(
    f"O. V adapter has no CLI entrypoint（found {found_cli}）"
)

# ---------------------------------------------------------------------------
# [P/Q/R] AST-based import check
# ---------------------------------------------------------------------------
print("[P] V adapter imports only allowed modules")
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
ok("P. V adapter imports only allowed modules") if not disallowed_roots else xx(
    f"P. V adapter imports only allowed modules（found disallowed roots {sorted(disallowed_roots)}）"
)

print("[Q] V adapter imports load_local_mock_fixture_preview")
ok("Q. V adapter imports load_local_mock_fixture_preview") if "load_local_mock_fixture_preview" in imported_names else xx(
    "Q. V adapter imports load_local_mock_fixture_preview"
)

print("[R] V adapter imports validate_local_mock_fixture_preview_object")
ok("R. V adapter imports validate_local_mock_fixture_preview_object") if "validate_local_mock_fixture_preview_object" in imported_names else xx(
    "R. V adapter imports validate_local_mock_fixture_preview_object"
)

# ---------------------------------------------------------------------------
# [S] fixture path literal must not appear (raw substring check)
# ---------------------------------------------------------------------------
print("[S] V adapter does not contain fixture path literal")
found_literals = [lit for lit in FIXTURE_PATH_LITERALS if lit in adapter_source]
ok("S. V adapter does not contain fixture path literal") if not found_literals else xx(
    f"S. V adapter does not contain fixture path literal（found {found_literals}）"
)

# ---------------------------------------------------------------------------
# [T] adapter does not directly read fixture JSON (no direct file I/O calls)
# ---------------------------------------------------------------------------
print("[T] V adapter does not directly read fixture JSON")
direct_read_markers = ["read_text", "json.load", "json.loads", "Path.read_text", "open("]
found_read_markers = [m for m in direct_read_markers if m in adapter_source]
ok("T. V adapter does not directly read fixture JSON") if not found_read_markers else xx(
    f"T. V adapter does not directly read fixture JSON（found {found_read_markers}）"
)

# ---------------------------------------------------------------------------
# [U] forbidden identifiers must not appear as NAME tokens
# ---------------------------------------------------------------------------
print("[U] V adapter does not contain forbidden identifiers")
name_tokens: set[str] = set()
with open(V_ADAPTER_PATH, "rb") as f:
    for tok in tokenize.tokenize(f.readline):
        if tok.type == tokenize.NAME:
            name_tokens.add(tok.string)
found_forbidden = sorted(name_tokens & FORBIDDEN_IDENTIFIERS)
ok("U. V adapter does not contain forbidden identifiers") if not found_forbidden else xx(
    f"U. V adapter does not contain forbidden identifiers（found {found_forbidden}）"
)

# ---------------------------------------------------------------------------
# [V-X] adapter exposes required functions
# ---------------------------------------------------------------------------
print("[V] V adapter exposes build_dashboard_preview_rows")
ok("V. V adapter exposes build_dashboard_preview_rows") if "build_dashboard_preview_rows" in adapter_source else xx(
    "V. V adapter exposes build_dashboard_preview_rows"
)

print("[W] V adapter exposes build_dashboard_preview_model")
ok("W. V adapter exposes build_dashboard_preview_model") if "build_dashboard_preview_model" in adapter_source else xx(
    "W. V adapter exposes build_dashboard_preview_model"
)

print("[X] V adapter exposes validate_dashboard_preview_model")
ok("X. V adapter exposes validate_dashboard_preview_model") if "validate_dashboard_preview_model" in adapter_source else xx(
    "X. V adapter exposes validate_dashboard_preview_model"
)

# ---------------------------------------------------------------------------
# [Y-AS] functional validation: dynamically import the V adapter (scripts/
#        dir temporarily added to sys.path so the adapter's plain import of
#        the P loader module resolves) and exercise the built model.
# ---------------------------------------------------------------------------
print("[Y-AS] functional model validation")
scripts_dir = str(REPO_ROOT / "scripts")
sys_path_inserted = False
model: dict[str, Any] | None = None
functional_error: str | None = None
try:
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
        sys_path_inserted = True

    spec = importlib.util.spec_from_file_location(
        "local_mock_fixture_dashboard_preview_adapter_v0_8_1", V_ADAPTER_PATH
    )
    if spec is None or spec.loader is None:
        raise ImportError("could not load V adapter module spec")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    model = module.build_dashboard_preview_model()
    module.validate_dashboard_preview_model(model)
except Exception as exc:  # noqa: BLE001 - surfaced as a single readiness failure below
    functional_error = f"{type(exc).__name__}: {exc}"
finally:
    if sys_path_inserted and scripts_dir in sys.path:
        sys.path.remove(scripts_dir)

if functional_error is not None or model is None:
    xx(f"Y. build_dashboard_preview_model() passes（error: {functional_error}）")
    for label in [
        "Z. model source = local_mock_fixture_dashboard_preview_adapter",
        "AA. model schema_version = v0.8.1-dashboard-preview-adapter-1",
        "AB. model adapter_version = v0.8.1-V",
        "AC. model is_mock = True",
        "AD. model local_only = True",
        "AE. model read_only = True",
        "AF. model execution_permission = False",
        "AG. model dispatch_permission = False",
        "AH. model external_side_effects_permission = False",
        "AI. model runtime_badges exactly disabled badges",
        "AJ. model row_count = 6",
        "AK. model rows list length = 6",
        "AL. every row has local_only = True",
        "AM. every row has read_only = True",
        "AN. every row has execution_permission = False",
        "AO. every row has dispatch_permission = False",
        "AP. every row has external_side_effects_permission = False",
        "AQ. every row has no action/execution/dispatch URL/control fields",
        "AR. rows are not the same object as loader preview records",
        "AS. validate_dashboard_preview_model(model) passes",
    ]:
        xx(f"{label}（skipped, functional model unavailable）")
else:
    ok("Y. build_dashboard_preview_model() passes")

    ok("Z. model source = local_mock_fixture_dashboard_preview_adapter") if model.get("source") == "local_mock_fixture_dashboard_preview_adapter" else xx(
        f"Z. model source = local_mock_fixture_dashboard_preview_adapter（found {model.get('source')!r}）"
    )
    ok("AA. model schema_version = v0.8.1-dashboard-preview-adapter-1") if model.get("schema_version") == EXPECTED_SCHEMA_VERSION else xx(
        f"AA. model schema_version = v0.8.1-dashboard-preview-adapter-1（found {model.get('schema_version')!r}）"
    )
    ok("AB. model adapter_version = v0.8.1-V") if model.get("adapter_version") == EXPECTED_ADAPTER_VERSION else xx(
        f"AB. model adapter_version = v0.8.1-V（found {model.get('adapter_version')!r}）"
    )
    ok("AC. model is_mock = True") if model.get("is_mock") is True else xx("AC. model is_mock = True")
    ok("AD. model local_only = True") if model.get("local_only") is True else xx("AD. model local_only = True")
    ok("AE. model read_only = True") if model.get("read_only") is True else xx("AE. model read_only = True")
    ok("AF. model execution_permission = False") if model.get("execution_permission") is False else xx(
        "AF. model execution_permission = False"
    )
    ok("AG. model dispatch_permission = False") if model.get("dispatch_permission") is False else xx(
        "AG. model dispatch_permission = False"
    )
    ok("AH. model external_side_effects_permission = False") if model.get("external_side_effects_permission") is False else xx(
        "AH. model external_side_effects_permission = False"
    )
    ok("AI. model runtime_badges exactly disabled badges") if model.get("runtime_badges") == EXPECTED_RUNTIME_BADGES else xx(
        f"AI. model runtime_badges exactly disabled badges（found {model.get('runtime_badges')!r}）"
    )
    ok("AJ. model row_count = 6") if model.get("row_count") == EXPECTED_ROW_COUNT else xx(
        f"AJ. model row_count = 6（found {model.get('row_count')!r}）"
    )

    rows = model.get("rows")
    rows_ok = isinstance(rows, list) and len(rows) == EXPECTED_ROW_COUNT
    ok("AK. model rows list length = 6") if rows_ok else xx(
        f"AK. model rows list length = 6（found {len(rows) if isinstance(rows, list) else rows!r}）"
    )

    if rows_ok:
        assert rows is not None
        all_local_only = all(r.get("local_only") is True for r in rows)
        ok("AL. every row has local_only = True") if all_local_only else xx("AL. every row has local_only = True")

        all_read_only = all(r.get("read_only") is True for r in rows)
        ok("AM. every row has read_only = True") if all_read_only else xx("AM. every row has read_only = True")

        all_no_exec = all(r.get("execution_permission") is False for r in rows)
        ok("AN. every row has execution_permission = False") if all_no_exec else xx(
            "AN. every row has execution_permission = False"
        )

        all_no_dispatch = all(r.get("dispatch_permission") is False for r in rows)
        ok("AO. every row has dispatch_permission = False") if all_no_dispatch else xx(
            "AO. every row has dispatch_permission = False"
        )

        all_no_external = all(r.get("external_side_effects_permission") is False for r in rows)
        ok("AP. every row has external_side_effects_permission = False") if all_no_external else xx(
            "AP. every row has external_side_effects_permission = False"
        )

        forbidden_row_keys = {
            "action_url",
            "post_url",
            "webhook_url",
            "endpoint_url",
            "execution_button",
            "dispatch_button",
            "execute_url",
            "dispatch_url",
            "external_control",
        }
        offending_rows = [r for r in rows if forbidden_row_keys & set(r.keys())]
        ok("AQ. every row has no action/execution/dispatch URL/control fields") if not offending_rows else xx(
            f"AQ. every row has no action/execution/dispatch URL/control fields（found in {len(offending_rows)} row(s)）"
        )
    else:
        for label in [
            "AL. every row has local_only = True",
            "AM. every row has read_only = True",
            "AN. every row has execution_permission = False",
            "AO. every row has dispatch_permission = False",
            "AP. every row has external_side_effects_permission = False",
            "AQ. every row has no action/execution/dispatch URL/control fields",
        ]:
            xx(f"{label}（skipped, rows shape invalid）")

    # Confirm rows are not the same object as the loader's own preview records list.
    try:
        loader_spec = importlib.util.spec_from_file_location(
            "load_local_mock_fixture_preview_v0_8_1_readonly_check", P_LOADER_PATH
        )
        if loader_spec is None or loader_spec.loader is None:
            raise ImportError("could not load P loader module spec")
        loader_module = importlib.util.module_from_spec(loader_spec)
        loader_spec.loader.exec_module(loader_module)
        loader_preview = loader_module.load_local_mock_fixture_preview()
        identity_violation = rows_ok and rows is loader_preview.get("records")
        ok("AR. rows are not the same object as loader preview records") if not identity_violation else xx(
            "AR. rows are not the same object as loader preview records"
        )
    except Exception as exc:  # noqa: BLE001
        xx(f"AR. rows are not the same object as loader preview records（error: {type(exc).__name__}: {exc}）")

    try:
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
            sys_path_inserted = True
        module.validate_dashboard_preview_model(model)
        ok("AS. validate_dashboard_preview_model(model) passes")
    except Exception as exc:  # noqa: BLE001
        xx(f"AS. validate_dashboard_preview_model(model) passes（error: {type(exc).__name__}: {exc}）")
    finally:
        if sys_path_inserted and scripts_dir in sys.path:
            sys.path.remove(scripts_dir)
            sys_path_inserted = False

# ---------------------------------------------------------------------------
# [AT] no tracked working-tree modifications
# ---------------------------------------------------------------------------
print("[AT] no tracked working-tree modifications")
diff_out = subprocess.run(
    ["git", "-C", str(REPO_ROOT), "diff", "--name-only"],
    capture_output=True,
    text=True,
)
tracked_changes = [l for l in diff_out.stdout.splitlines() if l.strip()]
ok("AT. no tracked working-tree modifications") if not tracked_changes else xx(
    f"AT. no tracked working-tree modifications（found {tracked_changes}）"
)

# ---------------------------------------------------------------------------
# [AU] no Dashboard/app/templates/static files changed (staged or unstaged)
# ---------------------------------------------------------------------------
print("[AU] no Dashboard/app/templates/static files changed")
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
ok("AU. no Dashboard/app/templates/static files changed") if not dashboard_changes else xx(
    f"AU. no Dashboard/app/templates/static files changed（found {dashboard_changes}）"
)

# ---------------------------------------------------------------------------
# [AV] no extra untracked files beyond allowed V files and existing patches/
# ---------------------------------------------------------------------------
print("[AV] no extra untracked files beyond allowed V files and patches/")
others_out = subprocess.run(
    ["git", "-C", str(REPO_ROOT), "ls-files", "--others", "--exclude-standard"],
    capture_output=True,
    text=True,
)
ALLOWED_UNTRACKED = {
    "scripts/local_mock_fixture_dashboard_preview_adapter_v0_8_1.py",
    "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_v0_8_1_v.py",
}
untracked = [l for l in others_out.stdout.splitlines() if l.strip()]
unexpected = [
    u for u in untracked if u not in ALLOWED_UNTRACKED and not u.startswith("patches/")
]
ok("AV. no unexpected untracked files") if not unexpected else xx(
    f"AV. no unexpected untracked files（found {unexpected}）"
)

# ---------------------------------------------------------------------------
# 結果
# ---------------------------------------------------------------------------
total = len(PASS) + len(FAIL)
print(f"\n合計：{len(PASS)}/{total} 通過")
if FAIL:
    print(f"\nXX v0.8.1-V readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print("PASS: v0.8.1-V local mock fixture dashboard preview adapter")
    sys.exit(0)
