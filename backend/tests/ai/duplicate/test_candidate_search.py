"""Unit tests for candidate complaint retrieval."""
import uuid
import pytest
from sqlalchemy.orm import Session
from app.models.complaint import Complaint, ComplaintStatus, ComplaintCategory
from app.models.user import User
from app.ai.duplicate.candidate_search import find_duplicate_candidates


def test_candidate_retrieval_spatial_filtering(db: Session, test_user: User):
    # Complaint 1: Close by (within ~50m)
    c_close = Complaint(
        id=uuid.uuid4(),
        user_id=test_user.id,
        category="pothole",
        description="Pothole near market",
        image_path="test.jpg",
        image_original_name="test.jpg",
        latitude=12.9716,
        longitude=77.5946,
        status=ComplaintStatus.VERIFIED,
    )
    # Complaint 2: Far away (5 km away)
    c_far = Complaint(
        id=uuid.uuid4(),
        user_id=test_user.id,
        category="pothole",
        description="Pothole in distant suburb",
        image_path="test2.jpg",
        image_original_name="test2.jpg",
        latitude=13.0500,
        longitude=77.5946,
        status=ComplaintStatus.VERIFIED,
    )
    db.add_all([c_close, c_far])
    db.commit()

    candidates = find_duplicate_candidates(
        db=db,
        current_complaint_id=uuid.uuid4(),
        category="pothole",
        latitude=12.9718,
        longitude=77.5946,
    )

    cand_ids = [c.id for c in candidates]
    assert c_close.id in cand_ids
    assert c_far.id not in cand_ids


def test_candidate_retrieval_category_filtering(db: Session, test_user: User):
    # Pothole candidate
    c_pothole = Complaint(
        id=uuid.uuid4(),
        user_id=test_user.id,
        category="pothole",
        description="Road hole",
        image_path="p.jpg",
        image_original_name="p.jpg",
        latitude=12.9716,
        longitude=77.5946,
        status=ComplaintStatus.VERIFIED,
    )
    # Streetlight candidate at same location
    c_light = Complaint(
        id=uuid.uuid4(),
        user_id=test_user.id,
        category="broken_streetlight",
        description="Dark street lamp",
        image_path="l.jpg",
        image_original_name="l.jpg",
        latitude=12.9716,
        longitude=77.5946,
        status=ComplaintStatus.VERIFIED,
    )
    db.add_all([c_pothole, c_light])
    db.commit()

    candidates = find_duplicate_candidates(
        db=db,
        current_complaint_id=uuid.uuid4(),
        category="pothole",
        latitude=12.9716,
        longitude=77.5946,
    )

    cand_ids = [c.id for c in candidates]
    assert c_pothole.id in cand_ids
    assert c_light.id not in cand_ids
