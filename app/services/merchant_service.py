from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.merchant import Merchant
from app.schemas.merchant import MerchantCreate, MerchantUpdate


class MerchantService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: MerchantCreate) -> Merchant:
        merchant = Merchant(**data.model_dump())
        self.db.add(merchant)
        await self.db.commit()
        await self.db.refresh(merchant)
        return merchant

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
        self, page: int = 1, page_size: int = 20, search: Optional[str] = None
    ) -> tuple[list[Merchant], int]:
        query = select(Merchant)
        count_query = select(func.count()).select_from(Merchant)

        if search:
            query = query.where(Merchant.name.ilike(f"%{search}%"))
            count_query = count_query.where(Merchant.name.ilike(f"%{search}%"))

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
        await self.db.delete(merchant)
        await self.db.commit()
        return True
