"""Top-level facade for severity assessment."""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from .severity.severity_service import SeverityAssessmentService


class SeverityResult(BaseModel):
    severity_score: float
    level: str  # LOW, MEDIUM, HIGH, CRITICAL
    factors: List[str] = []
    explanation: List[str] = []


class SeverityAnalyzer:
    """Facade for the Phase 5 AI Severity Assessment engine."""

    def __init__(self):
        self._service = SeverityAssessmentService()

    def analyze(
        self,
        detections: List[Dict[str, Any]],
        image_metadata: Dict[str, Any],
        description: Optional[str] = None,
        location: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Delegate assessment to SeverityAssessmentService."""
        return self._service.assess(
            detections=detections,
            image_metadata=image_metadata,
            description=description,
            location=location,
        )
