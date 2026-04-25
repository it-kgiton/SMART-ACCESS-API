import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ticket import Ticket, TicketStatus
from app.schemas.ticket import TicketCreate, TicketUpdate
from app.core.exceptions import NotFoundException


SLA_HOURS = {
    "low": 72,
    "medium": 48,
    "high": 24,
    "critical": 4,
}


class TicketService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: TicketCreate, created_by: str) -> Ticket:
        ticket_number = f"TK-{uuid.uuid4().hex[:8].upper()}"
        sla_hours = SLA_HOURS.get(data.priority, 48)

        ticket = Ticket(
            ticket_number=ticket_number,
            created_by=created_by,
            school_id=data.school_id,
            category=data.category,
            subject=data.subject,
            description=data.description,
            priority=data.priority,
            sla_deadline=datetime.now(timezone.utc) + timedelta(hours=sla_hours),
        )
        self.db.add(ticket)
        await self.db.commit()
        await self.db.refresh(ticket)
        return ticket

    async def get_by_id(self, ticket_id: str) -> Optional[Ticket]:
        result = await self.db.execute(
            select(Ticket).where(Ticket.id == ticket_id)
        )
        return result.scalar_one_or_none()

    async def list(
        self, school_id: Optional[str] = None, status: Optional[str] = None,
        priority: Optional[str] = None, assigned_to: Optional[str] = None,
        created_by: Optional[str] = None, skip: int = 0, limit: int = 50,
    ) -> tuple:
        query = select(Ticket)
        count_query = select(func.count(Ticket.id))

        if school_id:
            query = query.where(Ticket.school_id == school_id)
            count_query = count_query.where(Ticket.school_id == school_id)
        if status:
            query = query.where(Ticket.status == status)
            count_query = count_query.where(Ticket.status == status)
        if priority:
            query = query.where(Ticket.priority == priority)
            count_query = count_query.where(Ticket.priority == priority)
        if assigned_to:
            query = query.where(Ticket.assigned_to == assigned_to)
            count_query = count_query.where(Ticket.assigned_to == assigned_to)
        if created_by:
            query = query.where(Ticket.created_by == created_by)
            count_query = count_query.where(Ticket.created_by == created_by)

        total = (await self.db.execute(count_query)).scalar()
        result = await self.db.execute(
            query.offset(skip).limit(limit).order_by(Ticket.created_at.desc())
        )
        return result.scalars().all(), total

    async def update(self, ticket_id: str, data: TicketUpdate) -> Ticket:
        ticket = await self.get_by_id(ticket_id)
        if not ticket:
            raise NotFoundException("Ticket")
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(ticket, key, value)
        if data.status == "resolved":
            ticket.resolved_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(ticket)
        return ticket

    async def resolve(self, ticket_id: str) -> Ticket:
        ticket = await self.get_by_id(ticket_id)
        if not ticket:
            raise NotFoundException("Ticket")
        ticket.status = TicketStatus.RESOLVED
        ticket.resolved_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(ticket)
        return ticket

    async def delete(self, ticket_id: str) -> None:
        ticket = await self.get_by_id(ticket_id)
        if not ticket:
            raise NotFoundException("Ticket")
        await self.db.delete(ticket)
        await self.db.commit()
