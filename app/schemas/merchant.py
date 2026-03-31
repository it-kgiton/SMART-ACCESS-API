from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class MerchantAdminAccount(BaseModel):
    admin_name: str
    admin_email: str
    admin_password: str


class MerchantCreate(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    admin: MerchantAdminAccount


class MerchantUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None


class MerchantResponse(BaseModel):
    id: str
    name: str
    code: str
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MerchantCreateResponse(BaseModel):
    merchant: MerchantResponse
    admin: dict


class MerchantListResponse(BaseModel):
    items: list[MerchantResponse]
    total: int
    page: int
    page_size: int
