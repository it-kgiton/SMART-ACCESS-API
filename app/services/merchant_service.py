from typing import Optional
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.merchant import Merchant, MerchantStatus
from app.models.user import User
from app.schemas.merchant import MerchantCreate, MerchantUpdate
from app.core.security import hash_password
from app.core.exceptions import BadRequestException, NotFoundException


class MerchantService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: MerchantCreate) -> dict:
        merchant = Merchant(
            school_id=data.school_id,
            business_name=data.business_name,
            business_type=data.business_type or "kantin",
            owner_name=data.owner_name,
            phone=data.phone,
            email=data.email,
            address=data.address,
        )
        self.db.add(merchant)
        await self.db.flush()

        admin_user = None
        if data.admin:
            existing_user = await self.db.execute(
                select(User).where(User.email == data.admin.admin_email)
            )
            if existing_user.scalar_one_or_none():
                raise BadRequestException("Admin email already registered")

            admin_user = User(
                email=data.admin.admin_email,
                hashed_password=hash_password(data.admin.admin_password),
                full_name=data.admin.admin_name,
                role="merchant",
                school_id=data.school_id,
                merchant_id=merchant.id,
            )
            self.db.add(admin_user)
            merchant.user_id = admin_user.id

        await self.db.commit()
        await self.db.refresh(merchant)

        result = {"merchant": merchant}
        if admin_user:
            await self.db.refresh(admin_user)
            result["admin"] = {
                "id": admin_user.id,
                "email": admin_user.email,
                "full_name": admin_user.full_name,
                "role": admin_user.role,
            }
        return result

    async def get_by_id(self, merchant_id: str) -> Optional[Merchant]:
        result = await self.db.execute(
            select(Merchant).where(Merchant.id == merchant_id)
        )
        return result.scalar_one_or_none()

    async def list(
        self, school_id: Optional[str] = None, search: Optional[str] = None,
        status: Optional[str] = None, skip: int = 0, limit: int = 50,
    ) -> tuple:
        query = select(Merchant)
        count_query = select(func.count(Merchant.id))

        if school_id:
            query = query.where(Merchant.school_id == school_id)
            count_query = count_query.where(Merchant.school_id == school_id)
        if search:
            pattern = f"%{search}%"
            cond = or_(
                Merchant.business_name.ilike(pattern),
                Merchant.owner_name.ilike(pattern),
            )
            query = query.where(cond)
            count_query = count_query.where(cond)
        if status:
            query = query.where(Merchant.status == status)
            count_query = count_query.where(Merchant.status == status)

        total = (await self.db.execute(count_query)).scalar()
        result = await self.db.execute(
            query.offset(skip).limit(limit).order_by(Merchant.created_at.desc())
        )
        return result.scalars().all(), total

    async def update(self, merchant_id: str, data: MerchantUpdate) -> Merchant:
        merchant = await self.get_by_id(merchant_id)
        if not merchant:
            raise NotFoundException("Merchant")
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(merchant, key, value)
        await self.db.commit()
        await self.db.refresh(merchant)
        return merchant

    async def suspend(self, merchant_id: str) -> Merchant:
        merchant = await self.get_by_id(merchant_id)
        if not merchant:
            raise NotFoundException("Merchant")
        merchant.status = MerchantStatus.SUSPENDED
        await self.db.commit()
        await self.db.refresh(merchant)
        return merchant

    async def activate(self, merchant_id: str) -> Merchant:
        merchant = await self.get_by_id(merchant_id)
        if not merchant:
            raise NotFoundException("Merchant")
        merchant.status = MerchantStatus.ACTIVE
        await self.db.commit()
        await self.db.refresh(merchant)
        return merchant

    async def delete(self, merchant_id: str) -> bool:
        merchant = await self.get_by_id(merchant_id)
        if not merchant:
            raise NotFoundException("Merchant")
        await self.db.delete(merchant)
        await self.db.commit()
        return True
