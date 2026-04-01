from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import NotFoundException, ForbiddenException
from app.schemas.outlet import (
    OutletCreate,
    OutletUpdate,
    OutletResponse,
    OutletListResponse,
)
from app.services.outlet_service import OutletService
from app.dependencies import (
    get_current_user,
    require_role,
    require_any_role,
    is_platform_admin,
    is_merchant_admin,
    get_user_merchant_id,
)

router = APIRouter()


@router.get("", response_model=OutletListResponse)
async def list_outlets(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    merchant_id: Optional[str] = None,
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("platform_admin", "merchant_admin")),
):
    service = OutletService(db)

    # Merchant admin is always scoped to their own merchant
    if is_merchant_admin(current_user):
        scoped_merchant_id = get_user_merchant_id(current_user)
        if not scoped_merchant_id:
            return OutletListResponse(items=[], total=0, page=page, page_size=page_size)
        items, total = await service.list_by_merchant(
            scoped_merchant_id, page=page, page_size=page_size, search=search, is_active=is_active
        )
    elif merchant_id:
        items, total = await service.list_by_merchant(
            merchant_id, page=page, page_size=page_size, search=search, is_active=is_active
        )
    else:
        items, total = await service.list_all(
            page=page, page_size=page_size, search=search, is_active=is_active
        )
    return OutletListResponse(
        items=[OutletResponse.model_validate(o) for o in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{outlet_id}", response_model=OutletResponse)
async def get_outlet(
    outlet_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("platform_admin", "merchant_admin")),
):
    service = OutletService(db)
    outlet = await service.get_by_id(outlet_id)
    if not outlet:
        raise NotFoundException("Outlet")

    # Merchant admin can only see their own outlets
    if is_merchant_admin(current_user):
        user_merchant_id = get_user_merchant_id(current_user)
        if outlet.merchant_id != user_merchant_id:
            raise ForbiddenException("You can only view your own outlets")

    return outlet


@router.post("", response_model=OutletResponse, status_code=201)
async def create_outlet(
    data: OutletCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("platform_admin", "merchant_admin")),
):
    """Platform admin can create for any merchant. Merchant admin can only create for their own merchant."""
    if is_merchant_admin(current_user):
        user_merchant_id = get_user_merchant_id(current_user)
        if data.merchant_id != user_merchant_id:
            raise ForbiddenException("You can only create outlets for your own merchant")

    service = OutletService(db)
    outlet = await service.create(data)
    return outlet


@router.put("/{outlet_id}", response_model=OutletResponse)
async def update_outlet(
    outlet_id: str,
    data: OutletUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("platform_admin", "merchant_admin")),
):
    service = OutletService(db)
    outlet = await service.get_by_id(outlet_id)
    if not outlet:
        raise NotFoundException("Outlet")

    # Merchant admin can only update their own outlets
    if is_merchant_admin(current_user):
        user_merchant_id = get_user_merchant_id(current_user)
        if outlet.merchant_id != user_merchant_id:
            raise ForbiddenException("You can only update your own outlets")

    updated = await service.update(outlet_id, data)
    return updated


@router.post("/{outlet_id}/deactivate", response_model=OutletResponse)
async def deactivate_outlet(
    outlet_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("platform_admin", "merchant_admin")),
):
    """Deactivate an outlet. Merchant admin can only deactivate their own outlets."""
    service = OutletService(db)
    outlet = await service.get_by_id(outlet_id)
    if not outlet:
        raise NotFoundException("Outlet")

    if is_merchant_admin(current_user):
        user_merchant_id = get_user_merchant_id(current_user)
        if outlet.merchant_id != user_merchant_id:
            raise ForbiddenException("You can only deactivate your own outlets")

    updated = await service.deactivate(outlet_id)
    return updated


@router.post("/{outlet_id}/reactivate", response_model=OutletResponse)
async def reactivate_outlet(
    outlet_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("platform_admin", "merchant_admin")),
):
    """Reactivate an outlet. Merchant admin can only reactivate their own outlets."""
    service = OutletService(db)
    outlet = await service.get_by_id(outlet_id)
    if not outlet:
        raise NotFoundException("Outlet")

    if is_merchant_admin(current_user):
        user_merchant_id = get_user_merchant_id(current_user)
        if outlet.merchant_id != user_merchant_id:
            raise ForbiddenException("You can only reactivate your own outlets")

    updated = await service.reactivate(outlet_id)
    return updated


@router.delete("/{outlet_id}")
async def delete_outlet(
    outlet_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("platform_admin", "merchant_admin")),
):
    """Platform admin can delete any outlet. Merchant admin can only delete their own outlets."""
    service = OutletService(db)
    outlet = await service.get_by_id(outlet_id)
    if not outlet:
        raise NotFoundException("Outlet")

    if is_merchant_admin(current_user):
        user_merchant_id = get_user_merchant_id(current_user)
        if outlet.merchant_id != user_merchant_id:
            raise ForbiddenException("You can only delete your own outlets")

    deleted = await service.delete(outlet_id)
    if not deleted:
        raise NotFoundException("Outlet")
    return {"message": "Outlet deleted"}
