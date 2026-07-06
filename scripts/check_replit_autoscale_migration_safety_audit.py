"""
Readiness check for Replit Autoscale Migration Safety Audit.

Rules:
- Does not read secrets.
- Does not call network.
- Does not call Replit API.
- Does not modify runtime files.
- Outputs PASS or FAIL with a clear summary.
"""

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
AUDIT_DOC = REPO_ROOT / "docs" / "REPLIT_AUTOSCALE_MIGRATION_SAFETY_AUDIT.md"
READINESS_SCRIPT = REPO_ROOT / "scripts" / "check_replit_autoscale_migration_safety_audit.py"

FORBIDDEN_RUNTIME_FILES = [
    "app/main.py",
    "templates/system.html",
    "static/dashboard.css",
    "CLAUDE.md",
    ".replit",
    "pyproject.toml",
    "requirements.txt",
    "Procfile",
]

REQUIRED_SAFETY_SENTENCES = [
    "Reserved VM shutdown is not runtime feature change.",
    "Autoscale migration is not Hermes activation.",
    "Autoscale migration is not OpenClaw activation.",
    "Autoscale migration is not Worker execution.",
    "Autoscale migration is not connector activation.",
    "Dashboard publish is not execution permission.",
    "Dashboard publish is not Blackboard write.",
    "Dashboard publish is not queue write.",
    "Dashboard publish is not audit trail write.",
    "Replit remains a remote observation dashboard.",
    "External side effects remain forbidden by default.",
]

failures = []
passes = []


def check(label, ok, detail=""):
    if ok:
        passes.append(f"  PASS  {label}")
    else:
        failures.append(f"  FAIL  {label}" + (f": {detail}" if detail else ""))


# 1. Audit doc exists.
check("audit doc exists", AUDIT_DOC.exists(), str(AUDIT_DOC))

# 2. Readiness script exists.
check("readiness script exists", READINESS_SCRIPT.exists(), str(READINESS_SCRIPT))

# Read doc content for subsequent checks.
doc_text = AUDIT_DOC.read_text(encoding="utf-8") if AUDIT_DOC.exists() else ""

# 3. Doc contains required safety sentences.
for sentence in REQUIRED_SAFETY_SENTENCES:
    check(f"doc contains safety sentence: {sentence[:60]!r}", sentence in doc_text)

# 4. Doc contains Reserved VM -> Autoscale migration content.
check(
    "doc contains Reserved VM -> Autoscale migration",
    "Reserved VM" in doc_text and "Autoscale" in doc_text,
)

# 5. Doc contains Replit remote observation dashboard positioning.
check(
    "doc contains Replit remote observation dashboard role",
    "Replit = remote observation dashboard" in doc_text,
)

# 6. Doc contains manual UI steps.
check(
    "doc contains manual UI steps (Open Replit Deployments)",
    "Open Replit Deployments" in doc_text,
)
check(
    "doc contains manual UI step: Verify /dashboard/system loads",
    "Verify /dashboard/system loads" in doc_text,
)

# 7. Doc contains "Stopping the editor is not enough."
check(
    "doc contains 'Stopping the editor is not enough.'",
    "Stopping the editor is not enough." in doc_text,
)

# 8. Forbidden runtime files not in staged diff (what the audit commits).
#    Pre-existing unstaged modifications (e.g. .replit modified before this audit
#    started) are reported as informational warnings, not failures.
PRE_EXISTING_UNSTAGED = {".replit"}  # confirmed present before audit start

try:
    staged_out = subprocess.run(
        ["git", "diff", "--name-only", "--cached"],
        capture_output=True, text=True, cwd=str(REPO_ROOT), check=True,
    ).stdout.strip()
    unstaged_out = subprocess.run(
        ["git", "diff", "--name-only"],
        capture_output=True, text=True, cwd=str(REPO_ROOT), check=True,
    ).stdout.strip()
    staged_set = set(staged_out.split()) if staged_out else set()
    unstaged_set = set(unstaged_out.split()) if unstaged_out else set()
    for f in FORBIDDEN_RUNTIME_FILES:
        in_staged = f in staged_set
        in_unstaged = f in unstaged_set
        if in_staged:
            check(
                f"forbidden file not in staged diff: {f}",
                False,
                "found in staged diff â audit must not commit this file",
            )
        elif in_unstaged and f not in PRE_EXISTING_UNSTAGED:
            check(
                f"forbidden file not in unstaged diff: {f}",
                False,
                "found in unstaged diff â not pre-existing, audit may have modified it",
            )
        else:
            label = (
                f"forbidden file not in staged diff: {f}"
                + (" (pre-existing unstaged change, not introduced by audit)" if in_unstaged else "")
            )
            check(label, True)
except Exception as exc:
    failures.append(f"  FAIL  could not run git diff: {exc}")

# Print results.
print("=" * 60)
print("Replit Autoscale Migration Safety Audit â Readiness Check")
print("=" * 60)
for line in passes:
    print(line)
for line in failures:
    print(line)
print("-" * 60)
if failures:
    print(f"RESULT: FAIL  ({len(failures)} failure(s), {len(passes)} pass(es))")
    sys.exit(1)
else:
    print(f"RESULT: PASS  ({len(passes)} checks passed)")
    sys.exit(0)
