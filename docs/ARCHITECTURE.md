# 架構說明：Hermes → Adapter → OpenClaw

## 目標

先建立最小可行版本：

```text
Hermes Agent
↓
Adapter
↓
OpenClaw
```

這版只處理「派任務」，不處理 Queue，也不處理 Callback。

---

## 角色分工

| 角色 | 白話理解 | 負責內容 |
|---|---|---|
| Hermes | 主腦 / 老闆 | 理解需求、拆任務、規劃流程 |
| Adapter | 翻譯官 / 秘書 | 把 Hermes 任務翻成 OpenClaw 可接收格式 |
| OpenClaw | 執行者 / 員工 | 執行任務、操作工具、接外部平台 |

---

## 資料流

```text
1. 使用者向 Hermes 下指令
2. Hermes 整理成標準任務格式
3. Hermes 呼叫 Adapter 的 /tasks/dispatch
4. Adapter 產生 task_id
5. Adapter 把任務轉成 OpenClaw payload
6. Adapter POST 到 OPENCLAW_WEBHOOK_URL
7. OpenClaw 接收任務並開始執行
```

---

## Adapter 核心

Adapter 最重要的地方是：

```python
build_openclaw_payload()
```

這個 function 負責：

```text
Hermes 任務格式
↓
OpenClaw 任務格式
```

正式串接時，你大多只需要改這裡。

---

## 安全原則

第一版至少要有：

```text
X-Adapter-Token
```

不要讓任何人都能呼叫你的 Adapter，否則外部的人可以隨便派任務給 OpenClaw。

---

## 第一版不要做的事

```text
不要做 Queue
不要做多 Worker
不要做複雜權限
不要讓 OpenClaw 有過高權限
不要一開始就接很多平台
```

先讓一條線跑通。
