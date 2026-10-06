"""
Unit tests for ComplaintService (Section 5).
"""
import pytest
import uuid
from sqlalchemy.orm import Session
from app.services import complaint_service
from app.schemas.complaint import ComplaintCreate
from app.models.complaint import Complaint, ComplaintStatus, ProcessingState
from app.models.user import User


def test_create_complaint(db: Session, test_user: User):
    """Test successful complaint creation with initial status."""
    data = ComplaintCreate(
        category="pothole",
        description="Deep pothole causing accidents near main junction",
        latitude=12.9716,
        longitude=77.5946,
        address="MG Road Junction",
    )
    complaint = complaint_service.create_complaint(
        db=db,
        user_id=test_user.id,
        complaint_data=data,
        image_path="/fake/uploads/test_pothole.jpg",
        image_original_name="pothole.jpg",
    )

    assert complaint.id is not None
    assert complaint.user_id == test_user.id
    assert complaint.category == "pothole"
    assert complaint.status == ComplaintStatus.AI_PROCESSING
    assert complaint.processing_state == ProcessingState.PENDING
    assert complaint.image_path == "/fake/uploads/test_pothole.jpg"
    assert complaint.latitude == 12.9716


def test_get_complaint_by_id(db: Session, test_user: User):
    """Test retrieving complaint by UUID."""
    data = ComplaintCreate(
        category="broken_streetlight",
        description="Streetlight flickering constantly",
        latitude=12.9720,
        longitude=77.5950,
    )
    created = complaint_service.create_complaint(
        db, test_user.id, data, "/fake/light.jpg", "light.jpg"
    )

    fetched = complaint_service.get_complaint(db, created.id)
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.category == "broken_streetlight"

    non_existent = complaint_service.get_complaint(db, uuid.uuid4())
    assert non_existent is None


def test_get_user_complaints_pagination(db: Session, test_user: User):
    """Test listing user's own complaints with pagination and filtering."""
    for i in range(5):
        data = ComplaintCreate(
            category="garbage_accumulation" if i % 2 == 0 else "water_leakage",
            description=f"Issue number {i} reporting civic trouble",
            latitude=12.90 + (i * 0.01),
            longitude=77.50 + (i * 0.01),
        )
        complaint_service.create_complaint(
            db, test_user.id, data, f"/fake/img_{i}.jpg", f"img_{i}.jpg"
        )

    all_complaints = complaint_service.get_user_complaints(db, test_user.id, page=1, limit=10)
    assert len(all_complaints) == 5

    garbage_only = complaint_service.get_user_complaints(
        db, test_user.id, category="garbage_accumulation"
    )
    assert len(garbage_only) == 3


def test_build_complaint_dict(db: Session, test_user: User):
    """Test serializing complaint object to dictionary with AI fields."""
    data = ComplaintCreate(
        category="open_manhole",
        description="Hazardous open manhole on pedestrian path",
        latitude=12.95,
        longitude=77.60,
    )
    complaint = complaint_service.create_complaint(
        db, test_user.id, data, "/fake/manhole.jpg", "manhole.jpg"
    )

    res_citizen = complaint_service.build_complaint_dict(complaint, db, is_admin=False)
    assert res_citizen["id"] == complaint.id
    assert res_citizen["category"] == "open_manhole"
    assert "user_id" in res_citizen

    res_admin = complaint_service.build_complaint_dict(complaint, db, is_admin=True)
    assert res_admin["id"] == complaint.id
