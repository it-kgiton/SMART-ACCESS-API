from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from loguru import logger
import traceback

from app.config import settings
from app.core.database import engine, Base, AsyncSessionLocal
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

    # BiometricEngine is initialized lazily on first API call to avoid OOM at startup
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


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}")
    logger.error(traceback.format_exc())
    origin = request.headers.get("origin", "")
    headers = {}
    if origin:
        headers["Access-Control-Allow-Origin"] = origin
        headers["Access-Control-Allow-Credentials"] = "false"
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
        headers=headers,
    )


@app.get("/health")
async def health_check():
    db_ok = False
    if settings.DATABASE_URL:
        try:
            from sqlalchemy import text
            async with AsyncSessionLocal() as session:
                await session.execute(text("SELECT 1"))
            db_ok = True
        except Exception as e:
            logger.error(f"Health check DB probe failed: {e}")
            db_ok = False

    return {
        "status": "ok",
        "version": settings.APP_VERSION,
        "biometric_engine": "ready" if biometric_engine.is_ready else "not_loaded",
        "database": "connected" if db_ok else "disconnected",
    }
