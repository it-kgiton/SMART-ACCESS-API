from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# statement_cache_size=0 — disables asyncpg's client-side prepared statement cache.
# prepared_statement_name_func=lambda: "" — forces ANONYMOUS prepared statements
# (empty name). PgBouncer in transaction mode only supports anonymous prepared
# statements; named ones (like __asyncpg_stmt_N__) cause DuplicatePreparedStatementError
# because PgBouncer reuses server-side connections that already have those names.
_connect_args: dict = {"statement_cache_size": 0}

# Add SSL + anonymous prepared statements for hosted Postgres (Railway public proxy, etc.)
# Skip for private/local network hosts (no PgBouncer in path)
_no_ssl_hosts = ("localhost", "127.0.0.1", "host.docker.internal", "railway.internal", "@db:", "@db/")
if not any(h in settings.DATABASE_URL for h in _no_ssl_hosts):
    _connect_args["ssl"] = "require"
    _connect_args["prepared_statement_name_func"] = lambda: ""

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
