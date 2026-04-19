from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class FaceEnrollmentResponse(BaseModel):
    credential_id: str
    client_id: str
    quality_score: Optional[float] = None
    status: str
    enrolled_at: datetime


class FingerprintEnrollmentResponse(BaseModel):
    credential_id: str
    client_id: str
    finger_index: int
    quality_score: Optional[float] = None
    status: str
    enrolled_at: datetime


class EnrollmentStatusResponse(BaseModel):
    client_id: str
    client_name: str
    has_face: bool
    face_status: Optional[str] = None
    face_quality: Optional[float] = None
    has_fingerprint: bool
    fingerprint_status: Optional[str] = None
    fingerprint_quality: Optional[float] = None


class FaceVerifyResponse(BaseModel):
    matched: bool
    similarity: float
    threshold: float
    client_id: str
    client_name: str
    submitted_quality: float
    enrolled_quality: Optional[float] = None
    confidence_label: str
    det_score: Optional[float] = None
    face_size: Optional[list] = None
    num_faces: Optional[int] = None
