from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.region import Region
from app.models.school import School, SchoolStatus
from app.schemas.organization import RegionCreate, RegionUpdate, SchoolCreate, SchoolUpdate
from app.core.exceptions import BadRequestException, NotFoundException, ConflictException


class OrganizationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Region CRUD ──

    async def create_region(self, data: RegionCreate, created_by: Optional[str] = None) -> Region:
        existing = await self.db.execute(
            select(Region).where(Region.region_code == data.region_code)
        )
        if existing.scalar_one_or_none():
            raise ConflictException("Region code already exists")

        region = Region(
            region_code=data.region_code,
            region_name=data.region_name,
            province=data.province,
            created_by=created_by,
        )
        self.db.add(region)
        await self.db.commit()
        await self.db.refresh(region)
        return region

    async def get_region(self, region_id: str) -> Optional[Region]:
        result = await self.db.execute(select(Region).where(Region.id == region_id))
        return result.scalar_one_or_none()

    async def list_regions(
        self, search: Optional[str] = None, skip: int = 0, limit: int = 50,
    ) -> tuple:
        query = select(Region)
        count_query = select(func.count(Region.id))

        if search:
            pattern = f"%{search}%"
            query = query.where(Region.region_name.ilike(pattern))
            count_query = count_query.where(Region.region_name.ilike(pattern))

        total = (await self.db.execute(count_query)).scalar()
        result = await self.db.execute(
            query.offset(skip).limit(limit).order_by(Region.created_at.desc())
        )
        return result.scalars().all(), total

    async def update_region(self, region_id: str, data: RegionUpdate) -> Region:
        region = await self.get_region(region_id)
        if not region:
            raise NotFoundException("Region")
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(region, key, value)
        await self.db.commit()
        await self.db.refresh(region)
        return region

    async def delete_region(self, region_id: str) -> bool:
        region = await self.get_region(region_id)
        if not region:
            raise NotFoundException("Region")
        await self.db.delete(region)
        await self.db.commit()
        return True

    # ── School CRUD ──

    async def create_school(self, data: SchoolCreate, created_by: Optional[str] = None) -> School:
        existing = await self.db.execute(
            select(School).where(School.school_code == data.school_code)
        )
        if existing.scalar_one_or_none():
            raise ConflictException("School code already exists")

        region = await self.get_region(data.region_id)
        if not region:
            raise BadRequestException("Region not found")

        school = School(
            region_id=data.region_id,
            school_code=data.school_code,
            school_name=data.school_name,
            address=data.address,
            city=data.city,
            school_type=data.school_type,
        )
        self.db.add(school)
        await self.db.commit()
        await self.db.refresh(school)
        return school

    async def get_school(self, school_id: str) -> Optional[School]:
        result = await self.db.execute(select(School).where(School.id == school_id))
        return result.scalar_one_or_none()

    async def list_schools(
        self, region_id: Optional[str] = None, search: Optional[str] = None,
        status: Optional[str] = None, skip: int = 0, limit: int = 50,
    ) -> tuple:
        query = select(School)
        count_query = select(func.count(School.id))

        if region_id:
            query = query.where(School.region_id == region_id)
            count_query = count_query.where(School.region_id == region_id)
        if search:
            pattern = f"%{search}%"
            query = query.where(School.school_name.ilike(pattern))
            count_query = count_query.where(School.school_name.ilike(pattern))
        if status:
            query = query.where(School.status == status)
            count_query = count_query.where(School.status == status)

        total = (await self.db.execute(count_query)).scalar()
        result = await self.db.execute(
            query.offset(skip).limit(limit).order_by(School.created_at.desc())
        )
        return result.scalars().all(), total

    async def update_school(self, school_id: str, data: SchoolUpdate) -> School:
        school = await self.get_school(school_id)
        if not school:
            raise NotFoundException("School")
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(school, key, value)
        await self.db.commit()
        await self.db.refresh(school)
        return school

    async def approve_school(self, school_id: str, approved_by: str) -> School:
        school = await self.get_school(school_id)
        if not school:
            raise NotFoundException("School")
        school.status = SchoolStatus.ACTIVE
        school.approved_by = approved_by
        await self.db.commit()
        await self.db.refresh(school)
        return school

    async def delete_school(self, school_id: str) -> bool:
        school = await self.get_school(school_id)
        if not school:
            raise NotFoundException("School")
        await self.db.delete(school)
        await self.db.commit()
        return True
