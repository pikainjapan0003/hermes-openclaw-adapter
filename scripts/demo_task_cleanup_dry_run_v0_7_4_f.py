"""v0.7.4-F — Safe Local Cleanup Tool CLI（dry-run-only）。

讀取使用者**明確傳入**的 synthetic JSON input，產生 demo task cleanup dry-run
candidate report，並只輸出 JSON 到 stdout。

本 CLI 是 dry-run-only：
  - 必須有 --input；沒有 --input 直接失敗。
  - 只讀使用者明確傳入的 JSON 檔；不讀真實 queue DB、不預設掃 queue。
  - 不修改任何資料、不刪除 task、不 archive task、不寫 output file（只寫 stdout）。
  - 不提供 apply path。若 argv 出現 --apply / --confirm-apply / 任何含 "apply" 的引數，
    立即 exit nonzero 並顯示 blocked，不做任何事。
  - 不 POST、不啟動 Worker、不呼叫 OpenClaw / Hermes / Google Sheets、不讀 secrets。

用法：
  python scripts/demo_task_cleanup_dry_run_v0_7_4_f.py \\
    --input /path/to/tasks.json \\
    --source-queue synthetic \\
    --target-environment local
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# 讓 CLI 能 import 純 helper（app 套件）。
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from app.demo_task_cleanup_v0_7 import (  # noqa: E402
    derive_demo_task_cleanup_dry_run_report,
)

# v0.7.4-F 沒有 apply path：任何 apply-like 引數一律拒絕。
_APPLY_BLOCKED_MESSAGE = (
    "blocked: apply path is not supported in v0.7.4-F (dry-run only). "
    "No apply, no deletion, no archive, no queue write was performed."
)


def _reject_apply_like_arguments(argv: list[str]) -> None:
    """若 argv 出現 --apply / --confirm-apply / 任何含 'apply' 的引數 → exit nonzero。

    在做任何其它事情之前先檢查；拒絕時不讀檔、不產報表、不修改任何資料。
    """
    for token in argv:
        if isinstance(token, str) and "apply" in token.strip().lower():
            print(_APPLY_BLOCKED_MESSAGE, file=sys.stderr)
            sys.exit(2)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Safe Local Cleanup Tool (v0.7.4-F) — dry-run-only candidate report.",
        add_help=True,
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to an explicit synthetic JSON input file (list of tasks or {\"tasks\": [...]}).",
    )
    parser.add_argument(
        "--source-queue",
        default="synthetic",
        help="Label for the source queue (informational only; no real queue is read).",
    )
    parser.add_argument(
        "--target-environment",
        default="local",
        help="Target environment label; only 'local' or 'preview' yield candidates.",
    )
    return parser


def _load_tasks_from_json(input_path: str) -> list:
    """只讀使用者明確傳入的 JSON 檔（list 或 {"tasks": [...]}）。不讀真實 queue DB。"""
    path = Path(input_path)
    if not path.is_file():
        print(f"error: --input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, ValueError) as exc:
        print(f"error: could not parse --input JSON: {exc}", file=sys.stderr)
        sys.exit(1)
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and isinstance(data.get("tasks"), list):
        return data["tasks"]
    print("error: --input JSON must be a list of tasks or {\"tasks\": [...]}.", file=sys.stderr)
    sys.exit(1)


def main(argv: list[str] | None = None) -> int:
    args_list = list(sys.argv[1:] if argv is None else argv)

    # 先擋掉所有 apply-like 引數（dry-run-only，無 apply path）。
    _reject_apply_like_arguments(args_list)

    parser = _build_parser()
    args = parser.parse_args(args_list)

    tasks = _load_tasks_from_json(args.input)
    report = derive_demo_task_cleanup_dry_run_report(
        tasks,
        source_queue=args.source_queue,
        target_environment=args.target_environment,
    )

    # 只輸出 JSON report 到 stdout（不寫 output file）。
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
