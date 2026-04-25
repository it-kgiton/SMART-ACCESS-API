from fastapi import APIRouter, Depends
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.schemas.parent import ParentCreate, ParentUpdate, ParentResponse
from app.services.parent_service import ParentService
from app.dependencies import require_any_role, require_role

router = APIRouter()


@router.get("/me", response_model=ParentResponse)
async def get_my_parent_profile(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("parent")),
):
    """Return the parent profile for the currently logged-in parent user."""
    service = ParentService(db)
    parent = await service.get_by_user_id(current_user["sub"])
    if not parent:
        raise NotFoundException("Parent profile not found for this user")
    return parent


@router.post("/")
async def create_parent(
    data: ParentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub", "admin_ops")),
):
    service = ParentService(db)
    parent = await service.create(data)
    return {"success": True, "data": ParentResponse.model_validate(parent)}


@router.get("")
async def list_parents(
    school_id: Optional[str] = None, search: Optional[str] = None,
    skip: int = 0, limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub", "admin_ops")),
):
    service = ParentService(db)
    parents, total = await service.list(school_id=school_id, search=search, skip=skip, limit=limit)
    return {
        "success": True,
        "data": [ParentResponse.model_validate(p) for p in parents],
        "total": total,
    }


@router.get("/me", response_model=ParentResponse)
async def get_my_parent(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("parent")),
):
    service = ParentService(db)
    parent = await service.get_by_user_id(current_user["sub"])
    if not parent:
        raise NotFoundException("Parent")
    return parent


@router.get("/{parent_id}", response_model=ParentResponse)
async def get_parent(
    parent_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub", "admin_ops", "parent")),
):
    service = ParentService(db)
    parent = await service.get_by_id(parent_id)
    if not parent:
        raise NotFoundException("Parent")
    return parent


@router.patch("/{parent_id}", response_model=ParentResponse)
async def update_parent(
    parent_id: str, data: ParentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub", "admin_ops", "parent")),
):
    service = ParentService(db)
    return await service.update(parent_id, data)


@router.delete("/{parent_id}")
async def delete_parent(
    parent_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub")),
):
    service = ParentService(db)
    await service.delete(parent_id)
    return {"success": True, "message": "Parent deleted"}
