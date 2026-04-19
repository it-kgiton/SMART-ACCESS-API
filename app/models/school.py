import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class SchoolType(str, enum.Enum):
    SD = "sd"
    SMP = "smp"
    SMA = "sma"
    SMK = "smk"
    BOARDING = "boarding"
    UNIVERSITY = "university"


class SchoolStatus(str, enum.Enum):
    ACTIVE = "active"
    PENDING_APPROVAL = "pending_approval"
    SUSPENDED = "suspended"


class School(Base):
    __tablename__ = "schools"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    region_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("regions.id"), nullable=False
    )
    school_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    school_name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str] = mapped_column(Text, nullable=True)
    city: Mapped[str] = mapped_column(String(255), nullable=True)
    admin_user_id: Mapped[str] = mapped_column(String(36), nullable=True)
    school_type: Mapped[str] = mapped_column(
        SAEnum(SchoolType, values_callable=lambda x: [e.value for e in x]),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        SAEnum(SchoolStatus, values_callable=lambda x: [e.value for e in x]),
        default=SchoolStatus.PENDING_APPROVAL,
    )
    approved_by: Mapped[str] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    region = relationship("Region", back_populates="schools")
    merchants = relationship("Merchant", back_populates="school", lazy="selectin")
    parents = relationship("Parent", back_populates="school", lazy="selectin")
    clients = relationship("Client", back_populates="school", lazy="selectin")
