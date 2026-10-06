"""Top-level facade for AI Complaint Prioritization."""
import uuid
from typing import Optional, Dict, Any
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.schemas.priority import PriorityLevel, PriorityResult
from app.ai.priority.priority_service import priority_service, PriorityService
from app.ai.priority.priority_engine import priority_engine, PriorityEngine


class PriorityFacade:
    """Facade for the Phase 7 AI Complaint Prioritization Engine."""

    def __init__(self):
        self._service = priority_service
        self._engine = priority_engine

    def evaluate(
        self,
        complaint_id: uuid.UUID,
        db: Session,
        unresolved_days: Optional[float] = None,
        is_arterial_road: Optional[bool] = None,
        is_school_zone: Optional[bool] = None,
        is_hospital_zone: Optional[bool] = None,
        reason: str = "INITIAL_ANALYSIS",
    ):
        """Evaluate and persist priority for a complaint."""
        return self._service.evaluate_complaint_priority(
            complaint_id=complaint_id,
            db=db,
            unresolved_days=unresolved_days,
            is_arterial_road=is_arterial_road,
            is_school_zone=is_school_zone,
            is_hospital_zone=is_hospital_zone,
            reason=reason,
        )


__all__ = ["PriorityResult", "PriorityLevel", "PriorityEngine", "PriorityFacade"]
