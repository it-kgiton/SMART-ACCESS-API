from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class MerchantAdminAccount(BaseModel):
    admin_name: str
    admin_email: str
    admin_password: str


class MerchantCreate(BaseModel):
    school_id: str
    business_name: str
    business_type: Optional[str] = "kantin"
    owner_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    admin: Optional[MerchantAdminAccount] = None


class MerchantUpdate(BaseModel):
    business_name: Optional[str] = None
    business_type: Optional[str] = None
    owner_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    status: Optional[str] = None


class MerchantResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    school_id: str
    business_name: str
    business_type: str
    owner_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    logo_url: Optional[str] = None
    balance: float
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MerchantCreateResponse(BaseModel):
    success: bool = True
    data: dict


class MerchantListResponse(BaseModel):
    success: bool = True
    data: List[MerchantResponse]
    total: int
