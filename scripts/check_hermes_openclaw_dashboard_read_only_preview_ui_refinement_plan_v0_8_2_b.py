"""v0.8.2-B readiness check: Dashboard Read-only Preview UI Refinement Plan (plan-only).

Pure local filesystem + git metadata validation. This script reads only the v0.8.2-B plan doc and
confirms the tracked state of the v0.8.2-A validation script and the app/main.py / templates/system.html
/ static/dashboard.css surfaces it plans over. It uses `git` read-only (ls-files / diff / status /
merge-base) to confirm tracked status, ancestry, and that no extra repo files exist; it never modifies
the git index.

It does NOT import app runtime, Dashboard runtime, QueueStore, Worker/OpenClaw/Hermes/Google Sheets
integration, the v0.8.1-P loader, or the v0.8.1-V adapter; it never starts a server; it reads no real
queue DB, sends no POST, makes no network call, reads no secrets, writes no repo file, and modifies no
adapter/loader/Dashboard file.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

B_DOC_PATH = REPO_ROOT / "docs/HERMES_OPENCLAW_DASHBOARD_READ_ONLY_PREVIEW_UI_REFINEMENT_PLAN_V0_8_2_B.md"
B_SCRIPT_PATH = REPO_ROOT / "scripts/check_hermes_openclaw_dashboard_read_only_preview_ui_refinement_plan_v0_8_2_b.py"

V082A_SCRIPT_PATH = REPO_ROOT / "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_read_only_display_integration_v0_8_2_a.py"
MAIN_PY_PATH = REPO_ROOT / "app/main.py"
SYSTEM_HTML_PATH = REPO_ROOT / "templates/system.html"
DASHBOARD_CSS_PATH = REPO_ROOT / "static/dashboard.css"

EXPECTED_BASE_HEAD = "7206afa7ed000fbaab761a1f0018524849cc8815"

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


def check(label: str, condition: bool) -> None:
    ok(label) if condition else xx(label)


def run_git(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args],
        capture_output=True,
        text=True,
    )


def git_tracked(rel: str) -> bool:
    out = run_git(["ls-files", "--", rel])
    return out.returncode == 0 and out.stdout.strip() != ""


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
# [B-E] v0.8.2-A validation script / app/main.py / templates/system.html /
#       static/dashboard.css exist and are tracked
# ---------------------------------------------------------------------------
print("[B] v0.8.2-A validation script exists and is tracked")
check("B. v0.8.2-A validation script exists", V082A_SCRIPT_PATH.exists())
check(
    "B. v0.8.2-A validation script is tracked",
    git_tracked(
        "scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_read_only_display_integration_v0_8_2_a.py"
    ),
)

print("[C] app/main.py exists and is tracked")
check("C. app/main.py exists", MAIN_PY_PATH.exists())
check("C. app/main.py is tracked", git_tracked("app/main.py"))

print("[D] templates/system.html exists and is tracked")
check("D. templates/system.html exists", SYSTEM_HTML_PATH.exists())
check("D. templates/system.html is tracked", git_tracked("templates/system.html"))

print("[E] static/dashboard.css exists and is tracked")
check("E. static/dashboard.css exists", DASHBOARD_CSS_PATH.exists())
check("E. static/dashboard.css is tracked", git_tracked("static/dashboard.css"))

# ---------------------------------------------------------------------------
# [F/G] B doc + readiness script exist
# ---------------------------------------------------------------------------
print("[F] B doc exists")
check("F. B doc exists", B_DOC_PATH.exists())
if not B_DOC_PATH.exists():
    print("\nXX B plan doc 不存在，無法繼續")
    sys.exit(1)

print("[G] B readiness script exists")
check("G. B readiness script exists at expected path", B_SCRIPT_PATH.exists())

doc = B_DOC_PATH.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# [H-AB] required doc content
# ---------------------------------------------------------------------------
print("[H] B doc contains v0.8.2-B title")
check(
    "H. B doc contains v0.8.2-B title",
    "v0.8.2-B" in doc and "Dashboard Read-only Preview UI Refinement Plan" in doc,
)

print("[I] B doc states plan-only")
check("I. B doc states plan-only", "v0.8.2-B is a plan-only round." in doc)

print("[J] B doc states it does not modify Dashboard implementation")
check(
    "J. B doc states it does not modify Dashboard implementation",
    "v0.8.2-B does not modify Dashboard implementation." in doc,
)

print("[K] B doc states it does not modify app/main.py/templates/system.html/static/dashboard.css")
check(
    "K. B doc states it does not modify app/main.py/templates/system.html/static/dashboard.css",
    "v0.8.2-B does not modify app/main.py." in doc
    and "v0.8.2-B does not modify templates/system.html." in doc
    and "v0.8.2-B does not modify static/dashboard.css." in doc,
)

print("[L] B doc states it only plans future UI refinement")
check(
    "L. B doc states it only plans future UI refinement",
    "v0.8.2-B only plans future Dashboard read-only preview UI refinement." in doc,
)

print("[M] B doc contains base HEAD")
check("M. B doc contains base HEAD", f"Base HEAD / origin/master:\n{EXPECTED_BASE_HEAD}" in doc)

print("[N] B doc mentions v0.8.2-A completed GET-only /dashboard/system read-only display")
check(
    "N. B doc mentions v0.8.2-A completed GET-only /dashboard/system read-only display",
    "v0.8.2-A added a read-only Dashboard preview display to the existing GET-only /dashboard/system surface."
    in doc,
)

print("[O] B doc says Dashboard consumes build_dashboard_preview_model()")
check(
    "O. B doc says Dashboard consumes build_dashboard_preview_model()",
    "Dashboard consumes build_dashboard_preview_model()." in doc,
)

print("[P] B doc says Dashboard does not call P loader")
check("P. B doc says Dashboard does not call P loader", "Dashboard does not call P loader." in doc)

print("[Q] B doc says Dashboard does not read fixture JSON directly")
check(
    "Q. B doc says Dashboard does not read fixture JSON directly",
    "Dashboard does not read fixture JSON directly." in doc,
)

print("[R] B doc says v0.8.2-A validation passes 30/30")
check(
    "R. B doc says v0.8.2-A validation passes 30/30",
    "v0.8.2-A validation passes 30/30 after the post-commit-aware follow-up fix." in doc,
)

print("[S] B doc contains read-only display contract")
check(
    "S. B doc contains read-only display contract",
    "## 4. Current read-only display contract" in doc
    and "The Dashboard preview display must remain GET-only." in doc,
)

print("[T] B doc contains all disabled runtime badges")
REQUIRED_BADGES = [
    "DISPATCH OFF",
    "WORKER OFF",
    "OPENCLAW NOT CONNECTED",
    "HERMES NOT CONNECTED",
    "GOOGLE SHEETS DISABLED",
]
check(
    "T. B doc contains all disabled runtime badges",
    all(b in doc for b in REQUIRED_BADGES),
)

print("[U] B doc contains future UI refinement categories")
check(
    "U. B doc contains future UI refinement categories",
    "## 6. Future UI refinement categories, plan-only" in doc
    and "1. Badge layout refinement" in doc
    and "10. Accessibility and semantic markup" in doc,
)

print("[V] B doc contains future candidate files")
check(
    "V. B doc contains future candidate files",
    "## 8. Future candidate files, plan-only" in doc
    and "Future candidate display file:\n- templates/system.html" in doc
    and "Future candidate style file:\n- static/dashboard.css" in doc,
)

print("[W] B doc says candidate files are not modified by v0.8.2-B")
check(
    "W. B doc says candidate files are not modified by v0.8.2-B",
    "These candidate files are not modified by v0.8.2-B." in doc,
)

print("[X] B doc contains forbidden UI controls")
check(
    "X. B doc contains forbidden UI controls",
    "## 9. Future forbidden UI controls, plan-only" in doc
    and "No Run button." in doc
    and "No dispatch_url." in doc,
)

print("[Y] B doc contains future validation requirements")
check(
    "Y. B doc contains future validation requirements",
    "## 10. Future validation requirements, plan-only" in doc
    and "Future UI refinement validation must confirm:" in doc,
)

print("[Z] B doc contains rollback boundary")
check(
    "Z. B doc contains rollback boundary",
    "## 11. Future rollback boundary, plan-only" in doc
    and "Rollback of future UI refinement must remove only the future UI refinement changes." in doc,
)

print("[AA] B doc contains exact v0.8.2-C authorization phrase")
EXACT_V082C_PHRASE = (
    "批准實作 v0.8.2-C — Dashboard Read-only Preview UI Refinement Implementation，"
    "僅允許改善 v0.8.2-A 已存在的 /dashboard/system read-only preview display 的版面、"
    "標籤、說明文字、表格可讀性與 CSS 樣式；必須保持 GET-only、read-only、synthetic local-only、"
    "permission flags false、disabled runtime badges visible；"
    "不得修改資料來源，不得呼叫 P loader，不得直接讀 fixture JSON，不得讀 real queue DB，不得 POST，"
    "不得新增 button/form/action URL/webhook/endpoint/execute/dispatch/send controls，"
    "不得啟 Worker/OpenClaw/Hermes/Google Sheets，不得讀 secrets，"
    "不得建立 production/shared DB 或 Remote Blackboard API runtime。"
)
check(
    "AA. B doc contains exact v0.8.2-C authorization phrase",
    doc.count(EXACT_V082C_PHRASE) == 1,
)

print("[AB] B doc says v0.8.2-C is not started")
check("AB. B doc says v0.8.2-C is not started", "v0.8.2-C is not started by v0.8.2-B." in doc)

# ---------------------------------------------------------------------------
# [AC] no tracked working-tree modifications
# ---------------------------------------------------------------------------
print("[AC] no tracked working-tree modifications")
diff_out = run_git(["diff", "--name-only"])
tracked_changes = [l for l in diff_out.stdout.splitlines() if l.strip()]
check(
    f"AC. no tracked working-tree modifications（found {tracked_changes}）"
    if tracked_changes
    else "AC. no tracked working-tree modifications",
    not tracked_changes,
)

# ---------------------------------------------------------------------------
# [AD] no app/templates/static files modified
# ---------------------------------------------------------------------------
print("[AD] no app/templates/static files modified")
status_out = run_git(["status", "--porcelain"])
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
check(
    f"AD. no app/templates/static files modified（found {dashboard_changes}）"
    if dashboard_changes
    else "AD. no app/templates/static files modified",
    not dashboard_changes,
)

# ---------------------------------------------------------------------------
# [AE] no extra untracked files beyond B doc/script and patches/
# ---------------------------------------------------------------------------
print("[AE] no extra untracked files beyond B doc/script and patches/")
others_out = run_git(["ls-files", "--others", "--exclude-standard"])
ALLOWED_UNTRACKED = {
    "docs/HERMES_OPENCLAW_DASHBOARD_READ_ONLY_PREVIEW_UI_REFINEMENT_PLAN_V0_8_2_B.md",
    "scripts/check_hermes_openclaw_dashboard_read_only_preview_ui_refinement_plan_v0_8_2_b.py",
}
untracked = [l for l in others_out.stdout.splitlines() if l.strip()]
unexpected = [u for u in untracked if u not in ALLOWED_UNTRACKED and not u.startswith("patches/")]
check(
    f"AE. no unexpected untracked files（found {unexpected}）" if unexpected else "AE. no unexpected untracked files",
    not unexpected,
)

# ---------------------------------------------------------------------------
# 結果
# ---------------------------------------------------------------------------
total = len(PASS) + len(FAIL)
print(f"\n合計：{len(PASS)}/{total} 通過")
if FAIL:
    print(f"\nXX v0.8.2-B readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print("PASS: v0.8.2-B dashboard read-only preview UI refinement plan")
    sys.exit(0)
