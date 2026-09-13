# Changes for frontend / 前端需要的改动

The existing React mock shape remains the source of truth. The only required
integration change is replacing the local constant with a fetch from the
backend:

现有 React mock shape 仍然是 source of truth。前端只需要把本地 constant 换成 backend fetch：

```js
const response = await fetch("http://localhost:8000/api/state");
const data = await response.json();
```

The response preserves `student`, `courses`, `assignments`, `events`, and
`updates`; all JSON names are camelCase. Assignments now include an additional
server-computed `progress` object:

response 保留 `student`、`courses`、`assignments`、`events` 和 `updates`；所有 JSON 名称都是 camelCase。每份 assignment 额外有 server 计算的 `progress`：

```js
assignment.progress = {
  actualPct, expectedPct, gap, band,
  priorityScore, daysLeft, wordsLeft,
};
```

The existing visual progress calculation can remain temporarily for offline
demo, but it should eventually render this server value so web, mobile, and
Telegram show the same result. The backend returns true ISO 8601 timestamps
with offsets, so `new Date(timestamp)` continues to work.

If the frontend later switches chat from local `reply()` to the backend, send:

```js
await fetch("http://localhost:8000/api/chat", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ message, studentId: "student_001" }),
});
```
