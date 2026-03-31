import io
import numpy as np
from typing import Optional
from loguru import logger


class BiometricEngine:
    """Biometric verification engine for face and fingerprint."""

    def __init__(self):
        self._face_model = None
        self._initialized = False

    async def initialize(self):
        """Initialize biometric models. Call on startup."""
        try:
            # InsightFace lazy import — only load when needed
            import insightface
            from insightface.app import FaceAnalysis

            self._face_model = FaceAnalysis(
                name="buffalo_l", providers=["CPUExecutionProvider"]
            )
            self._face_model.prepare(ctx_id=0, det_size=(640, 640))
            self._initialized = True
            logger.info("Biometric engine initialized successfully")
        except Exception as e:
            logger.warning(f"Face model not loaded (will use mock): {e}")
            self._initialized = False

    def extract_face_embedding(self, image_bytes: bytes) -> Optional[np.ndarray]:
        """Extract face embedding from image bytes."""
        if not self._initialized or self._face_model is None:
            # Return mock embedding for development (no cv2/insightface installed)
            logger.warning("Using mock face embedding (model not loaded)")
            return np.random.randn(512).astype(np.float32)

        try:
            import cv2
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                return None
            faces = self._face_model.get(img)
            if not faces:
                return None
            best_face = max(faces, key=lambda f: f.det_score)
            return best_face.normed_embedding
        except Exception as e:
            logger.warning(f"Face extraction failed, using mock: {e}")
            return np.random.randn(512).astype(np.float32)

    def compare_face_embeddings(
        self, embedding1: np.ndarray, embedding2: np.ndarray
    ) -> float:
        """Compare two face embeddings, return cosine similarity."""
        sim = np.dot(embedding1, embedding2) / (
            np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
        )
        return float(sim)

    def match_fingerprint(
        self, template1: bytes, template2: bytes
    ) -> tuple[bool, float]:
        """Match two fingerprint templates. Returns (is_match, score)."""
        # Placeholder — integrate SourceAFIS or sensor-specific matching
        logger.warning("Using placeholder fingerprint matching")
        # In production, use actual fingerprint matching library
        score = 0.0
        if template1 == template2:
            score = 100.0
        return score > 40, score

    def assess_face_quality(self, image_bytes: bytes) -> float:
        """Assess face image quality. Returns 0.0 - 1.0."""
        try:
            import cv2

            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                return 0.0

            h, w = img.shape[:2]
            resolution_score = min(1.0, (h * w) / (640 * 480))

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            brightness = gray.mean() / 255.0
            brightness_score = 1.0 - abs(brightness - 0.5) * 2

            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            blur_score = min(1.0, laplacian_var / 500.0)

            return (resolution_score + brightness_score + blur_score) / 3.0
        except Exception as e:
            logger.warning(f"Quality assessment failed, using default: {e}")
            return 0.8  # default quality for mock mode


# Singleton
biometric_engine = BiometricEngine()
