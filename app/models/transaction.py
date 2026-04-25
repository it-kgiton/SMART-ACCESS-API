import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import String, Boolean, DateTime, ForeignKey, Numeric, Float, Enum as SAEnum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class TransactionType(str, enum.Enum):
    TOPUP = "topup"
    PURCHASE = "purchase"
    REFUND = "refund"
    WITHDRAWAL = "withdrawal"


class TransactionStatus(str, enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"
    EXPIRED = "expired"


class PaymentMethod(str, enum.Enum):
    QRIS = "qris"
    BANK_TRANSFER = "bank_transfer"
    VA = "va"


class BiometricMethod(str, enum.Enum):
    FINGERPRINT_FACE = "fingerprint_face"
    FALLBACK_PIN = "fallback_pin"


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    transaction_ref: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False
    )
    type: Mapped[str] = mapped_column(
        SAEnum(TransactionType, values_callable=lambda x: [e.value for e in x], native_enum=False),
        nullable=False,
    )
    client_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("clients.id"), nullable=True
    )
    merchant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("merchants.id"), nullable=True
    )
    parent_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("parents.id"), nullable=True
    )
    school_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("schools.id"), nullable=True
    )
    device_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("devices.id"), nullable=True
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    fee_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0.00"))
    status: Mapped[str] = mapped_column(
        SAEnum(TransactionStatus, values_callable=lambda x: [e.value for e in x], native_enum=False),
        default=TransactionStatus.PENDING,
    )
    payment_method: Mapped[str] = mapped_column(
        SAEnum(PaymentMethod, values_callable=lambda x: [e.value for e in x], native_enum=False),
        nullable=True,
    )
    biometric_method: Mapped[str] = mapped_column(
        SAEnum(BiometricMethod, values_callable=lambda x: [e.value for e in x], native_enum=False),
        nullable=True,
    )
    confidence_score: Mapped[float] = mapped_column(Float, nullable=True)
    offline_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    rejection_reason: Mapped[str] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[str] = mapped_column(Text, nullable=True)
    reference_transaction_id: Mapped[str] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    items = relationship("TransactionItem", back_populates="transaction", lazy="selectin")


class TransactionItem(Base):
    __tablename__ = "transaction_items"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    transaction_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("transactions.id"), nullable=False
    )
    product_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("products.id"), nullable=True
    )
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[int] = mapped_column(default=1)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)

    transaction = relationship("Transaction", back_populates="items")
