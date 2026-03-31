from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DeviceCreate(BaseModel):
    outlet_id: str
    device_code: str
    license_key: str
    name: Optional[str] = None
    firmware_version: Optional[str] = None
    hardware_version: Optional[str] = None
    mac_address: Optional[str] = None


class DeviceUpdate(BaseModel):
    outlet_id: Optional[str] = None
    name: Optional[str] = None
    firmware_version: Optional[str] = None
    is_active: Optional[bool] = None
    status: Optional[str] = None


class DeviceResponse(BaseModel):
    id: str
    outlet_id: str
    device_code: str
    name: Optional[str] = None
    license_key: str
    device_serial_number: Optional[str] = None
    device_model: Optional[str] = None
    firmware_version: Optional[str] = None
    hardware_version: Optional[str] = None
    mac_address: Optional[str] = None
    ip_address: Optional[str] = None
    status: str
    is_active: bool
    last_seen_at: Optional[datetime] = None
    last_heartbeat_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DeviceListResponse(BaseModel):
    items: list[DeviceResponse]
    total: int
    page: int
    page_size: int


class DeviceHeartbeat(BaseModel):
    device_code: str
    firmware_version: str
    ip_address: Optional[str] = None
    free_heap: Optional[int] = None
    wifi_rssi: Optional[int] = None
    uptime_seconds: Optional[int] = None


class DeviceAuthRequest(BaseModel):
    device_code: str
    mac_address: str


class DeviceAuthResponse(BaseModel):
    token: str
    device_id: str
    outlet_id: str
    merchant_id: str
    biometric_mode: str
    config: Optional[dict] = None


class DeviceConfigResponse(BaseModel):
    biometric_mode: str
    max_fallback_attempts: int
    outlet_name: str
    merchant_name: str
    firmware_update_available: Optional[str] = None
