#!/usr/bin/env python3
"""v0.6.4 — Dashboard Auth Gate 測試。

完全離線。用 importlib.reload 在三種 DASHBOARD_AUTH_ENABLED 狀態下重建 app：
1. auth=false → 舊行為不變（Dashboard 直接可進、控制表單可用）。
2. auth=true 但無 token/cookie → 頁面 redirect 到 login、控制 POST 回 401。
3. auth=true + 正確 token → 登入後頁面可進、控制 POST 通過 gate 且狀態規則不變。

不啟動 worker、不呼叫真實 OpenClaw、不改 .env。
"""

from __future__ import annotations

import importlib
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient  # noqa: E402

FAILURES: list[str] = []


def _check(cond: bool, label: str) -> None:
    if cond:
        print(f"  ok: {label}")
    else:
        print(f"  ❌ FAIL: {label}")
        FAILURES.append(label)


def _load(auth_enabled: str, token: str):
    """設定 env 後 (re)load app.main，回傳 module。每次用全新 tmp queue。"""
    tmp = tempfile.mkdtemp(prefix="authgate_")
    os.environ["EXECUTION_MODE"] = "queue"
    os.environ["DATA_DIR"] = tmp
    os.environ["QUEUE_DB_PATH"] = str(Path(tmp) / "queue.db")
    os.environ["HERMES_ADAPTER_TOKEN"] = ""
    os.environ["CALLBACK_ENABLED"] = "false"
    os.environ["OPENCLAW_CLI_BIN"] = "/nonexistent/openclaw-should-never-be-called"
    os.environ["DASHBOARD_AUTH_ENABLED"] = auth_enabled
    os.environ["DASHBOARD_TOKEN"] = token
    import app.main as m  # noqa: PLC0415
    importlib.reload(m)
    return m


def _seed_queued(m, tid: str) -> None:
    m.get_queue().enqueue(task_id=tid, title=tid, task_text="t", safety_level=0,
                          payload={"metadata": {}}, initial_status="queued")


def main_test() -> int:
    # === 情境 1：auth 關閉 → 舊行為 ===
    print("[1] DASHBOARD_AUTH_ENABLED=false → 舊行為不變")
    m = _load("false", "")
    c = TestClient(m.app)
    _seed_queued(m, "t1")
    _check(c.get("/dashboard").status_code == 200, "auth off：/dashboard 200")
    _check(c.get("/dashboard/tasks").status_code == 200, "auth off：/dashboard/tasks 200")
    _check(c.get("/dashboard/system").status_code == 200, "auth off：/dashboard/system 200")
    r = c.post("/dashboard/tasks/t1/cancel", data={"reason": "x"}, follow_redirects=False)
    _check(r.status_code == 303 and m.get_queue().get("t1")["status"] == "cancelled",
           "auth off：控制表單 cancel 可用（303 + cancelled）")
    _check(c.get("/dashboard/login", follow_redirects=False).status_code == 303,
           "auth off：/dashboard/login 直接 redirect 回 dashboard")

    # === 情境 2：auth 開啟、無憑證 → 擋下 ===
    print("[2] DASHBOARD_AUTH_ENABLED=true 且無 token/cookie → 擋下")
    m = _load("true", "secret-xyz")
    c = TestClient(m.app)
    _seed_queued(m, "t2")
    for path in ("/dashboard", "/dashboard/tasks", "/dashboard/tasks/t2",
                 "/dashboard/reviews", "/dashboard/system"):
        r = c.get(path, follow_redirects=False)
        _check(r.status_code == 303 and r.headers.get("location") == "/dashboard/login",
               f"auth on 無憑證：GET {path} → 303 → login")
    for path, data in (("/dashboard/tasks/t2/approve", {}),
                       ("/dashboard/tasks/t2/reject", {"reason": "n"}),
                       ("/dashboard/tasks/t2/cancel", {"reason": "n"}),
                       ("/dashboard/tasks/t2/retry", {}),
                       ("/dashboard/tasks/t2/archive", {}),
                       ("/dashboard/tasks/t2/comments",
                        {"author_type": "user", "author_name": "o", "content": "hi"})):
        r = c.post(path, data=data, follow_redirects=False)
        _check(r.status_code == 401, f"auth on 無憑證：POST {path} → 401")
    # 控制 POST 被擋後，任務狀態不可被改動
    _check(m.get_queue().get("t2")["status"] == "queued", "被擋的 POST 沒有改任務狀態")
    # login 頁本身豁免、可開
    _check(c.get("/dashboard/login").status_code == 200, "auth on：/dashboard/login 200（豁免）")
    # 錯誤 token（header）仍被擋
    r = c.get("/dashboard", headers={"X-Dashboard-Token": "wrong"}, follow_redirects=False)
    _check(r.status_code == 303, "auth on：錯誤 X-Dashboard-Token 仍被擋")

    # === 情境 3：auth 開啟 + 正確 token ===
    print("[3] DASHBOARD_AUTH_ENABLED=true + 正確 token → 通過")
    m = _load("true", "secret-xyz")
    c = TestClient(m.app)
    _seed_queued(m, "t3")
    # header token 路徑
    _check(c.get("/dashboard", headers={"X-Dashboard-Token": "secret-xyz"}).status_code == 200,
           "正確 X-Dashboard-Token：/dashboard 200")
    # 登入流程（cookie）
    r = c.post("/dashboard/login", data={"dashboard_token": "secret-xyz"}, follow_redirects=False)
    _check(r.status_code == 303 and "set-cookie" in {k.lower() for k in r.headers},
           "登入成功：303 + set-cookie")
    # TestClient 會保存 cookie → 後續請求帶 cookie
    _check(c.get("/dashboard").status_code == 200, "登入後：/dashboard 200")
    _check(c.get("/dashboard/system").status_code == 200, "登入後：/dashboard/system 200")
    # 控制 POST 通過 gate，且狀態規則仍正常（queued→cancelled）
    r = c.post("/dashboard/tasks/t3/cancel", data={"reason": "ok"}, follow_redirects=False)
    _check(r.status_code == 303 and m.get_queue().get("t3")["status"] == "cancelled",
           "登入後：控制 cancel 通過 gate 且 queued→cancelled")
    # 狀態規則沒被 gate 破壞：running 不能 cancel → 重新 seed 一個 running 測 409
    m.get_queue().enqueue(task_id="t3b", title="t", task_text="t", safety_level=0,
                          payload={"metadata": {}}, initial_status="queued")
    m.get_queue().claim_next()  # 變 running（最舊 queued）
    # claim 可能領到別筆；直接強制 t3b 設 running 以測 409
    conn = m.get_queue()._connect()
    conn.execute("UPDATE queue SET status='running' WHERE task_id='t3b'"); conn.commit(); conn.close()
    r = c.post("/dashboard/tasks/t3b/cancel", data={"reason": "no"}, follow_redirects=False)
    _check(r.status_code == 303 and m.get_queue().get("t3b")["status"] == "running",
           "登入後：running cancel 仍被狀態機擋（維持 running，gate 沒破壞規則）")
    # 登出清 cookie
    r = c.get("/dashboard/logout", follow_redirects=False)
    _check(r.status_code == 303, "logout：303")
    c.cookies.clear()
    _check(c.get("/dashboard", follow_redirects=False).status_code == 303,
           "登出後：/dashboard 又被擋")

    if FAILURES:
        print(f"\n❌ Dashboard Auth Gate 測試失敗 {len(FAILURES)} 項：")
        for f in FAILURES:
            print(f"   - {f}")
        return 1
    print("\n✅ Dashboard Auth Gate 測試全數通過。")
    return 0


if __name__ == "__main__":
    sys.exit(main_test())
