import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
import enum

from app.core.database import Base


class ApprovalRequestType(str, enum.Enum):
    CREATE_ADMIN_OPS = "create_admin_ops"
    DELETE_ADMIN_OPS = "delete_admin_ops"
    REFUND = "refund"


class ApprovalStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ApprovalRequest(Base):
    __tablename__ = "approval_requests"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    request_type: Mapped[str] = mapped_column(
        SAEnum(ApprovalRequestType, values_callable=lambda x: [e.value for e in x], native_enum=False),
        nullable=False,
    )
    requestor_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )
    approver_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )
    entity_type: Mapped[str] = mapped_column(String(100), nullable=True)
    entity_data: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        SAEnum(ApprovalStatus, values_callable=lambda x: [e.value for e in x], native_enum=False),
        default=ApprovalStatus.PENDING,
    )
    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    decided_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    decision_note: Mapped[str] = mapped_column(Text, nullable=True)
