"""Mechanical integrity checks for governance cross-reference identifiers."""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
GOVERNANCE_DIR = ROOT / "docs" / "agent_operating_system"
TOKEN_RE = re.compile(
    r"(?<![A-Za-z0-9])(?:D-\d{2}|R-\d{2}|L-\d{3}|C-?\d+|F-?\d+|§6\.\d+)"
)
AUTHORITY_FILES = {
    "D": GOVERNANCE_DIR / "00_QUICK_DIAGNOSIS.md",
    "R": GOVERNANCE_DIR / "20_JUDGMENT_RUBRICS.md",
    "L": GOVERNANCE_DIR / "90_LESSONS_LEARNED.md",
    "C": GOVERNANCE_DIR / "10_MODEL_ORCHESTRATION.md",
    "F": GOVERNANCE_DIR / "40_MAINTENANCE_PROTOCOL.md",
    "§": GOVERNANCE_DIR / "05_VERIFIED_LONG_TERM_PLAN.md",
}


def _governance_files() -> list[Path]:
    files = sorted(GOVERNANCE_DIR.glob("*.md"))
    files.extend((ROOT / "CLAUDE.md", ROOT / "README.md"))
    return [path for path in files if path.is_file()]


def _tokens(path: Path) -> set[str]:
    return set(TOKEN_RE.findall(path.read_text(encoding="utf-8")))


def _definition_tokens(family: str, path: Path) -> set[str]:
    tokens = _tokens(path)
    if family == "§":
        headings = re.findall(
            r"(?m)^#{1,6}\s+6\.(\d+)\b",
            path.read_text(encoding="utf-8"),
        )
        tokens.update(f"§6.{suffix}" for suffix in headings)
    return tokens


def _family(token: str) -> str:
    return "§" if token.startswith("§") else token[0]


def test_every_governance_reference_has_an_authority_definition() -> None:
    files = _governance_files()
    assert files
    authority_tokens = {
        family: _definition_tokens(family, path)
        for family, path in AUTHORITY_FILES.items()
    }
    missing: list[str] = []
    for path in files:
        for token in sorted(_tokens(path)):
            if token not in authority_tokens[_family(token)]:
                missing.append(f"{path.relative_to(ROOT).as_posix()}: {token}")
    assert missing == []


def test_authority_files_and_identifier_families_are_present() -> None:
    for family, path in AUTHORITY_FILES.items():
        assert path.is_file(), family
        assert _definition_tokens(family, path), family


def test_unreferenced_definitions_are_reported_but_do_not_fail() -> None:
    files = _governance_files()
    counts: Counter[str] = Counter()
    for path in files:
        counts.update(_tokens(path))

    orphaned = sorted({
        token
        for family, authority in AUTHORITY_FILES.items()
        for token in _definition_tokens(family, authority)
        if counts[token] == 1
    })
    print("unreferenced governance definitions (advisory only):")
    print(", ".join(orphaned) if orphaned else "none")
    assert isinstance(orphaned, list)
