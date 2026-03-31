from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.schemas.device import (
    DeviceCreate,
    DeviceUpdate,
    DeviceResponse,
    DeviceListResponse,
    DeviceHeartbeat,
    DeviceAuthRequest,
    DeviceAuthResponse,
)
from app.services.device_service import DeviceService
from app.dependencies import (
    get_current_user,
    require_role,
    require_any_role,
    is_merchant_admin,
    get_user_merchant_id,
)

router = APIRouter()


@router.post("/auth", response_model=DeviceAuthResponse)
async def authenticate_device(
    data: DeviceAuthRequest,
    db: AsyncSession = Depends(get_db),
):
    """Device authentication endpoint — no user auth required."""
    service = DeviceService(db)
    result = await service.authenticate_device(data.device_code, data.mac_address)
    if not result:
        from app.core.exceptions import UnauthorizedException
        raise UnauthorizedException("Device authentication failed")
    return result


@router.post("/heartbeat")
async def device_heartbeat(
    data: DeviceHeartbeat,
    db: AsyncSession = Depends(get_db),
):
    """Device heartbeat endpoint."""
    service = DeviceService(db)
    success = await service.process_heartbeat(data)
    if not success:
        raise NotFoundException("Device")
    return {"status": "ok"}


@router.get("", response_model=DeviceListResponse)
async def list_devices(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    outlet_id: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("platform_admin", "merchant_admin")),
):
    service = DeviceService(db)

    # Merchant admin is scoped to their own merchant's devices
    merchant_id = None
    if is_merchant_admin(current_user):
        merchant_id = get_user_merchant_id(current_user)

    items, total = await service.list_all(
        page=page,
        page_size=page_size,
        outlet_id=outlet_id,
        status=status,
        merchant_id=merchant_id,
    )
    return DeviceListResponse(
        items=[DeviceResponse.model_validate(d) for d in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(
    device_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("platform_admin", "merchant_admin")),
):
    service = DeviceService(db)
    device = await service.get_by_id(device_id)
    if not device:
        raise NotFoundException("Device")
    return device


@router.post("", response_model=DeviceResponse, status_code=201)
async def create_device(
    data: DeviceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("platform_admin")),
):
    """Only platform_admin can register devices (requires KGiTON license validation)."""
    service = DeviceService(db)
    device = await service.create(data)
    return device


@router.put("/{device_id}", response_model=DeviceResponse)
async def update_device(
    device_id: str,
    data: DeviceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("platform_admin")),
):
    """Only platform_admin can update devices."""
    service = DeviceService(db)
    device = await service.update(device_id, data)
    if not device:
        raise NotFoundException("Device")
    return device


@router.post("/{device_id}/block")
async def block_device(
    device_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("platform_admin")),
):
    """Only platform_admin can block devices."""
    service = DeviceService(db)
    success = await service.block_device(device_id)
    if not success:
        raise NotFoundException("Device")
    return {"message": "Device blocked"}


@router.post("/{device_id}/unblock")
async def unblock_device(
    device_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("platform_admin")),
):
    """Only platform_admin can unblock devices."""
    service = DeviceService(db)
    success = await service.unblock_device(device_id)
    if not success:
        raise NotFoundException("Device")
    return {"message": "Device unblocked"}
