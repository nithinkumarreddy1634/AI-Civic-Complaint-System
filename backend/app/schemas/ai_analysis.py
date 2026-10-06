import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class DetectionItem(BaseModel):
    class_id: Optional[int] = None
    class_name: str
    confidence: float
    bbox: Optional[List[float]] = None  # [x1, y1, x2, y2]


class ImageQualitySchema(BaseModel):
    status: str
    score: int
    issues: List[str] = []
    metrics: Dict[str, Any] = {}


class TextCategorySchema(BaseModel):
    category: str
    confidence: float
    match_count: int = 1


class TextAnalysisSchema(BaseModel):
    has_description: bool = False
    categories: List[TextCategorySchema] = []
    keywords: List[str] = []
    urgency_markers: List[str] = []


class ConsistencySchema(BaseModel):
    score: float
    matched: bool
    explanation: str


class RelevanceSchema(BaseModel):
    is_relevant: bool
    score: float
    detected_issues: List[str] = []


class AuditTrailSchema(BaseModel):
    model_version: str
    config_version: str
    verified_at: str
    timing_ms: Dict[str, float] = {}


class VerificationResponse(BaseModel):
    verification_status: str  # VERIFIED, NEEDS_REVIEW, REJECTED
    verification_score: float  # 0.0 - 100.0
    detected_category: Optional[str] = None
    detection_confidence: float = 0.0
    image_quality: ImageQualitySchema
    detections: List[DetectionItem] = []
    relevance: RelevanceSchema
    text_analysis: TextAnalysisSchema
    consistency: ConsistencySchema
    category_match: bool = True
    selected_category: Optional[str] = None
    explanation: List[str] = []
    audit_trail: AuditTrailSchema


class ReviewActionRequest(BaseModel):
    action: str = Field(..., description="'approve', 'reject', or 'request_info'")
    remarks: Optional[str] = Field(None, description="Administrator feedback or notes")


class ReviewActionResponse(BaseModel):
    complaint_id: str
    previous_status: str
    new_status: str
    review_action: str
    remarks: Optional[str] = None
    reviewed_by: str
    updated_at: str


class DetectionResult(BaseModel):
    detected_issue: Optional[str] = None
    confidence: float
    bounding_box: Optional[List[float]] = None
    image_width: int
    image_height: int
    is_civic_issue: bool
    detection_status: str


class VerificationResult(BaseModel):
    verification_score: float
    verification_status: str
    is_civic_issue: bool


class AIAnalysisResponse(BaseModel):
    id: uuid.UUID
    complaint_id: uuid.UUID
    detected_class: Optional[str] = None
    confidence: float
    bounding_box: Optional[dict] = None
    image_width: Optional[int] = None
    image_height: Optional[int] = None
    is_civic_issue: bool
    detection_status: str
    verification_score: float
    verification_status: str
    image_quality_score: Optional[float] = None
    text_consistency_score: Optional[float] = None
    explanation: Optional[List[str]] = None
    audit_metadata: Optional[dict] = None
    model_version: Optional[str] = None
    config_version: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
