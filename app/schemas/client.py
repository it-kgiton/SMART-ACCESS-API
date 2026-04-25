from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class ClientCreate(BaseModel):
    parent_id: str
    school_id: str
    name: str
    student_id_number: Optional[str] = None
    class_name: Optional[str] = None
    grade: Optional[str] = None
    daily_spending_limit: Optional[Decimal] = None
    pin: Optional[str] = None


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    student_id_number: Optional[str] = None
    class_name: Optional[str] = None
    grade: Optional[str] = None
    daily_spending_limit: Optional[Decimal] = None
    status: Optional[str] = None


class ClientResponse(BaseModel):
    id: str
    user_id: Optional[str]
    parent_id: str
    school_id: str
    name: str
    student_id_number: Optional[str]
    class_name: Optional[str]
    grade: Optional[str]
    daily_spending_limit: Optional[float]
    biometric_enrolled: bool
    biometric_last_updated: Optional[datetime]
    balance: float
    status: str
    photo_url: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ClientListResponse(BaseModel):
    success: bool = True
    data: List[ClientResponse]
    total: int


class ClientSetPin(BaseModel):
    pin: str
