"""Unit tests for DuplicateDetectionService and duplicate grouping."""
import uuid
import pytest
from sqlalchemy.orm import Session
from app.models.complaint import Complaint, ComplaintStatus
from app.models.duplicate import DuplicateGroup, ComplaintDuplicateLink
from app.models.user import User
from app.ai.duplicate.duplicate_service import DuplicateDetectionService


@pytest.fixture
def service():
    return DuplicateDetectionService()


def test_detect_duplicates_no_candidates_returns_new(db: Session, test_user: User, service: DuplicateDetectionService):
    # Isolated complaint
    comp = Complaint(
        id=uuid.uuid4(),
        user_id=test_user.id,
        category="pothole",
        description="Isolated pothole in deserted lane",
        image_path="test_iso.jpg",
        image_original_name="test_iso.jpg",
        latitude=12.9716,
        longitude=77.5946,
        status=ComplaintStatus.VERIFIED,
    )
    db.add(comp)
    db.commit()

    res = service.detect_duplicates(comp.id, db)
    assert res["decision"] == "NEW"
    assert res["duplicate_score"] == 0.0
    assert res["is_duplicate"] is False
    assert res["duplicate_group_id"] is None


def test_detect_duplicates_group_creation_and_linking(db: Session, test_user: User, service: DuplicateDetectionService):
    # Complaint 1: Earlier complaint
    comp1 = Complaint(
        id=uuid.uuid4(),
        user_id=test_user.id,
        category="pothole",
        description="Large pothole near main bus stop",
        image_path="pothole_a.jpg",
        image_original_name="pothole_a.jpg",
        latitude=12.97160,
        longitude=77.59460,
        status=ComplaintStatus.VERIFIED,
    )
    db.add(comp1)
    db.commit()

    # Pre-embed complaint 1
    emb1 = service.get_or_generate_embedding(comp1, db)

    # Complaint 2: Submitted right next to complaint 1 (15m away, same category & description)
    comp2 = Complaint(
        id=uuid.uuid4(),
        user_id=test_user.id,
        category="pothole",
        description="Deep road hole beside the bus stop",
        image_path="pothole_b.jpg",
        image_original_name="pothole_b.jpg",
        latitude=12.97172,
        longitude=77.59460,
        status=ComplaintStatus.VERIFIED,
    )
    db.add(comp2)
    db.commit()

    # Mock identical image embeddings so visual similarity is high for deterministic test
    emb2 = service.get_or_generate_embedding(comp2, db)
    emb2.image_embedding = list(emb1.image_embedding)
    db.commit()

    res = service.detect_duplicates(comp2.id, db)

    assert res["decision"] == "LIKELY_DUPLICATE"
    assert res["is_duplicate"] is True
    assert res["duplicate_group_id"] is not None
    assert res["representative_complaint_id"] is not None

    # Check database status
    db.refresh(comp2)
    assert comp2.is_duplicate is True
    assert comp2.duplicate_of is not None

    # Verify duplicate group
    group = db.query(DuplicateGroup).filter(DuplicateGroup.id == res["duplicate_group_id"]).first()
    assert group is not None
    assert group.report_count == 2
