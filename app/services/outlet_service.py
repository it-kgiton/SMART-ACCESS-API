from typing import Optional
from sqlalchemy import select, func, or_, delete as sql_delete, update as sql_update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.outlet import Outlet
from app.models.user import User
from app.schemas.outlet import OutletCreate, OutletUpdate
from app.core.security import hash_password
from app.core.exceptions import BadRequestException


class OutletService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: OutletCreate) -> dict:
        """Create outlet + outlet_manager user account."""
        # Check if admin email already exists
        existing_user = await self.db.execute(
            select(User).where(User.email == data.admin.admin_email)
        )
        if existing_user.scalar_one_or_none():
            raise BadRequestException("Admin email already registered")

        outlet_data = data.model_dump(exclude={"admin"})
        outlet = Outlet(**outlet_data)
        self.db.add(outlet)
        await self.db.flush()

        admin_user = User(
            email=data.admin.admin_email,
            hashed_password=hash_password(data.admin.admin_password),
            name=data.admin.admin_name,
            role="outlet_manager",
            merchant_id=data.merchant_id,
            outlet_id=outlet.id,
        )
        self.db.add(admin_user)
        await self.db.commit()
        await self.db.refresh(outlet)
        await self.db.refresh(admin_user)

        return {
            "outlet": outlet,
            "admin": {
                "id": admin_user.id,
                "email": admin_user.email,
                "name": admin_user.name,
                "role": admin_user.role,
                "merchant_id": admin_user.merchant_id,
                "outlet_id": admin_user.outlet_id,
            },
        }

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
        is_active: Optional[bool] = None,
    ) -> tuple[list[Outlet], int]:
        query = select(Outlet).where(Outlet.merchant_id == merchant_id)
        count_query = select(func.count()).select_from(Outlet).where(
            Outlet.merchant_id == merchant_id
        )

        if search:
            query = query.where(or_(Outlet.name.ilike(f"%{search}%"), Outlet.code.ilike(f"%{search}%")))
            count_query = count_query.where(or_(Outlet.name.ilike(f"%{search}%"), Outlet.code.ilike(f"%{search}%")))

        if is_active is not None:
            query = query.where(Outlet.is_active == is_active)
            count_query = count_query.where(Outlet.is_active == is_active)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def list_all(
        self, page: int = 1, page_size: int = 20, search: Optional[str] = None, is_active: Optional[bool] = None
    ) -> tuple[list[Outlet], int]:
        query = select(Outlet)
        count_query = select(func.count()).select_from(Outlet)

        if search:
            query = query.where(or_(Outlet.name.ilike(f"%{search}%"), Outlet.code.ilike(f"%{search}%")))
            count_query = count_query.where(or_(Outlet.name.ilike(f"%{search}%"), Outlet.code.ilike(f"%{search}%")))

        if is_active is not None:
            query = query.where(Outlet.is_active == is_active)
            count_query = count_query.where(Outlet.is_active == is_active)

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

    async def deactivate(self, outlet_id: str) -> Optional[Outlet]:
        outlet = await self.get_by_id(outlet_id)
        if not outlet:
            return None
        outlet.is_active = False
        # Disable all users linked to this outlet
        await self.db.execute(
            sql_update(User)
            .where(User.outlet_id == outlet_id)
            .values(is_active=False)
        )
        await self.db.commit()
        await self.db.refresh(outlet)
        return outlet

    async def reactivate(self, outlet_id: str) -> Optional[Outlet]:
        outlet = await self.get_by_id(outlet_id)
        if not outlet:
            return None
        outlet.is_active = True
        # Re-enable all users linked to this outlet
        await self.db.execute(
            sql_update(User)
            .where(User.outlet_id == outlet_id)
            .values(is_active=True)
        )
        await self.db.commit()
        await self.db.refresh(outlet)
        return outlet

    async def delete(self, outlet_id: str) -> bool:
        outlet = await self.get_by_id(outlet_id)
        if not outlet:
            return False
        # Delete all users linked to this outlet so their emails can be reused
        await self.db.execute(
            sql_delete(User).where(User.outlet_id == outlet_id)
        )
        await self.db.delete(outlet)
        await self.db.commit()
        return True
