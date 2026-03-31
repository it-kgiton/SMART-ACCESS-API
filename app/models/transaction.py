import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import String, DateTime, ForeignKey, Numeric, Float, Enum as SAEnum, Text
from sqlalchemy.orm import Mapped, mapped_column
import enum

from app.core.database import Base


class TransactionStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    FAILED = "failed"
    CANCELED = "canceled"
    TIMED_OUT = "timed_out"


class BiometricMethod(str, enum.Enum):
    FACE = "face"
    FINGERPRINT = "fingerprint"


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    merchant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("merchants.id"), nullable=False
    )
    outlet_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("outlets.id"), nullable=False
    )
    device_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("devices.id"), nullable=False
    )
    customer_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("customers.id"), nullable=True
    )
    wallet_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("wallets.id"), nullable=True
    )
    biometric_method: Mapped[str] = mapped_column(
        SAEnum(BiometricMethod), nullable=False
    )
    fallback_from: Mapped[str] = mapped_column(
        SAEnum(BiometricMethod), nullable=True
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    status: Mapped[str] = mapped_column(
        SAEnum(TransactionStatus), default=TransactionStatus.PENDING
    )
    confidence_score: Mapped[float] = mapped_column(Float, nullable=True)
    request_reference: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False
    )
    rejection_reason: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
