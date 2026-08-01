"""Meta guard: every collected test belongs to exactly one suite layer."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

import conftest


def test_every_collected_test_has_exactly_one_layer_marker(
    request: pytest.FixtureRequest,
) -> None:
    assignments = conftest.COLLECTED_LAYER_ASSIGNMENTS

    assert assignments
    assert len(assignments) == conftest.COLLECTED_ITEM_COUNT
    assert {
        item.nodeid
        for item in request.session.items
    } <= set(assignments)
    invalid = {
        nodeid: layers
        for nodeid, layers in assignments.items()
        if len(layers) != 1
    }
    assert invalid == {}
    observed_layers = {
        layer for layers in assignments.values() for layer in layers
    }
    collected_files = {
        Path(nodeid.split("::", 1)[0]).name for nodeid in assignments
    }
    if collected_files == {
        path.name for path in Path(__file__).parent.glob("test_*.py")
    }:
        assert observed_layers == conftest.LAYER_MARKERS
    else:
        assert observed_layers
        assert observed_layers <= conftest.LAYER_MARKERS


def _explicit_layer_marker(path: Path) -> str | None:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(
            isinstance(target, ast.Name) and target.id == "pytestmark"
            for target in node.targets
        ):
            continue
        value = node.value
        if (
            isinstance(value, ast.Attribute)
            and isinstance(value.value, ast.Attribute)
            and isinstance(value.value.value, ast.Name)
            and value.value.value.id == "pytest"
            and value.value.attr == "mark"
            and value.attr in conftest.LAYER_MARKERS
        ):
            return value.attr
    return None


def test_test_file_inventory_has_one_reviewed_or_explicit_layer() -> None:
    test_files = {
        path.name
        for path in Path(__file__).parent.glob("test_*.py")
    }
    reviewed_files = (
        conftest.CONTRACT_FILES
        | conftest.FUZZ_FILES
        | conftest.GOVERNANCE_FILES
        | conftest.LEGACY_FILES
    )

    assert len(reviewed_files) == sum(
        len(group)
        for group in (
            conftest.CONTRACT_FILES,
            conftest.FUZZ_FILES,
            conftest.GOVERNANCE_FILES,
            conftest.LEGACY_FILES,
        )
    )
    unregistered = test_files - reviewed_files
    assert all(
        _explicit_layer_marker(Path(__file__).parent / name) is not None
        for name in unregistered
    )
    assert reviewed_files <= test_files


def test_new_unmarked_test_file_is_rejected_instead_of_defaulting_contract() -> None:
    with pytest.raises(ValueError, match="no explicit test-layer marker"):
        conftest._layer_for(Path("test_new_unmarked_module.py"))


def test_four_layer_outcome_sum_equals_complete_collection() -> None:
    counts = {layer: 0 for layer in conftest.LAYER_MARKERS}
    for layers in conftest.COLLECTED_LAYER_ASSIGNMENTS.values():
        assert len(layers) == 1
        counts[layers[0]] += 1

    assert sum(counts.values()) == conftest.COLLECTED_ITEM_COUNT
    collected_files = {
        Path(nodeid.split("::", 1)[0]).name
        for nodeid in conftest.COLLECTED_LAYER_ASSIGNMENTS
    }
    if collected_files == {
        path.name for path in Path(__file__).parent.glob("test_*.py")
    }:
        assert all(count > 0 for count in counts.values())
    else:
        assert any(count > 0 for count in counts.values())


def test_slow_marker_is_optional_and_never_counts_as_a_layer(
    request: pytest.FixtureRequest,
) -> None:
    assert set(conftest.COLLECTED_OPTIONAL_ASSIGNMENTS) == set(
        conftest.COLLECTED_LAYER_ASSIGNMENTS
    )
    for item in request.session.items:
        optional = conftest.COLLECTED_OPTIONAL_ASSIGNMENTS[item.nodeid]
        assert set(optional) <= conftest.OPTIONAL_MARKERS
        assert len(optional) <= 1
        assert len([marker for marker in item.iter_markers("slow")]) <= 1
        layers = conftest.COLLECTED_LAYER_ASSIGNMENTS[item.nodeid]
        assert "slow" not in layers
        assert len(layers) == 1
