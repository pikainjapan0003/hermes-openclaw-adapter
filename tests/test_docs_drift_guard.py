"""Fail-closed guards for current-state and repository-path documentation drift."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
PLAN = ROOT / "docs" / "agent_operating_system" / "05_VERIFIED_LONG_TERM_PLAN.md"
QUICK_DIAGNOSIS = ROOT / "docs" / "agent_operating_system" / "00_QUICK_DIAGNOSIS.md"
INDEX = ROOT / "docs" / "schemas" / "blackboard" / "INDEX.md"
GOVERNANCE_DIR = ROOT / "docs" / "agent_operating_system"

PATH_REFERENCE = re.compile(
    r"`(?P<path>(?:README\.md|CLAUDE\.md|"
    r"(?:app|docs|tests|fixtures|scripts|templates|data)/"
    r"[^`\s,;，。；：)）]+))`"
)

# These references are deliberately absent and are locked here so that the guard
# distinguishes planning/history from an accidental broken current-state link.
INTENTIONALLY_ABSENT_PATH_REFERENCES = {
    "app/audit_writer_local.py": "Phase 7 design target; writer is not authorized",
    "app/connector_scope_gate.py": "Phase 10 future output",
    "data/audit_dev.jsonl": "Phase 7 target; formal data path must remain absent",
    "data/blackboard_dev/": "planning-only board layout",
    "tests/v1_1_write_probe.txt": "planning-only v1.1 target",
    "data/results.jsonl": "historical README architecture record",
    "docs/schemas/approval_packet.json": "historical Phase 4 output spelling",
}


def _phase_rows(plan_text: str) -> dict[str, str]:
    section = plan_text.split("## 5. 狀態追蹤", 1)[1].split("## 6.", 1)[0]
    rows: dict[str, str] = {}
    for phase, status in re.findall(r"^\| ([0-9]+(?:–[0-9]+)?) \| ([^|]+) \|", section, re.MULTILINE):
        rows[phase] = status.strip().replace("**", "")
    return rows


def _git_tracked_paths(root: Path) -> set[str] | None:
    """Return the repo-state inventory, or ``None`` for explicit fallback."""

    try:
        completed = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=root,
            check=True,
            capture_output=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return {
        item.decode("utf-8").replace("\\", "/")
        for item in completed.stdout.split(b"\0")
        if item
    }


def _repo_state_exists(path: str, *, root: Path, tracked: set[str] | None) -> bool:
    normalized = path.rstrip("/").replace("\\", "/")
    if tracked is not None:
        return normalized in tracked or any(
            item.startswith(f"{normalized}/") for item in tracked
        )

    # Explicit fallback for environments where the read-only git query fails.
    # Runtime data remains non-repository state even if this machine has leftovers.
    if normalized.startswith("data/"):
        return False
    return (root / normalized).exists()


def test_readme_current_phase_claims_match_plan_status_table() -> None:
    readme = README.read_text(encoding="utf-8")
    current = readme.split("## 目前狀態", 1)[1].split("\n---", 1)[0]
    rows = _phase_rows(PLAN.read_text(encoding="utf-8"))

    assert "Phase 2（v1.0 Definition Freeze）與 Phase 3–6 已完成" in current
    assert all(rows[str(phase)] == "完成" for phase in range(2, 7))
    assert "Phase 7 audit write 設計已備但 writer 尚未授權" in current
    assert rows["7"] == "設計已備"
    assert "Phase 8 規劃與離線 projection contract 已完成" in current
    assert rows["8"] == "規劃完成"
    assert "Phase 9 N=1 需 Owner 在場" in current
    assert rows["9–11"] == "未開始"
    assert "493 passed" not in current
    assert "實際測試數量以 CI 或當次本機實跑輸出為準" in current


def test_governance_repo_paths_exist_or_match_exact_absent_design_inventory() -> None:
    governance_files = [README, *sorted(GOVERNANCE_DIR.glob("*.md"))]
    referenced: set[str] = set()
    for document in governance_files:
        for match in PATH_REFERENCE.finditer(document.read_text(encoding="utf-8")):
            path = re.sub(r":\d+$", "", match.group("path"))
            if not any(marker in path for marker in ("<", ">", "*")):
                referenced.add(path)

    tracked = _git_tracked_paths(ROOT)
    missing = {
        path
        for path in referenced
        if not _repo_state_exists(path, root=ROOT, tracked=tracked)
    }
    assert missing == set(INTENTIONALLY_ABSENT_PATH_REFERENCES), (
        "governance path inventory drifted; every new absent path must be fixed, "
        f"not silently exempted: {sorted(missing)}"
    )
    for path, reason in INTENTIONALLY_ABSENT_PATH_REFERENCES.items():
        assert path in referenced
        assert not _repo_state_exists(path, root=ROOT, tracked=tracked)
        assert reason


def test_git_inventory_ignores_runtime_artifact_presence_in_fake_repo(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    tracked_file = repo / "docs" / "tracked.md"
    tracked_file.parent.mkdir()
    tracked_file.write_text("tracked", encoding="utf-8")
    subprocess.run(["git", "add", "docs/tracked.md"], cwd=repo, check=True)

    runtime = repo / "data" / "results.jsonl"
    runtime.parent.mkdir()
    runtime.write_text("runtime", encoding="utf-8")
    with_runtime = _git_tracked_paths(repo)
    runtime.unlink()
    without_runtime = _git_tracked_paths(repo)

    assert with_runtime == without_runtime == {"docs/tracked.md"}
    assert _repo_state_exists(
        "docs/tracked.md", root=repo, tracked=with_runtime
    ) is True
    assert _repo_state_exists(
        "data/results.jsonl", root=repo, tracked=with_runtime
    ) is False
    assert _repo_state_exists(
        "data/results.jsonl", root=repo, tracked=without_runtime
    ) is False


def test_git_inventory_failure_uses_marked_fallback(
    tmp_path: Path, monkeypatch
) -> None:
    def fail(*_args, **_kwargs):
        raise OSError("synthetic git failure")

    monkeypatch.setattr(subprocess, "run", fail)
    assert _git_tracked_paths(tmp_path) is None
    existing = tmp_path / "docs" / "tracked.md"
    existing.parent.mkdir()
    existing.write_text("fallback", encoding="utf-8")
    assert _repo_state_exists("docs/tracked.md", root=tmp_path, tracked=None) is True
    assert _repo_state_exists("data/results.jsonl", root=tmp_path, tracked=None) is False


def test_quick_diagnosis_d04_closeout_reference_exists() -> None:
    text = QUICK_DIAGNOSIS.read_text(encoding="utf-8")
    section = text.split("### D-04", 1)[1].split("### D-05", 1)[0]
    match = re.search(r"`(?P<path>docs/[^`]+CLOSEOUT[^`]+\.md)`", section)
    assert match is not None
    assert (ROOT / match.group("path")).is_file()


def test_contract_index_table_paths_all_exist() -> None:
    text = INDEX.read_text(encoding="utf-8")
    rows = re.findall(
        r"^\| `[^`]+` \| [^|]+ \| `(?P<artifact>[^`]+)` "
        r"\| `(?P<reference>[^`]+)` \| `(?P<test>[^`]+)` \|$",
        text,
        re.MULTILINE,
    )
    assert len(rows) == 15
    for row in rows:
        for path in row:
            assert (ROOT / path).is_file(), f"INDEX references missing path: {path}"
