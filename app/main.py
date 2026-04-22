import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.core.database import engine, Base
from app.api.v1.router import api_router
from app.api.v1.endpoints.ws_device import router as ws_router
from app.services.biometric_engine import biometric_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
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
    return {
        "status": "ok",
        "version": settings.APP_VERSION,
        "biometric_engine": "ready" if biometric_engine.is_ready else "not_loaded",
    }
