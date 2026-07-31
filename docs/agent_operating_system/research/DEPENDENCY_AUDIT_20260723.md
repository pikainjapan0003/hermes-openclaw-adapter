# Dependency Audit — 2026-07-23

Status: read-only audit; no requirement file was changed.

Environment measured: isolated WSL virtualenv `/tmp/hermes-nb10-venv`.
Commands: `python -m pip list --format=freeze`, repository import scan over
`app/`, `scripts/`, and `tests/`, and direct comparison with
`requirements.txt`, `requirements-dev.txt`, and `pyproject.toml`.

## Declared direct dependencies

All entries in both requirements files use exact `==` pins.

| File | Direct entries |
|---|---|
| `requirements.txt` | fastapi 0.115.6; uvicorn[standard] 0.32.1; httpx 0.28.1; pydantic 2.10.4; python-dotenv 1.0.1; jinja2 3.1.4; python-multipart 0.0.32; jsonschema 4.26.0; google-auth-oauthlib 1.2.1; google-api-python-client 2.149.0 |
| `requirements-dev.txt` | pytest 9.1.1; pytest-cov 7.1.0; mypy 2.3.0; types-jsonschema 4.26.0.20260518 |

Unpinned direct requirements: **none**. Transitive packages are not locked in
these files, so exact environment reproduction still depends on resolver time.

## Declared versus imported

| Finding | Result |
|---|---|
| Product imports with matching direct declaration | `fastapi`, `httpx`, `pydantic`, `dotenv`/python-dotenv, `jsonschema`; Jinja and multipart are runtime requirements used through FastAPI/Jinja integration. |
| Guarded live-only imports | `google.oauth2` and `googleapiclient` occur only as lazy imports in `app/google_sheets_oauth_writer.py`; their two direct distributions are declared. This audit did not modify or execute that module. |
| Dev imports with matching declaration | `pytest`, `pytest-cov` plugin use, mypy configuration, and types-jsonschema stubs. |
| Imported but not directly declared | No unresolved third-party import found in the scanned repository. |
| Declared but no literal direct import | `uvicorn` is the service runner; `python-multipart` supports FastAPI form parsing; `jinja2` is reached through FastAPI templating. These are operational dependencies, not unused declarations. |

## `pyproject.toml` drift

The `[project].dependencies` list matches only the original web-service subset.
It omits `jsonschema`, `google-auth-oauthlib`, and
`google-api-python-client`, even though `requirements.txt` declares them.
Dev dependencies are also represented only in `requirements-dev.txt`, not as a
`project.optional-dependencies` group. This is a packaging-metadata drift, not a
runtime failure in the requirements-based workflow.

## Installed environment

All 14 direct production/dev distributions are present at their declared
versions. Notable installed transitive packages include Starlette, AnyIO,
httpcore, google-auth, google-api-core, requests, oauthlib, coverage, pluggy,
and mypy's `ast_serialize`.

`PyYAML==6.0.3` is installed but no repository Python import of `yaml` was
found and `pip show` reported no reverse dependency in this environment. It is
the only clearly unexplained installed top-level distribution found by this
lightweight audit; it may be environment residue and is not added to either
requirements file.

## Risks and next action

- Exact top-level pins do not lock transitive versions; a later resolver run can
  select newer transitives.
- Installing from `pyproject.toml` alone produces a materially smaller
  environment than installing `requirements.txt`.
- A separately authorized packaging-maintenance package should choose one
  authority (lock file or synchronized pyproject/requirements) before changing
  dependency declarations.
