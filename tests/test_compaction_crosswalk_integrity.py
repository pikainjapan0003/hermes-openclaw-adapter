"""Permanent zero-rule-loss guard for the 05 compaction crosswalk."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PLAN = ROOT / "docs" / "agent_operating_system" / "05_VERIFIED_LONG_TERM_PLAN.md"
CROSSWALK = (
    ROOT
    / "docs"
    / "agent_operating_system"
    / "research"
    / "05_COMPACTION_RULE_CROSSWALK_20260723.md"
)
CROSSWALK_REF = "research/05_COMPACTION_RULE_CROSSWALK_20260723.md"

ARCHIVED_BLOCKS = {
    "§2": """```text
v1.0 = Owner-supervised Full-chain Baseline
     = Phase 3–7 全部完成
     + Phase 9 的 N=1：一次無害查詢型 openclaw agent 真實調用成功
```

- 包含：本機 Blackboard 讀寫（schema 驗證）、approval packet 流程、dry-run evidence、audit 檔 local write、rollback preview、**一次真實全鏈路查詢調用（零寫入）**。
- 不包含：任何真實寫入型執行（→ v1.1）、真實代碼任務（→ v1.2）、connector read/write（Phase 10，無限期規劃）、production DB、remote API runtime、Dashboard 新控制項。
- 與第一輪定義（Drive 報告建議版）的差異：**Phase 9 N=1 併入 v1.0**（Owner Q4=C）；理由：「傳話中樞的 v1.0」必須證明真的能傳話。
- 本候選仍需 Phase 2 正式簽核（見 6.9），簽核前不得宣稱 v1.0 定義已凍結。""",
    "§3": """Phase 2 執行時，向 Owner 逐條取得逐字簽核，全部完成才得產出
`02_V1_0_DEFINITION.md` 並宣告凍結：

```text
[ ] 1. v1.0 候選定義（6.3 全文）逐字接受？（含 Phase 9 併入 v1.0）
[ ] 2. 「包含」六項，各自的驗收方式逐項接受？
[ ] 3. 「不包含」各項的推遲去向（v1.1/v1.2/Phase 10）接受？
[ ] 4. 任務三級分類寫入 01 §6 接受？
[ ] 5. 02 文件內記錄簽核行：Owner approved on <date>, instruction quote: <逐字>
```

- 已預裁決（盤問時 Owner 口頭已答，Phase 2 只需正式化，不必重問）：Q4/Q5/Q8 的內容。若 Owner 在簽核時改主意，以新裁決為準並更新本節 6.0 表。""",
    "§4": """包1（Sol+xhigh 設計稿）觸發 fixture 矛盾 HOLD，Owner 裁決如下：

1. **`safety_flags` 正本＝16 面旗、巢狀 boolean object**：14 個共同鍵（synthetic_local_only／mock_only／dry_run／owner_review_required／external_side_effects_allowed／external_side_effects_occurred／blackboard_write_allowed／queue_write_allowed／audit_trail_write_allowed／worker_dispatch_allowed／openclaw_call_allowed／hermes_runtime_allowed／connector_call_allowed／google_sheets_write_allowed）＋ follow_up_allowed ＋ follow_up_requires_owner_confirmation。
2. RC-D fixture 的 17 鍵版（多 read_only／follow_up_task_creation_allowed／dashboard_controls_allowed）與 view model 的 `"key=value"` 字串陣列版一律降為**舊 fixture／顯示層投影**：不進新 schema、不改舊檔，validator 只驗新 contract。
3. 追認包1設計的兩處泛化：公共欄位加 `message_type`、`created_at`（共 9 個公共欄位）；`role`＝產物作者的功能角色（不限 worker）。
4. 包2 交付方式：Codex 於 GitHub 開工作 branch＋PR（不碰 master），Fable 5 審＋本地實跑測試，Owner 按 merge。""",
}

PLAN_INDEXES = {
    "### 6.3 ": "§2",
    "### 6.9 ": "§3",
    "### 6.12 ": "§4",
}


def _heading_block(text: str, heading_prefix: str) -> str:
    start = text.index(heading_prefix)
    match = re.search(r"(?m)^### ", text[start + len(heading_prefix) :])
    if match is None:
        return text[start:]
    return text[start : start + len(heading_prefix) + match.start()]


def test_every_archived_rule_group_retains_the_complete_original_block() -> None:
    crosswalk = CROSSWALK.read_text(encoding="utf-8")

    for section, original_block in ARCHIVED_BLOCKS.items():
        assert original_block in crosswalk, section


def test_crosswalk_rule_inventory_is_exact_and_fully_located() -> None:
    crosswalk = CROSSWALK.read_text(encoding="utf-8")
    rows = re.findall(r"(?m)^\| ([CM]\d{2}) \| (.+?) \| (.+?) \| (.+?) \|$", crosswalk)
    by_id = {rule_id: (rule, location, status) for rule_id, rule, location, status in rows}

    expected_ids = {
        *(f"C{index:02d}" for index in range(1, 19)),
        *(f"M{index:02d}" for index in range(1, 12)),
    }
    assert set(by_id) == expected_ids
    assert len(rows) == len(expected_ids)
    assert all(rule.strip() for rule, _location, _status in by_id.values())
    assert all(location.strip() for _rule, location, _status in by_id.values())
    assert all(
        status in {"exact", "preserved"}
        for _rule, _location, status in by_id.values()
    )


def test_current_plan_retains_an_index_to_each_archived_original() -> None:
    plan = PLAN.read_text(encoding="utf-8")

    for heading, crosswalk_section in PLAN_INDEXES.items():
        block = _heading_block(plan, heading)
        assert CROSSWALK_REF in block, heading
        assert crosswalk_section in block, heading


def test_crosswalk_declares_fail_closed_zero_rule_loss() -> None:
    crosswalk = CROSSWALK.read_text(encoding="utf-8")

    assert "Owner decisions or HOLD rules deleted | 0 | 0 | required" in crosswalk
    assert "Any missing crosswalk row makes this compaction invalid" in crosswalk
    assert "requires HOLD rather than" in crosswalk

