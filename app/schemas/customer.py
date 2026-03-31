from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CustomerCreate(BaseModel):
    name: str
    merchant_id: Optional[str] = None
    external_id: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    identity_number: Optional[str] = None
    initial_balance: float = 0.0


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    identity_number: Optional[str] = None
    status: Optional[str] = None


class CustomerResponse(BaseModel):
    id: str
    merchant_id: Optional[str] = None
    external_id: Optional[str] = None
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    identity_number: Optional[str] = None
    photo_url: Optional[str] = None
    status: str
    has_face_credential: bool = False
    has_fingerprint_credential: bool = False
    wallet_balance: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CustomerListResponse(BaseModel):
    items: list[CustomerResponse]
    total: int
    page: int
    page_size: int
