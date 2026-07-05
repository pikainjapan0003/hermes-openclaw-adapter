"""v0.9-D readiness check: Dashboard Hermes Advice Panel.

Pure local filesystem + git metadata validation, standard library only. `app/main.py`,
`templates/system.html`, and `static/dashboard.css` are shared runtime files that already
contain unrelated, previously-approved routes/content (including legitimate POST routes
elsewhere in the app), so this script does NOT scan those whole files for dangerous
strings. Instead it diffs each file against the fixed pre-round base commit and scans only
the *added* lines this round introduced — a precise check that this round's own diff
stayed read-only, regardless of what already exists elsewhere in those files.

This script does NOT modify any file, does NOT start a server, sends no POST, makes no
network call, reads no secrets, reads no real queue DB, writes no queue, and does not call
Worker/OpenClaw/Hermes/Google Sheets. Its only subprocess use is read-only git plumbing
(rev-parse, status, diff, ls-files, tag, merge-base).
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

MAIN_PY_REL = "app/main.py"
SYSTEM_HTML_REL = "templates/system.html"
DASHBOARD_CSS_REL = "static/dashboard.css"
CLAUDE_MD_REL = "CLAUDE.md"

DOC_REL = "docs/HERMES_DASHBOARD_ADVICE_PANEL_V0_9_D.md"
DOC_PATH = REPO_ROOT / DOC_REL

SELF_SCRIPT_REL = "scripts/check_hermes_dashboard_advice_panel_v0_9_d.py"
SELF_SCRIPT_PATH = REPO_ROOT / SELF_SCRIPT_REL

B_MODEL_REL = "app/hermes_strategy_suggestion_model.py"
C_GENERATOR_REL = "app/mock_hermes_generator.py"

# v0.9-C commit — HEAD at the start of this round, before app/main.py, templates/system.html,
# and static/dashboard.css were touched.
EXPECTED_BASE_HEAD = "6f58d3ba1feb490b670c8a8e95d6fcc4e3bd6dda"

REQUIRED_DOC_SAFETY_SENTENCES = (
    "Dashboard Hermes advice panel is read-only.",
    "Dashboard Hermes advice panel is not Hermes activation.",
    "Mock Hermes advice is not Owner approval.",
    "Mock Hermes advice is not Blackboard write.",
    "Mock Hermes advice is not automatic follow-up execution.",
    "Mock Hermes advice is not Worker dispatch.",
    "Mock Hermes advice is not OpenClaw call.",
    "Mock Hermes cannot bypass Owner Review.",
    "Mock Hermes cannot bypass Blackboard Activation Policy.",
    "External side effects remain forbidden by default.",
)

REQUIRED_TEMPLATE_READONLY_MARKERS = (
    "This is a Mock Hermes advice preview.",
    "READ-ONLY PREVIEW",
    "MOCK HERMES ONLY",
    "ADVISORY ONLY",
    "NOT OWNER APPROVAL",
    "NOT BLACKBOARD WRITE",
    "NOT WORKER DISPATCH",
    "NOT OPENCLAW CALL",
    "NO EXTERNAL SIDE EFFECTS",
    "OWNER CONFIRMATION REQUIRED",
)

# Structural/attribute patterns forbidden anywhere in the *added* template markup —
# exact substring match is fine, these are tag/attribute shapes, not English prose words.
FORBIDDEN_TEMPLATE_STRUCTURAL_PARTS = (
    ('method="pos', 't"'),
    ("<for", "m"),
    ("<but", "ton"),
    ("action", "="),
)
FORBIDDEN_TEMPLATE_STRUCTURAL_STRINGS = tuple(a + b for a, b in FORBIDDEN_TEMPLATE_STRUCTURAL_PARTS)

# Word-shaped control terms forbidden as whole words in the *added* template markup.
# Word-boundary matched (not substring) so an existing, pre-approved CSS class name like
# "badge-rejected" (a display-only negative-status badge used throughout this repo) does
# not trip a check meant to catch an actual "reject" control.
FORBIDDEN_TEMPLATE_WORD_PARTS = (
    ("appro", "ve"),
    ("rejec", "t"),
    ("execu", "te"),
    ("dispat", "ch"),
    ("sen", "d"),
)
FORBIDDEN_TEMPLATE_WORDS = tuple(a + b for a, b in FORBIDDEN_TEMPLATE_WORD_PARTS)

# Dangerous strings for the *added* app/main.py lines.
FORBIDDEN_MAIN_PY_STRING_PARTS = (
    ("@app.pos", "t("),
    (".pos", "t("),
    ("webhoo", "k"),
    ("connecto", "r"),
)
FORBIDDEN_MAIN_PY_STRINGS = tuple(a + b for a, b in FORBIDDEN_MAIN_PY_STRING_PARTS)

# Dangerous button-like class/style strings for the *added* CSS lines.
FORBIDDEN_CSS_STRING_PARTS = (
    ("appro", "ve"),
    ("execu", "te"),
    ("dispat", "ch"),
    ("sen", "d"),
    ("cursor", ":pointer"),
    ("cursor", ": pointer"),
)
FORBIDDEN_CSS_STRINGS = tuple(a + b for a, b in FORBIDDEN_CSS_STRING_PARTS)

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


def is_tracked(rel: str) -> bool:
    return run_git(["ls-files", "--error-unmatch", rel]).returncode == 0


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def added_lines_since_base(rel: str) -> str:
    """Diff of `rel` between EXPECTED_BASE_HEAD and the full current state (working tree,
    staged, or committed — whichever this round is currently in), added lines only."""
    out = run_git(["diff", EXPECTED_BASE_HEAD, "--", rel])
    added = [
        line[1:] for line in out.stdout.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    ]
    return "\n".join(added)


def untracked_names() -> set[str]:
    return set(git_lines(["ls-files", "--others", "--exclude-standard"]))


def tag_markup_only(html_text: str) -> str:
    """Strip prose text content between tags, keeping only tag markup (tag names and
    attributes). A real dangerous control lives in markup (`<button>`, `action="..."`,
    `class="...reject..."`), not in a text node reciting a safety sentence like "is not
    Worker dispatch." — so scanning only the markup avoids flagging this round's own
    negated safety prose while still catching an actual control if one were added."""
    return re.sub(r">[^<]*<", "><", html_text)


def detect_phase() -> str:
    self_tracked = is_tracked(SELF_SCRIPT_REL)
    if not self_tracked:
        return "owner_review"
    head = run_git(["rev-parse", "HEAD"]).stdout.strip()
    origin = run_git(["rev-parse", "origin/master"]).stdout.strip()
    if head != origin:
        return "post_commit_or_ahead"
    return "post_push_or_synced"


def main() -> None:
    doc_text = read_text(DOC_PATH)
    self_text = read_text(SELF_SCRIPT_PATH)
    main_py_text = read_text(REPO_ROOT / MAIN_PY_REL)
    system_html_text = read_text(REPO_ROOT / SYSTEM_HTML_REL)

    untracked = untracked_names()
    phase = detect_phase()
    print(f"INFO: detected phase = {phase}")

    print("[A] current HEAD contains EXPECTED_BASE_HEAD in git history")
    is_ancestor = run_git(["merge-base", "--is-ancestor", EXPECTED_BASE_HEAD, "HEAD"]).returncode == 0
    check(f"A. HEAD contains {EXPECTED_BASE_HEAD} in git history", is_ancestor)

    print("[B] v0.9-D doc exists")
    check("B. v0.9-D doc exists", DOC_PATH.is_file())

    print("[C] v0.9-D readiness script exists")
    check("C. v0.9-D readiness script exists", SELF_SCRIPT_PATH.is_file())

    print("[D] app/main.py exists")
    check("D. app/main.py exists", (REPO_ROOT / MAIN_PY_REL).is_file())

    print("[E] templates/system.html exists")
    check("E. templates/system.html exists", (REPO_ROOT / SYSTEM_HTML_REL).is_file())

    print("[F] static/dashboard.css exists")
    check("F. static/dashboard.css exists", (REPO_ROOT / DASHBOARD_CSS_REL).is_file())

    print("[G] v0.9-B strategy suggestion model exists")
    check("G. v0.9-B strategy suggestion model exists", (REPO_ROOT / B_MODEL_REL).is_file())

    print("[H] v0.9-C mock Hermes generator exists")
    check("H. v0.9-C mock Hermes generator exists", (REPO_ROOT / C_GENERATOR_REL).is_file())

    print("[I] doc is untracked in Owner Review phase")
    check("I. doc is untracked in Owner Review phase", phase != "owner_review" or not is_tracked(DOC_REL))

    print("[J] readiness script is untracked in Owner Review phase")
    check(
        "J. readiness script is untracked in Owner Review phase",
        phase != "owner_review" or not is_tracked(SELF_SCRIPT_REL),
    )

    print("[K] CLAUDE.md not modified since base")
    claude_md_diff = added_lines_since_base(CLAUDE_MD_REL)
    check(
        f"K. CLAUDE.md not modified since base（found added lines）"
        if claude_md_diff
        else "K. CLAUDE.md not modified since base",
        not claude_md_diff,
    )

    print("[L] untracked only v0.9-D doc/script, patches/*")
    allowed_untracked = {DOC_REL, SELF_SCRIPT_REL} if phase == "owner_review" else set()
    unexpected_untracked = {
        p for p in untracked if p not in allowed_untracked and not p.startswith("patches/")
    }
    check(
        f"L. no unexpected untracked files（found {sorted(unexpected_untracked)}）"
        if unexpected_untracked
        else "L. no unexpected untracked files",
        not unexpected_untracked,
    )

    letters_sentences = ["M", "N", "O", "P", "Q", "R", "S", "T", "U", "V"]
    for letter, sentence in zip(letters_sentences, REQUIRED_DOC_SAFETY_SENTENCES):
        print(f"[{letter}] doc contains: {sentence}")
        check(f"{letter}. doc contains: {sentence}", sentence in doc_text)

    # -----------------------------------------------------------------
    print("[W] Dashboard template contains Hermes advice panel read-only wording")
    missing_readonly_markers = [m for m in REQUIRED_TEMPLATE_READONLY_MARKERS if m not in system_html_text]
    check(
        f"W. Dashboard template contains Hermes advice panel read-only wording（missing {missing_readonly_markers}）"
        if missing_readonly_markers
        else "W. Dashboard template contains Hermes advice panel read-only wording",
        not missing_readonly_markers,
    )

    print("[X] Dashboard template added lines contain no forbidden control strings")
    template_added = added_lines_since_base(SYSTEM_HTML_REL)
    template_added_markup_only = tag_markup_only(template_added)
    found_structural_danger = [s for s in FORBIDDEN_TEMPLATE_STRUCTURAL_STRINGS if s in template_added_markup_only]
    found_word_danger = [
        w for w in FORBIDDEN_TEMPLATE_WORDS
        if re.search(r"\b" + re.escape(w) + r"\b", template_added_markup_only, flags=re.IGNORECASE)
    ]
    found_template_danger = found_structural_danger + found_word_danger
    check(
        f"X. Dashboard template added lines contain no forbidden control strings（found {found_template_danger}）"
        if found_template_danger
        else "X. Dashboard template added lines contain no forbidden control strings",
        not found_template_danger,
    )

    print("[Y] app/main.py added lines contain no forbidden POST/route/webhook/connector strings")
    main_py_added = added_lines_since_base(MAIN_PY_REL)
    found_main_py_danger = [s for s in FORBIDDEN_MAIN_PY_STRINGS if s in main_py_added]
    check(
        f"Y. app/main.py added lines contain no forbidden POST/route/webhook/connector strings（found {found_main_py_danger}）"
        if found_main_py_danger
        else "Y. app/main.py added lines contain no forbidden POST/route/webhook/connector strings",
        not found_main_py_danger,
    )

    print("[Z] static/dashboard.css added lines contain no button-like/interactive styling")
    css_added = added_lines_since_base(DASHBOARD_CSS_REL)
    found_css_danger = [
        s for s in FORBIDDEN_CSS_STRINGS
        if (re.search(r"\b" + re.escape(s) + r"\b", css_added, flags=re.IGNORECASE) if s.isalpha() else s in css_added)
    ]
    check(
        f"Z. static/dashboard.css added lines contain no button-like/interactive styling（found {found_css_danger}）"
        if found_css_danger
        else "Z. static/dashboard.css added lines contain no button-like/interactive styling",
        not found_css_danger,
    )

    print("[AA] app/main.py contains dashboard_hermes_advice_view wiring")
    check(
        "AA. app/main.py contains dashboard_hermes_advice_view wiring",
        "dashboard_hermes_advice_view" in main_py_text
        and "build_mock_hermes_advice" in main_py_text,
    )

    print("[AB] templates/system.html contains dashboard-hermes-advice-view section id")
    check(
        "AB. templates/system.html contains dashboard-hermes-advice-view section id",
        'id="dashboard-hermes-advice-view"' in system_html_text,
    )

    # -----------------------------------------------------------------
    print("[AC] readiness script only invokes read-only git plumbing as subprocess")
    self_subprocess_targets = re.findall(r'subprocess\.run\(\s*\[\s*"([^"]+)"', self_text)
    check(
        f"AC. readiness script only invokes read-only git plumbing as subprocess（found {self_subprocess_targets}）"
        if any(t != "git" for t in self_subprocess_targets)
        else "AC. readiness script only invokes read-only git plumbing as subprocess",
        all(t == "git" for t in self_subprocess_targets),
    )

    print("[AD] readiness script imports no os/network/db module")
    forbidden_self_imports = ("socket", "requests", "httpx", "urllib", "sqlite3")
    found_forbidden_self_imports = [
        m for m in forbidden_self_imports
        if re.search(r"^\s*import\s+" + re.escape(m) + r"\b", self_text, flags=re.MULTILINE)
        or re.search(r"^\s*from\s+" + re.escape(m) + r"\b", self_text, flags=re.MULTILINE)
    ]
    check(
        f"AD. readiness script imports no os/network/db module（found {found_forbidden_self_imports}）"
        if found_forbidden_self_imports
        else "AD. readiness script imports no os/network/db module",
        not found_forbidden_self_imports,
    )

    print("[AE] patches/ remains untracked")
    patches_tracked = git_lines(["ls-files", "--", "patches/"])
    check(
        f"AE. patches/ remains untracked（found tracked {patches_tracked}）"
        if patches_tracked
        else "AE. patches/ remains untracked",
        not patches_tracked,
    )

    print("[AF] no tag")
    tags_at_head = git_lines(["tag", "--points-at", "HEAD"])
    check(
        f"AF. no tag（found {tags_at_head}）" if tags_at_head else "AF. no tag",
        not tags_at_head,
    )

    # -----------------------------------------------------------------
    total = len(PASS) + len(FAIL)
    print(f"\n合計：{len(PASS)}/{total} 通過")
    if FAIL:
        print(f"\nXX v0.9-D readiness 失敗 {len(FAIL)} 項：")
        for f in FAIL:
            print(f"   - {f}")
        sys.exit(1)
    else:
        print("PASS: v0.9-D dashboard Hermes advice panel")
        sys.exit(0)


if __name__ == "__main__":
    main()
