import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Boolean, DateTime, Float, ForeignKey, Enum as SAEnum, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class CredentialStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    REVOKED = "revoked"


class FaceCredential(Base):
    __tablename__ = "face_credentials"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    customer_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("customers.id"), unique=True, nullable=False
    )
    embedding: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    embedding_version: Mapped[str] = mapped_column(String(50), default="arcface_r100")
    quality_score: Mapped[float] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(
        SAEnum(CredentialStatus), default=CredentialStatus.ACTIVE
    )
    enrolled_by: Mapped[str] = mapped_column(String(36), nullable=True)
    enrolled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    customer = relationship("Customer", back_populates="face_credential")


class FingerprintCredential(Base):
    __tablename__ = "fingerprint_credentials"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    customer_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("customers.id"), unique=True, nullable=False
    )
    template_data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    finger_index: Mapped[int] = mapped_column(default=1)
    quality_score: Mapped[float] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(
        SAEnum(CredentialStatus), default=CredentialStatus.ACTIVE
    )
    enrolled_by: Mapped[str] = mapped_column(String(36), nullable=True)
    enrolled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    customer = relationship("Customer", back_populates="fingerprint_credential")
