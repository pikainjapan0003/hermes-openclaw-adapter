"""v0.7.2-UI-E-B-R readiness check: Replit regression + demo task fixture alignment.

Verifies the dashboard regression tests are auth-aware and assert UI-E-B markers,
and that the demo review-task seed script is a safe, default-dry-run, local-only
fixture (no external side effects, no secrets, no Worker/OpenClaw/Hermes/Sheets).

This script only reads the three target scripts. It does NOT read .env,
credentials, tokens, or secrets, touches no app/ logic, and makes no network
call.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SCRIPTS = ROOT / "scripts"
PASS = []
FAIL = []

READONLY = SCRIPTS / "test_dashboard_readonly.py"
POLISH = SCRIPTS / "test_dashboard_polish.py"
SEED = SCRIPTS / "seed_dashboard_demo_review_task_v0_7_2_ui_e_b_r.py"


def ok(label):
    PASS.append(label)
    print(f"  ok : {label}")


def xx(label):
    FAIL.append(label)
    print(f"  XX : {label}")


# ---------------------------------------------------------------------------
# [1] 檔案存在
# ---------------------------------------------------------------------------
print("[1] 目標檔案存在")
for rel, path in (("test_dashboard_readonly.py", READONLY),
                  ("test_dashboard_polish.py", POLISH),
                  ("seed_dashboard_demo_review_task_v0_7_2_ui_e_b_r.py", SEED)):
    ok(f"{rel} 存在") if path.exists() else xx(f"{rel} 存在")

if not (READONLY.exists() and POLISH.exists() and SEED.exists()):
    print("\nXX 缺少目標檔案，無法繼續")
    sys.exit(1)

readonly = READONLY.read_text(encoding="utf-8")
polish = POLISH.read_text(encoding="utf-8")
seed = SEED.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# [2] 測試已 auth-aware 且對齊 UI-E-B markers
# ---------------------------------------------------------------------------
print("[2] regression 測試 auth-aware + UI-E-B markers")
for name, text in (("readonly", readonly), ("polish", polish)):
    ok(f"{name} 啟用 DASHBOARD_AUTH_ENABLED") if "DASHBOARD_AUTH_ENABLED" in text else xx(f"{name} 啟用 DASHBOARD_AUTH_ENABLED")
    ok(f"{name} 使用 X-Dashboard-Token 認證") if "X-Dashboard-Token" in text else xx(f"{name} 使用 X-Dashboard-Token 認證")
    ok(f"{name} 驗證未登入 redirect login") if "/dashboard/login" in text else xx(f"{name} 驗證未登入 redirect login")

# UI-E-B markers across the two tests (combined)。
tests_corpus = readonly + "\n" + polish
for marker in ("Owner 待處理", "Owner 審核佇列", "Owner 審核面板",
               "核准前請確認風險", "拒絕會保留任務記錄", "安全邊界"):
    ok(f"測試含 UI-E-B marker「{marker}」") if marker in tests_corpus else xx(f"測試含 UI-E-B marker「{marker}」")

# ---------------------------------------------------------------------------
# [3] demo seed script 安全屬性
# ---------------------------------------------------------------------------
print("[3] demo seed script 安全屬性")
SEED_REQUIRED = [
    "dry-run",
    "--apply",
    "--confirm-local-demo-write",
    "DEMO ONLY",
    "LOCAL ONLY",
    "demo-ui-e-b-review-",
    "waiting_review",
    "requires_confirmation",
    "safety_level",
]
for token in SEED_REQUIRED:
    ok(f"seed 含「{token}」") if token in seed else xx(f"seed 含「{token}」")

# 預設 dry-run：apply 必須與 confirm flag 綁定（不可只給 --apply 就寫）。
ok("seed apply 需 confirm flag 綁定") if re.search(r"apply\s+and\s+.*confirm_local_demo_write", seed) else xx("seed apply 需 confirm flag 綁定")
# import 時不可寫入：寫入動作在 main() / __main__ guard 內。
ok("seed 有 __main__ guard") if '__name__ == "__main__"' in seed else xx("seed 有 __main__ guard")

# ---------------------------------------------------------------------------
# [4] 禁止包含（不安全狀態 / 機密 / 外部副作用）
# ---------------------------------------------------------------------------
print("[4] 禁止包含的不安全 markers")
corpus = readonly + "\n" + polish + "\n" + seed
FORBIDDEN_SUBSTR = [
    "GOOGLE_SHEETS_ENABLED=true",
    "Worker enabled",
    "OpenClaw connected",
    "Hermes connected",
    "Google Sheets live write enabled",
    "subprocess worker start",
    "webhook create",
]
for token in FORBIDDEN_SUBSTR:
    ok(f"無「{token}」") if token not in corpus else xx(f"不得含「{token}」")

FORBIDDEN_PATTERNS = [
    (r"spreadsheets/d/[A-Za-z0-9_-]{20,}", "real spreadsheet URL"),
    (r'"?refresh_token"?\s*[:=]\s*"[^"]+"', "refresh token value"),
    (r'"?client_secret"?\s*[:=]\s*"[^"]+"', "client secret value"),
    (r'-----BEGIN[ A-Z]*PRIVATE KEY-----', "private key value"),
]
for pat, label in FORBIDDEN_PATTERNS:
    found = bool(re.search(pat, corpus, re.IGNORECASE))
    ok(f"無「{label}」") if not found else xx(f"不得含「{label}」")

# seed 不得 import 外部副作用模組（網路 / 子程序）。
print("[5] seed 不得有外部副作用 import")
for mod in ("requests", "urllib", "httpx", "socket", "subprocess", "gspread", "websocket"):
    bad = bool(re.search(rf'^\s*import\s+{mod}\b', seed, re.MULTILINE)) or \
        bool(re.search(rf'^\s*from\s+{mod}\b', seed, re.MULTILINE))
    ok(f"seed 不 import {mod}") if not bad else xx(f"seed 不得 import {mod}")

# ---------------------------------------------------------------------------
# 結果
# ---------------------------------------------------------------------------
total = len(PASS) + len(FAIL)
print(f"\n合計：{len(PASS)}/{total} 通過")
if FAIL:
    print(f"\nXX v0.7.2-UI-E-B-R readiness 失敗 {len(FAIL)} 項：")
    for f in FAIL:
        print(f"   - {f}")
    sys.exit(1)
else:
    print("\nv0.7.2-UI-E-B-R regression + demo fixture alignment readiness: ALL PASS")
    sys.exit(0)
