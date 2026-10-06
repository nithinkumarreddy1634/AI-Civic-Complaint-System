"""Civic Issue Verification Interface and Implementation.

Wraps the complete Phase 4 ComplaintVerificationService while maintaining
backwards compatibility with the BaseVerifier abstract base class.
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from .detection import DetectionResult
from .verification.verification_service import ComplaintVerificationService
from .verification.config import DEFAULT_VERIFICATION_CONFIG, VerificationConfig


class VerificationResult(BaseModel):
    is_verified: bool
    status: str  # VERIFIED, NEEDS_REVIEW, REJECTED
    verification_score: float
    explanation: List[str] = []
    detected_category: Optional[str] = None
    detection_confidence: float = 0.0


class BaseVerifier(ABC):
    """Abstract interface for verifying if a detected object represents a genuine civic issue."""

    @abstractmethod
    async def verify(
        self,
        detection_result: Optional[DetectionResult],
        image_path: str,
        description: Optional[str] = None,
        selected_category: Optional[str] = None
    ) -> VerificationResult:
        pass


class CivicIssueVerifier(BaseVerifier):
    """Verifies civic complaints using Computer Vision, image quality, and text consistency."""

    def __init__(self, verification_service: Optional[ComplaintVerificationService] = None):
        self.service = verification_service or ComplaintVerificationService()

    async def verify(
        self,
        detection_result: Optional[DetectionResult] = None,
        image_path: str = "",
        description: Optional[str] = None,
        selected_category: Optional[str] = None
    ) -> VerificationResult:
        mock_dets = None
        if detection_result and detection_result.detected_issue:
            mock_dets = [{
                "class_name": detection_result.detected_issue,
                "confidence": detection_result.confidence,
                "bbox": detection_result.bounding_box or [0, 0, 0, 0]
            }]

        res = self.service.verify_complaint(
            image_input=image_path,
            description=description,
            selected_category=selected_category,
            mock_detections=mock_dets
        )

        return VerificationResult(
            is_verified=(res["verification_status"] == "VERIFIED"),
            status=res["verification_status"],
            verification_score=res["verification_score"],
            explanation=res["explanation"],
            detected_category=res.get("detected_category"),
            detection_confidence=res.get("detection_confidence", 0.0)
        )
