from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class DeviceCreate(BaseModel):
    device_serial: str
    school_id: Optional[str] = None
    merchant_id: Optional[str] = None
    device_type: Optional[str] = "combo_device"
    name: Optional[str] = None
    license_key: Optional[str] = None


class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    school_id: Optional[str] = None
    merchant_id: Optional[str] = None
    device_type: Optional[str] = None
    firmware_version: Optional[str] = None
    sdk_version: Optional[str] = None


class DeviceResponse(BaseModel):
    id: str
    device_serial: str
    school_id: Optional[str]
    merchant_id: Optional[str]
    device_type: str
    name: Optional[str]
    license_key: Optional[str]
    firmware_version: Optional[str]
    sdk_version: Optional[str]
    status: str
    is_active: bool
    last_heartbeat: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DeviceListResponse(BaseModel):
    success: bool = True
    data: List[DeviceResponse]
    total: int


class DeviceHeartbeat(BaseModel):
    device_serial: str


class DeviceAuthRequest(BaseModel):
    device_serial: str
    license_key: str


class DeviceAuthResponse(BaseModel):
    success: bool = True
    data: dict
