# ChatGPT / Claude Code Loop Format Contract

目的：讓每次 Claude Code final summary 貼回 ChatGPT 後，ChatGPT 下一則回覆能穩定產生「下一步指令」，避免跑題、廢話、抓錯 phase、或無法 loop。

## 1. ChatGPT 下一步指令格式

每次 Owner Review 通過後，ChatGPT 下一則回覆第一段必須是：

```
# 下一步指令：<phase>
```

例如：

```
# 下一步指令：v0.8.5-A Commit / Push / Closeout
# 下一步指令：v0.8.5-B OpenClaw Mock Gateway Helper
```

第一段不得是閒聊、背景、感想或長篇摘要。

## 2. Owner Review 格式

下一步指令後，必須接：

```
Owner Review：<上一 phase> 通過。
```

或：

```
Owner Review：<上一 phase> 不通過，原因：...
```

## 3. 判斷格式

必須使用：

```
## 判斷

PASS。
```

或：

```
## 判斷

STOP。
```

不要用模糊語氣。

## 4. 概要格式

可以寫概要，但最多 16 點。只列和本輪授權有關的事。不要寫長篇歷史。不要寫情緒化說明。不要寫無關背景。

## 5. 本次唯一授權任務

每個要交給 Claude Code 的任務都必須有：

```
## 本次唯一授權任務

本次唯一授權任務是：

​```text
<phase>
​```
```

Claude Code 只能執行這個 phase。不得自行延伸到下一 phase。

## 6. Owner instruction boundary

真正要給 Claude Code 執行的內容，必須包在：

```
[OWNER-INSTRUCTION-START]
...
[OWNER-INSTRUCTION-END]
```

而且必須包含：

```
[PHASE] <phase>
[EXPECTED-LAST-LINE] <最後一句>
```

Claude Code 收到指令後，必須先確認：

- `[OWNER-INSTRUCTION-START]` exists
- `[OWNER-INSTRUCTION-END]` exists
- `[PHASE]` exists
- `[EXPECTED-LAST-LINE]` exists
- phase 一致
- 最後 300–500 字完整
- 沒有截斷

如果缺失，停止並回報：

```
Owner instruction format incomplete; stopped before execution.
```

## 7. Phase lock

Claude Code 必須鎖定當前 phase。

如果指令 phase 是：

```
v0.8.5-B OpenClaw Mock Gateway Helper
```

就不得執行：

- v0.8.5-A
- v0.8.5-C
- v0.8.4-G
- 任何其他 phase

如果發現 phase mismatch，停止並回報：

```
Source phase mismatch; stopped before execution.
```

## 8. 繁體中文規則

說明文字必須使用繁體中文。檔名、commit message、shell command、程式碼可以保留英文。

## 9. 禁止無關內容

ChatGPT 下一步指令不得包含：

- 長篇感想
- 無關歷史
- 多餘鼓勵
- 未授權的下一階段
- 模糊的「也許可以」
- 未經 Owner 授權的自動延伸任務

Claude Code final summary 也不得產生下一階段任務。Claude Code 只能回報本輪完成狀態，等待 Owner 下一步。

## 10. 回覆結尾固定停止點

每個 Owner 指令結尾必須包含硬性停止點，例如：

```
完成後停止，等待 Owner 下一步。
不要開始 <下一 phase>。
```

Claude Code 完成後也必須停止。不得自動開始下一輪。

## 11. Claude Code final summary 建議格式

Claude Code 完成任務後，final summary 應使用繁體中文，並包含：

```
<phase> complete.

1. Files changed / committed / pushed
2. Validation result
3. Commit result, if any
4. Push result, if any
5. Final git status, if relevant
6. Safety confirmation
7. Hard stop confirmation
```

最後必須寫：

```
完成後停止，等待 Owner 下一步。
```

不得自行生成下一步指令。下一步指令由 ChatGPT / Owner Review 產生。
