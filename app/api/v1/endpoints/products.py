from fastapi import APIRouter, Depends
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.services.product_service import ProductService
from app.dependencies import get_current_user, require_any_role

router = APIRouter()


@router.post("/")
async def create_product(
    data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub", "admin_ops", "merchant")),
):
    service = ProductService(db)
    product = await service.create(data)
    return {"success": True, "data": ProductResponse.model_validate(product)}


@router.get("/")
async def list_products(
    merchant_id: Optional[str] = None, category: Optional[str] = None,
    available_only: bool = False, search: Optional[str] = None,
    skip: int = 0, limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = ProductService(db)
    products, total = await service.list(
        merchant_id=merchant_id, category=category,
        available_only=available_only, search=search, skip=skip, limit=limit,
    )
    return {
        "success": True,
        "data": [ProductResponse.model_validate(p) for p in products],
        "total": total,
    }


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = ProductService(db)
    product = await service.get_by_id(product_id)
    if not product:
        raise NotFoundException("Product")
    return product


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str, data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub", "admin_ops", "merchant")),
):
    service = ProductService(db)
    return await service.update(product_id, data)


@router.delete("/{product_id}")
async def delete_product(
    product_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub", "admin_ops", "merchant")),
):
    service = ProductService(db)
    await service.delete(product_id)
    return {"success": True, "message": "Product deleted"}
