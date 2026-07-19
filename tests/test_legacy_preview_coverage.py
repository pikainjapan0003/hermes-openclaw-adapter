"""Branch-focused tests for the two legacy read-only preview adapters."""

from __future__ import annotations

from copy import deepcopy
import json

import pytest

import app.full_loop_preview_adapter as full_loop
import app.result_feedback_preview as feedback


class _StaticFixturePath:
    def __init__(self, payload: str) -> None:
        self._payload = payload

    def read_text(self, *, encoding: str) -> str:
        assert encoding == "utf-8"
        return self._payload


def _full_loop_record() -> dict[str, object]:
    return json.loads(full_loop.FIXTURE_PATH.read_text(encoding="utf-8"))


def _feedback_record() -> dict[str, object]:
    return json.loads(feedback.FIXTURE_PATH.read_text(encoding="utf-8"))


def _build_full_loop_with(
    monkeypatch: pytest.MonkeyPatch, record: dict[str, object]
) -> dict[str, object]:
    monkeypatch.setattr(
        full_loop, "load_full_loop_rehearsal_fixture", lambda: record
    )
    return full_loop.build_full_loop_rehearsal_preview_model()


def _build_feedback_with(
    monkeypatch: pytest.MonkeyPatch, record: dict[str, object]
) -> dict[str, object]:
    monkeypatch.setattr(
        feedback, "load_result_feedback_preview_fixture", lambda: record
    )
    return feedback.build_result_feedback_preview_view_model()


def test_full_loop_loader_rejects_non_object_root(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(full_loop, "FIXTURE_PATH", _StaticFixturePath("[]"))

    with pytest.raises(ValueError, match="fixture root must be a JSON object"):
        full_loop.load_full_loop_rehearsal_fixture()


def test_full_loop_load_failure_is_fail_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_load() -> dict[str, object]:
        raise OSError("synthetic read failure")

    monkeypatch.setattr(full_loop, "load_full_loop_rehearsal_fixture", fail_load)
    preview = full_loop.build_full_loop_rehearsal_preview_model()

    assert preview["accepted"] is False
    assert preview["validation_status"] == "unsafe_rejected"
    assert preview["timeline_preview"] == []
    assert "synthetic read failure" in str(preview["validation_summary"])


def test_full_loop_missing_field_is_fail_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    record = _full_loop_record()
    record.pop("artifacts")

    preview = _build_full_loop_with(monkeypatch, record)

    assert preview["accepted"] is False
    assert preview["validation_summary"] == "missing required top-level fixture fields"
    assert "missing field: artifacts" in preview["fail_closed_reasons"]


def test_full_loop_rejects_both_unsafe_top_level_flag_polarities(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    record = _full_loop_record()
    record["synthetic_local_only"] = False
    record["external_side_effects_allowed"] = True

    preview = _build_full_loop_with(monkeypatch, record)

    assert preview["accepted"] is False
    assert preview["validation_summary"] == "unsafe top-level fixture flags"
    assert "top-level synthetic_local_only must be true" in preview[
        "fail_closed_reasons"
    ]
    assert "top-level external_side_effects_allowed must be false" in preview[
        "fail_closed_reasons"
    ]


def test_full_loop_rejects_non_mapping_and_unsafe_global_flags(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    non_mapping = _full_loop_record()
    non_mapping["safety_flags"] = []
    preview = _build_full_loop_with(monkeypatch, non_mapping)
    assert preview["validation_summary"] == "unsafe global safety flags"
    assert preview["fail_closed_reasons"] == ["safety_flags must be a mapping"]

    unsafe = _full_loop_record()
    flags = unsafe["safety_flags"]
    assert isinstance(flags, dict)
    flags["synthetic_local_only"] = False
    flags["external_side_effects_allowed"] = True
    preview = _build_full_loop_with(monkeypatch, unsafe)
    assert "safety_flags.synthetic_local_only must be true" in preview[
        "fail_closed_reasons"
    ]
    assert "safety_flags.external_side_effects_allowed must be false" in preview[
        "fail_closed_reasons"
    ]


def test_full_loop_timeline_validation_covers_fail_closed_branches(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    empty = _full_loop_record()
    empty["timeline"] = []
    preview = _build_full_loop_with(monkeypatch, empty)
    assert preview["validation_summary"] == "unsafe or invalid timeline"
    assert preview["fail_closed_reasons"] == ["timeline must be a non-empty list"]

    assert "timeline[0] must be a mapping" in full_loop._validate_timeline([42])
    missing_fields = full_loop._validate_timeline(
        [{"step_id": "owner_rehearsal_request"}]
    )
    assert "timeline[0] missing fields" in missing_fields[0]

    timeline = deepcopy(_full_loop_record()["timeline"])
    assert isinstance(timeline, list)
    first = timeline[0]
    assert isinstance(first, dict)
    first["step_order"] = 99
    first["safety_flags"] = []
    violations = full_loop._validate_timeline(timeline)
    assert any("step_order must be 1" in item for item in violations)
    assert "timeline[0] safety_flags must be a mapping" in violations

    timeline = deepcopy(_full_loop_record()["timeline"])
    assert isinstance(timeline, list)
    first = timeline[0]
    assert isinstance(first, dict)
    first["safety_flags"] = {"worker_dispatch_allowed": True}
    violations = full_loop._validate_timeline(timeline)
    assert (
        "timeline[0] safety_flags.worker_dispatch_allowed must be false, got True"
        in violations
    )

    timeline = deepcopy(_full_loop_record()["timeline"])
    assert isinstance(timeline, list)
    timeline[0], timeline[1] = timeline[1], timeline[0]
    violations = full_loop._validate_timeline(timeline)
    assert "timeline steps are out of the required deterministic order" in violations


def test_full_loop_rejects_nested_forbidden_names_and_unsafe_text(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    forbidden = _full_loop_record()
    forbidden["extra"] = [{"api_token": "redacted"}]
    preview = _build_full_loop_with(monkeypatch, forbidden)
    assert preview["validation_summary"] == "forbidden field names detected in fixture"
    assert preview["fail_closed_reasons"] == ["forbidden field name: api_token"]

    unsafe_text = _full_loop_record()
    unsafe_text["loop_summary"] = {"nested": ["sk-synthetic-secret"]}
    preview = _build_full_loop_with(monkeypatch, unsafe_text)
    assert preview["validation_summary"].startswith("unsafe text content detected")
    assert preview["accepted"] is False


def test_result_feedback_loader_rejects_non_object_root(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(feedback, "FIXTURE_PATH", _StaticFixturePath("[]"))

    with pytest.raises(ValueError, match="fixture root must be a JSON object"):
        feedback.load_result_feedback_preview_fixture()


def test_result_feedback_load_failure_is_fail_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_load() -> dict[str, object]:
        raise OSError("synthetic feedback read failure")

    monkeypatch.setattr(feedback, "load_result_feedback_preview_fixture", fail_load)
    view = feedback.build_result_feedback_preview_view_model()

    assert view["accepted"] is False
    assert view["preview_only"] is True
    assert "synthetic feedback read failure" in str(view["rejection_reason"])
    assert view["callback_id"] is None


def test_result_feedback_missing_field_is_fail_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    record = _feedback_record()
    record.pop("summary")

    view = _build_feedback_with(monkeypatch, record)

    assert view["accepted"] is False
    assert view["rejection_reason"] == "missing required fixture fields"
    assert view["rejection_details"] == ["missing field: summary"]


def test_result_feedback_rejects_both_unsafe_flag_polarities(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    record = _feedback_record()
    record["synthetic_local_only"] = False
    record["external_side_effects_allowed"] = True

    view = _build_feedback_with(monkeypatch, record)

    assert view["accepted"] is False
    assert view["rejection_reason"] == "unsafe fixture safety flags"
    assert "synthetic_local_only must be true" in view["rejection_details"]
    assert "external_side_effects_allowed must be false" in view["rejection_details"]


def test_result_feedback_valid_fixture_remains_read_only(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    view = _build_feedback_with(monkeypatch, _feedback_record())

    assert view["accepted"] is True
    assert view["preview_only"] is True
    assert view["rejection_reason"] is None
    assert view["worker_dispatch_allowed"] is False
    assert view["blackboard_write_allowed"] is False
