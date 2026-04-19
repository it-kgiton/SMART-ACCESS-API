from fastapi import APIRouter, Depends
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.schemas.ticket import TicketCreate, TicketUpdate, TicketResponse
from app.services.ticket_service import TicketService
from app.dependencies import get_current_user, require_any_role

router = APIRouter()


@router.post("/")
async def create_ticket(
    data: TicketCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = TicketService(db)
    ticket = await service.create(data, created_by=current_user["sub"])
    return {"success": True, "data": TicketResponse.model_validate(ticket)}


@router.get("/")
async def list_tickets(
    school_id: Optional[str] = None, status: Optional[str] = None,
    priority: Optional[str] = None, assigned_to: Optional[str] = None,
    skip: int = 0, limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = TicketService(db)
    tickets, total = await service.list(
        school_id=school_id, status=status, priority=priority,
        assigned_to=assigned_to, skip=skip, limit=limit,
    )
    return {
        "success": True,
        "data": [TicketResponse.model_validate(t) for t in tickets],
        "total": total,
    }


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = TicketService(db)
    ticket = await service.get_by_id(ticket_id)
    if not ticket:
        raise NotFoundException("Ticket")
    return ticket


@router.patch("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(
    ticket_id: str, data: TicketUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub", "admin_ops")),
):
    service = TicketService(db)
    return await service.update(ticket_id, data)


@router.post("/{ticket_id}/resolve")
async def resolve_ticket(
    ticket_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub", "admin_ops")),
):
    service = TicketService(db)
    ticket = await service.resolve(ticket_id)
    return {"success": True, "data": TicketResponse.model_validate(ticket)}


@router.delete("/{ticket_id}")
async def delete_ticket(
    ticket_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub")),
):
    service = TicketService(db)
    await service.delete(ticket_id)
    return {"success": True, "message": "Ticket deleted"}
