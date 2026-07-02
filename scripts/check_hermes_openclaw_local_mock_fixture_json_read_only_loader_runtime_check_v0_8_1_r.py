"""v0.8.1-R runtime check: Local Mock Fixture Read-only Loader Runtime Check.

Re-runs and validates the v0.8.1-P read-only loader at runtime: import-based self-test, output
contract, permission flags, no __main__ / CLI entrypoint, standard-library-only imports, no
app/QueueStore/Dashboard/Worker/OpenClaw/Hermes/Google Sheets imports, and no real queue DB / POST /
network / secrets access. It also confirms the loader returns a deep-copied records list rather than
aliasing the on-disk fixture.

Pure local filesystem validation. This script reads only the v0.8.1-P loader, the v0.8.1-L fixture
JSON, and the v0.8.1-M/N/O/Q docs/scripts. It imports the P loader (via importlib, from its file
path) for an import-based self-test; the loader in turn runs the tracked v0.8.1-M validation script
as a subprocess. It uses `git` read-only (ls-files / diff / status / merge-base) to confirm tracked
status and that no extra repo files exist; it never modifies the git index.

The loader source is inspected with `ast` (imports) and `tokenize` (NAME identifier tokens) so the
loader's own safety-documentation docstring — which legitimately mentions words like "POST", ".env",
"QueueStore" as prose — is not mis-flagged. Only real imports and real code identifiers are checked.

It does NOT read real queue DB, send POST, read the network, read secrets, import app runtime,
import QueueStore, start Worker/OpenClaw/Hermes/Google Sheets, write any repo file, modify the
loader, or modify the Dashboard.
"""
from __future__ import annotations

import ast
import importlib.util
import io
import json
import subprocess
import sys
import tokenize
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

R_SCRIPT_PATH = REPO_ROOT / "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_runtime_check_v0_8_1_r.py"

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

EXPECTED_BASE_HEAD = "e09b790dede5e1503ea834272e1dcc5f139ac9d7"
EXPECTED_SCHEMA_VERSION = "v0.8.1-local-mock-1"
EXPECTED_RECORD_COUNT = 6

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
    "json",
    "subprocess",
    "sys",
    "pathlib",
    "typing",
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
    "dashboard",
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

# Code identifiers that would indicate the loader writes/deletes files.
FILE_WRITE_IDENTIFIERS = {"write_text", "write_bytes", "open", "remove", "unlink", "rmtree", "mkdir", "rename"}

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
# [A] R runtime check script path is correct
# ---------------------------------------------------------------------------
print("[A] R runtime check script path is correct")
ok("A. R runtime check script exists at expected path") if R_SCRIPT_PATH.exists() else xx(
    "A. R runtime check script exists at expected path"
)

# ---------------------------------------------------------------------------
# [B-G] L/M/N/O/P/Q artifacts exist and are tracked
# ---------------------------------------------------------------------------
print("[B] L fixture JSON exists and is tracked")
ok("B. L fixture JSON exists") if FIXTURE_PATH.exists() else xx("B. L fixture JSON exists")
ok("B. L fixture JSON is tracked") if git_tracked(
    "fixtures/local_mock_data/hermes_openclaw_local_mock_messages_v0_8_1.json"
) else xx("B. L fixture JSON is tracked")

print("[C] M validation doc/script exist and are tracked")
ok("C. M validation doc exists") if M_DOC_PATH.exists() else xx("C. M validation doc exists")
ok("C. M validation doc is tracked") if git_tracked(
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_DATA_FIXTURE_JSON_ARTIFACT_VALIDATION_V0_8_1_M.md"
) else xx("C. M validation doc is tracked")
ok("C. M validation script exists") if M_SCRIPT_PATH.exists() else xx("C. M validation script exists")
ok("C. M validation script is tracked") if git_tracked(
    "scripts/check_hermes_openclaw_local_mock_data_fixture_json_artifact_validation_v0_8_1_m.py"
) else xx("C. M validation script is tracked")

print("[D] N plan doc/script exist and are tracked")
ok("D. N plan doc exists") if N_DOC_PATH.exists() else xx("D. N plan doc exists")
ok("D. N plan doc is tracked") if git_tracked(
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_PLAN_V0_8_1_N.md"
) else xx("D. N plan doc is tracked")
ok("D. N readiness script exists") if N_SCRIPT_PATH.exists() else xx("D. N readiness script exists")
ok("D. N readiness script is tracked") if git_tracked(
    "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_plan_v0_8_1_n.py"
) else xx("D. N readiness script is tracked")

print("[E] O authorization doc/script exist and are tracked")
ok("E. O authorization doc exists") if O_DOC_PATH.exists() else xx("E. O authorization doc exists")
ok("E. O authorization doc is tracked") if git_tracked(
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_IMPLEMENTATION_AUTHORIZATION_PLAN_V0_8_1_O.md"
) else xx("E. O authorization doc is tracked")
ok("E. O readiness script exists") if O_SCRIPT_PATH.exists() else xx("E. O readiness script exists")
ok("E. O readiness script is tracked") if git_tracked(
    "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_implementation_authorization_plan_v0_8_1_o.py"
) else xx("E. O readiness script is tracked")

print("[F] P loader exists and is tracked")
ok("F. P loader exists") if P_LOADER_PATH.exists() else xx("F. P loader exists")
ok("F. P loader is tracked") if git_tracked(
    "scripts/load_local_mock_fixture_preview_v0_8_1.py"
) else xx("F. P loader is tracked")

print("[G] Q validation doc/script exist and are tracked")
ok("G. Q validation doc exists") if Q_DOC_PATH.exists() else xx("G. Q validation doc exists")
ok("G. Q validation doc is tracked") if git_tracked(
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_VALIDATION_PLAN_V0_8_1_Q.md"
) else xx("G. Q validation doc is tracked")
ok("G. Q readiness script exists") if Q_SCRIPT_PATH.exists() else xx("G. Q readiness script exists")
ok("G. Q readiness script is tracked") if git_tracked(
    "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_validation_plan_v0_8_1_q.py"
) else xx("G. Q readiness script is tracked")

# ---------------------------------------------------------------------------
# [H] current HEAD contains the expected base commit in git history
# ---------------------------------------------------------------------------
print("[H] git history contains expected base commit")
anc = subprocess.run(
    ["git", "-C", str(REPO_ROOT), "merge-base", "--is-ancestor", EXPECTED_BASE_HEAD, "HEAD"],
    capture_output=True,
    text=True,
)
ok(f"H. HEAD history contains {EXPECTED_BASE_HEAD}") if anc.returncode == 0 else xx(
    f"H. HEAD history contains {EXPECTED_BASE_HEAD}"
)

# ---------------------------------------------------------------------------
# P loader static source inspection ([I],[J],[K],[L],[M],[N],[AF],[AG])
# ---------------------------------------------------------------------------
loader_src = P_LOADER_PATH.read_text(encoding="utf-8")

print("[I] P loader has no __main__ block")
ok("I. P loader has no __main__ block") if "__main__" not in loader_src else xx(
    "I. P loader has no __main__ block"
)

print("[J] P loader has no CLI entrypoint")
no_cli = ("if __name__" not in loader_src) and ("__main__" not in loader_src)
ok("J. P loader has no CLI entrypoint") if no_cli else xx("J. P loader has no CLI entrypoint")

tree = ast.parse(loader_src)
import_roots: set[str] = set()
for node in ast.walk(tree):
    if isinstance(node, ast.Import):
        for alias in node.names:
            import_roots.add(alias.name.split(".")[0])
    elif isinstance(node, ast.ImportFrom):
        if node.module:
            import_roots.add(node.module.split(".")[0])

name_tokens: set[str] = set()
for tok in tokenize.generate_tokens(io.StringIO(loader_src).readline):
    if tok.type == tokenize.NAME:
        name_tokens.add(tok.string)

print("[K] P loader imports only allowed standard-library modules")
disallowed_imports = sorted(import_roots - ALLOWED_IMPORT_ROOTS)
ok("K. P loader imports only allowed standard-library modules") if not disallowed_imports else xx(
    f"K. P loader imports only allowed standard-library modules（found {disallowed_imports}）"
)

print("[L] P loader source has no forbidden code identifiers")
forbidden_hits = sorted((import_roots | name_tokens) & FORBIDDEN_IDENTIFIERS)
ok("L. P loader has no forbidden code identifiers") if not forbidden_hits else xx(
    f"L. P loader has no forbidden code identifiers（found {forbidden_hits}）"
)

print("[M] P loader contains exact fixture path")
ok("M. P loader contains exact fixture path") if (
    "fixtures/local_mock_data/hermes_openclaw_local_mock_messages_v0_8_1.json" in loader_src
) else xx("M. P loader contains exact fixture path")

print("[N] P loader contains exact M validation script path")
ok("N. P loader contains exact M validation script path") if (
    "scripts/check_hermes_openclaw_local_mock_data_fixture_json_artifact_validation_v0_8_1_m.py"
    in loader_src
) else xx("N. P loader contains exact M validation script path")

# ---------------------------------------------------------------------------
# Import-based loader self-test ([O],[P],[Q]-[AB])
# ---------------------------------------------------------------------------
print("[O-AB] import-based loader self-test")
spec = importlib.util.spec_from_file_location("p_loader_v0_8_1_r", P_LOADER_PATH)
mod = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(mod)
    loaded_ok = True
except Exception as exc:  # noqa: BLE001
    loaded_ok = False
    xx(f"loader module import failed（{exc}）")

preview: dict[str, Any] | None = None
if loaded_ok:
    ok("O. P loader exposes load_local_mock_fixture_preview") if hasattr(
        mod, "load_local_mock_fixture_preview"
    ) else xx("O. P loader exposes load_local_mock_fixture_preview")
    ok("P. P loader exposes validate_local_mock_fixture_preview_object") if hasattr(
        mod, "validate_local_mock_fixture_preview_object"
    ) else xx("P. P loader exposes validate_local_mock_fixture_preview_object")

    try:
        preview = mod.load_local_mock_fixture_preview()
        ok("Q. import-based loader self-test passes")
    except Exception as exc:  # noqa: BLE001
        xx(f"Q. import-based loader self-test passes（{exc}）")

    if isinstance(preview, dict):
        ok("R. output source = local_mock_fixture") if preview.get(
            "source"
        ) == "local_mock_fixture" else xx("R. output source = local_mock_fixture")
        ok("S. output schema_version = v0.8.1-local-mock-1") if preview.get(
            "schema_version"
        ) == EXPECTED_SCHEMA_VERSION else xx("S. output schema_version = v0.8.1-local-mock-1")
        ok("T. output is_mock = true") if preview.get("is_mock") is True else xx(
            "T. output is_mock = true"
        )
        ok("U. output local_only = true") if preview.get("local_only") is True else xx(
            "U. output local_only = true"
        )
        ok("V. output read_only = true") if preview.get("read_only") is True else xx(
            "V. output read_only = true"
        )
        recs = preview.get("records")
        ok("W. output records list length 6") if isinstance(recs, list) and len(
            recs
        ) == EXPECTED_RECORD_COUNT else xx("W. output records list length 6")
        ok("X. output runtime_badges exact") if preview.get(
            "runtime_badges"
        ) == EXPECTED_RUNTIME_BADGES else xx("X. output runtime_badges exact")
        ok("Y. output execution_permission = false") if preview.get(
            "execution_permission"
        ) is False else xx("Y. output execution_permission = false")
        ok("Z. output dispatch_permission = false") if preview.get(
            "dispatch_permission"
        ) is False else xx("Z. output dispatch_permission = false")
        ok("AA. output external_side_effects_permission = false") if preview.get(
            "external_side_effects_permission"
        ) is False else xx("AA. output external_side_effects_permission = false")
        try:
            mod.validate_local_mock_fixture_preview_object(preview)
            ok("AB. output validates with validate_local_mock_fixture_preview_object")
        except Exception as exc:  # noqa: BLE001
            xx(f"AB. output validates with validate_local_mock_fixture_preview_object（{exc}）")
    else:
        for label in [
            "R. output source = local_mock_fixture",
            "S. output schema_version = v0.8.1-local-mock-1",
            "T. output is_mock = true",
            "U. output local_only = true",
            "V. output read_only = true",
            "W. output records list length 6",
            "X. output runtime_badges exact",
            "Y. output execution_permission = false",
            "Z. output dispatch_permission = false",
            "AA. output external_side_effects_permission = false",
            "AB. output validates with validate_local_mock_fixture_preview_object",
        ]:
            xx(label)

# ---------------------------------------------------------------------------
# [AC] L fixture JSON still parses and has unchanged safety invariants
# ---------------------------------------------------------------------------
print("[AC] L fixture JSON invariants unchanged")
fixture: Any = None
try:
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    inv = fixture.get("safety_invariants", {}) if isinstance(fixture, dict) else {}
    inv = inv if isinstance(inv, dict) else {}
    ac_ok = (
        isinstance(fixture, dict)
        and fixture.get("schema_version") == EXPECTED_SCHEMA_VERSION
        and fixture.get("is_mock") is True
        and isinstance(fixture.get("records"), list)
        and len(fixture["records"]) == EXPECTED_RECORD_COUNT
        and inv.get("execution_permission") is False
        and inv.get("dispatch_permission") is False
        and inv.get("external_side_effects_permission") is False
    )
    ok("AC. L fixture JSON parses with unchanged safety invariants") if ac_ok else xx(
        "AC. L fixture JSON parses with unchanged safety invariants"
    )
except Exception as exc:  # noqa: BLE001
    xx(f"AC. L fixture JSON parses with unchanged safety invariants（{exc}）")

# ---------------------------------------------------------------------------
# [AD] output records equals fixture records
# [AE] output records object is not the same object as fixture records (deep copy)
# ---------------------------------------------------------------------------
print("[AD/AE] output records deep-copy semantics")
if isinstance(preview, dict) and isinstance(fixture, dict):
    fixture_records = fixture.get("records")
    preview_records = preview.get("records")
    ok("AD. output records equals fixture records") if preview_records == fixture_records else xx(
        "AD. output records equals fixture records"
    )
    ok("AE. output records is not the same object as fixture records") if (
        preview_records is not fixture_records
    ) else xx("AE. output records is not the same object as fixture records")
else:
    xx("AD. output records equals fixture records")
    xx("AE. output records is not the same object as fixture records")

# ---------------------------------------------------------------------------
# [AF] loader source contains copy.deepcopy
# ---------------------------------------------------------------------------
print("[AF] loader source uses copy.deepcopy")
ok("AF. loader source contains copy.deepcopy") if "copy.deepcopy" in loader_src else xx(
    "AF. loader source contains copy.deepcopy"
)

# ---------------------------------------------------------------------------
# [AG] loader source has no raw file-write code identifiers
# ---------------------------------------------------------------------------
print("[AG] loader source has no file-write code identifiers")
write_hits = sorted(name_tokens & FILE_WRITE_IDENTIFIERS)
ok("AG. loader source has no file-write code identifiers") if not write_hits else xx(
    f"AG. loader source has no file-write code identifiers（found {write_hits}）"
)

# ---------------------------------------------------------------------------
# [AH] no tracked working-tree modifications
# ---------------------------------------------------------------------------
print("[AH] no tracked working-tree modifications")
diff_out = subprocess.run(
    ["git", "-C", str(REPO_ROOT), "diff", "--name-only"],
    capture_output=True,
    text=True,
)
tracked_changes = [l for l in diff_out.stdout.splitlines() if l.strip()]
ok("AH. no tracked working-tree modifications") if not tracked_changes else xx(
    f"AH. no tracked working-tree modifications（found {tracked_changes}）"
)

# ---------------------------------------------------------------------------
# [AI] no extra untracked files beyond allowed R file and existing patches/
# ---------------------------------------------------------------------------
print("[AI] no extra untracked files beyond allowed R file and patches/")
others_out = subprocess.run(
    ["git", "-C", str(REPO_ROOT), "ls-files", "--others", "--exclude-standard"],
    capture_output=True,
    text=True,
)
ALLOWED_UNTRACKED = {
    "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_runtime_check_v0_8_1_r.py",
}
untracked = [l for l in others_out.stdout.splitlines() if l.strip()]
unexpected = [
    u for u in untracked if u not in ALLOWED_UNTRACKED and not u.startswith("patches/")
]
ok("AI. no unexpected untracked files") if not unexpected else xx(
    f"AI. no unexpected untracked files（found {unexpected}）"
)

# ---------------------------------------------------------------------------
# 結果
# ---------------------------------------------------------------------------
total = len(PASS) + len(FAIL)
print(f"\n合計：{len(PASS)}/{total} 通過")
if FAIL:
    print(f"\nXX v0.8.1-R runtime check 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print("PASS: v0.8.1-R local mock fixture read-only loader runtime check")
    sys.exit(0)
