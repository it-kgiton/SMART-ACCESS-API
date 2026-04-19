from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class NotificationResponse(BaseModel):
    id: str
    recipient_user_id: str
    notification_type: str
    title: str
    message: str
    reference_type: Optional[str]
    reference_id: Optional[str]
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationListResponse(BaseModel):
    success: bool = True
    data: List[NotificationResponse]
    total: int
    unread_count: int
