"""Pydantic schemas for duplicate complaint detection."""
import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class DuplicateDecision(str, Enum):
    NEW = "NEW"
    POSSIBLE_DUPLICATE = "POSSIBLE_DUPLICATE"
    LIKELY_DUPLICATE = "LIKELY_DUPLICATE"


class CandidateMatch(BaseModel):
    complaint_id: uuid.UUID
    duplicate_score: float
    distance_meters: Optional[float] = None
    location_similarity: Optional[float] = None
    image_similarity: float
    text_similarity: float
    category_similarity: float
    category: str
    status: str


class DuplicateCheckRequest(BaseModel):
    complaint_id: uuid.UUID
    force_recompute: bool = False


class DuplicateCheckResponse(BaseModel):
    complaint_id: uuid.UUID
    decision: DuplicateDecision
    duplicate_score: float
    is_duplicate: bool
    best_match: Optional[CandidateMatch] = None
    candidates: List[CandidateMatch] = Field(default_factory=list)
    explanation: List[str] = Field(default_factory=list)
    duplicate_group_id: Optional[uuid.UUID] = None
    representative_complaint_id: Optional[uuid.UUID] = None
    cached: bool = False


class DuplicateGroupResponse(BaseModel):
    group_id: uuid.UUID
    representative_complaint_id: Optional[uuid.UUID] = None
    report_count: int
    unique_users_count: int
    status: str
    complaint_ids: List[uuid.UUID] = Field(default_factory=list)
    created_at: datetime
