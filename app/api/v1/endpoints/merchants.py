from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import NotFoundException, ConflictException, ForbiddenException
from app.schemas.merchant import (
    MerchantCreate,
    MerchantUpdate,
    MerchantResponse,
    MerchantListResponse,
    MerchantCreateResponse,
)
from app.services.merchant_service import MerchantService
from app.dependencies import (
    get_current_user,
    require_role,
    require_any_role,
    is_platform_admin,
    is_merchant_admin,
    get_user_merchant_id,
)

router = APIRouter()


@router.get("", response_model=MerchantListResponse)
async def list_merchants(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("platform_admin", "merchant_admin")),
):
    service = MerchantService(db)

    # Merchant admin can only see their own merchant
    if is_merchant_admin(current_user):
        merchant_id = get_user_merchant_id(current_user)
        if not merchant_id:
            return MerchantListResponse(items=[], total=0, page=page, page_size=page_size)
        merchant = await service.get_by_id(merchant_id)
        if not merchant:
            return MerchantListResponse(items=[], total=0, page=page, page_size=page_size)
        return MerchantListResponse(
            items=[MerchantResponse.model_validate(merchant)],
            total=1,
            page=1,
            page_size=page_size,
        )

    items, total = await service.list(page=page, page_size=page_size, search=search, is_active=is_active)
    return MerchantListResponse(
        items=[MerchantResponse.model_validate(m) for m in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{merchant_id}", response_model=MerchantResponse)
async def get_merchant(
    merchant_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("platform_admin", "merchant_admin")),
):
    # Merchant admin can only view their own merchant
    if is_merchant_admin(current_user):
        user_merchant_id = get_user_merchant_id(current_user)
        if user_merchant_id != merchant_id:
            raise ForbiddenException("You can only view your own merchant")

    service = MerchantService(db)
    merchant = await service.get_by_id(merchant_id)
    if not merchant:
        raise NotFoundException("Merchant")
    return merchant


@router.post("", response_model=MerchantCreateResponse, status_code=201)
async def create_merchant(
    data: MerchantCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("platform_admin")),
):
    """Only platform_admin can create merchants. Creates merchant + merchant_admin account."""
    service = MerchantService(db)
    existing = await service.get_by_code(data.code)
    if existing:
        raise ConflictException("Merchant code already exists")
    result = await service.create(data)
    return MerchantCreateResponse(
        merchant=MerchantResponse.model_validate(result["merchant"]),
        admin=result["admin"],
    )


@router.put("/{merchant_id}", response_model=MerchantResponse)
async def update_merchant(
    merchant_id: str,
    data: MerchantUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("platform_admin")),
):
    """Only platform_admin can update merchants."""
    service = MerchantService(db)
    merchant = await service.update(merchant_id, data)
    if not merchant:
        raise NotFoundException("Merchant")
    return merchant


@router.delete("/{merchant_id}")
async def delete_merchant(
    merchant_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("platform_admin")),
):
    """Only platform_admin can delete merchants."""
    service = MerchantService(db)
    deleted = await service.delete(merchant_id)
    if not deleted:
        raise NotFoundException("Merchant")
    return {"message": "Merchant deleted"}


@router.post("/{merchant_id}/reactivate", response_model=MerchantResponse)
async def reactivate_merchant(
    merchant_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("platform_admin")),
):
    """Only platform_admin can reactivate a deactivated merchant."""
    service = MerchantService(db)
    merchant = await service.reactivate(merchant_id)
    if not merchant:
        raise NotFoundException("Merchant")
    return merchant


@router.post("/{merchant_id}/deactivate", response_model=MerchantResponse)
async def deactivate_merchant(
    merchant_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("platform_admin")),
):
    """Only platform_admin can deactivate a merchant."""
    service = MerchantService(db)
    merchant = await service.deactivate(merchant_id)
    if not merchant:
        raise NotFoundException("Merchant")
    return merchant
