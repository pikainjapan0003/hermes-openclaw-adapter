"""v0.6.9-B — Guarded Google Sheets OAuth writer（獨立模組；本版不真寫、不連 Google）。

設計原則：
- **獨立**：不被 Queue / Worker / result_sink / app.main 引用；不接自動化。
- **預設關閉**：`GOOGLE_SHEETS_ENABLED` 必須明確等於 `true` 才可能寫入；否則直接 skipped，
  且**不** import google、**不**連 Google、**不**讀 token 值。
- **多重 guard**：write_mode 必須 `pilot`、spreadsheet_id 非空、worksheet 必須
  `pilot_result_sink`、row 必須剛好 8 欄、一次只 append 一列、必須顯式 `allow_live_write=True`。
- **transport 可注入**：測試傳入 fake transport，永不走真 Google；只有真要 live 且未注入
  transport 時，才 lazy import google libs、用 refresh token 建 credentials、呼叫 Sheets API。
- **token 安全**：refresh token / client secret 只在真 live build 時從 env 讀取，**永不**印出 / log。

本版不真寫 Google Sheets，測試只用 fake env / mock transport。
詳見 docs/HERMES_OPENCLAW_GOOGLE_SHEETS_OAUTH_WRITER_V0_6_9_B.md。
"""

from __future__ import annotations

import os
from dataclasses import dataclass

# 固定合約。
WORKSHEET_NAME_REQUIRED = "pilot_result_sink"
PILOT_ROW_COLUMNS = (
    "timestamp", "source", "environment", "event_type",
    "task_id", "status", "message", "metadata_json",
)
PILOT_ROW_LEN = len(PILOT_ROW_COLUMNS)  # 8
APPEND_RANGE = f"{WORKSHEET_NAME_REQUIRED}!A:H"
REQUIRED_WRITE_MODE = "pilot"
OAUTH_TOKEN_URI = "https://oauth2.googleapis.com/token"
SHEETS_SCOPE = "https://www.googleapis.com/auth/spreadsheets"


class GoogleSheetsWriterError(Exception):
    """writer 基礎例外。"""


class GoogleSheetsWriterConfigError(GoogleSheetsWriterError):
    """設定不完整 / 不合法。"""


class GoogleSheetsWriterGuardError(GoogleSheetsWriterError):
    """違反 guard（不安全的寫入嘗試）。"""


@dataclass
class GoogleSheetsWriterConfig:
    """writer 設定（不含 token 值；token 只在真 live build 時才從 env 讀）。"""

    enabled: bool
    write_mode: str
    spreadsheet_id: str
    worksheet_name: str

    @property
    def is_enabled(self) -> bool:
        return self.enabled


def load_google_sheets_writer_config(env=None) -> GoogleSheetsWriterConfig:
    """從 env 載入設定（只讀非 token 欄位；不讀 / 不檢查 refresh token 值）。"""
    env = os.environ if env is None else env
    return GoogleSheetsWriterConfig(
        enabled=(env.get("GOOGLE_SHEETS_ENABLED", "").strip().lower() == "true"),
        write_mode=env.get("GOOGLE_SHEETS_WRITE_MODE", "").strip().lower(),
        spreadsheet_id=env.get("GOOGLE_SHEETS_SPREADSHEET_ID", "").strip(),
        worksheet_name=env.get("GOOGLE_SHEETS_WORKSHEET_NAME", "").strip(),
    )


def build_pilot_row(
    *,
    timestamp: str,
    source: str = "hermes-openclaw-adapter",
    environment: str = "pilot",
    event_type: str = "oauth_sheets_write_pilot",
    task_id: str = "manual-pilot-001",
    status: str = "ok",
    message: str = "Google Sheets OAuth pilot write succeeded",
    metadata_json: str = '{"version":"v0.6.9","mode":"pilot","single_row":true}',
) -> list[str]:
    """組出固定 8 欄的 single pilot row（全部轉成 str）。"""
    return [
        str(timestamp), str(source), str(environment), str(event_type),
        str(task_id), str(status), str(message), str(metadata_json),
    ]


def _validate_row(row) -> None:
    if not isinstance(row, (list, tuple)):
        raise GoogleSheetsWriterGuardError("row 必須是 list / tuple")
    if len(row) != PILOT_ROW_LEN:
        raise GoogleSheetsWriterGuardError(
            f"row 必須剛好 {PILOT_ROW_LEN} 欄（single row），收到 {len(row)} 欄")
    for cell in row:
        if isinstance(cell, (list, tuple, dict)):
            raise GoogleSheetsWriterGuardError("row 內含巢狀結構（疑似多列）；一次只允許一列純值")


def _build_live_transport(env=None):
    """只有真要 live 且未注入 transport 時才呼叫：lazy import google + 建 credentials。

    refresh token / client secret 只在此處從 env 讀取，**永不**印出 / log。本版測試不會走到這裡。
    """
    env = os.environ if env is None else env
    refresh_token = env.get("GOOGLE_OAUTH_REFRESH_TOKEN", "").strip()
    client_id = env.get("GOOGLE_OAUTH_CLIENT_ID", "").strip()
    client_secret = env.get("GOOGLE_OAUTH_CLIENT_SECRET", "").strip()
    if not (refresh_token and client_id and client_secret):
        raise GoogleSheetsWriterConfigError(
            "live 需要 GOOGLE_OAUTH_REFRESH_TOKEN / CLIENT_ID / CLIENT_SECRET（值不顯示）")

    from google.oauth2.credentials import Credentials  # lazy import
    from googleapiclient.discovery import build  # lazy import

    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        client_id=client_id,
        client_secret=client_secret,
        token_uri=OAUTH_TOKEN_URI,
        scopes=[SHEETS_SCOPE],
    )
    service = build("sheets", "v4", credentials=creds, cache_discovery=False)
    return _SheetsApiTransport(service)


class _SheetsApiTransport:
    """真 Google Sheets transport（本版測試不使用）。"""

    def __init__(self, service) -> None:
        self._service = service

    def append(self, spreadsheet_id: str, range_a1: str, values: list[list[str]]) -> dict:
        return (
            self._service.spreadsheets().values()
            .append(
                spreadsheetId=spreadsheet_id,
                range=range_a1,
                valueInputOption="RAW",
                insertDataOption="INSERT_ROWS",
                body={"values": values},
            )
            .execute()
        )


def append_single_pilot_row(
    row,
    config: GoogleSheetsWriterConfig,
    *,
    transport=None,
    allow_live_write: bool = False,
    env=None,
) -> dict:
    """受 guard 保護的 single-row append。

    guard 順序：disabled → write_mode → spreadsheet_id → worksheet → row(8) → allow_live_write →
    transport append。disabled 時直接 skipped，不 import google、不讀 token。
    """
    if not config.is_enabled:
        return {"status": "skipped", "reason": "GOOGLE_SHEETS_ENABLED 不是 true（writer 預設關閉）"}

    if config.write_mode != REQUIRED_WRITE_MODE:
        raise GoogleSheetsWriterGuardError(
            f"GOOGLE_SHEETS_WRITE_MODE 必須為 {REQUIRED_WRITE_MODE}")
    if not config.spreadsheet_id:
        raise GoogleSheetsWriterConfigError("GOOGLE_SHEETS_SPREADSHEET_ID 不可為空")
    if config.worksheet_name != WORKSHEET_NAME_REQUIRED:
        raise GoogleSheetsWriterGuardError(
            f"GOOGLE_SHEETS_WORKSHEET_NAME 必須為 {WORKSHEET_NAME_REQUIRED}")
    _validate_row(row)

    if not allow_live_write:
        raise GoogleSheetsWriterGuardError(
            "fail-safe：需顯式 allow_live_write=True 才可能 append（避免誤寫）")

    active_transport = transport if transport is not None else _build_live_transport(env=env)
    result = active_transport.append(config.spreadsheet_id, APPEND_RANGE, [list(row)])
    return {
        "status": "appended",
        "range": APPEND_RANGE,
        "appended_rows": 1,
        "transport_result": result,
    }
