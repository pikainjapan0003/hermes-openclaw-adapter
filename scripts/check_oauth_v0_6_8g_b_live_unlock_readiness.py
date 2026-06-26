#!/usr/bin/env python3
"""v0.6.8G-B — Live Consent Unlock 靜態 + fake-flow 檢查（永不連真 Google、不讀 .env、不碰真 token）。

驗證 helper 已 unlock guarded local consent，且整套 guard 正確：
- helper 不再靠永久 kill-switch；改靠 explicit Owner flags + local-only + file validation +
  token display acknowledgement。
- no-arg / dry-run / explain 正常（exit 0）。
- --live 缺旗標、缺檔、非本機環境、repo 內檔、service_account、my-openclaw 檔名 → 拒絕。
- 未帶 --show-refresh-token-once 時不輸出 refresh token（只 present: YES/NO）。
- 帶 --show-refresh-token-once 但缺 --i-understand-token-will-be-visible → 拒絕。
- fake flow + show-once + ack → 只顯示 fake refresh token，**不**顯示 fake access token。
- helper 不寫 token file、不讀 .env、不含 Owner 真路徑。

所有「跑 flow」的測試都 monkeypatch helper 的 _obtain_credentials，注入 fake 憑證，
因此**永不**連真 Google、**永不**開瀏覽器、**永不**使用 Owner 真 JSON。回傳 0/1。
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

# 以 chr(92) 組裝禁用路徑樣式，避免本腳本原始碼出現真路徑字面。
BS = chr(92)
BAD_USER_PATH = "C:" + BS + "Users" + BS + "Lnovo"
BAD_SECRETS_PATH = "Desktop" + BS + "secrets"

# 測試用 fake 憑證值（大寫，刻意不符合敏感掃描的小寫 token 樣式）。
FAKE_REFRESH = "FAKE_REFRESH_TOKEN_FOR_TEST_ONLY"
FAKE_ACCESS = "FAKE_ACCESS_TOKEN_MUST_NOT_BE_SHOWN"

FAKE_INSTALLED = {"installed": {"client_id": "fake.apps.googleusercontent.com",
                                "client_secret": "FAKE_NOT_A_REAL_SECRET",
                                "redirect_uris": ["http://localhost"]}}
FAKE_WEB = {"web": {"client_id": "fake", "client_secret": "FAKE"}}
FAKE_SA = {"type": "service_account", "client_email": "fake@fake.iam.gserviceaccount.com",
           "private_key": "FAKE_NOT_A_REAL_KEY"}

FAILURES: list[str] = []


def _check(cond: bool, label: str) -> None:
    print(f"  {'ok ' if cond else '❌ '}: {label}")
    if not cond:
        FAILURES.append(label)


def _write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data), encoding="utf-8")


class _FakeCreds:
    def __init__(self) -> None:
        self.refresh_token = FAKE_REFRESH
        self.token = FAKE_ACCESS
        self.scopes = ["https://www.googleapis.com/auth/spreadsheets"]


def _capture(fn) -> tuple[int, str]:
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        rc = fn()
    return rc, out.getvalue()


def main() -> int:
    helper = SCRIPTS / "oauth_local_consent_helper.py"
    src = helper.read_text(encoding="utf-8") if helper.is_file() else ""
    lower = src.lower()

    try:
        import oauth_local_consent_helper as H
    except Exception as exc:  # pragma: no cover
        print(f"❌ 無法 import helper：{exc}")
        return 1

    print("[1] helper 不再靠永久 kill-switch，改靠 explicit Owner flags")
    _check("DEFAULT_DRY_RUN = True" in src, "helper 預設 dry-run")
    _check("LIVE_CONSENT_ENABLED = False" not in src,
           "helper 不再保留永久 kill-switch（無 LIVE_CONSENT_ENABLED = False）")
    _check("--i-understand-local-only" in src and "--client-secret-file" in src
           and "--show-refresh-token-once" in src and "--i-understand-token-will-be-visible" in src,
           "helper 具備完整 explicit Owner 風險旗標")

    print("[2] no-arg / dry-run / explain 正常（exit 0）")
    rc, _ = _capture(lambda: H.main([]))
    _check(rc == 0, "no-arg → exit 0")
    rc, _ = _capture(lambda: H.main(["--dry-run"]))
    _check(rc == 0, "--dry-run → exit 0")
    rc, _ = _capture(lambda: H.main(["--explain"]))
    _check(rc == 0, "--explain → exit 0")

    print("[3] --live 缺旗標會拒絕（exit 2）")
    rc, _ = _capture(lambda: H.main(["--live"]))
    _check(rc == 2, "--live 缺 --i-understand-local-only → exit 2")
    rc, _ = _capture(lambda: H.main(["--live", "--i-understand-local-only"]))
    _check(rc == 2, "--live 缺 --client-secret-file → exit 2")

    # 準備 fixtures（repo 外）。
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        good = tdp / "oauth-client.json"; _write_json(good, FAKE_INSTALLED)
        sa = tdp / "sa.json"; _write_json(sa, FAKE_SA)
        web = tdp / "web.json"; _write_json(web, FAKE_WEB)
        myopen = tdp / "my-openclaw-foo.json"; _write_json(myopen, FAKE_INSTALLED)

        print("[4] Replit / CI 環境會拒絕 live（exit 2）")
        os.environ["REPL_ID"] = "fake-repl"
        try:
            rc, _ = _capture(lambda: H._run_live_guarded(str(good)))
            _check(rc == 2, "偵測到 Replit 環境 → exit 2")
        finally:
            os.environ.pop("REPL_ID", None)

        print("[5] 檔案驗證：repo 內 / service_account / my-openclaw 拒絕，installed 通過")
        repo_fixture = ROOT / "_gb_fixture_client.json"
        try:
            _write_json(repo_fixture, FAKE_INSTALLED)
            rc, _ = _capture(lambda: H._run_live_guarded(str(repo_fixture)))
            _check(rc == 2, "repo 內 client secret → exit 2")
        finally:
            if repo_fixture.exists():
                repo_fixture.unlink()
        rc, _ = _capture(lambda: H._run_live_guarded(str(sa)))
        _check(rc == 2, "service_account JSON → exit 2")
        rc, _ = _capture(lambda: H._run_live_guarded(str(myopen)))
        _check(rc == 2, "my-openclaw*.json 檔名 → exit 2")
        ok, _reason = H._validate_client_secret_file(str(good))
        _check(ok, "installed fake JSON 通過前置驗證")
        ok, _reason = H._validate_client_secret_file(str(web))
        _check(not ok, "web client JSON → 驗證拒絕")

        # 後續 flow 測試：monkeypatch _obtain_credentials，跳過 countdown。
        H._obtain_credentials = lambda path: _FakeCreds()
        H.SHOW_TOKEN_COUNTDOWN_SECONDS = 0

        print("[6] 未帶 --show-refresh-token-once：不輸出真 token，只回報 present")
        rc, out = _capture(lambda: H._run_live_guarded(str(good)))
        _check(rc == 0, "fake flow（不顯示）→ exit 0")
        _check("refresh token present: YES" in out, "回報 refresh token present: YES")
        _check(FAKE_REFRESH not in out, "未帶 show-once 時不輸出 refresh token 值")
        _check(FAKE_ACCESS not in out, "未輸出 access token 值")

        print("[7] --show-refresh-token-once 缺 ack → 拒絕（exit 2），不顯示 token")
        rc, out = _capture(lambda: H._run_live_guarded(
            str(good), show_refresh_token_once=True, understand_token_visible=False))
        _check(rc == 2, "show-once 缺 ack → exit 2")
        _check(FAKE_REFRESH not in out, "拒絕時不顯示 refresh token")

        print("[8] fake flow + show-once + ack → 只顯示 fake refresh token，不顯示 access token")
        rc, out = _capture(lambda: H._run_live_guarded(
            str(good), show_refresh_token_once=True, understand_token_visible=True))
        _check(rc == 0, "show-once + ack（fake）→ exit 0")
        _check(FAKE_REFRESH in out, "show-once 顯示 fake refresh token")
        _check(FAKE_ACCESS not in out, "show-once 仍不顯示 access token")

    print("[9] helper 不寫 token file / 不讀 .env / 不含 Owner 真路徑")
    for bad in ("token.json", "token.pickle", "credentials.json", ".write_text(",
                "open(\"token", "open('token", "write_token"):
        _check(bad not in lower, f"helper 無寫 token 檔樣式（{bad}）")
    _check("load_dotenv" not in lower, "helper 不使用 load_dotenv（不讀 .env）")
    _check(BAD_USER_PATH not in src, "helper 不含使用者目錄真路徑")
    _check(BAD_SECRETS_PATH not in src, "helper 不含 Desktop secrets 真路徑")
    # access token 不得被 print（只允許 present 判斷）。
    for bad_print in ("print(creds.token)", "print(access_token", "print(creds.token,"):
        _check(bad_print not in lower, f"helper 不 print access token（{bad_print}）")

    print("[10] v0.6.8G-B 文件存在")
    _check((ROOT / "docs" / "HERMES_OPENCLAW_OAUTH_V0_6_8G_B_LIVE_CONSENT_UNLOCK.md").is_file(),
           "docs/HERMES_OPENCLAW_OAUTH_V0_6_8G_B_LIVE_CONSENT_UNLOCK.md 存在")

    if FAILURES:
        print(f"\n❌ v0.6.8G-B live unlock readiness 檢查失敗 {len(FAILURES)} 項：")
        for f in FAILURES:
            print(f"   - {f}")
        return 1
    print("\n✅ v0.6.8G-B live unlock readiness 全數通過（fake flow only，沒有連真 Google）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
