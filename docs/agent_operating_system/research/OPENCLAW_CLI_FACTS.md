# OpenClaw CLI Facts for the Phase 9 N=1 Session

Status: **PLANNING ONLY. Phase 9 execution is not authorized.**

Date: 2026-08-03
Scope: one future Owner-present, harmless, query-shaped call. This document does
not authorize a command, infer an installed CLI interface, or permit a probe.

Authorization ladder: an Owner design selection chooses facts/architecture only;
a later exact instruction must separately authorize implementation; after that
work passes independent review, another exact Owner-present instruction must
authorize the one execution. No layer implies the next.

## Threat model

Source: `05_VERIFIED_LONG_TERM_PLAN.md` §6.16, commit `e34ca1c`.

> 在範圍內（設計必須擋住）：模型過度熱心、誤解授權、自作主張、把顯示當授權、意外重放、崩潰後誤續跑。
>
> 明確不在範圍內：一個刻意規避的對抗性模型。
>
> 已知並接受的殘餘風險（不得再被當成待修缺陷）：模型可經 `wsl.exe -u root` 取得 root；gate 程式碼與 `.venv` 對模型可寫；burn ledger 與 frozen artifact 可被有意刪改；`~/.openclaw/` config 可被有意竄改。

Accordingly, this document relies on **procedural constraint plus best-effort
technical isolation, effective against a non-adversarial model**. It makes no
claim that a deliberately evasive model is mechanically excluded.

## 1. Method and evidence boundary

This review used only repository text/source and read-only filesystem metadata.
No `openclaw` command was executed, including help or version commands. A repo
claim describes what existing code expects; it does not prove what the installed
binary currently accepts.

Read-only environment evidence collected for this design round:

- `stat /usr/bin/openclaw` reported that `/usr/bin/openclaw` exists in WSL as a
  symbolic link. The link target and CLI behavior were not invoked or validated.
- directory-presence checks found `~/.openclaw/agents`, `~/.openclaw/cache`, and
  `~/.openclaw/devices`.
- the F8 precheck supplied by the dispatching reviewer states that Windows PATH
  has no OpenClaw command. This is environment evidence for the review, not a
  portable guarantee.

The directory names show that OpenClaw has local agent, cache, and device state.
They do **not** prove whether a harmless query writes those locations.

## 2. What is known about the repository's expectations

| Fact | Evidence | Consequence for Phase 9 |
|---|---|---|
| v1.0 requires one real harmless query-shaped OpenClaw call with zero intended target writes. | `02_V1_0_DEFINITION.md:9-26`; `05_VERIFIED_LONG_TERM_PLAN.md:224-236` | The exact action still requires Owner instruction and synchronous presence. |
| The call is one attempt, not one success: failure cannot trigger an automatic retry. | `05_VERIFIED_LONG_TERM_PLAN.md:229-233`; `09_N1_PREFLIGHT_RUNBOOK.md:91-105` | A timeout, exception, or ambiguous result consumes the attempt. |
| The accepted Phase 4 packet cannot carry a live token. | `docs/schemas/blackboard/approval_packet.schema.json:191-194` | A separately approved Phase 9 token/schema design is required. |
| The static preflight has twelve checks. Five contract/evidence checks are ready, the Phase 7 writer check is ready, and six execution-time checks remain blocked. | `tests/test_n1_preflight_dryrun.py:48-75` | A writer existing is not an execution unlock. |
| No Phase 9 gate module exists at the expected path. | `tests/test_n1_preflight_dryrun.py:22-24,68-74` | Legacy approval/security helpers cannot substitute for the missing gate. |
| The mock bridge and mock gateway never dispatch or call real OpenClaw and keep the real-call/write flags false. | `app/worker_mock_gateway_dry_run.py:20-23,51-58,94-104`; `app/mock_openclaw_gateway.py:94-106` | Mock acceptance proves contract shape only, not CLI compatibility. |
| Existing legacy adapter code constructs an `agent` argv with message, JSON, timeout, agent, and session-key options. | `app/main.py:277-285,544-558` | This is a repo-held expectation only; every option remains pending live verification. |
| Legacy parsing expects either plain stdout or JSON with `payloads[0].text` / `meta.agentMeta.finalAssistantVisibleText`. | `app/main.py:507-524` | These shapes must not be required by the Phase 9 design until the installed CLI is verified. |
| Legacy execution treats missing binary, timeout, and nonzero exit as errors and captures stdout/stderr separately. | `app/main.py:564-600` | These are desired adapter behaviors, not verified CLI guarantees. |
| Local OpenClaw state directories exist. | read-only WSL directory-presence evidence above | A before/after filesystem check is mandatory on execution day. |

## 2b. Measured CLI introspection (Owner-authorized 2026-08-04)

**授權範圍（Owner 於 2026-08-04 對話中選定「乙」，嚴格解釋）**：僅 `--version`
與 `--help` 系列的自我描述指令；**不得**下任何任務、不得帶任何提示詞、不得
`--deliver`、不得建立 session。以下為實跑結果，非推論。

| 指令 | 結果 | exit |
|---|---|---|
| `openclaw --version` | `OpenClaw 2026.6.1 (2e08f0f)` | 0 |
| `readlink -f /usr/bin/openclaw` | `/usr/lib/node_modules/openclaw/openclaw.mjs` | — |
| `openclaw --help` | 全域選項與 30+ 子命令清單 | 0 |
| `openclaw agent --help` | `agent` 子命令完整選項表 | 0 |

由此**解除**的假設（原 §3 第 1、7、9 項）：

- **子命令與參數（原 §3-1）**：`openclaw agent` 存在，實際選項包含
  `-m/--message <text>`、`--json`、`--local`、`--agent <id>`、
  `--timeout <seconds>`、`--model <id>`、`--session-id`、`--session-key`、
  `--channel`、`--deliver`、`--thinking`。與 `app/main.py:277-285` 的既有預期
  **相符**。
- **逾時行為（原 §3-7）**：CLI **自帶**逾時，`--timeout <seconds>`，說明文字為
  `default 600 or config value`。故 gate 不可假設「逾時只由呼叫端控制」，
  必須顯式指定並與 gate 自身的逾時取較嚴者。
- **版本身分（原 §3-9）**：可執行目標與版本已確定（見上表）；執行日仍須
  重新比對，版本變動即視為 drift。

由此**新增**的設計約束（探測前未知，屬新事實）：

1. **`--deliver` 預設為 false**，不加該旗標時回覆不會送到任何通道。Phase 9
   **必須**依賴此預設並顯式禁止該旗標——它是最直接的 egress 風險。
2. **不加 `--local` 時，`agent` 是「via the Gateway」執行**，亦即牽涉一個常駐
   Gateway 服務，而非自足的單一行程。這推翻了「一次呼叫＝一個可完全觀察的
   子行程」的隱含假設；gate 必須明示採 `--local` 或採 Gateway，並各自說明
   證據可觀察性。**此項須在實作規格中裁決。**
3. **`--channel` 支援 20+ 對外通道**（telegram/whatsapp/discord/slack/signal…）。
   Phase 9 必須把通道參數釘死或完全不傳，並在 argv 契約中列為禁止欄位。
4. **session 是可定址且會持續的**（`--session-id`／`--session-key`），佐證
   §3-3「local state writes」為真實風險而非臆測——執行日的前後檔案系統比對
   為**必要**而非建議。

**仍未解除**：原 §3 第 2、3、4、5、6、8、10 項（唯讀語意、local state 實際
寫入、工具/網路行為、任務 exit code 意義、輸出 JSON 實際形狀、session 副作用、
prompt 侷限性）。`--help` 的描述**不是**行為保證。

## 3. What remains an assumption — 待驗證

Every item in this section is **待驗證** and must remain absent from an
implementation contract until verified with the Owner present:

1. **待驗證：subcommand and flags.** The installed CLI may or may not accept
   `agent`, a message option, JSON output, timeout, agent selection, or session
   selection in the forms assumed by `app/main.py`.
2. **待驗證：read-only semantics.** A query-shaped prompt does not by itself
   prove that OpenClaw, its agent, a plugin, or a model tool will avoid writes.
3. **待驗證：local state writes.** The call may update cache, device, agent,
   session, log, SQLite, or other files below `~/.openclaw`.
4. **待驗證：network/tool behavior.** The selected agent may have tools or
   connector capabilities beyond returning text.
5. **待驗證：exit-code meaning.** Zero may not mean a complete, parseable final
   response; nonzero categories and partial-success behavior are unknown.
6. **待驗證：output contract.** Encoding, stdout/stderr division, JSON shape,
   streaming, multiple records, and maximum output size are unknown.
7. **待驗證：timeout behavior.** It is unknown whether the CLI enforces its own
   timeout, whether child work survives termination, and what result is emitted.
8. **待驗證：session behavior.** Agent and session identifiers, reuse rules,
   history effects, and whether a new session writes state are unknown.
9. **待驗證：version identity.** The executable target, package version, and
   installed configuration used on execution day have not been frozen.
10. **待驗證：prompt confinement.** It is unknown whether the exact harmless
    query can be expressed so the selected agent cannot select a write-capable
    tool.

Historical reports that contain a concrete command are evidence of an earlier
workflow, not current CLI documentation. They must not be copied into the Phase
9 implementation package without execution-day verification.

## 4. Minimum facts to confirm in the Owner-present session

The verification itself requires a separately authorized Phase 9 session. The
Owner must see the proposed check before any CLI process starts.

| Required fact | Accept only if | Stop condition |
|---|---|---|
| Executable identity | resolved path, file identity/version evidence, and environment are recorded | path or version differs after evidence freeze |
| Exact argv | official/local documentation or Owner-present inspection confirms every argument | any flag or positional form is guessed |
| Exact harmless action | one agent, one prompt, no tool request, no target mutation | action could select a write-capable tool |
| Output format | one bounded, UTF-8-decodable result shape is confirmed | streaming/partial/unknown output cannot be classified |
| Exit semantics | success, nonzero, signal, and ambiguous completion are distinguishable | zero cannot be tied to a complete response |
| Timeout/termination | parent and any child work are known to stop; no retry occurs | child survival or completion state is uncertain |
| Local filesystem effects | before/after inventory and hashes cover relevant OpenClaw state paths | any unreviewed write appears |
| External effects | the agent/tool posture proves no connector, queue, business target, or follow-up write | any side effect is enabled or cannot be observed |
| Session isolation | the run is bound to one fresh, identifiable session/attempt | prior state can trigger work or a second call |
| Secret handling | token and credentials never enter argv evidence, stdout, fixtures, or audit plaintext | raw secret would be persisted or displayed broadly |

If the CLI necessarily writes local state, that fact is not silently compatible
with “zero write.” The session must stop until the Owner explicitly decides
whether those exact operational writes are acceptable and adds them to the
authorized scope. Audit appends through the already accepted Phase 7 writer are
control-plane evidence, not permission for OpenClaw to write elsewhere.
The writer's accepted existence likewise does not authorize Phase 9 pre/post
execution audit appends; those require a new exact Owner authorization.

An unavoidable local-state write also breaks the current `05` §6.8 zero-write
premise. Continuing would require an explicit Owner-approved revision of that L0
definition and a new exact authorization for the revised scope. A model,
reviewer, or implementation package must not silently broaden §6.8 or infer that
the earlier Phase 7 audit authorization covers OpenClaw state writes.

### Owner-pending L0 alignment proposal

If execution-day evidence proves an unavoidable OpenClaw local-state write, the
Owner must decide whether to revise both `05` §6.8 and the corresponding `09`
runbook zero-write checks. This is a proposal only; this docs-only batch changes
neither authority. Until an explicit F2/L0 decision exists, the current
zero-write rule remains controlling and the rehearsal is HOLD.

Owner decision on a future `05`/`09` alignment proposal: ____________________

## 5. Execution-day evidence record

Before token issuance, the Owner should receive a read-only facts sheet with:

- resolved executable identity and verified CLI interface;
- exact redacted argv structure and action hash;
- selected agent/session posture and disabled capabilities;
- filesystem inventory scope and before-state digest;
- output/exit/timeout classification rules;
- the explicit “one attempt, no retry” abort rule; and
- every remaining unknown marked `BLOCK`.

Any unverified item keeps the execution gate disabled. These facts must be
verified in the Owner-present Phase 9 session; they must not be probed in advance.
