"""v0.8.1-Q readiness check: Local Mock Fixture Read-only Loader Validation Plan (validation plan-only).

Pure local filesystem validation. This script reads only the v0.8.1-Q validation plan doc, the
v0.8.1-P loader, the v0.8.1-L fixture JSON, and the v0.8.1-M/N/O docs/scripts. It imports the P
loader (via importlib, from its file path) for an import-based self-test. It uses `git` read-only
(ls-files / diff / status) to confirm tracked status and that no extra repo files exist; it never
modifies the git index.

The loader source is inspected with `ast` (imports) and `tokenize` (identifier tokens) so that the
loader's own safety-documentation docstring — which legitimately mentions words like "POST", ".env",
"QueueStore" as prose — is not mis-flagged. Only real imports and real code identifiers are checked
against the forbidden sets.

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

Q_DOC_PATH = REPO_ROOT / "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_VALIDATION_PLAN_V0_8_1_Q.md"
Q_SCRIPT_PATH = REPO_ROOT / "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_validation_plan_v0_8_1_q.py"

FIXTURE_PATH = REPO_ROOT / "fixtures/local_mock_data/hermes_openclaw_local_mock_messages_v0_8_1.json"
P_LOADER_PATH = REPO_ROOT / "scripts/load_local_mock_fixture_preview_v0_8_1.py"

M_DOC_PATH = REPO_ROOT / "docs/HERMES_OPENCLAW_LOCAL_MOCK_DATA_FIXTURE_JSON_ARTIFACT_VALIDATION_V0_8_1_M.md"
M_SCRIPT_PATH = REPO_ROOT / "scripts/check_hermes_openclaw_local_mock_data_fixture_json_artifact_validation_v0_8_1_m.py"

N_DOC_PATH = REPO_ROOT / "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_PLAN_V0_8_1_N.md"
N_SCRIPT_PATH = REPO_ROOT / "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_plan_v0_8_1_n.py"

O_DOC_PATH = REPO_ROOT / "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_IMPLEMENTATION_AUTHORIZATION_PLAN_V0_8_1_O.md"
O_SCRIPT_PATH = REPO_ROOT / "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_implementation_authorization_plan_v0_8_1_o.py"

EXPECTED_HEAD = "d44922f81c77195429c11e2e1d2836a8f80a3bc0"
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

# Real code identifiers (import roots and NAME tokens) that must never appear in the loader.
# subprocess is intentionally NOT here: the loader legitimately uses subprocess.run to invoke the
# tracked v0.8.1-M validation script.
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

REQUIRED_DOC_PHRASES = [
    "v0.8.1-Q",
    "Local Mock Fixture Read-only Loader Validation Plan",
    "validation plan-only",
    "HEAD = origin/master = d44922f81c77195429c11e2e1d2836a8f80a3bc0",
    "scripts/load_local_mock_fixture_preview_v0_8_1.py",
    "v0.8.1-Q does not modify loader.",
    "v0.8.1-Q does not modify Dashboard.",
    "v0.8.1-Q does not read real queue DB.",
    "v0.8.1-Q does not send POST.",
    "v0.8.1-Q does not start Worker.",
    "v0.8.1-Q does not connect OpenClaw.",
    "v0.8.1-Q does not activate Hermes.",
    "v0.8.1-Q does not read Google Sheets.",
    "v0.8.1-Q does not write Google Sheets.",
    "v0.8.1-Q does not read secrets.",
    "Validation targets, plan-only:",
    "Validation method, plan-only:",
    "Known pre-commit coupling:",
    "v0.8.1-Q acceptance criteria:",
    "v0.8.1-R must not start unless separately approved by Owner.",
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
# [A/B] Q validation plan doc + readiness script exist
# ---------------------------------------------------------------------------
print("[A] Q validation plan doc exists")
ok("A. Q validation plan doc exists") if Q_DOC_PATH.exists() else xx("A. Q validation plan doc exists")
if not Q_DOC_PATH.exists():
    print("\nXX Q validation plan doc 不存在，無法繼續")
    sys.exit(1)

print("[B] Q readiness script path is correct")
ok("B. Q readiness script exists at expected path") if Q_SCRIPT_PATH.exists() else xx(
    "B. Q readiness script exists at expected path"
)

doc = Q_DOC_PATH.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# [C-G] L/M/N/O/P artifacts exist and are tracked
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

# ---------------------------------------------------------------------------
# [H] current master SHA present in Q doc
# ---------------------------------------------------------------------------
print("[H] Q doc contains current master SHA")
ok(f"H. Q doc contains current master SHA {EXPECTED_HEAD}") if EXPECTED_HEAD in doc else xx(
    f"H. Q doc contains current master SHA {EXPECTED_HEAD}"
)

# ---------------------------------------------------------------------------
# [I-S] required doc phrases
# ---------------------------------------------------------------------------
print("[I-S] required doc phrases")
for phrase in REQUIRED_DOC_PHRASES:
    ok(f"doc contains「{phrase}」") if phrase in doc else xx(f"doc contains「{phrase}」")

# ---------------------------------------------------------------------------
# P loader static source inspection ([T],[U],[V],[W],[X],[Y])
# ---------------------------------------------------------------------------
loader_src = P_LOADER_PATH.read_text(encoding="utf-8")

print("[T] P loader has no __main__ block")
ok("T. P loader has no __main__ block") if "__main__" not in loader_src else xx(
    "T. P loader has no __main__ block"
)

print("[U] P loader has no CLI entrypoint")
no_cli = ("if __name__" not in loader_src) and ("__main__" not in loader_src)
ok("U. P loader has no CLI entrypoint") if no_cli else xx("U. P loader has no CLI entrypoint")

# Parse imports (AST) and identifier NAME tokens (tokenize, strings/comments excluded).
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

print("[V] P loader imports only allowed standard-library modules")
disallowed_imports = sorted(import_roots - ALLOWED_IMPORT_ROOTS)
ok("V. P loader imports only allowed standard-library modules") if not disallowed_imports else xx(
    f"V. P loader imports only allowed standard-library modules（found {disallowed_imports}）"
)

print("[W] P loader source has no forbidden imports/identifiers")
forbidden_hits = sorted((import_roots | name_tokens) & FORBIDDEN_IDENTIFIERS)
ok("W. P loader has no forbidden imports/identifiers") if not forbidden_hits else xx(
    f"W. P loader has no forbidden imports/identifiers（found {forbidden_hits}）"
)

print("[X] P loader contains exact fixture path")
ok("X. P loader contains exact fixture path") if (
    "fixtures/local_mock_data/hermes_openclaw_local_mock_messages_v0_8_1.json" in loader_src
) else xx("X. P loader contains exact fixture path")

print("[Y] P loader contains exact M validation script path")
ok("Y. P loader contains exact M validation script path") if (
    "scripts/check_hermes_openclaw_local_mock_data_fixture_json_artifact_validation_v0_8_1_m.py"
    in loader_src
) else xx("Y. P loader contains exact M validation script path")

# ---------------------------------------------------------------------------
# Import-based loader self-test ([Z],[AA],[AB]-[AL])
# ---------------------------------------------------------------------------
print("[Z-AL] import-based loader self-test")
spec = importlib.util.spec_from_file_location("p_loader_v0_8_1", P_LOADER_PATH)
mod = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(mod)
    loaded_ok = True
except Exception as exc:  # noqa: BLE001 - report any import failure as a check failure
    loaded_ok = False
    xx(f"loader module import failed（{exc}）")

if loaded_ok:
    ok("Z. P loader exposes load_local_mock_fixture_preview") if hasattr(
        mod, "load_local_mock_fixture_preview"
    ) else xx("Z. P loader exposes load_local_mock_fixture_preview")
    ok("AA. P loader exposes validate_local_mock_fixture_preview_object") if hasattr(
        mod, "validate_local_mock_fixture_preview_object"
    ) else xx("AA. P loader exposes validate_local_mock_fixture_preview_object")

    preview: dict[str, Any] | None = None
    try:
        preview = mod.load_local_mock_fixture_preview()
        mod.validate_local_mock_fixture_preview_object(preview)
        ok("AB. import-based loader self-test passes")
    except Exception as exc:  # noqa: BLE001
        xx(f"AB. import-based loader self-test passes（{exc}）")

    if isinstance(preview, dict):
        ok("AC. output source = local_mock_fixture") if preview.get(
            "source"
        ) == "local_mock_fixture" else xx("AC. output source = local_mock_fixture")
        ok("AD. output schema_version = v0.8.1-local-mock-1") if preview.get(
            "schema_version"
        ) == EXPECTED_SCHEMA_VERSION else xx("AD. output schema_version = v0.8.1-local-mock-1")
        ok("AE. output is_mock = true") if preview.get("is_mock") is True else xx(
            "AE. output is_mock = true"
        )
        ok("AF. output local_only = true") if preview.get("local_only") is True else xx(
            "AF. output local_only = true"
        )
        ok("AG. output read_only = true") if preview.get("read_only") is True else xx(
            "AG. output read_only = true"
        )
        recs = preview.get("records")
        ok("AH. output records list length 6") if isinstance(recs, list) and len(
            recs
        ) == EXPECTED_RECORD_COUNT else xx("AH. output records list length 6")
        ok("AI. output runtime_badges exact") if preview.get(
            "runtime_badges"
        ) == EXPECTED_RUNTIME_BADGES else xx("AI. output runtime_badges exact")
        ok("AJ. output execution_permission = false") if preview.get(
            "execution_permission"
        ) is False else xx("AJ. output execution_permission = false")
        ok("AK. output dispatch_permission = false") if preview.get(
            "dispatch_permission"
        ) is False else xx("AK. output dispatch_permission = false")
        ok("AL. output external_side_effects_permission = false") if preview.get(
            "external_side_effects_permission"
        ) is False else xx("AL. output external_side_effects_permission = false")
    else:
        for label in [
            "AC. output source = local_mock_fixture",
            "AD. output schema_version = v0.8.1-local-mock-1",
            "AE. output is_mock = true",
            "AF. output local_only = true",
            "AG. output read_only = true",
            "AH. output records list length 6",
            "AI. output runtime_badges exact",
            "AJ. output execution_permission = false",
            "AK. output dispatch_permission = false",
            "AL. output external_side_effects_permission = false",
        ]:
            xx(label)

# ---------------------------------------------------------------------------
# [AM] L fixture JSON still parses and has same safety invariants
# ---------------------------------------------------------------------------
print("[AM] L fixture JSON invariants unchanged")
try:
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    inv = fixture.get("safety_invariants", {}) if isinstance(fixture, dict) else {}
    inv = inv if isinstance(inv, dict) else {}
    am_ok = (
        isinstance(fixture, dict)
        and fixture.get("schema_version") == EXPECTED_SCHEMA_VERSION
        and fixture.get("is_mock") is True
        and isinstance(fixture.get("records"), list)
        and len(fixture["records"]) == EXPECTED_RECORD_COUNT
        and inv.get("execution_permission") is False
        and inv.get("dispatch_permission") is False
        and inv.get("external_side_effects_permission") is False
    )
    ok("AM. L fixture JSON parses with unchanged safety invariants") if am_ok else xx(
        "AM. L fixture JSON parses with unchanged safety invariants"
    )
except Exception as exc:  # noqa: BLE001
    xx(f"AM. L fixture JSON parses with unchanged safety invariants（{exc}）")

# ---------------------------------------------------------------------------
# [AN] no tracked working-tree modifications
# ---------------------------------------------------------------------------
print("[AN] no tracked working-tree modifications")
diff_out = subprocess.run(
    ["git", "-C", str(REPO_ROOT), "diff", "--name-only"],
    capture_output=True,
    text=True,
)
tracked_changes = [l for l in diff_out.stdout.splitlines() if l.strip()]
ok("AN. no tracked working-tree modifications") if not tracked_changes else xx(
    f"AN. no tracked working-tree modifications（found {tracked_changes}）"
)

# ---------------------------------------------------------------------------
# [AO] no extra untracked files beyond allowed Q files and existing patches/
# ---------------------------------------------------------------------------
print("[AO] no extra untracked files beyond allowed Q files and patches/")
others_out = subprocess.run(
    ["git", "-C", str(REPO_ROOT), "ls-files", "--others", "--exclude-standard"],
    capture_output=True,
    text=True,
)
ALLOWED_UNTRACKED = {
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_VALIDATION_PLAN_V0_8_1_Q.md",
    "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_validation_plan_v0_8_1_q.py",
}
untracked = [l for l in others_out.stdout.splitlines() if l.strip()]
unexpected = [
    u for u in untracked if u not in ALLOWED_UNTRACKED and not u.startswith("patches/")
]
ok("AO. no unexpected untracked files") if not unexpected else xx(
    f"AO. no unexpected untracked files（found {unexpected}）"
)

# ---------------------------------------------------------------------------
# 結果
# ---------------------------------------------------------------------------
total = len(PASS) + len(FAIL)
print(f"\n合計：{len(PASS)}/{total} 通過")
if FAIL:
    print(f"\nXX v0.8.1-Q readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print("PASS: v0.8.1-Q local mock fixture read-only loader validation plan")
    sys.exit(0)
