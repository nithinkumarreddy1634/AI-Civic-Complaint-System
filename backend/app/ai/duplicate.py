"""Top-level facade for duplicate complaint detection."""
import uuid
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from pydantic import BaseModel
from .duplicate.duplicate_service import DuplicateDetectionService


class DuplicateCheckResult(BaseModel):
    is_duplicate: bool
    duplicate_complaint_id: Optional[uuid.UUID] = None
    similarity_score: float
    factors: dict = {}


class DuplicateDetector:
    """Facade for the Phase 6 AI Duplicate Detection engine."""

    def __init__(self):
        self._service = DuplicateDetectionService()

    def check(self, complaint_id: uuid.UUID, db: Session, force_recompute: bool = False) -> Dict[str, Any]:
        """Delegate duplicate detection to DuplicateDetectionService."""
        return self._service.detect_duplicates(complaint_id=complaint_id, db=db, force_recompute=force_recompute)
