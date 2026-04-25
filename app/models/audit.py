import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, Text, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
import enum

from app.core.database import Base


class AuditEventType(str, enum.Enum):
    AUTH = "auth"
    USER_MGMT = "user_mgmt"
    BIOMETRIC = "biometric"
    TRANSACTION = "transaction"
    FINANCIAL = "financial"
    SYSTEM = "system"
    SUPPORT = "support"


class AuditResult(str, enum.Enum):
    SUCCESS = "success"
    FAILURE = "failure"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    event_type: Mapped[str] = mapped_column(
        SAEnum(AuditEventType, values_callable=lambda x: [e.value for e in x], native_enum=False),
        nullable=False,
    )
    actor_id: Mapped[str] = mapped_column(String(36), nullable=True)
    actor_role: Mapped[str] = mapped_column(String(50), nullable=True)
    target_id: Mapped[str] = mapped_column(String(36), nullable=True)
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    details: Mapped[str] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=True)
    device_info: Mapped[str] = mapped_column(String(500), nullable=True)
    result: Mapped[str] = mapped_column(
        SAEnum(AuditResult, values_callable=lambda x: [e.value for e in x], native_enum=False),
        default=AuditResult.SUCCESS,
    )
    school_id: Mapped[str] = mapped_column(String(36), nullable=True)
