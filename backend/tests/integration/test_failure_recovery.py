"""
Failure recovery and resiliency integration tests (Section 12).

Tests how the pipeline behaves when components fail intentionally:
- Missing image file on disk
- Non-existent complaint ID
- Model / service exceptions
- Verifies processing_state == FAILED
- Verifies error message recorded internally
- Verifies pipeline does not silently succeed on failures
"""
import pytest
import uuid
from unittest.mock import patch
from sqlalchemy.orm import Session
from app.services.complaint_processing_service import ComplaintProcessingService
from app.models.complaint import Complaint, ComplaintStatus, ProcessingState
from app.models.user import User


def test_missing_image_file_failure_recovery(db: Session, test_user: User):
    """If image file is deleted from disk before AI processing runs, mark FAILED gracefully."""
    complaint = Complaint(
        id=uuid.uuid4(),
        user_id=test_user.id,
        category="pothole",
        description="Pothole whose image was lost",
        image_path="/non_existent/directory/missing_image.jpg",
        image_original_name="missing_image.jpg",
        status=ComplaintStatus.AI_PROCESSING,
        processing_state=ProcessingState.PENDING,
    )
    db.add(complaint)
    db.commit()

    service = ComplaintProcessingService()
    # Mock verification service to raise FileNotFoundError when reading non-existent file
    with patch.object(service.verification_service, "verify_complaint", side_effect=FileNotFoundError("Image file missing from disk")):
        result = service.process_complaint(complaint.id, db=db)

    db.refresh(complaint)
    assert complaint.processing_state == ProcessingState.FAILED
    assert complaint.processing_error is not None
    assert "Image file missing" in complaint.processing_error
    assert result["processing_state"] == ProcessingState.FAILED


def test_non_existent_complaint_id(db: Session):
    """Passing a random unpersisted UUID returns an error dictionary without raising unhandled exception."""
    service = ComplaintProcessingService()
    random_id = uuid.uuid4()
    result = service.process_complaint(random_id, db=db)

    assert result["status"] == "error"
    assert "not found" in result["message"]


def test_severity_failure_records_failed_state(db: Session, test_user: User):
    """If severity stage throws an unexpected exception, processing state transitions to FAILED."""
    complaint = Complaint(
        id=uuid.uuid4(),
        user_id=test_user.id,
        category="pothole",
        description="Issue triggering severity failure",
        image_path="/fake/test.jpg",
        image_original_name="test.jpg",
        status=ComplaintStatus.AI_PROCESSING,
        processing_state=ProcessingState.PENDING,
    )
    db.add(complaint)
    db.commit()

    service = ComplaintProcessingService()
    # Mock verification to succeed as VERIFIED, but severity to crash
    with patch.object(service.verification_service, "verify_complaint", return_value={
        "verification_status": "VERIFIED",
        "verification_score": 0.9,
        "detections": [{"bbox": [10, 10, 50, 50]}],
        "image_quality": {"score": 0.9, "metrics": {"width": 640, "height": 480}},
        "relevance": {"is_relevant": True},
        "consistency": {"score": 0.8},
        "audit_trail": {},
    }):
        with patch.object(service.severity_service, "assess", side_effect=RuntimeError("CUDA Out of Memory in severity")):
            result = service.process_complaint(complaint.id, db=db)

    db.refresh(complaint)
    assert complaint.processing_state == ProcessingState.FAILED
    assert "CUDA Out of Memory" in complaint.processing_error
    assert result["processing_state"] == ProcessingState.FAILED
