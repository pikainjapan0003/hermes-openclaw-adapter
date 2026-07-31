"""Executable schema checks for the three-source tool's real JSON stdout."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from scripts import check_three_source_readonly as checker


pytestmark = pytest.mark.contract

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "docs" / "schemas" / "three_source_report.schema.json"
LOCAL_HASH = "a" * 40


def _schema() -> dict[str, object]:
    loaded = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    Draft202012Validator.check_schema(loaded)
    return loaded


@pytest.mark.parametrize(
    ("verdict", "local", "github", "replit", "exit_code"),
    [
        ("ALIGNED", LOCAL_HASH, LOCAL_HASH, "REACHABLE", 0),
        ("DRIFT", LOCAL_HASH, "b" * 40, "REACHABLE", 1),
        ("INCOMPLETE", LOCAL_HASH, "UNREACHABLE", "UNREACHABLE", 2),
    ],
)
def test_real_json_stdout_conforms_for_every_verdict(
    verdict: str,
    local: str,
    github: str,
    replit: str,
    exit_code: int,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    report = checker.ThreeSourceReport(
        checker.SourceState("local", local, "synthetic local detail"),
        checker.SourceState("github", github, "synthetic GitHub detail"),
        checker.SourceState("replit", replit, "synthetic Replit detail"),
        verdict,
    )
    monkeypatch.setattr(
        checker,
        "check_three_sources",
        lambda *_args, **_kwargs: report,
    )

    assert checker.main(["--repo", ".", "--json"]) == exit_code
    payload = json.loads(capsys.readouterr().out)
    Draft202012Validator(_schema()).validate(payload)

    assert payload["sources"]["replit"]["deployed_hash"] is None
    assert payload["sources"]["replit"]["deployed_hash_status"] == "UNKNOWN"
    assert payload["sources"]["replit"]["deployed_hash_verified"] is False


def test_schema_rejects_missing_or_claimed_replit_hash_state() -> None:
    payload = checker.report_as_json(
        checker.ThreeSourceReport(
            checker.SourceState("local", LOCAL_HASH, "local"),
            checker.SourceState("github", LOCAL_HASH, "github"),
            checker.SourceState("replit", "REACHABLE", "HTTP 200"),
            "ALIGNED",
        )
    )
    validator = Draft202012Validator(_schema())

    for field in (
        "deployed_hash",
        "deployed_hash_status",
        "deployed_hash_verified",
    ):
        mutation = json.loads(json.dumps(payload))
        del mutation["sources"]["replit"][field]
        assert list(validator.iter_errors(mutation)), field

    claimed = json.loads(json.dumps(payload))
    claimed["sources"]["replit"].update(
        {
            "deployed_hash": LOCAL_HASH,
            "deployed_hash_status": "VERIFIED",
            "deployed_hash_verified": True,
        }
    )
    assert list(validator.iter_errors(claimed))

