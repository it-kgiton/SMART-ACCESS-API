import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Boolean, DateTime, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class DeviceStatus(str, enum.Enum):
    REGISTERED = "registered"
    PROVISIONED = "provisioned"
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    BLOCKED = "blocked"


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    outlet_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("outlets.id"), nullable=False
    )
    device_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=True)
    license_key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    device_serial_number: Mapped[str] = mapped_column(String(100), nullable=True)
    device_model: Mapped[str] = mapped_column(String(100), nullable=True)
    firmware_version: Mapped[str] = mapped_column(String(50), nullable=True)
    hardware_version: Mapped[str] = mapped_column(String(50), nullable=True)
    mac_address: Mapped[str] = mapped_column(String(17), nullable=True)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=True)
    status: Mapped[str] = mapped_column(
        SAEnum(DeviceStatus), default=DeviceStatus.REGISTERED
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    last_heartbeat_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    config_json: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    outlet = relationship("Outlet", back_populates="devices")
