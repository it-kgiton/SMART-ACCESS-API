import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, Text, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class RegionStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"


class Region(Base):
    __tablename__ = "regions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    region_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    region_name: Mapped[str] = mapped_column(String(255), nullable=False)
    province: Mapped[str] = mapped_column(String(255), nullable=True)
    admin_user_id: Mapped[str] = mapped_column(String(36), nullable=True)
    status: Mapped[str] = mapped_column(
        SAEnum(RegionStatus, values_callable=lambda x: [e.value for e in x]),
        default=RegionStatus.ACTIVE,
    )
    created_by: Mapped[str] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    schools = relationship("School", back_populates="region", lazy="selectin")
