"""Keep the Owner one-pager labels identical to their authority designs."""

from pathlib import Path

import pytest


pytestmark = pytest.mark.governance

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "docs" / "agent_operating_system" / "research"
ONE_PAGER = RESEARCH / "OWNER_DECISION_ONE_PAGER_20260726.md"
REDACTION = RESEARCH / "SCHEMA_ERROR_REDACTION_CONTRACT_DESIGN.md"
V1_1 = ROOT / "docs" / "agent_operating_system" / "11_V1_1_FIRST_REAL_WRITE_DESIGN.md"
HERMES = ROOT / "docs" / "agent_operating_system" / "13_HERMES_WIRING_DESIGN.md"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _decision_row(decision: str) -> str:
    prefix = f"| **{decision}**"
    return next(line for line in _text(ONE_PAGER).splitlines() if line.startswith(prefix))


@pytest.mark.parametrize(
    ("decision", "source", "label_pairs"),
    [
        (
            "RED",
            REDACTION,
            (
                ("A: redact inside each validator", "Option A — redact inside each validator"),
                (
                    "B: keep validator output and redact only at exposure points",
                    "Option B — keep validator output and redact only at exposure points",
                ),
                ("C (recommended): double-layer contract", "Option C — double-layer contract"),
            ),
        ),
        (
            "AUD",
            V1_1,
            (
                ("A: 擴充 `audit_event`", "A：擴充 `audit_event`"),
                ("B (recommended): 新增 `v1_1_write_record`", "B：新增 `v1_1_write_record`"),
                ("C: 塞入 `event_notes` 結構化字串", "C：塞入 `event_notes` 結構化字串"),
            ),
        ),
        (
            "RB",
            V1_1,
            (
                ("A: 升版 `rollback_event`", "A：升版 `rollback_event`"),
                ("B (recommended): 新增 `v1_1_rollback_record`", "B：新增 `v1_1_rollback_record`"),
                ("C: 內嵌在候選 `v1_1_write_record`", "C：內嵌在候選 `v1_1_write_record`"),
            ),
        ),
        (
            "PB",
            HERMES,
            (
                ("A (recommended): 精確 enum", "A：精確 enum"),
                ("B: namespace pattern", "B：namespace pattern"),
                ("C: 保留非空字串", "C：保留非空字串"),
            ),
        ),
    ],
)
def test_one_pager_option_labels_match_source_titles(
    decision: str, source: Path, label_pairs: tuple[tuple[str, str], ...]
) -> None:
    row = _decision_row(decision)
    source_text = _text(source)

    for one_pager_label, source_title in label_pairs:
        assert one_pager_label in row
        assert source_title in source_text


def test_root_does_not_invent_an_option_label() -> None:
    row = _decision_row("ROOT")

    assert "No formal source options exist yet." in row
    assert "Suggested direction (not an option label)" in row
    assert "R (recommended)" not in row
    assert "ROOT=R" not in _text(ONE_PAGER)


def test_all_owner_decisions_remain_blank() -> None:
    for decision in ("RED", "AUD", "RB", "PB", "ROOT"):
        assert _decision_row(decision).rstrip().endswith("| **________** |")
