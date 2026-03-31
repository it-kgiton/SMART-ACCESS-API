import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Boolean, DateTime, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class BiometricMode(str, enum.Enum):
    FACE_ONLY = "face_only"
    FINGERPRINT_ONLY = "fingerprint_only"
    FACE_PRIMARY_FINGER_FALLBACK = "face_primary_finger_fallback"
    FINGER_PRIMARY_FACE_FALLBACK = "finger_primary_face_fallback"
    OPERATOR_CHOICE = "operator_choice"
    CUSTOMER_CHOICE = "customer_choice"


class Outlet(Base):
    __tablename__ = "outlets"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    merchant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("merchants.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    address: Mapped[str] = mapped_column(Text, nullable=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    biometric_mode: Mapped[str] = mapped_column(
        SAEnum(BiometricMode),
        default=BiometricMode.FACE_PRIMARY_FINGER_FALLBACK,
    )
    max_fallback_attempts: Mapped[int] = mapped_column(default=2)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    merchant = relationship("Merchant", back_populates="outlets")
    devices = relationship("Device", back_populates="outlet", lazy="selectin")
