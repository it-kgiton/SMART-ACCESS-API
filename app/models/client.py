import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import String, Boolean, DateTime, ForeignKey, Numeric, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class ClientStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    LOCKED = "locked"
    PENDING_DELETION = "pending_deletion"
    DELETED = "deleted"


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )
    parent_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("parents.id"), nullable=False
    )
    school_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("schools.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    student_id_number: Mapped[str] = mapped_column(String(50), nullable=True)
    class_name: Mapped[str] = mapped_column(String(50), nullable=True)
    grade: Mapped[str] = mapped_column(String(20), nullable=True)
    daily_spending_limit: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=True
    )
    biometric_enrolled: Mapped[bool] = mapped_column(Boolean, default=False)
    biometric_last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    balance: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0.00"))
    pin_hash: Mapped[str] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(
        SAEnum(ClientStatus, values_callable=lambda x: [e.value for e in x], native_enum=False),
        default=ClientStatus.ACTIVE,
    )
    photo_url: Mapped[str] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    parent = relationship("Parent", back_populates="clients")
    school = relationship("School", back_populates="clients")
    wallet = relationship("Wallet", back_populates="client", uselist=False, lazy="selectin", cascade="all, delete-orphan")
    face_credential = relationship(
        "FaceCredential", back_populates="client", uselist=False, lazy="selectin", cascade="all, delete-orphan"
    )
    fingerprint_credential = relationship(
        "FingerprintCredential", back_populates="client", uselist=False, lazy="selectin", cascade="all, delete-orphan"
    )
