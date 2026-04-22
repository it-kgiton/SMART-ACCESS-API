from fastapi import APIRouter, Depends
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.schemas.device import (
    DeviceCreate,
    DeviceUpdate,
    DeviceResponse,
    DeviceHeartbeat,
    DeviceAuthRequest,
    DeviceAuthResponse,
)
from app.services.device_service import DeviceService
from app.dependencies import get_current_user, require_any_role

router = APIRouter()


@router.post("/")
async def create_device(
    data: DeviceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub", "admin_ops")),
):
    service = DeviceService(db)
    device = await service.create(data)
    return {"success": True, "data": DeviceResponse.model_validate(device)}


@router.get("")
async def list_devices(
    school_id: Optional[str] = None, merchant_id: Optional[str] = None,
    status: Optional[str] = None, skip: int = 0, limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub", "admin_ops")),
):
    service = DeviceService(db)
    devices, total = await service.list_all(
        school_id=school_id, merchant_id=merchant_id, status=status,
        skip=skip, limit=limit,
    )
    return {
        "success": True,
        "data": [DeviceResponse.model_validate(d) for d in devices],
        "total": total,
    }


@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(
    device_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub", "admin_ops")),
):
    service = DeviceService(db)
    device = await service.get_by_id(device_id)
    if not device:
        raise NotFoundException("Device")
    return device


@router.patch("/{device_id}", response_model=DeviceResponse)
async def update_device(
    device_id: str, data: DeviceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub", "admin_ops")),
):
    service = DeviceService(db)
    return await service.update(device_id, data)


@router.post("/auth", response_model=DeviceAuthResponse)
async def authenticate_device(
    data: DeviceAuthRequest,
    db: AsyncSession = Depends(get_db),
):
    service = DeviceService(db)
    result = await service.authenticate_device(data.device_serial, data.license_key)
    return result


@router.post("/heartbeat")
async def device_heartbeat(
    data: DeviceHeartbeat,
    db: AsyncSession = Depends(get_db),
):
    service = DeviceService(db)
    await service.process_heartbeat(data)
    return {"success": True, "message": "Heartbeat recorded"}


@router.post("/{device_id}/block")
async def block_device(
    device_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub")),
):
    service = DeviceService(db)
    device = await service.block_device(device_id)
    return {"success": True, "data": DeviceResponse.model_validate(device)}


@router.post("/{device_id}/unblock")
async def unblock_device(
    device_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub")),
):
    service = DeviceService(db)
    device = await service.unblock_device(device_id)
    return {"success": True, "data": DeviceResponse.model_validate(device)}


@router.delete("/{device_id}")
async def delete_device(
    device_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub")),
):
    service = DeviceService(db)
    await service.delete(device_id)
    return {"success": True, "message": "Device deleted"}
