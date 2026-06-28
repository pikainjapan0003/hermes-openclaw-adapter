#!/usr/bin/env python3
"""DEMO ONLY / LOCAL ONLY — seed a single demo waiting_review task so the Owner
can see the Owner 審核面板 on /dashboard/tasks/{id} in Replit Preview.

v0.7.2-UI-E-B-R.

SAFETY MODEL (read before使用):
  - 預設 dry-run：不寫入任何 queue，只印出將會建立的 demo 任務內容。
  - 僅在同時給 --apply --confirm-local-demo-write 時，才會透過 QueueStore.enqueue
    寫入「一筆」demo 任務（status=waiting_review）。
  - 本腳本是 LOCAL ONLY 的視覺 demo 夾具，不是功能接線。
  - 本腳本不會啟動背景執行器、不會呼叫 OpenClaw、不會呼叫 Hermes、不會寫
    Google Sheets、不會讀 secrets、不會建立任何外部回呼、不會連外部網路。
  - 不會把任務轉成 running / completed，不會自動核准或拒絕。
  - import 時不做任何寫入（所有動作都在 main() 內、且需明確 flags）。
  - cleanup 僅針對 task_id 前綴 demo-ui-e-b-review-，不會動到其他任務。
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

DEMO_PREFIX = "demo-ui-e-b-review-"
DEMO_TASK_ID = DEMO_PREFIX + "001"
DEMO_TITLE = "DEMO ONLY - Owner 審核面板視覺測試"
DEMO_SAFETY_LEVEL = 3
DEMO_TASK_TEXT = (
    "DEMO ONLY / LOCAL ONLY：這是 v0.7.2-UI-E-B-R 的視覺 demo 任務，"
    "只是為了讓 Owner 在 Replit Preview 看到 /dashboard/tasks/{id} 的 Owner 審核面板。"
    "本任務不會被執行、不會呼叫任何外部工具、不會改動其他任務。"
)
DEMO_PAYLOAD = {
    "title": DEMO_TITLE,
    "metadata": {
        "safety_level": DEMO_SAFETY_LEVEL,
        "requires_confirmation": True,
        "demo_only": True,
        "local_only": True,
        "note": "DEMO ONLY local-only review fixture; not executable.",
    },
}


def _print_demo_plan() -> None:
    print("===== DEMO ONLY / LOCAL ONLY review task fixture =====")
    print(f"  task_id              : {DEMO_TASK_ID}")
    print(f"  status               : waiting_review")
    print(f"  safety_level         : {DEMO_SAFETY_LEVEL}")
    print(f"  requires_confirmation: True")
    print(f"  title                : {DEMO_TITLE}")
    print(f"  task_text            : {DEMO_TASK_TEXT}")
    print("=======================================================")


def _seed(apply_write: bool) -> int:
    """Dry-run 印出計畫；apply_write=True 才透過 QueueStore.enqueue 實際寫入。"""
    _print_demo_plan()
    if not apply_write:
        print("\n[dry-run] 未寫入任何 queue。若要實際建立，請加上："
              "\n  --apply --confirm-local-demo-write")
        return 0

    # 只有在明確確認後才 import app 並寫入 queue（避免 import 副作用）。
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from app import main  # noqa: PLC0415

    queue = main.get_queue()
    existing = queue.get(DEMO_TASK_ID)
    if existing is not None:
        print(f"\n[apply] demo 任務已存在（{DEMO_TASK_ID}, status={existing.get('status')}），"
              "不重複建立。")
        return 0

    created = queue.enqueue(
        task_id=DEMO_TASK_ID,
        title=DEMO_TITLE,
        task_text=DEMO_TASK_TEXT,
        safety_level=DEMO_SAFETY_LEVEL,
        payload=DEMO_PAYLOAD,
        initial_status="waiting_review",
    )
    if created is None:
        print("\n[apply] enqueue 回傳 None（可能被 INSERT OR IGNORE 略過）。")
        return 1
    print(f"\n[apply] 已建立 demo waiting_review 任務：{DEMO_TASK_ID}")
    print("提示：到 /dashboard/reviews 或 /dashboard/tasks/" + DEMO_TASK_ID
          + " 查看 Owner 審核面板。")
    return 0


def _cleanup(apply_write: bool) -> int:
    """只清理 demo-ui-e-b-review- 前綴的任務。

    QueueStore 目前沒有安全的刪除 API；為避免繞過 QueueStore 亂寫檔，
    本腳本不會自行刪除任務，只會列出符合前綴的 demo 任務並請 Owner 手動處理。
    """
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from app import main  # noqa: PLC0415

    queue = main.get_queue()
    item = queue.get(DEMO_TASK_ID)
    print("===== cleanup（僅限 demo-ui-e-b-review- 前綴）=====")
    if item is None:
        print(f"  無 demo 任務 {DEMO_TASK_ID}，無需清理。")
        return 0
    print(f"  發現 demo 任務：{DEMO_TASK_ID}（status={item.get('status')}）")
    print("  QueueStore 無安全刪除 API；為不繞過 QueueStore，本腳本不自行刪除。")
    print("  請由 Owner 以受控方式處理此 demo-only 任務。")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="DEMO ONLY / LOCAL ONLY: seed one waiting_review demo task "
                    "for Owner 審核面板 視覺驗收。預設 dry-run。",
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="（預設行為）只印出將建立的 demo 任務，不寫入。")
    parser.add_argument("--apply", action="store_true",
                        help="實際寫入 demo 任務（需同時加 --confirm-local-demo-write）。")
    parser.add_argument("--cleanup", action="store_true",
                        help="列出 demo-ui-e-b-review- 前綴任務（不自行刪除）。")
    parser.add_argument("--confirm-local-demo-write", action="store_true",
                        help="確認這是 local-only demo 寫入；與 --apply 一起使用。")
    args = parser.parse_args(argv)

    print("DEMO ONLY / LOCAL ONLY — Owner 審核面板 視覺 demo 夾具 (v0.7.2-UI-E-B-R)")

    if args.cleanup:
        if not args.confirm_local_demo_write:
            print("\n[cleanup] 需要 --confirm-local-demo-write 才會進行 cleanup 檢視。")
            return 0
        return _cleanup(apply_write=True)

    apply_write = bool(args.apply and args.confirm_local_demo_write)
    if args.apply and not args.confirm_local_demo_write:
        print("\n[拒絕] --apply 必須與 --confirm-local-demo-write 同時使用；本次不寫入。")
        return 2
    return _seed(apply_write=apply_write)


if __name__ == "__main__":
    raise SystemExit(main())
