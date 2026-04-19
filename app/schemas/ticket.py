from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class TicketCreate(BaseModel):
    school_id: Optional[str] = None
    category: str = "other"
    subject: str
    description: Optional[str] = None
    priority: str = "medium"


class TicketUpdate(BaseModel):
    assigned_to: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None


class TicketResponse(BaseModel):
    id: str
    ticket_number: str
    created_by: str
    assigned_to: Optional[str]
    school_id: Optional[str]
    category: str
    subject: str
    description: Optional[str]
    status: str
    priority: str
    sla_deadline: Optional[datetime]
    resolved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TicketListResponse(BaseModel):
    success: bool = True
    data: List[TicketResponse]
    total: int
