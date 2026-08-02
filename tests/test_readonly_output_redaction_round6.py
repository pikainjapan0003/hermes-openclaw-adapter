"""Round 6 no-extra-leak checks for renderer and mirror stdout."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_mirror_drift_readonly import compare_mirror, render_report
from scripts.render_schema_docs_readonly import render_schema_markdown


pytestmark = pytest.mark.contract
SECRET = "FAKE-SECRET-ROUND6-MUST-NOT-ECHO"
ABSOLUTE = "C:/synthetic/private/environment/path"


def test_renderer_does_not_echo_nonpresented_schema_metadata() -> None:
    rendered = render_schema_markdown(
        {
            "title": "Public synthetic schema",
            "type": "object",
            "$comment": SECRET,
            "properties": {
                "nullable": {
                    "oneOf": [{"type": "string"}, {"type": "null"}],
                    "$comment": SECRET,
                    "examples": [SECRET],
                    "default": ABSOLUTE,
                }
            },
        },
        "public.schema.json",
    )

    assert "| `nullable` | string | null |" in rendered
    assert SECRET not in rendered
    assert ABSOLUTE not in rendered


def test_mirror_report_omits_raw_content_and_absolute_roots(tmp_path: Path) -> None:
    repo = tmp_path / f"repo-{SECRET}"
    mirror = tmp_path / f"mirror-{SECRET}"
    repo.mkdir()
    mirror.mkdir()
    (repo / "safe.md").write_text(SECRET + ABSOLUTE, encoding="utf-8")
    (mirror / "safe.md").write_text("different private body", encoding="utf-8")

    rendered = render_report(compare_mirror(repo, mirror))

    assert "DIFFERS | safe.md |" in rendered
    assert SECRET not in rendered
    assert ABSOLUTE not in rendered
    assert str(repo.resolve()) not in rendered
    assert str(mirror.resolve()) not in rendered
