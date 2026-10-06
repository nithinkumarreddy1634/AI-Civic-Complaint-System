"""Tests for administrative priority queue service."""
import uuid
import pytest
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.complaint import Complaint, ComplaintStatus
from app.models.priority import PriorityAnalysis
from app.models.severity import SeverityAnalysis
from app.services.priority_queue_service import priority_queue_service


def seed_prioritized_complaint(
    db: Session,
    user: User,
    category: str,
    priority_score: float,
    priority_level: str,
    severity_score: float,
) -> Complaint:
    complaint = Complaint(
        id=uuid.uuid4(),
        user_id=user.id,
        category=category,
        description=f"Complaint for {category}",
        image_path="/tmp/img.jpg",
        image_original_name="img.jpg",
        status=ComplaintStatus.PRIORITIZED,
    )
    db.add(complaint)
    db.commit()

    sev = SeverityAnalysis(
        complaint_id=complaint.id,
        severity_score=severity_score,
        severity_level="HIGH" if severity_score >= 70 else "LOW",
        explanation="sev exp",
    )
    db.add(sev)

    prio = PriorityAnalysis(
        complaint_id=complaint.id,
        priority_score=priority_score,
        priority_level=priority_level,
        base_score=priority_score,
        escalation_boost=0.0,
        contributing_factors={},
        explanation="prio exp",
    )
    db.add(prio)
    db.commit()
    db.refresh(complaint)
    return complaint


def test_priority_queue_sorting_and_filtering(db: Session, test_user: User):
    c1 = seed_prioritized_complaint(db, test_user, "pothole", 92.0, "URGENT", 95.0)
    c2 = seed_prioritized_complaint(db, test_user, "garbage_accumulation", 75.0, "HIGH", 70.0)
    c3 = seed_prioritized_complaint(db, test_user, "broken_streetlight", 35.0, "LOW", 30.0)

    # Test default sort (priority_score desc)
    items, total = priority_queue_service.get_priority_queue(db)
    assert total >= 3
    assert items[0].priority_score >= items[1].priority_score

    # Filter by level
    urgent_items, u_total = priority_queue_service.get_priority_queue(db, priority_level="URGENT")
    assert u_total == 1
    assert urgent_items[0].complaint_id == c1.id

    # Filter by category
    pothole_items, p_total = priority_queue_service.get_priority_queue(db, category="pothole")
    assert p_total == 1
    assert pothole_items[0].complaint_id == c1.id

    # Filter by score range
    range_items, r_total = priority_queue_service.get_priority_queue(db, min_score=70.0, max_score=80.0)
    assert r_total == 1
    assert range_items[0].complaint_id == c2.id


def test_priority_queue_pagination(db: Session, test_user: User):
    seed_prioritized_complaint(db, test_user, "pothole", 88.0, "HIGH", 80.0)
    seed_prioritized_complaint(db, test_user, "open_manhole", 94.0, "URGENT", 90.0)
    seed_prioritized_complaint(db, test_user, "water_leakage", 60.0, "MEDIUM", 55.0)

    # Limit 2, offset 0
    page1, total = priority_queue_service.get_priority_queue(db, limit=2, offset=0)
    assert len(page1) == 2

    # Limit 2, offset 2
    page2, _ = priority_queue_service.get_priority_queue(db, limit=2, offset=2)
    assert len(page2) >= 1
    # Page 1 and Page 2 should not have overlapping first item
    assert page1[0].complaint_id != page2[0].complaint_id
