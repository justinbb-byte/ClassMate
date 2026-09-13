# ClassMate backend / ClassMate 后端

## Phase 1 scope / 第一阶段范围

This checkout is intentionally **mock-only**. With `USE_MOCK=true`, the
server serves a relative-date fixture and keeps writes in memory. It does not
create a SQLAlchemy engine or make any Supabase connection, so it works before
database credentials exist.

这个版本刻意只实现 **mock 模式**。`USE_MOCK=true` 时，服务器使用相对当前时间生成的假资料，并把写入保存在内存中；不会创建数据库连接，因此没有 Supabase credentials 也可以启动。

## Run in under two minutes / 两分钟内运行

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

Then open `http://localhost:8000/api/state`. The frontend can call the same
server because CORS defaults to `http://localhost:5173` and
`http://localhost:3000`.

然后打开 `http://localhost:8000/api/state`。CORS 默认允许前端开发服务器。

```bash
curl http://localhost:8000/healthz
curl http://localhost:8000/api/state
```

Expected health response / 健康检查：

```json
{"ok":true,"mock":true,"db":"up"}
```

## Configuration / 配置

All settings are read with `pydantic-settings`. Copy `.env.example` to
`.env`; never commit `.env`.

所有配置通过 `pydantic-settings` 读取。请复制 `.env.example` 为 `.env`，不要把 `.env` 提交到 Git。

- `USE_MOCK=true` is the only supported mode in this Phase 1 response.
- `INGEST_API_KEY` protects n8n ingestion routes with `X-API-Key`.
- `CORS_ORIGINS` is a comma-separated allow-list.

`USE_MOCK=false` currently reports `db: down` and returns service unavailable
for API reads. Supabase persistence, SQLAlchemy models, migrations, and the
seed script are deliberately deferred to Phase 2 as requested.

`USE_MOCK=false` 目前只用于明确表示数据库尚未实现；Supabase persistence、SQLAlchemy models、migrations 和 seed script 按要求留到第二阶段。

## Contract rules / 合约规则

- API JSON uses camelCase (`dueAt`, `courseId`).
- Every returned timestamp is timezone-aware ISO 8601 (`+08:00` or `Z`).
- `milestones` are nested under assignments.
- Assignments, events, and updates are sorted by the frozen contract.
- Progress is calculated server-side by pure functions in `app/progress.py`.

## Test / 测试

```bash
pytest -q
```

See `API.md` for endpoint examples and `CHANGES-FOR-FRONTEND.md` for the
small frontend integration change.
