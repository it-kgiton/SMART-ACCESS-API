from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    email: str
    password: str
    name: str
    role: str
    merchant_id: Optional[str] = None
    outlet_id: Optional[str] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    merchant_id: Optional[str] = None
    outlet_id: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: str
    merchant_id: Optional[str] = None
    outlet_id: Optional[str] = None
    is_active: bool
    last_login_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class MerchantAdminUpdateName(BaseModel):
    name: str


class MerchantAdminResetPassword(BaseModel):
    new_password: str
    confirm_password: str


class ProfileUpdateName(BaseModel):
    name: str


class ProfileChangePassword(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str
