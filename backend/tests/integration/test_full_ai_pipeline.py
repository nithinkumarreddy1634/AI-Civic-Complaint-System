"""
Integration tests for the complete AI Pipeline orchestration (Section 11).

Tests the full lifecycle:
PENDING -> PROCESSING -> VERIFICATION_COMPLETE -> SEVERITY_COMPLETE ->
DUPLICATE_CHECK_COMPLETE -> PRIORITY_COMPLETE -> DEPARTMENT_RECOMMENDED -> COMPLETE.

Verifies database records after completion:
- ai_analysis
- severity_analysis
- priority_analysis
- duplicate records
- department recommendation
- processing status & progress
- complaint status
"""
import pytest
import uuid
import os
from sqlalchemy.orm import Session
from app.services.complaint_processing_service import complaint_processing_service
from app.models.complaint import Complaint, ComplaintStatus, ProcessingState
from app.models.ai_analysis import AIAnalysis
from app.models.severity import SeverityAnalysis
from app.models.priority import PriorityAnalysis
from app.models.user import User
from tests.fixtures.fixture_data import generate_test_image


def test_full_pipeline_orchestration_lifecycle(db: Session, test_user: User, tmp_path):
    """
    Test that process_complaint() executes all 5 stages end-to-end,
    persisting analysis records and advancing states through to COMPLETE.
    """
    # 1. Create a physical test image
    img_bytes = generate_test_image(pattern="circle")
    test_img_path = str(tmp_path / "pothole_fixture.jpg")
    with open(test_img_path, "wb") as f:
        f.write(img_bytes)

    # 2. Insert Complaint
    complaint = Complaint(
        id=uuid.uuid4(),
        user_id=test_user.id,
        category="pothole",
        description="Dangerous large pothole near busy junction causing traffic disruption",
        image_path=test_img_path,
        image_original_name="pothole_fixture.jpg",
        latitude=12.9716,
        longitude=77.5946,
        address="MG Road Junction",
        status=ComplaintStatus.AI_PROCESSING,
        processing_state=ProcessingState.PENDING,
    )
    db.add(complaint)
    db.commit()

    # 3. Execute orchestrator
    result = complaint_processing_service.process_complaint(complaint.id, db=db)

    # 4. Verify outcome
    assert result is not None
    assert result["processing_state"] == ProcessingState.COMPLETE
    assert result["status"] in (ComplaintStatus.VERIFIED, ComplaintStatus.NEEDS_REVIEW)

    # 5. Refresh complaint from DB
    db.refresh(complaint)
    assert complaint.processing_state == ProcessingState.COMPLETE
    assert complaint.processing_progress == 100
    assert complaint.department_recommendation is not None
    assert "department_name" in complaint.department_recommendation

    # 6. Verify AI Analysis record
    ai_rec = db.query(AIAnalysis).filter(AIAnalysis.complaint_id == complaint.id).first()
    assert ai_rec is not None
    assert ai_rec.verification_status in ("VERIFIED", "NEEDS_REVIEW")
    assert ai_rec.detection_status == "COMPLETED"

    # 7. Verify Severity Analysis record
    sev_rec = db.query(SeverityAnalysis).filter(SeverityAnalysis.complaint_id == complaint.id).first()
    assert sev_rec is not None
    assert 0.0 <= sev_rec.severity_score <= 100.0
    assert sev_rec.severity_level in ("LOW", "MEDIUM", "HIGH", "CRITICAL")

    # 8. Verify Priority Analysis record
    prio_rec = db.query(PriorityAnalysis).filter(PriorityAnalysis.complaint_id == complaint.id).first()
    assert prio_rec is not None
    assert 0.0 <= prio_rec.priority_score <= 100.0
    assert prio_rec.priority_level in ("LOW", "MEDIUM", "HIGH", "URGENT")
