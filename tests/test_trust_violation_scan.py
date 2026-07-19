"""Permanent static guards for trust-boundary regressions.

This complements the queue-claim guard.  It does not authorize any legacy POST
route or execution path; it freezes the current inventory and fails if new code
introduces a non-null execution token, the Phase 7 audit target, a new POST
surface, or an approve-to-dispatch call path.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parent.parent
APP_DIR = ROOT / "app"
APPROVAL_SCHEMA = (
    ROOT / "docs" / "schemas" / "blackboard" / "approval_packet.schema.json"
)
TOKEN_FIELD = "single_use_execution_token"
AUDIT_TARGET = "data/audit_dev.jsonl"

KNOWN_POST_ROUTES = {
    ("app/main.py", "/tasks/dispatch"),
    ("app/main.py", "/tasks/{task_id}/cancel"),
    ("app/main.py", "/tasks/{task_id}/retry"),
    ("app/main.py", "/tasks/{task_id}/archive"),
    ("app/main.py", "/tasks/{task_id}/comments"),
    ("app/main.py", "/tasks/{task_id}/approve"),
    ("app/main.py", "/tasks/{task_id}/reject"),
    ("app/main.py", "/dashboard/login"),
    ("app/main.py", "/dashboard/tasks/{task_id}/comments"),
    ("app/main.py", "/dashboard/tasks/{task_id}/approve"),
    ("app/main.py", "/dashboard/tasks/{task_id}/reject"),
    ("app/main.py", "/dashboard/tasks/{task_id}/cancel"),
    ("app/main.py", "/dashboard/tasks/{task_id}/retry"),
    ("app/main.py", "/dashboard/tasks/{task_id}/archive"),
}

APPROVE_DISPATCH_CALLS = {
    "add_task",
    "claim_next",
    "create_task",
    "dispatch_task",
    "enqueue",
    "execute",
    "run_forever",
    "run_openclaw_and_callback",
    "run_openclaw_cli",
    "send_callback_to_hermes",
    "start",
}


def _app_sources() -> dict[str, str]:
    return {
        path.relative_to(ROOT).as_posix(): path.read_text(encoding="utf-8")
        for path in sorted(APP_DIR.rglob("*.py"))
    }


def _literal_text(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _is_none(node: ast.AST | None) -> bool:
    return isinstance(node, ast.Constant) and node.value is None


def _subscript_key(node: ast.AST) -> str | None:
    if not isinstance(node, ast.Subscript):
        return None
    return _literal_text(node.slice)


def _token_ast_violations(source: str, filename: str) -> list[str]:
    tree = ast.parse(source, filename=filename)
    violations: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            for key, value in zip(node.keys, node.values):
                if _literal_text(key) == TOKEN_FIELD and not _is_none(value):
                    violations.append(
                        f"{filename}:{node.lineno}: non-null {TOKEN_FIELD} dict value"
                    )

        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets: Iterable[ast.AST]
            if isinstance(node, ast.Assign):
                targets = node.targets
            else:
                targets = (node.target,)
            if any(_subscript_key(target) == TOKEN_FIELD for target in targets):
                if not _is_none(node.value):
                    violations.append(
                        f"{filename}:{node.lineno}: non-null {TOKEN_FIELD} assignment"
                    )

        if not isinstance(node, ast.Call):
            continue
        for keyword in node.keywords:
            if keyword.arg == TOKEN_FIELD and not _is_none(keyword.value):
                violations.append(
                    f"{filename}:{node.lineno}: non-null {TOKEN_FIELD} keyword"
                )
        if not isinstance(node.func, ast.Attribute):
            continue
        if node.func.attr == "setdefault" and len(node.args) >= 2:
            if _literal_text(node.args[0]) == TOKEN_FIELD and not _is_none(node.args[1]):
                violations.append(
                    f"{filename}:{node.lineno}: non-null {TOKEN_FIELD} setdefault"
                )
        if node.func.attr == "update":
            for keyword in node.keywords:
                if keyword.arg == TOKEN_FIELD and not _is_none(keyword.value):
                    violations.append(
                        f"{filename}:{node.lineno}: non-null {TOKEN_FIELD} update"
                    )

    return violations


def _token_text_occurrences(sources: dict[str, str]) -> set[tuple[str, str]]:
    return {
        (filename, line.strip())
        for filename, source in sources.items()
        for line in source.splitlines()
        if TOKEN_FIELD in line
    }


def _audit_text_violations(sources: dict[str, str]) -> list[str]:
    violations: list[str] = []
    for filename, source in sources.items():
        if filename.endswith("/audit_writer_local.py"):
            violations.append(f"{filename}: forbidden audit writer module")
        for line_number, line in enumerate(source.splitlines(), start=1):
            if AUDIT_TARGET in line.replace("\\", "/"):
                violations.append(
                    f"{filename}:{line_number}: forbidden audit target reference"
                )
    return violations


def _post_routes(sources: dict[str, str]) -> set[tuple[str, str]]:
    routes: set[tuple[str, str]] = set()
    for filename, source in sources.items():
        tree = ast.parse(source, filename=filename)
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for decorator in node.decorator_list:
                if not isinstance(decorator, ast.Call):
                    continue
                if not isinstance(decorator.func, ast.Attribute):
                    continue
                if decorator.func.attr.lower() != "post":
                    continue
                path = _literal_text(decorator.args[0]) if decorator.args else None
                routes.add((filename, path or "<dynamic-post-path>"))
    return routes


def _call_name(call: ast.Call) -> str | None:
    if isinstance(call.func, ast.Name):
        return call.func.id
    if isinstance(call.func, ast.Attribute):
        return call.func.attr
    return None


def _is_approve_post(function: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    for decorator in function.decorator_list:
        if not isinstance(decorator, ast.Call):
            continue
        if not isinstance(decorator.func, ast.Attribute):
            continue
        if decorator.func.attr.lower() != "post" or not decorator.args:
            continue
        route = _literal_text(decorator.args[0])
        if route and route.endswith("/approve"):
            return True
    return False


def _approve_dispatch_violations(source: str, filename: str) -> list[str]:
    """Walk same-module helpers reachable from an approve POST function."""

    tree = ast.parse(source, filename=filename)
    functions = {
        node.name: node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    pending = [node.name for node in functions.values() if _is_approve_post(node)]
    visited: set[str] = set()
    violations: list[str] = []

    while pending:
        function_name = pending.pop()
        if function_name in visited:
            continue
        visited.add(function_name)
        function = functions[function_name]
        for node in ast.walk(function):
            if not isinstance(node, ast.Call):
                continue
            call_name = _call_name(node)
            if call_name in APPROVE_DISPATCH_CALLS:
                violations.append(
                    f"{filename}:{node.lineno}: approve path reaches {call_name}(...)"
                )
            if isinstance(node.func, ast.Name) and node.func.id in functions:
                pending.append(node.func.id)

    return violations


def test_execution_token_remains_null_in_schema_ast_and_source_text() -> None:
    schema = json.loads(APPROVAL_SCHEMA.read_text(encoding="utf-8"))
    token_schema = schema["properties"][TOKEN_FIELD]
    assert token_schema["type"] == "null"
    assert token_schema["const"] is None

    sources = _app_sources()
    ast_violations = [
        violation
        for filename, source in sources.items()
        for violation in _token_ast_violations(source, filename)
    ]
    assert ast_violations == []
    assert _token_text_occurrences(sources) == {
        ("app/approval_packet_builder.py", '"single_use_execution_token": None,')
    }


def test_no_phase7_audit_writer_or_audit_dev_target_exists_in_app() -> None:
    assert _audit_text_violations(_app_sources()) == []
    assert not (APP_DIR / "audit_writer_local.py").exists()


def test_post_route_inventory_is_exact_and_rejects_new_surface() -> None:
    assert _post_routes(_app_sources()) == KNOWN_POST_ROUTES


def test_approve_routes_have_no_reachable_dispatch_or_execution_call() -> None:
    violations = [
        violation
        for filename, source in _app_sources().items()
        for violation in _approve_dispatch_violations(source, filename)
    ]
    assert violations == []


def test_injected_trust_violations_are_detected() -> None:
    token_source = f'packet = {{"{TOKEN_FIELD}": "live-token"}}\n'
    assert _token_ast_violations(token_source, "token_example.py")
    assert _token_text_occurrences({"token_example.py": token_source})

    audit_source = f'open("{AUDIT_TARGET}", "a")\n'
    assert _audit_text_violations({"app/audit_example.py": audit_source})

    new_post_source = '@app.post("/new-write")\ndef new_write():\n    return None\n'
    assert _post_routes({"app/new_route.py": new_post_source}) == {
        ("app/new_route.py", "/new-write")
    }
    assert _post_routes({"app/new_route.py": new_post_source}) - KNOWN_POST_ROUTES

    dispatch_source = (
        '@app.post("/tasks/{task_id}/approve")\n'
        "def unsafe_approve(task_id):\n"
        "    dispatch_task(task_id)\n"
    )
    assert _approve_dispatch_violations(dispatch_source, "approve_example.py")
