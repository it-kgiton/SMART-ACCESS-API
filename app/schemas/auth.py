from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    phone: Optional[str] = None
    role: str
    region_id: Optional[str] = None
    school_id: Optional[str] = None
    merchant_id: Optional[str] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    status: Optional[str] = None
    region_id: Optional[str] = None
    school_id: Optional[str] = None
    merchant_id: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    email: str
    phone: Optional[str] = None
    full_name: str
    role: str
    status: str
    region_id: Optional[str] = None
    school_id: Optional[str] = None
    merchant_id: Optional[str] = None
    is_active: bool
    last_login_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class EntityInfo(BaseModel):
    type: str
    id: str
    name: str


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    success: bool = True
    data: dict


class ProfileUpdateName(BaseModel):
    full_name: str


class ProfileChangePassword(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str


class UserListResponse(BaseModel):
    success: bool = True
    data: list[UserResponse]
    total: int
