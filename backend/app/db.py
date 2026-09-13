"""Database boundary reserved for Phase 2.

Phase 1 deliberately does not create an engine in mock mode. This prevents a
missing DATABASE_URL from making the mock server fail at import or startup.
"""

from collections.abc import AsyncGenerator

from .config import Settings


async def get_db(settings: Settings) -> AsyncGenerator[object, None]:
    if settings.use_mock:
        raise RuntimeError("Database access is disabled while USE_MOCK=true")
    raise RuntimeError("Supabase persistence is planned for Phase 2")
    yield  # pragma: no cover
