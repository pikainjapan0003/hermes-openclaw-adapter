"""Fail-closed guards for current-state and repository-path documentation drift."""

from __future__ import annotations

import re
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


def test_governance_repo_paths_exist_or_match_exact_absent_design_inventory() -> None:
    governance_files = [README, *sorted(GOVERNANCE_DIR.glob("*.md"))]
    referenced: set[str] = set()
    for document in governance_files:
        for match in PATH_REFERENCE.finditer(document.read_text(encoding="utf-8")):
            path = re.sub(r":\d+$", "", match.group("path"))
            if not any(marker in path for marker in ("<", ">", "*")):
                referenced.add(path)

    def _repo_state_exists(path: str) -> bool:
        # data/ holds gitignored runtime artifacts; their presence on a given
        # machine must not change the documented repo-state inventory.
        if path.startswith("data/"):
            return False
        return (ROOT / path).exists()

    missing = {path for path in referenced if not _repo_state_exists(path)}
    assert missing == set(INTENTIONALLY_ABSENT_PATH_REFERENCES), (
        "governance path inventory drifted; every new absent path must be fixed, "
        f"not silently exempted: {sorted(missing)}"
    )
    for path, reason in INTENTIONALLY_ABSENT_PATH_REFERENCES.items():
        assert path in referenced
        assert not _repo_state_exists(path)
        assert reason


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
