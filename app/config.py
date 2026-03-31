from pydantic_settings import BaseSettings
from typing import List


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

    # Biometric
    FACE_SIMILARITY_THRESHOLD: float = 0.45
    FINGERPRINT_MATCH_THRESHOLD: int = 40
    MAX_FACE_CANDIDATES: int = 5
    FACE_LIVENESS_ENABLED: bool = True

    # Storage
    FIRMWARE_STORAGE_BUCKET: str = "firmware"
    BIOMETRIC_STORAGE_BUCKET: str = "biometric-assets"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # KGiTON API Integration
    KGITON_API_URL: str = ""
    KGITON_API_KEY: str = ""

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
