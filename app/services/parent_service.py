from typing import Optional
from decimal import Decimal
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.parent import Parent
from app.models.user import User
from app.schemas.parent import ParentCreate, ParentUpdate
from app.core.security import hash_password
from app.core.exceptions import BadRequestException, NotFoundException


class ParentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: ParentCreate) -> Parent:
        # Create user account for parent
        existing = await self.db.execute(
            select(User).where(User.email == data.email)
        )
        if existing.scalar_one_or_none():
            raise BadRequestException("Email already registered")

        user = User(
            email=data.email,
            hashed_password=hash_password(data.password),
            full_name=data.name,
            phone=data.phone,
            role="parent",
            school_id=data.school_id,
        )
        self.db.add(user)
        await self.db.flush()

        parent = Parent(
            user_id=user.id,
            school_id=data.school_id,
            name=data.name,
            phone=data.phone,
            email=data.email,
            daily_limit_default=data.daily_limit_default or Decimal("50000.00"),
        )
        self.db.add(parent)
        await self.db.commit()
        await self.db.refresh(parent)
        return parent

    async def get_by_id(self, parent_id: str) -> Optional[Parent]:
        result = await self.db.execute(
            select(Parent).where(Parent.id == parent_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: str) -> Optional[Parent]:
        result = await self.db.execute(
            select(Parent).where(Parent.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def list(
        self, school_id: Optional[str] = None, search: Optional[str] = None,
        skip: int = 0, limit: int = 50,
    ) -> tuple:
        query = select(Parent)
        count_query = select(func.count(Parent.id))

        if school_id:
            query = query.where(Parent.school_id == school_id)
            count_query = count_query.where(Parent.school_id == school_id)
        if search:
            pattern = f"%{search}%"
            query = query.where(Parent.name.ilike(pattern))
            count_query = count_query.where(Parent.name.ilike(pattern))

        total = (await self.db.execute(count_query)).scalar()
        result = await self.db.execute(
            query.offset(skip).limit(limit).order_by(Parent.created_at.desc())
        )
        return result.scalars().all(), total

    async def update(self, parent_id: str, data: ParentUpdate) -> Parent:
        parent = await self.get_by_id(parent_id)
        if not parent:
            raise NotFoundException("Parent")
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(parent, key, value)
        await self.db.commit()
        await self.db.refresh(parent)
        return parent

    async def delete(self, parent_id: str) -> bool:
        parent = await self.get_by_id(parent_id)
        if not parent:
            raise NotFoundException("Parent")
        await self.db.delete(parent)
        await self.db.commit()
        return True
