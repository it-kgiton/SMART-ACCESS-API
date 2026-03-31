from typing import Optional
from sqlalchemy import select, func, update as sql_update, delete as sql_delete, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.merchant import Merchant
from app.models.user import User
from app.schemas.merchant import MerchantCreate, MerchantUpdate
from app.core.security import hash_password
from app.core.exceptions import BadRequestException


class MerchantService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: MerchantCreate) -> dict:
        # Check if admin email already exists
        existing_user = await self.db.execute(
            select(User).where(User.email == data.admin.admin_email)
        )
        if existing_user.scalar_one_or_none():
            raise BadRequestException("Admin email already registered")

        merchant_data = data.model_dump(exclude={"admin"})
        merchant = Merchant(**merchant_data)
        self.db.add(merchant)
        await self.db.flush()

        admin_user = User(
            email=data.admin.admin_email,
            hashed_password=hash_password(data.admin.admin_password),
            name=data.admin.admin_name,
            role="merchant_admin",
            merchant_id=merchant.id,
        )
        self.db.add(admin_user)
        await self.db.commit()
        await self.db.refresh(merchant)
        await self.db.refresh(admin_user)

        return {
            "merchant": merchant,
            "admin": {
                "id": admin_user.id,
                "email": admin_user.email,
                "name": admin_user.name,
                "role": admin_user.role,
                "merchant_id": admin_user.merchant_id,
            },
        }

    async def get_by_id(self, merchant_id: str) -> Optional[Merchant]:
        result = await self.db.execute(
            select(Merchant).where(Merchant.id == merchant_id)
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> Optional[Merchant]:
        result = await self.db.execute(
            select(Merchant).where(Merchant.code == code)
        )
        return result.scalar_one_or_none()

    async def list(
        self, page: int = 1, page_size: int = 20, search: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> tuple[list[Merchant], int]:
        query = select(Merchant)
        count_query = select(func.count()).select_from(Merchant)

        if search:
            pattern = f"%{search}%"
            condition = or_(
                Merchant.name.ilike(pattern),
                Merchant.code.ilike(pattern),
                Merchant.email.ilike(pattern),
            )
            query = query.where(condition)
            count_query = count_query.where(condition)

        if is_active is not None:
            query = query.where(Merchant.is_active == is_active)
            count_query = count_query.where(Merchant.is_active == is_active)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def update(self, merchant_id: str, data: MerchantUpdate) -> Optional[Merchant]:
        merchant = await self.get_by_id(merchant_id)
        if not merchant:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(merchant, field, value)

        await self.db.commit()
        await self.db.refresh(merchant)
        return merchant

    async def delete(self, merchant_id: str) -> bool:
        merchant = await self.get_by_id(merchant_id)
        if not merchant:
            return False

        # Hard-delete all users linked to this merchant so their emails can be reused
        await self.db.execute(
            sql_delete(User).where(User.merchant_id == merchant_id)
        )

        await self.db.delete(merchant)
        await self.db.commit()
        return True

    async def reactivate(self, merchant_id: str) -> Optional[Merchant]:
        merchant = await self.get_by_id(merchant_id)
        if not merchant:
            return None
        merchant.is_active = True
        # Re-enable all users linked to this merchant
        await self.db.execute(
            sql_update(User)
            .where(User.merchant_id == merchant_id)
            .values(is_active=True)
        )
        await self.db.commit()
        await self.db.refresh(merchant)
        return merchant

    async def deactivate(self, merchant_id: str) -> Optional[Merchant]:
        merchant = await self.get_by_id(merchant_id)
        if not merchant:
            return None
        merchant.is_active = False
        # Disable all users linked to this merchant
        await self.db.execute(
            sql_update(User)
            .where(User.merchant_id == merchant_id)
            .values(is_active=False)
        )
        await self.db.commit()
        await self.db.refresh(merchant)
        return merchant
