from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class DashboardStats(BaseModel):
    total_transactions: int = 0
    total_transaction_amount: float = 0
    total_users: int = 0
    total_merchants: int = 0
    total_clients: int = 0
    total_parents: int = 0
    active_devices: int = 0
    pending_approvals: int = 0
    open_tickets: int = 0
    enrollment_rate: float = 0


class DashboardResponse(BaseModel):
    success: bool = True
    data: DashboardStats


class AuditLogResponse(BaseModel):
    id: str
    timestamp: datetime
    event_type: str
    actor_id: Optional[str]
    actor_role: Optional[str]
    target_id: Optional[str]
    action: str
    details: Optional[str]
    ip_address: Optional[str]
    device_info: Optional[str]
    result: str
    school_id: Optional[str]

    model_config = {"from_attributes": True}


class AuditLogListResponse(BaseModel):
    success: bool = True
    data: List[AuditLogResponse]
    total: int
