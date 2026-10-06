"""Complaint lifecycle status transition management and validation service."""
import uuid
from typing import Optional, Dict, List, Set
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.complaint import Complaint, ComplaintStatus
from app.models.status_history import ComplaintStatusHistory
from app.core.exceptions import BadRequestException, NotFoundException


class StatusService:
    """Enforces strict municipal workflow state transitions and logs historical audit trails."""

    ALLOWED_TRANSITIONS: Dict[str, Set[str]] = {
        ComplaintStatus.SUBMITTED: {
            ComplaintStatus.AI_PROCESSING,
            ComplaintStatus.REJECTED,
        },
        ComplaintStatus.AI_PROCESSING: {
            ComplaintStatus.VERIFIED,
            ComplaintStatus.NEEDS_REVIEW,
            ComplaintStatus.REJECTED,
            ComplaintStatus.PRIORITIZED,
        },
        ComplaintStatus.VERIFIED: {
            ComplaintStatus.PRIORITIZED,
            ComplaintStatus.ASSIGNED,
            ComplaintStatus.NEEDS_REVIEW,
            ComplaintStatus.REJECTED,
        },
        ComplaintStatus.PRIORITIZED: {
            ComplaintStatus.ASSIGNED,
            ComplaintStatus.NEEDS_REVIEW,
            ComplaintStatus.REJECTED,
        },
        ComplaintStatus.NEEDS_REVIEW: {
            ComplaintStatus.VERIFIED,
            ComplaintStatus.REJECTED,
            ComplaintStatus.ASSIGNED,
        },
        ComplaintStatus.ASSIGNED: {
            ComplaintStatus.IN_PROGRESS,
            ComplaintStatus.ASSIGNED,  # Re-assignment to different department
            ComplaintStatus.REJECTED,
        },
        ComplaintStatus.IN_PROGRESS: {
            ComplaintStatus.RESOLVED,
            ComplaintStatus.ASSIGNED,  # Escalation or transfer
        },
        ComplaintStatus.RESOLVED: {
            ComplaintStatus.CLOSED,
            ComplaintStatus.IN_PROGRESS,  # Re-opened upon citizen feedback
        },
        ComplaintStatus.CLOSED: {
            ComplaintStatus.IN_PROGRESS,  # Admin override re-open
        },
        ComplaintStatus.REJECTED: {
            ComplaintStatus.NEEDS_REVIEW,  # Citizen appeal / manual review
        },
    }

    def validate_transition(self, current_status: str, new_status: str) -> bool:
        """Check if a status transition is permitted."""
        allowed = self.ALLOWED_TRANSITIONS.get(current_status, set())
        return new_status in allowed

    def update_status(
        self,
        complaint_id: uuid.UUID,
        new_status: str,
        changed_by: uuid.UUID,
        db: Session,
        remarks: Optional[str] = None,
        force: bool = False,
    ) -> Complaint:
        """Update complaint lifecycle status and log to complaint_status_history."""
        complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
        if not complaint:
            raise NotFoundException(detail=f"Complaint {complaint_id} not found")

        old_status = complaint.status

        # If unchanged
        if old_status == new_status:
            return complaint

        # Validate transition
        if not force and not self.validate_transition(old_status, new_status):
            allowed_list = sorted(list(self.ALLOWED_TRANSITIONS.get(old_status, set())))
            raise BadRequestException(
                detail=(
                    f"Invalid status transition from '{old_status}' to '{new_status}'. "
                    f"Allowed transitions: {allowed_list}"
                )
            )

        # Update complaint
        complaint.status = new_status
        complaint.updated_at = datetime.now(timezone.utc)

        # Log history
        history_entry = ComplaintStatusHistory(
            complaint_id=complaint.id,
            old_status=old_status,
            new_status=new_status,
            changed_by=changed_by,
            remarks=remarks,
            changed_at=datetime.now(timezone.utc),
        )
        db.add(history_entry)
        db.commit()
        db.refresh(complaint)

        return complaint


status_service = StatusService()
