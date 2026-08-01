"""Lock the measured >2-second baseline to explicit ``slow`` markers.

The baseline comes from the one-time ``--durations`` measurement recorded in
``TEST_PERFORMANCE_20260729.md`` plus the remeasurement of the queue runtime
guard performed for NIGHT-BATCH-19 package 2.  This meta-test does not time or
rerun other tests; it verifies that the reviewed baseline remains selected by
the optional marker without becoming a suite layer.
"""

from __future__ import annotations

from pathlib import Path
import ast

import pytest

import conftest


pytestmark = pytest.mark.governance

MEASURED_OVER_TWO_SECONDS = frozenset(
    {
        "tests/test_main_coverage_floor.py::test_main_branch_coverage_does_not_regress",
        "tests/test_board_reader_stress.py::test_board_reader_stress_measures_200_complete_boards",
        "tests/test_board_reader_capacity.py::test_reader_capacity_probe_reports_runtime_and_peak_memory",
        "tests/test_error_surface_no_leak.py::test_fixture_loader_pytest_report_redacts_sensitive_markers",
        "tests/test_dependency_declaration_sync.py::test_declared_without_literal_import_baseline_does_not_silently_grow",
        "tests/test_dependency_declaration_sync.py::test_literal_third_party_imports_have_a_declared_distribution",
        "tests/test_queue_claim_guard.py::test_app_import_all_dashboard_gets_and_approve_never_claim",
    }
)


def _base_nodeid(nodeid: str) -> str:
    return nodeid.split("[", 1)[0].replace("\\", "/")


def _is_pytest_marker(node: ast.AST, marker: str) -> bool:
    return (
        isinstance(node, ast.Attribute)
        and node.attr == marker
        and isinstance(node.value, ast.Attribute)
        and node.value.attr == "mark"
        and isinstance(node.value.value, ast.Name)
        and node.value.value.id == "pytest"
    )


def _contains_pytest_marker(node: ast.AST, marker: str) -> bool:
    if _is_pytest_marker(node, marker):
        return True
    if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        return any(_contains_pytest_marker(item, marker) for item in node.elts)
    return False


def _pytestmark_value(tree: ast.Module) -> ast.AST | None:
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if any(
            isinstance(target, ast.Name) and target.id == "pytestmark"
            for target in node.targets
        ):
            return node.value
    return None


def _slow_nodes_from_sources() -> set[str]:
    tests_dir = Path(__file__).resolve().parent
    slow_nodes: set[str] = set()
    for path in sorted(tests_dir.glob("test_*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        pytestmark_value = _pytestmark_value(tree)
        file_is_slow = pytestmark_value is not None and _contains_pytest_marker(
            pytestmark_value, "slow"
        )
        for node in tree.body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if not node.name.startswith("test_"):
                continue
            if file_is_slow or any(
                _is_pytest_marker(decorator, "slow")
                for decorator in node.decorator_list
            ):
                slow_nodes.add(f"tests/{path.name}::{node.name}")
    return slow_nodes


def _layer_for_source(nodeid: str) -> str:
    path = Path(nodeid.split("::", 1)[0])
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    pytestmark_value = _pytestmark_value(tree)
    explicit = {
        layer
        for layer in conftest.LAYER_MARKERS
        if pytestmark_value is not None
        and _contains_pytest_marker(pytestmark_value, layer)
    }
    if explicit:
        assert len(explicit) == 1
        return next(iter(explicit))
    return conftest._layer_for(path)


def test_every_measured_over_two_second_test_is_marked_slow() -> None:
    slow_nodes = {_base_nodeid(nodeid) for nodeid in _slow_nodes_from_sources()}

    assert MEASURED_OVER_TWO_SECONDS <= slow_nodes


def test_slow_assignments_remain_compatible_with_exactly_one_layer() -> None:
    slow_assignments = {
        nodeid: _layer_for_source(nodeid)
        for nodeid in _slow_nodes_from_sources()
    }

    assert slow_assignments
    assert set(slow_assignments.values()) <= conftest.LAYER_MARKERS
    assert all(layer != "slow" for layer in slow_assignments.values())


def test_recorded_duration_baseline_names_every_guarded_family() -> None:
    report = (
        Path(__file__).resolve().parent.parent
        / "docs"
        / "agent_operating_system"
        / "research"
        / "TEST_PERFORMANCE_20260729.md"
    ).read_text(encoding="utf-8")

    for nodeid in MEASURED_OVER_TWO_SECONDS - {
        "tests/test_queue_claim_guard.py::test_app_import_all_dashboard_gets_and_approve_never_claim"
    }:
        recorded_name = nodeid.split("/", 1)[1]
        if "test_fixture_loader_pytest_report_redacts_sensitive_markers" in recorded_name:
            recorded_name = recorded_name.replace(
                "test_fixture_loader_pytest_report_redacts_sensitive_markers",
                "test_fixture_loader_pytest_report_leak_baseline_is_explicit",
            )
        assert recorded_name in report
