from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.models.outlet import BiometricMode


class OutletAdminAccount(BaseModel):
    admin_name: str
    admin_email: str
    admin_password: str


class OutletCreate(BaseModel):
    merchant_id: str
    name: str
    code: str
    address: Optional[str] = None
    phone: Optional[str] = None
    biometric_mode: BiometricMode = BiometricMode.FACE_PRIMARY_FINGER_FALLBACK
    max_fallback_attempts: int = 2
    admin: OutletAdminAccount


class OutletUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    biometric_mode: Optional[BiometricMode] = None
    max_fallback_attempts: Optional[int] = None
    is_active: Optional[bool] = None


class OutletResponse(BaseModel):
    id: str
    merchant_id: str
    name: str
    code: str
    address: Optional[str] = None
    phone: Optional[str] = None
    biometric_mode: str
    max_fallback_attempts: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class OutletCreateResponse(BaseModel):
    outlet: OutletResponse
    admin: dict


class OutletListResponse(BaseModel):
    items: list[OutletResponse]
    total: int
    page: int
    page_size: int
