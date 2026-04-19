from typing import Optional
from decimal import Decimal
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.client import Client, ClientStatus
from app.models.wallet import Wallet
from app.schemas.client import ClientCreate, ClientUpdate
from app.core.security import hash_password
from app.core.exceptions import BadRequestException, NotFoundException


class ClientService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: ClientCreate) -> Client:
        client = Client(
            parent_id=data.parent_id,
            school_id=data.school_id,
            name=data.name,
            student_id_number=data.student_id_number,
            class_name=data.class_name,
            grade=data.grade,
            daily_spending_limit=data.daily_spending_limit,
        )
        if data.pin:
            client.pin_hash = hash_password(data.pin)

        self.db.add(client)
        await self.db.flush()

        # Create wallet for client
        wallet = Wallet(client_id=client.id, balance=Decimal("0.00"))
        self.db.add(wallet)

        await self.db.commit()
        await self.db.refresh(client)
        return client

    async def get_by_id(self, client_id: str) -> Optional[Client]:
        result = await self.db.execute(
            select(Client).where(Client.id == client_id)
        )
        return result.scalar_one_or_none()

    async def list(
        self, school_id: Optional[str] = None, parent_id: Optional[str] = None,
        status: Optional[str] = None, search: Optional[str] = None,
        skip: int = 0, limit: int = 50,
    ) -> tuple:
        query = select(Client)
        count_query = select(func.count(Client.id))

        if school_id:
            query = query.where(Client.school_id == school_id)
            count_query = count_query.where(Client.school_id == school_id)
        if parent_id:
            query = query.where(Client.parent_id == parent_id)
            count_query = count_query.where(Client.parent_id == parent_id)
        if status:
            query = query.where(Client.status == status)
            count_query = count_query.where(Client.status == status)
        if search:
            pattern = f"%{search}%"
            query = query.where(Client.name.ilike(pattern))
            count_query = count_query.where(Client.name.ilike(pattern))

        total = (await self.db.execute(count_query)).scalar()
        result = await self.db.execute(
            query.offset(skip).limit(limit).order_by(Client.created_at.desc())
        )
        return result.scalars().all(), total

    async def update(self, client_id: str, data: ClientUpdate) -> Client:
        client = await self.get_by_id(client_id)
        if not client:
            raise NotFoundException("Client")
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(client, key, value)
        await self.db.commit()
        await self.db.refresh(client)
        return client

    async def set_pin(self, client_id: str, pin: str) -> Client:
        client = await self.get_by_id(client_id)
        if not client:
            raise NotFoundException("Client")
        client.pin_hash = hash_password(pin)
        await self.db.commit()
        await self.db.refresh(client)
        return client

    async def suspend(self, client_id: str) -> Client:
        client = await self.get_by_id(client_id)
        if not client:
            raise NotFoundException("Client")
        client.status = ClientStatus.SUSPENDED
        await self.db.commit()
        await self.db.refresh(client)
        return client

    async def activate(self, client_id: str) -> Client:
        client = await self.get_by_id(client_id)
        if not client:
            raise NotFoundException("Client")
        client.status = ClientStatus.ACTIVE
        await self.db.commit()
        await self.db.refresh(client)
        return client

    async def lock(self, client_id: str) -> Client:
        client = await self.get_by_id(client_id)
        if not client:
            raise NotFoundException("Client")
        client.status = ClientStatus.LOCKED
        await self.db.commit()
        await self.db.refresh(client)
        return client

    async def delete(self, client_id: str) -> bool:
        client = await self.get_by_id(client_id)
        if not client:
            raise NotFoundException("Client")
        client.status = ClientStatus.DELETED
        await self.db.commit()
        return True
