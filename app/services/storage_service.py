from pathlib import Path
from uuid import uuid4
from typing import Optional

from supabase import acreate_client

from app.config import settings
from app.core.exceptions import BadRequestException


class StorageService:
    def _get_public_url(self, bucket_name: str, object_path: str) -> str:
        """Construct public URL without a network call."""
        base = settings.SUPABASE_URL.rstrip("/")
        return f"{base}/storage/v1/object/public/{bucket_name}/{object_path}"

    async def upload_merchant_logo(
        self,
        merchant_id: str,
        file_bytes: bytes,
        filename: str,
        content_type: Optional[str],
    ) -> str:
        if not file_bytes:
            raise BadRequestException("Uploaded file is empty")
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
            raise BadRequestException("Supabase storage is not configured")

        ext = Path(filename).suffix or ".jpg"
        object_path = f"merchants/{merchant_id}/{uuid4().hex}{ext}"

        client = await acreate_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY,
        )
        bucket = client.storage.from_(settings.MERCHANT_STORAGE_BUCKET)
        await bucket.upload(
            object_path,
            file_bytes,
            {"content-type": content_type or "application/octet-stream", "upsert": "true"},
        )
        return self._get_public_url(settings.MERCHANT_STORAGE_BUCKET, object_path)

    async def upload_product_image(
        self,
        product_id: str,
        file_bytes: bytes,
        filename: str,
        content_type: Optional[str],
    ) -> str:
        if not file_bytes:
            raise BadRequestException("Uploaded file is empty")
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
            raise BadRequestException("Supabase storage is not configured")

        ext = Path(filename).suffix or ".jpg"
        object_path = f"products/{product_id}/{uuid4().hex}{ext}"

        client = await acreate_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY,
        )
        bucket = client.storage.from_(settings.PRODUCT_STORAGE_BUCKET)
        await bucket.upload(
            object_path,
            file_bytes,
            {"content-type": content_type or "application/octet-stream", "upsert": "true"},
        )
        return self._get_public_url(settings.PRODUCT_STORAGE_BUCKET, object_path)
