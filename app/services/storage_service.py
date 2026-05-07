from pathlib import Path
from uuid import uuid4
from typing import Optional

from supabase import create_client

from app.config import settings
from app.core.exceptions import BadRequestException


class StorageService:
    def __init__(self):
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
            raise BadRequestException("Supabase storage is not configured")
        self.client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY,
        )

    def upload_merchant_logo(
        self,
        merchant_id: str,
        file_bytes: bytes,
        filename: str,
        content_type: Optional[str],
    ) -> str:
        if not file_bytes:
            raise BadRequestException("Uploaded file is empty")

        ext = Path(filename).suffix or ".jpg"
        object_path = f"merchants/{merchant_id}/{uuid4().hex}{ext}"
        bucket = self.client.storage.from_(settings.MERCHANT_STORAGE_BUCKET)

        upload_result = bucket.upload(
            object_path,
            file_bytes,
            {
                "content-type": content_type or "application/octet-stream",
                "upsert": "true",
            },
        )

        if isinstance(upload_result, dict) and upload_result.get("error"):
            raise BadRequestException(
                upload_result["error"].get("message", "Upload failed")
            )

        public_url = bucket.get_public_url(object_path)
        if isinstance(public_url, dict):
            public_url = (
                public_url.get("publicUrl")
                or public_url.get("public_url")
                or public_url.get("data", {}).get("publicUrl")
            )

        if not public_url:
            raise BadRequestException("Failed to generate public URL")

        return public_url

    def upload_product_image(
        self,
        product_id: str,
        file_bytes: bytes,
        filename: str,
        content_type: Optional[str],
    ) -> str:
        if not file_bytes:
            raise BadRequestException("Uploaded file is empty")

        ext = Path(filename).suffix or ".jpg"
        object_path = f"products/{product_id}/{uuid4().hex}{ext}"
        bucket = self.client.storage.from_(settings.PRODUCT_STORAGE_BUCKET)

        upload_result = bucket.upload(
            object_path,
            file_bytes,
            {
                "content-type": content_type or "application/octet-stream",
                "upsert": "true",
            },
        )

        if isinstance(upload_result, dict) and upload_result.get("error"):
            raise BadRequestException(
                upload_result["error"].get("message", "Upload failed")
            )

        public_url = bucket.get_public_url(object_path)
        if isinstance(public_url, dict):
            public_url = (
                public_url.get("publicUrl")
                or public_url.get("public_url")
                or public_url.get("data", {}).get("publicUrl")
            )

        if not public_url:
            raise BadRequestException("Failed to generate public URL")

        return public_url
