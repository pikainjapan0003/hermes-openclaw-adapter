"""Round-seven reverse checks for renderer and artifact-inventory errors."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.render_schema_docs_readonly import (
    render_schema_markdown,
    render_schema_tree,
)
from tests import test_artifact_integrity_v5 as inventory


pytestmark = pytest.mark.contract

SECRET = "FAKE-SECRET-ROUND7-MUST-NOT-ECHO"


def test_renderer_composite_branches_do_not_echo_hidden_metadata() -> None:
    rendered = render_schema_markdown(
        {
            "title": "Composite display",
            "type": "object",
            "properties": {
                "nullable": {
                    "oneOf": [
                        {"type": "string", "$comment": SECRET},
                        {"type": "null", "examples": [SECRET]},
                    ]
                },
                "intersection": {
                    "allOf": [
                        {"type": "string", "default": SECRET},
                        {"type": "number", "$comment": SECRET},
                    ]
                },
            },
        },
        "synthetic.schema.json",
    )

    assert "| `nullable` | string | null |" in rendered
    assert "| `intersection` | string & number |" in rendered
    assert SECRET not in rendered


def test_renderer_invalid_root_error_does_not_echo_raw_payload(
    tmp_path: Path,
) -> None:
    schema_root = tmp_path / "schemas"
    schema_root.mkdir()
    (schema_root / "invalid.json").write_text(
        json.dumps([SECRET]), encoding="utf-8"
    )

    with pytest.raises(ValueError) as caught:
        render_schema_tree(schema_root)

    message = str(caught.value)
    assert "schema root must be an object" in message
    assert SECRET not in message


def test_artifact_inventory_bare_cr_payload_exposure_is_explicitly_detected(
    tmp_path: Path,
) -> None:
    artifact = tmp_path / "artifact.txt"
    artifact.write_bytes((SECRET + "\r").encode("utf-8"))

    with pytest.raises(AssertionError) as caught:
        inventory._normalized_bytes(artifact)

    # Pytest assertion rewriting includes the failing bytes expression. This
    # local-only exposure is recorded as ESR7-02 and must not be published.
    assert SECRET in str(caught.value)


def test_artifact_inventory_missing_path_exposure_is_explicitly_detected(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    secret_root = tmp_path / SECRET
    secret_root.mkdir()
    monkeypatch.setattr(inventory, "ROOT", secret_root)

    with pytest.raises(FileNotFoundError) as caught:
        inventory._manifest_digest({"missing-artifact.txt"})

    # This local test-tool path exposure is also recorded as ESR7-02. It must
    # not be wired to a remote/dashboard surface.
    assert SECRET in str(caught.value)
