import uuid
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any, List, Optional


class PriorityLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class FactorContributionSchema(BaseModel):
    raw_value: Any
    normalized_score: float
    nominal_weight: float
    effective_weight: float
    contribution: float
    status: str = "included"


class PriorityEvaluateRequest(BaseModel):
    complaint_id: uuid.UUID
    force_recalculate: bool = False
    unresolved_days: Optional[float] = None
    is_arterial_road: Optional[bool] = None
    is_school_zone: Optional[bool] = None
    is_hospital_zone: Optional[bool] = None


class PriorityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    complaint_id: uuid.UUID
    priority_score: float
    priority_level: PriorityLevel
    base_score: float
    escalation_boost: float
    contributing_factors: Dict[str, Any]
    explanation: str
    algorithm_version: str = "v1.0.0"
    config_version: str = "v1.0.0"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class PriorityHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    complaint_id: uuid.UUID
    priority_score: float
    priority_level: PriorityLevel
    reason: str
    contributing_factors: Dict[str, Any]
    explanation: str
    created_at: datetime


class PriorityQueueItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    complaint_id: uuid.UUID
    category: str
    description: str
    status: str
    priority_score: float
    priority_level: str
    verification_status: Optional[str] = None
    severity_score: Optional[float] = None
    safety_risk_score: Optional[float] = None
    report_count: int = 1
    is_duplicate: bool = False
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    created_at: datetime


class PriorityResult(BaseModel):
    priority_score: float
    priority_level: PriorityLevel
    contributing_factors: Dict[str, Any]
    explanation: str
