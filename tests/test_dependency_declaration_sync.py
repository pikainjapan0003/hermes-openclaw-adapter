"""Report-style dependency drift guard with the current mismatch as baseline."""

from __future__ import annotations

import ast
import re
import sys
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
REQUIREMENTS = ROOT / "requirements.txt"
REQUIREMENTS_DEV = ROOT / "requirements-dev.txt"
PYPROJECT = ROOT / "pyproject.toml"

EXPECTED_REQUIREMENTS_ONLY = frozenset(
    {"google-api-python-client", "google-auth-oauthlib", "jsonschema"}
)
EXPECTED_PYPROJECT_ONLY = frozenset()
EXPECTED_IMPORTED_DISTRIBUTIONS = frozenset(
    {
        "fastapi",
        "google-api-python-client",
        "google-auth-oauthlib",
        "httpx",
        "jsonschema",
        "pydantic",
        "pytest",
        "python-dotenv",
    }
)
EXPECTED_DECLARED_WITHOUT_LITERAL_IMPORT = frozenset(
    {
        "jinja2",
        "mypy",
        "pytest-cov",
        "python-multipart",
        "types-jsonschema",
        "uvicorn",
    }
)
IMPORT_TO_DISTRIBUTION = {
    "dotenv": "python-dotenv",
    "fastapi": "fastapi",
    "google": "google-api-python-client",
    "google_auth_oauthlib": "google-auth-oauthlib",
    "googleapiclient": "google-api-python-client",
    "httpx": "httpx",
    "jsonschema": "jsonschema",
    "pydantic": "pydantic",
    "pytest": "pytest",
}


def _normalize_distribution(requirement: str) -> str:
    name = re.split(r"[<>=!~;\[]", requirement, maxsplit=1)[0]
    return re.sub(r"[-_.]+", "-", name.strip().lower())


def _requirements(path: Path) -> frozenset[str]:
    return frozenset(
        _normalize_distribution(line)
        for raw in path.read_text(encoding="utf-8").splitlines()
        if (line := raw.strip()) and not line.startswith("#")
    )


def _pyproject_dependencies() -> frozenset[str]:
    document = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    return frozenset(
        _normalize_distribution(item)
        for item in document["project"]["dependencies"]
    )


def _literal_import_roots() -> frozenset[str]:
    roots: set[str] = set()
    for source_root in (ROOT / "app", ROOT / "scripts", ROOT / "tests"):
        for path in source_root.rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    roots.update(alias.name.split(".", 1)[0] for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    roots.add(node.module.split(".", 1)[0])
    return frozenset(roots)


def test_production_declaration_drift_matches_the_reviewed_baseline() -> None:
    project = _pyproject_dependencies()
    requirements = _requirements(REQUIREMENTS)

    assert requirements - project == EXPECTED_REQUIREMENTS_ONLY, (
        "requirements.txt-only dependency drift changed; review authority before "
        f"accepting: added={sorted((requirements - project) - EXPECTED_REQUIREMENTS_ONLY)}, "
        f"removed={sorted(EXPECTED_REQUIREMENTS_ONLY - (requirements - project))}"
    )
    assert project - requirements == EXPECTED_PYPROJECT_ONLY, (
        "pyproject-only dependency drift changed; review before accepting: "
        f"{sorted(project - requirements)}"
    )


def test_literal_third_party_imports_have_a_declared_distribution() -> None:
    roots = _literal_import_roots()
    unknown_third_party_roots = {
        root
        for root in roots
        if root not in sys.stdlib_module_names
        and root not in {"__future__", "app", "conftest", "scripts", "tests"}
        and not (ROOT / f"{root}.py").exists()
        and not (ROOT / "app" / f"{root}.py").exists()
        and not (ROOT / "scripts" / f"{root}.py").exists()
        and root not in IMPORT_TO_DISTRIBUTION
    }
    assert unknown_third_party_roots == set(), (
        "new import roots need an explicit distribution mapping and declaration: "
        f"{sorted(unknown_third_party_roots)}"
    )

    imported_distributions = frozenset(
        IMPORT_TO_DISTRIBUTION[root]
        for root in roots
        if root in IMPORT_TO_DISTRIBUTION
    )
    declared = _requirements(REQUIREMENTS) | _requirements(REQUIREMENTS_DEV)
    assert imported_distributions <= declared
    assert imported_distributions == EXPECTED_IMPORTED_DISTRIBUTIONS, (
        "literal third-party import baseline changed: "
        f"added={sorted(imported_distributions - EXPECTED_IMPORTED_DISTRIBUTIONS)}, "
        f"removed={sorted(EXPECTED_IMPORTED_DISTRIBUTIONS - imported_distributions)}"
    )


def test_declared_without_literal_import_baseline_does_not_silently_grow() -> None:
    declared = _requirements(REQUIREMENTS) | _requirements(REQUIREMENTS_DEV)
    roots = _literal_import_roots()
    imported = frozenset(
        IMPORT_TO_DISTRIBUTION[root]
        for root in roots
        if root in IMPORT_TO_DISTRIBUTION
    )

    assert declared - imported == EXPECTED_DECLARED_WITHOUT_LITERAL_IMPORT, (
        "declared-without-literal-import baseline changed; operational/plugin "
        f"dependencies require review: added={sorted((declared - imported) - EXPECTED_DECLARED_WITHOUT_LITERAL_IMPORT)}, "
        f"removed={sorted(EXPECTED_DECLARED_WITHOUT_LITERAL_IMPORT - (declared - imported))}"
    )
