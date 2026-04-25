from typing import Optional
from datetime import datetime, timezone
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.device import Device, DeviceStatus
from app.models.school import School
from app.models.merchant import Merchant
from app.schemas.device import DeviceCreate, DeviceUpdate, DeviceHeartbeat
from app.core.security import create_device_token
from app.core.exceptions import ConflictException, NotFoundException


class DeviceService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: DeviceCreate) -> Device:
        # Check duplicate serial
        existing = await self.db.execute(
            select(Device).where(Device.device_serial == data.device_serial)
        )
        if existing.scalar_one_or_none():
            raise ConflictException("Device serial already registered")

        # Check duplicate license key
        existing_license = await self.db.execute(
            select(Device).where(Device.license_key == data.license_key)
        )
        if existing_license.scalar_one_or_none():
            raise ConflictException("License key already registered")

        device = Device(
            device_serial=data.device_serial,
            school_id=data.school_id,
            merchant_id=data.merchant_id,
            device_type=data.device_type or "combo_device",
            name=data.name,
            license_key=data.license_key,
        )
        self.db.add(device)
        await self.db.commit()
        await self.db.refresh(device)
        return device

    async def get_by_id(self, device_id: str) -> Optional[Device]:
        result = await self.db.execute(
            select(Device).where(Device.id == device_id)
        )
        return result.scalar_one_or_none()

    async def get_by_serial(self, device_serial: str) -> Optional[Device]:
        result = await self.db.execute(
            select(Device).where(Device.device_serial == device_serial)
        )
        return result.scalar_one_or_none()

    async def authenticate_device(self, device_serial: str, license_key: str) -> Optional[dict]:
        device = await self.get_by_serial(device_serial)
        if not device or not device.is_active:
            return None
        if device.status == DeviceStatus.BLOCKED:
            return None
        if device.license_key and device.license_key != license_key:
            return None

        device.status = DeviceStatus.ACTIVE
        device.last_heartbeat = datetime.now(timezone.utc)

        config = {}
        if device.school_id:
            school_result = await self.db.execute(
                select(School).where(School.id == device.school_id)
            )
            school = school_result.scalar_one_or_none()
            if school:
                config["school_name"] = school.school_name

        if device.merchant_id:
            merchant_result = await self.db.execute(
                select(Merchant).where(Merchant.id == device.merchant_id)
            )
            merchant = merchant_result.scalar_one_or_none()
            if merchant:
                config["merchant_name"] = merchant.business_name

        token = create_device_token(device.id, device.device_serial)
        await self.db.commit()

        return {
            "token": token,
            "device_id": device.id,
            "school_id": device.school_id,
            "merchant_id": device.merchant_id,
            "config": config,
        }

    async def process_heartbeat(self, heartbeat: DeviceHeartbeat) -> bool:
        device = await self.get_by_serial(heartbeat.device_serial)
        if not device:
            return False

        device.last_heartbeat = datetime.now(timezone.utc)
        device.status = DeviceStatus.ACTIVE
        await self.db.commit()
        return True

    async def list_all(
        self, school_id: Optional[str] = None, merchant_id: Optional[str] = None,
        status: Optional[str] = None, skip: int = 0, limit: int = 50,
    ) -> tuple:
        query = select(Device)
        count_query = select(func.count(Device.id))

        if school_id:
            query = query.where(Device.school_id == school_id)
            count_query = count_query.where(Device.school_id == school_id)
        if merchant_id:
            query = query.where(Device.merchant_id == merchant_id)
            count_query = count_query.where(Device.merchant_id == merchant_id)
        if status:
            query = query.where(Device.status == status)
            count_query = count_query.where(Device.status == status)

        total = (await self.db.execute(count_query)).scalar()
        result = await self.db.execute(
            query.offset(skip).limit(limit).order_by(Device.created_at.desc())
        )
        return result.scalars().all(), total

    async def update(self, device_id: str, data: DeviceUpdate) -> Device:
        device = await self.get_by_id(device_id)
        if not device:
            raise NotFoundException("Device")
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(device, key, value)
        await self.db.commit()
        await self.db.refresh(device)
        return device

    async def block_device(self, device_id: str) -> bool:
        device = await self.get_by_id(device_id)
        if not device:
            return False
        device.status = DeviceStatus.BLOCKED
        device.is_active = False
        await self.db.commit()
        return True

    async def unblock_device(self, device_id: str) -> bool:
        device = await self.get_by_id(device_id)
        if not device:
            return False
        device.status = DeviceStatus.REGISTERED
        device.is_active = True
        await self.db.commit()
        return True
