"""
Pydantic schemas for complaints.

Includes complaint categories, statuses, processing states, and request/response models.
"""
import uuid
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List


class ComplaintCategory(str, Enum):
    """Supported civic infrastructure complaint categories."""
    POTHOLE = "pothole"
    GARBAGE = "garbage_accumulation"
    MANHOLE = "open_manhole"
    DAMAGED_ROAD = "damaged_road"
    STREETLIGHT = "broken_streetlight"
    WATER_LEAKAGE = "water_leakage"
    SIDEWALK = "damaged_sidewalk"
    TREE = "fallen_tree"
    DUMPING = "illegal_dumping"
    OTHER = "other"


class ComplaintStatus(str, Enum):
    """
    Complaint lifecycle statuses.

    Workflow:
        SUBMITTED → AI_PROCESSING → VERIFIED / NEEDS_REVIEW / REJECTED
        → ASSIGNED → IN_PROGRESS → RESOLVED → CLOSED
    """
    SUBMITTED = "SUBMITTED"
    AI_PROCESSING = "AI_PROCESSING"
    VERIFIED = "VERIFIED"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    REJECTED = "REJECTED"
    PRIORITIZED = "PRIORITIZED"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class ProcessingStateEnum(str, Enum):
    """Internal AI Pipeline processing states."""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    VERIFICATION_COMPLETE = "VERIFICATION_COMPLETE"
    SEVERITY_COMPLETE = "SEVERITY_COMPLETE"
    DUPLICATE_CHECK_COMPLETE = "DUPLICATE_CHECK_COMPLETE"
    PRIORITY_COMPLETE = "PRIORITY_COMPLETE"
    DEPARTMENT_RECOMMENDED = "DEPARTMENT_RECOMMENDED"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"


class ComplaintCreate(BaseModel):
    """Schema for creating a new complaint."""
    category: ComplaintCategory
    description: str = Field(..., min_length=5, max_length=2000)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    address: Optional[str] = Field(None, max_length=500)


class ComplaintCreateResponse(BaseModel):
    complaint_id: uuid.UUID
    status: str
    processing_state: str
    message: str = "Complaint submitted successfully."


class ProcessingStatusResponse(BaseModel):
    complaint_id: uuid.UUID
    processing_state: str
    progress: int
    message: Optional[str] = None
    error: Optional[str] = None


class ComplaintUpdate(BaseModel):
    """Schema for updating complaint fields."""
    status: Optional[ComplaintStatus] = None
    category: Optional[ComplaintCategory] = None
    description: Optional[str] = None


class ComplaintListResponse(BaseModel):
    """Compact complaint representation for list views."""
    id: uuid.UUID
    category: str
    description: str
    status: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    created_at: datetime
    priority_level: Optional[str] = None
    processing_state: Optional[str] = None
    image_path: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ComplaintResponse(ComplaintListResponse):
    """Full complaint representation with all details."""
    user_id: uuid.UUID
    image_path: str
    image_original_name: str
    address: Optional[str] = None
    is_duplicate: bool = False
    duplicate_of: Optional[uuid.UUID] = None
    updated_at: datetime
    processing_progress: Optional[int] = 0
    processing_message: Optional[str] = None

    # Nested AI analysis structures
    verification: Optional[Dict[str, Any]] = None
    severity: Optional[Dict[str, Any]] = None
    duplicates: Optional[Dict[str, Any]] = None
    priority: Optional[Dict[str, Any]] = None
    department: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class ComplaintDetailAdminResponse(ComplaintResponse):
    """Full detail view for administrative inspection."""
    assignments: List[Dict[str, Any]] = Field(default_factory=list)
    status_history: List[Dict[str, Any]] = Field(default_factory=list)