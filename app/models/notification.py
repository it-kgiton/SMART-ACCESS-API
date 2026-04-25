import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Boolean, DateTime, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
import enum

from app.core.database import Base


class NotificationType(str, enum.Enum):
    TRANSACTION = "transaction"
    TOPUP = "topup"
    LIMIT_ALERT = "limit_alert"
    ACCOUNT_LOCK = "account_lock"
    APPROVAL = "approval"
    SLA_BREACH = "sla_breach"
    SYSTEM = "system"


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    recipient_user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )
    notification_type: Mapped[str] = mapped_column(
        SAEnum(NotificationType, values_callable=lambda x: [e.value for e in x], native_enum=False),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    reference_type: Mapped[str] = mapped_column(String(100), nullable=True)
    reference_id: Mapped[str] = mapped_column(String(36), nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
