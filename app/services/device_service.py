from typing import Optional
from datetime import datetime, timezone
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.models.device import Device, DeviceStatus
from app.models.outlet import Outlet
from app.models.merchant import Merchant
from app.schemas.device import DeviceCreate, DeviceUpdate, DeviceHeartbeat, DeviceAssignOutlet
from app.core.security import create_device_token
from app.core.exceptions import BadRequestException, ConflictException, NotFoundException
from app.services.kgiton_service import kgiton_service


class DeviceService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: DeviceCreate) -> Device:
        # Validate license key with KGiTON API
        license_info = await kgiton_service.validate_license(data.license_key)
        if not license_info:
            raise BadRequestException(
                "Invalid license key. License not found in KGiTON system."
            )

        # Check ownership
        ownership = await kgiton_service.validate_license_ownership(data.license_key)
        if not ownership or not ownership.get("is_owner", False):
            raise BadRequestException(
                "License key is not assigned to this account in KGiTON."
            )

        # Check if license_key already registered
        existing = await self.db.execute(
            select(Device).where(Device.license_key == data.license_key)
        )
        if existing.scalar_one_or_none():
            raise ConflictException("License key already registered to another device")

        device_data = data.model_dump()
        # Sync device info from KGiTON
        device_data["device_serial_number"] = license_info.get("device_serial_number")
        device_data["device_model"] = license_info.get("device_model")
        if not device_data.get("name") and license_info.get("device_name"):
            device_data["name"] = license_info.get("device_name")

        device = Device(**device_data)
        self.db.add(device)
        await self.db.commit()
        await self.db.refresh(device)
        return device

    async def get_by_id(self, device_id: str) -> Optional[Device]:
        result = await self.db.execute(
            select(Device).where(Device.id == device_id)
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, device_code: str) -> Optional[Device]:
        result = await self.db.execute(
            select(Device).where(Device.device_code == device_code)
        )
        return result.scalar_one_or_none()

    async def authenticate_device(self, device_code: str, mac_address: str) -> Optional[dict]:
        device = await self.get_by_code(device_code)
        if not device or not device.is_active:
            return None
        if device.status == DeviceStatus.BLOCKED:
            return None
        if device.mac_address and device.mac_address != mac_address:
            return None

        # Update MAC if first auth
        if not device.mac_address:
            device.mac_address = mac_address

        device.status = DeviceStatus.ONLINE
        device.last_seen_at = datetime.now(timezone.utc)

        # Get outlet and merchant info
        outlet_result = await self.db.execute(
            select(Outlet).where(Outlet.id == device.outlet_id)
        )
        outlet = outlet_result.scalar_one_or_none()
        if not outlet:
            return None

        merchant_result = await self.db.execute(
            select(Merchant).where(Merchant.id == outlet.merchant_id)
        )
        merchant = merchant_result.scalar_one_or_none()
        if not merchant:
            return None

        token = create_device_token(device.id, device.device_code)

        await self.db.commit()

        return {
            "token": token,
            "device_id": device.id,
            "outlet_id": outlet.id,
            "merchant_id": merchant.id,
            "biometric_mode": outlet.biometric_mode,
            "config": {
                "biometric_mode": outlet.biometric_mode,
                "max_fallback_attempts": outlet.max_fallback_attempts,
                "outlet_name": outlet.name,
                "merchant_name": merchant.name,
            },
        }

    async def process_heartbeat(self, heartbeat: DeviceHeartbeat) -> bool:
        device = await self.get_by_code(heartbeat.device_code)
        if not device:
            return False

        device.last_heartbeat_at = datetime.now(timezone.utc)
        device.last_seen_at = datetime.now(timezone.utc)
        device.firmware_version = heartbeat.firmware_version
        if heartbeat.ip_address:
            device.ip_address = heartbeat.ip_address
        device.status = DeviceStatus.ONLINE

        await self.db.commit()
        return True

    async def list_all(
        self,
        page: int = 1,
        page_size: int = 20,
        outlet_id: Optional[str] = None,
        status: Optional[str] = None,
        merchant_id: Optional[str] = None,
    ) -> tuple[list[Device], int]:
        query = select(Device)
        count_query = select(func.count()).select_from(Device)

        if merchant_id:
            # Filter devices by merchant via outlet relationship
            outlet_ids_query = select(Outlet.id).where(
                Outlet.merchant_id == merchant_id
            )
            query = query.where(Device.outlet_id.in_(outlet_ids_query))
            count_query = count_query.where(Device.outlet_id.in_(outlet_ids_query))

        if outlet_id:
            query = query.where(Device.outlet_id == outlet_id)
            count_query = count_query.where(Device.outlet_id == outlet_id)
        if status:
            query = query.where(Device.status == status)
            count_query = count_query.where(Device.status == status)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def update(self, device_id: str, data: DeviceUpdate) -> Optional[Device]:
        device = await self.get_by_id(device_id)
        if not device:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(device, field, value)

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

    async def assign_to_outlet(
        self, device_id: str, data: DeviceAssignOutlet, merchant_id: Optional[str] = None
    ) -> Device:
        device = await self.get_by_id(device_id)
        if not device:
            raise NotFoundException("Device not found")

        # Validate outlet exists and belongs to merchant
        outlet_result = await self.db.execute(
            select(Outlet).where(Outlet.id == data.outlet_id)
        )
        outlet = outlet_result.scalar_one_or_none()
        if not outlet:
            raise NotFoundException("Outlet not found")

        if merchant_id and outlet.merchant_id != merchant_id:
            raise BadRequestException("Outlet does not belong to your merchant")

        # If merchant_admin, verify device currently belongs to one of their outlets
        if merchant_id:
            current_outlet_result = await self.db.execute(
                select(Outlet).where(Outlet.id == device.outlet_id)
            )
            current_outlet = current_outlet_result.scalar_one_or_none()
            if not current_outlet or current_outlet.merchant_id != merchant_id:
                raise BadRequestException("Device does not belong to your merchant")

        device.outlet_id = data.outlet_id
        await self.db.commit()
        await self.db.refresh(device)
        return device
