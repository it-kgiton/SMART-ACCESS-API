from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class ParentCreate(BaseModel):
    school_id: str
    name: str
    phone: Optional[str] = None
    email: str
    password: str
    daily_limit_default: Optional[Decimal] = Decimal("50000.00")


class ParentUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    daily_limit_default: Optional[Decimal] = None


class ParentResponse(BaseModel):
    id: str
    user_id: Optional[str]
    school_id: str
    name: str
    phone: Optional[str]
    email: Optional[str]
    daily_limit_default: Decimal
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ParentListResponse(BaseModel):
    success: bool = True
    data: List[ParentResponse]
    total: int
