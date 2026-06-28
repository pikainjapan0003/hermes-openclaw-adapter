"""v0.7.2-UI-B readiness check: Dashboard root redirect + Replit smoke plan."""
import ast
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
PASS = []
FAIL = []

DOC_PATH = ROOT / "docs" / "HERMES_OPENCLAW_DASHBOARD_ROOT_REDIRECT_REPLIT_SMOKE_PLAN_V0_7_2_UI_B.md"
SELF_PATH = ROOT / "scripts" / "check_hermes_openclaw_dashboard_root_redirect_replit_smoke_v0_7_2_ui_b.py"
MAIN_PATH = ROOT / "app" / "main.py"


def ok(label):
    PASS.append(label)
    print(f"  ok : {label}")


def xx(label):
    FAIL.append(label)
    print(f"  XX : {label}")


# ---------------------------------------------------------------------------
# [1] 文件 / readiness 自身存在
# ---------------------------------------------------------------------------
print("[1] UI-B doc / readiness 存在")
ok("UI-B doc 存在") if DOC_PATH.exists() else xx("UI-B doc 存在")
ok("UI-B readiness 自身存在") if SELF_PATH.exists() else xx("UI-B readiness 自身存在")

# ---------------------------------------------------------------------------
# [2] app/main.py 靜態分析：root route 存在且正確
# ---------------------------------------------------------------------------
print("[2] app/main.py — root route 存在且正確")
main_text = MAIN_PATH.read_text(encoding="utf-8")

# 2a. 有 @app.get("/") 裝飾器
has_root_decorator = bool(re.search(r'@app\.get\(\s*"/"\s*\)', main_text))
ok('main.py 含 @app.get("/")') if has_root_decorator else xx('main.py 含 @app.get("/")')

# 2b. 有 RedirectResponse(url="/dashboard"
has_redirect_dashboard = bool(re.search(r'RedirectResponse\s*\(\s*url\s*=\s*"/dashboard"', main_text))
ok('root route redirects to "/dashboard"') if has_redirect_dashboard else xx('root route redirects to "/dashboard"')

# 2c. status_code=303
has_303 = bool(re.search(r'RedirectResponse\s*\(\s*url\s*=\s*"/dashboard"\s*,\s*status_code\s*=\s*303', main_text))
ok("root route uses status_code=303") if has_303 else xx("root route uses status_code=303")

# 2d. /dashbord alias は追加されていない
has_dashbord_alias = bool(re.search(r'@app\.\w+\(\s*"/dashbord"', main_text))
ok("/dashbord alias not added") if not has_dashbord_alias else xx("/dashbord alias not added — alias should NOT exist")

# 2e. /dashboard route still exists
has_dashboard = bool(re.search(r'@app\.get\(\s*"/dashboard"\s*[,)]', main_text))
ok('/dashboard route still exists') if has_dashboard else xx('/dashboard route still exists')

# 2f. /dashboard/login route still exists
has_login = bool(re.search(r'@app\.get\(\s*"/dashboard/login"', main_text))
ok('/dashboard/login route still exists') if has_login else xx('/dashboard/login route still exists')

# ---------------------------------------------------------------------------
# [3] import app route list 確認
# ---------------------------------------------------------------------------
print("[3] import app — route list 確認")
try:
    sys.path.insert(0, str(ROOT))
    from app.main import app as fastapi_app  # noqa: PLC0415

    paths = {getattr(r, "path", "") for r in fastapi_app.routes}
    ok("import app.main OK")

    ok("/ registered") if "/" in paths else xx("/ registered")
    ok("/dashboard registered") if "/dashboard" in paths else xx("/dashboard registered")
    ok("/dashboard/login registered") if "/dashboard/login" in paths else xx("/dashboard/login registered")
    ok("/dashbord NOT registered") if "/dashbord" not in paths else xx("/dashbord NOT registered — typo route should not exist")

    # root() 関数の return が RedirectResponse であることを確認
    root_route = next((r for r in fastapi_app.routes if getattr(r, "path", "") == "/"), None)
    if root_route is not None:
        import inspect
        src = inspect.getsource(root_route.endpoint)
        ok("root() returns RedirectResponse") if "RedirectResponse" in src else xx("root() returns RedirectResponse")
    else:
        xx("root route object found in app.routes")

except Exception as e:  # noqa: BLE001
    xx(f"import app.main OK — ERROR: {e}")

# ---------------------------------------------------------------------------
# [4] templates / static 未被修改（git diff 確認）
# ---------------------------------------------------------------------------
print("[4] templates / static 未被修改")
try:
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        capture_output=True, text=True, cwd=str(ROOT), timeout=10,
    )
    modified = result.stdout.strip().splitlines()
    template_modified = [f for f in modified if f.startswith("templates/") or f.startswith("static/")]
    ok("templates/ not modified") if not template_modified else xx(f"templates/static unexpectedly modified: {template_modified}")
except Exception as e:  # noqa: BLE001
    xx(f"git diff check — ERROR: {e}")

# ---------------------------------------------------------------------------
# [5] 禁止事項マーカーが app/main.py 新差分に混入していないこと
# ---------------------------------------------------------------------------
print("[5] 境界：Worker/OpenClaw/Hermes/Google Sheets マーカーが root() に混入していないこと")
# root 関数のソースだけ抽出して確認
root_func_match = re.search(
    r'(@app\.get\("/"\)\s*\ndef root\(\).*?)(?=\n@app\.|\Z)',
    main_text, re.DOTALL,
)
if root_func_match:
    root_src = root_func_match.group(1)
    ok("root() 無 run_openclaw_cli") if "run_openclaw_cli" not in root_src else xx("root() 含 run_openclaw_cli")
    ok("root() 無 QueueStore") if "QueueStore" not in root_src else xx("root() 含 QueueStore")
    ok("root() 無 worker") if "worker" not in root_src.lower() else xx("root() 含 worker reference")
    ok("root() 無 google") if "google" not in root_src.lower() else xx("root() 含 google reference")
    ok("root() 無 gspread") if "gspread" not in root_src.lower() else xx("root() 含 gspread reference")
else:
    xx("root() 函數擷取失敗")

# ---------------------------------------------------------------------------
# [6] secrets パターンが doc / readiness に含まれていないこと
# ---------------------------------------------------------------------------
print("[6] 機密パターン非混入確認（doc / readiness）")
SECRET_PATTERNS = [
    r'[0-9a-zA-Z_-]{20,}/[0-9a-zA-Z_-]{10,}',   # spreadsheet URL 断片
    r'1[0-9a-zA-Z_-]{40,}',                        # spreadsheet ID
    r'"refresh_token"\s*:\s*"[^"]+"',
    r'"client_secret"\s*:\s*"[^"]+"',
    r'"private_key"\s*:\s*"-----BEGIN',
]
for target_path in [DOC_PATH, SELF_PATH]:
    content = target_path.read_text(encoding="utf-8")
    found = any(re.search(p, content) for p in SECRET_PATTERNS)
    label = f"{target_path.name} 無 secret パターン"
    ok(label) if not found else xx(label)

# ---------------------------------------------------------------------------
# [7] doc 必須記載確認
# ---------------------------------------------------------------------------
print("[7] doc 必須記載確認")
doc_text = DOC_PATH.read_text(encoding="utf-8")

REQUIRED_STATEMENTS = [
    ("v0.7.2-UI-B only adds root redirect to /dashboard.", "UI-B only adds root redirect"),
    ("v0.7.2-UI-B does not redesign dashboard visuals.", "UI-B does not redesign visuals"),
    ("v0.7.2-UI-B does not add approve-route behavior.", "UI-B does not add approve-route"),
    ("v0.7.2-UI-B does not start Worker.", "UI-B does not start Worker"),
    ("v0.7.2-UI-B does not call OpenClaw.", "UI-B does not call OpenClaw"),
    ("v0.7.2-UI-B does not call Hermes.", "UI-B does not call Hermes"),
    ("v0.7.2-UI-B does not write Google Sheets.", "UI-B does not write Google Sheets"),
    ("v0.7.2-UI-B does not read or display secrets.", "UI-B does not read secrets"),
    ("/dashbord", "doc mentions /dashbord typo"),
    ("DASHBOARD_AUTH_ENABLED", "doc mentions auth redirect behavior"),
    ("303", "doc mentions 303 redirect"),
]
REQUIRED_SECTIONS = [
    "1. Purpose",
    "2. UI-A Findings",
    "3. /dashboard Exists",
    "4. /dashbord Is Typo",
    "5. Root / Currently 404",
    "6. Root Redirect Decision",
    "7. Auth Redirect Behavior",
    "8. Replit-local .replit Overlay",
    "9. .claude Local Metadata",
    "10. Browser Smoke Test Plan",
    "11. Dashboard Visual Design Future Work",
    "12. Not Connected Boundaries",
    "13. No Worker / OpenClaw / Hermes",
    "14. No Google Sheets Live Write",
    "15. No Secrets Read",
    "16. Future v0.7.2-UI-C",
]

for stmt, label in REQUIRED_STATEMENTS:
    ok(f"doc 含聲明「{label}」") if stmt in doc_text else xx(f"doc 含聲明「{label}」")

for section in REQUIRED_SECTIONS:
    ok(f"doc 含章節「{section}」") if section in doc_text else xx(f"doc 含章節「{section}」")

# ---------------------------------------------------------------------------
# 結果
# ---------------------------------------------------------------------------
total = len(PASS) + len(FAIL)
print(f"\n合計：{len(PASS)}/{total} 通過")
if FAIL:
    print(f"\nXX v0.7.2-UI-B readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print("\nv0.7.2-UI-B readiness: ALL PASS")
    sys.exit(0)
