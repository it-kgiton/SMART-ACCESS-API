from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# statement_cache_size=0 — required for Supabase/PgBouncer transaction pooling.
# Safe for all environments (minor perf tradeoff, prevents DuplicatePreparedStatementError).
# ssl=require — Supabase enforces SSL; harmless default for other hosted Postgres.
_connect_args: dict = {
    "statement_cache_size": 0,
    "ssl": "require",
}

# For local dev (plain localhost URLs), skip SSL
if any(h in settings.DATABASE_URL for h in ("localhost", "127.0.0.1", "host.docker.internal")):
    _connect_args.pop("ssl")

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,   # validates connections before use, catching stale connections
    pool_recycle=3600,    # recycle connections every hour to prevent stale prepared statements
    pool_size=5,
    max_overflow=5,
    connect_args=_connect_args,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
