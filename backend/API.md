# ClassMate API / ClassMate API 文档

Base URL: `http://localhost:8000`  
基础 URL：`http://localhost:8000`

Phase 1 uses an in-memory fixture. Restarting the server resets mock writes.
All JSON fields are camelCase and all timestamps include a timezone offset.

第一阶段使用内存 fixture。重启服务器会重置 mock 写入。所有 JSON 字段使用 camelCase，所有时间带 timezone offset。

## Health / 健康检查

```bash
curl http://localhost:8000/healthz
```

```json
{"ok":true,"mock":true,"db":"up"}
```

## Read endpoints / 读取接口

### `GET /api/state`

Returns the complete frontend state, including computed `progress` on each
assignment.

返回完整前端 state，并在每份 assignment 上附加计算出来的 `progress`。

```bash
curl http://localhost:8000/api/state
```

Response excerpt / response 摘要：

```json
{
  "student":{"id":"student_001","name":"Wan","timezone":"Asia/Kuala_Lumpur"},
  "courses":[{"id":"c1","code":"BDA2043","name":"Big Data Analytics"}],
  "assignments":[{
    "id":"a3","courseId":"c3","title":"Library system SQL exercises",
    "assignedAt":"2026-09-11T23:59:00+08:00",
    "dueAt":"2026-09-14T12:00:00+08:00",
    "gradeWeightPct":10,"totalWords":0,"status":"in_progress",
    "milestones":[{"id":"m12","name":"Questions 1 to 5","weight":40,"targetWords":0,"words":0,"done":true,"doneAt":"2026-09-12T23:59:00+08:00"}],
    "progress":{"actualPct":40,"expectedPct":66.6667,"gap":-26.6667,"band":"red","priorityScore":75.2,"daysLeft":1.5,"wordsLeft":0}
  }],
  "events":[],"updates":[]
}
```

The exact dates move with the clock in mock mode.

mock 模式的日期会随着当前时间移动。

### `GET /api/assignments?status=&courseId=`

```bash
curl 'http://localhost:8000/api/assignments?status=in_progress&courseId=c1'
```

Returns an array of assignment objects in due-date order.

### `GET /api/assignments/{id}`

```bash
curl http://localhost:8000/api/assignments/a1
```

Returns one assignment with nested milestones and computed progress.

### `GET /api/events?from=&to=`

The default range is now through the next seven days. Query values must be
timezone-aware ISO 8601 strings.

```bash
curl 'http://localhost:8000/api/events?from=2026-09-13T00:00:00%2B08:00&to=2026-09-20T00:00:00%2B08:00'
```

Response / response：

```json
[{"id":"e1","courseId":"c1","title":"BDA lecture","type":"lecture","startAt":"2026-09-13T09:00:00+08:00","endAt":"2026-09-13T11:00:00+08:00","location":"UW2-4"}]
```

## Write endpoints / 写入接口

Writes mutate the in-memory fixture in Phase 1. They return the same
camelCase object shape consumed by the frontend.

第一阶段的写入只修改内存 fixture，并返回前端使用的 camelCase 对象。

```bash
curl -X POST http://localhost:8000/api/assignments \
  -H 'Content-Type: application/json' \
  -d '{"courseId":"c1","title":"New report","assignedAt":"2026-09-13T09:00:00+08:00","dueAt":"2026-09-20T17:00:00+08:00","gradeWeightPct":20,"totalWords":1000,"status":"not_started","milestones":[]}'
```

```bash
curl -X PATCH http://localhost:8000/api/assignments/a1 \
  -H 'Content-Type: application/json' \
  -d '{"status":"in_progress","dueAt":"2026-09-17T17:00:00+08:00"}'
```

```bash
curl -X PATCH http://localhost:8000/api/milestones/m3 \
  -H 'Content-Type: application/json' \
  -d '{"done":true}'
```

Setting `done` to true stamps `doneAt`; setting it false clears `doneAt`.

```bash
curl -X POST http://localhost:8000/api/events \
  -H 'Content-Type: application/json' \
  -d '{"courseId":"c1","title":"Study block","type":"consultation","startAt":"2026-09-13T18:00:00+08:00","endAt":"2026-09-13T19:00:00+08:00","location":"Library"}'
```

```bash
curl -X PATCH http://localhost:8000/api/events/e1 \
  -H 'Content-Type: application/json' \
  -d '{"location":"Online"}'
```

## For the n8n teammate / 给 n8n 队友

All ingestion requests require `X-API-Key: $INGEST_API_KEY`.
每个 ingestion request 都需要 `X-API-Key: $INGEST_API_KEY`。

```bash
curl -X POST http://localhost:8000/api/ingest/assignments \
  -H "X-API-Key: $INGEST_API_KEY" -H 'Content-Type: application/json' \
  -d '{"items":[{"externalId":"sha256-example","courseId":"c1","title":"Database assignment","assignedAt":"2026-09-13T09:00:00+08:00","dueAt":"2026-09-20T17:00:00+08:00","gradeWeightPct":30,"totalWords":2000,"status":"not_started","milestones":[]}]}'
```

```json
{"created":1,"updated":0,"skipped":0,"errors":[],"warnings":[]}
```

Post the exact same item again and it is counted as `skipped`; change its
academic fields and it is counted as `updated`. `externalId` is the stable
idempotency key supplied by n8n. Bad rows are reported individually in
`errors` while good rows continue.

The same batch shape is used for `/api/ingest/events` and
`/api/ingest/updates`. Assignment milestone weights are accepted with a
warning if they do not sum to 100.

## Chat / 对话

```bash
curl -X POST http://localhost:8000/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"What should I do today?","studentId":"student_001"}'
```

```json
{"text":"Three things, about 2.7 hours in total. Start at the top.","cards":[{"title":"Questions 6 to 10","meta":"CSC1024 · 40 min · due tomorrow","band":"red","index":1}]}
```

Chat is rule-based in Phase 1: today/plan, catch-up, deadlines, behind/risk,
breakdown, course names/codes, and fallback. No LLM call is made.

Phase 1 的 chat 使用规则路由，不会调用 LLM。
