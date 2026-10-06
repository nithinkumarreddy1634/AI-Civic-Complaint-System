"""Priority Queue management and retrieval service for administrative triage."""
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc

from app.models.complaint import Complaint, ComplaintStatus
from app.models.priority import PriorityAnalysis
from app.models.severity import SeverityAnalysis
from app.models.ai_analysis import AIAnalysis
from app.models.duplicate import DuplicateGroup, ComplaintDuplicateLink
from app.schemas.priority import PriorityQueueItemResponse


class PriorityQueueService:
    """Provides querying, filtering, and sorting for municipal complaint prioritization queues."""

    def get_priority_queue(
        self,
        db: Session,
        priority_level: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
        min_score: Optional[float] = None,
        max_score: Optional[float] = None,
        sort_by: str = "priority_score",  # priority_score, created_at, severity_score
        order: str = "desc",  # asc, desc
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[PriorityQueueItemResponse], int]:
        """Fetch prioritized complaints matching administrative triage filters."""
        query = (
            db.query(
                Complaint,
                PriorityAnalysis,
                SeverityAnalysis,
                AIAnalysis,
                ComplaintDuplicateLink,
                DuplicateGroup,
            )
            .join(PriorityAnalysis, PriorityAnalysis.complaint_id == Complaint.id)
            .outerjoin(SeverityAnalysis, SeverityAnalysis.complaint_id == Complaint.id)
            .outerjoin(AIAnalysis, AIAnalysis.complaint_id == Complaint.id)
            .outerjoin(ComplaintDuplicateLink, ComplaintDuplicateLink.complaint_id == Complaint.id)
            .outerjoin(DuplicateGroup, DuplicateGroup.id == ComplaintDuplicateLink.group_id)
        )

        # Filters
        if priority_level:
            query = query.filter(PriorityAnalysis.priority_level == priority_level.upper())
        if category:
            query = query.filter(Complaint.category == category)
        if status:
            query = query.filter(Complaint.status == status)
        if min_score is not None:
            query = query.filter(PriorityAnalysis.priority_score >= min_score)
        if max_score is not None:
            query = query.filter(PriorityAnalysis.priority_score <= max_score)

        total_count = query.count()

        # Sorting
        if sort_by == "priority_score":
            sort_col = PriorityAnalysis.priority_score
        elif sort_by == "severity_score":
            sort_col = SeverityAnalysis.severity_score
        elif sort_by == "created_at":
            sort_col = Complaint.created_at
        else:
            sort_col = PriorityAnalysis.priority_score

        if order.lower() == "asc":
            query = query.order_by(asc(sort_col))
        else:
            query = query.order_by(desc(sort_col))

        rows = query.offset(offset).limit(limit).all()

        items: List[PriorityQueueItemResponse] = []
        for complaint, prio, sev, ai, link, group in rows:
            rep_count = group.report_count if group else 1
            items.append(
                PriorityQueueItemResponse(
                    complaint_id=complaint.id,
                    category=complaint.category,
                    description=complaint.description,
                    status=complaint.status,
                    priority_score=prio.priority_score,
                    priority_level=prio.priority_level,
                    verification_status=ai.verification_status if ai else None,
                    severity_score=sev.severity_score if sev else None,
                    safety_risk_score=sev.safety_risk_score if sev else None,
                    report_count=rep_count,
                    is_duplicate=complaint.is_duplicate or (link is not None),
                    latitude=complaint.latitude,
                    longitude=complaint.longitude,
                    address=complaint.address,
                    created_at=complaint.created_at,
                )
            )

        return items, total_count


priority_queue_service = PriorityQueueService()
