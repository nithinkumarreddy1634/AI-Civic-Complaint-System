import uuid
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class SeverityLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class DetectionSeverityDetail(BaseModel):
    category: str
    confidence: float
    damage_extent_score: float
    damage_area_ratio: float
    safety_risk_score: float
    infrastructure_impact_score: float
    public_impact_score: float
    severity_contribution: float
    bbox: List[float] = Field(default_factory=list)


class SeverityEvidenceBreakdown(BaseModel):
    damage_extent: float
    safety_risk: float
    infrastructure_impact: float
    public_impact: float
    detection_confidence: float
    text_signal: float


class SeverityAssessmentRequest(BaseModel):
    complaint_id: Optional[uuid.UUID] = None
    force_recompute: bool = False


class SeverityAssessmentResponse(BaseModel):
    complaint_id: Optional[uuid.UUID] = None
    severity_score: float
    severity_level: SeverityLevel
    safety_risk_score: float
    infrastructure_impact_score: float
    public_impact_score: float
    detection_analysis: List[DetectionSeverityDetail] = Field(default_factory=list)
    evidence: SeverityEvidenceBreakdown
    factors: List[str] = Field(default_factory=list)
    explanation: List[str] = Field(default_factory=list)
    model_version: str = "civic_yolo_v1"
    severity_config_version: str = "v1.0.0"
    processing_time_ms: Optional[float] = None
    cached: bool = False


# Backward-compatibility alias
SeverityResult = SeverityAssessmentResponse
