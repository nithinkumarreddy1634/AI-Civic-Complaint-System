"""Human review management service for complaints in NEEDS_REVIEW status."""
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.complaint import Complaint, ComplaintStatus
from app.models.status_history import ComplaintStatusHistory
from app.models.ai_analysis import AIAnalysis


class HumanReviewService:
    """Handles administrator review actions for ambiguous or borderline AI verifications."""

    @staticmethod
    def process_review_action(
        db: Session,
        complaint_id: uuid.UUID,
        reviewer_id: uuid.UUID,
        action: str,  # 'approve', 'reject', 'request_info'
        remarks: Optional[str] = None
    ) -> Dict[str, Any]:
        """Applies manual human review decision to a complaint and logs audit trail."""
        complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
        if not complaint:
            raise HTTPException(status_code=404, detail=f"Complaint not found: {complaint_id}")

        old_status = complaint.status

        if action == "approve":
            new_status = ComplaintStatus.VERIFIED
            action_desc = "Complaint manually verified and approved by municipal reviewer."
        elif action == "reject":
            new_status = ComplaintStatus.REJECTED
            action_desc = "Complaint reviewed and rejected by municipal reviewer."
        elif action == "request_info":
            new_status = ComplaintStatus.NEEDS_REVIEW
            action_desc = "Additional clarification or a clearer photograph requested from citizen."
        else:
            raise HTTPException(status_code=400, detail=f"Invalid review action: '{action}'. Allowed: approve, reject, request_info.")

        # Update complaint record
        complaint.status = new_status
        complaint.updated_at = datetime.now(timezone.utc)

        # Update AI analysis record if present
        ai_record = db.query(AIAnalysis).filter(AIAnalysis.complaint_id == complaint_id).first()
        if ai_record:
            if action == "approve":
                ai_record.verification_status = "VERIFIED_MANUAL"
            elif action == "reject":
                ai_record.verification_status = "REJECTED_MANUAL"

        # Log status transition history
        history_entry = ComplaintStatusHistory(
            complaint_id=complaint.id,
            old_status=old_status.value if hasattr(old_status, "value") else str(old_status),
            new_status=new_status.value if hasattr(new_status, "value") else str(new_status),
            changed_by=reviewer_id,
            remarks=f"{action_desc} Notes: {remarks or 'None'}"
        )
        db.add(history_entry)
        db.commit()
        db.refresh(complaint)

        return {
            "complaint_id": str(complaint.id),
            "previous_status": old_status.value if hasattr(old_status, "value") else str(old_status),
            "new_status": new_status.value if hasattr(new_status, "value") else str(new_status),
            "review_action": action,
            "remarks": remarks,
            "reviewed_by": str(reviewer_id),
            "updated_at": complaint.updated_at.isoformat()
        }
