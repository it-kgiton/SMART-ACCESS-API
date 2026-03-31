"""
KGiTON API Integration Service
================================
HTTP client for communicating with KGiTON Core API.
Uses X-API-Key header for authentication (same pattern as huba_api).
"""

from typing import Optional
import httpx
from loguru import logger

from app.config import settings


class KGiTONService:
    def __init__(self):
        self.base_url = settings.KGITON_API_URL.rstrip("/")
        self.api_key = settings.KGITON_API_KEY
        self.timeout = 30.0

    def _headers(self) -> dict:
        return {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
        }

    async def validate_license(self, license_key: str) -> Optional[dict]:
        """
        Validate a license key exists and is valid in KGiTON.
        Returns license info or None if invalid.
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/public/validate",
                    params={"key": license_key},
                    headers=self._headers(),
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("data", data)
                logger.warning(
                    f"KGiTON license validation failed: {response.status_code} - {response.text}"
                )
                return None
        except httpx.RequestError as e:
            logger.error(f"KGiTON API request error: {e}")
            return None

    async def validate_license_ownership(self, license_key: str) -> Optional[dict]:
        """
        Validate license ownership - checks if the license is assigned to this API key owner.
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/user/licenses/validate-ownership",
                    params={"key": license_key},
                    headers=self._headers(),
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("data", data)
                logger.warning(
                    f"KGiTON ownership validation failed: {response.status_code} - {response.text}"
                )
                return None
        except httpx.RequestError as e:
            logger.error(f"KGiTON API request error: {e}")
            return None

    async def get_license_info(self, license_key: str) -> Optional[dict]:
        """
        Get full license info including device details from KGiTON.
        Returns: license_key, device_name, device_serial_number, device_model, 
                 token_balance, status, etc.
        """
        result = await self.validate_license(license_key)
        if not result:
            return None
        return result


kgiton_service = KGiTONService()
