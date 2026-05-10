from pydantic_settings import BaseSettings
from typing import List
from pathlib import Path

_ENV_FILE = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
    APP_NAME: str = "BiometricPaymentAPI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_PREFIX: str = "/api/v1"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""

    # Database
    DATABASE_URL: str = ""

    # JWT
    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DEVICE_TOKEN_EXPIRE_DAYS: int = 365

    # Biometric — ArcFace w600k_r50 cosine similarity thresholds
    # 0.55 = payment-grade (FAR < 0.01%, FRR ~ 2%)
    BIOMETRIC_ENGINE_ENABLED: bool = True  # Set False on low-memory deployments (e.g. Railway free tier)
    FACE_SIMILARITY_THRESHOLD: float = 0.55
    FINGERPRINT_MATCH_THRESHOLD: int = 40
    MAX_FACE_CANDIDATES: int = 5
    FACE_LIVENESS_ENABLED: bool = True
    FACE_MIN_QUALITY: float = 0.35

    # Storage
    FIRMWARE_STORAGE_BUCKET: str = "smart-access-firmware"
    BIOMETRIC_STORAGE_BUCKET: str = "smart-access-biometric"
    MERCHANT_STORAGE_BUCKET: str = "smart-access-merchant"
    PRODUCT_STORAGE_BUCKET: str = "smart-access-product"

    # CORS
    CORS_ORIGINS: List[str] = ["*"]  # Allow all for dev; restrict in production

    # KGiTON API Integration
    KGITON_API_URL: str = ""
    KGITON_API_KEY: str = ""

    model_config = {"env_file": str(_ENV_FILE), "extra": "ignore"}


settings = Settings()
