from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class RegionCreate(BaseModel):
    region_code: str = Field(..., max_length=50)
    region_name: str = Field(..., max_length=255)
    province: Optional[str] = None


class RegionUpdate(BaseModel):
    region_name: Optional[str] = None
    province: Optional[str] = None
    status: Optional[str] = None


class RegionResponse(BaseModel):
    id: str
    region_code: str
    region_name: str
    province: Optional[str]
    admin_user_id: Optional[str]
    status: str
    created_by: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RegionListResponse(BaseModel):
    success: bool = True
    data: List[RegionResponse]
    total: int


class SchoolCreate(BaseModel):
    region_id: str
    school_code: str = Field(..., max_length=50)
    school_name: str = Field(..., max_length=255)
    address: Optional[str] = None
    city: Optional[str] = None
    school_type: Optional[str] = None


class SchoolUpdate(BaseModel):
    school_name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    school_type: Optional[str] = None
    status: Optional[str] = None


class SchoolResponse(BaseModel):
    id: str
    region_id: str
    school_code: str
    school_name: str
    address: Optional[str]
    city: Optional[str]
    admin_user_id: Optional[str]
    school_type: Optional[str]
    status: str
    approved_by: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SchoolListResponse(BaseModel):
    success: bool = True
    data: List[SchoolResponse]
    total: int
