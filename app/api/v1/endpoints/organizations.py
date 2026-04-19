from fastapi import APIRouter, Depends
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.organization import (
    RegionCreate, RegionUpdate, RegionResponse, RegionListResponse,
    SchoolCreate, SchoolUpdate, SchoolResponse, SchoolListResponse,
)
from app.services.organization_service import OrganizationService
from app.dependencies import get_current_user, require_role, require_any_role

router = APIRouter()


# ── Regions ──

@router.post("/regions", response_model=RegionResponse)
async def create_region(
    data: RegionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("super_admin")),
):
    service = OrganizationService(db)
    region = await service.create_region(data, created_by=current_user["sub"])
    return region


@router.get("/regions")
async def list_regions(
    search: Optional[str] = None, skip: int = 0, limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub")),
):
    service = OrganizationService(db)
    regions, total = await service.list_regions(search=search, skip=skip, limit=limit)
    return {"success": True, "data": [RegionResponse.model_validate(r) for r in regions], "total": total}


@router.get("/regions/{region_id}", response_model=RegionResponse)
async def get_region(
    region_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub")),
):
    from app.core.exceptions import NotFoundException
    service = OrganizationService(db)
    region = await service.get_region(region_id)
    if not region:
        raise NotFoundException("Region")
    return region


@router.patch("/regions/{region_id}", response_model=RegionResponse)
async def update_region(
    region_id: str, data: RegionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("super_admin")),
):
    service = OrganizationService(db)
    return await service.update_region(region_id, data)


@router.delete("/regions/{region_id}")
async def delete_region(
    region_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("super_admin")),
):
    service = OrganizationService(db)
    await service.delete_region(region_id)
    return {"success": True, "message": "Region deleted"}


# ── Schools ──

@router.post("/schools", response_model=SchoolResponse)
async def create_school(
    data: SchoolCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub")),
):
    service = OrganizationService(db)
    return await service.create_school(data, created_by=current_user["sub"])


@router.get("/schools")
async def list_schools(
    region_id: Optional[str] = None, search: Optional[str] = None,
    status: Optional[str] = None, skip: int = 0, limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub", "admin_ops")),
):
    service = OrganizationService(db)
    schools, total = await service.list_schools(
        region_id=region_id, search=search, status=status, skip=skip, limit=limit,
    )
    return {"success": True, "data": [SchoolResponse.model_validate(s) for s in schools], "total": total}


@router.get("/schools/{school_id}", response_model=SchoolResponse)
async def get_school(
    school_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub", "admin_ops")),
):
    from app.core.exceptions import NotFoundException
    service = OrganizationService(db)
    school = await service.get_school(school_id)
    if not school:
        raise NotFoundException("School")
    return school


@router.patch("/schools/{school_id}", response_model=SchoolResponse)
async def update_school(
    school_id: str, data: SchoolUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub")),
):
    service = OrganizationService(db)
    return await service.update_school(school_id, data)


@router.post("/schools/{school_id}/approve", response_model=SchoolResponse)
async def approve_school(
    school_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub")),
):
    service = OrganizationService(db)
    return await service.approve_school(school_id, approved_by=current_user["sub"])


@router.delete("/schools/{school_id}")
async def delete_school(
    school_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub")),
):
    service = OrganizationService(db)
    await service.delete_school(school_id)
    return {"success": True, "message": "School deleted"}
