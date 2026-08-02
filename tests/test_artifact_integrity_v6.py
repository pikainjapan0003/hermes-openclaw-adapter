"""Round-six closed inventory including top-level governance documents."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from tests.test_artifact_integrity_v5 import ROOT, _normalized_bytes, _v5_paths


pytestmark = pytest.mark.contract

EXPECTED_GOVERNANCE_PATHS = frozenset(
    {
        "docs/agent_operating_system/00_QUICK_DIAGNOSIS.md",
        "docs/agent_operating_system/01_SAFETY_BOUNDARIES.md",
        "docs/agent_operating_system/02_V1_0_DEFINITION.md",
        "docs/agent_operating_system/05_VERIFIED_LONG_TERM_PLAN.md",
        "docs/agent_operating_system/07_AUDIT_WRITE_DESIGN.md",
        "docs/agent_operating_system/08_REMOTE_READONLY_PLAN.md",
        "docs/agent_operating_system/09_N1_PREFLIGHT_RUNBOOK.md",
        "docs/agent_operating_system/10_MODEL_ORCHESTRATION.md",
        "docs/agent_operating_system/11_V1_1_FIRST_REAL_WRITE_DESIGN.md",
        "docs/agent_operating_system/12_BLACKBOARD_DATA_LAYOUT.md",
        "docs/agent_operating_system/13_HERMES_WIRING_DESIGN.md",
        "docs/agent_operating_system/14_V1_2_FIRST_CODE_TASK_DESIGN.md",
        "docs/agent_operating_system/20_JUDGMENT_RUBRICS.md",
        "docs/agent_operating_system/30_DELEGATION_PROMPTS.md",
        "docs/agent_operating_system/40_MAINTENANCE_PROTOCOL.md",
        "docs/agent_operating_system/90_LESSONS_LEARNED.md",
        "docs/agent_operating_system/99_LETTER_TO_FUTURE_SESSIONS.md",
        "docs/agent_operating_system/NIGHT_BATCH_BACKLOG.md",
        "docs/agent_operating_system/README.md",
    }
)
EXPECTED_V6_PATH_COUNT = 298
EXPECTED_V6_PATH_SET_SHA256 = (
    "1150d7896b4517ec7d4d862f73b1ea7bbbcc96896559d8850fb7f1e147b4dc22"
)
EXPECTED_GOVERNANCE_PATH_MANIFEST_SHA256 = (
    "fd6cb7f07fd1d1fe668ff03438a23ddcf284df0efe4d1fe6acef9c03703e73a1"
)


def _governance_paths() -> set[str]:
    root = ROOT / "docs" / "agent_operating_system"
    return {
        path.relative_to(ROOT).as_posix()
        for path in root.glob("*.md")
        if path.is_file()
    }


def _path_manifest_digest(paths: set[str] | frozenset[str]) -> str:
    encoded = "".join(f"{path}\n" for path in sorted(paths)).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _v6_path_set() -> set[str]:
    return _v5_paths() | set(EXPECTED_GOVERNANCE_PATHS)


def test_v6_inventory_is_closed_and_extends_v5_with_governance_docs() -> None:
    actual_governance = _governance_paths()
    expected_all = _v5_paths() | set(EXPECTED_GOVERNANCE_PATHS)

    assert actual_governance == set(EXPECTED_GOVERNANCE_PATHS), {
        "unregistered": sorted(actual_governance - EXPECTED_GOVERNANCE_PATHS),
        "missing": sorted(EXPECTED_GOVERNANCE_PATHS - actual_governance),
    }
    assert len(expected_all) == EXPECTED_V6_PATH_COUNT
    assert _v5_paths() <= expected_all


def test_v6_governance_path_manifest_is_pinned() -> None:
    assert (
        _path_manifest_digest(EXPECTED_GOVERNANCE_PATHS)
        == EXPECTED_GOVERNANCE_PATH_MANIFEST_SHA256
    )


def test_v6_collection_path_set_digest_is_pinned() -> None:
    """The membership digest complements, but does not replace, content hashes."""

    paths = _v6_path_set()
    assert len(paths) == EXPECTED_V6_PATH_COUNT
    assert _path_manifest_digest(paths) == EXPECTED_V6_PATH_SET_SHA256


@pytest.mark.parametrize("relative_path", sorted(EXPECTED_GOVERNANCE_PATHS))
def test_v6_governance_docs_are_portably_normalizable(relative_path: str) -> None:
    normalized = _normalized_bytes(ROOT / relative_path)

    assert normalized.decode("utf-8")
    assert len(hashlib.sha256(normalized).hexdigest()) == 64


def test_v6_new_governance_file_would_be_unregistered(tmp_path: Path) -> None:
    unregistered = tmp_path / "docs" / "agent_operating_system" / "NEW.md"
    unregistered.parent.mkdir(parents=True)
    unregistered.write_text("new\n", encoding="utf-8")

    discovered = {
        path.relative_to(tmp_path).as_posix()
        for path in unregistered.parent.glob("*.md")
        if path.is_file()
    }
    assert discovered - EXPECTED_GOVERNANCE_PATHS == {
        "docs/agent_operating_system/NEW.md"
    }
