from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ApprovalCreate(BaseModel):
    request_type: str
    entity_type: Optional[str] = None
    entity_data: Optional[str] = None


class ApprovalDecision(BaseModel):
    decision: str  # "approved" or "rejected"
    decision_note: Optional[str] = None


class ApprovalResponse(BaseModel):
    id: str
    request_type: str
    requestor_id: str
    approver_id: Optional[str]
    entity_type: Optional[str]
    entity_data: Optional[str]
    status: str
    requested_at: datetime
    decided_at: Optional[datetime]
    decision_note: Optional[str]

    model_config = {"from_attributes": True}


class ApprovalListResponse(BaseModel):
    success: bool = True
    data: List[ApprovalResponse]
    total: int
