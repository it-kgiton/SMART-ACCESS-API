import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger

from app.config import settings
from app.core.database import engine, Base
from app.api.v1.router import api_router
from app.api.v1.endpoints.ws_device import router as ws_router
from app.services.biometric_engine import biometric_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables — wrapped so a bad DATABASE_URL doesn't kill the process
    if not settings.DATABASE_URL:
        logger.critical("DATABASE_URL is not set! API will start but DB operations will fail.")
    else:
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables verified/created OK")
        except Exception as e:
            logger.critical(f"Database connection failed at startup: {e}")
            logger.critical("Server will still start — fix DATABASE_URL and redeploy.")

    # Initialize InsightFace ArcFace model in background — server starts immediately
    asyncio.create_task(biometric_engine.initialize())
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Hybrid Biometric Merchant Payment Platform — Single Device Edition",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_PREFIX)

# WebSocket routes at root level (ESP32 connects to /ws/device/{license_key})
app.include_router(ws_router, tags=["WebSocket"])


@app.get("/health")
async def health_check():
    db_ok = False
    if settings.DATABASE_URL:
        try:
            async with engine.connect() as conn:
                await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
            db_ok = True
        except Exception:
            db_ok = False

    return {
        "status": "ok",
        "version": settings.APP_VERSION,
        "biometric_engine": "ready" if biometric_engine.is_ready else "not_loaded",
        "database": "connected" if db_ok else "disconnected",
    }
