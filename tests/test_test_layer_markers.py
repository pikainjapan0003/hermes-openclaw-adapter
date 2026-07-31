"""Meta guard: every collected test belongs to exactly one suite layer."""

from __future__ import annotations

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
    assert set(layer for layers in assignments.values() for layer in layers) == (
        conftest.LAYER_MARKERS
    )
