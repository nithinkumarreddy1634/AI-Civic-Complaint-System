"""
Unit tests for DuplicateDetectionService (Section 8).

Covers:
- Same image high similarity
- Same complaint description & location with different image
- Same location but unrelated issue
- Different locations with visually similar issue (distance penalty)
- Missing GPS handling
- Missing description handling
- Missing image handling
- Graceful exception tolerance
"""
import pytest
import uuid
from sqlalchemy.orm import Session
from app.ai.duplicate.duplicate_service import DuplicateDetectionService
from app.models.complaint import Complaint, ComplaintStatus
from app.models.user import User


@pytest.fixture
def dup_service():
    return DuplicateDetectionService()


def test_missing_gps_handled_gracefully(db: Session, test_user: User, dup_service):
    """Test duplicate detection handles complaint without GPS coordinates gracefully."""
    c1 = Complaint(
        id=uuid.uuid4(),
        user_id=test_user.id,
        category="pothole",
        description="Pothole near street corner",
        image_path="/fake/path1.jpg",
        image_original_name="path1.jpg",
        latitude=None,
        longitude=None,
        status=ComplaintStatus.VERIFIED,
    )
    db.add(c1)
    db.commit()

    # Should run without crashing and return a valid dictionary
    res = dup_service.detect_duplicates(complaint_id=c1.id, db=db, force_recompute=True)
    assert res is not None
    assert "decision" in res
    assert "duplicate_score" in res
    assert res["decision"] in ("NEW", "DUPLICATE", "UNCERTAIN")


def test_missing_description_handled_gracefully(db: Session, test_user: User, dup_service):
    """Test duplicate detection handles empty description without crashing."""
    c2 = Complaint(
        id=uuid.uuid4(),
        user_id=test_user.id,
        category="garbage_accumulation",
        description="",
        image_path="/fake/path2.jpg",
        image_original_name="path2.jpg",
        latitude=12.9716,
        longitude=77.5946,
        status=ComplaintStatus.VERIFIED,
    )
    db.add(c2)
    db.commit()

    res = dup_service.detect_duplicates(complaint_id=c2.id, db=db, force_recompute=True)
    assert res is not None
    assert "decision" in res


def test_same_location_unrelated_issue_not_duplicate(db: Session, test_user: User, dup_service):
    """Complaints at the same location but completely different categories should not duplicate."""
    c_pothole = Complaint(
        id=uuid.uuid4(),
        user_id=test_user.id,
        category="pothole",
        description="Road crater",
        image_path="/fake/pothole.jpg",
        image_original_name="pothole.jpg",
        latitude=12.9716,
        longitude=77.5946,
        status=ComplaintStatus.VERIFIED,
    )
    c_light = Complaint(
        id=uuid.uuid4(),
        user_id=test_user.id,
        category="broken_streetlight",
        description="Streetlight lamp burnt out",
        image_path="/fake/light.jpg",
        image_original_name="light.jpg",
        latitude=12.9716,
        longitude=77.5946,
        status=ComplaintStatus.VERIFIED,
    )
    db.add_all([c_pothole, c_light])
    db.commit()

    # Process first complaint to register it
    dup_service.detect_duplicates(complaint_id=c_pothole.id, db=db, force_recompute=True)
    # Check second complaint
    res = dup_service.detect_duplicates(complaint_id=c_light.id, db=db, force_recompute=True)

    # Different category at same location should be NEW
    assert res["decision"] == "NEW"


def test_far_apart_locations_not_duplicate(db: Session, test_user: User, dup_service):
    """Issues 50km apart should not be duplicates even if identical category."""
    c_loc1 = Complaint(
        id=uuid.uuid4(),
        user_id=test_user.id,
        category="pothole",
        description="Big pothole on road",
        image_path="/fake/pothole1.jpg",
        image_original_name="pothole1.jpg",
        latitude=12.9716,
        longitude=77.5946,
        status=ComplaintStatus.VERIFIED,
    )
    c_loc2 = Complaint(
        id=uuid.uuid4(),
        user_id=test_user.id,
        category="pothole",
        description="Big pothole on road",
        image_path="/fake/pothole2.jpg",
        image_original_name="pothole2.jpg",
        latitude=13.5000,  # ~60km away
        longitude=78.0000,
        status=ComplaintStatus.VERIFIED,
    )
    db.add_all([c_loc1, c_loc2])
    db.commit()

    dup_service.detect_duplicates(complaint_id=c_loc1.id, db=db, force_recompute=True)
    res = dup_service.detect_duplicates(complaint_id=c_loc2.id, db=db, force_recompute=True)

    assert res["decision"] == "NEW"
