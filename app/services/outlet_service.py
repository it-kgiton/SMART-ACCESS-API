from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.outlet import Outlet
from app.schemas.outlet import OutletCreate, OutletUpdate


class OutletService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: OutletCreate) -> Outlet:
        outlet = Outlet(**data.model_dump())
        self.db.add(outlet)
        await self.db.commit()
        await self.db.refresh(outlet)
        return outlet

    async def get_by_id(self, outlet_id: str) -> Optional[Outlet]:
        result = await self.db.execute(
            select(Outlet).where(Outlet.id == outlet_id)
        )
        return result.scalar_one_or_none()

    async def list_by_merchant(
        self,
        merchant_id: str,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
    ) -> tuple[list[Outlet], int]:
        query = select(Outlet).where(Outlet.merchant_id == merchant_id)
        count_query = select(func.count()).select_from(Outlet).where(
            Outlet.merchant_id == merchant_id
        )

        if search:
            query = query.where(Outlet.name.ilike(f"%{search}%"))
            count_query = count_query.where(Outlet.name.ilike(f"%{search}%"))

        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def list_all(
        self, page: int = 1, page_size: int = 20, search: Optional[str] = None
    ) -> tuple[list[Outlet], int]:
        query = select(Outlet)
        count_query = select(func.count()).select_from(Outlet)

        if search:
            query = query.where(Outlet.name.ilike(f"%{search}%"))
            count_query = count_query.where(Outlet.name.ilike(f"%{search}%"))

        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def update(self, outlet_id: str, data: OutletUpdate) -> Optional[Outlet]:
        outlet = await self.get_by_id(outlet_id)
        if not outlet:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(outlet, field, value)

        await self.db.commit()
        await self.db.refresh(outlet)
        return outlet

    async def delete(self, outlet_id: str) -> bool:
        outlet = await self.get_by_id(outlet_id)
        if not outlet:
            return False
        await self.db.delete(outlet)
        await self.db.commit()
        return True
