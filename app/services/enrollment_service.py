import asyncio
import numpy as np
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.models.client import Client
from app.models.biometric import FaceCredential, FingerprintCredential, CredentialStatus
from app.services.biometric_engine import biometric_engine
from app.core.exceptions import BadRequestException, NotFoundException


class EnrollmentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def enroll_face(
        self,
        client_id: str,
        image_bytes: bytes,
        enrolled_by: Optional[str] = None,
    ) -> FaceCredential:
        client = await self._get_client(client_id)

        if not biometric_engine.is_ready:
            raise BadRequestException("Biometric engine is not initialized. Please restart the server.")

        loop = asyncio.get_event_loop()
        embedding = await loop.run_in_executor(
            None, biometric_engine.extract_face_embedding, image_bytes
        )
        if embedding is None:
            raise BadRequestException("No face detected in the image. Ensure good lighting and face the camera directly.")

        quality = await loop.run_in_executor(
            None, biometric_engine.assess_face_quality, image_bytes
        )

        result = await self.db.execute(
            select(FaceCredential).where(FaceCredential.client_id == client_id)
        )
        existing = result.scalar_one_or_none()

        embedding_bytes = embedding.astype(np.float32).tobytes()

        if existing:
            existing.embedding = embedding_bytes
            existing.quality_score = quality
            existing.status = CredentialStatus.ACTIVE
            existing.enrolled_by = enrolled_by
            await self.db.commit()
            await self.db.refresh(existing)
            credential = existing
        else:
            credential = FaceCredential(
                client_id=client_id,
                embedding=embedding_bytes,
                quality_score=quality,
                enrolled_by=enrolled_by,
            )
            self.db.add(credential)
            await self.db.commit()
            await self.db.refresh(credential)

        # Update client biometric status
        client.biometric_enrolled = True
        client.biometric_last_updated = datetime.now(timezone.utc)
        await self.db.commit()

        return credential

    async def enroll_fingerprint(
        self,
        client_id: str,
        template_data: bytes,
        finger_index: int = 1,
        enrolled_by: Optional[str] = None,
    ) -> FingerprintCredential:
        client = await self._get_client(client_id)

        result = await self.db.execute(
            select(FingerprintCredential).where(
                FingerprintCredential.client_id == client_id
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            existing.template_data = template_data
            existing.finger_index = finger_index
            existing.quality_score = 1.0
            existing.status = CredentialStatus.ACTIVE
            existing.enrolled_by = enrolled_by
            await self.db.commit()
            await self.db.refresh(existing)
            credential = existing
        else:
            credential = FingerprintCredential(
                client_id=client_id,
                template_data=template_data,
                finger_index=finger_index,
                quality_score=1.0,
                enrolled_by=enrolled_by,
            )
            self.db.add(credential)
            await self.db.commit()
            await self.db.refresh(credential)

        client.biometric_enrolled = True
        client.biometric_last_updated = datetime.now(timezone.utc)
        await self.db.commit()

        return credential

    async def revoke_face(self, client_id: str) -> bool:
        result = await self.db.execute(
            select(FaceCredential).where(FaceCredential.client_id == client_id)
        )
        credential = result.scalar_one_or_none()
        if not credential:
            return False
        await self.db.delete(credential)
        await self.db.commit()
        return True

    async def revoke_fingerprint(self, client_id: str) -> bool:
        result = await self.db.execute(
            select(FingerprintCredential).where(
                FingerprintCredential.client_id == client_id
            )
        )
        credential = result.scalar_one_or_none()
        if not credential:
            return False
        await self.db.delete(credential)
        await self.db.commit()
        return True

    async def get_enrollment_status(self, client_id: str) -> dict:
        client = await self._get_client(client_id)

        face_result = await self.db.execute(
            select(FaceCredential).where(FaceCredential.client_id == client_id)
        )
        face = face_result.scalar_one_or_none()

        fp_result = await self.db.execute(
            select(FingerprintCredential).where(
                FingerprintCredential.client_id == client_id
            )
        )
        fp = fp_result.scalar_one_or_none()

        return {
            "client_id": client.id,
            "client_name": client.name,
            "has_face": face is not None,
            "face_status": face.status if face else None,
            "face_quality": face.quality_score if face else None,
            "has_fingerprint": fp is not None,
            "fingerprint_status": fp.status if fp else None,
            "fingerprint_quality": fp.quality_score if fp else None,
        }

    async def _get_client(self, client_id: str) -> Client:
        result = await self.db.execute(
            select(Client).where(Client.id == client_id)
        )
        client = result.scalar_one_or_none()
        if not client:
            raise NotFoundException("Client")
        return client

    async def verify_face(self, client_id: str, image_bytes: bytes) -> dict:
        from app.config import settings

        if not biometric_engine.is_ready:
            raise BadRequestException("Biometric engine is not initialized.")

        client = await self._get_client(client_id)

        result = await self.db.execute(
            select(FaceCredential).where(
                FaceCredential.client_id == client_id,
                FaceCredential.status == CredentialStatus.ACTIVE,
            )
        )
        credential = result.scalar_one_or_none()
        if not credential:
            raise BadRequestException("Client has no active face credential")

        face_data = biometric_engine.extract_face_data(image_bytes)
        if face_data is None:
            raise BadRequestException("No face detected in the submitted image.")

        embedding = face_data["embedding"]
        submitted_quality = biometric_engine.assess_face_quality(image_bytes)

        stored_embedding = np.frombuffer(credential.embedding, dtype=np.float32)
        similarity = biometric_engine.compare_face_embeddings(embedding, stored_embedding)

        threshold = settings.FACE_SIMILARITY_THRESHOLD
        matched = similarity >= threshold

        if similarity >= 0.70:
            confidence_label = "Very High"
        elif similarity >= 0.60:
            confidence_label = "High"
        elif similarity >= threshold:
            confidence_label = "Acceptable"
        elif similarity >= threshold - 0.10:
            confidence_label = "Low (below threshold)"
        else:
            confidence_label = "No Match"

        return {
            "matched": matched,
            "similarity": round(float(similarity), 4),
            "threshold": threshold,
            "client_id": client.id,
            "client_name": client.name,
            "submitted_quality": round(float(submitted_quality), 4),
            "enrolled_quality": credential.quality_score,
            "confidence_label": confidence_label,
            "det_score": face_data["det_score"],
            "face_size": face_data["face_size"],
            "num_faces": face_data["num_faces"],
        }
