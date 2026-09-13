from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .mock.fixture import MockStore
from .routers import assignments, chat, events, ingest, state


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    # Phase 1 assumption: non-mock persistence is intentionally not started yet.
    app.state.mock_store = MockStore() if settings.use_mock else None
    yield


settings = get_settings()
app = FastAPI(title="ClassMate API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(state.router)
app.include_router(assignments.router)
app.include_router(events.router)
app.include_router(ingest.router)
app.include_router(chat.router)


@app.get("/healthz")
def healthz():
    return {"ok": True, "mock": settings.use_mock, "db": "up" if settings.use_mock else "down"}
