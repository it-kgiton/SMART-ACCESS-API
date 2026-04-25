import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import String, DateTime, Text, ForeignKey, Numeric, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class BusinessType(str, enum.Enum):
    KANTIN = "kantin"
    LAUNDRY = "laundry"
    MINIMARKET = "minimarket"
    FOTOKOPI = "fotokopi"
    OTHER = "other"


class MerchantStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"


class Merchant(Base):
    __tablename__ = "merchants"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )
    school_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("schools.id"), nullable=False
    )
    business_name: Mapped[str] = mapped_column(String(255), nullable=False)
    business_type: Mapped[str] = mapped_column(
        SAEnum(BusinessType, values_callable=lambda x: [e.value for e in x], native_enum=False),
        default=BusinessType.KANTIN,
    )
    owner_name: Mapped[str] = mapped_column(String(255), nullable=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    email: Mapped[str] = mapped_column(String(255), nullable=True)
    address: Mapped[str] = mapped_column(Text, nullable=True)
    logo_url: Mapped[str] = mapped_column(String(500), nullable=True)
    balance: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0.00"))
    status: Mapped[str] = mapped_column(
        SAEnum(MerchantStatus, values_callable=lambda x: [e.value for e in x], native_enum=False),
        default=MerchantStatus.ACTIVE,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    school = relationship("School", back_populates="merchants")
    products = relationship("Product", back_populates="merchant", lazy="selectin")
