import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Boolean, DateTime, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
import enum

from app.core.database import Base


class DeviceType(str, enum.Enum):
    FINGERPRINT_READER = "fingerprint_reader"
    FACE_CAMERA = "face_camera"
    COMBO_DEVICE = "combo_device"


class DeviceStatus(str, enum.Enum):
    ACTIVE = "active"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    RETIRED = "retired"
    REGISTERED = "registered"
    BLOCKED = "blocked"


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    device_serial: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    school_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("schools.id"), nullable=True
    )
    merchant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("merchants.id"), nullable=True
    )
    device_type: Mapped[str] = mapped_column(
        SAEnum(DeviceType, values_callable=lambda x: [e.value for e in x], native_enum=False),
        default=DeviceType.COMBO_DEVICE,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=True)
    license_key: Mapped[str] = mapped_column(String(100), unique=True, nullable=True)
    firmware_version: Mapped[str] = mapped_column(String(50), nullable=True)
    sdk_version: Mapped[str] = mapped_column(String(50), nullable=True)
    mac_address: Mapped[str] = mapped_column(String(17), nullable=True)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=True)
    status: Mapped[str] = mapped_column(
        SAEnum(DeviceStatus, values_callable=lambda x: [e.value for e in x], native_enum=False),
        default=DeviceStatus.REGISTERED,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_heartbeat: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    config_json: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
