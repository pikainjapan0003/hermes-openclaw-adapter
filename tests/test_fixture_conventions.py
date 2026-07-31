"""Mechanical checks for the tracked fixture naming and loader conventions."""

from __future__ import annotations

import re
from pathlib import Path

from app.blackboard_validators import SCHEMA_FILES


ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "fixtures"
TESTS = ROOT / "tests"
APP = ROOT / "app"
SCRIPTS = ROOT / "scripts"

ALLOWED_DIRECTORIES = {
    "blackboard_contract",
    "builder_golden_vectors",
    "hash_chain_vectors",
    "local_mock_data",
}
BLACKBOARD_CASES = {
    "valid",
    "invalid_missing_common",
    "invalid_extra_safety_flag",
}
BLACKBOARD_NAME = re.compile(
    r"^(?P<message_type>[a-z][a-z0-9_]*)\."
    r"(?P<case>valid|invalid_missing_common|invalid_extra_safety_flag)\.json$"
)
SNAKE_JSON_NAME = re.compile(r"^[a-z][a-z0-9_]*\.json$")
LOCAL_MOCK_NAME = re.compile(r"^[a-z0-9][a-z0-9_.]*\.json$")


def _fixture_files() -> list[Path]:
    return sorted(path for path in FIXTURES.rglob("*") if path.is_file())


def _python_source_corpus() -> str:
    files = (
        sorted(APP.rglob("*.py"))
        + sorted(TESTS.glob("*.py"))
        + sorted(SCRIPTS.glob("*.py"))
    )
    return "\n".join(path.read_text(encoding="utf-8") for path in files)


def test_fixture_directories_and_shared_names_are_closed() -> None:
    files = _fixture_files()
    assert files
    assert {path.parent.name for path in files} == ALLOWED_DIRECTORIES
    assert all(path.parent.parent == FIXTURES for path in files)
    assert all(path.suffix == ".json" for path in files)
    assert all(path.name == path.name.lower() for path in files)
    assert all(" " not in path.name for path in files)


def test_blackboard_fixture_names_cover_exact_registered_cases() -> None:
    seen: dict[str, set[str]] = {}
    for path in sorted((FIXTURES / "blackboard_contract").glob("*.json")):
        match = BLACKBOARD_NAME.fullmatch(path.name)
        assert match is not None, path.name
        message_type = match.group("message_type")
        assert message_type in SCHEMA_FILES
        seen.setdefault(message_type, set()).add(match.group("case"))

    assert set(seen) == set(SCHEMA_FILES)
    assert all(cases == BLACKBOARD_CASES for cases in seen.values())


def test_vector_and_local_mock_names_follow_their_family_rules() -> None:
    builders = {
        path.name
        for path in (FIXTURES / "builder_golden_vectors").glob("*.json")
    }
    assert builders == {
        "approval_packet_vectors.json",
        "evidence_bundle_vectors.json",
    }

    hash_names = {
        path.name
        for path in (FIXTURES / "hash_chain_vectors").glob("*.json")
    }
    assert hash_names
    assert all(SNAKE_JSON_NAME.fullmatch(name) for name in hash_names)

    local_names = {
        path.name
        for path in (FIXTURES / "local_mock_data").glob("*.json")
    }
    assert local_names
    assert all(LOCAL_MOCK_NAME.fullmatch(name) for name in local_names)


def test_each_fixture_family_has_an_executable_loader_reference() -> None:
    blackboard_test = (TESTS / "test_blackboard_schemas.py").read_text(encoding="utf-8")
    assert 'FIXTURE_DIR.glob("*.json")' in blackboard_test
    assert 'f"{message_type}.{case}.json"' in blackboard_test

    builder_test = (TESTS / "test_builder_golden_vectors.py").read_text(encoding="utf-8")
    for name in (
        "approval_packet_vectors.json",
        "evidence_bundle_vectors.json",
    ):
        assert name in builder_test

    hash_test = (TESTS / "test_hash_chain_vectors.py").read_text(encoding="utf-8")
    assert 'VECTOR_DIR.glob("*.json")' in hash_test

    source_corpus = _python_source_corpus()
    for path in sorted((FIXTURES / "local_mock_data").glob("*.json")):
        assert path.name in source_corpus, path.name
