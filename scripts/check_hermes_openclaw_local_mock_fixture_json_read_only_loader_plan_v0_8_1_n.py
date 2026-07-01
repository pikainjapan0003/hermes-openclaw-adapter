"""v0.8.1-N readiness check: Local Mock Fixture JSON Read-only Loader Plan (plan-only).

Pure local filesystem validation. This script reads only the v0.8.1-N plan doc, the v0.8.1-L
fixture JSON, the v0.8.1-M validation doc, and the v0.8.1-M validation script. It uses `git` in a
read-only way (ls-files / status) to confirm tracked status and that no extra repo files exist; it
never modifies the git index.

It does NOT read real queue DB, send POST, read the network, read secrets, import app runtime,
import QueueStore, start Worker/OpenClaw/Hermes/Google Sheets, write any repo file, create a loader,
or modify the Dashboard.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

N_DOC_PATH = REPO_ROOT / "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_PLAN_V0_8_1_N.md"
N_SCRIPT_PATH = REPO_ROOT / "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_plan_v0_8_1_n.py"

FIXTURE_PATH = REPO_ROOT / "fixtures/local_mock_data/hermes_openclaw_local_mock_messages_v0_8_1.json"
M_DOC_PATH = REPO_ROOT / "docs/HERMES_OPENCLAW_LOCAL_MOCK_DATA_FIXTURE_JSON_ARTIFACT_VALIDATION_V0_8_1_M.md"
M_SCRIPT_PATH = REPO_ROOT / "scripts/check_hermes_openclaw_local_mock_data_fixture_json_artifact_validation_v0_8_1_m.py"

EXPECTED_HEAD = "6db5764409cd8d4da766a2a992e572156848db2b"
EXPECTED_SCHEMA_VERSION = "v0.8.1-local-mock-1"

PASS: list[str] = []
FAIL: list[str] = []


def ok(label: str) -> None:
    PASS.append(label)
    print(f"  ok : {label}")


def xx(label: str) -> None:
    FAIL.append(label)
    print(f"  XX : {label}")


def git_tracked(rel: str) -> bool:
    """Return True if the given repo-relative path is tracked (read-only git call)."""
    out = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "ls-files", "--", rel],
        capture_output=True,
        text=True,
    )
    return out.returncode == 0 and out.stdout.strip() != ""


REQUIRED_DOC_PHRASES = [
    "v0.8.1-N",
    "Local Mock Fixture JSON Read-only Loader Plan",
    "plan-only",
    "HEAD = origin/master = 6db5764409cd8d4da766a2a992e572156848db2b",
    "fixtures/local_mock_data/hermes_openclaw_local_mock_messages_v0_8_1.json",
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_DATA_FIXTURE_JSON_ARTIFACT_VALIDATION_V0_8_1_M.md",
    "scripts/check_hermes_openclaw_local_mock_data_fixture_json_artifact_validation_v0_8_1_m.py",
    "v0.8.1-N does not create a loader.",
    "v0.8.1-N does not create a read-only loader.",
    "v0.8.1-N does not create a preview data loader.",
    "v0.8.1-N does not modify Dashboard.",
    "v0.8.1-N does not read real queue DB.",
    "v0.8.1-N does not send POST.",
    "v0.8.1-N does not start Worker.",
    "v0.8.1-N does not connect OpenClaw.",
    "v0.8.1-N does not activate Hermes.",
    "v0.8.1-N does not read Google Sheets.",
    "v0.8.1-N does not write Google Sheets.",
    "Future read-only loader contract, plan-only:",
    "Precondition:",
    "v0.8.1-M validation must pass before any loader reads the fixture.",
    "Future loader output, plan-only:",
    '"source": "local_mock_fixture"',
    '"schema_version": "v0.8.1-local-mock-1"',
    '"is_mock": true',
    '"local_only": true',
    '"read_only": true',
    '"execution_permission": false',
    '"dispatch_permission": false',
    '"external_side_effects_permission": false',
    "This output contract is plan-only.",
    "No code in v0.8.1-N returns this object.",
    "No loader in v0.8.1-N reads this fixture.",
    "No Dashboard in v0.8.1-N consumes this output.",
    "future loader implementation requires separate Owner approval",
    "v0.8.1-O must not start unless separately approved by Owner.",
]

FORBIDDEN_DONE_CLAIMS = [
    "loader implemented",
    "read-only loader implemented",
    "preview data loader created",
    "fixture loader runtime created",
    "Dashboard route created",
    "Dashboard endpoint created",
    "Dashboard template created",
    "Dashboard static asset created",
    "real queue DB read",
    "queue write enabled",
    "POST sent",
    "Worker started",
    "OpenClaw connected",
    "OpenClaw called",
    "Hermes activated",
    "Hermes connected",
    "Hermes called",
    "Google Sheets live write enabled",
    "secrets read",
    "webhook created",
    "connector created",
    "production DB created",
    "shared DB created",
    "Remote Blackboard API runtime created",
    "execution_permission = true",
    "dispatch_permission = true",
    "external_side_effects_permission = true",
    "tag created",
]

# Safe negations that literally embed a forbidden-claim substring. These are scrubbed from the doc
# before scanning FORBIDDEN_DONE_CLAIMS so benign negations are not mis-flagged.
SAFE_NEGATIONS = [
    "No real queue DB read is performed in v0.8.1-N.",
    "N clearly forbids real queue DB reads",
    "No real queue DB read.",
    "no real queue DB read",
    "No secrets read.",
    "no secrets read",
]

# Value-bearing secret patterns only (bare planning tokens are allowed).
FORBIDDEN_PATTERNS = [
    (r"spreadsheets/d/[A-Za-z0-9_-]{20,}", "real spreadsheet URL"),
    (r'"?refresh_token"?\s*[:=]\s*"[^"]+"', "refresh token value"),
    (r'"?client_secret"?\s*[:=]\s*"[^"]+"', "client secret value"),
    (r'"?private_key"?\s*[:=]\s*"[^"]+"', "private key value"),
    (r"-----BEGIN[ A-Z]*PRIVATE KEY-----", "private key block"),
    (r'"?spreadsheet_id"?\s*[:=]\s*"[A-Za-z0-9_-]{20,}"', "spreadsheet id value"),
]

# ---------------------------------------------------------------------------
# [A/B] N plan doc + readiness script exist at the correct paths
# ---------------------------------------------------------------------------
print("[A] N plan doc exists")
ok("A. N plan doc exists") if N_DOC_PATH.exists() else xx("A. N plan doc exists")
if not N_DOC_PATH.exists():
    print("\nXX N plan doc 不存在，無法繼續")
    sys.exit(1)

print("[B] N readiness script path is correct")
ok("B. N readiness script exists at expected path") if N_SCRIPT_PATH.exists() else xx(
    "B. N readiness script exists at expected path"
)

doc = N_DOC_PATH.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# [C/D/E] L fixture + M validation files exist and are tracked
# ---------------------------------------------------------------------------
print("[C] L fixture JSON exists and is tracked")
ok("C. L fixture JSON exists") if FIXTURE_PATH.exists() else xx("C. L fixture JSON exists")
ok("C. L fixture JSON is tracked") if git_tracked(
    "fixtures/local_mock_data/hermes_openclaw_local_mock_messages_v0_8_1.json"
) else xx("C. L fixture JSON is tracked")

print("[D] M validation doc exists and is tracked")
ok("D. M validation doc exists") if M_DOC_PATH.exists() else xx("D. M validation doc exists")
ok("D. M validation doc is tracked") if git_tracked(
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_DATA_FIXTURE_JSON_ARTIFACT_VALIDATION_V0_8_1_M.md"
) else xx("D. M validation doc is tracked")

print("[E] M validation script exists and is tracked")
ok("E. M validation script exists") if M_SCRIPT_PATH.exists() else xx(
    "E. M validation script exists"
)
ok("E. M validation script is tracked") if git_tracked(
    "scripts/check_hermes_openclaw_local_mock_data_fixture_json_artifact_validation_v0_8_1_m.py"
) else xx("E. M validation script is tracked")

# ---------------------------------------------------------------------------
# [F] current master SHA present in N doc
# ---------------------------------------------------------------------------
print("[F] N doc contains current master SHA")
ok(f"F. N doc contains current master SHA {EXPECTED_HEAD}") if EXPECTED_HEAD in doc else xx(
    f"F. N doc contains current master SHA {EXPECTED_HEAD}"
)

# ---------------------------------------------------------------------------
# [G-S] required doc phrases (plan-only boundary, no-loader, no-Dashboard,
#        no-real-queue-DB, no-POST, no-Worker/OpenClaw/Hermes/Sheets,
#        future input/precondition/output contract, permission flags,
#        future implementation requires separate Owner approval)
# ---------------------------------------------------------------------------
print("[G-S] required doc phrases")
for phrase in REQUIRED_DOC_PHRASES:
    ok(f"doc contains「{phrase}」") if phrase in doc else xx(f"doc contains「{phrase}」")

# ---------------------------------------------------------------------------
# [T] N doc must not contain unsafe done-claims (after scrubbing safe negations)
# ---------------------------------------------------------------------------
print("[T] N doc has no unsafe done-claims")
scrubbed = doc
for neg in SAFE_NEGATIONS:
    scrubbed = scrubbed.replace(neg, "")
for claim in FORBIDDEN_DONE_CLAIMS:
    ok(f"T. doc has no unsafe claim「{claim}」") if claim not in scrubbed else xx(
        f"T. doc must not contain「{claim}」"
    )
for pat, label in FORBIDDEN_PATTERNS:
    found = bool(re.search(pat, doc, re.IGNORECASE))
    ok(f"T. doc has no「{label}」") if not found else xx(f"T. doc must not contain「{label}」")

# ---------------------------------------------------------------------------
# [U-Y] L fixture JSON invariants still hold (read-only parse)
# ---------------------------------------------------------------------------
print("[U-Y] L fixture JSON invariants")
raw = FIXTURE_PATH.read_text(encoding="utf-8")
data: Any = None
try:
    data = json.loads(raw)
    ok("U. L fixture JSON still parses")
except json.JSONDecodeError as exc:
    xx(f"U. L fixture JSON still parses（{exc}）")

if isinstance(data, dict):
    ok("V. L fixture schema_version = v0.8.1-local-mock-1") if data.get(
        "schema_version"
    ) == EXPECTED_SCHEMA_VERSION else xx("V. L fixture schema_version = v0.8.1-local-mock-1")

    ok("W. L fixture is_mock = true") if data.get("is_mock") is True else xx(
        "W. L fixture is_mock = true"
    )

    recs = data.get("records")
    ok("X. L fixture has 6 records") if isinstance(recs, list) and len(recs) == 6 else xx(
        "X. L fixture has 6 records"
    )

    inv = data.get("safety_invariants", {})
    inv = inv if isinstance(inv, dict) else {}
    perms_ok = (
        inv.get("execution_permission") is False
        and inv.get("dispatch_permission") is False
        and inv.get("external_side_effects_permission") is False
    )
    ok("Y. L fixture safety_invariants execution/dispatch/external permissions false") if perms_ok else xx(
        "Y. L fixture safety_invariants execution/dispatch/external permissions false"
    )
else:
    xx("V. L fixture schema_version = v0.8.1-local-mock-1")
    xx("W. L fixture is_mock = true")
    xx("X. L fixture has 6 records")
    xx("Y. L fixture safety_invariants execution/dispatch/external permissions false")

# ---------------------------------------------------------------------------
# [Z] no extra repo files beyond allowed N files and existing patches/
# ---------------------------------------------------------------------------
print("[Z] no extra repo files beyond allowed N files and patches/")
# tracked working-tree modifications must be empty
diff_out = subprocess.run(
    ["git", "-C", str(REPO_ROOT), "diff", "--name-only"],
    capture_output=True,
    text=True,
)
tracked_changes = [l for l in diff_out.stdout.splitlines() if l.strip()]
ok("Z. no tracked working-tree modifications") if not tracked_changes else xx(
    f"Z. no tracked working-tree modifications（found {tracked_changes}）"
)

others_out = subprocess.run(
    ["git", "-C", str(REPO_ROOT), "ls-files", "--others", "--exclude-standard"],
    capture_output=True,
    text=True,
)
ALLOWED_UNTRACKED = {
    "docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_PLAN_V0_8_1_N.md",
    "scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_plan_v0_8_1_n.py",
}
untracked = [l for l in others_out.stdout.splitlines() if l.strip()]
unexpected = [
    u for u in untracked if u not in ALLOWED_UNTRACKED and not u.startswith("patches/")
]
ok("Z. no unexpected untracked files") if not unexpected else xx(
    f"Z. no unexpected untracked files（found {unexpected}）"
)

# ---------------------------------------------------------------------------
# 結果
# ---------------------------------------------------------------------------
total = len(PASS) + len(FAIL)
print(f"\n合計：{len(PASS)}/{total} 通過")
if FAIL:
    print(f"\nXX v0.8.1-N readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print("PASS: v0.8.1-N local mock fixture JSON read-only loader plan")
    sys.exit(0)
