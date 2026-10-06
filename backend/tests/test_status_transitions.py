"""Tests for complaint lifecycle status transitions and audit history."""
import uuid
import pytest
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.complaint import Complaint, ComplaintStatus
from app.models.status_history import ComplaintStatusHistory
from app.services.status_service import status_service
from app.core.exceptions import BadRequestException, NotFoundException


def create_test_complaint(db: Session, user: User, initial_status: str = ComplaintStatus.SUBMITTED) -> Complaint:
    complaint = Complaint(
        id=uuid.uuid4(),
        user_id=user.id,
        category="pothole",
        description="Test complaint for status lifecycle",
        image_path="/tmp/test.jpg",
        image_original_name="test.jpg",
        status=initial_status,
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    return complaint


def test_valid_lifecycle_progression(db: Session, test_user: User, test_admin: User):
    complaint = create_test_complaint(db, test_user, initial_status=ComplaintStatus.SUBMITTED)

    # 1. SUBMITTED -> AI_PROCESSING
    status_service.update_status(complaint.id, ComplaintStatus.AI_PROCESSING, test_admin.id, db, remarks="AI pipeline start")
    assert complaint.status == ComplaintStatus.AI_PROCESSING

    # 2. AI_PROCESSING -> VERIFIED
    status_service.update_status(complaint.id, ComplaintStatus.VERIFIED, test_admin.id, db, remarks="Verified by CV")
    assert complaint.status == ComplaintStatus.VERIFIED

    # 3. VERIFIED -> ASSIGNED
    status_service.update_status(complaint.id, ComplaintStatus.ASSIGNED, test_admin.id, db, remarks="Assigned to Roads")
    assert complaint.status == ComplaintStatus.ASSIGNED

    # 4. ASSIGNED -> IN_PROGRESS
    status_service.update_status(complaint.id, ComplaintStatus.IN_PROGRESS, test_admin.id, db, remarks="Work crew dispatched")
    assert complaint.status == ComplaintStatus.IN_PROGRESS

    # 5. IN_PROGRESS -> RESOLVED
    status_service.update_status(complaint.id, ComplaintStatus.RESOLVED, test_admin.id, db, remarks="Pothole filled and sealed")
    assert complaint.status == ComplaintStatus.RESOLVED

    # 6. RESOLVED -> CLOSED
    status_service.update_status(complaint.id, ComplaintStatus.CLOSED, test_admin.id, db, remarks="Citizen verified repair")
    assert complaint.status == ComplaintStatus.CLOSED

    # Check status history records
    history = (
        db.query(ComplaintStatusHistory)
        .filter(ComplaintStatusHistory.complaint_id == complaint.id)
        .order_by(ComplaintStatusHistory.changed_at.asc())
        .all()
    )
    assert len(history) == 6
    assert history[0].old_status == ComplaintStatus.SUBMITTED
    assert history[0].new_status == ComplaintStatus.AI_PROCESSING
    assert history[-1].old_status == ComplaintStatus.RESOLVED
    assert history[-1].new_status == ComplaintStatus.CLOSED


def test_invalid_status_transition_raises_error(db: Session, test_user: User, test_admin: User):
    complaint = create_test_complaint(db, test_user, initial_status=ComplaintStatus.SUBMITTED)

    # Illegal transition: SUBMITTED directly to RESOLVED without verification or assignment
    with pytest.raises(BadRequestException, match="Invalid status transition"):
        status_service.update_status(complaint.id, ComplaintStatus.RESOLVED, test_admin.id, db)

    # State must remain SUBMITTED
    assert complaint.status == ComplaintStatus.SUBMITTED


def test_nonexistent_complaint_raises_error(db: Session, test_admin: User):
    random_id = uuid.uuid4()
    with pytest.raises(NotFoundException):
        status_service.update_status(random_id, ComplaintStatus.IN_PROGRESS, test_admin.id, db)
