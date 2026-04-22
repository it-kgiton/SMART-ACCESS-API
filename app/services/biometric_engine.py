import io
import asyncio
import numpy as np
from typing import Optional
from loguru import logger

# buffalo_l includes:
#   - det_10g.onnx      : RetinaFace R50 face detector
#   - w600k_r50.onnx    : ArcFace R50 recognition (WebFace600K, LFW 99.80%)
#   - 1k3d68.onnx       : 3D 68-point landmark
#   - 2d106det.onnx     : 2D 106-point landmark
#   - genderage.onnx    : Gender & age estimation
#
# ArcFace w600k_r50 produces 512-dim L2-normalized embeddings.
# Cosine similarity between two embeddings:
#   same person   ≳ 0.45  (typical 0.55-0.85)
#   diff person   ≲ 0.30


class BiometricEngine:
    """Production biometric verification engine using InsightFace ArcFace."""

    def __init__(self):
        self._face_model = None
        self._initialized = False

    def _initialize_sync(self):
        """Synchronous part — runs in a thread pool so it doesn't block the event loop."""
        try:
            from insightface.app import FaceAnalysis

            self._face_model = FaceAnalysis(
                name="buffalo_l",
                providers=["CPUExecutionProvider"],
            )
            # det_size=(640,640) — standard detection resolution
            self._face_model.prepare(ctx_id=0, det_size=(640, 640))
            self._initialized = True
            models = [m.taskname for m in self._face_model.models.values()]
            logger.info(f"BiometricEngine initialized — models: {models}")
        except Exception as e:
            logger.error(f"CRITICAL: InsightFace failed to load: {e}")
            self._initialized = False

    async def initialize(self):
        """Initialize InsightFace model in a thread pool (non-blocking for the event loop)."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._initialize_sync)

    @property
    def is_ready(self) -> bool:
        return self._initialized and self._face_model is not None

    # ── Face Embedding ──

    def extract_face_embedding(self, image_bytes: bytes) -> Optional[np.ndarray]:
        """Extract 512-dim ArcFace embedding from the best face in the image.
        Returns None if no face detected or model not ready."""
        if not self._initialized:
            self._initialize_sync()
        if not self.is_ready:
            logger.error("extract_face_embedding called but model not ready")
            return None

        import cv2

        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            logger.warning("Failed to decode image bytes")
            return None

        faces = self._face_model.get(img)
        if not faces:
            logger.info("No face detected in image")
            return None

        # Pick the face with highest detection confidence
        best = max(faces, key=lambda f: f.det_score)

        # Reject low-confidence detections
        if best.det_score < 0.5:
            logger.info(f"Face detection score too low: {best.det_score:.3f}")
            return None

        # Reject if face bounding box is too small (min 60×60 px)
        bbox = best.bbox.astype(int)
        face_w = bbox[2] - bbox[0]
        face_h = bbox[3] - bbox[1]
        if face_w < 60 or face_h < 60:
            logger.info(f"Face too small: {face_w}×{face_h} px")
            return None

        return best.normed_embedding  # 512-dim, L2-normalized

    def extract_face_data(self, image_bytes: bytes) -> Optional[dict]:
        """Extract full face analysis data including embedding, landmarks, quality metrics."""
        if not self._initialized:
            self._initialize_sync()
        if not self.is_ready:
            return None

        import cv2

        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return None

        h, w = img.shape[:2]
        faces = self._face_model.get(img)
        if not faces:
            return None

        best = max(faces, key=lambda f: f.det_score)

        if best.det_score < 0.5:
            return None

        bbox = best.bbox.astype(int)
        face_w = bbox[2] - bbox[0]
        face_h = bbox[3] - bbox[1]

        if face_w < 60 or face_h < 60:
            return None

        # Compute pose angles from landmarks (yaw estimation)
        pose_ok = True
        if hasattr(best, 'pose'):
            # pose is [pitch, yaw, roll] in degrees
            yaw = abs(best.pose[1]) if len(best.pose) > 1 else 0
            pitch = abs(best.pose[0]) if len(best.pose) > 0 else 0
            pose_ok = yaw < 40 and pitch < 30
        else:
            yaw, pitch = 0, 0

        # Face-to-image ratio
        face_area_ratio = (face_w * face_h) / (w * h)

        return {
            "embedding": best.normed_embedding,
            "det_score": float(best.det_score),
            "bbox": [int(x) for x in bbox],
            "face_size": (int(face_w), int(face_h)),
            "face_area_ratio": float(face_area_ratio),
            "num_faces": len(faces),
            "pose_ok": pose_ok,
            "gender": int(best.gender) if hasattr(best, 'gender') else None,
            "age": int(best.age) if hasattr(best, 'age') else None,
        }

    # ── Comparison ──

    def compare_face_embeddings(
        self, embedding1: np.ndarray, embedding2: np.ndarray
    ) -> float:
        """Cosine similarity between two 512-dim ArcFace embeddings.
        Both should already be L2-normalized by InsightFace.
        Returns value in range [-1, 1], practically [0, 1] for face embeddings."""
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        sim = float(np.dot(embedding1, embedding2) / (norm1 * norm2))
        return sim

    # ── Quality Assessment ──

    def assess_face_quality(self, image_bytes: bytes) -> float:
        """Comprehensive face quality score (0.0 - 1.0).
        Evaluates: resolution, brightness, blur, detection confidence,
        face size, number of faces."""
        import cv2

        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return 0.0

        h, w = img.shape[:2]
        scores = {}

        # 1. Resolution score (ideal ≥ 640×480)
        pixel_count = h * w
        scores["resolution"] = min(1.0, pixel_count / (640 * 480))

        # 2. Brightness score (ideal ~0.45-0.55)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        brightness = gray.mean() / 255.0
        scores["brightness"] = max(0.0, 1.0 - abs(brightness - 0.5) * 3.0)

        # 3. Sharpness / blur score (Laplacian variance)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        scores["sharpness"] = min(1.0, laplacian_var / 300.0)

        # 4. Contrast score
        contrast = gray.std() / 128.0
        scores["contrast"] = min(1.0, contrast)

        # 5. Face detection quality
        face_data = None
        if self.is_ready:
            faces = self._face_model.get(img)
            if faces:
                best = max(faces, key=lambda f: f.det_score)
                scores["det_confidence"] = float(best.det_score)

                bbox = best.bbox.astype(int)
                fw = bbox[2] - bbox[0]
                fh = bbox[3] - bbox[1]
                # Face size relative to image (ideal: 15-60% of image area)
                face_ratio = (fw * fh) / (w * h)
                scores["face_size"] = min(1.0, face_ratio / 0.10)

                # Penalize multiple faces
                scores["single_face"] = 1.0 if len(faces) == 1 else 0.5
            else:
                scores["det_confidence"] = 0.0
                scores["face_size"] = 0.0
                scores["single_face"] = 0.0

        # Weighted average
        weights = {
            "resolution": 0.10,
            "brightness": 0.10,
            "sharpness": 0.20,
            "contrast": 0.10,
            "det_confidence": 0.25,
            "face_size": 0.15,
            "single_face": 0.10,
        }

        total_weight = sum(weights.get(k, 0) for k in scores)
        if total_weight == 0:
            return 0.0

        quality = sum(scores.get(k, 0) * weights.get(k, 0) for k in scores) / total_weight
        return round(max(0.0, min(1.0, quality)), 4)

    # ── Fingerprint ──

    def match_fingerprint(
        self, template1: bytes, template2: bytes
    ) -> tuple[bool, float]:
        """Match two fingerprint templates. Returns (is_match, score)."""
        logger.warning("Using placeholder fingerprint matching")
        score = 0.0
        if template1 == template2:
            score = 100.0
        return score > 40, score


# Singleton
biometric_engine = BiometricEngine()
