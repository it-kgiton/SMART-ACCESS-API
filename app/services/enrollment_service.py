import numpy as np
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.models.customer import Customer
from app.models.biometric import FaceCredential, FingerprintCredential, CredentialStatus
from app.services.biometric_engine import biometric_engine
from app.core.exceptions import BadRequestException, NotFoundException


class EnrollmentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def enroll_face(
        self,
        customer_id: str,
        image_bytes: bytes,
        enrolled_by: Optional[str] = None,
    ) -> FaceCredential:
        customer = await self._get_customer(customer_id)

        if not biometric_engine.is_ready:
            raise BadRequestException("Biometric engine is not initialized. Please restart the server.")

        embedding = biometric_engine.extract_face_embedding(image_bytes)
        if embedding is None:
            raise BadRequestException("No face detected in the image. Ensure good lighting and face the camera directly.")

        quality = biometric_engine.assess_face_quality(image_bytes)

        # Check if credential exists
        result = await self.db.execute(
            select(FaceCredential).where(FaceCredential.customer_id == customer_id)
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
            return existing

        credential = FaceCredential(
            customer_id=customer_id,
            embedding=embedding_bytes,
            quality_score=quality,
            enrolled_by=enrolled_by,
        )
        self.db.add(credential)
        await self.db.commit()
        await self.db.refresh(credential)
        return credential

    async def enroll_fingerprint(
        self,
        customer_id: str,
        template_data: bytes,
        finger_index: int = 1,
        enrolled_by: Optional[str] = None,
    ) -> FingerprintCredential:
        customer = await self._get_customer(customer_id)

        result = await self.db.execute(
            select(FingerprintCredential).where(
                FingerprintCredential.customer_id == customer_id
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            existing.template_data = template_data
            existing.finger_index = finger_index
            existing.quality_score = 1.0  # Placeholder
            existing.status = CredentialStatus.ACTIVE
            existing.enrolled_by = enrolled_by
            await self.db.commit()
            await self.db.refresh(existing)
            return existing

        credential = FingerprintCredential(
            customer_id=customer_id,
            template_data=template_data,
            finger_index=finger_index,
            quality_score=1.0,
            enrolled_by=enrolled_by,
        )
        self.db.add(credential)
        await self.db.commit()
        await self.db.refresh(credential)
        return credential

    async def revoke_face(self, customer_id: str) -> bool:
        result = await self.db.execute(
            select(FaceCredential).where(FaceCredential.customer_id == customer_id)
        )
        credential = result.scalar_one_or_none()
        if not credential:
            return False
        await self.db.delete(credential)
        await self.db.commit()
        return True

    async def revoke_fingerprint(self, customer_id: str) -> bool:
        result = await self.db.execute(
            select(FingerprintCredential).where(
                FingerprintCredential.customer_id == customer_id
            )
        )
        credential = result.scalar_one_or_none()
        if not credential:
            return False
        await self.db.delete(credential)
        await self.db.commit()
        return True

    async def get_enrollment_status(self, customer_id: str) -> dict:
        customer = await self._get_customer(customer_id)

        face_result = await self.db.execute(
            select(FaceCredential).where(FaceCredential.customer_id == customer_id)
        )
        face = face_result.scalar_one_or_none()

        fp_result = await self.db.execute(
            select(FingerprintCredential).where(
                FingerprintCredential.customer_id == customer_id
            )
        )
        fp = fp_result.scalar_one_or_none()

        return {
            "customer_id": customer.id,
            "customer_name": customer.name,
            "has_face": face is not None,
            "face_status": face.status if face else None,
            "face_quality": face.quality_score if face else None,
            "has_fingerprint": fp is not None,
            "fingerprint_status": fp.status if fp else None,
            "fingerprint_quality": fp.quality_score if fp else None,
        }

    async def _get_customer(self, customer_id: str) -> Customer:
        result = await self.db.execute(
            select(Customer).where(Customer.id == customer_id)
        )
        customer = result.scalar_one_or_none()
        if not customer:
            raise NotFoundException("Customer")
        return customer

    async def verify_face(self, customer_id: str, image_bytes: bytes) -> dict:
        """Verify a face image against stored enrollment for a given customer."""
        from app.config import settings

        if not biometric_engine.is_ready:
            raise BadRequestException("Biometric engine is not initialized. Please restart the server.")

        customer = await self._get_customer(customer_id)

        # Get stored credential
        result = await self.db.execute(
            select(FaceCredential).where(
                FaceCredential.customer_id == customer_id,
                FaceCredential.status == CredentialStatus.ACTIVE,
            )
        )
        credential = result.scalar_one_or_none()
        if not credential:
            raise BadRequestException("Customer has no active face credential")

        # Extract full face data from submitted image
        face_data = biometric_engine.extract_face_data(image_bytes)
        if face_data is None:
            raise BadRequestException("No face detected in the submitted image. Ensure good lighting and face the camera directly.")

        embedding = face_data["embedding"]

        # Assess quality
        submitted_quality = biometric_engine.assess_face_quality(image_bytes)

        # Compare with stored embedding
        stored_embedding = np.frombuffer(credential.embedding, dtype=np.float32)
        similarity = biometric_engine.compare_face_embeddings(embedding, stored_embedding)

        threshold = settings.FACE_SIMILARITY_THRESHOLD
        matched = similarity >= threshold

        # Confidence labels tuned for ArcFace cosine similarity
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
            "customer_id": customer.id,
            "customer_name": customer.name,
            "submitted_quality": round(float(submitted_quality), 4),
            "enrolled_quality": credential.quality_score,
            "confidence_label": confidence_label,
            "det_score": face_data["det_score"],
            "face_size": face_data["face_size"],
            "num_faces": face_data["num_faces"],
        }
