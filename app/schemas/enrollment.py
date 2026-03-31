from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class FaceEnrollmentResponse(BaseModel):
    credential_id: str
    customer_id: str
    quality_score: Optional[float] = None
    status: str
    enrolled_at: datetime


class FingerprintEnrollmentResponse(BaseModel):
    credential_id: str
    customer_id: str
    finger_index: int
    quality_score: Optional[float] = None
    status: str
    enrolled_at: datetime


class EnrollmentStatusResponse(BaseModel):
    customer_id: str
    customer_name: str
    has_face: bool
    face_status: Optional[str] = None
    face_quality: Optional[float] = None
    has_fingerprint: bool
    fingerprint_status: Optional[str] = None
    fingerprint_quality: Optional[float] = None
