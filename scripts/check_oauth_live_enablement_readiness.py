#!/usr/bin/env python3
"""v0.6.8F — OAuth Live Helper Enablement 靜態 + fixture 檢查（不連 Google、不讀 .env、不印 secret）。

確認 v0.6.8F 的 guarded live 能力安全且未越界：
- helper 預設 dry-run、LIVE_CONSENT_ENABLED 仍為 False（最終 kill-switch）。
- `--live` 無安全旗標拒絕；live 需要 `--client-secret-file`。
- client secret 驗證（用 fake fixture，不碰 Owner 真檔）：
    * 合法 Desktop App（installed）→ 接受
    * service account JSON → 拒絕
    * my-openclaw*.json 檔名 → 拒絕
    * repo 內路徑 → 拒絕
    * web client → 拒絕
    * 不存在 → 拒絕
- helper 不讀 .env、不寫 token 檔、不 print refresh token 真值、無禁用旗標。
- dry-run 不在模組層 import google。
- 未修改 Worker / Queue / result_sink / app/main（git 工作區未顯示這些檔被改）。
- result_sink 仍不 import google；token / credential 未被 tracked；v0.6.8F 文件存在。

本腳本不讀 .env 真值、不輸出任何 secret value，回傳 0/1。
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

FAILURES: list[str] = []


def _check(cond: bool, label: str) -> None:
    print(f"  {'ok ' if cond else '❌ '}: {label}")
    if not cond:
        FAILURES.append(label)


def _tracked(pattern: str) -> bool:
    out = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", pattern],
        capture_output=True, text=True,
    ).stdout.strip()
    return bool(out)


def _modified(rel_path: str) -> bool:
    out = subprocess.run(
        ["git", "-C", str(ROOT), "status", "--porcelain", "--", rel_path],
        capture_output=True, text=True,
    ).stdout.strip()
    return bool(out)


# 假的 client secret 內容（純結構，無真值）。
FAKE_INSTALLED = {"installed": {"client_id": "fake.apps.googleusercontent.com",
                                "client_secret": "FAKE_NOT_A_REAL_SECRET",
                                "redirect_uris": ["http://localhost"]}}
FAKE_WEB = {"web": {"client_id": "fake", "client_secret": "FAKE"}}
FAKE_SA = {"type": "service_account", "client_email": "fake@fake.iam.gserviceaccount.com",
           "private_key": "FAKE_NOT_A_REAL_KEY"}


def _write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data), encoding="utf-8")


def main() -> int:
    helper = SCRIPTS / "oauth_local_consent_helper.py"
    src = helper.read_text(encoding="utf-8") if helper.is_file() else ""
    lower = src.lower()

    print("[1] helper 預設 dry-run + live 改由 explicit guard 把關（非永久 kill-switch）")
    _check(helper.is_file(), "scripts/oauth_local_consent_helper.py 存在")
    _check("DEFAULT_DRY_RUN = True" in src, "helper 預設 dry-run（DEFAULT_DRY_RUN = True）")
    # v0.6.8G-B 後：helper 不再靠永久 kill-switch，而是靠 explicit Owner flags +
    # local-only + file validation + token display acknowledgement。
    _check("--i-understand-local-only" in src and "--i-understand-token-will-be-visible" in src,
           "helper 以 explicit Owner 風險旗標把關 live（取代永久 kill-switch）")

    print("[2] --live guard + 需要 --client-secret-file + Replit/CI 偵測")
    _check("--i-understand-local-only" in src and "_refuse_live_no_flag" in src,
           "helper 無安全旗標時拒絕 --live")
    _check("--client-secret-file" in src, "helper 含 --client-secret-file 參數")
    _check("REPL_ID" in src and "_detect_non_local_env" in src,
           "helper 含 Replit / CI 偵測並會拒絕 live")

    print("[3] 無禁用旗標 / 不讀 .env / 不寫 token / 不 print token 真值")
    # 註：--show-refresh-token-once 在 v0.6.8G-B 後是「受 ack 旗標守門的允許選項」，不再禁用。
    for bad_arg in ("--write-token-file", "--print-secret-to-clipboard"):
        _check(bad_arg not in src, f"helper 無禁用旗標 {bad_arg}")
    _check("load_dotenv" not in lower, "helper 不使用 load_dotenv（不讀 .env）")
    for bad_write in ("token.json", "token.pickle", "credentials.json",
                      "open(\"token", "open('token", "write_token"):
        _check(bad_write not in lower, f"helper 無寫 token 檔樣式（{bad_write}）")
    for bad_print in ("print(creds.refresh_token", "print(refresh_token",
                      "print(creds.token)"):
        _check(bad_print not in lower, f"helper 不 print token 真值（{bad_print}）")

    print("[4] dry-run 不在模組層 import google（只允許 live 路徑延遲 import）")
    def _is_module_level_google_import(ln: str) -> bool:
        if not ln or ln[0].isspace():
            return False
        s = ln.strip().lower()
        return s.startswith("import google") or s.startswith("from google")
    _check(not any(_is_module_level_google_import(ln) for ln in src.splitlines()),
           "helper 模組層未 import google（dry-run 不 import google）")

    print("[5] client secret 驗證（fake fixture，不碰 Owner 真檔）")
    try:
        import oauth_local_consent_helper as H  # noqa: E402
        validate = H._validate_client_secret_file
    except Exception as exc:  # pragma: no cover
        _check(False, f"無法 import helper 驗證函式：{exc}")
        validate = None

    repo_fixture = ROOT / "_enablement_fixture_client.json"
    if validate is not None:
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            good = tdp / "oauth-client.json"
            _write_json(good, FAKE_INSTALLED)
            sa = tdp / "sa.json"
            _write_json(sa, FAKE_SA)
            myopen = tdp / "my-openclaw-foo.json"
            _write_json(myopen, FAKE_INSTALLED)
            web = tdp / "web.json"
            _write_json(web, FAKE_WEB)
            missing = tdp / "nope.json"

            ok, _ = validate(str(good))
            _check(ok, "合法 Desktop App（installed）client → 接受")
            ok, _ = validate(str(sa))
            _check(not ok, "service account JSON → 拒絕")
            ok, _ = validate(str(myopen))
            _check(not ok, "my-openclaw*.json 檔名 → 拒絕")
            ok, _ = validate(str(web))
            _check(not ok, "web client JSON → 拒絕")
            ok, _ = validate(str(missing))
            _check(not ok, "不存在的檔 → 拒絕")

            # repo 內路徑 → 拒絕（建立暫存 fixture 於 repo 內，測後刪除）。
            try:
                _write_json(repo_fixture, FAKE_INSTALLED)
                ok, _ = validate(str(repo_fixture))
                _check(not ok, "repo 內 client secret 路徑 → 拒絕")
            finally:
                if repo_fixture.exists():
                    repo_fixture.unlink()

    print("[6] 未修改 Worker / Queue / result_sink / app/main（工作區未顯示被改）")
    for rel in ("app/main.py", "app/worker.py", "app/queue_store.py", "app/result_sink.py"):
        _check(not _modified(rel), f"{rel} 未被修改")

    print("[7] result_sink 仍不 import google client（mock-safe）")
    rs = ROOT / "app" / "result_sink.py"
    rs_text = rs.read_text(encoding="utf-8").lower() if rs.is_file() else ""
    rs_bad = ("import google", "from google", "googleapiclient", "gspread",
              "google.oauth", "google_auth", "google.auth", "import oauthlib")
    _check(rs.is_file() and not any(b in rs_text for b in rs_bad),
           "result_sink.py 不 import 任何 google client library")

    print("[8] token / credential 檔未被 git tracked")
    for pat in ("*token*.json", "*credentials*.json", "*client_secret*.json",
                "*service*account*.json", "my-openclaw*.json", ".env"):
        _check(not _tracked(pat), f"{pat} 未 tracked")

    print("[9] v0.6.8F 文件存在")
    _check(
        (ROOT / "docs" / "HERMES_OPENCLAW_OAUTH_LIVE_HELPER_ENABLEMENT_V0_6_8F.md").is_file(),
        "docs/HERMES_OPENCLAW_OAUTH_LIVE_HELPER_ENABLEMENT_V0_6_8F.md 存在",
    )

    print("[10] requirements google-auth-oauthlib 現況（只回報）")
    req = ROOT / "requirements.txt"
    has = "google-auth-oauthlib" in req.read_text(encoding="utf-8").lower() if req.is_file() else False
    print(f"  info: requirements 目前{'已' if has else '尚未'}含 google-auth-oauthlib"
          f"（僅供本機 live helper；dry-run / result_sink 不 import）")

    if FAILURES:
        print(f"\n❌ OAuth live enablement readiness 檢查失敗 {len(FAILURES)} 項：")
        for f in FAILURES:
            print(f"   - {f}")
        return 1
    print("\n✅ OAuth live enablement readiness 全數通過（沒有連 Google、沒有輸出任何 secret）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
