import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
import enum

from app.core.database import Base


class TicketCategory(str, enum.Enum):
    TRANSACTION = "transaction"
    BIOMETRIC = "biometric"
    ACCOUNT = "account"
    OTHER = "other"


class TicketPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TicketStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    ticket_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    created_by: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )
    assigned_to: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )
    school_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("schools.id"), nullable=True
    )
    category: Mapped[str] = mapped_column(
        SAEnum(TicketCategory, values_callable=lambda x: [e.value for e in x]),
        default=TicketCategory.OTHER,
    )
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        SAEnum(TicketStatus, values_callable=lambda x: [e.value for e in x]),
        default=TicketStatus.OPEN,
    )
    priority: Mapped[str] = mapped_column(
        SAEnum(TicketPriority, values_callable=lambda x: [e.value for e in x]),
        default=TicketPriority.MEDIUM,
    )
    sla_deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
