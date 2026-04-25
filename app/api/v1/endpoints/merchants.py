from fastapi import APIRouter, Depends
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.schemas.merchant import MerchantCreate, MerchantUpdate, MerchantResponse
from app.services.merchant_service import MerchantService
from app.dependencies import require_any_role

router = APIRouter()


@router.post("/")
async def create_merchant(
    data: MerchantCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub", "admin_ops")),
):
    service = MerchantService(db)
    result = await service.create(data)
    return {"success": True, "data": result}


@router.get("")
async def list_merchants(
    school_id: Optional[str] = None, search: Optional[str] = None,
    status: Optional[str] = None, skip: int = 0, limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub", "admin_ops")),
):
    service = MerchantService(db)
    merchants, total = await service.list(
        school_id=school_id, search=search, status=status, skip=skip, limit=limit,
    )
    return {
        "success": True,
        "data": [MerchantResponse.model_validate(m) for m in merchants],
        "total": total,
    }


@router.get("/{merchant_id}", response_model=MerchantResponse)
async def get_merchant(
    merchant_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub", "admin_ops", "merchant")),
):
    service = MerchantService(db)
    merchant = await service.get_by_id(merchant_id)
    if not merchant:
        raise NotFoundException("Merchant")
    return merchant


@router.patch("/{merchant_id}", response_model=MerchantResponse)
async def update_merchant(
    merchant_id: str, data: MerchantUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub", "admin_ops", "merchant")),
):
    service = MerchantService(db)
    return await service.update(merchant_id, data)


@router.post("/{merchant_id}/suspend")
async def suspend_merchant(
    merchant_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub", "admin_ops")),
):
    service = MerchantService(db)
    merchant = await service.suspend(merchant_id)
    return {"success": True, "data": MerchantResponse.model_validate(merchant)}


@router.post("/{merchant_id}/activate")
async def activate_merchant(
    merchant_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub", "admin_ops")),
):
    service = MerchantService(db)
    merchant = await service.activate(merchant_id)
    return {"success": True, "data": MerchantResponse.model_validate(merchant)}


@router.delete("/{merchant_id}")
async def delete_merchant(
    merchant_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub")),
):
    service = MerchantService(db)
    await service.delete(merchant_id)
    return {"success": True, "message": "Merchant deleted"}
